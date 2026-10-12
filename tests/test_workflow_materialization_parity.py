from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from _cli_harness import run_cli
from omj.skill_pack import builtin_skill_reference_templates, builtin_skill_templates
from omj.skills.render import workflow_reference_markdown


class WorkflowMaterializationParityTests(unittest.TestCase):
    @staticmethod
    def _materialize_builtin_tree(root: Path) -> tuple[Path, Path, object]:
        skills_root = root / "skills"
        skill_templates = tuple(builtin_skill_templates())
        reference_templates = tuple(builtin_skill_reference_templates())
        for template in skill_templates:
            target = skills_root / template.name / "SKILL.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(template.content, encoding="utf-8")
        for template in reference_templates:
            target = skills_root / template.skill_name / template.relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(template.content, encoding="utf-8")

        workflow_docs = root / "docs" / "WORKFLOWS.md"
        workflow_docs.parent.mkdir(parents=True, exist_ok=True)
        workflow_docs.write_text(workflow_reference_markdown(), encoding="utf-8")
        deepest_reference = max(reference_templates, key=lambda template: template.relative_path.count("/"))
        return skills_root, workflow_docs, deepest_reference

    @staticmethod
    def _run_check(root: Path, workflow_docs: Path) -> tuple[int, str, str]:
        previous_cwd = Path.cwd()
        os.chdir(root)
        try:
            return run_cli(
                ["docs", "workflows", "--check", "--output", str(workflow_docs)],
                output_json=False,
            )
        finally:
            os.chdir(previous_cwd)

    def test_materialized_builtin_tree_passes_and_counts_top_level_and_deep_references(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills_root, workflow_docs, deepest_reference = self._materialize_builtin_tree(root)

            status, stdout, stderr = self._run_check(root, workflow_docs)

            self.assertEqual(status, 0, stderr)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"])
            tap_skills = payload["tap_skills"]
            expected = len(builtin_skill_templates()) + len(builtin_skill_reference_templates())
            self.assertEqual(tap_skills["root"], str(skills_root.resolve()))
            self.assertEqual(tap_skills["expected"], expected)
            self.assertEqual(tap_skills["checked"], expected)
            self.assertEqual(tap_skills["missing"], [])
            self.assertEqual(tap_skills["stale"], [])
            self.assertEqual(tap_skills["extra"], [])
            self.assertEqual(deepest_reference.relative_path.count("/"), 6)
            self.assertTrue((skills_root / "oh-my-jeo" / deepest_reference.relative_path).is_file())

    def test_materialized_tree_rejects_missing_modified_and_extra_named_paths(self) -> None:
        reference_templates = tuple(builtin_skill_reference_templates())
        top_level = next(template for template in reference_templates if template.relative_path == "references/workflow-registry.md")
        deepest = max(reference_templates, key=lambda template: template.relative_path.count("/"))
        cases = (
            ("missing top-level reference", top_level, "missing", None),
            ("modified top-level reference", top_level, "modified", None),
            ("missing deeply nested method reference", deepest, "missing", None),
            ("modified deeply nested method reference", deepest, "modified", None),
            ("unexpected deeply nested reference", deepest, "extra", "unexpected-extra.md"),
        )

        for case_name, template, mutation, extra_name in cases:
            with self.subTest(case_name=case_name):
                with TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    skills_root, workflow_docs, _ = self._materialize_builtin_tree(root)
                    target = skills_root / template.skill_name / template.relative_path
                    expected_path = str(target.relative_to(skills_root))
                    if mutation == "missing":
                        target.unlink()
                    elif mutation == "modified":
                        target.write_text(template.content + "\nmodified\n", encoding="utf-8")
                    else:
                        extra_path = target.parent / str(extra_name)
                        extra_path.write_text("unexpected nested reference\n", encoding="utf-8")
                        expected_path = str(extra_path.relative_to(skills_root))

                    status, stdout, stderr = self._run_check(root, workflow_docs)

                    self.assertNotEqual(status, 0)
                    self.assertEqual(stdout, "")
                    self.assertIn(expected_path, stderr)


if __name__ == "__main__":
    unittest.main()
