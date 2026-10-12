from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()

from omj.paths import OmjPaths
from omj.maintenance.doctor import run_doctor
from omj.install.installer import skill_profile_report
from omj.skills.packaging import builtin_skill_templates
from omj.skills.catalog import CORE_PROFILE_SKILLS


class SkillProfileAlignmentTests(unittest.TestCase):
    def _paths(self, root: Path) -> OmjPaths:
        return OmjPaths(root / ".omj", root / ".hermes")

    def _run(self, args: list[str]) -> tuple[int, dict[str, object], str]:
        status, stdout, stderr = run_cli(args)
        payload = json.loads(stdout) if stdout.strip() else {}
        return status, payload, stderr
    def _tree_bytes(self, root: Path) -> dict[str, bytes]:
        return {
            str(path.relative_to(root)): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts
        }

    def _run_raw(self, args: list[str]) -> tuple[int, str, str]:
        return run_cli(args, output_json=False)

    def test_profiles_are_hermes_only_and_refuse_portable_targets_before_writes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            portable = root / ".claude" / "skills" / "portable"
            portable.mkdir(parents=True)
            (portable / "SKILL.md").write_text("operator portable content\n", encoding="utf-8")
            before = self._tree_bytes(root)
            base = ["--omj-home", str(paths.omj_home), "--hermes-home", str(paths.hermes_home)]
            old_cwd = Path.cwd()
            try:
                os.chdir(root)
                for profile in ("core", "full"):
                    status, _, stderr = self._run(
                        [*base, "install", "--target", "agents", "--host", "claude", "--scope", "project", f"--{profile}"]
                    )
                    self.assertNotEqual(status, 0, stderr)
                    self.assertEqual(before, self._tree_bytes(root))
            finally:
                os.chdir(old_cwd)

    def test_profile_status_and_reconcile_have_distinct_human_and_json_outputs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            base = ["--omj-home", str(paths.omj_home), "--hermes-home", str(paths.hermes_home)]
            status, _, stderr = self._run([*base, "install", "--full"])
            self.assertEqual(status, 0, stderr)

            status, human_status, stderr = self._run_raw([*base, "skill-profile", "status"])
            self.assertEqual(status, 0, stderr)
            self.assertIn("OMJ skill profile", human_status)
            self.assertIn("Requested:", human_status)
            self.assertIn("Effective:", human_status)
            self.assertIn("Installed skills:", human_status)
            status, stdout_json, stderr = run_cli([*base, "skill-profile", "status", "--json"], output_json=True)
            self.assertEqual(status, 0, stderr)
            status_payload = json.loads(stdout_json)
            self.assertIn("profile_state", status_payload)
            self.assertIn("installed_skill_count", status_payload["profile_state"])

            status, human_reconcile, stderr = self._run_raw(
                [*base, "skill-profile", "reconcile", "--to", "core", "--dry-run"]
            )
            self.assertEqual(status, 0, stderr)
            self.assertIn("OMJ skill profile reconciliation", human_reconcile)
            self.assertIn("Mode: preview", human_reconcile)
            self.assertIn("Target:", human_reconcile)
            self.assertIn("Would remove", human_reconcile)
            self.assertIn("Retained", human_reconcile)
            status, stdout_json, stderr = run_cli(
                [*base, "skill-profile", "reconcile", "--to", "core", "--dry-run", "--json"],
                output_json=True,
            )
            self.assertEqual(status, 0, stderr)
            reconcile_payload = json.loads(stdout_json)
            self.assertEqual(reconcile_payload["target_profile"], "core")
            self.assertTrue(reconcile_payload["dry_run"])

    def test_default_full_explicit_core_and_update_inheritance_preserve_existing_installs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            base = ["--omj-home", str(paths.omj_home), "--hermes-home", str(paths.hermes_home)]

            status, first, stderr = self._run([*base, "install"])
            self.assertEqual(status, 0, stderr)
            self.assertIn("skill_profile", first)
            self.assertEqual(first["skill_profile"], "full")
            full_paths = {record["path"] for record in first["skills"]}
            self.assertGreater(len(full_paths), 1)

            status, core, stderr = self._run([*base, "install", "--core"])
            self.assertEqual(status, 0, stderr)
            self.assertEqual(core["skill_profile"], "core")
            self.assertTrue(full_paths.issubset({record["path"] for record in core["skills"]}))

            status, update, stderr = self._run([*base, "update"])
            self.assertEqual(status, 0, stderr)
            self.assertEqual(update["skill_profile"], "core")
            self.assertTrue(full_paths.issubset({record["path"] for record in update["skills"]}))

            manifest = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["skill_profile_state"]["requested_profile"], "core")

    def test_reconcile_preview_and_apply_preserve_all_unowned_or_modified_payloads(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            base = ["--omj-home", str(paths.omj_home), "--hermes-home", str(paths.hermes_home)]
            status, installed, stderr = self._run([*base, "install", "--full"])
            self.assertEqual(status, 0, stderr)
            records = list(installed["skills"])
            self.assertGreater(len(records), 1)

            modified_record = records[-1]
            modified_path = paths.skills_dir / modified_record["path"]
            modified_original = modified_path.read_bytes()
            modified_path.write_bytes(modified_original + b"\noperator edit\n")
            extra_path = modified_path.parent / "operator-extra.md"
            extra_path.write_text("retain this\n", encoding="utf-8")
            before_manifest = paths.manifest_path.read_bytes()

            status, preview, stderr = self._run([*base, "skill-profile", "reconcile", "--to", "core", "--dry-run"])
            self.assertEqual(status, 0, stderr)
            self.assertEqual(preview["target_profile"], "core")
            self.assertTrue(preview["dry_run"])
            self.assertTrue(preview["would_remove_skills"])
            self.assertIn(str(modified_record["path"]), preview["retained_skills"])
            self.assertEqual(before_manifest, paths.manifest_path.read_bytes())
            self.assertEqual(extra_path.read_text(encoding="utf-8"), "retain this\n")

            status, applied, stderr = self._run([*base, "skill-profile", "reconcile", "--to", "core", "--apply"])
            self.assertEqual(status, 0, stderr)
            self.assertEqual(applied["target_profile"], "core")
            self.assertFalse(applied["dry_run"])
            self.assertTrue(applied["removed_skills"])
            self.assertTrue(modified_path.exists())
            self.assertEqual(modified_path.read_bytes(), modified_original + b"\noperator edit\n")
            self.assertEqual(extra_path.read_text(encoding="utf-8"), "retain this\n")
            self.assertIn("effective_profile", applied["profile_state_after"])
            self.assertTrue(paths.manifest_path.exists())

    def test_reconcile_preserves_original_ownership_and_update_boundaries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            base = ["--omj-home", str(paths.omj_home), "--hermes-home", str(paths.hermes_home)]

            status, _, stderr = self._run([*base, "install", "--full"])
            self.assertEqual(status, 0, stderr)
            before = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
            before["operator_marker"] = {"keep": True}
            paths.manifest_path.write_text(json.dumps(before), encoding="utf-8")
            before_records = {record["name"]: record for record in before["skills"]}
            retained_full_only = before_records["loop"]
            retained_core = before_records["oh-my-jeo"]
            self.assertTrue(retained_full_only.get("files"))
            self.assertTrue(retained_core.get("files"))
            edited_path = paths.skills_dir / retained_full_only["path"]
            original_bytes = edited_path.read_bytes()
            edited_path.write_bytes(original_bytes + b"\noperator edit\n")

            status, applied, stderr = self._run([*base, "skill-profile", "reconcile", "--to", "core", "--apply"])
            self.assertEqual(status, 0, stderr)
            self.assertIn(retained_full_only["path"], applied["retained_skills"])

            after = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
            after_records = {record["name"]: record for record in after["skills"]}
            self.assertEqual(after_records["loop"], retained_full_only)
            self.assertEqual(after_records["oh-my-jeo"], retained_core)
            self.assertEqual(after["source"], before["source"])
            self.assertEqual(after["installed_at"], before["installed_at"])
            self.assertEqual(after["operator_marker"], {"keep": True})
            for record in (retained_full_only, retained_core):
                for item in record.get("files", []):
                    self.assertEqual(after["owned_files"][item["path"]], item["sha256"])

            status, _, stderr = self._run([*base, "update"])
            self.assertNotEqual(status, 0)
            self.assertIn(retained_full_only["path"], stderr)
            self.assertIn("modified owned file", stderr)
            edited_path.write_bytes(original_bytes)
            status, _, stderr = self._run([*base, "update"])
            self.assertEqual(status, 0, stderr)

    def test_profile_status_retains_unreadable_optional_member_without_escaping(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            base = ["--omj-home", str(paths.omj_home), "--hermes-home", str(paths.hermes_home)]
            status, _, stderr = self._run([*base, "install", "--full"])
            self.assertEqual(status, 0, stderr)
            manifest = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
            loop_record = next(record for record in manifest["skills"] if record["name"] == "loop")
            unreadable = paths.skills_dir / loop_record["path"]
            original_read_bytes = Path.read_bytes

            def read_bytes(path: Path) -> bytes:
                if path == unreadable:
                    raise OSError("fixture unreadable")
                return original_read_bytes(path)

            with patch.object(Path, "read_bytes", autospec=True, side_effect=read_bytes):
                payload = skill_profile_report(paths)
            self.assertIn("loop", payload["retained_skills"])
            self.assertNotIn("loop", payload["reconcilable_skills"])


    def test_core_reconcile_removes_unchanged_reference_bearing_full_only_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            base = ["--omj-home", str(paths.omj_home), "--hermes-home", str(paths.hermes_home)]
            status, _, stderr = self._run([*base, "install", "--full"])
            self.assertEqual(status, 0, stderr)
            before_manifest = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
            removed_records = {
                name: next(record for record in before_manifest["skills"] if record["name"] == name)
                for name in ("loop", "ultraqa", "ultrawork")
            }
            removed_prefixes = [str(Path(record["path"]).parent).replace("\\", "/") + "/" for record in removed_records.values()]
            before_tree = self._tree_bytes(paths.omj_home)

            status, preview, stderr = self._run([*base, "skill-profile", "reconcile", "--to", "core", "--dry-run"])
            self.assertEqual(status, 0, stderr)
            self.assertEqual(before_tree, self._tree_bytes(paths.omj_home))
            for name in ("loop", "ultraqa", "ultrawork"):
                self.assertIn(name, preview["would_remove_skills"])
                self.assertNotIn(name, {item["name"] for item in preview["retained"]})

            status, applied, stderr = self._run([*base, "skill-profile", "reconcile", "--to", "core", "--apply"])
            self.assertEqual(status, 0, stderr)
            self.assertTrue({"loop", "ultraqa", "ultrawork"}.issubset(set(applied["removed_skills"])))
            self.assertEqual(applied["profile_state_after"]["effective_profile"], "core")
            self.assertEqual(applied["profile_state_after"]["full_only_installed_skills"], [])
            manifest = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
            installed_names = {record["name"] for record in manifest["skills"]}
            self.assertEqual(installed_names, set(CORE_PROFILE_SKILLS))
            for record in removed_records.values():
                self.assertFalse((paths.skills_dir / Path(record["path"]).parent).exists())
            for relative in manifest.get("owned_files", {}):
                self.assertFalse(any(relative.startswith(prefix) for prefix in removed_prefixes))
    def test_profile_status_reports_requested_and_physical_effective_membership(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            base = ["--omj-home", str(paths.omj_home), "--hermes-home", str(paths.hermes_home)]
            status, _, stderr = self._run([*base, "install", "--core"])
            self.assertEqual(status, 0, stderr)
            status, status_payload, stderr = self._run([*base, "skill-profile", "status"])
            self.assertEqual(status, 0, stderr)
            profile_state = status_payload["profile_state"]
            self.assertEqual(profile_state["requested_profile"], "core")
            self.assertIn(profile_state["effective_profile"], {"core", "mixed", "full"})
            self.assertEqual(profile_state["installed_skill_count"], len(status_payload["reconcilable_skills"]) + len(status_payload["retained_skills"]))


    def test_core_install_uses_authored_subset_and_doctor_has_no_failing_skill_checks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            base = ["--omj-home", str(paths.omj_home), "--hermes-home", str(paths.hermes_home)]

            status, payload, stderr = self._run([*base, "install", "--core"])
            self.assertEqual(status, 0, stderr)
            records = payload["skills"]
            self.assertEqual(len(records), 11)
            self.assertLess(len(records), len(builtin_skill_templates()))

            skill_checks = [check for check in run_doctor(paths) if check.name.startswith("skill:")]
            self.assertTrue(skill_checks)
            failing = [f"{check.name}: {check.message}" for check in skill_checks if not check.ok]
            self.assertEqual(failing, [])

if __name__ == "__main__":
    unittest.main()
