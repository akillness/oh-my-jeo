from __future__ import annotations

import json
import unittest

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()
from omj.quality.skill_manifest_coverage import (
    _evaluate_template,
    build_skill_manifest_coverage_demo,
    format_skill_manifest_coverage_summary,
)

VALID_SKILL = (
    "---\n"
    "name: sample\n"
    "description: [omj] A sample skill description.\n"
    "metadata:\n"
    "  hermes:\n"
    "    tags: [workflow, oh-my-jeo, review]\n"
    "    category: review\n"
    "    phase: critique\n"
    "    role: reviewer\n"
    "    quality_tier: evidence-gated\n"
    "---\n"
    "\n# Sample\n\n## Why This Exists\n\nBecause.\n"
)


class SkillManifestCoverageTests(unittest.TestCase):
    def test_demo_validates_every_shipped_skill_manifest(self) -> None:
        payload = build_skill_manifest_coverage_demo()

        self.assertEqual(payload["schema_version"], "skill_manifest_coverage/v1")
        self.assertTrue(payload["summary"]["all_passing"])
        self.assertEqual(payload["summary"]["skill_count"], 43)
        self.assertEqual(payload["summary"]["passing_count"], 43)
        self.assertEqual(payload["summary"]["secret_finding_count"], 0)
        self.assertTrue(payload["summary"]["secret_control_detected"])
        self.assertIn("does not prove Hermes", payload["claim_boundary"])

        for row in payload["skills"]:
            self.assertTrue(row["passed"], (row["name"], row["issues"]))
            observed = row["observed"]
            self.assertTrue(observed["has_frontmatter_open"])
            self.assertTrue(observed["has_frontmatter_close"])
            self.assertEqual(observed["name"], row["name"])
            self.assertTrue(observed["description"].startswith("[omj]"))
            self.assertIn("oh-my-jeo", observed["tags"])
            self.assertTrue(observed["quality_tier"])
            self.assertGreaterEqual(observed["section_count"], 1)
            self.assertFalse(observed["secret_detected"])

    def test_secret_detection_control_fires_on_synthetic_credential(self) -> None:
        control = build_skill_manifest_coverage_demo()["secret_detection_control"]
        self.assertTrue(control["detected"])
        self.assertEqual(control["matched_keyword"], "api_key")

    def test_evaluate_template_flags_hardcoded_secret(self) -> None:
        leaked = VALID_SKILL + "\nGITHUB_TOKEN = ghp_abcdefghijklmnopqrstuvwxyz0123456789\n"
        row = _evaluate_template("sample", leaked)
        self.assertFalse(row["passed"])
        self.assertTrue(row["observed"]["secret_detected"])
        self.assertTrue(any("hardcoded secret" in issue for issue in row["issues"]))

    def test_evaluate_template_flags_missing_frontmatter_fields(self) -> None:
        broken = (
            "---\n"
            "name: sample\n"
            "description: A description without provenance.\n"
            "metadata:\n"
            "  hermes:\n"
            "    tags: [workflow, oh-my-jeo, planning]\n"
            "---\n\n# body\n\n## Section\n\nx\n"
        )
        row = _evaluate_template("sample", broken)
        self.assertFalse(row["passed"])
        issues = row["issues"]
        for field in ("category", "phase", "role", "quality_tier"):
            self.assertTrue(any(f"'{field}'" in issue for issue in issues), field)
        self.assertTrue(any("[omj] provenance" in issue for issue in issues))

    def test_evaluate_template_flags_name_and_category_mismatch(self) -> None:
        mismatched = VALID_SKILL.replace("category: review", "category: planning")
        row = _evaluate_template("not-sample", mismatched)
        self.assertFalse(row["passed"])
        self.assertTrue(any("does not match template" in issue for issue in row["issues"]))
        self.assertTrue(any("does not match category" in issue for issue in row["issues"]))

    def test_evaluate_template_accepts_valid_manifest(self) -> None:
        row = _evaluate_template("sample", VALID_SKILL)
        self.assertTrue(row["passed"], row["issues"])
        self.assertEqual(row["observed"]["category"], "review")

    def test_summary_reports_passing_rollup(self) -> None:
        summary = format_skill_manifest_coverage_summary(build_skill_manifest_coverage_demo())
        self.assertIn("OMJ skill manifest coverage", summary)
        self.assertIn("43/43 skill manifests passing", summary)
        self.assertIn("secret scanner control: fires", summary)

    def test_cli_outputs_summary_and_json(self) -> None:
        status, stdout, stderr = run_cli(["demo", "skill-manifest-coverage", "--summary"], output_json=False)
        self.assertEqual(status, 0, stderr)
        self.assertEqual(stderr, "")
        self.assertIn("OMJ skill manifest coverage", stdout)
        self.assertIn("43/43 skill manifests passing", stdout)

        status, stdout, stderr = run_cli(["demo", "skill-manifest-coverage"], output_json=False)
        self.assertEqual(status, 0, stderr)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertEqual(payload["schema_version"], "skill_manifest_coverage/v1")
        self.assertTrue(payload["summary"]["all_passing"])


if __name__ == "__main__":
    unittest.main()
