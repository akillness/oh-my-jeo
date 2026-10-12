from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()

from omj.paths import resolve_paths
from omj.commands import setup as setup_commands

from omj.install.config_adapter import ensure_omj_home_binding

class LifecycleAlignmentTests(unittest.TestCase):
    def _base(self, root: Path) -> list[str]:
        return ["--omj-home", str(root / ".omj"), "--hermes-home", str(root / ".hermes")]

    def test_machine_modes_never_prompt_even_when_interactive_is_requested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with (
                patch("omj.commands.setup._ask_setup_language") as ask_language,
                patch("omj.commands.setup._ask_setup_scope") as ask_scope,
                patch("omj.commands.setup._run_setup_wizard") as wizard,
                patch("omj.commands.setup._offer_github_star_before_setup") as star,
            ):
                status, stdout, stderr = run_cli(self._base(root) + ["setup", "--interactive"], output_json=True)
                self.assertEqual((status, stderr), (0, ""))
                payload = json.loads(stdout)
                self.assertTrue(payload["ok"])
                status, stdout, stderr = run_cli(
                    self._base(root / "dry") + ["setup", "--interactive", "--dry-run"],
                    output_json=False,
                )
                self.assertEqual((status, stderr), (0, ""))
                self.assertIn("dry run", stdout.lower())
                self.assertNotIn("ready", stdout.lower())
                self.assertNotIn("configured", stdout.lower())
                self.assertNotIn("saved", stdout.lower())
                self.assertFalse((root / "dry" / ".omj").exists())
                self.assertFalse((root / "dry" / ".hermes").exists())
                ask_language.assert_not_called()
                ask_scope.assert_not_called()
                wizard.assert_not_called()
                star.assert_not_called()

    def test_wizard_owner_choice_is_optional_and_preserves_hermes_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            calls: list[list[dict[str, str]]] = []

            def choose(*args, **kwargs):
                options = kwargs.get("options") or (args[2] if len(args) > 2 else [])
                calls.append(options)
                return "choose"

            with patch("omj.commands.setup._ask_single_choice", side_effect=choose):
                selected = setup_commands._ask_default_executor(use_color=False, language="en")
            self.assertEqual(selected, "choose")
            values = {option["value"] for option in calls[-1]}
            self.assertTrue({"choose", "hermes", "codex", "claude-code", "generic"}.issubset(values))

            status, stdout, stderr = run_cli(self._base(root) + ["setup", "--no-interactive"])
            self.assertEqual((status, stderr), (0, ""))
            first_profile = json.loads(paths.setup_profile_path.read_text(encoding="utf-8"))
            status, stdout, stderr = run_cli(self._base(root) + ["setup", "--no-interactive"])
            self.assertEqual((status, stderr), (0, ""))
            second_profile = json.loads(paths.setup_profile_path.read_text(encoding="utf-8"))
            first_profile.pop("updated_at", None)
            second_profile.pop("updated_at", None)
            self.assertEqual(second_profile, first_profile)
            self.assertIn("configuration unchanged", stdout.lower())

    def test_normal_setup_never_stars_github_without_explicit_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("omj.commands.setup._try_star_github_repo") as star:
                status, _stdout, stderr = run_cli(self._base(root) + ["setup", "--interactive"], output_json=False)
            self.assertEqual((status, stderr), (0, ""))
            star.assert_not_called()

    def test_setup_enables_owned_plugin_without_dropping_unrelated_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hermes = root / ".hermes"
            hermes.mkdir(parents=True)
            config = hermes / "config.yaml"
            config.write_text(
                "model:\n  default: gpt-6-sol\n"
                "plugins:\n"
                "  enabled:\n    - unrelated-plugin\n"
                "  entries:\n    unrelated-plugin:\n      settings:\n        keep: true\n",
                encoding="utf-8",
            )
            status, stdout, stderr = run_cli(self._base(root) + ["setup", "--no-interactive"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(json.loads(stdout)["ok"], True)
            text = config.read_text(encoding="utf-8")
            self.assertIn("    - unrelated-plugin", text)
            self.assertIn("    - omj", text)
            self.assertIn("default: gpt-6-sol", text)
            self.assertIn("keep: true", text)

    def test_apply_uses_selected_home_and_uninstall_only_reverses_owned_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            paths.hermes_config_path.parent.mkdir(parents=True)
            paths.hermes_config_path.write_text(
                "model:\n  default: operator-model\n"
                "plugins:\n  entries:\n    omj:\n      settings:\n        unrelated: keep\n",
                encoding="utf-8",
            )
            status, _stdout, stderr = run_cli(self._base(root) + ["apply"])
            self.assertEqual((status, stderr), (0, ""))
            config_after_apply = paths.hermes_config_path.read_text(encoding="utf-8")
            self.assertIn(str(paths.omj_home.resolve()), config_after_apply)
            self.assertIn("unrelated: keep", config_after_apply)
            paths.hermes_config_path.write_text(config_after_apply + "operator_edit: retained\n", encoding="utf-8")
            status, stdout, stderr = run_cli(self._base(root) + ["uninstall", "--registration-only"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertIn("operator-model", paths.hermes_config_path.read_text(encoding="utf-8"))
            self.assertIn("unrelated: keep", paths.hermes_config_path.read_text(encoding="utf-8"))
            self.assertIn("operator_edit: retained", paths.hermes_config_path.read_text(encoding="utf-8"))
            self.assertNotIn(str(paths.omj_home.resolve()), paths.hermes_config_path.read_text(encoding="utf-8"))
            self.assertEqual(json.loads(stdout)["config_changed"], True)

    def test_full_uninstall_removes_only_owned_config_and_plugin_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self._base(root)
            self.assertEqual(run_cli(base + ["setup", "--no-interactive"])[0], 0)
            config = root / ".hermes" / "config.yaml"
            config.write_text(config.read_text(encoding="utf-8") + "operator_owned: retained\n", encoding="utf-8")
            plugin_dir = root / ".hermes" / "plugins" / "omj"
            (plugin_dir / "operator-file.txt").write_text("keep", encoding="utf-8")
            status, stdout, stderr = run_cli(base + ["uninstall", "--all"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertIn("operator_owned: retained", config.read_text(encoding="utf-8"))
            self.assertTrue((plugin_dir / "operator-file.txt").exists())
            self.assertNotIn(str(root / ".omj" / "skills"), config.read_text(encoding="utf-8"))
            self.assertEqual(json.loads(stdout)["config_changed"], True)

    def test_registration_uninstall_removes_only_owned_inline_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            paths.hermes_config_path.parent.mkdir(parents=True)
            paths.hermes_config_path.write_text(
                "plugins:\n"
                "  enabled: [omj, other-plugin]\n"
                "  entries:\n"
                "    other-plugin:\n"
                "      settings:\n"
                "        omj_home: /operator/other\n"
                "    omj:\n"
                "      settings:\n"
                f"        omj_home: {paths.omj_home.resolve()}\n"
                "        operator_setting: keep\n",
                encoding="utf-8",
            )
            status, stdout, stderr = run_cli(self._base(root) + ["uninstall", "--registration-only"])
            self.assertEqual((status, stderr), (0, ""))
            text = paths.hermes_config_path.read_text(encoding="utf-8")
            self.assertIn("    omj:\n", text)
            self.assertNotIn("omj_home:", text.split("    omj:\n", 1)[1])
            self.assertIn("  enabled: [ other-plugin]", text)
            self.assertIn("other-plugin", text)
            self.assertIn("/operator/other", text)
            self.assertIn("operator_setting: keep", text)
            self.assertTrue(json.loads(stdout)["config_changed"])

    def test_registration_uninstall_does_not_remove_mismatched_owned_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            paths.hermes_config_path.parent.mkdir(parents=True)
            original = (
                "plugins:\n"
                "  enabled:\n"
                "    - omj\n"
                "  entries:\n"
                "    omj:\n"
                "      settings:\n"
                "        omj_home: /operator/not-omj\n"
                "        keep: true\n"
            )
            paths.hermes_config_path.write_text(original, encoding="utf-8")
            status, _stdout, stderr = run_cli(self._base(root) + ["uninstall", "--registration-only"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(paths.hermes_config_path.read_text(encoding="utf-8"), original)

    def test_force_uninstall_removes_edited_owned_plugin_but_preserves_foreign_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self._base(root)
            self.assertEqual(run_cli(base + ["setup", "--no-interactive"])[0], 0)
            plugin_dir = root / ".hermes" / "plugins" / "omj"
            descriptor = plugin_dir / "plugin.yaml"
            descriptor.write_text(descriptor.read_text(encoding="utf-8") + "operator_edit: true\n", encoding="utf-8")
            edited_descriptor = descriptor.read_bytes()
            foreign = root / ".hermes" / "plugins" / "foreign"
            foreign.mkdir(parents=True)
            foreign_bytes = b"operator-owned-foreign-plugin\n"
            (foreign / "plugin.yaml").write_bytes(foreign_bytes)
            status, _stdout, stderr = run_cli(base + ["uninstall", "--all"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertTrue(plugin_dir.exists())
            self.assertEqual(descriptor.read_bytes(), edited_descriptor)
            receipt = plugin_dir / ".omj-plugin-manifest.json"
            self.assertTrue(receipt.is_file())
            receipt_payload = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertIn("plugin.yaml", {str(item["path"]) for item in receipt_payload["files"]})
            status, _stdout, stderr = run_cli(base + ["uninstall", "--all", "--force"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertFalse(plugin_dir.exists())
            self.assertEqual((foreign / "plugin.yaml").read_bytes(), foreign_bytes)

    def test_uninstall_dry_run_leaves_selected_home_tree_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self._base(root)
            self.assertEqual(run_cli(base + ["setup", "--no-interactive"])[0], 0)

            def snapshot() -> dict[str, tuple[str, bytes | str]]:
                result: dict[str, tuple[str, bytes | str]] = {}
                for path in sorted(root.rglob("*")):
                    rel = str(path.relative_to(root))
                    if path.is_symlink():
                        result[rel] = ("link", str(path.readlink()))
                    elif path.is_file():
                        result[rel] = ("file", path.read_bytes())
                return result

            before = snapshot()
            status, _stdout, stderr = run_cli(base + ["uninstall", "--all", "--dry-run"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(snapshot(), before)


    def test_setup_handles_all_plugin_enablement_shapes_and_localized_summaries(self) -> None:
        shapes = {
            "absent": "model:\n  default: operator-model\n",
            "inline": "plugins:\n  enabled: [other-plugin]\n",
            "block": "plugins:\n  enabled:\n    - other-plugin\n",
            "no_enabled": "plugins:\n  entries:\n    other-plugin:\n      settings:\n        keep: true\n",
        }
        expected_messages = {"appended plugins.enabled", "expanded plugins.enabled", "added plugin to plugins.enabled", "inserted plugins.enabled"}
        localized = {
            "en": "OMJ plugin enablement configured",
            "ko": "OMJ 플러그인 활성화가 설정됨",
            "ja": "OMJ プラグインの有効化を設定しました",
            "zh": "已配置 OMJ 插件启用设置",
        }
        for shape, initial in shapes.items():
            with self.subTest(shape=shape):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    config = root / ".hermes" / "config.yaml"
                    config.parent.mkdir(parents=True)
                    config.write_text(initial, encoding="utf-8")
                    status, stdout, stderr = run_cli(self._base(root) + ["setup", "--no-interactive", "--json"])
                    self.assertEqual((status, stderr), (0, ""))
                    payload = json.loads(stdout)
                    messages = payload["steps"]["apply"]["messages"]
                    self.assertTrue(set(messages) & expected_messages)
        for locale, label in localized.items():
            with self.subTest(locale=locale):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    status, stdout, stderr = run_cli(self._base(root) + ["setup", "--no-interactive", "--language", locale], output_json=False)
                    self.assertEqual((status, stderr), (0, ""))
                    self.assertIn(label, stdout)
    def test_repeated_setup_reports_configuration_unchanged_for_each_locale(self) -> None:
        for locale in ("en", "ko", "ja", "zh"):
            with self.subTest(locale=locale):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    base = self._base(root) + ["setup", "--no-interactive", "--language", locale, "--json"]
                    first_status, _first_stdout, first_stderr = run_cli(base)
                    self.assertEqual((first_status, first_stderr), (0, ""))
                    second_status, second_stdout, second_stderr = run_cli(base)
                    self.assertEqual((second_status, second_stderr), (0, ""))
                    messages = json.loads(second_stdout)["steps"]["apply"]["messages"]
                    self.assertIn("configuration unchanged", messages)

    def test_setup_preview_with_each_enablement_shape_does_not_write_config(self) -> None:
        shapes = ("", "plugins:\n  enabled: [other-plugin]\n", "plugins:\n  enabled:\n    - other-plugin\n", "plugins:\n  entries: {}\n")
        for initial in shapes:
            with self.subTest(initial=initial):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    config = root / ".hermes" / "config.yaml"
                    config.parent.mkdir(parents=True)
                    config.write_text(initial, encoding="utf-8")
                    before = config.read_bytes()
                    status, _stdout, stderr = run_cli(self._base(root) + ["setup", "--no-interactive", "--dry-run", "--json"])
                    self.assertEqual((status, stderr), (0, ""))
                    self.assertEqual(config.read_bytes(), before)
                    self.assertFalse((root / ".hermes" / "plugins" / "omj").exists())
    def test_flow_style_plugins_mapping_is_preserved_or_refused_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / ".hermes" / "config.yaml"
            config.parent.mkdir(parents=True)
            original = "plugins: {enabled: [operator-plugin], disabled: []}\n"
            config.write_bytes(original.encode("utf-8"))

            status, _stdout, _stderr = run_cli(self._base(root) + ["setup", "--no-interactive"])

            if status == 0:
                text = config.read_text(encoding="utf-8")
                self.assertEqual(sum(line.startswith("plugins:") for line in text.splitlines()), 1)
                self.assertIn("operator-plugin", text)
                self.assertIn("omj", text)
            else:
                self.assertEqual(status, 2)
                self.assertEqual(config.read_bytes(), original.encode("utf-8"))
    def test_apply_flow_style_plugins_mapping_is_preserved_or_refused_before_binding_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / ".hermes" / "config.yaml"
            config.parent.mkdir(parents=True)
            original = "plugins: {enabled: [omj], disabled: []}\n"
            config.write_bytes(original.encode("utf-8"))

            status, _stdout, _stderr = run_cli(self._base(root) + ["apply"])

            if status == 0:
                text = config.read_text(encoding="utf-8")
                self.assertEqual(sum(line.startswith("plugins:") for line in text.splitlines()), 1)
                self.assertIn("omj", text)
                self.assertIn("omj_home", text)
            else:
                self.assertEqual(status, 2)
                self.assertEqual(config.read_bytes(), original.encode("utf-8"))

    def test_home_binding_refuses_or_preserves_flow_style_plugins_mapping(self) -> None:
        flow_texts = (
            "plugins: {enabled: [omj], disabled: []}\n",
            "plugins: {enabled: [omj, operator-plugin], disabled: []}\n",
        )
        with tempfile.TemporaryDirectory() as tmp:
            for flow_text in flow_texts:
                with self.subTest(flow_text=flow_text):
                    try:
                        change = ensure_omj_home_binding(flow_text, Path(tmp) / ".omj")
                    except ValueError:
                        continue
                    if change.changed:
                        self.assertEqual(sum(line.startswith("plugins:") for line in change.text.splitlines()), 1)
                        self.assertIn("omj", change.text)
                        self.assertIn("omj_home", change.text)
                    else:
                        self.assertEqual(change.text, flow_text)


    def test_profile_sync_registers_primary_store_twice_and_preserves_explicit_dispatch_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profile = root / ".hermes" / "profiles" / "bot"
            profile.mkdir(parents=True)
            plain_profile = root / ".hermes" / "profiles" / "plain"
            plain_profile.mkdir(parents=True)
            explicit_home = root / "dispatch-home"
            env_bytes = (
                f"OMJ_HOME={explicit_home}\n"
                "HERMES_HOME=/operator/dispatch-hermes\n"
                "OMJ_DEFAULT_EXECUTOR=codex\n"
            ).encode("utf-8")
            (profile / ".env").write_bytes(env_bytes)
            base = self._base(root)

            first_status, first_stdout, first_stderr = run_cli(base + ["setup", "--no-interactive"])
            self.assertEqual((first_status, first_stderr), (0, ""))
            first_rows = {row["profile"]: row for row in json.loads(first_stdout)["hermes_profiles"]}
            self.assertEqual(first_rows["bot"]["status"], "bootstrapped")
            self.assertEqual(first_rows["plain"]["status"], "bootstrapped")
            profile_config = profile / "config.yaml"
            plain_config = plain_profile / "config.yaml"
            primary_skills = root / ".omj" / "skills"
            self.assertTrue(primary_skills.is_dir())
            first_config = profile_config.read_text(encoding="utf-8")
            plain_first_config = plain_config.read_text(encoding="utf-8")
            self.assertIn(str(primary_skills), first_config)
            self.assertIn(str(primary_skills), plain_first_config)
            self.assertIn(str(explicit_home), first_config)
            self.assertFalse((plain_profile / ".omj" / "skills").exists())
            self.assertFalse((explicit_home / "skills").exists())
            self.assertEqual((profile / ".env").read_bytes(), env_bytes)

            second_status, second_stdout, second_stderr = run_cli(base + ["setup", "--no-interactive"])
            self.assertEqual((second_status, second_stderr), (0, ""))
            second_rows = {row["profile"]: row for row in json.loads(second_stdout)["hermes_profiles"]}
            self.assertEqual(second_rows["bot"]["status"], "refreshed")
            self.assertEqual(second_rows["bot"]["registration"], "unchanged")
            self.assertEqual(second_rows["plain"]["status"], "refreshed")
            self.assertEqual(second_rows["plain"]["registration"], "unchanged")
            self.assertIn(str(primary_skills), profile_config.read_text(encoding="utf-8"))
            self.assertIn(str(primary_skills), plain_config.read_text(encoding="utf-8"))
            self.assertIn(str(explicit_home), profile_config.read_text(encoding="utf-8"))
            self.assertFalse((plain_profile / ".omj" / "skills").exists())
            self.assertFalse((explicit_home / "skills").exists())
            self.assertEqual((profile / ".env").read_bytes(), env_bytes)

    def test_dirty_profile_plugin_becomes_failed_row_and_other_profiles_continue(self) -> None:

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            profiles = root / ".hermes" / "profiles"
            for name in ("dirty", "healthy"):
                (profiles / name).mkdir(parents=True)
            base = self._base(root)
            first_status, _first_stdout, first_stderr = run_cli(base + ["setup", "--no-interactive"])
            self.assertEqual((first_status, first_stderr), (0, ""))
            primary_skills = str(root / ".omj" / "skills")
            for name in ("dirty", "healthy"):
                config = profiles / name / "config.yaml"
                config.write_text(config.read_text(encoding="utf-8").replace(str(profiles / name / ".omj" / "skills"), primary_skills), encoding="utf-8")
            dirty_plugin = profiles / "dirty" / "plugins" / "omj" / "plugin.yaml"
            dirty_before = dirty_plugin.read_bytes()
            dirty_plugin.write_bytes(dirty_before + b"operator_edit: retain\n")
            dirty_after = dirty_plugin.read_bytes()
            self.assertNotEqual(dirty_after, dirty_before)

            status, stdout, stderr = run_cli(base + ["setup", "--no-interactive"])

            self.assertEqual((status, stderr), (0, ""))
            rows = {row["profile"]: row for row in json.loads(stdout)["hermes_profiles"]}
            self.assertEqual(rows["dirty"]["status"], "failed")
            self.assertIn("managed plugin files changed", rows["dirty"]["error"])
            self.assertEqual(rows["healthy"]["status"], "refreshed")
            self.assertEqual(dirty_plugin.read_bytes(), dirty_after)
            self.assertTrue((profiles / "healthy" / "plugins" / "omj" / "plugin.yaml").is_file())


    def test_concurrent_config_write_is_not_overwritten_by_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            paths.hermes_config_path.parent.mkdir(parents=True)
            paths.hermes_config_path.write_text("model:\n  default: operator-model\n", encoding="utf-8")
            original = paths.hermes_config_path.read_text(encoding="utf-8")
            competing = original + "concurrent_writer: retained\n"
            real_read = setup_commands.read_config
            reads = {"count": 0}

            def read_with_competing_write(path: Path) -> str:
                value = real_read(path)
                reads["count"] += 1
                if reads["count"] == 1:
                    path.write_text(competing, encoding="utf-8")
                return value

            with patch("omj.commands.setup.read_config", side_effect=read_with_competing_write):
                status, _stdout, stderr = run_cli(self._base(root) + ["apply"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertIn("concurrent_writer: retained", paths.hermes_config_path.read_text(encoding="utf-8"))

    def test_offline_update_repairs_owned_plugin_and_existing_registration_but_not_opt_out(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self._base(root)
            self.assertEqual(run_cli(base + ["setup", "--no-interactive"])[0], 0)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            setup_profile_before = paths.setup_profile_path.read_bytes()
            imported = paths.skills_dir / "imported" / "foreign"
            imported.mkdir(parents=True)
            (imported / "SKILL.md").write_text(
                "---\nname: foreign\ndescription: fixture\n---\n\nindependent payload\n",
                encoding="utf-8",
            )
            config = root / ".hermes" / "config.yaml"
            manifest_before = paths.manifest_path.read_bytes()
            plugin = root / ".hermes" / "plugins" / "omj" / "plugin.yaml"
            plugin.unlink()
            config = root / ".hermes" / "config.yaml"
            config.write_text(config.read_text(encoding="utf-8").replace(str(root / ".omj" / "skills"), "/unregistered"), encoding="utf-8")
            with patch.dict(os.environ, {"OMJ_SKIP_SELF_UPDATE": "1"}, clear=False):
                status, stdout, stderr = run_cli(base + ["update"])
            self.assertEqual((status, stderr), (0, ""))
            payload = json.loads(stdout)
            self.assertTrue((root / ".hermes" / "plugins" / "omj" / "plugin.yaml").exists())
            self.assertIn("registration", json.dumps(payload))
            self.assertEqual(paths.setup_profile_path.read_bytes(), setup_profile_before)
            self.assertEqual(paths.manifest_path.read_bytes(), manifest_before)
            self.assertEqual((imported / "SKILL.md").read_text(encoding="utf-8"), "---\nname: foreign\ndescription: fixture\n---\n\nindependent payload\n")

    def test_update_without_plugin_preserves_preferences_imports_and_foreign_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self._base(root)
            self.assertEqual(
                run_cli(base + ["setup", "--no-interactive", "--default-executor", "codex", "--memory-mode", "auto-safe"])[0],
                0,
            )
            paths = resolve_paths(root / ".omj", root / ".hermes")
            imported = paths.skills_dir / "imported" / "foreign"
            imported.mkdir(parents=True)
            (imported / "SKILL.md").write_text(
                "---\nname: foreign\ndescription: fixture\n---\n\nindependent payload\n",
                encoding="utf-8",
            )
            hermes = root / ".hermes"
            config = hermes / "config.yaml"
            manifest = paths.manifest_path
            plugin = hermes / "plugins" / "omj" / "plugin.yaml"
            plugin.unlink()
            foreign = hermes / "plugins" / "foreign-plugin" / "plugin.yaml"
            foreign.parent.mkdir(parents=True)
            foreign.write_text("name: foreign-plugin\noperator_edit: retain\n", encoding="utf-8")
            before_config = config.read_bytes()
            before_manifest = manifest.read_bytes()
            before_foreign = foreign.read_bytes()
            with patch.dict(os.environ, {"OMJ_SKIP_SELF_UPDATE": "1"}, clear=False):
                status, _stdout, stderr = run_cli(base + ["update", "--without-plugin"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(config.read_bytes(), before_config)
            self.assertEqual(manifest.read_bytes(), before_manifest)
            self.assertEqual(foreign.read_bytes(), before_foreign)
            self.assertFalse(plugin.exists())
            names = {record["name"] for record in json.loads(manifest.read_text(encoding="utf-8"))["skills"]}
            self.assertNotIn("foreign", names)
            self.assertEqual((imported / "SKILL.md").read_text(encoding="utf-8"), "---\nname: foreign\ndescription: fixture\n---\n\nindependent payload\n")

    def test_update_refuses_modified_owned_plugin_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self._base(root)
            self.assertEqual(run_cli(base + ["setup", "--no-interactive"])[0], 0)
            plugin = root / ".hermes" / "plugins" / "omj" / "plugin.yaml"
            original = plugin.read_bytes()
            plugin.write_bytes(original + b"operator_edit: retain\n")
            modified = plugin.read_bytes()
            with patch.dict(os.environ, {"OMJ_SKIP_SELF_UPDATE": "1"}, clear=False):
                status, _stdout, _stderr = run_cli(base + ["update"])
            self.assertNotEqual(status, 0)
            self.assertEqual(plugin.read_bytes(), modified)

    def test_update_does_not_adopt_unmanaged_same_name_plugin_even_with_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self._base(root)
            plugin_dir = root / ".hermes" / "plugins" / "omj"
            plugin_dir.mkdir(parents=True)
            descriptor = plugin_dir / "plugin.yaml"
            descriptor.write_text("name: operator-owned-omj\noperator_edit: retain\n", encoding="utf-8")
            before_descriptor = descriptor.read_bytes()
            with patch.dict(os.environ, {"OMJ_SKIP_SELF_UPDATE": "1"}, clear=False):
                status, _stdout, stderr = run_cli(base + ["update", "--command-package-updated", "--force"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(descriptor.read_bytes(), before_descriptor)
            self.assertFalse((plugin_dir / ".omj-plugin-manifest.json").exists())
            config = root / ".hermes" / "config.yaml"
            self.assertFalse(config.exists())

    def test_update_force_does_not_adopt_foreign_plugin(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self._base(root)
            self.assertEqual(run_cli(base + ["setup", "--no-interactive"])[0], 0)
            foreign = root / ".hermes" / "plugins" / "foreign-plugin" / "plugin.yaml"
            foreign.parent.mkdir(parents=True)
            foreign.write_text("name: foreign-plugin\noperator_edit: retain\n", encoding="utf-8")
            before = foreign.read_bytes()
            with patch.dict(os.environ, {"OMJ_SKIP_SELF_UPDATE": "1"}, clear=False):
                status, _stdout, stderr = run_cli(base + ["update", "--force"])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(foreign.read_bytes(), before)

    def test_setup_propagates_profiles_with_env_override_optout_and_isolated_failure(self) -> None:
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self._base(root)
            profiles = root / ".hermes" / "profiles"
            for name in ("alpha", "beta", "broken"):
                (profiles / name).mkdir(parents=True)
            source = Path(__file__).resolve().parents[1] / "src" / "plugin_bundle" / "omj"
            shutil.copytree(source, profiles / "beta" / "plugins" / "omj")
            (profiles / "beta" / "config.yaml").write_text("plugins:\n  enabled: []\n", encoding="utf-8")
            (profiles / "alpha" / ".env").write_text(f"OMJ_HOME={root / '.profile-store'}\n", encoding="utf-8")
            (profiles / "broken" / "config.yaml").write_text("plugins: [broken\n", encoding="utf-8")
            status, stdout, stderr = run_cli(base + ["setup", "--no-interactive"])
            self.assertEqual((status, stderr), (0, ""))
            rows = {row["profile"]: row for row in json.loads(stdout)["hermes_profiles"]}
            self.assertEqual(rows["alpha"]["status"], "bootstrapped")
            self.assertEqual(rows["beta"]["status"], "unregistered_kept")
            self.assertEqual(rows["broken"]["status"], "failed")
            self.assertTrue((profiles / "alpha" / ".env").read_text(encoding="utf-8").startswith("OMJ_HOME="))
            self.assertNotIn("omj", (profiles / "beta" / "config.yaml").read_text(encoding="utf-8"))
    def test_doctor_profile_isolation_has_pairwise_exit_contract_and_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before = sorted(str(path) for path in root.rglob("*"))
            pair = ["doctor", "--profile-isolation", f"{root}/a-omj,{root}/a-hermes", f"{root}/b-omj,{root}/b-hermes"]
            status, stdout, stderr = run_cli(pair)
            self.assertEqual((status, stderr), (0, ""))
            payload = json.loads(stdout)
            self.assertEqual(payload["schema_version"], "profile_isolation/v1")
            self.assertNotIn("checks", payload)
            self.assertEqual(sorted(str(path) for path in root.rglob("*")), before)

            status, _stdout, stderr = run_cli(["doctor", "--profile-isolation", "", f"{root}/b-omj,{root}/b-hermes"])
            self.assertEqual(status, 2)
            self.assertIn("home", stderr.lower())
    def test_profile_isolation_cli_returns_contract_exit_codes_without_writes(self) -> None:
        cases = (
            ("isolated", ("a-omj", "a-hermes"), ("b-omj", "b-hermes"), 0),
            ("same", ("shared-omj", "shared-hermes"), ("shared-omj", "shared-hermes"), 1),
            ("nested", ("outer-omj", "outer-hermes"), ("outer-omj/inner", "outer-hermes/inner"), 1),
            ("unresolved", ("a-unresolved", None), ("b-unresolved", None), 3),
            ("malformed", ("", None), ("b-malformed", "b-malformed-hermes"), 2),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in (
                "a-omj",
                "a-hermes",
                "b-omj",
                "b-hermes",
                "shared-omj",
                "shared-hermes",
                "outer-omj/inner",
                "outer-hermes/inner",
                "a-unresolved",
                "b-unresolved",
                "b-malformed",
                "b-malformed-hermes",
            ):
                home = root / relative
                home.mkdir(parents=True, exist_ok=True)
                (home / "existing.bin").write_bytes(relative.encode("utf-8"))
            (root / "sentinel.txt").write_bytes(b"must remain byte-identical\n")

            def profile_ref(pair: tuple[str, str | None]) -> str:
                omj_home, hermes_home = pair
                if not omj_home:
                    return ""
                value = str(root / omj_home)
                return value if hermes_home is None else f"{value},{root / hermes_home}"

            for name, first_pair, second_pair, expected_status in cases:
                with self.subTest(case=name):
                    before = sorted(
                        (str(path.relative_to(root)), path.read_bytes() if path.is_file() else str(path.readlink()))
                        for path in root.rglob("*")
                        if path.is_file() or path.is_symlink()
                    )
                    status, stdout, stderr = run_cli(
                        ["doctor", "--profile-isolation", profile_ref(first_pair), profile_ref(second_pair)]
                    )
                    self.assertEqual(status, expected_status)
                    after = sorted(
                        (str(path.relative_to(root)), path.read_bytes() if path.is_file() else str(path.readlink()))
                        for path in root.rglob("*")
                        if path.is_file() or path.is_symlink()
                    )
                    self.assertEqual(after, before)
                    if expected_status == 2:
                        self.assertIn("profile isolation comparison failed", stderr)
                        self.assertEqual(stdout, "")
                    else:
                        summary = json.loads(stdout)["summary"]
                        if expected_status == 0:
                            self.assertGreater(summary["isolated"], 0)
                            self.assertEqual(summary["leaked"], 0)
                            self.assertEqual(summary["unknown"], 0)
                        elif expected_status == 1:
                            self.assertGreater(summary["leaked"], 0)
                        else:
                            self.assertGreater(summary["unknown"], 0)

    def test_doctor_advice_is_read_only_and_provider_warning_does_not_fail_health(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self._base(root)
            self.assertEqual(run_cli(base + ["setup", "--no-interactive"])[0], 0)
            state = root / ".omj" / "runtime" / "state.json"
            before = state.read_bytes()
            status, human_stdout, stderr = run_cli(base + ["doctor"], output_json=False)
            self.assertEqual((status, stderr), (0, ""))
            self.assertNotIn("State log:", human_stdout)
            self.assertNotIn("last_doctor", human_stdout)
            status, stdout, stderr = run_cli(base + ["doctor"])
            self.assertEqual((status, stderr), (0, ""))
            payload = json.loads(stdout)
            self.assertIn("advice", payload)
            self.assertEqual(payload["ok"], True)
            self.assertEqual(state.read_bytes(), before)
            self.assertTrue(any(item.get("severity") == "warning" for item in payload.get("advice", [])))

    def test_doctor_selected_home_permission_boundary_is_read_only_and_traceback_free(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = self._base(root)
            self.assertEqual(run_cli(base + ["setup", "--no-interactive"])[0], 0)
            omj_home = root / ".omj"
            files_before = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
            try:
                omj_home.chmod(0o500)
                status, stdout, stderr = run_cli(base + ["doctor"])
                self.assertIn(status, (0, 1))
                self.assertEqual(stderr, "")
                self.assertNotIn("Traceback", stdout)
                payload = json.loads(stdout)
                self.assertIn("checks", payload)
                self.assertIn("advice", payload)
                self.assertEqual({path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}, files_before)
            finally:
                omj_home.chmod(0o700)


if __name__ == "__main__":
    unittest.main()
