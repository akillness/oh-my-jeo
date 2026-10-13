from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()

from omj.paths import resolve_paths
from omj.plugin_pack import inspect_plugin_bundle
from test_plugin_distribution import FakeHermesContext, load_installed_plugin


class HomeBindingParityTests(unittest.TestCase):
    def _setup(self, omj_home: Path, hermes_home: Path) -> tuple[dict, Path]:
        status, stdout, stderr = run_cli(
            [
                "--omj-home",
                str(omj_home),
                "--hermes-home",
                str(hermes_home),
                "setup",
                "--yes",
                "--no-menubar",
            ]
        )
        self.assertEqual((status, stderr), (0, ""))
        return json.loads(stdout), hermes_home / "plugins" / "omj"

    def _binding_check(self, omj_home: Path, hermes_home: Path) -> dict:
        status, stdout, stderr = run_cli(["--omj-home", str(omj_home), "--hermes-home", str(hermes_home), "doctor"])
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        checks = [
            check
            for check in payload["checks"]
            if "plugin" in str(check.get("name", "")) and "binding" in str(check.get("name", ""))
        ]
        self.assertEqual(len(checks), 1, checks)
        return checks[0]

    def test_default_and_custom_setup_persist_explicit_home_binding(self) -> None:
        """Setup must record the selected OMJ store in each Hermes profile."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            default_omj = (root / ".omj").resolve()
            default_hermes = (root / ".hermes").resolve()
            with patch.dict(
                os.environ,
                {"HOME": str(root), "OMJ_HOME": str(default_omj), "HERMES_HOME": str(default_hermes)},
                clear=False,
            ):
                status, stdout, stderr = run_cli(["setup", "--yes", "--no-menubar"])
                self.assertEqual((status, stderr), (0, ""))
                self.assertIsInstance(json.loads(stdout), dict)
                default_config = (default_hermes / "config.yaml").read_text(encoding="utf-8")
                self.assertRegex(
                    default_config,
                    rf"(?m)^\s+omj_home:\s*[\"']?{re.escape(str(default_omj))}[\"']?\s*$",
                )

            custom_omj = (root / "stores" / "custom-omj").resolve()
            custom_hermes = (root / "profiles" / "custom-hermes").resolve()
            self._setup(custom_omj, custom_hermes)
            custom_config = (custom_hermes / "config.yaml").read_text(encoding="utf-8")
            self.assertRegex(
                custom_config,
                rf"(?m)^\s+omj_home:\s*[\"']?{re.escape(str(custom_omj))}[\"']?\s*$",
            )

    def test_host_configured_home_wins_over_wrong_ambient_store_for_all_retained_handlers(self) -> None:
        """Native handlers must read the host-selected store, not process ambient paths."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected_omj = (root / "selected" / ".omj").resolve()
            selected_hermes = (root / "selected" / ".hermes").resolve()
            ambient_omj = (root / "ambient" / ".omj").resolve()
            ambient_hermes = (root / "ambient" / ".hermes").resolve()
            self._setup(selected_omj, selected_hermes)
            (selected_omj / "runtime" / "state.json").write_text(
                json.dumps({"last_run_id": "selected-run", "version": "selected"}), encoding="utf-8"
            )
            (ambient_omj / "runtime").mkdir(parents=True)
            (ambient_omj / "runtime" / "state.json").write_text(
                json.dumps({"last_run_id": "ambient-run", "version": "ambient"}), encoding="utf-8"
            )

            plugin = load_installed_plugin(selected_hermes / "plugins" / "omj")
            context = FakeHermesContext()
            plugin.register(context)
            host_kwargs = {
                "omj_home": str(selected_omj),
                "hermes_home": str(selected_hermes),
                "host": "hermes-agent",
                "session_id": "binding-session",
            }
            with patch.dict(
                os.environ,
                {"OMJ_HOME": str(ambient_omj), "HERMES_HOME": str(ambient_hermes)},
                clear=False,
            ):
                status_payload = json.loads(context.tools["omj_status"]["args"][2]({}, **host_kwargs))
                hud_payload = json.loads(context.tools["omj_hud"]["args"][2]({}, **host_kwargs))
                probe_payload = json.loads(context.tools["omj_probe"]["args"][2]({}, **host_kwargs))

            self.assertEqual(status_payload["omj_home"], str(selected_omj))
            self.assertEqual(status_payload["latest_run_id"], "selected-run")
            self.assertEqual(hud_payload["omj_home"], str(selected_omj))
            self.assertEqual(hud_payload["runtime"]["latest_run_id"], "selected-run")
            self.assertEqual(probe_payload["omj_home"], str(selected_omj))
            self.assertEqual(status_payload["plugin_host_observation"]["session_id"], "binding-session")
            observation_path = selected_omj / "runtime" / "plugin_host_observations.jsonl"
            observations = [json.loads(line) for line in observation_path.read_text(encoding="utf-8").splitlines()]
            self.assertTrue(any(item.get("session_id") == "binding-session" for item in observations))
            self.assertFalse((ambient_omj / "runtime" / "plugin_host_observations.jsonl").exists())

    def test_native_interact_uses_host_binding_for_executor_and_session_writes(self) -> None:
        """Native chat must resolve the installed host homes, not ambient env homes."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected_omj = (root / "selected" / ".omj").resolve()
            selected_hermes = (root / "selected" / ".hermes").resolve()
            ambient_omj = (root / "ambient" / ".omj").resolve()
            ambient_hermes = (root / "ambient" / ".hermes").resolve()
            self._setup(selected_omj, selected_hermes)
            profile_path = selected_omj / "setup-profile.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile.update(
                {
                    "selected_categories": ["codex-lifecycle"],
                    "default_executor": "codex",
                    "dispatch_policy": "ask_before_dispatch",
                }
            )
            profile_path.write_text(json.dumps(profile), encoding="utf-8")

            plugin = load_installed_plugin(selected_hermes / "plugins" / "omj")
            context = FakeHermesContext()
            plugin.register(context)
            args = {
                "message": "prepare a safe refactor",
                "mode": "delegate",
                "record_session": True,
            }
            with patch.dict(
                os.environ,
                {"OMJ_HOME": str(ambient_omj), "HERMES_HOME": str(ambient_hermes)},
                clear=False,
            ):
                payload = json.loads(
                    context.tools["omj_interact"]["args"][2](
                        args,
                        omj_home=str(selected_omj),
                        hermes_home=str(selected_hermes),
                        host="hermes-agent",
                        session_id="bound-interact-session",
                    )
                )

            self.assertEqual(payload["delegation"]["selected_executor_profile"], "codex")
            self.assertEqual(payload["wrapper_session"]["recorded"], True)
            self.assertEqual(payload["plugin_host_observation"]["host"], "hermes-agent")
            self.assertEqual(payload["plugin_host_observation"]["session_id"], "bound-interact-session")
            self.assertEqual(payload["plugin_host_observation"]["event"], "tool_call")
            self.assertEqual(payload["plugin_host_observation"]["status"], "observed")
            wrapper_session_id = payload["wrapper_session"]["session_id"]
            expected_session_id = "ws-" + hashlib.sha256(
                payload["thread_key"].encode("utf-8")
            ).hexdigest()[:24]
            self.assertEqual(wrapper_session_id, expected_session_id)
            session_path = selected_omj / "runtime" / "wrapper_sessions" / wrapper_session_id / "session.json"
            persisted_session = json.loads(session_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted_session["session_id"], wrapper_session_id)
            self.assertEqual(persisted_session["thread_key"], payload["thread_key"])

            observation_path = selected_omj / "runtime" / "plugin_host_observations.jsonl"
            observations = [
                json.loads(line)
                for line in observation_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertTrue(
                any(
                    item.get("event") == "tool_call"
                    and item.get("tool") == "omj_interact"
                    and item.get("host") == "hermes-agent"
                    and item.get("session_id") == "bound-interact-session"
                    and item.get("status") == "observed"
                    for item in observations
                )
            )
            self.assertFalse((ambient_omj / "runtime").exists())

    def test_native_interact_refusal_does_not_create_runtime_state(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected_omj = (root / "selected" / ".omj").resolve()
            selected_hermes = (root / "selected" / ".hermes").resolve()
            self._setup(selected_omj, selected_hermes)
            runtime_before = {
                path.relative_to(selected_omj): path.read_bytes()
                for path in selected_omj.joinpath("runtime").rglob("*")
                if path.is_file()
            }
            plugin = load_installed_plugin(selected_hermes / "plugins" / "omj")
            context = FakeHermesContext()
            plugin.register(context)

            payload = json.loads(
                context.tools["omj_interact"]["args"][2](
                    {"message": "   "},
                    omj_home=str(selected_omj),
                    hermes_home=str(selected_hermes),
                    host="hermes-agent",
                    session_id="refused-interact-session",
                )
            )
            runtime_after = {
                path.relative_to(selected_omj): path.read_bytes()
                for path in selected_omj.joinpath("runtime").rglob("*")
                if path.is_file()
            }

            self.assertEqual(payload["status"], "error")
            self.assertEqual(runtime_after, runtime_before)
            self.assertNotIn("plugin_host_observation", payload)
            self.assertFalse(
                (selected_omj / "runtime" / "wrapper_sessions" / "refused-interact-session").exists()
            )

    def test_args_home_control_case_reads_selected_store(self) -> None:
        """The existing explicit tool-argument path remains a green control."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            selected_omj = (root / "selected" / ".omj").resolve()
            selected_hermes = (root / "selected" / ".hermes").resolve()
            self._setup(selected_omj, selected_hermes)
            (selected_omj / "runtime" / "state.json").write_text(
                json.dumps({"last_run_id": "selected-run"}), encoding="utf-8"
            )
            plugin = load_installed_plugin(selected_hermes / "plugins" / "omj")
            context = FakeHermesContext()
            plugin.register(context)
            payload = json.loads(
                context.tools["omj_status"]["args"][2](
                    {"omj_home": str(selected_omj), "limit": 1},
                    host="hermes-agent",
                    session_id="control-session",
                )
            )
            self.assertEqual(payload["omj_home"], str(selected_omj))
            self.assertEqual(payload["latest_run_id"], "selected-run")



    def test_doctor_flags_missing_invalid_and_mismatched_profile_binding(self) -> None:
        """Doctor must surface absent, malformed, and contradictory profile bindings."""
        cases = (
            ("missing", "remove"),
            ("invalid", "omj_home: '${UNKNOWN_HOME}'"),
            ("mismatched", "omj_home: '/wrong/store'"),
        )
        for name, replacement in cases:
            with self.subTest(binding=name), TemporaryDirectory() as tmp:
                root = Path(tmp)
                omj_home = (root / "selected" / ".omj").resolve()
                hermes_home = (root / "selected" / ".hermes").resolve()
                self._setup(omj_home, hermes_home)
                config_path = hermes_home / "config.yaml"
                config = config_path.read_text(encoding="utf-8")
                if replacement == "remove":
                    config = re.sub(r"(?m)^plugins:\n(?:  .*\n|\n)*", "", config)
                    self.assertNotRegex(config, r"(?m)^\s+omj_home:")
                else:
                    config += f"\nplugins:\n  entries:\n    omj:\n      settings:\n        {replacement}\n"
                config_path.write_text(config, encoding="utf-8")
                check = self._binding_check(omj_home, hermes_home)
                self.assertIn(check["severity"], {"warning", "blocking"})
                self.assertTrue(str(check["message"]).strip())

    def _make_valid_stale_bundle(self, plugin_dir: Path) -> None:
        init_path = plugin_dir / "__init__.py"
        stale = init_path.read_text(encoding="utf-8")
        stale = stale.replace(
            "    ctx.register_tool(\n"
            '        "omj_probe",\n'
            "        _TOOLSET,\n"
            "        OMJ_PROBE_SCHEMA,\n"
            "        omj_probe_handler,\n"
            '        description=OMJ_PROBE_SCHEMA["description"],\n'
            "    )\n",
            "",
        )
        init_path.write_text(stale, encoding="utf-8")
        manifest_path = plugin_dir / ".omj-plugin-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for record in manifest["files"]:
            if record["path"] == "__init__.py":
                record["sha256"] = hashlib.sha256(stale.encode("utf-8")).hexdigest()
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def test_managed_update_refreshes_stale_plugin_and_preserves_user_config_hooks(self) -> None:
        """A package update must restore shipped registrations without replacing operator files."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            omj_home = root / ".omj"
            hermes_home = root / ".hermes"
            self._setup(omj_home, hermes_home)
            plugin_dir = hermes_home / "plugins" / "omj"
            self._make_valid_stale_bundle(plugin_dir)
            config_path = hermes_home / "config.yaml"
            config_path.write_text(config_path.read_text(encoding="utf-8") + "\nuser_owned: keep\n", encoding="utf-8")
            hooks_path = hermes_home / "hooks.yaml"
            hooks_path.write_text("user_hook: keep\n", encoding="utf-8")

            status, _, stderr = run_cli(
                [
                    "--omj-home",
                    str(omj_home),
                    "--hermes-home",
                    str(hermes_home),
                    "update",
                    "--command-package-updated",
                ]
            )
            self.assertEqual((status, stderr), (0, ""))
            inspection = inspect_plugin_bundle(resolve_paths(omj_home, hermes_home))
            self.assertFalse(inspection["plugin_bundle_stale"])
            self.assertIn("omj_probe", inspection["registered_tools"])
            self.assertIn("user_owned: keep", config_path.read_text(encoding="utf-8"))
            self.assertEqual(hooks_path.read_text(encoding="utf-8"), "user_hook: keep\n")

    def test_managed_update_dry_run_does_not_refresh_or_touch_operator_files(self) -> None:
        """Dry-run update reports no writes, including plugin refresh and operator files."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            omj_home = root / ".omj"
            hermes_home = root / ".hermes"
            self._setup(omj_home, hermes_home)
            plugin_dir = hermes_home / "plugins" / "omj"
            self._make_valid_stale_bundle(plugin_dir)
            config_path = hermes_home / "config.yaml"
            config_before = config_path.read_text(encoding="utf-8")
            hooks_path = hermes_home / "hooks.yaml"
            hooks_path.write_text("user_hook: keep\n", encoding="utf-8")
            init_before = (plugin_dir / "__init__.py").read_text(encoding="utf-8")

            status, stdout, stderr = run_cli(
                [
                    "--omj-home",
                    str(omj_home),
                    "--hermes-home",
                    str(hermes_home),
                    "update",
                    "--command-package-updated",
                    "--dry-run",
                ]
            )
            self.assertEqual((status, stderr), (0, ""))
            payload = json.loads(stdout)
            self.assertTrue(payload["dry_run"])
            self.assertEqual((plugin_dir / "__init__.py").read_text(encoding="utf-8"), init_before)
            self.assertEqual(config_path.read_text(encoding="utf-8"), config_before)
            self.assertEqual(hooks_path.read_text(encoding="utf-8"), "user_hook: keep\n")
            inspection = inspect_plugin_bundle(resolve_paths(omj_home, hermes_home))
            self.assertIn("omj_probe", inspection["missing_registered_tools"])


if __name__ == "__main__":
    unittest.main()
