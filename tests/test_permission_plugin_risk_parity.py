from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import unittest
from tempfile import TemporaryDirectory
from unittest import mock

from _local_package import load_local_package

load_local_package()

from omj.plugin_bundle.omj.toolcall_rules import toolcall_rule_directive
from omj.workflows.permission_rehearsal import (
    MAX_PLAN_FILE_BYTES,
    MAX_PLANNED_CALLS,
    PERMISSION_REHEARSAL_PLAN_SCHEMA_VERSION,
    PERMISSION_REHEARSAL_SCHEMA_VERSION,
    PlannedCall,
    parse_planned_calls,
    read_planned_calls,
    rehearse_planned_calls,
)
from omj.workflows.plugin_hook_contract import HostVersionObservation
from omj.workflows.plugin_risk_audit import audit_plugin_risk


class PermissionPluginRiskParityTests(unittest.TestCase):
    def _rules_file(self, home: Path, *, repeat: str = "once") -> None:
        rules_path = home / "rules" / "toolcall-rules.json"
        rules_path.parent.mkdir(parents=True, exist_ok=True)
        rules_path.write_text(
            json.dumps(
                {
                    "schema_version": "omj_toolcall_rules/v1",
                    "rules": [
                        {
                            "name": "deny-shell",
                            "pattern": "shell|dangerous",
                            "message": "shell calls require an approved alternative",
                            "tools": ["shell"],
                            "repeat": repeat,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def test_rehearsal_uses_enforcing_matcher_and_keeps_once_claims_isolated(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            omj_home = root / "omj"
            self._rules_file(omj_home)
            calls = (
                PlannedCall("shell", {"command": "dangerous"}),
                PlannedCall("network", {"url": "https://example.test"}),
            )

            enforcing = toolcall_rule_directive(
                tool_name="shell",
                tool_input=calls[0].args,
                session_id="enforcing-session",
                omj_home=str(omj_home),
            )
            rehearsal = rehearse_planned_calls(calls, omj_home=omj_home, hermes_home=root / "hermes")
            real_after_rehearsal = toolcall_rule_directive(
                tool_name="shell",
                tool_input=calls[0].args,
                session_id="real-session",
                omj_home=str(omj_home),
            )

            self.assertEqual(enforcing["action"], "block")
            self.assertEqual(rehearsal["schema_version"], PERMISSION_REHEARSAL_SCHEMA_VERSION)
            self.assertEqual(
                [
                    (row["tool"], row["verdict"], row["rule"], row["reason"])
                    for row in rehearsal["calls"]
                ],
                [
                    ("shell", "refused", "deny-shell", "refused_by_rule"),
                    ("network", "unknown", "", "needs_approval_not_readable"),
                ],
            )
            self.assertEqual(real_after_rehearsal["action"], "block")
            self.assertEqual(
                rehearsal["summary"],
                {"planned": 2, "refused": 1, "unknown": 1, "approval_bypass_active": False},
            )
            self.assertNotIn("allowed", rehearsal["summary"])
            self.assertIn("executes nothing", rehearsal["claim_boundary"])


    def test_rehearsal_reports_observed_approval_bypass_without_reclassifying_calls(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            omj_home = root / "omj"
            hermes_home = root / "hermes"
            hermes_home.mkdir()
            (hermes_home / "config.yaml").write_text("approvals:\n  mode: off\n", encoding="utf-8")

            payload = rehearse_planned_calls(
                (PlannedCall("network", {"url": "https://example.test"}),),
                omj_home=omj_home,
                hermes_home=hermes_home,
            )

            self.assertTrue(payload["approval_bypass"]["enabled"])
            self.assertEqual(payload["approval_bypass"]["status"], "observed")
            self.assertTrue(payload["summary"]["approval_bypass_active"])
            self.assertEqual(payload["calls"][0]["verdict"], "unknown")

    def test_plan_parser_fails_closed_at_schema_and_count_bounds(self) -> None:
        valid = {
            "schema_version": PERMISSION_REHEARSAL_PLAN_SCHEMA_VERSION,
            "calls": [{"tool": "shell", "args": {}}],
        }
        cases = (
            ("wrong schema", {**valid, "schema_version": "other/v1"}, "schema_version"),
            ("empty calls", {**valid, "calls": []}, "nonempty list"),
            (
                "too many calls",
                {**valid, "calls": [{"tool": "shell"}] * (MAX_PLANNED_CALLS + 1)},
                "at most",
            ),
            ("non-object entry", {**valid, "calls": ["shell"]}, r"calls\[0\]"),
            ("blank tool", {**valid, "calls": [{"tool": "  "}]}, "nonempty string"),
        )
        for name, raw, message in cases:
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, message):
                    parse_planned_calls(raw)

    def test_plan_reader_refuses_missing_malformed_and_truncated_documents(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing.json"
            malformed = root / "malformed.json"
            malformed.write_text('{"schema_version":', encoding="utf-8")
            oversized = root / "oversized.json"
            oversized.write_bytes(b"{" + b" " * MAX_PLAN_FILE_BYTES + b"}")

            for name, path in (("missing", missing), ("malformed", malformed), ("oversized", oversized)):
                with self.subTest(name=name):
                    with self.assertRaises(ValueError):
                        read_planned_calls(path)

    def test_rehearsal_has_no_dispatch_shell_or_network_side_effects(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            omj_home = root / "omj"
            hermes_home = root / "hermes"
            before = sorted(path.relative_to(root) for path in root.rglob("*"))
            calls = (
                PlannedCall("shell", {"command": "echo should-not-run"}),
                PlannedCall("network", {"url": "https://example.test"}),
            )
            with (
                mock.patch.object(subprocess, "run") as run,
                mock.patch.object(subprocess, "Popen") as popen,
                mock.patch.object(subprocess, "call") as call,
                mock.patch.object(subprocess, "check_call") as check_call,
                mock.patch.object(subprocess, "check_output") as check_output,
                mock.patch.object(os, "system") as system,
                mock.patch.object(socket, "create_connection") as connection,
                mock.patch.object(socket, "socket") as raw_socket,
            ):
                result = rehearse_planned_calls(calls, omj_home=omj_home, hermes_home=hermes_home)

            self.assertEqual(result["summary"]["planned"], 2)
            for boundary in (run, popen, call, check_call, check_output, system, connection, raw_socket):
                boundary.assert_not_called()
            self.assertEqual(sorted(path.relative_to(root) for path in root.rglob("*")), before)

    def _write_plugin(self, root: Path, manifest: str = "name: sample\n") -> None:
        root.mkdir(parents=True, exist_ok=True)
        (root / "plugin.yaml").write_text(manifest, encoding="utf-8")

    def test_static_audit_reports_declared_hook_semantics_without_runtime_claims(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "plugin"
            self._write_plugin(
                root,
                "name: sample\nprovides_hooks:\n  - pre_tool_call\n  - pre_llm_call\n  - on_stream_delta\n",
            )
            marker = Path(tmp) / "imported.marker"
            (root / "plugin.py").write_text(
                f"import subprocess, requests\nsubprocess.run(['echo', 'not-run'])\nrequests.get('https://example.test')\neval('2 + 2')\napi_key = 'sk_live_12345678901234567890'\nfrom pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n",
                encoding="utf-8",
            )

            report = audit_plugin_risk(
                root,
                host_version=HostVersionObservation("0.21.1", "operator_declared", "compatible"),
            )
            hooks = {item["hook"]: item for item in report["declared_hooks"]["hooks"]}

            self.assertEqual(report["schema_version"], "plugin_risk_audit/v1")
            self.assertEqual(report["declared_hooks"]["classification_status"], "classified")
            self.assertEqual(
                {
                    name: (row["effect"], row["host_contract"], row["timeout_semantics"])
                    for name, row in hooks.items()
                },
                {
                    "pre_tool_call": ("policy_gate", "bounded", "fail_closed"),
                    "pre_llm_call": ("prompt_context_contributor", "bounded", "fail_open"),
                    "on_stream_delta": ("observer", "queued_worker", "not_applicable"),
                },
            )
            self.assertEqual(
                report["declared_hooks"]["host_contract"]["inspected_host"]["compatibility"],
                "compatible",
            )
            self.assertFalse(marker.exists())
            self.assertEqual(report["not_observed"]["plugin_execution"]["status"], "not_observed")
            self.assertEqual(report["summary"]["scanned_file_count"], 2)
            for category in (
                "hermes_hook_capability",
                "process_execution",
                "dynamic_code_execution",
                "network_request",
                "potential_committed_secret",
            ):
                with self.subTest(category=category):
                    self.assertIn(category, report["summary"]["risk_categories"])
            self.assertIn("hermes-agent", report["declared_hooks"]["host_contract"]["contract_source"])
            self.assertIn("not evidence", report["claim_boundary"])

    def test_unsupported_host_and_unreadable_declarations_remain_unknown_findings(self) -> None:
        with TemporaryDirectory() as tmp:
            unsupported = Path(tmp) / "unsupported"
            self._write_plugin(unsupported, "name: sample\nprovides_hooks:\n  - pre_tool_call\n")
            held = audit_plugin_risk(
                unsupported,
                host_version=HostVersionObservation("0.22.0", "operator_declared", "incompatible"),
            )
            self.assertEqual(held["declared_hooks"]["classification_status"], "unknown")
            self.assertIn("undetermined_hook_contract", held["summary"]["risk_categories"])
            self.assertEqual(held["declared_hooks"]["hooks"][0]["effect"], "policy_gate")

            unreadable = Path(tmp) / "unreadable"
            self._write_plugin(unreadable, "name: sample\nprovides_hooks: [pre_tool_call]\n")
            report = audit_plugin_risk(unreadable)
            self.assertEqual(report["source"]["manifest_yaml_status"], "unreadable")
            self.assertEqual(report["declared_hooks"]["classification_status"], "unknown")
            self.assertIn("undetermined_hook_contract", report["summary"]["risk_categories"])

    def test_self_update_requires_retrieval_plus_installed_code_replacement_and_checksum_is_mitigation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "plugin"
            self._write_plugin(root)
            (root / "retrieve.py").write_text(
                'import requests\nrequests.get("https://example.test/plugin.py")\n',
                encoding="utf-8",
            )
            (root / "replace.py").write_text(
                'import hashlib, shutil\nhashlib.sha256(b"payload")\nshutil.copy2("download.py", "plugin.py")\n',
                encoding="utf-8",
            )

            report = audit_plugin_risk(root)
            self.assertEqual(report["self_update"]["classification"], "detected")
            self.assertEqual(report["self_update"]["composition"], "remote_retrieval_and_code_replacement")
            self.assertIn("remote_retrieval", report["self_update"]["signals"])
            self.assertIn("code_replacement_write", report["self_update"]["signals"])
            self.assertEqual(report["self_update"]["mitigating_signals"], ["integrity_verification"])
            self.assertIn("self_update_or_code_replacement", report["summary"]["risk_categories"])
            self.assertTrue(any("not evidence" in text for text in report["self_update"]["diagnostics"]))

    def test_network_and_unrelated_write_do_not_compose_as_self_update(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "plugin"
            self._write_plugin(root)
            (root / "retrieve.py").write_text(
                'import requests\nrequests.get("https://example.test/data")\n',
                encoding="utf-8",
            )
            (root / "write.py").write_text(
                'with open("notes.txt", "w") as handle:\n    handle.write("log")\n',
                encoding="utf-8",
            )

            report = audit_plugin_risk(root)
            self.assertEqual(report["self_update"]["classification"], "not_detected")
            self.assertIsNone(report["self_update"]["composition"])
            self.assertNotIn("self_update_or_code_replacement", report["summary"]["risk_categories"])
            self.assertIn("network_request", report["summary"]["risk_categories"])

    def test_static_audit_securely_bounds_reads_rejects_symlinks_and_redacts_secret_content(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "plugin"
            self._write_plugin(root)
            (root / "oversized.py").write_bytes(b"x" * 131_073)
            with self.assertRaises(ValueError):
                audit_plugin_risk(root)

            safe = Path(tmp) / "safe-plugin"
            self._write_plugin(safe)
            secret = "sk_live_12345678901234567890"
            (safe / "credentials.py").write_text(f'api_key = "{secret}"\n', encoding="utf-8")
            outside = Path(tmp) / "outside.py"
            outside.write_text("print('outside')\n", encoding="utf-8")
            os.symlink(outside, safe / "linked.py")
            with self.assertRaises(ValueError):
                audit_plugin_risk(safe)

            clean = Path(tmp) / "clean-plugin"
            self._write_plugin(clean)
            (clean / "credentials.py").write_text(f'api_key = "{secret}"\n', encoding="utf-8")
            report = audit_plugin_risk(clean)
            serialized = json.dumps(report, sort_keys=True)
            self.assertIn("potential_committed_secret", report["summary"]["risk_categories"])
            self.assertNotIn(secret, serialized)

            root_link = Path(tmp) / "plugin-link"
            os.symlink(clean, root_link)
            with self.assertRaises(ValueError):
                audit_plugin_risk(root_link)

    def test_permission_rehearsal_cli_returns_refusal_status_and_payload(self) -> None:
        from _cli_harness import run_cli

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            omj_home = root / ".omj"
            hermes_home = root / ".hermes"
            self._rules_file(omj_home)
            plan = root / "plan.json"
            plan.write_text(
                json.dumps(
                    {
                        "schema_version": PERMISSION_REHEARSAL_PLAN_SCHEMA_VERSION,
                        "calls": [{"tool": "shell", "args": {"command": "dangerous"}}],
                    }
                ),
                encoding="utf-8",
            )

            status, stdout, stderr = run_cli(
                [
                    "--omj-home",
                    str(omj_home),
                    "--hermes-home",
                    str(hermes_home),
                    "ops",
                    "permission-rehearse",
                    "--plan",
                    str(plan),
                ]
            )

            self.assertEqual(status, 1, stderr)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(payload["schema_version"], PERMISSION_REHEARSAL_SCHEMA_VERSION)
            self.assertEqual(payload["calls"][0]["verdict"], "refused")
            self.assertEqual(payload["summary"]["refused"], 1)
            self.assertNotIn("allowed", payload["summary"])

    def test_plugin_risk_audit_cli_preserves_static_boundary_and_host_option_exclusion(self) -> None:
        from _cli_harness import run_cli

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = root / "plugin"
            self._write_plugin(plugin, "name: sample\nprovides_hooks:\n  - pre_tool_call\n")

            status, stdout, stderr = run_cli(
                [
                    "ops",
                    "plugin-risk-audit",
                    "--path",
                    str(plugin),
                    "--hermes-version",
                    "0.21.1",
                ]
            )
            self.assertEqual(status, 0, stderr)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(payload["schema_version"], "plugin_risk_audit/v1")
            self.assertEqual(payload["declared_hooks"]["classification_status"], "classified")
            self.assertEqual(payload["not_observed"]["plugin_execution"]["status"], "not_observed")

            status, _, stderr = run_cli(
                [
                    "ops",
                    "plugin-risk-audit",
                    "--path",
                    str(plugin),
                    "--hermes-version",
                    "0.21.1",
                    "--hermes-install",
                    str(root),
                ]
            )
            self.assertEqual(status, 2)
            self.assertIn("not allowed with argument", stderr)
