from __future__ import annotations

import json
import sys
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from omj.paths import OmjPaths
from omj.release import (
    hermes_release_smoke_plan,
    product_readiness_report,
    release_evidence_bundle,
    release_readiness_checklist,
    run_hermes_release_smoke,
    skill_content_smoke,
)
from omj.release_install_smoke import install_script_smoke_plan, run_install_script_smoke
from omj.release_smoke_core import CommandResult, subprocess_runner, subprocess_runner_exact_env


class ReleaseSmokeTests(unittest.TestCase):
    def test_release_readiness_checklist_is_plan_only_and_names_required_gates(self) -> None:
        payload = release_readiness_checklist(version="v1.0.0", omj_command="/tmp/omj")

        self.assertEqual(payload["schema_version"], "release_readiness_checklist/v1")
        self.assertEqual(payload["mode"], "plan")
        self.assertFalse(payload["observed"])
        self.assertEqual(payload["version"], "1.0.0")
        self.assertEqual(payload["tag"], "v1.0.0")
        self.assertIn("does not run commands", payload["proof_boundary"])
        items = {item["id"]: item for item in payload["items"]}
        self.assertIn("unit_tests", items)
        self.assertIn("skill_content_smoke", items)
        self.assertIn("installed_command_smoke", items)
        self.assertIn("installed_command_path", items)
        self.assertIn("use_case_demo_cards", items)
        self.assertIn("use_case_artifact_bundle", items)
        self.assertIn("use_case_replay", items)
        self.assertIn("use_case_readiness", items)
        self.assertIn("product_readiness", items)
        self.assertIn("release_evidence_bundle", items)
        self.assertIn("live_tap_smoke", items)
        self.assertIn("tag_and_publish", items)
        self.assertEqual(items["installed_command_path"]["command"], "command -v /tmp/omj")
        self.assertEqual(items["installed_command_help"]["command"], "/tmp/omj --help")
        self.assertEqual(items["skill_content_smoke"]["command"], "/tmp/omj release skill-content-smoke --json")
        self.assertIn("generated workflow context rails", items["skill_content_smoke"]["evidence_required"])
        self.assertIn("bundled role context", items["skill_content_smoke"]["evidence_required"])
        self.assertIn("all-skill awareness lane coverage", items["skill_content_smoke"]["evidence_required"])
        self.assertIn("full capability manifest context", items["skill_content_smoke"]["evidence_required"])
        self.assertIn("playbook capability context", items["skill_content_smoke"]["evidence_required"])
        self.assertIn("standalone plugin capability fallback coverage", items["skill_content_smoke"]["evidence_required"])
        self.assertIn("G1-G10 use-case demo cards", items["skill_content_smoke"]["evidence_required"])
        self.assertIn("G1-G10 use-case artifact bundles", items["skill_content_smoke"]["evidence_required"])
        self.assertIn("G1-G10 natural-language use-case replay", items["skill_content_smoke"]["evidence_required"])
        self.assertIn("bounded prompt context budgets", items["skill_content_smoke"]["evidence_required"])
        self.assertIn("bounded capability payload budgets", items["skill_content_smoke"]["evidence_required"])
        self.assertIn("--include-command-smoke", items["installed_command_smoke"]["command"])
        self.assertIn("dist/oh_my_jeo-1.0.0-py3-none-any.whl", items["wheel_install"]["command"])
        self.assertIn("wheel_setup_dry_run", items)
        self.assertIn("setup --dry-run --channel stable --version 1.0.0", items["wheel_setup_dry_run"]["command"])
        self.assertIn("release install-smoke --live", items["installer_smoke"]["command"])
        self.assertEqual(items["use_case_demo_cards"]["command"], "uv run python -m omj.cli cases demo --all --json")
        self.assertIn("G1-G10", items["use_case_demo_cards"]["evidence_required"])
        self.assertIn("wrapper-renderable projections", items["use_case_demo_cards"]["proof_boundary"])
        self.assertIn("not prove", items["use_case_demo_cards"]["proof_boundary"])
        self.assertEqual(items["use_case_artifact_bundle"]["command"], "uv run python -m omj.cli cases artifact --all --json")
        self.assertIn("prepared artifacts", items["use_case_artifact_bundle"]["evidence_required"])
        self.assertIn("prepared runbook projection", items["use_case_artifact_bundle"]["proof_boundary"])
        self.assertIn("not prove", items["use_case_artifact_bundle"]["proof_boundary"])
        self.assertEqual(items["use_case_replay"]["command"], "uv run python -m omj.cli cases replay --json")
        self.assertIn("English and Korean operator fixtures", items["use_case_replay"]["evidence_required"])
        self.assertIn("synthetic fixtures", items["use_case_replay"]["proof_boundary"])
        self.assertIn("does not prove live Hermes chat behavior", items["use_case_replay"]["proof_boundary"])
        self.assertEqual(items["use_case_readiness"]["command"], "uv run python -m omj.cli cases readiness --json")
        self.assertIn("readiness", items["use_case_readiness"]["evidence_required"])
        self.assertIn("deterministic local use-case contracts", items["use_case_readiness"]["proof_boundary"])
        self.assertEqual(items["product_readiness"]["command"], "/tmp/omj release product-readiness --version 1.0.0 --json")
        self.assertIn("skill-content", items["product_readiness"]["evidence_required"])
        self.assertIn("product contracts", items["product_readiness"]["proof_boundary"])
        self.assertEqual(items["release_evidence_bundle"]["command"], "/tmp/omj release evidence-bundle --version 1.0.0 --write --json")
        self.assertIn("omj_release_evidence_bundle/v1", items["release_evidence_bundle"]["evidence_required"])
        self.assertIn("local deterministic evidence", items["release_evidence_bundle"]["proof_boundary"])
        self.assertTrue(items["live_tap_smoke"]["mutates_profile"])
        self.assertTrue(items["live_tap_smoke"]["requires_release_authority"])
        self.assertFalse(items["tag_and_publish"]["required"])
        self.assertIn('git tag -a v1.0.0 -m "Release v1.0.0"', items["tag_and_publish"]["command"])
        self.assertTrue(items["tag_and_publish"]["requires_release_authority"])
        self.assertGreaterEqual(payload["required_item_count"], 18)

    def test_release_readiness_checklist_rejects_unsafe_versions_and_quotes_command_paths(self) -> None:
        with self.assertRaises(ValueError):
            release_readiness_checklist(version="1.0.0; echo injected")

        payload = release_readiness_checklist(version="1.0.0", omj_command="/tmp/omj command")

        items = {item["id"]: item for item in payload["items"]}
        self.assertEqual(items["installed_command_help"]["command"], "'/tmp/omj command' --help")
        self.assertEqual(items["installed_command_path"]["command"], "command -v '/tmp/omj command'")
        self.assertEqual(items["skill_content_smoke"]["command"], "'/tmp/omj command' release skill-content-smoke --json")
        self.assertEqual(
            items["product_readiness"]["command"],
            "'/tmp/omj command' release product-readiness --version 1.0.0 --json",
        )
        self.assertEqual(
            items["release_evidence_bundle"]["command"],
            "'/tmp/omj command' release evidence-bundle --version 1.0.0 --write --json",
        )
        self.assertIn("--omj-command '/tmp/omj command'", items["installed_command_smoke"]["command"])
        self.assertIn("'/tmp/omj command' release hermes-smoke --live", items["live_tap_smoke"]["command"])

    def test_skill_content_smoke_checks_router_and_workflow_context(self) -> None:
        payload = skill_content_smoke()

        self.assertEqual(payload["schema_version"], "skill_content_smoke/v1")
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["observed"])
        self.assertEqual(payload["router_skill"], "oh-my-jeo")
        self.assertIn("img-summary", payload["representative_skills"])
        self.assertEqual(payload["missing_representative_skills"], [])
        self.assertEqual(payload["missing_awareness_lane_skills"], [])
        self.assertEqual(payload["unexpected_awareness_surfaces"], [])
        self.assertIn("request-to-handoff", payload["allowed_conceptual_awareness_surfaces"])
        self.assertGreaterEqual(payload["awareness_lane_skill_count"], payload["workflow_skill_count"])
        self.assertGreaterEqual(payload["full_capability_skill_count"], payload["workflow_skill_count"])
        self.assertEqual(payload["missing_full_capability_skills"], [])
        self.assertEqual(payload["missing_full_capability_context_skills"], [])
        self.assertGreaterEqual(payload["playbook_capability_count"], 20)
        self.assertGreaterEqual(payload["standalone_playbook_capability_count"], 8)
        self.assertIn("request-to-handoff", payload["required_playbook_capability_ids"])
        self.assertEqual(payload["missing_required_playbook_capabilities"], [])
        self.assertEqual(payload["missing_required_standalone_playbook_capabilities"], [])
        self.assertEqual(payload["missing_playbook_context_playbooks"], [])
        self.assertEqual(payload["missing_standalone_playbook_context_playbooks"], [])
        self.assertEqual(payload["missing_standalone_capability_skills"], [])
        self.assertEqual(payload["unexpected_standalone_capability_skills"], [])
        self.assertEqual(payload["missing_standalone_capability_context_skills"], [])
        self.assertGreaterEqual(payload["role_context_count"], 8)
        self.assertEqual(payload["missing_role_context_roles"], [])
        self.assertEqual(payload["bundled_role_context_count"], payload["role_context_count"])
        self.assertEqual(payload["missing_bundled_role_context_roles"], [])
        self.assertEqual(payload["missing_bundled_role_files"], [])
        self.assertEqual(payload["unexpected_bundled_role_files"], [])
        self.assertEqual(payload["stale_bundled_role_context_roles"], [])
        self.assertIn("OMJ Role Context", payload["required_role_context_markers"])
        self.assertIn("workflow_routing_hint", payload["required_capability_context_fields"])
        self.assertIn("evidence_boundary", payload["required_capability_context_fields"])
        self.assertIn("pipeline", payload["required_playbook_context_fields"])
        self.assertIn("prepared_is_not", payload["required_playbook_context_fields"])
        self.assertIn("primary_owner_role", payload["required_playbook_context_fields"])
        self.assertIn("available_wrapper_actions", payload["required_playbook_context_fields"])
        self.assertIn("first_stage", payload["required_playbook_context_fields"])
        self.assertIn("workflow_routing_hint", payload["required_standalone_capability_context_fields"])
        self.assertIn("evidence_boundary", payload["required_standalone_capability_context_fields"])
        self.assertGreaterEqual(payload["catalog_skill_count"], payload["skill_count"])
        self.assertGreaterEqual(payload["standalone_capability_skill_count"], payload["workflow_skill_count"])
        self.assertLessEqual(
            payload["full_capability_skill_section_chars"],
            payload["capability_context_char_limits"]["full_skill_section"],
        )
        self.assertLessEqual(
            payload["standalone_capability_skill_section_chars"],
            payload["capability_context_char_limits"]["standalone_skill_section"],
        )
        self.assertLessEqual(
            payload["max_full_capability_skill_chars"],
            payload["capability_context_char_limits"]["full_skill_item"],
        )
        self.assertLessEqual(
            payload["max_standalone_capability_skill_chars"],
            payload["capability_context_char_limits"]["standalone_skill_item"],
        )
        self.assertEqual(payload["capability_budget_failures"], [])
        self.assertEqual(payload["use_case_demo_collection_schema"], "omj_use_case_demo_collection/v1")
        self.assertEqual(payload["use_case_demo_card_count"], 10)
        self.assertEqual(payload["expected_use_case_demo_card_count"], 10)
        self.assertEqual(payload["use_case_demo_failures"], [])
        self.assertEqual(payload["use_case_artifact_collection_schema"], "omj_use_case_artifact_collection/v1")
        self.assertEqual(payload["use_case_artifact_count"], 10)
        self.assertEqual(payload["expected_use_case_artifact_count"], 10)
        self.assertEqual(payload["use_case_artifact_failures"], [])
        self.assertEqual(payload["use_case_replay_schema"], "omj_use_case_replay/v1")
        self.assertEqual(payload["use_case_replay_status"], "passed")
        self.assertEqual(payload["use_case_replay_total"], 20)
        self.assertEqual(payload["use_case_replay_passed"], 20)
        self.assertEqual(payload["expected_use_case_replay_total"], 20)
        self.assertEqual(payload["use_case_replay_failures"], [])
        self.assertEqual(payload["use_case_readiness_schema"], "omj_use_case_readiness/v1")
        self.assertEqual(payload["use_case_readiness_status"], "ready")
        self.assertEqual(payload["use_case_readiness_score"], 100)
        self.assertEqual(payload["use_case_readiness_blocking_failures"], 0)
        self.assertGreaterEqual(payload["use_case_readiness_warning_count"], 0)
        self.assertEqual(payload["use_case_readiness_failures"], [])
        self.assertLessEqual(
            payload["awareness_primer_context_chars"],
            payload["awareness_context_char_limits"]["primer_context"],
        )
        self.assertLessEqual(
            payload["awareness_primer_markdown_chars"],
            payload["awareness_context_char_limits"]["primer_markdown"],
        )
        self.assertLessEqual(
            payload["max_workflow_context_chars"],
            payload["awareness_context_char_limits"]["workflow_context"],
        )
        self.assertEqual(payload["oversized_awareness_contexts"], [])
        self.assertEqual(payload["awareness_budget_failures"], [])
        self.assertLessEqual(
            payload["max_role_context_chars"],
            payload["awareness_context_char_limits"]["role_context"],
        )
        self.assertEqual(payload["oversized_role_contexts"], [])
        self.assertEqual(payload["role_context_budget_failures"], [])
        self.assertEqual(payload["failed_checks"], [])
        self.assertGreaterEqual(payload["skill_count"], 40)
        self.assertGreaterEqual(payload["checked_marker_count"], 100)
        self.assertIn("does not prove the target Hermes profile", payload["proof_boundary"])

    def test_product_readiness_report_rolls_up_public_release_story(self) -> None:
        payload = product_readiness_report(version="v1.0.1", omj_command="/tmp/omj command")

        self.assertEqual(payload["schema_version"], "omj_product_readiness/v1")
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["score"], 100)
        self.assertTrue(payload["observed"])
        self.assertEqual(payload["version"], "1.0.1")
        self.assertEqual(payload["blocking_failures"], 0)
        gates = {gate["id"]: gate for gate in payload["gates"]}
        self.assertEqual(
            set(gates),
            {"skill_content", "use_cases", "parity_contracts", "release_checklist"},
        )
        self.assertEqual(gates["skill_content"]["status"], "passed")
        self.assertEqual(gates["use_cases"]["status"], "passed")
        self.assertEqual(gates["parity_contracts"]["status"], "passed")
        self.assertEqual(gates["release_checklist"]["status"], "passed")
        self.assertIn(
            "'/tmp/omj command' release checklist --version 1.0.1 --json",
            gates["release_checklist"]["command"],
        )
        self.assertIn("deterministic local OMJ package", payload["boundary"])
        self.assertIn("Attach observed evidence", " ".join(payload["next_actions"]))
        self.assertIn("evidence-bundle", " ".join(payload["next_actions"]))

    def test_release_evidence_bundle_packages_and_writes_local_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = OmjPaths(omj_home=Path(tmp) / ".omj", hermes_home=Path(tmp) / ".hermes")

            payload = release_evidence_bundle(version="v1.0.1", omj_command="/tmp/omj command", paths=paths)

            self.assertEqual(payload["schema_version"], "omj_release_evidence_bundle/v1")
            self.assertEqual(payload["status"], "ready")
            self.assertFalse(payload["written"])
            self.assertFalse(paths.release_evidence_index_path.exists())
            self.assertIn("local_artifact_store: not_written", payload["warnings"])
            self.assertEqual(payload["summary"]["product_readiness_status"], "ready")
            self.assertEqual(payload["evidence"]["product_readiness"]["schema_version"], "omj_product_readiness/v1")
            self.assertEqual(payload["evidence"]["release_checklist"]["schema_version"], "release_readiness_checklist/v1")
            self.assertIn("executor_dispatch", payload["not_evidence_for"])

            written = release_evidence_bundle(version="v1.0.1", omj_command="/tmp/omj command", paths=paths, write=True)

            self.assertTrue(written["written"])
            artifact_path = Path(str(written["artifact_path"]))
            self.assertTrue(artifact_path.exists())
            self.assertTrue(paths.release_evidence_index_path.exists())
            stored = json.loads(artifact_path.read_text(encoding="utf-8"))
            index = json.loads(paths.release_evidence_index_path.read_text(encoding="utf-8"))
            self.assertEqual(stored["schema_version"], "omj_release_evidence_bundle/v1")
            self.assertEqual(index["schema_version"], "omj_release_evidence_index/v1")
            self.assertEqual(index["latest_version"], "1.0.1")
            self.assertEqual(index["latest_artifact_path"], str(artifact_path))

    def test_release_readiness_checklist_rejects_empty_version(self) -> None:
        with self.assertRaises(ValueError):
            release_readiness_checklist(version=" ")

    def test_hermes_smoke_plan_is_non_mutating_until_live(self) -> None:
        omj_home = str(Path("/tmp/omj-smoke").resolve())
        hermes_home = str(Path("/tmp/hermes-smoke").resolve())
        payload = hermes_release_smoke_plan(omj_home="/tmp/omj-smoke", hermes_home="/tmp/hermes-smoke")

        self.assertEqual(payload["schema_version"], "hermes_release_smoke/v1")
        self.assertEqual(payload["mode"], "plan")
        self.assertFalse(payload["observed"])
        self.assertIn("--live", payload["live_command"])
        commands = [step["command"] for step in payload["steps"]]
        self.assertEqual(commands[0], ["hermes", "skills", "tap", "add", "rlaope/oh-my-hermes"])
        self.assertEqual(
            commands[1],
            ["hermes", "skills", "install", "rlaope/oh-my-hermes/skills/oh-my-hermes", "--yes"],
        )
        self.assertIn(["hermes", "skills", "list", "--enabled-only"], commands)
        self.assertIn(["hermes", "skills", "check", "oh-my-hermes"], commands)
        self.assertIn(["hermes", "skills", "inspect", "rlaope/oh-my-hermes/skills/oh-my-hermes"], commands)
        self.assertIn("does not touch", payload["proof_boundary"])
        self.assertEqual(payload["target_binding"]["hermes_home"], hermes_home)
        self.assertIn("--hermes-home", payload["live_command"])
        self.assertEqual(payload["installed_command_smoke"]["schema_version"], "installed_omj_command_smoke/v1")
        self.assertEqual(payload["installed_command_smoke"]["path_check"]["schema_version"], "installed_omj_path_check/v1")
        self.assertFalse(payload["installed_command_smoke"]["path_check"]["observed"])
        installed_commands = [step["command"] for step in payload["installed_command_smoke"]["steps"]]
        self.assertEqual(installed_commands[0], ["omj", "--help"])
        self.assertIn(["omj", "release", "skill-content-smoke", "--json"], installed_commands)
        self.assertIn(
            ["omj", "--omj-home", omj_home, "--hermes-home", hermes_home, "release", "hermes-smoke", "--install-path", "setup", "--omj-command", "omj"],
            installed_commands,
        )
        self.assertEqual(payload["first_use_status_smoke"]["schema_version"], "first_use_status_smoke/v1")
        self.assertFalse(payload["first_use_status_smoke"]["observed"])
        first_use_commands = [step["command"] for step in payload["first_use_status_smoke"]["steps"]]
        self.assertIn("chat", first_use_commands[0])
        self.assertIn("session", first_use_commands[0])
        self.assertIn("accept-plan", first_use_commands[1])
        self.assertIn("select-executor", first_use_commands[2])
        self.assertIn("prepare-handoff", first_use_commands[3])
        self.assertIn("status", first_use_commands[4])
        self.assertEqual(
            payload["first_use_status_smoke"]["expected_status_boundary"]["before_handoff"]["executor_actions_visible"],
            False,
        )

    def test_setup_install_path_uses_omj_setup_before_hermes_checks(self) -> None:
        omj_home = str(Path("/tmp/omj-smoke").resolve())
        hermes_home = str(Path("/tmp/hermes-smoke").resolve())
        payload = hermes_release_smoke_plan(
            install_path="setup",
            omj_command="omj-dev",
            omj_home="/tmp/omj-smoke",
            hermes_home="/tmp/hermes-smoke",
        )

        commands = [step["command"] for step in payload["steps"]]
        self.assertEqual(commands[0], ["omj-dev", "--omj-home", omj_home, "--hermes-home", hermes_home, "setup"])
        self.assertIn(["hermes", "skills", "check", "oh-my-jeo"], commands)
        self.assertIn(["omj-dev", "--omj-home", omj_home, "--hermes-home", hermes_home, "doctor"], commands)
        self.assertNotIn(["hermes", "skills", "inspect", "oh-my-hermes"], commands)
        installed_commands = [step["command"] for step in payload["installed_command_smoke"]["steps"]]
        self.assertEqual(installed_commands[0], ["omj-dev", "--help"])
        self.assertIn(["omj-dev", "release", "skill-content-smoke", "--json"], installed_commands)
        self.assertIn(
            [
                "omj-dev",
                "--omj-home",
                omj_home,
                "--hermes-home",
                hermes_home,
                "release",
                "hermes-smoke",
                "--install-path",
                "setup",
                "--omj-command",
                "omj-dev",
            ],
            installed_commands,
        )

    def test_install_script_smoke_plan_is_isolated_and_non_observed(self) -> None:
        payload = install_script_smoke_plan(repo_root="/tmp/omj-repo", install_script="/tmp/omj-repo/install.sh")

        self.assertEqual(payload["schema_version"], "install_script_smoke/v1")
        self.assertEqual(payload["mode"], "plan")
        self.assertFalse(payload["observed"])
        self.assertEqual(payload["repo_root"], str(Path("/tmp/omj-repo").resolve()))
        self.assertEqual(payload["package_url"], str(Path("/tmp/omj-repo").resolve()))
        self.assertIn("OMJ_VENV_DIR", payload["environment"])
        self.assertIn("OMJ_BIN_DIR", payload["environment"])
        self.assertEqual(payload["environment"]["OMJ_HOME"], "<tempdir>/home/.omj")
        self.assertEqual(payload["environment"]["HERMES_HOME"], "<tempdir>/home/.hermes")
        first_use = payload["first_use_status_smoke"]
        self.assertEqual(first_use["target_binding"]["omj_home"], "<tempdir>/home/.omj")
        self.assertEqual(first_use["target_binding"]["hermes_home"], "<tempdir>/home/.hermes")
        self.assertEqual(payload["environment"]["OMJ_RUN_SETUP"], "0")
        self.assertEqual(payload["environment"]["OMJ_RUN_DOCTOR"], "1")
        self.assertEqual(payload["environment"]["OMJ_SETUP_ARGS"], "")
        self.assertIn("<tempdir>", payload["work_dir"])
        self.assertEqual(payload["steps"][0]["command"], ["sh", str(Path("/tmp/omj-repo/install.sh").resolve())])
        self.assertEqual(payload["steps"][1]["name"], "installed_command_smoke")
        self.assertIn("release", payload["steps"][1]["command"])
        self.assertIn("first_use_status_smoke", payload)
        self.assertIn("does not download over curl", payload["proof_boundary"])

    def test_install_script_smoke_live_installs_command_without_setup_and_runs_command_smoke(self) -> None:
        seen: list[list[str]] = []
        seen_env: list[dict[str, str]] = []

        def runner(command, _timeout, env):
            seen.append(list(command))
            seen_env.append(dict(env or {}))
            if list(command)[0] == "sh":
                bin_dir = Path(env["OMJ_BIN_DIR"])
                bin_dir.mkdir(parents=True, exist_ok=True)
                installed = bin_dir / "omj"
                installed.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                installed.chmod(0o755)
                return CommandResult(command, 0, "installer ok", "")
            return CommandResult(command, 0, "ok", "")

        with self.subTest("live"):
            from tempfile import TemporaryDirectory

            with TemporaryDirectory() as tmp:
                root = Path(tmp)
                install_script = root / "install.sh"
                install_script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                with patch.dict(
                    "os.environ",
                    {"OMJ_HOME": "/real/operator/omj", "HERMES_HOME": "/real/operator/hermes"},
                ):
                    payload = run_install_script_smoke(
                        repo_root=root,
                        install_script=install_script,
                        work_dir=root / "work",
                        runner=runner,
                        timeout_seconds=5,
                    )

        self.assertTrue(payload["ok"])
        self.assertTrue(payload["observed"])
        self.assertEqual(payload["failed_step"], "")
        self.assertTrue(payload["retained_work_dir"])
        self.assertEqual(seen[0], ["sh", str(install_script.resolve())])
        self.assertNotIn([str((root / "work" / "bin" / "omj").resolve()), "doctor", "--json"], seen)
        self.assertIn([str((root / "work" / "bin" / "omj").resolve()), "--help"], seen)
        expected_omj_home = str((root / "work" / "home" / ".omj").resolve())
        expected_hermes_home = str((root / "work" / "home" / ".hermes").resolve())
        self.assertTrue(seen_env)
        self.assertTrue(all(env["OMJ_HOME"] == expected_omj_home for env in seen_env))
        self.assertTrue(all(env["HERMES_HOME"] == expected_hermes_home for env in seen_env))
        self.assertTrue(all(env["OMJ_HOME"] != "/real/operator/omj" for env in seen_env))
        self.assertTrue(all(env["HERMES_HOME"] != "/real/operator/hermes" for env in seen_env))
        self.assertEqual(payload["environment"]["OMJ_HOME"], expected_omj_home)
        self.assertEqual(payload["environment"]["HERMES_HOME"], expected_hermes_home)
        self.assertTrue(payload["installed_command_smoke"]["ok"])
        self.assertTrue(payload["installed_command_smoke"]["observed"])
        self.assertEqual(payload["environment"]["OMJ_RUN_SETUP"], "0")
        self.assertIn("isolated", payload["proof_boundary"])

    def test_install_script_smoke_default_runner_does_not_inherit_operator_controls(self) -> None:
        seen_env: list[dict[str, str]] = []

        def fake_run(command, *, stdout, stderr, text, timeout, check, env):
            del stdout, stderr, text, timeout, check
            run_env = dict(env or {})
            seen_env.append(run_env)
            if list(command)[0] == "sh":
                bin_dir = Path(run_env["OMJ_BIN_DIR"])
                bin_dir.mkdir(parents=True, exist_ok=True)
                installed = bin_dir / "omj"
                installed.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                installed.chmod(0o755)
            return subprocess.CompletedProcess(command, 0, "ok", "")

        with self.subTest("live"):
            from tempfile import TemporaryDirectory

            with TemporaryDirectory() as tmp:
                root = Path(tmp)
                install_script = root / "install.sh"
                install_script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                with patch.dict(
                    "os.environ",
                    {
                        "OMJ_HOME": "/real/operator/omj",
                        "HERMES_HOME": "/real/operator/hermes",
                        "OMJ_SCOPE": "project",
                        "OMJ_PROFILE_PACKS": "cto-loop",
                        "OMJ_SETUP_PROFILES": "1,3",
                        "OMJ_DEFAULT_EXECUTOR": "claude-code",
                        "OMJ_WITH_MCP": "1",
                        "OMJ_WITH_PLUGIN": "1",
                        "OMJ_PIP_ARGS": "--break-system-packages",
                    },
                    clear=False,
                ):
                    with patch("omj.release_smoke_core.subprocess.run", side_effect=fake_run):
                        payload = run_install_script_smoke(
                            repo_root=root,
                            install_script=install_script,
                            work_dir=root / "work",
                            timeout_seconds=5,
                        )

        self.assertTrue(payload["ok"])
        self.assertTrue(seen_env)
        blocked_keys = {
            "OMJ_SCOPE",
            "OMJ_PROFILE_PACKS",
            "OMJ_SETUP_PROFILES",
            "OMJ_DEFAULT_EXECUTOR",
            "OMJ_WITH_MCP",
            "OMJ_WITH_PLUGIN",
            "OMJ_PIP_ARGS",
        }
        for run_env in seen_env:
            self.assertTrue(blocked_keys.isdisjoint(run_env))
            self.assertEqual(run_env["OMJ_HOME"], str((root / "work" / "home" / ".omj").resolve()))
            self.assertEqual(run_env["HERMES_HOME"], str((root / "work" / "home" / ".hermes").resolve()))
            self.assertEqual(run_env["OMJ_RUN_SETUP"], "0")
            self.assertEqual(run_env["OMJ_SETUP_ARGS"], "")

    def test_exact_subprocess_runner_uses_only_explicit_env(self) -> None:
        with patch.dict("os.environ", {"OMJ_SCOPE": "project", "OMJ_PROFILE_PACKS": "cto-loop"}, clear=False):
            result = subprocess_runner_exact_env(
                [
                    sys.executable,
                    "-c",
                    "import os; print('OMJ_SCOPE' in os.environ, 'OMJ_PROFILE_PACKS' in os.environ, os.environ['HOME'])",
                ],
                5,
                {"HOME": "/tmp/omj-smoke-home"},
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "False False /tmp/omj-smoke-home")

    def test_install_script_smoke_fails_before_running_when_script_missing(self) -> None:
        def runner(command, _timeout, _env):  # pragma: no cover - missing script should stop first
            raise AssertionError(f"unexpected command: {command}")

        payload = run_install_script_smoke(repo_root="/tmp/no-such-omj-repo", runner=runner)

        self.assertFalse(payload["ok"])
        self.assertFalse(payload["observed"])
        self.assertEqual(payload["failed_step"], "install_script_missing")
        self.assertIn("--install-script", payload["recommended_next_action"])

    def test_live_smoke_records_successful_command_results(self) -> None:
        seen: list[list[str]] = []
        seen_env: list[dict[str, str]] = []

        def runner(command, _timeout, env):
            seen.append(list(command))
            seen_env.append(dict(env or {}))
            return CommandResult(command, 0, "ok", "")

        with patch("omj.release.shutil.which", return_value="/usr/local/bin/hermes"):
            payload = run_hermes_release_smoke(runner=runner, timeout_seconds=5, hermes_home="/tmp/hermes-smoke")

        self.assertTrue(payload["ok"])
        self.assertTrue(payload["observed"])
        self.assertEqual(payload["hermes_cli"]["path"], "/usr/local/bin/hermes")
        self.assertEqual(seen[0], ["hermes", "skills", "tap", "add", "rlaope/oh-my-hermes"])
        self.assertEqual(seen[-1], ["hermes", "skills", "inspect", "rlaope/oh-my-hermes/skills/oh-my-hermes"])
        self.assertTrue(all(env["HERMES_HOME"] == str(Path("/tmp/hermes-smoke").resolve()) for env in seen_env))
        self.assertTrue(all(result["environment"]["HERMES_HOME"] == str(Path("/tmp/hermes-smoke").resolve()) for result in payload["results"]))
        self.assertTrue(all(result["ok"] for result in payload["results"]))
        self.assertIn("does not prove a later chat session", payload["proof_boundary"])
        self.assertFalse(payload["installed_command_smoke"]["observed"])

    def test_live_smoke_can_include_installed_command_smoke(self) -> None:
        seen: list[list[str]] = []

        def runner(command, _timeout, _env):
            seen.append(list(command))
            return CommandResult(command, 0, "ok", "")

        with patch("omj.release.shutil.which", return_value="/usr/local/bin/hermes"):
            payload = run_hermes_release_smoke(
                runner=runner,
                timeout_seconds=5,
                hermes_home="/tmp/hermes-smoke",
                omj_home="/tmp/omj-smoke",
                omj_command="omj-dev",
                include_command_smoke=True,
            )

        omj_home = str(Path("/tmp/omj-smoke").resolve())
        hermes_home = str(Path("/tmp/hermes-smoke").resolve())
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["installed_command_smoke"]["observed"])
        self.assertTrue(payload["installed_command_smoke"]["path_check"]["ok"])
        self.assertEqual(payload["installed_command_smoke"]["path_check"]["mode"], "live")
        self.assertIn(["omj-dev", "--help"], seen)
        self.assertIn(["omj-dev", "release", "skill-content-smoke", "--json"], seen)
        self.assertIn(
            [
                "omj-dev",
                "--omj-home",
                omj_home,
                "--hermes-home",
                hermes_home,
                "release",
                "hermes-smoke",
                "--install-path",
                "setup",
                "--omj-command",
                "omj-dev",
            ],
            seen,
        )

    def test_installed_command_smoke_failure_marks_release_smoke_failed(self) -> None:
        def runner(command, _timeout, _env):
            if list(command) == ["omj-dev", "--help"]:
                return CommandResult(command, 127, "", "missing omj")
            return CommandResult(command, 0, "ok", "")

        with patch("omj.release.shutil.which", return_value="/usr/local/bin/hermes"):
            payload = run_hermes_release_smoke(runner=runner, omj_command="omj-dev", include_command_smoke=True)

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["failed_step"], "installed_command_smoke")
        self.assertEqual(payload["installed_command_smoke"]["failed_step"], "installed_omj_help")
        self.assertIn("console script", payload["recommended_next_action"])

    def test_installed_command_smoke_failure_from_skill_content_marks_release_smoke_failed(self) -> None:
        def runner(command, _timeout, _env):
            if list(command) == ["omj-dev", "release", "skill-content-smoke", "--json"]:
                return CommandResult(command, 1, '{"ok": false}', "missing context rail")
            return CommandResult(command, 0, "ok", "")

        with patch("omj.release.shutil.which", return_value="/usr/local/bin/hermes"):
            payload = run_hermes_release_smoke(runner=runner, omj_command="omj-dev", include_command_smoke=True)

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["failed_step"], "installed_command_smoke")
        self.assertEqual(payload["installed_command_smoke"]["failed_step"], "installed_omj_skill_content")
        self.assertIn("skill-content-smoke", payload["installed_command_smoke"]["recommended_next_action"])

    def test_installed_command_smoke_fails_before_help_when_omj_is_not_on_path(self) -> None:
        def runner(command, _timeout, _env):  # pragma: no cover - path check should stop first
            raise AssertionError(f"unexpected command: {command}")

        with patch("omj.release.shutil.which", side_effect=lambda command: "/usr/local/bin/hermes" if command == "hermes" else None):
            payload = run_hermes_release_smoke(runner=runner, omj_command="omj-dev", include_command_smoke=True)

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["failed_step"], "installed_command_smoke")
        self.assertEqual(payload["installed_command_smoke"]["failed_step"], "installed_omj_path")
        self.assertFalse(payload["installed_command_smoke"]["observed"])
        self.assertTrue(payload["installed_command_smoke"]["path_check"]["observed"])
        self.assertFalse(payload["installed_command_smoke"]["path_check"]["ok"])
        self.assertEqual(payload["installed_command_smoke"]["results"], [])
        self.assertIn("command -v omj-dev", payload["installed_command_smoke"]["recommended_next_action"])

    def test_live_smoke_stops_on_required_failure(self) -> None:
        def runner(command, _timeout, _env):
            if list(command)[:3] == ["hermes", "skills", "install"]:
                return CommandResult(command, 1, "", "scan failed")
            return CommandResult(command, 0, "ok", "")

        with patch("omj.release.shutil.which", return_value="/usr/local/bin/hermes"):
            payload = run_hermes_release_smoke(runner=runner)

        self.assertFalse(payload["ok"])
        self.assertEqual(payload["failed_step"], "skill_install")
        self.assertEqual(len(payload["results"]), 2)
        self.assertIn("Hermes skill scan", payload["recommended_next_action"])

    def test_live_smoke_reports_missing_hermes_cli_without_running_steps(self) -> None:
        def runner(command, _timeout, _env):  # pragma: no cover - should not be called
            raise AssertionError(f"unexpected command: {command}")

        with patch("omj.release.shutil.which", return_value=None):
            payload = run_hermes_release_smoke(runner=runner)

        self.assertFalse(payload["ok"])
        self.assertFalse(payload["observed"])
        self.assertEqual(payload["failed_step"], "hermes_cli")
        self.assertEqual(payload["results"], [])

    def test_missing_hermes_cli_can_still_observe_installed_command_smoke(self) -> None:
        seen: list[list[str]] = []

        def runner(command, _timeout, _env):
            seen.append(list(command))
            return CommandResult(command, 0, "ok", "")

        def which(command: str) -> str | None:
            if command == "omj-dev":
                return "/usr/local/bin/omj-dev"
            return None

        with patch("omj.release.shutil.which", side_effect=which):
            payload = run_hermes_release_smoke(runner=runner, omj_command="omj-dev", include_command_smoke=True)

        self.assertFalse(payload["ok"])
        self.assertFalse(payload["observed"])
        self.assertEqual(payload["failed_step"], "hermes_cli")
        self.assertTrue(payload["installed_command_smoke"]["observed"])
        self.assertIn(["omj-dev", "--help"], seen)
        self.assertEqual(payload["results"], [])

    def test_subprocess_runner_reports_missing_executable_as_command_failure(self) -> None:
        result = subprocess_runner(["/definitely/not/a/real/omj-command"], 1)

        self.assertEqual(result.returncode, 127)
        self.assertIn("No such file", result.stderr)

    def test_subprocess_runner_normalizes_timeout_bytes_output(self) -> None:
        result = subprocess_runner(
            [
                sys.executable,
                "-c",
                "import sys,time; sys.stdout.write('hello'); sys.stdout.flush(); sys.stderr.write('warn'); sys.stderr.flush(); time.sleep(5)",
            ],
            1,
        )

        self.assertEqual(result.returncode, 124)
        self.assertIn("hello", result.stdout)
        self.assertTrue(result.stderr)


if __name__ == "__main__":
    unittest.main()
