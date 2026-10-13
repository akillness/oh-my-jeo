from __future__ import annotations

import json
import os

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
    scan_governed_memory,
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
    apply_memory_correction,
    apply_memory_reapproval,
    apply_memory_restore,
    apply_memory_retirement,
    build_memory_correction,
    build_memory_reapproval,
    build_memory_restore,
    build_memory_retirement,
    compare_retrieval_reports,
    lifecycle_replay_status,
    make_lifecycle_receipt,
    validate_lifecycle_receipt,
)
import omj.commands.memory as memory_commands


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

    def test_g8_bounded_diagnostic_scan_names_corruption_schema_escape_duplicates_and_pending(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            first = capture_project_memory_candidate(paths, "first release note", source="release-import")
            first_record = approve_project_memory_candidate(paths, first["candidate"]["candidate_id"])["record"]
            second = capture_project_memory_candidate(paths, "second release note", source="release-import")
            second_record = approve_project_memory_candidate(paths, second["candidate"]["candidate_id"])["record"]
            pending = capture_project_memory_candidate(paths, "pending release note", source="release-import")

            records_dir = paths.memory_dir / "records"
            candidates_dir = paths.memory_dir / "candidates"
            pending_payload = json.loads((candidates_dir / f"{pending['candidate']['candidate_id']}.json").read_text(encoding="utf-8"))
            unsupported_candidate_list = candidates_dir / "unsupported-list.json"
            unsupported_candidate_list.write_text(json.dumps({**pending_payload, "schema_version": ["project_memory_candidate/v99"]}), encoding="utf-8")
            unsupported_candidate_mapping = candidates_dir / "unsupported-mapping.json"
            unsupported_candidate_mapping.write_text(json.dumps({**pending_payload, "schema_version": {"version": "project_memory_candidate/v99"}}), encoding="utf-8")
            duplicate = records_dir / "duplicate.json"
            duplicate.write_text(json.dumps(first_record), encoding="utf-8")
            unsupported = records_dir / "unsupported.json"
            unsupported.write_text(json.dumps({**second_record, "schema_version": "project_memory_record/v99"}), encoding="utf-8")
            unsupported_list = records_dir / "unsupported-list.json"
            unsupported_list.write_text(json.dumps({**second_record, "schema_version": ["project_memory_record/v99"]}), encoding="utf-8")
            unsupported_mapping = records_dir / "unsupported-mapping.json"
            unsupported_mapping.write_text(json.dumps({**second_record, "schema_version": {"version": "project_memory_record/v99"}}), encoding="utf-8")
            corrupt = records_dir / "corrupt.json"
            corrupt.write_text("{not-json", encoding="utf-8")
            outside = root / "outside.json"
            outside.write_text(json.dumps(first_record), encoding="utf-8")
            escaped = records_dir / "escaped.json"
            try:
                os.symlink(outside, escaped)
            except OSError as exc:
                self.skipTest(f"symlink fixtures unavailable: {exc}")

            report = build_memory_source_index(paths, source="release-import")

            self.assertEqual(report["selected"]["outcome"], "matched")
            self.assertEqual(report["selected"]["count"], 2)
            self.assertEqual(
                {item["record_id"] for item in report["selected"]["records"]},
                {first_record["record_id"], second_record["record_id"]},
            )
            unreadable_reasons = [item["reason"] for item in report["indeterminate"]["unreadable"]]
            reasons = set(unreadable_reasons)
            self.assertTrue({"duplicate_record", "unsupported_record_schema", "corrupt_json"} <= reasons)
            self.assertGreaterEqual(unreadable_reasons.count("unsupported_record_schema"), 5)
            self.assertTrue(any(item["reason"] in {"symlink_path", "outside_memory_root"} for item in report["indeterminate"]["unreadable"]))
            self.assertNotIn(pending["candidate"]["candidate_id"], json.dumps(report["selected"]))
            self.assertGreaterEqual(report["indeterminate"]["count"], 4)


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

    def test_g8_source_index_refuses_oversized_active_records_as_indeterminate(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            captured = capture_project_memory_candidate(paths, "bounded source record", source="release-import")
            approved = approve_project_memory_candidate(paths, captured["candidate"]["candidate_id"])
            record = approved["record"]
            record_path = paths.memory_dir / "records" / f"{record['record_id']}.json"
            oversized = json.loads(record_path.read_text(encoding="utf-8"))
            oversized["summary"] = "x" * 1_000_100
            record_path.write_text(json.dumps(oversized), encoding="utf-8")
            report = build_memory_source_index(paths, source="release-import")

            self.assertEqual(report["selected"]["count"], 0)
            self.assertEqual(report["selected"]["records"], [])
            self.assertGreaterEqual(report["indeterminate"]["count"], 1)

    def test_g8_scan_refusal_states_are_explicit_for_deep_unreadable_and_byte_budget_inputs(self) -> None:
        for label in ("deep-1500", "deep-20000", "unreadable", "byte-budget"):
            with self.subTest(input=label):
                with TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    paths = resolve_paths(root / ".omj", root / ".hermes")
                    captured = capture_project_memory_candidate(paths, f"refusal fixture {label}", source="operator")
                    record = approve_project_memory_candidate(paths, captured["candidate"]["candidate_id"])["record"]
                    record_path = paths.memory_dir / "records" / f"{record['record_id']}.json"
                    if label.startswith("deep"):
                        depth = 1_500 if label == "deep-1500" else 20_000
                        nested_open = "".join('{"next":' for _ in range(depth))
                        nested_raw = nested_open + json.dumps("leaf") + ("}" * depth)
                        record_json = json.dumps(record)
                        record_path.write_text(record_json[:-1] + ',"extra":' + nested_raw + "}", encoding="utf-8")
                        expected_state = "partial"
                        expected_diagnostic = "corrupt_json"
                    elif label == "unreadable":
                        outside = root / "outside.json"
                        outside.write_text(json.dumps(record), encoding="utf-8")
                        record_path.unlink()
                        record_path.symlink_to(outside)
                        expected_state = "partial"
                        expected_diagnostic = "symlink_path"
                    else:
                        record_path.write_bytes(b"x" * 1_000_001)
                        expected_state = "budget_exceeded"
                        expected_diagnostic = "file_budget_exceeded"

                    scan = scan_governed_memory(paths)

                    self.assertEqual(scan["read_state"], expected_state)
                    self.assertFalse(scan["complete"])
                    self.assertIn(expected_diagnostic, {item["diagnostic"] for item in scan["findings"]})
                    if label == "byte-budget":
                        self.assertTrue(scan["limit_reached"])

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

    def test_restore_reapproval_refuses_destination_and_tombstone_races_without_receipt(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            captured = capture_project_memory_candidate(
                paths,
                "restorable release procedure",
                record_type="procedure",
                source="operator",
                ttl_days=1,
            )
            approved = approve_project_memory_candidate(paths, captured["candidate"]["candidate_id"])
            origin = approved["record"]
            record_id = str(origin["record_id"])
            record_path = paths.memory_dir / "records" / f"{record_id}.json"
            expired = json.loads(record_path.read_text(encoding="utf-8"))
            expired["ttl"] = {"expires_at": "2000-01-01T00:00:00Z", "ttl_days": 1}
            record_path.write_text(json.dumps(expired), encoding="utf-8")

            now = datetime(2031, 1, 2, tzinfo=timezone.utc)
            retirement = build_memory_retirement(paths, record_id, 1, now=now)
            retired = apply_memory_retirement(
                paths,
                retirement,
                transaction_executor=memory_commands._lifecycle_executor,
            )
            self.assertTrue(retired["applied"])
            tombstone_path = paths.memory_dir / "tombstones" / f"retired-{record_id}-r1.json"
            tombstone_before = tombstone_path.read_bytes()

            restore = build_memory_restore(paths, record_id, 1, now=now)
            self.assertTrue(restore.report["eligible"])
            existing_candidates = {
                path.name: path.read_bytes()
                for path in (paths.memory_dir / "candidates").glob("*.json")
            }
            tombstone = json.loads(tombstone_path.read_text(encoding="utf-8"))
            tombstone["tombstoned_at"] = "2031-01-03T00:00:00Z"
            tombstone_path.write_text(json.dumps(tombstone), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "operation_guard_mismatch"):
                apply_memory_restore(paths, restore, transaction_executor=memory_commands._lifecycle_executor)
            self.assertEqual(
                {
                    path.name: path.read_bytes()
                    for path in (paths.memory_dir / "candidates").glob("*.json")
                },
                existing_candidates,
            )
            tombstone_path.write_bytes(tombstone_before)

            restored = apply_memory_restore(paths, restore, transaction_executor=memory_commands._lifecycle_executor)
            self.assertTrue(restored["applied"])
            candidate_path = next(
                path
                for path in (paths.memory_dir / "candidates").glob("*.json")
                if json.loads(path.read_text(encoding="utf-8")).get("lifecycle") == "restore"
            )
            candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
            candidate_before = candidate_path.read_bytes()
            reapproval = build_memory_reapproval(
                paths,
                str(candidate["candidate_id"]),
                reviewer_claim="reviewer",
                now=now,
            )
            self.assertTrue(reapproval.report["eligible"])

            tombstone = json.loads(tombstone_path.read_text(encoding="utf-8"))
            tombstone["tombstoned_at"] = "2031-01-04T00:00:00Z"
            tombstone_path.write_text(json.dumps(tombstone), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "operation_guard_mismatch"):
                apply_memory_reapproval(paths, reapproval, transaction_executor=memory_commands._lifecycle_executor)
            self.assertFalse(record_path.exists())
            self.assertEqual(candidate_path.read_bytes(), candidate_before)
            tombstone_path.write_bytes(tombstone_before)

            reapproval = build_memory_reapproval(
                paths,
                str(candidate["candidate_id"]),
                reviewer_claim="reviewer",
                now=now,
            )
            newer = json.loads((paths.memory_dir / "archive" / f"{record_id}.r1.json").read_text(encoding="utf-8"))
            newer.update(
                {
                    "revision": 10,
                    "review_status": "approved",
                    "admission": {"state": "approved_manual"},
                    "updated_at": "2031-01-04T00:00:00Z",
                }
            )
            record_path.write_text(json.dumps(newer), encoding="utf-8")
            newer_before = record_path.read_bytes()
            with self.assertRaisesRegex(ValueError, "operation_guard_mismatch"):
                apply_memory_reapproval(paths, reapproval, transaction_executor=memory_commands._lifecycle_executor)
            self.assertEqual(record_path.read_bytes(), newer_before)
            self.assertFalse((paths.memory_dir / "reviews" / f"review-{record_id}-r2.json").exists())

    def test_lifecycle_apply_rejects_false_receipts_but_accepts_successful_receipt(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            captured = capture_project_memory_candidate(paths, "receipt-bound correction", source="operator")
            origin = approve_project_memory_candidate(paths, captured["candidate"]["candidate_id"])["record"]
            plan = build_memory_correction(
                paths,
                str(origin["record_id"]),
                int(origin.get("revision", 1)),
                "receipt-bound replacement",
                now=datetime(2031, 1, 2, tzinfo=timezone.utc),
            )
            self.assertTrue(plan.report["eligible"])

            def valid_receipt(outcomes: list[dict[str, object]] | None = None) -> dict[str, object]:
                return make_lifecycle_receipt(plan, outcomes or successes)

            successes = [
                {
                    "target_id": mutation.target_id,
                    "artifact_kind": mutation.artifact_kind,
                    "outcome": {"write": "written", "move": "moved", "delete": "removed"}.get(mutation.action, mutation.action),
                    "reason_code": "ok",
                }
                for mutation in plan.mutations
            ]
            rejected = [{**outcome, "outcome": "rejected", "reason_code": "refused"} for outcome in successes]
            wrong_action = [{**outcome, "outcome": "already_absent", "reason_code": "wrong_action"} if index == 0 else outcome for index, outcome in enumerate(successes)]
            invalid_receipts = {
                "rejected": valid_receipt(rejected),
                "operation": {**valid_receipt(), "operation_id": "other-operation"},
                "operation_type": {**valid_receipt(), "operation_type": "retire"},
                "record": {**valid_receipt(), "record_id": "other-record"},
                "revision": {**valid_receipt(), "revision": int(origin.get("revision", 1)) + 1},
                "scope": {**valid_receipt(), "scope": {"kind": "project", "ref": "other-repo"}},
                "outcome": valid_receipt(wrong_action),
            }
            for label, receipt in invalid_receipts.items():
                with self.subTest(receipt=label):
                    def executor(_paths, _plan, receipt=receipt):
                        return {"receipt": receipt}

                    try:
                        result = apply_memory_correction(paths, plan, transaction_executor=executor)
                    except ValueError as exc:
                        self.assertIn("receipt", str(exc))
                    else:
                        self.assertFalse(result.get("applied", False))

            applied = apply_memory_correction(paths, plan, transaction_executor=memory_commands._lifecycle_executor)
            self.assertTrue(applied["applied"])
            self.assertEqual(applied["receipt"]["state"], "completed")
            self.assertEqual(
                {item["outcome"] for item in applied["receipt"]["outcomes"]},
                {
                    {"write": "written", "move": "moved", "delete": "removed"}.get(mutation.action, mutation.action)
                    for mutation in plan.mutations
                },
            )


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
