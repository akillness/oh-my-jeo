from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
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
