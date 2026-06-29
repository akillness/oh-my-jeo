from __future__ import annotations

import json
import unittest

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()
from omj.quality.context_brief_coverage import build_context_brief_coverage_demo


class ContextBriefCoverageTests(unittest.TestCase):
    def test_context_brief_coverage_demo_checks_hermes_facing_context(self) -> None:
        payload = build_context_brief_coverage_demo(source="discord")

        self.assertEqual(payload["schema_version"], "context_brief_coverage/v1")
        self.assertEqual(payload["source"], "discord")
        self.assertTrue(payload["summary"]["all_passing"])
        self.assertEqual(payload["summary"]["case_count"], 8)
        self.assertEqual(payload["summary"]["passing_count"], 8)
        self.assertEqual(payload["summary"]["route_hint_count"], 7)
        self.assertEqual(payload["summary"]["catalog_question_count"], 1)
        self.assertIn("metadata-only", payload["check_basis"][0])
        self.assertIn("does not prove live Hermes chat rendering", payload["claim_boundary"])

        cases = {case["id"]: case for case in payload["cases"]}
        visual = cases["visual-summary-before-image-tool"]
        self.assertEqual(visual["observed"]["primary_workflow"], "img-summary")
        self.assertEqual(visual["observed"]["primary_next_action"], "prepare_visual_prompt_card")
        self.assertFalse(visual["observed"]["sensitive_token_leaked"])
        self.assertTrue(visual["observed"]["prompt_context_has_route_hint"])
        self.assertEqual(visual["observed"]["raw_prompt_stored"], False)
        self.assertEqual(visual["observed"]["raw_prompt_echoed"], False)

        catalog = cases["catalog-picker-without-shell-approval"]
        self.assertTrue(catalog["observed"]["catalog_question"])
        self.assertEqual(catalog["observed"]["catalog_next_action"], "show_workflow_picker")
        self.assertEqual(catalog["observed"]["catalog_recommended_tool"], "omj_capabilities")
        self.assertEqual(catalog["observed"]["route_hint_status"], "no_hint")

    def test_context_brief_coverage_covers_every_recognized_route_hint_workflow(self) -> None:
        payload = build_context_brief_coverage_demo(source="discord")
        cases = {case["id"]: case for case in payload["cases"]}
        expected = {
            "missed-route-learning": ("workflow-learning", "record_missed_route"),
            "scheduled-automation-blueprint": ("automation-blueprint", "prepare_scheduled_ops_blueprint"),
            "feedback-triage-before-coding": ("feedback-triage", "classify_signal_and_prepare_investigation"),
            "paper-learning": ("paper-learning", "prepare_paper_learning"),
            "web-research": ("web-research", "gather_source_backed_evidence"),
            "one-cycle-delivery": ("ultraprocess", "prepare_one_cycle_delivery"),
        }
        for case_id, (workflow, next_action) in expected.items():
            observed = cases[case_id]["observed"]
            self.assertTrue(cases[case_id]["passed"], cases[case_id]["issues"])
            self.assertEqual(observed["route_hint_status"], "hinted")
            self.assertEqual(observed["primary_workflow"], workflow)
            self.assertEqual(observed["primary_next_action"], next_action)
            self.assertTrue(observed["workflow_context_card"])

    def test_context_brief_coverage_rejects_unsupported_source(self) -> None:
        with self.assertRaises(ValueError):
            build_context_brief_coverage_demo(source="pager")

    def test_context_brief_coverage_cli_outputs_summary_and_json(self) -> None:
        status, stdout, stderr = run_cli(["demo", "context-brief-coverage", "--summary"], output_json=False)

        self.assertEqual(status, 0, stderr)
        self.assertEqual(stderr, "")
        self.assertIn("OMJ context brief coverage", stdout)
        self.assertIn("8/8 context brief cases passing", stdout)
        self.assertIn("catalog picker hints: 1", stdout)

        status, stdout, stderr = run_cli(["demo", "context-brief-coverage"], output_json=False)

        self.assertEqual(status, 0, stderr)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertEqual(payload["schema_version"], "context_brief_coverage/v1")
        self.assertTrue(payload["summary"]["all_passing"])


if __name__ == "__main__":
    unittest.main()
