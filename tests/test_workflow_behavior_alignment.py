from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from _local_package import load_local_package

load_local_package()

from omj.paths import resolve_paths
from omj.plugin_bundle.omj.hooks import llm_hooks, session_hooks
from omj.wrapper_sessions import (
    WrapperSessionError,
    build_wrapper_session_status,
    create_or_resume_wrapper_session,
    record_plan_decision,
)
from omj.skill_pack import builtin_harnesses, builtin_skill_reference_templates, builtin_skill_templates


def _skill_bodies() -> dict[str, str]:
    return {template.name: template.content for template in builtin_skill_templates()}


def _reference_bodies() -> dict[str, str]:
    return {template.relative_path: template.content for template in builtin_skill_reference_templates()}


class WorkflowBehaviorAlignmentTests(unittest.TestCase):
    def test_generated_planning_consumers_define_answer_only_acceptance(self) -> None:
        bodies = _skill_bodies()
        expected = (
            "Take plan acceptance only from the answer the user gave",
            "the response status and value the question tool returns",
            "never from the wording of the question you asked",
            "times out",
            "is dismissed",
            "returns with no answer",
            "the plan stays unaccepted",
            "record no acceptance",
            "prepare no handoff",
            "start nothing",
            "not a refusal either",
        )
        for name in ("plan", "ralplan"):
            with self.subTest(skill=name):
                body = " ".join(bodies[name].split())
                for fragment in expected:
                    self.assertIn(fragment, body)
                self.assertEqual(body.count("Take plan acceptance only from the answer the user gave"), 1)
                self.assertNotIn("user or wrapper accepts", body.lower())

    def test_planning_harness_acceptance_is_user_owned_not_wrapper_originated(self) -> None:
        planning = next(harness for harness in builtin_harnesses() if harness.name == "planning")
        quality_bar = " ".join(planning.quality_bar)
        self.assertIn("user's actual answer", quality_bar)
        self.assertIn("response status and value", quality_bar)
        self.assertIn("cannot originate acceptance", quality_bar)
        self.assertNotIn("user or wrapper accepts", quality_bar.lower())

    def test_wrapper_rejects_non_answers_without_mutating_plan_state(self) -> None:
        non_answers = ("timeout", "dismissed", "no answer", "Do you accept this plan?")
        for value in non_answers:
            with self.subTest(value=value), TemporaryDirectory() as tmp:
                root = Path(tmp)
                paths = resolve_paths(root / ".omj", root / ".hermes")
                started = create_or_resume_wrapper_session(
                    paths,
                    "risky refactor with a regression test",
                    source="discord",
                    source_metadata={"source_event_id": "m1", "channel_ref": "c1"},
                )
                session_id = str(started["session"]["session_id"])
                session_dir = paths.runtime_wrapper_sessions_dir / session_id
                before_session = (session_dir / "session.json").read_bytes()
                before_events = (session_dir / "events.jsonl").read_bytes()

                with self.assertRaises(WrapperSessionError):
                    record_plan_decision(paths, session_id, value)

                self.assertEqual((session_dir / "session.json").read_bytes(), before_session)
                self.assertEqual((session_dir / "events.jsonl").read_bytes(), before_events)
                status = build_wrapper_session_status(paths, session_id)
                self.assertEqual(status["session_status"], "plan_presented")

    def test_accepted_plan_prepares_handoff_but_does_not_dispatch(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = resolve_paths(root / ".omj", root / ".hermes")
            started = create_or_resume_wrapper_session(
                paths,
                "risky refactor with a regression test",
                source="discord",
                source_metadata={"source_event_id": "m1", "channel_ref": "c1"},
            )
            session_id = str(started["session"]["session_id"])
            accepted = record_plan_decision(paths, session_id, "accept")
            self.assertEqual(accepted["session"]["status"], "executor_choice_required")
            self.assertEqual(accepted["session"]["current_run_id"], "")
            self.assertEqual(accepted["status"]["chat_response"]["state"]["next_action"], "choose_executor")

    def test_generated_fault_debugging_guidance_separates_observation_and_fix_counts(self) -> None:
        reference = _reference_bodies()["references/hypothesis-and-race-method.md"]
        start = reference.index("## 6. After three failed fixes")
        section = reference[start : reference.index("\n## ", start + 1)]
        probe = next(paragraph for paragraph in section.split("\n\n") if "hidden behind the first" in paragraph)
        for fragment in (
            "with the section-1 loop at the same run count",
            "for an intermittent symptom, run the probe with the section-1 loop at the same run count",
            "cannot run on its own or its result is inconclusive",
            "record it as not observed. The next fix may proceed",
            "the probe stays open in the record as not observed",
            "until it is observed the fix under test counts toward the three as a failed fix",
            "If the pre-fix tree already shows the new symptom, the fix is not counted as failed",
            "the new symptom is a separate fault with its own reproduction record and count",
            "its hypothesis is not eliminated",
            "verified under section 7 once the reproduction passes",
            "If it does not, the fix moved the fault, and a fault that moved is a failed fix, not progress.",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, probe)
        for fragment in (
            "After the third failed fix, stop fixing.",
            "Prepare no fourth fix.",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, section)
        self.assertNotIn("the fix holds", section)
        recording = next(paragraph for paragraph in section.split("\n\n") if "the root cause is open again" in paragraph)
        moved = recording.index("When the fault moved")
        self.assertIn("record its hypothesis as unresolved, not eliminated", recording[moved:])

    def test_generated_full_fence_guidance_checks_untracked_nested_and_runtime_skips(self) -> None:
        body = _reference_bodies()["references/loop-design-review.md"]
        for fragment in (
            "`git -c core.quotePath=false ls-files --others -- <fenced dirs>`, without `--exclude-standard`",
            "`.git/info/exclude`",
            "core.excludesFile",
            "A line ending in `/` there is a nested repository; read the files inside it as well.",
            "from both listings in step 3",
            "a compiled or generated file with no matching tracked source fails",
            "Skip status comes from the acceptance run's own output, never from a collection-only listing",
            "fails unless the record lists it as skipped at launch",
            "the tests reported as skipped by a launch run of the test command the acceptance checks run",
            "are the POSIX shell forms",
            "`Test-Path`, `Get-ChildItem -Recurse -Force`, and `Get-FileHash -Algorithm SHA256`",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, body)
        self.assertNotIn("or now reports skipped", body)

    def test_child_callbacks_keep_suppression_and_preserve_research_and_advisory_hints(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            home_a = root / "home-a"
            home_b = root / "home-b"
            message = "Research source-backed behavior, then run ultraqa checks with Codex. [omj-role:reviewer]"
            session_hooks.subagent_start(
                child_session_id="child-a",
                parent_session_id="parent-a",
                omj_home=str(home_a),
                hermes_home=str(root / "hermes-a"),
            )
            child = llm_hooks.pre_llm_call(
                user_message=message,
                session_id="child-a",
                parent_session_id="parent-a",
                omj_home=str(home_a),
                hermes_home=str(root / "hermes-a"),
                platform="subagent",
                is_first_turn=True,
            )
            self.assertIsNotNone(child)
            child_context = str(child["context"])
            self.assertIn("[OMJ Role: reviewer]", child_context)
            self.assertIn("ultraqa", child_context)
            self.assertIn("selected=web-research", child_context)
            self.assertNotIn("selected=ultraprocess", child_context)
            self.assertNotIn("lane=coding_handoff", child_context)
            self.assertNotIn("next_action=prepare_one_cycle_delivery", child_context)
            self.assertNotIn("adjacent_workflows=ralplan", child_context)
            unrelated_parent = llm_hooks.pre_llm_call(
                user_message=message,
                session_id="parent-a",
                omj_home=str(home_a),
                hermes_home=str(root / "hermes-a"),
                platform="hermes",
                is_first_turn=True,
            )
            self.assertIsNotNone(unrelated_parent)
            self.assertIn("selected=ultraprocess", str(unrelated_parent["context"]))

            same_session_in_other_home = llm_hooks.pre_llm_call(
                user_message=message,
                session_id="child-a",
                parent_session_id="parent-a",
                omj_home=str(home_b),
                hermes_home=str(root / "hermes-b"),
                platform="subagent",
                is_first_turn=True,
            )
            self.assertIsNotNone(same_session_in_other_home)
            self.assertIn("selected=ultraprocess", str(same_session_in_other_home["context"]))


if __name__ == "__main__":
    unittest.main()
