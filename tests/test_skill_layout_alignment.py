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
from omj import converter
from omj.converter import extract_name
from omj.config_adapter import ensure_external_dir
from omj.installer import install_skill_pack
from omj.manifest import new_manifest, skill_records, write_manifest
from omj.maintenance.doctor import run_doctor
from omj.paths import OmjPaths
from omj.skills.packaging import builtin_skill_templates
from omj.core.errors import OmjError


class SkillLayoutAlignmentTests(unittest.TestCase):
    def _paths(self, root: Path) -> OmjPaths:
        return OmjPaths(root / ".omj", root / ".hermes")

    def _skill(self, path: Path, name: str, *, body: str = "body\n") -> None:
        path.mkdir(parents=True, exist_ok=True)
        (path / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: fixture\n---\n\n{body}",
            encoding="utf-8",
        )

    def _tree_bytes(self, root: Path) -> dict[str, bytes]:
        return {
            str(path.relative_to(root)): path.read_bytes()
            for path in sorted(root.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts
        }

    def _managed_skill_dir(self, paths: OmjPaths, name: str) -> Path:
        manifest = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
        record = next(record for record in manifest["skills"] if record["name"] == name)
        return paths.skills_dir / Path(record["path"]).parent
    def test_mixed_repo_root_discovery_deduplicates_projections_and_preserves_explicit_roots(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            self._skill(root / "skills" / "native", "native", body="native source\n")
            self._skill(root / "agent-skills" / "native", "native", body="portable projection\n")
            self._skill(root / ".agents" / "skills" / "native", "native", body="another projection\n")
            self._skill(root / ".claude" / "skills" / "custom", "custom", body="shared custom\n")
            nested = root / "vendor-checkout"
            nested.mkdir(parents=True)
            (nested / ".git").write_text("gitdir: ../.git/worktrees/vendor\n", encoding="utf-8")
            self._skill(nested / "skills" / "nested", "nested", body="nested checkout\n")

            paths = self._paths(Path(tmp) / "home")
            result = install_skill_pack(paths, source_dir=root, source=str(root))

            names = {record["name"] for record in result["skills"]}
            self.assertEqual(names, {"native", "custom"})
            installed_native = (paths.skills_dir / "native" / "SKILL.md").read_text()
            self.assertIn("native source", installed_native)
            self.assertNotIn("portable projection", installed_native)
            self.assertFalse((paths.skills_dir / "nested").exists())

    def test_destination_category_symlink_is_rejected_before_any_write(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root / "home")
            paths.skills_dir.mkdir(parents=True)
            foreign = root / "foreign"
            foreign.mkdir()
            category = paths.skills_dir / "goal-loop"
            category.symlink_to(foreign, target_is_directory=True)
            before = self._tree_bytes(root)

            with self.assertRaises(OmjError):
                install_skill_pack(paths)

            self.assertEqual(before, self._tree_bytes(root))
            self.assertTrue(category.is_symlink())
            self.assertFalse(paths.manifest_path.exists())
    def test_destination_category_file_collision_is_rejected_before_any_write(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root / "home")
            paths.skills_dir.mkdir(parents=True)
            category = paths.skills_dir / "goal-loop"
            category.write_bytes(b"not a category directory\n")
            before = self._tree_bytes(root)

            for force in (False, True):
                with self.subTest(force=force):
                    with self.assertRaises(OmjError):
                        install_skill_pack(paths, force=force)
                    self.assertEqual(before, self._tree_bytes(root))
                    self.assertFalse(paths.manifest_path.exists())


    def test_source_mutation_after_discovery_cannot_admit_duplicate_identity(self) -> None:
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            first = source / "first"
            second = source / "second"
            self._skill(first, "first", body="first payload\n")
            self._skill(second, "second", body="second payload\n")
            paths = self._paths(Path(tmp) / "home")
            before = self._tree_bytes(paths.omj_home) if paths.omj_home.exists() else {}
            original_second = (second / "SKILL.md").read_bytes()
            original_discover = converter.discover_skill_files
            calls = 0

            def discover_then_mutate(root: Path) -> list[Path]:
                nonlocal calls
                selected = original_discover(root)
                if calls == 0:
                    (second / "SKILL.md").write_text(
                        (second / "SKILL.md").read_text(encoding="utf-8").replace("name: second", "name: first"),
                        encoding="utf-8",
                    )
                calls += 1
                return selected

            with patch("omj.converter.discover_skill_files", side_effect=discover_then_mutate):
                try:
                    result = install_skill_pack(paths, source_dir=source, source=str(source))
                except (OmjError, ValueError):
                    self.assertEqual(before, self._tree_bytes(paths.omj_home) if paths.omj_home.exists() else {})
                else:
                    names = [record["name"] for record in result["skills"]]
                    self.assertEqual(names, ["first", "second"])
                    target = self._managed_skill_dir(paths, "second") / "SKILL.md"
                    self.assertEqual(target.read_bytes(), original_second)
    def test_known_source_labels_round_trip_without_renaming_custom_skills(self) -> None:
        self.assertEqual(extract_name("---\nname: ulw-work\n---\n", "fallback"), "ultrawork")
        self.assertEqual(extract_name("---\nname: ulw-interview\n---\n", "fallback"), "deep-interview")
        self.assertEqual(extract_name("---\nname: custom-workflow\n---\n", "fallback"), "custom-workflow")

        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            self._skill(source / "one", "../escape")
            self._skill(source / "two", "safe")
            paths = self._paths(Path(tmp) / "home")
            before = self._tree_bytes(Path(tmp) / "home") if (Path(tmp) / "home").exists() else {}
            with self.assertRaises((OmjError, ValueError)):
                install_skill_pack(paths, source_dir=source, source=str(source))
            self.assertEqual(before, self._tree_bytes(Path(tmp) / "home") if (Path(tmp) / "home").exists() else {})
    def test_source_symlink_is_rejected_before_destination_writes(self) -> None:
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            self._skill(source / "real", "real")
            linked = source / "linked"
            linked.mkdir(parents=True)
            (linked / "SKILL.md").symlink_to(source / "real" / "SKILL.md")
            home = Path(tmp) / "home"
            paths = self._paths(home)
            with self.assertRaises((OmjError, ValueError)):
                install_skill_pack(paths, source_dir=source, source=str(source))
            self.assertFalse(home.exists())

    def test_local_source_import_carries_nested_references_and_preserves_edits(self) -> None:
        with TemporaryDirectory() as tmp:
            source = Path(tmp) / "source"
            skill_dir = source / "example"
            self._skill(skill_dir, "example", body="Read references/methods/deep.md before proceeding.\n")
            (skill_dir / "references" / "methods").mkdir(parents=True)
            reference = skill_dir / "references" / "methods" / "deep.md"
            reference.write_bytes(b"exact imported reference bytes\n")
            paths = self._paths(Path(tmp) / "home")

            install_skill_pack(paths, source_dir=source, source=str(source))
            target = self._managed_skill_dir(paths, "example") / "references" / "methods" / "deep.md"
            self.assertTrue(target.is_file(), target)
            self.assertEqual(target.read_bytes(), reference.read_bytes())

            target.write_bytes(b"operator edit\n")
            before = self._tree_bytes(paths.omj_home)
            with self.assertRaises((OmjError, ValueError)):
                install_skill_pack(paths, source_dir=source, source=str(source))
            self.assertEqual(target.read_bytes(), b"operator edit\n")
            self.assertEqual(before, self._tree_bytes(paths.omj_home))

    def test_every_prepared_contract_advertises_a_resolvable_local_method_path(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            install_skill_pack(paths)
            prepared_root = self._managed_skill_dir(paths, "oh-my-jeo") / "references" / "prepared"
            contracts = [path for path in prepared_root.rglob("*.md") if path.parent != prepared_root]
            self.assertTrue(contracts)
            for contract in contracts:
                text = contract.read_text(encoding="utf-8")
                if "## Method references\n" not in text or "## Method references\n- No source-specific" in text:
                    continue
                section = text.split("## Method references\n", 1)[1].split("\n## Source gaps", 1)[0]
                for line in section.splitlines():
                    if not line.startswith("- `"):
                        continue
                    pointer = line.split("`", 2)[1]
                    self.assertTrue((contract.parent / pointer).is_file(), f"{contract}: {pointer}")

    def test_reference_edits_and_unowned_new_targets_block_update_before_any_write(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            install_skill_pack(paths)
            owner_dir = self._managed_skill_dir(paths, "oh-my-jeo")
            reference = next(owner_dir.rglob("references/prepared/**/*.md"))
            reference.write_text("edited method\n", encoding="utf-8")
            unowned = owner_dir / "references" / "operator-note.md"
            unowned.write_text("do not adopt\n", encoding="utf-8")
            external = Path(tmp) / "outside.md"
            external.write_bytes(b"outside\n")
            link = owner_dir / "references" / "operator-link.md"
            link.symlink_to(external)
            before = self._tree_bytes(paths.omj_home)
            manifest_before = paths.manifest_path.read_bytes()

            with self.assertRaises((OmjError, ValueError)):
                install_skill_pack(paths)

            self.assertEqual(before, self._tree_bytes(paths.omj_home))
            self.assertEqual(manifest_before, paths.manifest_path.read_bytes())
            self.assertEqual(unowned.read_text(encoding="utf-8"), "do not adopt\n")
            self.assertTrue(link.is_symlink())
            self.assertEqual(external.read_bytes(), b"outside\n")

    def test_update_never_adopts_independently_imported_or_custom_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            install_skill_pack(paths)
            imported = paths.skills_dir / "imported" / "foreign"
            self._skill(imported, "foreign", body="independent payload\n")
            custom = paths.skills_dir / "custom"
            self._skill(custom, "custom", body="custom payload\n")
            install_skill_pack(paths)
            manifest = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
            names = {record["name"] for record in manifest["skills"]}
            self.assertNotIn("foreign", names)
            self.assertNotIn("custom", names)
            self.assertEqual((imported / "SKILL.md").read_text(encoding="utf-8"), "---\nname: foreign\ndescription: fixture\n---\n\nindependent payload\n")

    def test_categorized_managed_migration_preserves_names_references_and_user_payloads(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            template = next(item for item in builtin_skill_templates() if item.name == "ralph")
            flat = paths.skills_dir / "ralph" / "SKILL.md"
            flat.parent.mkdir(parents=True)
            flat.write_text(template.content, encoding="utf-8")
            write_manifest(paths.manifest_path, new_manifest("builtin", paths.skills_dir, skill_records(paths.skills_dir, "builtin")))
            extra = flat.parent / "operator-extra.md"
            extra.write_text("retain me\n", encoding="utf-8")

            install_skill_pack(paths)
            manifest = json.loads(paths.manifest_path.read_text(encoding="utf-8"))
            self.assertTrue(all(len(Path(record["path"]).parts) == 3 for record in manifest["skills"]))
            self.assertFalse(flat.exists())
            self.assertEqual(extra.read_text(encoding="utf-8"), "retain me\n")

    def test_realpath_registration_migration_only_retires_verified_managed_candidates(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            managed = root / "managed"
            managed.mkdir()
            alias = root / "alias"
            alias.symlink_to(managed, target_is_directory=True)
            config = f"skills:\n  external_dirs:\n    - {alias}\n"
            change = ensure_external_dir(config, managed)
            self.assertFalse(change.changed)
            self.assertEqual(change.text, config)
            unrelated = root / "unrelated"
            unrelated.mkdir()
            keep = ensure_external_dir(change.text, unrelated)
            self.assertTrue(keep.changed)
            self.assertIn(str(unrelated), keep.text)
            self.assertIn(str(alias), keep.text)

    def test_installed_package_materializes_native_resources_without_checkout(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            old_cwd = Path.cwd()
            try:
                os.chdir(tmp)
                result = install_skill_pack(paths)
            finally:
                os.chdir(old_cwd)
            self.assertEqual(len(result["skills"]), len(builtin_skill_templates()))
            self.assertTrue(any(path.is_file() for path in paths.skills_dir.rglob("references/**/*.md")))

    def test_doctor_and_update_compare_observed_owned_content_not_only_release_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with patch("omj.maintenance.doctor._append_model_checks"):
                checks = run_doctor(paths)
            names = {check.name for check in checks}
            self.assertIn("content_freshness", names)

            source = Path(tmp) / "source"
            self._skill(source / "sample", "sample", body="v1\n")
            args = ["--omj-home", str(paths.omj_home), "--hermes-home", str(paths.hermes_home), "install", "--channel", "local", "--source", str(source), "--source-ref", "same-release"]
            status, stdout, stderr = run_cli(args)
            self.assertEqual(status, 0, stderr)
            self._skill(source / "sample", "sample", body="v2\n")
            status, stdout, stderr = run_cli(args)
            self.assertEqual(status, 0, stderr)
            payload = json.loads(stdout)
            self.assertIn("release_update", payload)
            self.assertTrue(payload.get("release_update", {}).get("content_changed"), payload)


if __name__ == "__main__":
    unittest.main()
