from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from _cli_harness import run_cli


class GovernedCliParityTests(unittest.TestCase):
    def _base(self, root: Path) -> list[str]:
        return ["--omj-home", str(root / ".omj"), "--hermes-home", str(root / ".hermes")]

    def _run(self, root: Path, args: list[str]) -> tuple[int, dict[str, object] | None, str]:
        status, stdout, stderr = run_cli(self._base(root) + args)
        return status, json.loads(stdout) if stdout else None, stderr

    def _approve_memory(self, root: Path, summary: str, **flags: str) -> dict[str, object]:
        args = ["memory", "capture", summary]
        for key, value in flags.items():
            args.extend([f"--{key.replace('_', '-')}", value])
        status, payload, stderr = self._run(root, args)
        self.assertEqual((status, stderr), (0, ""))
        assert payload is not None
        candidate = payload["candidate"]
        candidate_id = str(candidate["candidate_id"])
        status, approved, stderr = self._run(root, ["memory", "approve", candidate_id, "--approved-by", "reviewer"])
        self.assertEqual((status, stderr), (0, ""))
        assert approved is not None
        return approved["record"]

    def test_memory_sources_indexes_source_and_source_ref_axes_without_mutation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = self._approve_memory(root, "release note", source="release-import", source_ref="docs/release.md")
            record_path = root / ".omj" / "memory" / "records" / f"{record['record_id']}.json"
            before = record_path.read_bytes()

            status, report, stderr = self._run(root, ["memory", "sources", "--source", "release-import"])
            self.assertEqual((status, stderr), (0, ""))
            assert report is not None
            self.assertEqual(report["schema_version"], "memory_source_index/v1")
            self.assertEqual(report["selected"]["outcome"], "matched")
            self.assertEqual(report["selected"]["records"][0]["matched_axes"], ["source"])
            self.assertEqual(record_path.read_bytes(), before)

            dual = self._approve_memory(root, "dual origin", source="dual-origin", source_ref="dual-origin")
            status, report, stderr = self._run(root, ["memory", "sources", "--source", "dual-origin"])
            self.assertEqual((status, stderr), (0, ""))
            assert report is not None
            self.assertEqual(report["selected"]["records"][0]["record_id"], dual["record_id"])
            self.assertEqual(report["selected"]["records"][0]["matched_axes"], ["source", "source_ref"])

    def test_domain_capture_review_approval_is_scoped_and_tamper_refuses(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            capture_args = [
                "memory", "domain", "capture", "--scope-kind", "project", "--scope-ref", "repo-a",
                "--domain-id", "payments", "--mapping", "refund=refund_flow", "--workflow-hint", "billing-review",
                "--source-class", "operator_supplied", "--source-ref", "review-42", "--observation-count", "2",
                "--confidence", "0.75",
            ]
            status, captured, stderr = self._run(root, capture_args)
            self.assertEqual((status, stderr), (0, ""))
            assert captured is not None
            candidate = captured["candidate"]
            self.assertEqual(candidate["schema_version"], "domain_intelligence_candidate/v1")
            self.assertEqual(candidate["scope"]["kind"], "project")
            candidate_id = str(candidate["candidate_id"])

            status, review, stderr = self._run(root, ["memory", "domain", "review"])
            self.assertEqual((status, stderr), (0, ""))
            assert review is not None
            self.assertEqual(review["pending_count"], 1)
            self.assertEqual(review["cards"][0]["scope"]["kind"], "project")
            self.assertEqual(review["cards"][0]["scope"]["ref"], "repo-a")

            candidate_path = root / ".omj" / "memory" / "domain-intelligence" / "candidates" / f"{candidate_id}.json"
            tampered = json.loads(candidate_path.read_text(encoding="utf-8"))
            tampered["scope"]["ref"] = "repo-b"
            candidate_path.write_text(json.dumps(tampered), encoding="utf-8")
            status, payload, stderr = self._run(root, ["memory", "domain", "approve", candidate_id, "--approved-by", "reviewer"])
            self.assertNotEqual(status, 0)
            self.assertIsNone(payload)
            self.assertIn("profile_identity_mismatch", stderr)
            self.assertFalse((root / ".omj" / "memory" / "domain-intelligence" / "profiles").exists())

    def test_memory_lifecycle_preview_apply_stale_retire_restore_and_receipt_outcomes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            record = self._approve_memory(root, "expiring note", source="cli", source_ref="lifecycle", ttl_days="1")
            record_path = root / ".omj" / "memory" / "records" / f"{record['record_id']}.json"
            payload = json.loads(record_path.read_text(encoding="utf-8"))
            payload["ttl"]["expires_at"] = "2000-01-01T00:00:00Z"
            record_path.write_text(json.dumps(payload), encoding="utf-8")
            record_id = str(record["record_id"])

            status, preview, stderr = self._run(root, ["memory", "retire", record_id, "--revision", "1"])
            self.assertEqual((status, stderr), (0, ""))
            assert preview is not None
            self.assertTrue(preview["plan"]["eligible"])
            self.assertEqual(sum(1 for item in preview["plan"]["manifest"] if item["artifact_kind"] == "record"), 1)
            status, applied, stderr = self._run(root, ["memory", "retire", record_id, "--revision", "1", "--apply"])
            self.assertEqual((status, stderr), (0, ""))
            assert applied is not None
            self.assertEqual(applied["apply"]["receipt"]["state"], "completed")
            self.assertEqual({item["outcome"] for item in applied["apply"]["receipt"]["outcomes"]}, {"moved", "written"})
            archive = root / ".omj" / "memory" / "archive" / f"{record_id}.r1.json"
            self.assertTrue(archive.exists())
            self.assertFalse(record_path.exists())

            status, stale, stderr = self._run(root, ["memory", "retire", record_id, "--revision", "1", "--apply"])
            self.assertNotEqual(status, 0)
            self.assertIn("already_absent", stderr)

            status, restore_preview, stderr = self._run(root, ["memory", "restore", record_id, "--revision", "1"])
            self.assertEqual((status, stderr), (0, ""))
            assert restore_preview is not None
            self.assertTrue(restore_preview["plan"]["eligible"])
            self.assertEqual(sum(1 for item in restore_preview["plan"]["manifest"] if item["artifact_kind"] == "candidate"), 1)
            status, restored, stderr = self._run(root, ["memory", "restore", record_id, "--revision", "1", "--apply"])
            self.assertEqual((status, stderr), (0, ""))
            assert restored is not None
            self.assertEqual(restored["apply"]["receipt"]["operation_type"], "restore")
            self.assertEqual(restored["apply"]["receipt"]["outcomes"][0]["outcome"], "written")

    def test_retrieval_evaluate_is_metadata_only_and_preserves_executor_boundary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = root / "retrieval.json"
            fixture.write_text(json.dumps({"cases": [{"case_id": "c1", "passed": True, "selected": ["r1"]}]}), encoding="utf-8")
            status, report, stderr = self._run(root, ["memory", "evaluate", "--fixture", str(fixture), "--target-revision", "rev-1"])
            self.assertEqual((status, stderr), (0, ""))
            assert report is not None
            self.assertEqual(report["schema_version"], "omj_memory_retrieval_evaluation/v1")
            self.assertEqual(report["case_count"], 1)
            self.assertIn("no model call", report["execution_boundary"])
            self.assertTrue(report["fairness"]["executor_neutral"])

    def test_context_terms_capture_rejects_role_markers_and_preserves_omj_source_identity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            terms = root / "PROJECT_TERMS.md"
            valid = (
                "# Project Terms\n\n"
                "Project terminology only. This file is not agent instructions, routing rules, approval, execution, or evidence. Changes affect OMJ only after explicit review.\n\n"
                "<!-- omj-project-terms/v1 -->\n\n"
                "## domain: delivery\n\n"
                "- term: `dispatch packet` = `handoff`\n"
                "  definition: A prepared package.\n"
                "  say-instead: prepared handoff\n"
            )
            terms.write_text(valid, encoding="utf-8")
            status, payload, stderr = self._run(root, ["context", "terms", "capture", "--source", str(terms), "--json"])
            self.assertEqual((status, stderr), (0, ""))
            assert payload is not None
            self.assertEqual(payload["schema_version"], "omj_project_terms_capture/v1")
            self.assertEqual(payload["captures"][0]["source_class"], "omj_local")
            self.assertTrue(payload["captures"][0]["source_ref"].startswith("pt_sha256:"))
            self.assertFalse(payload["source"]["raw_persisted"])

            terms.write_text(valid + "  role: executor\n", encoding="utf-8")
            status, payload, stderr = self._run(root, ["context", "terms", "capture", "--source", str(terms), "--json"])
            self.assertNotEqual(status, 0)
            self.assertIsNone(payload)
            self.assertIn("unknown_project_terms", stderr)

    def test_provider_chain_blank_model_effort_and_invalid_effort_fail_without_fallback(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = (
                '{"deep":[["", "high"]]}',
                '{"deep":[["model", ""]]}',
                '{"deep":[["model", "invalid"]]}',
            )
            for chain in cases:
                with self.subTest(chain=chain):
                    status, payload, stderr = self._run(root, ["providers", "complexity", "audit", "the", "release", "--chain-json", chain, "--json"])
                    self.assertNotEqual(status, 0)
                    self.assertIsNone(payload)
                    self.assertIn("chain", stderr)
                    self.assertNotIn("recommendation", stderr.lower())

    def test_source_recovery_is_one_url_bounded_gap_without_fetch(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, payload, stderr = self._run(root, [
                "ops", "source-recovery", "--url", "https://vendor.example/docs/limits",
                "--failure-class", "authentication_required", "--capability-available", "--budget", "1", "--attempts", "0",
                "--source-requirement", "primary source",
            ])
            self.assertEqual((status, stderr), (0, ""))
            assert payload is not None
            self.assertEqual(payload["record"]["recovery_attempts"], 0)
            self.assertEqual(payload["record"]["evidence_class"], "none")
            self.assertIn("no retrieval", payload["record"]["claim_boundary"])
            self.assertIsNone(payload["handoff"])

    def test_ops_incident_and_file_lineage_are_cited_redacted_prepared_projections(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "repo"
            (workspace / "src").mkdir(parents=True)
            session = root / "session.jsonl"
            secret = "RAW-USER-PROMPT-SECRET"
            call = {
                "id": "c1", "call_id": "c1", "type": "function", "function": {
                    "name": "read_file", "arguments": json.dumps({"path": "src/app.py"})
                }
            }
            rows = [
                {"session_id": "sess-1", "role": "user", "content": secret, "timestamp": 1.0},
                {"session_id": "sess-1", "role": "assistant", "content": "", "timestamp": 2.0, "tool_calls": [call]},
                {"session_id": "sess-1", "role": "tool", "content": json.dumps({"content": "safe", "error": secret}), "tool_call_id": "c1", "tool_name": "read_file", "timestamp": 3.0},
            ]
            session.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
            status, capsule, stderr = self._run(root, ["ops", "incident-capsule", "--session-record", str(session), "--hermes-session", "sess-1", "--observable", "looping"])
            self.assertEqual((status, stderr), (0, ""))
            assert capsule is not None
            self.assertEqual(capsule["schema_version"], "omj_incident_capsule/v1")
            self.assertEqual(capsule["metadata"]["execution_status"], "prepared")
            self.assertFalse(capsule["metadata"]["historical_execution_observed"])
            self.assertNotIn(secret, json.dumps(capsule))
            self.assertTrue(capsule["incident"]["agent_failure_pattern_hypothesis"]["hypotheses"])

            status, lineage, stderr = self._run(root, ["ops", "file-lineage", "--session-record", str(session), "--hermes-session", "sess-1", "--workspace", str(workspace)])
            self.assertEqual((status, stderr), (0, ""))
            assert lineage is not None
            self.assertEqual(lineage["metadata"]["execution_status"], "prepared")
            self.assertFalse(lineage["metadata"]["file_contents_read"])
            self.assertEqual(lineage["files"][0]["path"], "src/app.py")
            self.assertNotIn(secret, json.dumps(lineage))

    def test_rules_import_preview_apply_foreign_ownership_and_stale_target_refuse_without_overwrite(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            repo = root / "repo"
            repo.mkdir()
            source = repo / ".cursorrules"
            source.write_text("Use bounded local checks.\n", encoding="utf-8")
            skills = root / "skills"
            omj_home = root / ".omj"
            base = ["--omj-home", str(omj_home), "--hermes-home", str(root / ".hermes")]

            status, preview, stderr = run_cli(base + ["rules-import", "--repo-root", str(repo), "--skills-dir", str(skills)])
            self.assertEqual((status, stderr), (0, ""))
            preview_payload = json.loads(preview)
            self.assertEqual(preview_payload["metadata"]["mode"], "preview")
            target_rel = preview_payload["planned"][0]["target"]
            self.assertFalse((skills / target_rel).exists())
            self.assertFalse((omj_home / "skills-import-manifest.json").exists())

            status, applied, stderr = run_cli(base + ["rules-import", "--repo-root", str(repo), "--skills-dir", str(skills), "--apply"])
            self.assertEqual((status, stderr), (0, ""))
            applied_payload = json.loads(applied)
            self.assertEqual(applied_payload["metadata"]["mode"], "apply")
            target = skills / target_rel
            self.assertTrue(target.exists())
            before = target.read_text(encoding="utf-8")

            source.write_text("Changed after prior import.\n", encoding="utf-8")
            target.write_text("foreign local ownership\n", encoding="utf-8")
            status, refused, stderr = run_cli(base + ["rules-import", "--repo-root", str(repo), "--skills-dir", str(skills), "--apply"])
            self.assertEqual((status, stderr), (0, ""))
            refused_payload = json.loads(refused)
            self.assertEqual(refused_payload["refused"][0]["status"], "refused")
            self.assertTrue(any("local modifications" in reason for reason in refused_payload["refused"][0]["refusal_reasons"]))
            self.assertEqual(target.read_text(encoding="utf-8"), "foreign local ownership\n")
            self.assertNotEqual(target.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
