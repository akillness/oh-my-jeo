from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from _local_package import load_local_package

load_local_package()

from omj.capabilities.hooks import hook_manifest
from omj.executor_progress import build_progress_binding
from omj.plugin_bundle.omj import metadata
from omj.plugin_bundle.omj.hooks import llm_hooks, session_hooks
from omj.plugin_bundle.omj import runtime_reader
from omj.plugin_bundle.omj.runtime_reader import _progress_bindings


_CLAIM_BOUNDARY = "Executor progress is not result evidence."


def _write_progress_fixture(runtime_dir: Path, *, target_type: str, target_id: str, updated_at: str) -> dict[str, object]:
    binding = build_progress_binding(
        target_type=target_type,
        target_id=target_id,
        executor_profile="codex",
        now=updated_at,
        freshness_seconds=315360000,
        expiry_seconds=315360000,
    )
    progress_dir = runtime_dir / ("runs" if target_type == "run" else "wrapper_sessions") / target_id / "executor_progress"
    progress_dir.mkdir(parents=True)
    (progress_dir / "binding.json").write_text(json.dumps(binding), encoding="utf-8")
    event = {
        "schema_version": "omj_progress_event/v1",
        "binding_id": binding["binding_id"],
        "instance_id": binding["instance_id"],
        "executor_profile": "codex",
        "event_type": "diff_started",
        "status": "running",
        "summary": f"event for {target_id}",
        "observed_at": updated_at,
        "transition_fingerprint": f"fingerprint-{target_id}",
        "claim_boundary": _CLAIM_BOUNDARY,
    }
    report = {
        "schema_version": "omj_progress_report/v1",
        "binding_id": binding["binding_id"],
        "instance_id": binding["instance_id"],
        "executor_profile": "codex",
        "event_type": "diff_started",
        "status": "running",
        "summary": f"report for {target_id}",
        "reported_at": updated_at,
        "claim_boundary": _CLAIM_BOUNDARY,
    }
    (progress_dir / "events.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")
    (progress_dir / "reports.jsonl").write_text(json.dumps(report) + "\n", encoding="utf-8")
    return binding


class ChildProgressParityTests(unittest.TestCase):
    def test_subagent_start_is_a_declared_host_lifecycle_hook(self) -> None:
        manifest = hook_manifest()
        hooks = {item["name"]: item for item in manifest["plugin_hooks"]}

        self.assertIn("subagent_start", metadata.PROVIDED_HOOKS)
        self.assertIn("subagent_start", hooks)
        self.assertIn("child_session_id", hooks["subagent_start"]["payload_fields"])
        self.assertIn("parent_session_id", hooks["subagent_start"]["payload_fields"])

    def test_host_reported_child_suppresses_orchestration_only_in_bound_home_and_session(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            home_a = root / "home-a"
            home_b = root / "home-b"
            message = "Research source-backed behavior, then run ultraqa checks with Codex. [omj-role:reviewer]"

            session_hooks.subagent_start(
                child_session_id="child-a",
                parent_session_id="parent-a",
                omj_home=str(home_a),
                hermes_home=str(root / "hermes-a"),
            )

            child = llm_hooks.pre_llm_call(
                user_message=message,
                session_id="child-a",
                parent_session_id="parent-a",
                omj_home=str(home_a),
                hermes_home=str(root / "hermes-a"),
                platform="subagent",
                is_first_turn=True,
            )
            self.assertIsNotNone(child)
            child_context = str(child["context"])
            self.assertIn("[OMJ Role: reviewer]", child_context)
            self.assertIn("ultraqa", child_context)
            self.assertIn("selected=web-research", child_context)
            self.assertNotIn("selected=ultraprocess", child_context)
            self.assertNotIn("lane=coding_handoff", child_context)
            self.assertNotIn("next_action=prepare_one_cycle_delivery", child_context)
            self.assertNotIn("adjacent_workflows=ralplan", child_context)

            unrelated_parent = llm_hooks.pre_llm_call(
                user_message=message,
                session_id="parent-a",
                omj_home=str(home_a),
                hermes_home=str(root / "hermes-a"),
                platform="hermes",
                is_first_turn=True,
            )
            self.assertIsNotNone(unrelated_parent)
            self.assertIn("selected=ultraprocess", str(unrelated_parent["context"]))

            same_session_in_other_home = llm_hooks.pre_llm_call(
                user_message=message,
                session_id="child-a",
                parent_session_id="parent-a",
                omj_home=str(home_b),
                hermes_home=str(root / "hermes-b"),
                platform="subagent",
                is_first_turn=True,
            )
            self.assertIsNotNone(same_session_in_other_home)
            self.assertIn("selected=ultraprocess", str(same_session_in_other_home["context"]))

    def test_parent_session_id_without_host_lifecycle_evidence_stays_ordinary(self) -> None:
        with TemporaryDirectory() as tmp:
            result = llm_hooks.pre_llm_call(
                user_message="Implement this with Codex and keep the assigned role [omj-role:reviewer].",
                session_id="unregistered-child",
                parent_session_id="parent-only-metadata",
                omj_home=str(Path(tmp) / "home"),
                hermes_home=str(Path(tmp) / "hermes"),
                is_first_turn=True,
            )

            self.assertIsNotNone(result)
            self.assertIn("[OMJ Role: reviewer]", str(result["context"]))
            self.assertIn("selected=ultraprocess", str(result["context"]))

    def test_progress_limit_reads_only_the_newest_valid_binding_logs(self) -> None:
        with TemporaryDirectory() as tmp:
            runtime_dir = Path(tmp) / "runtime"
            older = _write_progress_fixture(
                runtime_dir,
                target_type="run",
                target_id="run-older",
                updated_at="2026-10-10T00:00:00Z",
            )
            newest = _write_progress_fixture(
                runtime_dir,
                target_type="run",
                target_id="run-newest",
                updated_at="2026-10-12T00:00:00Z",
            )
            middle = _write_progress_fixture(
                runtime_dir,
                target_type="run",
                target_id="run-middle",
                updated_at="2026-10-11T00:00:00Z",
            )

            with patch.object(runtime_reader, "_read_jsonl", wraps=runtime_reader._read_jsonl) as read_jsonl:
                items = _progress_bindings(runtime_dir, limit=1)

            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["binding"]["binding_id"], newest["binding_id"])
            self.assertEqual(items[0]["latest_event"]["summary"], "event for run-newest")
            self.assertEqual(items[0]["latest_report"]["summary"], "report for run-newest")
            opened = {Path(call.args[0]) for call in read_jsonl.call_args_list}
            expected = {
                runtime_dir / "runs" / "run-newest" / "executor_progress" / "events.jsonl",
                runtime_dir / "runs" / "run-newest" / "executor_progress" / "reports.jsonl",
            }
            self.assertEqual(opened, expected)
            self.assertEqual(read_jsonl.call_count, 2)
            self.assertNotIn(older["binding_id"], {item["binding"]["binding_id"] for item in items})
            self.assertNotIn(middle["binding_id"], {item["binding"]["binding_id"] for item in items})

    def test_progress_limit_ignores_invalid_bindings_across_run_and_wrapper_roots(self) -> None:
        with TemporaryDirectory() as tmp:
            runtime_dir = Path(tmp) / "runtime"
            valid_run = _write_progress_fixture(
                runtime_dir,
                target_type="run",
                target_id="run-valid",
                updated_at="2026-10-10T00:00:00Z",
            )
            valid_wrapper = _write_progress_fixture(
                runtime_dir,
                target_type="wrapper_session",
                target_id="wrapper-valid",
                updated_at="2026-10-11T00:00:00Z",
            )
            for root_name, target_id in (("runs", "run-invalid"), ("wrapper_sessions", "wrapper-invalid")):
                progress_dir = runtime_dir / root_name / target_id / "executor_progress"
                progress_dir.mkdir(parents=True)
                (progress_dir / "binding.json").write_text(
                    json.dumps({"schema_version": "broken", "binding_id": target_id}),
                    encoding="utf-8",
                )
                (progress_dir / "events.jsonl").write_text("should not be opened\n", encoding="utf-8")
                (progress_dir / "reports.jsonl").write_text("should not be opened\n", encoding="utf-8")

            with patch.object(runtime_reader, "_read_jsonl", wraps=runtime_reader._read_jsonl) as read_jsonl:
                items = _progress_bindings(runtime_dir, limit=1)

            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["binding"]["binding_id"], valid_wrapper["binding_id"])
            self.assertEqual(items[0]["latest_event"]["summary"], "event for wrapper-valid")
            opened = {Path(call.args[0]) for call in read_jsonl.call_args_list}
            expected = {
                runtime_dir / "wrapper_sessions" / "wrapper-valid" / "executor_progress" / "events.jsonl",
                runtime_dir / "wrapper_sessions" / "wrapper-valid" / "executor_progress" / "reports.jsonl",
            }
            self.assertEqual(opened, expected)
            self.assertEqual(read_jsonl.call_count, 2)
            self.assertNotIn(valid_run["binding_id"], {item["binding"]["binding_id"] for item in items})

    def test_progress_reads_live_log_changes_on_each_poll(self) -> None:
        with TemporaryDirectory() as tmp:
            runtime_dir = Path(tmp) / "runtime"
            binding = _write_progress_fixture(
                runtime_dir,
                target_type="run",
                target_id="run-live",
                updated_at="2026-10-12T00:00:00Z",
            )
            progress_dir = runtime_dir / "runs" / "run-live" / "executor_progress"
            first = _progress_bindings(runtime_dir, limit=1)

            changed_event = {
                "schema_version": "omj_progress_event/v1",
                "binding_id": binding["binding_id"],
                "instance_id": binding["instance_id"],
                "executor_profile": "codex",
                "event_type": "tests_started",
                "status": "running",
                "summary": "new live event",
                "observed_at": "2026-10-12T00:01:00Z",
                "transition_fingerprint": "fingerprint-live-2",
                "claim_boundary": _CLAIM_BOUNDARY,
            }
            changed_report = {
                "schema_version": "omj_progress_report/v1",
                "binding_id": binding["binding_id"],
                "instance_id": binding["instance_id"],
                "executor_profile": "codex",
                "event_type": "tests_started",
                "status": "running",
                "summary": "new live report",
                "reported_at": "2026-10-12T00:01:00Z",
                "claim_boundary": _CLAIM_BOUNDARY,
            }
            (progress_dir / "events.jsonl").write_text(json.dumps(changed_event) + "\n", encoding="utf-8")
            (progress_dir / "reports.jsonl").write_text(json.dumps(changed_report) + "\n", encoding="utf-8")
            second = _progress_bindings(runtime_dir, limit=1)

            self.assertEqual(first[0]["latest_event"]["summary"], "event for run-live")
            self.assertEqual(first[0]["latest_report"]["summary"], "report for run-live")
            self.assertEqual(second[0]["latest_event"]["summary"], "new live event")
            self.assertEqual(second[0]["latest_report"]["summary"], "new live report")


if __name__ == "__main__":
    unittest.main()
