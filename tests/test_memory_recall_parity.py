from __future__ import annotations

import hashlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from _local_package import load_local_package

load_local_package()

from omj.memory import (
    approve_project_memory_candidate,
    build_project_memory_recall_pack,
    capture_project_memory_candidate,
    capture_project_memory_failed_attempt,
)
from omj.paths import resolve_paths
from omj.profiles.setup import write_setup_profile


class RecallParityTests(unittest.TestCase):
    def _approve(self, paths, captured: dict[str, object]) -> dict[str, object]:
        candidate = captured["candidate"]
        assert isinstance(candidate, dict)
        approved = approve_project_memory_candidate(paths, str(candidate["candidate_id"]))
        record = approved["record"]
        assert isinstance(record, dict)
        return record

    def test_unsupported_script_or_emoji_query_matches_eligible_unqueried_recall(self) -> None:
        """Unsupported query text must not make approved memory disappear."""
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            record = self._approve(
                paths,
                capture_project_memory_candidate(
                    paths,
                    "Keep the release checklist next to the deployment notes",
                    record_type="procedure",
                    scope_kind="project",
                    scope_ref="default",
                    tags=["release"],
                ),
            )

            unqueried = build_project_memory_recall_pack(paths, "", executor_target="codex")
            expected_ids = [item["record_id"] for item in unqueried["included_records"]]
            self.assertEqual(expected_ids, [record["record_id"]])
            self.assertEqual(unqueried["scope"], {"kind": "*", "ref": "*"})

            for query in ("δοκιμή", "проверка", "🚀🧪"):
                with self.subTest(query=query):
                    recalled = build_project_memory_recall_pack(paths, query, executor_target="codex")
                    self.assertEqual(
                        [item["record_id"] for item in recalled["included_records"]],
                        expected_ids,
                    )
                    self.assertEqual(recalled["record_count"], unqueried["record_count"])
                    self.assertEqual(recalled["included_records"][0]["scope"], {"kind": "project", "ref": "default"})
                    self.assertEqual(recalled["included_records"][0]["score"], 1)
                    self.assertFalse(recalled["included_records"][0]["failure_first"])
                    self.assertFalse(
                        any(item["reason"] == "no_query_overlap" for item in recalled["excluded_records"])
                    )

    def test_generic_fallback_does_not_promote_unrelated_failure_but_real_overlap_does(self) -> None:
        """Failure-first is gated by a real token/tag hit, not fallback score 1."""
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            useful = self._approve(
                paths,
                capture_project_memory_candidate(
                    paths,
                    "Release checklist requires unittest discovery",
                    record_type="procedure",
                    tags=["release"],
                ),
            )
            failed = self._approve(
                paths,
                capture_project_memory_failed_attempt(
                    paths,
                    "loader cache workaround",
                    cause="loader kept the old module",
                    tags=["loader"],
                ),
            )

            unsupported = build_project_memory_recall_pack(paths, "🚀", executor_target="codex")
            self.assertEqual(
                {item["record_id"] for item in unsupported["included_records"]},
                {useful["record_id"], failed["record_id"]},
            )
            self.assertFalse(any(item["failure_first"] for item in unsupported["included_records"]))

            unrelated = build_project_memory_recall_pack(paths, "release checklist", executor_target="codex")
            self.assertEqual(
                [item["record_id"] for item in unrelated["included_records"]],
                [useful["record_id"]],
            )
            self.assertIn(
                failed["record_id"],
                {item["record_id"] for item in unrelated["excluded_records"]},
            )

            matched_failure = build_project_memory_recall_pack(paths, "loader", executor_target="codex")
            self.assertEqual(matched_failure["included_records"][0]["record_id"], failed["record_id"])
            self.assertTrue(matched_failure["included_records"][0]["failure_first"])

    def test_two_character_ci_and_korean_cjk_bigrams_remain_indexable(self) -> None:
        """Short CI and Korean particle-glued nouns use their source-backed token rules."""
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            ci_record = self._approve(
                paths,
                capture_project_memory_candidate(paths, "CI runs the release verification", tags=["ci"]),
            )
            korean_record = self._approve(
                paths,
                capture_project_memory_candidate(paths, "배포는 승인된 체크리스트로 진행", tags=["korean"]),
            )
            unrelated = self._approve(
                paths,
                capture_project_memory_candidate(paths, "Database migration notes", tags=["database"]),
            )

            ci_recall = build_project_memory_recall_pack(paths, "CI", executor_target="codex")
            self.assertEqual(
                [item["record_id"] for item in ci_recall["included_records"]],
                [ci_record["record_id"]],
            )
            self.assertNotIn(unrelated["record_id"], {item["record_id"] for item in ci_recall["included_records"]})

            korean_recall = build_project_memory_recall_pack(paths, "배포", executor_target="codex")
            self.assertEqual(
                [item["record_id"] for item in korean_recall["included_records"]],
                [korean_record["record_id"]],
            )
            self.assertNotIn(unrelated["record_id"], {item["record_id"] for item in korean_recall["included_records"]})

    def test_shared_eligibility_gates_out_rank_relevance_and_allow_stale(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            records: dict[str, tuple[dict[str, object], Path]] = {}
            for label in ("eligible", "expired", "pending", "bad-ttl", "unreadable-source", "stale"):
                captured = capture_project_memory_candidate(
                    paths,
                    f"needle {label}",
                    record_type="procedure",
                    source="operator",
                    tags=[label],
                )
                record = self._approve(paths, captured)
                path = paths.memory_dir / "records" / f"{record['record_id']}.json"
                records[label] = (record, path)

            expired, _ = records["expired"]
            expired["ttl"] = {"expires_at": "2000-01-01T00:00:00Z", "ttl_days": 1}
            pending, _ = records["pending"]
            pending["admission"] = {"state": "pending_review"}
            bad_ttl, _ = records["bad-ttl"]
            bad_ttl["ttl"] = {"expires_at": "not-a-timestamp", "ttl_days": 1}
            unreadable, _ = records["unreadable-source"]
            unreadable["source_status"] = "unreadable"
            stale, _ = records["stale"]
            stale["staleness"] = {"stale_after": "2000-01-01T00:00:00Z", "review_due_at": "2000-01-01T00:00:00Z"}
            for record, path in records.values():
                path.write_text(json.dumps(record), encoding="utf-8")

            pack = build_project_memory_recall_pack(paths, "needle", executor_target="codex")
            included = {item["record_id"] for item in pack["included_records"]}
            excluded = {item["record_id"]: item["reason"] for item in pack["excluded_records"]}
            self.assertEqual(included, {records["eligible"][0]["record_id"]})
            self.assertEqual(excluded[expired["record_id"]], "expired")
            self.assertIn(excluded[pending["record_id"]], {"not_approved", "pending_review"})
            self.assertIn(excluded[bad_ttl["record_id"]], {"malformed_ttl", "unreadable_retention"})
            self.assertIn(excluded[unreadable["record_id"]], {"unreadable_source", "source_unreadable"})
            self.assertIn(excluded[stale["record_id"]], {"stale", "review_due"})

            with_stale = build_project_memory_recall_pack(paths, "needle", executor_target="codex", include_stale=True)
            stale_ids = {item["record_id"] for item in with_stale["included_records"]}
            self.assertIn(stale["record_id"], stale_ids)
            self.assertNotIn(expired["record_id"], stale_ids)


    def test_governed_recall_rejects_each_invalid_expiry_and_poison_marker(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            fixtures: dict[str, tuple[dict[str, object], Path]] = {}
            for label in (
                "retention-expired",
                "retention-malformed",
                "source-changed",
                "source-unreadable",
                "revision-zero",
                "superseded",
                "contaminated",
                "stale",
            ):
                record = self._approve(
                    paths,
                    capture_project_memory_candidate(
                        paths,
                        f"needle {label}",
                        record_type="procedure",
                        source="operator",
                        tags=[label],
                    ),
                )
                record_path = paths.memory_dir / "records" / f"{record['record_id']}.json"
                fixtures[label] = (record, record_path)

            fixtures["retention-expired"][0].update(
                {
                    "ttl": {"expires_at": "2999-01-01T00:00:00Z", "ttl_days": 1},
                    "retention": {"class": "standard", "expires_at": "2000-01-01T00:00:00Z"},
                }
            )
            fixtures["retention-malformed"][0].update(
                {
                    "ttl": {"expires_at": "2999-01-01T00:00:00Z", "ttl_days": 1},
                    "retention": {"class": "standard", "expires_at": "not-a-timestamp"},
                }
            )
            fixtures["source-changed"][0]["source_evidence"] = {"status": "changed"}
            fixtures["source-unreadable"][0]["source_evidence"] = {"status": "unreadable"}
            fixtures["revision-zero"][0]["revision"] = 0
            fixtures["superseded"][0]["superseded_by"] = "newer-record"
            fixtures["contaminated"][0]["contamination_class"] = "prompt_injection"
            fixtures["stale"][0]["staleness"] = {
                "stale_after": "2000-01-01T00:00:00Z",
                "review_due_at": "2000-01-01T00:00:00Z",
            }
            for record, record_path in fixtures.values():
                record_path.write_text(json.dumps(record), encoding="utf-8")

            pack = build_project_memory_recall_pack(paths, "needle", executor_target="codex")
            included = {item["record_id"] for item in pack["included_records"]}
            excluded = {item["record_id"]: item["reason"] for item in pack["excluded_records"]}
            self.assertEqual(included, set())
            allowed_reasons = {
                "retention-expired": {"expired", "expired_standard"},
                "retention-malformed": {"malformed_ttl", "unreadable_retention", "unreadable_expiry"},
                "source-changed": {"source_changed"},
                "source-unreadable": {"unreadable_source", "source_unreadable"},
                "revision-zero": {"invalid_revision"},
                "superseded": {"superseded", "superseded_record"},
                "contaminated": {"contaminated", "contamination"},
                "stale": {"stale", "review_due", "stale_review_required"},
            }
            for label, (record, _) in fixtures.items():
                with self.subTest(label=label):
                    self.assertIn(record["record_id"], excluded)
                    self.assertIn(excluded[record["record_id"]], allowed_reasons[label])

            with_stale = build_project_memory_recall_pack(
                paths,
                "needle",
                executor_target="codex",
                include_stale=True,
            )
            stale_ids = {item["record_id"] for item in with_stale["included_records"]}
            self.assertIn(fixtures["stale"][0]["record_id"], stale_ids)
            for label, (record, _) in fixtures.items():
                if label != "stale":
                    with self.subTest(include_stale=label):
                        self.assertNotIn(record["record_id"], stale_ids)

    def test_recall_rejects_changed_or_unreadable_declared_source_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            source_path = root / "source.txt"
            source_path.write_text("original source", encoding="utf-8")
            canonical_source_path = source_path.resolve()
            digest = hashlib.sha256(canonical_source_path.read_bytes()).hexdigest()
            symlink_path = root / "source-link.txt"
            symlink_path.symlink_to(source_path)
            oversized_path = root / "oversized-source.txt"
            oversized_path.write_bytes(b"x" * 1_000_001)
            oversized_digest = hashlib.sha256(oversized_path.read_bytes()).hexdigest()
            fixtures: dict[str, tuple[dict[str, object], set[str]]] = {}
            for label, evidence, reasons in (
                (
                    "changed",
                    {"path": str(source_path), "sha256": digest},
                    {"source_changed", "source_unreadable", "unreadable_source"},
                ),
                (
                    "unreadable",
                    {"path": str(root / "missing-source.txt"), "sha256": "0" * 64},
                    {"source_unreadable", "unreadable_source"},
                ),
                (
                    "symlink",
                    {"path": str(symlink_path), "sha256": digest},
                    {"source_unreadable", "unreadable_source"},
                ),
                (
                    "oversized",
                    {"path": str(oversized_path), "sha256": oversized_digest},
                    {"source_unreadable", "unreadable_source"},
                ),
            ):
                captured = capture_project_memory_candidate(
                    paths,
                    f"needle direct-source-{label}",
                    record_type="procedure",
                    source="operator",
                )
                record = self._approve(paths, captured)
                record["source_evidence"] = evidence
                record_path = paths.memory_dir / "records" / f"{record['record_id']}.json"
                record_path.write_text(json.dumps(record), encoding="utf-8")
                fixtures[label] = (record, reasons)

            source_path.write_text("changed source", encoding="utf-8")
            recall = build_project_memory_recall_pack(paths, "needle", executor_target="codex")
            self.assertFalse(recall["included_records"])
            excluded = {item["record_id"]: item["reason"] for item in recall["excluded_records"]}
            for label, (record, reasons) in fixtures.items():
                with self.subTest(label=label):
                    self.assertIn(record["record_id"], excluded)
                    self.assertIn(excluded[record["record_id"]], reasons)

    def test_legacy_approved_v1_record_remains_recallable(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            captured = capture_project_memory_candidate(paths, "legacy deployment procedure", record_type="procedure", source="operator")
            record = self._approve(paths, captured)
            record_path = paths.memory_dir / "records" / f"{record['record_id']}.json"
            legacy = json.loads(record_path.read_text(encoding="utf-8"))
            legacy["schema_version"] = "project_memory_record/v1"
            legacy.pop("source_class", None)
            legacy.pop("admission", None)
            legacy.pop("retention", None)
            record_path.write_text(json.dumps(legacy), encoding="utf-8")
            recall = build_project_memory_recall_pack(paths, "legacy", executor_target="codex")
            self.assertEqual([item["record_id"] for item in recall["included_records"]], [record["record_id"]])
    def test_canonical_recall_rejects_explicit_empty_admission_state_but_accepts_absent_legacy_admission(self) -> None:
        for state in (None, ""):
            with self.subTest(admission_state=state):
                with TemporaryDirectory() as tmp:
                    paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
                    record = self._approve(
                        paths,
                        capture_project_memory_candidate(
                            paths,
                            "legacy admission compatibility",
                            record_type="procedure",
                            source="operator",
                        ),
                    )
                    record_path = paths.memory_dir / "records" / f"{record['record_id']}.json"
                    persisted = json.loads(record_path.read_text(encoding="utf-8"))
                    persisted["review_status"] = "approved"
                    persisted["admission"] = {"state": state}
                    record_path.write_text(json.dumps(persisted), encoding="utf-8")

                    recall = build_project_memory_recall_pack(paths, "legacy admission", executor_target="codex")

                    self.assertEqual(recall["included_records"], [])
                    excluded = {row["record_id"]: row["reason"] for row in recall["excluded_records"]}
                    self.assertEqual(excluded[record["record_id"]], "not_approved")

        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            record = self._approve(
                paths,
                capture_project_memory_candidate(
                    paths,
                    "legacy admission compatibility",
                    record_type="procedure",
                    source="operator",
                ),
            )
            record_path = paths.memory_dir / "records" / f"{record['record_id']}.json"
            persisted = json.loads(record_path.read_text(encoding="utf-8"))
            persisted.pop("admission", None)
            persisted["review_status"] = "approved"
            record_path.write_text(json.dumps(persisted), encoding="utf-8")

            recall = build_project_memory_recall_pack(paths, "legacy admission", executor_target="codex")

            self.assertEqual([row["record_id"] for row in recall["included_records"]], [record["record_id"]])

    def test_fallback_respects_project_scope_review_stale_and_expiry_gates(self) -> None:
        """Recall fallback changes token eligibility only, never governance gates."""
        with TemporaryDirectory() as tmp:
            paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
            fresh = self._approve(
                paths,
                capture_project_memory_candidate(
                    paths,
                    "Stable project release guidance",
                    scope_kind="project",
                    scope_ref="default",
                    stale_after_days=30,
                ),
            )
            stale = self._approve(
                paths,
                capture_project_memory_candidate(
                    paths,
                    "Old project guidance",
                    scope_kind="project",
                    scope_ref="default",
                    stale_after_days=-1,
                ),
            )
            expired = self._approve(
                paths,
                capture_project_memory_candidate(
                    paths,
                    "Expired episode guidance",
                    record_type="episode",
                    scope_kind="project",
                    scope_ref="default",
                    ttl_days=-1,
                ),
            )
            target = self._approve(
                paths,
                capture_project_memory_candidate(
                    paths,
                    "Target-only guidance",
                    scope_kind="target",
                    scope_ref="mobile",
                ),
            )
            pending = capture_project_memory_candidate(paths, "Pending unreviewed guidance")
            self.assertEqual(pending["candidate"]["status"], "pending_review")

            default_scope = build_project_memory_recall_pack(paths, "δοκιμή", executor_target="codex")
            unqueried_scope = build_project_memory_recall_pack(paths, "", executor_target="codex")
            explicit_scope = build_project_memory_recall_pack(
                paths,
                "δοκιμή",
                executor_target="codex",
                scope_kind="project",
                scope_ref="default",
            )
            kind_only_scope = build_project_memory_recall_pack(
                paths,
                "δοκιμή",
                executor_target="codex",
                scope_kind="project",
            )
            ref_only_scope = build_project_memory_recall_pack(
                paths,
                "δοκιμή",
                executor_target="codex",
                scope_ref="default",
            )
            self.assertEqual(default_scope["scope"], {"kind": "*", "ref": "*"})
            self.assertEqual(kind_only_scope["scope"], {"kind": "project", "ref": "*"})
            self.assertEqual(ref_only_scope["scope"], {"kind": "*", "ref": "default"})
            self.assertEqual(explicit_scope["scope"], {"kind": "project", "ref": "default"})
            self.assertEqual(
                [item["record_id"] for item in kind_only_scope["included_records"]],
                [fresh["record_id"]],
            )
            self.assertEqual(
                [item["record_id"] for item in ref_only_scope["included_records"]],
                [fresh["record_id"]],
            )
            default_ids = [item["record_id"] for item in default_scope["included_records"]]
            unqueried_ids = [item["record_id"] for item in unqueried_scope["included_records"]]
            self.assertEqual(default_ids, unqueried_ids)
            self.assertIn(fresh["record_id"], default_ids)
            self.assertIn(target["record_id"], default_ids)
            self.assertEqual(
                [item["record_id"] for item in explicit_scope["included_records"]],
                [fresh["record_id"]],
            )
            excluded = {item["record_id"]: item["reason"] for item in default_scope["excluded_records"]}
            self.assertEqual(excluded[stale["record_id"]], "stale")
            self.assertEqual(excluded[expired["record_id"]], "expired")
            self.assertNotIn(
                "Pending unreviewed guidance",
                {item["summary"] for item in default_scope["included_records"]},
            )

            with_stale = build_project_memory_recall_pack(
                paths,
                "δοκιμή",
                executor_target="codex",
                include_stale=True,
            )
            self.assertEqual(
                {item["record_id"] for item in with_stale["included_records"]},
                {fresh["record_id"], stale["record_id"], target["record_id"]},
            )
            self.assertNotIn(expired["record_id"], {item["record_id"] for item in with_stale["included_records"]})

            with_stale_scoped = build_project_memory_recall_pack(
                paths,
                "δοκιμή",
                executor_target="codex",
                scope_kind="project",
                scope_ref="default",
                include_stale=True,
            )
            self.assertEqual(
                {item["record_id"] for item in with_stale_scoped["included_records"]},
                {fresh["record_id"], stale["record_id"]},
            )
            self.assertNotIn(expired["record_id"], {item["record_id"] for item in with_stale_scoped["included_records"]})

            write_setup_profile(paths, memory_mode="off")
            disabled_unscoped = build_project_memory_recall_pack(paths, "δοκιμή", executor_target="codex")
            disabled_kind_only = build_project_memory_recall_pack(
                paths,
                "δοκιμή",
                executor_target="codex",
                scope_kind="project",
            )
            disabled_explicit = build_project_memory_recall_pack(
                paths,
                "δοκιμή",
                executor_target="codex",
                scope_kind="project",
                scope_ref="default",
            )
            self.assertFalse(disabled_unscoped["enabled"])
            self.assertEqual(disabled_unscoped["scope"], {"kind": "*", "ref": "*"})
            self.assertEqual(disabled_kind_only["scope"], {"kind": "project", "ref": "*"})
            self.assertEqual(disabled_explicit["scope"], {"kind": "project", "ref": "default"})
            self.assertEqual(disabled_unscoped["included_records"], [])


if __name__ == "__main__":
    unittest.main()
