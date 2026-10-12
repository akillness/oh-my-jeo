from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from _cli_harness import run_cli
from _local_package import load_local_package

GOAL_ROOT = Path(__file__).resolve().parents[1]
assert GOAL_ROOT == Path("/Users/jangyoung/.superset/worktrees/omj-hermes-updates-icon")
load_local_package()

from omj.coding.handoff_contract import contract_digest  # noqa: E402
from omj.paths import resolve_paths  # noqa: E402
from omj.wrapper.lifecycle import (  # noqa: E402
    CodingLifecycleError,
    record_codex_dispatch,
    record_codex_result,
    record_codex_verification,
    report_codex_delegation_lifecycle,
    start_codex_delegation_lifecycle,
)
from omj.wrapper.sessions import (  # noqa: E402
    WrapperSessionError,
    create_or_resume_wrapper_session,
    prepare_wrapper_session_handoff,
    record_plan_decision,
    select_wrapper_session_executor,
)


DECLARATION = {
    "inputs": [{"name": "test_path", "input_type": "file", "requirement": "required"}],
    "postconditions": [{"id": "tests", "command": "python -m unittest {test_path}"}],
    "forbidden_actions": ["Do not push to the default branch."],
    "output_shape": {"format": "json", "required_fields": ["status"]},
}


class ReceiptIntegrityRegressionTests(unittest.TestCase):
    @staticmethod
    def _base(root: Path) -> list[str]:
        return ["--omj-home", str(root / ".omj"), "--hermes-home", str(root / ".hermes")]

    def _run(self, root: Path, args: list[str]) -> tuple[int, dict[str, object] | None, str]:
        status, stdout, stderr = run_cli(self._base(root) + args)
        payload = json.loads(stdout) if stdout else None
        return status, payload, stderr

    def _start_session(self, root: Path, executor: str) -> str:
        status, payload, stderr = self._run(
            root,
            ["chat", "session", "start", "risky refactor with private-token-123"],
        )
        self.assertEqual((status, stderr), (0, ""))
        assert payload is not None
        session_id = str(payload["session"]["session_id"])
        for command in (
            ["chat", "session", "accept-plan", session_id],
            ["chat", "session", "select-executor", session_id, executor],
        ):
            status, _payload, stderr = self._run(root, command)
            self.assertEqual((status, stderr), (0, ""), command)
        return session_id

    def _prepare_session(self, root: Path, executor: str) -> tuple[str, Path]:
        contract_path = root / "handoff-contract.json"
        contract_path.write_text(json.dumps(DECLARATION), encoding="utf-8")
        session_id = self._start_session(root, executor)
        status, payload, stderr = self._run(
            root,
            [
                "chat",
                "session",
                "prepare-handoff",
                session_id,
                "Implement a concrete coding change in src/runtime/artifacts.py and run tests",
                "--handoff-contract",
                str(contract_path),
            ],
        )
        self.assertEqual((status, stderr), (0, ""))
        assert payload is not None
        session_path = root / ".omj" / "runtime" / "wrapper_sessions" / session_id / "session.json"
        self.assertEqual(payload["session"]["selected_executor_profile"], executor)
        return session_id, session_path

    @staticmethod
    def _stored_contract(record: dict[str, object]) -> dict[str, object]:
        for key in ("executor_handoff", "prompt_handoff", "runtime_handoff"):
            handoff = record.get(key)
            if isinstance(handoff, dict) and isinstance(handoff.get("handoff_contract"), dict):
                return handoff["handoff_contract"]
        raise AssertionError("prepared session omitted its handoff contract")

    @staticmethod
    def _files_snapshot(directory: Path) -> dict[str, bytes]:
        return {
            str(path.relative_to(directory)): path.read_bytes()
            for path in sorted(directory.rglob("*"))
            if path.is_file()
        }

    def test_codex_chat_handoff_zero_receipt_is_invalidated_by_declaration_tamper_without_verification_write(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            session_id, session_path = self._prepare_session(root, "codex")
            session = json.loads(session_path.read_text(encoding="utf-8"))
            run_id = str(session["current_run_id"])
            run_dir = root / ".omj" / "runtime" / "runs" / run_id
            coding_path = run_dir / "coding_delegation.json"
            coding = json.loads(coding_path.read_text(encoding="utf-8"))
            contract = self._stored_contract(coding)
            pinned_digest = str(coding["handoff_contract_digest"])
            self.assertEqual(pinned_digest, contract_digest(contract))

            for args in (
                ["coding", "lifecycle", "dispatch", "--run", run_id],
                ["coding", "lifecycle", "result", "--run", run_id, "--result", "completed"],
                ["coding", "lifecycle", "verify", "--run", run_id, "--postcondition-exit", "tests=0"],
            ):
                status, _payload, stderr = self._run(root, args)
                self.assertEqual((status, stderr), (0, ""), args)

            receipt_path = run_dir / "handoff_contract_receipt.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual((receipt["status"], receipt["verdict"]), ("observed", "passed"))
            self.assertEqual(receipt["contract_digest"], pinned_digest)

            tampered = dict(coding)
            for key in ("executor_handoff", "prompt_handoff", "runtime_handoff"):
                handoff = tampered.get(key)
                if isinstance(handoff, dict) and isinstance(handoff.get("handoff_contract"), dict):
                    changed = dict(handoff["handoff_contract"])
                    changed["forbidden_actions"] = ["Changed after dispatch."]
                    handoff["handoff_contract"] = changed
                    break
            else:
                self.fail("persisted Codex handoff omitted its contract")
            coding_path.write_text(json.dumps(tampered), encoding="utf-8")

            status, chat_status, stderr = self._run(root, ["chat", "session", "status", session_id])
            self.assertEqual((status, stderr), (0, ""))
            assert chat_status is not None
            runtime_status = chat_status["runtime_status"]
            receipt_status = runtime_status["handoff_contract"]
            self.assertFalse(runtime_status["verification"]["observed"])
            self.assertEqual(receipt_status["status"], "prepared_not_observed")
            self.assertEqual(receipt_status["verdict"], "not_observed")
            self.assertEqual(runtime_status["next_action"], "record_verification_evidence")
            self.assertFalse(chat_status["status_card"]["completion"]["enabled"] if isinstance(chat_status["status_card"].get("completion"), dict) else False)
            self.assertFalse(any(action.get("id") == "report_completion_with_evidence" and action.get("enabled") for action in chat_status["executor_session_status"]["actions"]))

            status, report, stderr = self._run(root, ["coding", "lifecycle", "report", "--run", run_id])
            self.assertEqual((status, stderr), (0, ""))
            assert report is not None
            self.assertFalse(report["can_report_completion"])
            self.assertFalse(report["can_report_terminal_status"])
            self.assertNotEqual(report["next_action"], "report_completion_with_evidence")
            self.assertFalse(report["verification"]["observed"])

    def test_contradictory_receipt_top_level_fields_never_publish_passed_for_codex_and_non_codex(self) -> None:
        for executor in ("codex", "generic"):
            with self.subTest(executor=executor), TemporaryDirectory() as tmp:
                root = Path(tmp)
                session_id, session_path = self._prepare_session(root, executor)
                session = json.loads(session_path.read_text(encoding="utf-8"))
                if executor == "codex":
                    run_id = str(session["current_run_id"])
                    for args in (
                        ["coding", "lifecycle", "dispatch", "--run", run_id],
                        ["coding", "lifecycle", "result", "--run", run_id, "--result", "completed"],
                        ["coding", "lifecycle", "verify", "--run", run_id, "--postcondition-exit", "tests=1"],
                    ):
                        status, _payload, stderr = self._run(root, args)
                        self.assertEqual((status, stderr), (0, ""), args)
                    receipt_path = root / ".omj" / "runtime" / "runs" / run_id / "handoff_contract_receipt.json"
                else:
                    status, _payload, stderr = self._run(
                        root,
                        ["chat", "session", "open-executor", session_id, "--observed", "--external-session-ref", "generic-1"],
                    )
                    self.assertEqual((status, stderr), (0, ""))
                    status, _payload, stderr = self._run(root, ["chat", "session", "record-executor", session_id, "--result", "completed"])
                    self.assertEqual((status, stderr), (0, ""))
                    receipt_path = root / ".omj" / "runtime" / "wrapper_sessions" / session_id / "handoff_contract_receipt.json"
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                receipt["status"] = "observed"
                receipt["verdict"] = "passed"
                receipt["unobserved_postconditions"] = []
                receipt_path.write_text(json.dumps(receipt), encoding="utf-8")

                status, payload, stderr = self._run(root, ["chat", "session", "status", session_id])
                self.assertEqual((status, stderr), (0, ""))
                assert payload is not None
                if executor == "codex":
                    summary = payload["runtime_status"]["handoff_contract"]
                else:
                    summary = payload["executor_session_status"]["handoff_contract_receipt"]
                self.assertEqual(summary["status"], "prepared_not_observed")
                self.assertEqual(summary["verdict"], "not_observed")
                self.assertNotEqual(summary["verdict"], "passed")
                if executor == "codex":
                    self.assertFalse(payload["runtime_status"]["verification"]["observed"])
    def test_digest_drift_rejects_unknown_bool_and_string_exit_evidence_before_wrapper_mutation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            lifecycle = start_codex_delegation_lifecycle(
                paths,
                "Implement a concrete coding change in src/runtime/artifacts.py and run tests",
                source="generic",
                source_metadata={"source_event_id": "g3", "channel_ref": "tests"},
                handoff_contract=DECLARATION,
            )
            run_id = str(lifecycle["run"]["run_id"])
            record_codex_dispatch(paths, run_id)
            record_codex_result(paths, run_id, result="completed")
            run_dir = paths.runtime_runs_dir / run_id
            coding_path = run_dir / "coding_delegation.json"
            coding = json.loads(coding_path.read_text(encoding="utf-8"))
            attached = coding["executor_handoff"]["handoff_contract"]
            attached["forbidden_actions"] = ["Changed after dispatch."]
            coding_path.write_text(json.dumps(coding), encoding="utf-8")
            wrapper_path = run_dir / "wrapper.json"
            before = wrapper_path.read_bytes()
            receipt_path = run_dir / "handoff_contract_receipt.json"
            receipt_before = receipt_path.read_bytes() if receipt_path.exists() else None
            for exits in ({"unknown": 0}, {"tests": True}, {"tests": "0"}):
                with self.subTest(exits=exits):
                    with self.assertRaises(CodingLifecycleError):
                        record_codex_verification(paths, run_id, postcondition_exits=exits)
                    self.assertEqual(wrapper_path.read_bytes(), before)
                    if receipt_before is None:
                        self.assertFalse(receipt_path.exists())
                    else:
                        self.assertEqual(receipt_path.read_bytes(), receipt_before)
                    status = report_codex_delegation_lifecycle(paths, run_id)
                    self.assertFalse(status["verification"]["observed"])

    def test_orphaned_prepared_codex_run_is_not_recovered_across_contract_change_or_absence(self) -> None:
        for retry_contract in ({**DECLARATION, "forbidden_actions": ["Changed before retry."]}, None):
            with self.subTest(contract_present=retry_contract is not None), TemporaryDirectory() as tmp:
                root = Path(tmp)
                paths = resolve_paths(root / ".omj", root / ".hermes")
                message = "Implement a concrete coding change in src/runtime/artifacts.py and run tests"
                started = create_or_resume_wrapper_session(
                    paths,
                    "risky refactor with private-token-123",
                    source="generic",
                    source_metadata={"source_event_id": "orphan", "channel_ref": "tests"},
                )
                session_id = str(started["session"]["session_id"])
                record_plan_decision(paths, session_id, "accept")
                select_wrapper_session_executor(paths, session_id, "codex")
                with patch("omj.wrapper.sessions._link_prepared_handoff_run", side_effect=RuntimeError("simulated crash")):
                    with self.assertRaises(RuntimeError):
                        prepare_wrapper_session_handoff(paths, session_id, message, handoff_contract=DECLARATION)
                session_path = paths.runtime_wrapper_sessions_dir / session_id / "session.json"
                orphan_session = json.loads(session_path.read_text(encoding="utf-8"))
                self.assertEqual(orphan_session["current_run_id"], "")
                orphan_runs = sorted(path.parent.name for path in paths.runtime_runs_dir.glob("*/coding_delegation.json"))
                self.assertEqual(len(orphan_runs), 1)
                orphan_run_id = orphan_runs[0]
                retried = prepare_wrapper_session_handoff(paths, session_id, message, handoff_contract=retry_contract)
                retried_session = retried["session"]
                self.assertNotEqual(retried_session["current_run_id"], orphan_run_id)
                self.assertTrue((paths.runtime_runs_dir / orphan_run_id / "coding_delegation.json").exists())

    def test_coding_delegate_contract_intake_preserves_queued_words_and_refuses_fifo_and_cap_plus_one(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract_path = root / "contract.json"
            contract_path.write_text(json.dumps(DECLARATION), encoding="utf-8")
            status, payload, stderr = self._run(
                root,
                ["coding", "delegate", "risky", "refactor", "--executor", "codex", "--include-message", "--handoff-contract", str(contract_path)],
            )
            self.assertEqual((status, stderr), (0, ""))
            assert payload is not None
            self.assertEqual(payload["message"], "risky refactor")
            self.assertEqual(payload["executor_handoff"]["handoff_contract"]["schema_version"], "handoff_contract/v1")

            fifo_path = root / "contract.fifo"
            os.mkfifo(fifo_path)
            status, payload, stderr = self._run(
                root,
                ["coding", "delegate", "risky", "refactor", "--executor", "codex", "--handoff-contract", str(fifo_path)],
            )
            self.assertEqual((status, payload, stderr), (2, None, "omj: handoff contract must be a regular file\n"))

            oversized_file = root / "oversized.json"
            oversized_file.write_bytes(b"{" + b"a" * 262143 + b"}")
            status, payload, stderr = self._run(
                root,
                ["coding", "delegate", "risky", "refactor", "--executor", "codex", "--handoff-contract", str(oversized_file)],
            )
            self.assertEqual((status, payload, stderr), (2, None, "omj: handoff contract exceeds maximum size of 262144 bytes\n"))

            oversized_inline = '{"x":"' + ("a" * 262137) + '"}'
            self.assertEqual(len(oversized_inline.encode("utf-8")), 262145)
            status, payload, stderr = self._run(
                root,
                ["coding", "delegate", "risky", "refactor", "--executor", "codex", "--handoff-contract", oversized_inline],
            )
            self.assertEqual((status, payload, stderr), (2, None, "omj: handoff contract exceeds maximum size of 262144 bytes\n"))


    def test_malformed_stored_contract_collections_refuse_status_open_and_result_without_mutation(self) -> None:
        malformed = (
            ("inputs scalar", "inputs", "not-a-list"),
            ("postconditions scalar", "postconditions", {"id": "tests"}),
            ("forbidden scalar entry", "forbidden_actions", [123]),
            ("malformed input entry", "inputs", [0]),
            ("malformed postcondition entry", "postconditions", [None]),
        )
        for label, field, value in malformed:
            with self.subTest(case=label), TemporaryDirectory() as tmp:
                root = Path(tmp)
                session_id, session_path = self._prepare_session(root, "generic")
                status, _payload, stderr = self._run(
                    root,
                    ["chat", "session", "open-executor", session_id, "--observed", "--external-session-ref", "generic-1"],
                )
                self.assertEqual((status, stderr), (0, ""))
                session = json.loads(session_path.read_text(encoding="utf-8"))
                contract = self._stored_contract(session)
                contract[field] = value
                session_path.write_text(json.dumps(session), encoding="utf-8")
                session_dir = session_path.parent
                before = self._files_snapshot(session_dir)
                for command in (
                    ["chat", "session", "status", session_id],
                    ["chat", "session", "open-executor", session_id, "--observed", "--external-session-ref", "generic-2"],
                    ["chat", "session", "record-executor", session_id, "--result", "completed"],
                ):
                    status, payload, stderr = self._run(root, command)
                    self.assertEqual(status, 2, command)
                    self.assertIsNone(payload)
                    self.assertNotIn("Traceback", stderr)
                    self.assertEqual(self._files_snapshot(session_dir), before, command)

    def test_chat_prepare_rejects_fifo_and_oversize_contract_without_partial_run_or_session_result(self) -> None:
        for kind in ("fifo", "oversize"):
            with self.subTest(kind=kind), TemporaryDirectory() as tmp:
                root = Path(tmp)
                session_id = self._start_session(root, "codex")
                session_path = root / ".omj" / "runtime" / "wrapper_sessions" / session_id / "session.json"
                session_before = session_path.read_bytes()
                events_path = session_path.with_name("events.jsonl")
                events_before = events_path.read_bytes() if events_path.exists() else None
                contract_path = root / ("contract.fifo" if kind == "fifo" else "contract.json")
                if kind == "fifo":
                    os.mkfifo(contract_path)
                else:
                    contract_path.write_bytes(b"x" * (262_144 + 1))
                status, payload, stderr = self._run(
                    root,
                    ["chat", "session", "prepare-handoff", session_id, "Implement a concrete coding change", "--handoff-contract", str(contract_path)],
                )
                self.assertEqual(status, 2)
                self.assertIsNone(payload)
                self.assertNotIn("Traceback", stderr)
                self.assertEqual(session_path.read_bytes(), session_before)
                runs_root = root / ".omj" / "runtime" / "runs"
                self.assertFalse(runs_root.exists() and any(runs_root.iterdir()))
                if events_before is None:
                    self.assertFalse(events_path.exists())
                else:
                    self.assertEqual(events_path.read_bytes(), events_before)

    def test_document_budget_and_append_only_progress_refuse_regression_and_wrong_unhashed_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "paper.txt"
            source.write_text("document bytes", encoding="utf-8")
            status, plan_payload, stderr = self._run(
                root,
                [
                    "document", "plan", "--source", str(source), "--pages", "300", "--chars", "480000",
                    "--budget-chars", "100000", "--chars-per-page", "1600",
                ],
            )
            self.assertEqual((status, stderr), (0, ""))
            assert plan_payload is not None
            plan = plan_payload["plan"]
            self.assertEqual(plan["range_count"], 5)
            self.assertEqual([entry["pages"] for entry in plan["ranges"]], [
                {"start": 1, "end": 60}, {"start": 61, "end": 120}, {"start": 121, "end": 180},
                {"start": 181, "end": 240}, {"start": 241, "end": 300},
            ])
            self.assertFalse(plan["delegation_hint"]["mode"] == "sequential")
            plan_id = str(plan["plan_id"])
            plan_path = root / ".omj" / "documents" / plan_id / "plan.json"
            for chunk in ("1", "2"):
                status, _payload, stderr = self._run(
                    root,
                    ["document", "mark", "--plan-id", plan_id, "--range", chunk, "--state", "covered", "--source", str(source)],
                )
                self.assertEqual((status, stderr), (0, ""))
            before = plan_path.read_bytes()
            status, payload, stderr = self._run(
                root,
                ["document", "mark", "--plan-id", plan_id, "--range", "1", "--state", "next", "--source", str(source)],
            )
            self.assertEqual(status, 2)
            self.assertIsNone(payload)
            self.assertNotIn("Traceback", stderr)
            self.assertEqual(plan_path.read_bytes(), before)
            stored = json.loads(before)
            self.assertEqual([item["chunk"] for item in stored["progress_history"]], [1, 2])
            self.assertEqual([item["state"] for item in stored["progress_history"]], ["covered", "covered"])

            sensitive = root / ".env"
            wrong_path = root / "other.env"
            sensitive.write_text("TOKEN=private\n", encoding="utf-8")
            wrong_path.write_text("TOKEN=private\n", encoding="utf-8")
            status, sensitive_payload, stderr = self._run(
                root,
                ["document", "plan", "--source", str(sensitive), "--pages", "2", "--chars", "3200", "--budget-chars", "1600", "--chars-per-page", "1600"],
            )
            self.assertEqual((status, stderr), (0, ""))
            assert sensitive_payload is not None
            sensitive_id = str(sensitive_payload["plan"]["plan_id"])
            sensitive_plan = root / ".omj" / "documents" / sensitive_id / "plan.json"
            sensitive_before = sensitive_plan.read_bytes()
            status, payload, stderr = self._run(
                root,
                ["document", "mark", "--plan-id", sensitive_id, "--range", "1", "--state", "covered", "--source", str(wrong_path)],
            )
            self.assertEqual(status, 2)
            self.assertIsNone(payload)
            self.assertIn("source identity changed", stderr)
            self.assertEqual(sensitive_plan.read_bytes(), sensitive_before)


if __name__ == "__main__":
    unittest.main()
