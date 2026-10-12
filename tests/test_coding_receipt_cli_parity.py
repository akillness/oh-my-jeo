from __future__ import annotations

import json
import socket
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()
from omj.paths import resolve_paths

from omj.profiles.setup import write_setup_profile
from omj.profiles.transport import SETUP_PROFILE_PACK_SCHEMA_VERSION


class CodingReceiptCliParityTests(unittest.TestCase):
    @staticmethod
    def _base(root: Path) -> list[str]:
        return ["--omj-home", str(root / ".omj"), "--hermes-home", str(root / ".hermes")]

    def _run(self, root: Path, args: list[str], *, stdin_text: str = "") -> tuple[int, dict[str, object] | None, str]:
        status, stdout, stderr = run_cli(self._base(root) + args, stdin_text=stdin_text)
        payload: dict[str, object] | None = json.loads(stdout) if stdout else None
        return status, payload, stderr

    def test_setup_profile_export_preview_apply_and_tamper_refusal_are_cli_observable(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            source_paths = resolve_paths(source / ".omj", source / ".hermes")
            write_setup_profile(
                source_paths,
                ["codex-lifecycle"],
                default_executor="codex",
                memory_mode="auto-safe",
            )
            # The command reads and writes only the caller-owned OMJ home.
            status, exported, stderr = self._run(source, ["setup-profile", "export"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertIsNotNone(exported)
            assert exported is not None
            self.assertFalse(exported["written"])
            self.assertIsNone(exported["output"])
            pack = exported["pack"]
            self.assertEqual(pack["schema_version"], SETUP_PROFILE_PACK_SCHEMA_VERSION)

            pack_path = root / "pack.json"
            pack_path.write_text(json.dumps(pack), encoding="utf-8")
            target = root / "target"
            target_paths = resolve_paths(target / ".omj", target / ".hermes")
            write_setup_profile(
                target_paths,
                ["hermes-retained"],
                default_executor="hermes",
            )
            before = target_paths.setup_profile_path.read_bytes()

            status, preview, stderr = self._run(target, ["setup-profile", "import", "--from", str(pack_path)])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(preview["dry_run"], True)  # type: ignore[index]
            self.assertEqual(preview["applied"], False)  # type: ignore[index]
            self.assertEqual(target_paths.setup_profile_path.read_bytes(), before)

            status, applied, stderr = self._run(
                target,
                ["setup-profile", "import", "--from", str(pack_path), "--apply"],
            )
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(applied["applied"], True)  # type: ignore[index]
            after_apply = json.loads(target_paths.setup_profile_path.read_text(encoding="utf-8"))
            self.assertEqual(after_apply["default_executor"], "codex")

            tampered = json.loads(pack_path.read_text(encoding="utf-8"))
            tampered["profile"]["default_executor"] = "generic"
            tampered_path = root / "tampered.json"
            tampered_path.write_text(json.dumps(tampered), encoding="utf-8")
            protected = target_paths.setup_profile_path.read_bytes()
            with patch.object(subprocess, "run", side_effect=AssertionError("execution forbidden")), patch.object(
                subprocess, "Popen", side_effect=AssertionError("execution forbidden")
            ), patch.object(socket, "create_connection", side_effect=AssertionError("network forbidden")):
                status, rejected, stderr = self._run(
                    target,
                    ["setup-profile", "import", "--from", str(tampered_path), "--apply"],
                )
            self.assertEqual(status, 2)
            self.assertIsNone(rejected)
            self.assertIn("digest mismatch", stderr)
            self.assertEqual(target_paths.setup_profile_path.read_bytes(), protected)

    def test_graph_build_and_delegate_attach_only_explicit_persisted_graph(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            (repo / "src" / "pkg").mkdir(parents=True)
            (repo / "src" / "pkg" / "core.py").write_text("def parse():\n    return 1\n", encoding="utf-8")
            (repo / "src" / "pkg" / "cli.py").write_text("from .core import parse\n\ndef main():\n    return parse()\n", encoding="utf-8")
            status, built, stderr = self._run(root, ["codegraph", "build", "--repo", str(repo), "--write"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(built["schema_version"], "omj_codegraph/v1")  # type: ignore[index]
            artifact = repo / ".omj" / "codegraph" / "codegraph.json"
            self.assertTrue(artifact.exists())

            status, attached, stderr = self._run(
                root,
                ["coding", "delegate", "risky", "refactor", "--executor", "codex", "--graph-repo", str(repo)],
            )
            self.assertEqual((status, stderr), (0, ""))
            assert attached is not None
            handoff = attached["executor_handoff"]
            self.assertEqual(handoff["codegraph_context"]["schema_version"], "omj_codegraph_context/v1")  # type: ignore[index]

            no_graph_repo = root / "no-graph"
            no_graph_repo.mkdir()
            status, plain, stderr = self._run(
                no_graph_repo,
                ["coding", "delegate", "risky", "refactor", "--executor", "codex"],
            )
            self.assertEqual((status, stderr), (0, ""))
            assert plain is not None
            self.assertNotIn("codegraph_context", json.dumps(plain))
            self.assertFalse((no_graph_repo / ".omj" / "codegraph" / "codegraph.json").exists())

            malformed = root / "malformed"
            malformed_artifact = malformed / ".omj" / "codegraph" / "codegraph.json"
            malformed_artifact.parent.mkdir(parents=True)
            malformed_artifact.write_text(json.dumps({"schema_version": "wrong/v1"}), encoding="utf-8")
            status, refused, stderr = self._run(
                malformed,
                ["coding", "delegate", "risky", "refactor", "--executor", "codex", "--graph-repo", str(malformed)],
            )
            self.assertEqual((status, stderr), (0, ""))
            assert refused is not None
            note = refused["codegraph_context_not_attached"]
            self.assertEqual(note["status"], "not_attached")  # type: ignore[index]
            self.assertIn("malformed_persisted_graph", note["reason"])  # type: ignore[index]

    def test_typed_contract_cli_reaches_executor_prompt_and_refuses_closed_contract(self) -> None:
        declaration = {
            "inputs": [{"name": "test_path", "input_type": "file", "requirement": "required"}],
            "postconditions": [{"id": "tests", "command": "python -m unittest {test_path}"}],
            "forbidden_actions": ["Do not push to the default branch."],
            "output_shape": {"format": "json", "required_fields": ["status", "changed_files"]},
        }
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, payload, stderr = self._run(
                root,
                [
                    "coding",
                    "delegate",
                    "risky",
                    "refactor",
                    "--executor",
                    "codex",
                    "--handoff-contract",
                    json.dumps(declaration),
                ],
            )
            self.assertEqual((status, stderr), (0, ""))
            assert payload is not None
            handoff = payload["executor_handoff"]
            prompt = str(handoff["prompt_template"])  # type: ignore[index]
            self.assertIn("Do not push to the default branch.", prompt)
            self.assertIn("Postcondition `tests`", prompt)
            self.assertIn("changed_files", prompt)
            self.assertEqual(handoff["handoff_contract"]["schema_version"], "handoff_contract/v1")  # type: ignore[index]

            closed = dict(declaration)
            closed["unexpected"] = "refuse"
            status, rejected, stderr = self._run(
                root,
                [
                    "coding",
                    "delegate",
                    "risky",
                    "refactor",
                    "--executor",
                    "codex",
                    "--handoff-contract",
                    json.dumps(closed),
                ],
            )
            self.assertEqual(status, 2)
            self.assertIsNone(rejected)
            self.assertIn("unexpected", stderr)
    def _receipt_declaration(self) -> dict[str, object]:
        return {
            "inputs": [{"name": "test_path", "input_type": "file", "requirement": "required"}],
            "postconditions": [{"id": "tests", "command": "python -m unittest {test_path}"}],
            "forbidden_actions": ["Do not push to the default branch."],
            "output_shape": {"format": "json", "required_fields": ["status"]},
        }

    def _prepared_run(self, root: Path) -> str:
        status, payload, stderr = self._run(
            root,
            [
                "coding",
                "delegate",
                "implement safe runtime feature in src/omj/runtime/artifacts.py without overclaiming",
                "--executor",
                "codex",
                "--record",
                "--force-record",
                "--handoff-contract",
                json.dumps(self._receipt_declaration()),
            ],
        )
        self.assertEqual((status, stderr), (0, ""))
        assert payload is not None
        runtime = payload["runtime"]
        self.assertIn("run", runtime, json.dumps(payload, sort_keys=True))
        return str(runtime["run"]["run_id"])  # type: ignore[index]

    def _dispatch_and_complete(self, root: Path, run_id: str) -> None:
        status, _, stderr = self._run(root, ["coding", "lifecycle", "dispatch", "--run", run_id])
        self.assertEqual((status, stderr), (0, ""))
        status, _, stderr = self._run(
            root,
            ["coding", "lifecycle", "result", "--run", run_id, "--result", "completed"],
        )
        self.assertEqual((status, stderr), (0, ""))

    def test_receipt_cli_statuses_are_observed_only_from_explicit_integer_exit_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = self._prepared_run(root)
            self._dispatch_and_complete(root, run_id)

            status, missing, stderr = self._run(root, ["coding", "lifecycle", "verify", "--run", run_id])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(missing["wrapper"]["verification_observed"], False)  # type: ignore[index]
            self.assertEqual(missing["status"]["handoff_contract"]["verdict"], "not_observed")  # type: ignore[index]

            status, passed, stderr = self._run(
                root,
                ["coding", "lifecycle", "verify", "--run", run_id, "--postcondition-exit", "tests=0"],
            )
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(passed["wrapper"]["verification_observed"], True)  # type: ignore[index]
            self.assertEqual(passed["status"]["handoff_contract"]["verdict"], "passed")  # type: ignore[index]
            self.assertEqual(passed["status"]["handoff_contract"]["status"], "observed")  # type: ignore[index]

    def test_receipt_cli_failed_unknown_and_non_integer_evidence_refuse_or_fail_narrowly(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = self._prepared_run(root)
            self._dispatch_and_complete(root, run_id)

            status, failed, stderr = self._run(
                root,
                ["coding", "lifecycle", "verify", "--run", run_id, "--postcondition-exit", "tests=1"],
            )
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(failed["wrapper"]["verification_observed"], False)  # type: ignore[index]
            self.assertEqual(failed["status"]["handoff_contract"]["verdict"], "failed")  # type: ignore[index]
            receipt = root / ".omj" / "runtime" / "runs" / run_id / "handoff_contract_receipt.json"
            self.assertTrue(receipt.exists())
            persisted = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(persisted["status"], "observed")
            self.assertEqual(persisted["verdict"], "failed")

            for evidence in ("unknown=0", "tests=True", "tests=tests passed"):
                with self.subTest(evidence=evidence):
                    status, rejected, stderr = self._run(
                        root,
                        ["coding", "lifecycle", "verify", "--run", run_id, "--postcondition-exit", evidence],
                    )
                    self.assertEqual(status, 2)
                    self.assertIsNone(rejected)
                    self.assertTrue(stderr.startswith("omj:"), stderr)

    def test_no_declaration_preserves_legacy_verification_but_exit_evidence_refuses(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, started, stderr = self._run(
                root,
                ["coding", "lifecycle", "start", "--record", "implement safe runtime feature in src/omj/runtime/artifacts.py"],
            )
            self.assertEqual((status, stderr), (0, ""))
            run_id = str(started["run"]["run_id"])  # type: ignore[index]
            self._dispatch_and_complete(root, run_id)

            status, legacy, stderr = self._run(root, ["coding", "lifecycle", "verify", "--run", run_id])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(legacy["wrapper"]["verification_observed"], True)  # type: ignore[index]

            status, rejected, stderr = self._run(
                root,
                ["coding", "lifecycle", "verify", "--run", run_id, "--postcondition-exit", "tests=0"],
            )
            self.assertEqual(status, 2)
            self.assertIsNone(rejected)
            self.assertIn("declaration", stderr)

    def test_receipt_digest_change_is_unobserved_and_does_not_claim_completion(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = self._prepared_run(root)
            self._dispatch_and_complete(root, run_id)
            run_dir = root / ".omj" / "runtime" / "runs" / run_id
            contract_path = run_dir / "coding_delegation.json"
            stored = json.loads(contract_path.read_text(encoding="utf-8"))
            for handoff_key in ("executor_handoff", "runtime_handoff", "prompt_handoff"):
                handoff = stored.get(handoff_key)
                if isinstance(handoff, dict) and isinstance(handoff.get("handoff_contract"), dict):
                    handoff["handoff_contract"]["forbidden_actions"] = ["Changed after dispatch."]
                    break
            else:
                self.fail("persisted coding delegation omitted its attached handoff contract")
            contract_path.write_text(json.dumps(stored), encoding="utf-8")

            status, refused, stderr = self._run(
                root,
                ["coding", "lifecycle", "verify", "--run", run_id, "--postcondition-exit", "tests=0"],
            )
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(refused["wrapper"]["verification_observed"], False)  # type: ignore[index]
            self.assertEqual(refused["status"]["handoff_contract"]["verdict"], "not_observed")  # type: ignore[index]
            self.assertFalse((run_dir / "handoff_contract_receipt.json").exists())



    def test_commit_plan_cli_consumes_nul_status_file_and_preserves_all_paths(self) -> None:
        status_z = " M src/a.py\0R  src/new.py\0src/old.py\0?? notes with spaces.txt\0"
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            status_file = root / "status.z"
            status_file.write_bytes(status_z.encode("utf-8"))
            with patch.object(subprocess, "run", side_effect=AssertionError("git execution forbidden")), patch.object(
                subprocess, "Popen", side_effect=AssertionError("process execution forbidden")
            ), patch.object(socket, "create_connection", side_effect=AssertionError("network forbidden")):
                status, plan, stderr = self._run(
                    root,
                    ["coding", "commit-plan", "--status-file", str(status_file), "--json"],
                )
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(plan["schema_version"], "commit_plan/v1")  # type: ignore[index]
            self.assertEqual(plan["changed_file_count"], 3)  # type: ignore[index]
            planned = sorted(path for commit in plan["commits"] for path in commit["files"])  # type: ignore[index]
            self.assertEqual(planned, ["notes with spaces.txt", "src/a.py", "src/new.py"])
            rename_commit = next(commit for commit in plan["commits"] if "src/new.py" in commit["files"])  # type: ignore[index]
            self.assertEqual(rename_commit["renames"], {"src/new.py": "src/old.py"})  # type: ignore[index]

            status, from_stdin, stderr = self._run(
                root,
                ["coding", "commit-plan", "--status-file", "-", "--json"],
                stdin_text=status_z,
            )
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(from_stdin["commits"], plan["commits"])  # type: ignore[index]

    def test_commit_plan_cli_refuses_unknown_porcelain_frames_without_mutation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            status_file = root / "bad-status.z"
            status_file.write_bytes(b"XX src/bad.py\0")
            original = status_file.read_bytes()
            status, payload, stderr = self._run(
                root,
                ["coding", "commit-plan", "--status-file", str(status_file), "--json"],
            )
            self.assertEqual(status, 2)
            self.assertIsNone(payload)
            self.assertIn("unknown porcelain status", stderr)
            self.assertEqual(status_file.read_bytes(), original)

if __name__ == "__main__":
    unittest.main()
