from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from _local_package import load_local_package

load_local_package()

from omj.paths import resolve_paths
from omj.workflows.memory import (
    approve_project_memory_candidate,
    build_project_memory_recall_pack,
    capture_project_memory_candidate,
)
from omj.workflows.memory_provenance import build_memory_source_index
from omj.workflows.domain_intelligence import (
    DOMAIN_CANDIDATE_SCHEMA_VERSION,
    DOMAIN_PROFILE_SCHEMA_VERSION,
    REDUCTION_POLICY,
    CLAIM_BOUNDARY,
    capture_domain_candidate,
    approve_domain_candidate,
    reject_domain_candidate,
    retire_domain_profile,
    validate_candidate_contract,
    validate_profile_contract,
)
from omj.workflows.memory_lifecycle import (
    RECEIPT_SCHEMA_VERSION,
    build_memory_correction,
    build_memory_restore,
    build_memory_retirement,
    compare_retrieval_reports,
    lifecycle_replay_status,
    validate_lifecycle_receipt,
)


class MemoryExtensionsParityTests(unittest.TestCase):
    def test_g8_source_index_matches_independent_axes_without_mutating_records(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            captured = capture_project_memory_candidate(
                paths,
                "Use the release checklist",
                source="release-import",
                source_ref="docs/release.md",
            )
            approved = approve_project_memory_candidate(paths, captured["candidate"]["candidate_id"])
            record = approved["record"]
            record_path = paths.memory_dir / "records" / f"{record['record_id']}.json"
            before = record_path.read_bytes()

            report = build_memory_source_index(paths, source="release-import")

            self.assertEqual(report["schema_version"], "memory_source_index/v1")
            self.assertEqual(report["selected"]["outcome"], "matched")
            self.assertEqual(report["selected"]["count"], 1)
            selected = report["selected"]["records"][0]
            self.assertIn("changes nothing", report["claim_boundary"])
            self.assertEqual(report["selected"]["records"][0]["record_id"], record["record_id"])
            self.assertEqual(record_path.read_bytes(), before)

            ref_report = build_memory_source_index(paths, source="docs/release.md")
            self.assertEqual(ref_report["selected"]["records"][0]["matched_axes"], ["source_ref"])
            dual = capture_project_memory_candidate(paths, "Dual origin note", source="dual-origin", source_ref="dual-origin")
            approve_project_memory_candidate(paths, dual["candidate"]["candidate_id"])
            dual_report = build_memory_source_index(paths, source="dual-origin")
            self.assertEqual(dual_report["selected"]["records"][0]["matched_axes"], ["source", "source_ref"])
            absent_report = build_memory_source_index(paths, source="never-seen")
            self.assertEqual(absent_report["selected"]["outcome"], "no_records_for_source")
            self.assertEqual(build_memory_source_index(paths, source="release-import", limit=0)["selected"]["records"], [])

    def test_g8_missing_source_and_unreadable_records_are_indeterminate(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            no_source = capture_project_memory_candidate(paths, "A source-less reviewed note", source="known", source_ref="known-ref")
            approved = approve_project_memory_candidate(paths, no_source["candidate"]["candidate_id"])
            source_path = paths.memory_dir / "records" / f"{approved['record']['record_id']}.json"
            source_record = json.loads(source_path.read_text(encoding="utf-8"))
            source_record["source"] = ""
            source_record["source_ref"] = ""
            source_path.write_text(json.dumps(source_record), encoding="utf-8")
            unreadable = paths.memory_dir / "records" / "unreadable.json"
            unreadable.parent.mkdir(parents=True, exist_ok=True)
            unreadable.write_text("{not-json", encoding="utf-8")

            report = build_memory_source_index(paths, source="never-seen")

            self.assertEqual(report["selected"]["outcome"], "source_never_recorded")
            self.assertGreaterEqual(report["indeterminate"]["count"], 2)
            self.assertTrue(any(item["reason"] == "source_not_recorded" for item in report["indeterminate"]["records"]))
            self.assertTrue(report["indeterminate"]["unreadable"])

            empty = build_memory_source_index(resolve_paths(Path(tmp) / "empty.omj", Path(tmp) / "empty.hermes"), source="anything")
            self.assertEqual(empty["selected"]["outcome"], "empty_store")

    def test_g8_index_does_not_broaden_recall_scope_or_expiry_filters(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            captured = capture_project_memory_candidate(
                paths,
                "Expired release note",
                source="release-import",
                scope_kind="project",
                scope_ref="repo-a",
                ttl_days=1,
            )
            approved = approve_project_memory_candidate(paths, captured["candidate"]["candidate_id"])
            record_path = paths.memory_dir / "records" / f"{approved['record']['record_id']}.json"
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record["ttl"]["expires_at"] = "2000-01-01T00:00:00+00:00"
            record_path.write_text(json.dumps(record), encoding="utf-8")

            index = build_memory_source_index(paths, source="release-import")
            recall = build_project_memory_recall_pack(paths, "expired release", scope_kind="project", scope_ref="repo-b")

            self.assertEqual(index["selected"]["count"], 1)
            self.assertEqual(recall["record_count"], 0)
            self.assertFalse(recall["included_records"])

    def _domain_candidate(self, paths: object) -> dict[str, object]:
        return capture_domain_candidate(
            paths,
            scope_kind="project",
            scope_ref="repo-a",
            domain_id="payments",
            mappings=[("refund", "refund_flow")],
            workflow_hints=["billing-review"],
            source_class="operator_supplied",
            source_ref="review-42",
            observation_count=2,
            confidence=0.75,
        )["candidate"]

    def test_g14_candidate_and_profile_contracts_require_reviewed_fields_and_lineage(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            candidate = self._domain_candidate(paths)

            self.assertEqual(candidate["schema_version"], DOMAIN_CANDIDATE_SCHEMA_VERSION)
            self.assertEqual(candidate["status"], "pending_review")
            self.assertEqual(validate_candidate_contract(candidate), "pending_review")
            self.assertEqual(candidate["provenance"]["source_class"], "operator_supplied")
            self.assertEqual(candidate["confidence"]["routing_authority"], "none")
            self.assertEqual(candidate["redaction_policy"], REDUCTION_POLICY)
            self.assertEqual(candidate["claim_boundary"], CLAIM_BOUNDARY)

            approved = approve_domain_candidate(paths, candidate["candidate_id"], approved_by="operator-1")
            profile = approved["profile"]
            self.assertEqual(profile["schema_version"], DOMAIN_PROFILE_SCHEMA_VERSION)
            self.assertEqual(validate_profile_contract(profile), "active")
            self.assertEqual(profile["revision"], 1)
            self.assertEqual(profile["payload_digest"], approved["review"]["payload_digest"])
            self.assertEqual(profile["candidate_id"], candidate["candidate_id"])

    def test_g14_capture_rejects_raw_prompt_transcript_credentials_and_injection(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            bad_inputs = (
                {"domain_id": "ignore previous instructions"},
                {"mappings": [("password=secret", "secret")]},
                {"workflow_hints": ["raw transcript: user said ..."]},
            )
            for overrides in bad_inputs:
                with self.subTest(overrides=overrides):
                    kwargs: dict[str, object] = {
                        "scope_kind": "project",
                        "scope_ref": "repo-a",
                        "domain_id": "payments",
                        "mappings": [("refund", "refund_flow")],
                    }
                    kwargs.update(overrides)
                    with self.assertRaises(ValueError):
                        capture_domain_candidate(paths, **kwargs)

    def test_g14_approval_rejects_stale_revision_and_preserves_rejection_provenance(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            first = self._domain_candidate(paths)
            stale = capture_domain_candidate(
                paths,
                scope_kind="project",
                scope_ref="repo-a",
                domain_id="payments",
                mappings=[("refund", "legacy_refund")],
                source_ref="review-43",
            )["candidate"]
            first_approval = approve_domain_candidate(paths, first["candidate_id"], approved_by="operator-1")
            self.assertEqual(first_approval["profile"]["revision"], 1)
            with self.assertRaises(ValueError):
                approve_domain_candidate(paths, stale["candidate_id"], approved_by="operator-2")

            rejected = reject_domain_candidate(paths, stale["candidate_id"], rejected_by="operator-2", reason_code="superseded")
            self.assertEqual(rejected["candidate"]["status"], "rejected")
            self.assertEqual(rejected["review"]["reason_code"], "superseded")
            self.assertEqual(rejected["review"]["candidate_id"], stale["candidate_id"])

    def test_g14_retire_requires_exact_scope_and_keeps_active_profile_immutable(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            candidate = self._domain_candidate(paths)
            approved = approve_domain_candidate(paths, candidate["candidate_id"], approved_by="operator-1")
            profile = approved["profile"]
            retired = retire_domain_profile(
                paths,
                profile_id=profile["profile_id"],
                scope_kind="project",
                scope_ref="repo-a",
                revision=profile["revision"],
                retired_by="operator-1",
                reason_code="superseded",
            )
            self.assertEqual(retired["profile"]["status"], "retired")
            self.assertEqual(retired["profile"]["revision"], profile["revision"] + 1)
            with self.assertRaises(ValueError):
                retire_domain_profile(
                    paths,
                    profile_id=profile["profile_id"],
                    scope_kind="project",
                    scope_ref="repo-b",
                    revision=profile["revision"],
                    retired_by="operator-1",
                    reason_code="superseded",
                )

    def test_g15_missing_revision_plans_are_rejected_without_store_mutation(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            now = datetime(2031, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
            retirement = build_memory_retirement(paths, "mem-missing", 4, now=now)
            restore = build_memory_restore(paths, "mem-missing", 4, now=now)
            correction = build_memory_correction(paths, "mem-missing", 4, "corrected", now=now)

            for plan in (retirement, restore, correction):
                with self.subTest(operation=plan.operation_type):
                    self.assertFalse(plan.report["eligible"])
                    self.assertEqual(plan.report["outcomes"][0]["outcome"], "rejected")
            self.assertFalse(paths.memory_dir.exists())

    def test_g15_replay_preserves_explicit_admission_modes_and_retention_tiers(self) -> None:
        now = datetime(2031, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        for admission_state, eligible in (("approved_manual", True), ("approved_auto_safe", True), ("pending_review", False)):
            with self.subTest(admission_state=admission_state):
                status = lifecycle_replay_status(
                    {
                        "record_id": "mem-mode",
                        "revision": 1,
                        "scope": {"kind": "project", "ref": "repo-a"},
                        "admission": {"state": admission_state},
                        "retention": {"class": "standard", "origin": "operator_selected"},
                        "staleness": {"resolution": "resolved"},
                    },
                    now=now,
                )
                self.assertEqual(status["admission_state"], admission_state)
                self.assertEqual(status["retention_class"], "standard")
                self.assertEqual(status["replay_eligible"], eligible)

    def test_g15_expiry_and_unreadable_state_outrank_open_resolution(self) -> None:
        now = datetime(2031, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        open_record = {
            "record_id": "mem-open",
            "revision": 3,
            "scope": {"kind": "project", "ref": "repo-a"},
            "admission": {"state": "approved_manual"},
            "retention": {"class": "standard"},
            "ttl": {"expires_at": "2030-01-01T00:00:00Z"},
            "staleness": {"resolution": "open", "open_expires_at": "2030-01-01T00:00:00Z"},
        }
        expired = lifecycle_replay_status(open_record, now=now)
        self.assertFalse(expired["replay_eligible"])
        self.assertIn(expired["reason_code"], {"expired_standard", "expired", "unreadable_source"})

        unreadable = dict(open_record)
        unreadable["source_status"] = "unreadable"
        unreadable_status = lifecycle_replay_status(unreadable, now=now)
        self.assertFalse(unreadable_status["replay_eligible"])
        self.assertNotEqual(unreadable_status["reason_code"], "review_required")

    def test_g15_receipt_validation_rejects_unknown_outcomes_and_invalid_revision(self) -> None:
        receipt = {
            "schema_version": RECEIPT_SCHEMA_VERSION,
            "operation_id": "op-1",
            "operation_type": "correct",
            "record_id": "mem-1",
            "revision": 2,
            "scope": {"kind": "project", "ref": "repo-a"},
            "actor_class": "operator",
            "created_at": "2031-01-02T03:04:05Z",
            "completed_at": "2031-01-02T03:04:06Z",
            "state": "completed",
            "outcomes": [{"target_id": "record-1", "artifact_kind": "record", "outcome": "written", "reason_code": "ok"}],
        }
        self.assertEqual(validate_lifecycle_receipt(receipt), [])
        broken = json.loads(json.dumps(receipt))
        broken["revision"] = 0
        broken["outcomes"][0]["outcome"] = "silently_promoted"
        errors = validate_lifecycle_receipt(broken)
        self.assertIn("invalid_receipt_revision", errors)
        self.assertIn("invalid_receipt_outcome", errors)

    def test_g15_retrieval_comparison_requires_same_fixture_digest_revision_clock_and_config(self) -> None:
        identity = {
            "schema_version": "omh-memory-evaluation/v1",
            "evaluator_version": "eval-1",
            "corpus_version": "corpus-1",
            "fixture_digest": "fixture-a",
            "retrieval_config_digest": "config-a",
            "clock": "2031-01-02T03:04:05Z",
            "target_revision": "rev-1",
        }
        left = {**identity, "cases": [{"case_id": "scope", "passed": True}]}
        right = {**identity, "fixture_digest": "fixture-b", "cases": [{"case_id": "scope", "passed": False}]}
        comparison = compare_retrieval_reports(left, right)
        self.assertFalse(comparison["comparable"])
        self.assertIn("fixture_digest", comparison["mismatched_identity_fields"])
        self.assertNotIn("regressed_cases", comparison)

    def test_g15_comparable_retrieval_reports_identify_regressions_without_admission_broadening(self) -> None:
        identity = {
            "schema_version": "omh-memory-evaluation/v1",
            "evaluator_version": "eval-1",
            "corpus_version": "corpus-1",
            "fixture_digest": "fixture-a",
            "retrieval_config_digest": "config-a",
            "clock": "2031-01-02T03:04:05Z",
            "target_revision": "rev-1",
        }
        left = {**identity, "cases": [{"case_id": "scope", "passed": True}]}
        right = {**identity, "cases": [{"case_id": "scope", "passed": False}]}
        comparison = compare_retrieval_reports(left, right)
        self.assertTrue(comparison["comparable"])
        self.assertEqual(comparison["regressed_cases"], ["scope"])
        self.assertEqual(comparison["left_identity"]["retrieval_config_digest"], "config-a")


if __name__ == "__main__":
    unittest.main()
