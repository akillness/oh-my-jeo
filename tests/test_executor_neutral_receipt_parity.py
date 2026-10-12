from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()
from omj.coding.handoff_contract import contract_digest
from omj.paths import resolve_paths
from omj.wrapper.executor_sessions import (
    ExecutorSessionError,
    build_executor_session_status,
    open_executor_session,
    record_executor_session_result,
    snapshot_executor_session_handoff,
)
from omj.wrapper.sessions import (
    create_or_resume_wrapper_session,
    prepare_wrapper_session_handoff,
    record_plan_decision,
    select_wrapper_session_executor,
)


class ExecutorNeutralReceiptParityTests(unittest.TestCase):
    _DECLARATION = {
        "inputs": [{"name": "test_path", "input_type": "file", "requirement": "required"}],
        "postconditions": [
            {"id": "tests", "command": "python -m unittest {test_path}"},
            {"id": "lint", "command": "python -m compileall {test_path}"},
        ],
        "forbidden_actions": ["Do not push to the default branch."],
        "output_shape": {"format": "json", "required_fields": ["status"]},
    }

    @staticmethod
    def _base(root: Path) -> list[str]:
        return ["--omj-home", str(root / ".omj"), "--hermes-home", str(root / ".hermes")]

    @staticmethod
    def _receipt_path(paths: Any, session_id: str) -> Path:
        return paths.runtime_wrapper_sessions_dir / session_id / "handoff_contract_receipt.json"

    def _prepare(self, root: Path, executor: str, *, declaration: dict[str, object] | None = None) -> tuple[Any, str, dict[str, Any]]:
        paths = resolve_paths(root / ".omj", root / ".hermes")
        message = "risky refactor"
        started = create_or_resume_wrapper_session(paths, message, source="generic")
        session_id = str(started["session"]["session_id"])
        record_plan_decision(paths, session_id, "accept")
        select_wrapper_session_executor(paths, session_id, executor)
        prepare_kwargs = {"handoff_contract": declaration} if declaration is not None else {}
        prepared = prepare_wrapper_session_handoff(paths, session_id, message, **prepare_kwargs)
        snapshot_executor_session_handoff(paths, session_id)
        stored = json.loads(
            (paths.runtime_wrapper_sessions_dir / session_id / "handoff_contract.json").read_text(encoding="utf-8")
        ) if declaration is not None else {}
        return paths, session_id, stored

    def _open(self, paths: Any, session_id: str, executor: str) -> None:
        opened = open_executor_session(
            paths,
            session_id,
            observed=True,
            external_session_ref=f"{executor}-session-1",
            evidence_refs=[f"{executor}-handoff"],
        )
        self.assertEqual(opened["status"]["result"], "not_observed")

    def test_claude_code_hermes_and_generic_receipts_round_trip_through_owned_session_artifacts(self) -> None:
        for executor in ("claude-code", "hermes", "generic"):
            with self.subTest(executor=executor), TemporaryDirectory() as tmp:
                paths, session_id, stored_contract = self._prepare(Path(tmp), executor, declaration=self._DECLARATION)
                session_dir = paths.runtime_wrapper_sessions_dir / session_id
                session_json_before = (session_dir / "session.json").read_bytes()
                self._open(paths, session_id, executor)

                result = record_executor_session_result(
                    paths,
                    session_id,
                    result="completed",
                    evidence_refs=["executor-receipt"],
                    postcondition_exit_statuses={"tests": 0, "lint": 0},
                )
                receipt = json.loads(self._receipt_path(paths, session_id).read_text(encoding="utf-8"))
                self.assertEqual(receipt["status"], "observed")
                self.assertEqual(receipt["verdict"], "passed")
                self.assertEqual(receipt["contract_digest"], contract_digest(stored_contract))
                self.assertEqual([row["status"] for row in receipt["postconditions"]], ["passed", "passed"])
                self.assertEqual(result["status"]["handoff_contract_receipt"]["verdict"], "passed")
                self.assertEqual(result["status"]["handoff_contract_receipt"]["status"], "observed")
                status = build_executor_session_status(paths, json.loads((session_dir / "session.json").read_text(encoding="utf-8")))
                self.assertEqual(status["handoff_contract_receipt"]["status"], "observed")
                self.assertEqual(status["handoff_contract_receipt"]["verdict"], "passed")
                session_json = json.loads(session_json_before)
                self.assertNotIn("result_observed", session_json)

    def test_missing_exit_mapping_persists_prepared_not_observed_receipt(self) -> None:
        with TemporaryDirectory() as tmp:
            paths, session_id, _ = self._prepare(Path(tmp), "generic", declaration=self._DECLARATION)
            self._open(paths, session_id, "generic")
            result = record_executor_session_result(paths, session_id, result="completed")
            receipt = json.loads(self._receipt_path(paths, session_id).read_text(encoding="utf-8"))
            self.assertEqual(receipt["status"], "prepared_not_observed")
            self.assertEqual(receipt["verdict"], "not_observed")
            self.assertEqual(receipt["unobserved_postconditions"], ["tests", "lint"])
            self.assertEqual(result["status"]["handoff_contract_receipt"]["verdict"], "not_observed")

    def test_nonzero_exit_persists_observed_failed_receipt_and_never_claims_verification(self) -> None:
        with TemporaryDirectory() as tmp:
            paths, session_id, _ = self._prepare(Path(tmp), "claude-code", declaration=self._DECLARATION)
            self._open(paths, session_id, "claude-code")
            result = record_executor_session_result(
                paths,
                session_id,
                result="completed",
                postcondition_exit_statuses={"tests": 1, "lint": 0},
            )
            receipt = json.loads(self._receipt_path(paths, session_id).read_text(encoding="utf-8"))
            self.assertEqual((receipt["status"], receipt["verdict"]), ("observed", "failed"))
            self.assertEqual(receipt["postconditions"][0]["exit_status"], 1)

    def test_bool_string_and_unknown_exit_statuses_are_rejected_without_receipt_mutation(self) -> None:
        for evidence in ({"tests": True}, {"tests": "0"}, {"unknown": 0}):
            with self.subTest(evidence=evidence), TemporaryDirectory() as tmp:
                paths, session_id, _ = self._prepare(Path(tmp), "generic", declaration=self._DECLARATION)
                self._open(paths, session_id, "generic")
                receipt_path = self._receipt_path(paths, session_id)
                with self.assertRaises(ExecutorSessionError):
                    record_executor_session_result(
                        paths,
                        session_id,
                        result="completed",
                        postcondition_exit_statuses=evidence,
                    )
                self.assertFalse(receipt_path.exists())

    def test_changed_stored_handoff_and_wrong_home_refuse_receipt_recording(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths, session_id, contract = self._prepare(root, "generic", declaration=self._DECLARATION)
            self._open(paths, session_id, "generic")
            handoff_path = paths.runtime_wrapper_sessions_dir / session_id / "handoff_contract.json"
            changed = dict(contract)
            changed["forbidden_actions"] = ["Changed after preparation."]
            handoff_path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaisesRegex(ExecutorSessionError, "changed after preparation"):
                record_executor_session_result(
                    paths,
                    session_id,
                    result="completed",
                    postcondition_exit_statuses={"tests": 0, "lint": 0},
                )
            self.assertFalse(self._receipt_path(paths, session_id).exists())

            wrong_paths = resolve_paths(root / "wrong" / ".omj", root / "wrong" / ".hermes")
            with self.assertRaises(FileNotFoundError):
                record_executor_session_result(
                    wrong_paths,
                    session_id,
                    result="completed",
                    postcondition_exit_statuses={"tests": 0, "lint": 0},
                )

    def test_no_declaration_preserves_result_behavior_but_rejects_exit_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            paths, session_id, _ = self._prepare(Path(tmp), "generic")
            self._open(paths, session_id, "generic")
            result = record_executor_session_result(paths, session_id, result="completed")
            self.assertEqual(result["status"]["result"], "completed")
            self.assertNotIn("handoff_contract_receipt", result["status"])
            with self.assertRaisesRegex(ExecutorSessionError, "require a declared handoff contract"):
                record_executor_session_result(
                    paths,
                    session_id,
                    result="completed",
                    postcondition_exit_statuses={"tests": 0},
                )

    def test_cli_record_executor_consumes_repeatable_postcondition_exit_flags(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths, session_id, contract = self._prepare(root, "claude-code", declaration=self._DECLARATION)
            self._open(paths, session_id, "claude-code")
            status, stdout, stderr = run_cli(
                self._base(root)
                + [
                    "chat",
                    "session",
                    "record-executor",
                    session_id,
                    "--result",
                    "completed",
                    "--postcondition-exit",
                    "tests=0",
                    "--postcondition-exit",
                    "lint=2",
                ]
            )
            self.assertEqual((status, stderr), (0, ""))
            payload = json.loads(stdout)
            receipt = json.loads(self._receipt_path(paths, session_id).read_text(encoding="utf-8"))
            self.assertEqual(payload["status"]["handoff_contract_receipt"]["verdict"], "failed")
            self.assertEqual(receipt["contract_digest"], contract_digest(contract))
            self.assertEqual(receipt["postconditions"][1]["exit_status"], 2)


    def test_cli_prepare_handoff_contract_reaches_each_selected_executor_receipt(self) -> None:
        for executor in ("claude-code", "hermes", "generic"):
            with self.subTest(executor=executor), TemporaryDirectory() as tmp:
                root = Path(tmp)
                declaration_path = root / "handoff-contract.json"
                declaration_path.write_text(json.dumps(self._DECLARATION), encoding="utf-8")
                message = "risky refactor"
                status, stdout, stderr = run_cli(self._base(root) + ["chat", "session", "start", message])
                self.assertEqual((status, stderr), (0, ""))
                session_id = json.loads(stdout)["session"]["session_id"]
                for args in (
                    ["chat", "session", "accept-plan", session_id],
                    ["chat", "session", "select-executor", session_id, executor],
                    [
                        "chat",
                        "session",
                        "prepare-handoff",
                        session_id,
                        message,
                        "--handoff-contract",
                        str(declaration_path),
                    ],
                ):
                    status, _stdout, stderr = run_cli(self._base(root) + args)
                    self.assertEqual((status, stderr), (0, ""), args)
                status, _stdout, stderr = run_cli(
                    self._base(root)
                    + [
                        "chat",
                        "session",
                        "open-executor",
                        session_id,
                        "--observed",
                        "--external-session-ref",
                        f"{executor}-cli-session",
                    ]
                )
                self.assertEqual((status, stderr), (0, ""))
                status, stdout, stderr = run_cli(
                    self._base(root)
                    + [
                        "chat",
                        "session",
                        "record-executor",
                        session_id,
                        "--result",
                        "completed",
                        "--postcondition-exit",
                        "tests=0",
                        "--postcondition-exit",
                        "lint=0",
                    ]
                )
                self.assertEqual((status, stderr), (0, ""))
                payload = json.loads(stdout)
                status, status_stdout, stderr = run_cli(self._base(root) + ["chat", "session", "status", session_id])
                self.assertEqual((status, stderr), (0, ""))
                status_payload = json.loads(status_stdout)
                receipt_status = payload["status"]["handoff_contract_receipt"]
                status_receipt = status_payload["executor_session_status"]["handoff_contract_receipt"]
                self.assertEqual((receipt_status["status"], receipt_status["verdict"]), ("observed", "passed"))
                self.assertEqual((status_receipt["status"], status_receipt["verdict"]), ("observed", "passed"))
                paths = resolve_paths(root / ".omj", root / ".hermes")
                receipt = json.loads(self._receipt_path(paths, session_id).read_text(encoding="utf-8"))
                self.assertEqual(receipt["status"], "observed")
                self.assertEqual(receipt["verdict"], "passed")

if __name__ == "__main__":
    unittest.main()
