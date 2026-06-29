from __future__ import annotations

import json
import unittest

from _local_package import load_local_package

load_local_package()

from omj.capabilities.hooks import hook_manifest
from omj.plugin_bundle.omj.awareness import awareness_route_hint
from omj.plugin_bundle.omj.hooks.llm_hooks import pre_llm_call
from omj.plugin_bundle.omj.hooks.tool_hooks import pre_tool_call


def sionic_omj_usage_evaluation_prompt() -> str:
    return """이번 Sionic 작업에서 OMJ가 얼마나 관여했는지 사용성 평가하고,
왜 OMJ를 덜 썼는지 분석해서 라우터 강화 플랜으로 잡아줘.
Sionic은 마크다운 노트뿐 아니라 위키 페이지/site 생성도 포함했어.
결과창에는 Background process proc_d5eb61ddcf80 finished with exit code 0~
Here's the final output: 같은 raw output, turn.completed usage, Self-improvement review 줄이 보였고
이걸 프리티하게 OMJ wrapper report로 정리해야 했어.

[OMJ Awareness]
status=prepared_not_observed; Evidence boundary: pasted status is diagnostic evidence.
[OMJ Route Hint]
intent=delivery_intent; selected=ultraprocess; confidence=medium.
mentioned_workflows=ultraprocess.
not_executed=Codex.
[omj]
selected_workflow=ultraprocess
latest_runtime_run=not_executed=Codex
execution_observed=false
review_observed=false
ci_observed=false
merge_observed=false
"""


class HookManifestTests(unittest.TestCase):
    def test_hook_manifest_projects_plugin_yaml_and_wrapper_events(self) -> None:
        manifest = hook_manifest()

        self.assertEqual(manifest["schema_version"], "omj_hook_manifest/v1")
        tools = {item["name"]: item for item in manifest["plugin_tools"]}
        hooks = {item["name"]: item for item in manifest["plugin_hooks"]}
        events = {item["name"]: item for item in manifest["wrapper_events"]}

        self.assertIn("omj_capabilities", tools)
        self.assertTrue(tools["omj_capabilities"]["supported_by_plugin_bundle"])
        self.assertTrue(tools["omj_capabilities"]["supported_by_cli_backend"])
        self.assertFalse(tools["omj_capabilities"]["observed_in_this_environment"])
        self.assertIn("omj_context", tools)
        self.assertTrue(tools["omj_context"]["supported_by_plugin_bundle"])
        self.assertTrue(tools["omj_context"]["supported_by_cli_backend"])
        self.assertTrue(tools["omj_context"]["supported_by_wrapper_contract"])
        self.assertEqual(tools["omj_context"]["cli_backend_surface"], "omj context brief")
        self.assertIn("omj_recommend", tools)
        self.assertTrue(tools["omj_recommend"]["supported_by_plugin_bundle"])
        self.assertTrue(tools["omj_recommend"]["supported_by_cli_backend"])
        self.assertTrue(tools["omj_recommend"]["supported_by_wrapper_contract"])
        self.assertIn("omj_interact", tools)
        self.assertTrue(tools["omj_interact"]["supported_by_plugin_bundle"])
        self.assertTrue(tools["omj_interact"]["supported_by_cli_backend"])
        self.assertTrue(tools["omj_interact"]["supported_by_wrapper_contract"])
        self.assertEqual(tools["omj_interact"]["cli_backend_surface"], "omj chat interact")
        self.assertIn("omj_probe", tools)
        self.assertTrue(tools["omj_probe"]["supported_by_plugin_bundle"])
        self.assertTrue(tools["omj_probe"]["supported_by_cli_backend"])
        self.assertTrue(tools["omj_probe"]["supported_by_wrapper_contract"])
        self.assertIn("pre_llm_call", hooks)
        self.assertIn("omj_awareness_primer", hooks["pre_llm_call"]["payload_fields"])
        self.assertIn("omj_context_brief", hooks["pre_llm_call"]["payload_fields"])
        self.assertIn("omj_route_hint", hooks["pre_llm_call"]["payload_fields"])
        self.assertIn("bounded_status_context", hooks["pre_llm_call"]["payload_fields"])
        self.assertIn("omj_generic_tool_checkpoint", hooks["pre_tool_call"]["payload_fields"])
        self.assertIn("tool_family_hint", hooks["pre_tool_call"]["payload_fields"])
        self.assertIn("redacted", hooks["pre_tool_call"]["payload_fields"])
        self.assertIn("executor_opened", events)
        self.assertIn("selected_executor_profile", events["executor_opened"]["payload_fields"])
        self.assertIn("native_command_registered", events)
        self.assertIn("registration_schema", events["native_command_registered"]["payload_fields"])
        self.assertIn("native_command_rendered", events)
        self.assertIn("render_kind", events["native_command_rendered"]["payload_fields"])
        self.assertIn("not proof", hooks["pre_llm_call"]["claim_boundary"])

    def test_awareness_route_hint_is_metadata_only_and_message_specific(self) -> None:
        message = "make an image explaining the cron feature with secret-token-123"

        payload = awareness_route_hint(message)
        suppressed = awareness_route_hint(message, max_hints=0)
        serialized = str(payload)

        self.assertEqual(payload["schema_version"], "omj_route_hint/v1")
        self.assertEqual(payload["status"], "hinted")
        self.assertEqual(payload["primary_workflow"], "img-summary")
        self.assertTrue(payload["message_sha256"])
        self.assertEqual(payload["message_length"], len(message))
        self.assertFalse(payload["privacy"]["raw_prompt_stored"])
        self.assertIn("image", payload["hints"][0]["matched_cues"])
        self.assertIn("not workflow execution", payload["claim_boundary"])
        self.assertNotIn(message, serialized)
        self.assertNotIn("secret-token-123", serialized)
        self.assertEqual(suppressed["status"], "no_hint")
        self.assertEqual(suppressed["hints"], [])

    def test_awareness_route_hint_uses_missed_route_primary_action(self) -> None:
        message = "missed route: Hermes skipped OMJ for my image request with secret-token-123"

        payload = awareness_route_hint(message)
        context_result = pre_llm_call(user_message=message, is_first_turn=False)
        context = context_result["context"] if context_result else ""
        serialized = str(payload)

        self.assertEqual(payload["schema_version"], "omj_route_hint/v1")
        self.assertEqual(payload["status"], "hinted")
        self.assertEqual(payload["primary_workflow"], "workflow-learning")
        self.assertEqual(payload["primary_next_action"], "record_missed_route")
        self.assertEqual(payload["hints"][0]["next_action"], "record_missed_route")
        self.assertIn("selected=workflow-learning", context)
        self.assertIn("next_action=record_missed_route", context)
        self.assertNotIn(message, serialized)
        self.assertNotIn(message, context)
        self.assertNotIn("secret-token-123", serialized)
        self.assertNotIn("secret-token-123", context)

    def test_awareness_route_hint_marks_workflow_vocabulary_as_mentioned_not_selected(self) -> None:
        message = "왜 ultraprocess 로그가 떠? Codex handoff 테스트 용어일 뿐이야."

        payload = awareness_route_hint(message)
        context_result = pre_llm_call(user_message=message, is_first_turn=False)
        context = context_result["context"] if context_result else ""

        self.assertEqual(payload["status"], "hinted")
        self.assertEqual(payload["primary_workflow"], "workflow-learning")
        self.assertEqual(payload["selected_workflow"], "workflow-learning")
        self.assertIn(payload["intent_class"], {"meta_discussion", "feedback_signal"})
        self.assertIn("ultraprocess", payload["mentioned_workflows"])
        self.assertIn("Codex", payload["mentioned_runtime_terms"])
        self.assertIn("ultraprocess", payload["not_executed"])
        self.assertIn("Codex", payload["not_executed"])
        self.assertIn("selected=workflow-learning", context)
        self.assertIn("mentioned_workflows=ultraprocess", context)
        self.assertIn("not_executed=ultraprocess, Codex", context)
        self.assertNotIn("selected=ultraprocess", context)
        self.assertNotIn(message, context)

    def test_awareness_route_hint_treats_pasted_omj_status_as_diagnostic(self) -> None:
        message = sionic_omj_usage_evaluation_prompt()

        payload = awareness_route_hint(message, max_hints=3)
        context_result = pre_llm_call(user_message=message, is_first_turn=False)
        context = context_result["context"] if context_result else ""

        self.assertEqual(payload["status"], "hinted")
        self.assertEqual(payload["primary_workflow"], "workflow-learning")
        self.assertEqual(payload["selected_workflow"], "workflow-learning")
        self.assertIn(payload["intent_class"], {"meta_discussion", "feedback_signal"})
        self.assertIn("ultraprocess", payload["mentioned_workflows"])
        self.assertIn("Codex", payload["mentioned_runtime_terms"])
        self.assertIn("ultraprocess", payload["not_executed"])
        self.assertIn("Codex", payload["not_executed"])
        self.assertEqual(payload["hints"][0]["workflow"], "workflow-learning")
        self.assertIn("selected=workflow-learning", context)
        self.assertIn("not_executed=ultraprocess, Codex", context)
        self.assertNotIn("selected=ultraprocess", context)
        self.assertNotIn(message, context)

    def test_pre_llm_call_includes_bounded_route_hint_without_raw_message(self) -> None:
        message = "make an image explaining the cron feature with secret-token-123"

        result = pre_llm_call(user_message=message, is_first_turn=False)
        context = result["context"] if result else ""
        context_brief = result["omj_context_brief"] if result else {}

        self.assertIn("[OMJ Awareness]", context)
        self.assertIn("[OMJ Route Hint]", context)
        self.assertIn("selected=img-summary", context)
        self.assertIn("selected=automation-blueprint", context)
        self.assertIn("first_response_shape=Separate copy/layout/package prep", context)
        self.assertIn("fallback_action=choose_image_generator_or_prompt_only_when_missing", context)
        self.assertIn("fallback_action=confirm_schedule_delivery_and_tools", context)
        self.assertIn("not_evidence_yet=file export, image generation", context)
        self.assertEqual(context_brief["schema_version"], "omj_context_brief/v1")
        self.assertEqual(context_brief["source"], "pre_llm_call")
        self.assertEqual(context_brief["route_hint"]["primary_workflow"], "img-summary")
        self.assertEqual(context_brief["route_hint"]["primary_next_action"], "prepare_visual_prompt_card")
        self.assertEqual(
            context_brief["route_hint"]["hints"][0]["fallback_action"],
            "choose_image_generator_or_prompt_only_when_missing",
        )
        self.assertIn(
            "generated file or image evidence",
            context_brief["route_hint"]["hints"][0]["workflow_context_card"]["first_response_shape"],
        )
        self.assertFalse(context_brief["message"]["raw_prompt_stored"])
        self.assertFalse(context_brief["message"]["raw_prompt_echoed"])
        self.assertNotIn(message, context)
        self.assertNotIn("secret-token-123", context)
        self.assertNotIn("secret-token-123", str(context_brief))

    def test_pre_llm_call_can_disable_awareness_route_hint(self) -> None:
        result = pre_llm_call(
            user_message="make an image explaining the cron feature",
            is_first_turn=False,
            include_omj_awareness=False,
        )
        context = result["context"] if result else ""

        self.assertNotIn("[OMJ Awareness]", context)
        self.assertNotIn("[OMJ Route Hint]", context)
        self.assertNotIn("selected=img-summary", context)

    def test_pre_llm_call_includes_catalog_question_hint_without_raw_message(self) -> None:
        message = "what OMJ workflows are available with secret-token-123?"

        result = pre_llm_call(user_message=message, is_first_turn=False)
        context_brief = result["omj_context_brief"] if result else {}
        catalog_question = context_brief["catalog_question"]

        self.assertEqual(catalog_question["schema_version"], "omj_catalog_question_hint/v1")
        self.assertEqual(catalog_question["status"], "matched")
        self.assertEqual(catalog_question["next_action"], "show_workflow_picker")
        self.assertEqual(catalog_question["recommended_tool"], "omj_capabilities")
        self.assertEqual(catalog_question["recommended_tool_args"], {"action": "summary"})
        self.assertIn("omj_skill_picker/v1", catalog_question["wrapper_contracts"])
        self.assertIn("omj_capability_summary/v1", catalog_question["wrapper_contracts"])
        self.assertNotIn(message, str(context_brief))
        self.assertNotIn("secret-token-123", str(context_brief))

    def test_pre_tool_call_injects_generic_tool_checkpoint_without_raw_input(self) -> None:
        cases = (
            ("image_generate", {}, "image_tools", "img-summary", "prepare_visual_prompt_card"),
            ("write_file", {}, "file_tools", "materials-package", "prepare_material_package"),
            ("web_search", {}, "search_tools", "web-research", "gather_source_backed_evidence"),
            ("codex_session_open", {}, "coding_tools", "ultraprocess", "prepare_one_cycle_delivery"),
            ("python_runner", {"tool_family": "search"}, "search_tools", "web-research", "gather_source_backed_evidence"),
        )

        for tool_name, extra_kwargs, tool_family, workflow, next_action in cases:
            with self.subTest(tool_name=tool_name):
                result = pre_tool_call(
                    tool_name=tool_name,
                    tool_input={"prompt": "secret-token-123 should never appear"},
                    **extra_kwargs,
                )
                context = result["context"] if result else ""
                checkpoint = result["omj_generic_tool_checkpoint"] if result else {}
                serialized_checkpoint = json.dumps(checkpoint, sort_keys=True)

                self.assertIn("[OMJ Tool Checkpoint]", context)
                self.assertIn("schema=omj_generic_tool_checkpoint/v1", context)
                self.assertIn(f"tool_family={tool_family}", context)
                self.assertIn(f"workflow={workflow}", context)
                self.assertIn(f"next_action={next_action}", context)
                self.assertIn("advisory tool-use context only", context)
                self.assertEqual(checkpoint["schema_version"], "omj_generic_tool_checkpoint/v1")
                self.assertEqual(checkpoint["source"], "pre_tool_call")
                self.assertEqual(checkpoint["tool_name"], tool_name)
                self.assertEqual(checkpoint["tool_family"], tool_family)
                self.assertEqual(checkpoint["primary_workflow"], workflow)
                self.assertEqual(checkpoint["primary_next_action"], next_action)
                self.assertFalse(checkpoint["privacy"]["raw_tool_input_stored"])
                self.assertFalse(checkpoint["privacy"]["raw_tool_input_echoed"])
                self.assertIn("Advisory tool-use context only", checkpoint["claim_boundary"])
                self.assertNotIn("secret-token-123", context)
                self.assertNotIn("should never appear", context)
                self.assertNotIn("secret-token-123", serialized_checkpoint)
                self.assertNotIn("should never appear", serialized_checkpoint)

    def test_pre_tool_call_checkpoint_can_be_disabled(self) -> None:
        result = pre_tool_call(
            tool_name="image_generate",
            tool_input={"prompt": "secret-token-123"},
            include_omj_tool_checkpoint=False,
        )

        self.assertIsNone(result)
