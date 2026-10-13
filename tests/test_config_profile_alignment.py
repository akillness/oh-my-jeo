from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()

from omj.capabilities.families import capability_family_projection
from omj.coding.coding_delegation import build_coding_delegation_payload
from omj.paths import OmjPaths
from omj.profiles.setup import read_setup_profile, write_setup_profile
from omj.profiles.transport import build_setup_profile_pack


class ConfigurationProfileAlignmentTests(unittest.TestCase):
    def _paths(self, root: Path) -> OmjPaths:
        return OmjPaths(root / ".omj", root / ".hermes")

    def _persist_capability_policy(self, paths: OmjPaths, disabled: list[str]) -> None:
        profile = read_setup_profile(paths)
        assert isinstance(profile, dict)
        profile["capability_policy"] = {
            "schema_version": "omj_capability_policy/v1",
            "disabled_families": list(disabled),
        }
        paths.setup_profile_path.write_text(json.dumps(profile), encoding="utf-8")

    def test_direct_hermes_plan_refuses_selected_home_disabled_workflow_before_writes(self) -> None:
        """The public Hermes plan command gates disabled workflows before recording artifacts."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            write_setup_profile(
                paths,
                ["codex-lifecycle"],
                default_executor="codex",
                capability_policy={
                    "schema_version": "omj_capability_policy/v1",
                    "disabled_families": ["plan_and_decide"],
                },
            )

            def snapshot() -> dict[str, bytes]:
                return {
                    str(path.relative_to(root)): path.read_bytes()
                    for path in sorted(root.rglob("*"))
                    if path.is_file()
                }

            before = snapshot()
            status, stdout, stderr = run_cli(
                [
                    "--omj-home",
                    str(paths.omj_home),
                    "--hermes-home",
                    str(paths.hermes_home),
                    "hermes",
                    "plan",
                    "organize",
                    "onboarding",
                    "work",
                    "--record",
                ]
            )

            self.assertEqual(status, 2)
            self.assertEqual(stdout, "")
            self.assertIn("disabled", stderr)
            self.assertEqual(snapshot(), before)
            self.assertFalse(paths.runtime_dir.exists())

    def test_direct_hermes_plan_allows_enabled_core_workflow_and_records_lifecycle_artifact(self) -> None:
        """An enabled plan workflow remains usable when an optional family is disabled."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            write_setup_profile(
                paths,
                ["codex-lifecycle"],
                default_executor="codex",
                capability_policy={
                    "schema_version": "omj_capability_policy/v1",
                    "disabled_families": ["create_materials_and_visuals"],
                },
            )

            status, stdout, stderr = run_cli(
                [
                    "--omj-home",
                    str(paths.omj_home),
                    "--hermes-home",
                    str(paths.hermes_home),
                    "hermes",
                    "plan",
                    "organize",
                    "onboarding",
                    "work",
                    "--record",
                ]
            )

            self.assertEqual((status, stderr), (0, ""))
            payload = json.loads(stdout)
            self.assertEqual(payload["plan"]["recommended_workflow"], "plan")
            artifact = payload["artifact"]
            self.assertEqual(artifact["status"], "draft")
            artifact_path = Path(artifact["path"])
            self.assertTrue(artifact_path.is_file())
            artifact_text = artifact_path.read_text(encoding="utf-8")
            self.assertIn("status: draft", artifact_text)

    def test_plan_lifecycle_aliases_remain_available_when_planning_family_disabled(self) -> None:
        """Accept, revise, and cancel aliases operate on existing plans without re-preparing them."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = self._paths(root)
            write_setup_profile(paths, ["codex-lifecycle"], default_executor="codex")
            status, stdout, stderr = run_cli(
                [
                    "--omj-home",
                    str(paths.omj_home),
                    "--hermes-home",
                    str(paths.hermes_home),
                    "hermes",
                    "plan",
                    "organize",
                    "onboarding",
                    "work",
                    "--record",
                ]
            )
            self.assertEqual((status, stderr), (0, ""))
            artifact_path = Path(json.loads(stdout)["artifact"]["path"])
            self._persist_capability_policy(paths, ["plan_and_decide"])

            for alias, expected_status in (("plan-accept", "accepted"), ("plan-revise", "revised"), ("plan-cancel", "cancelled")):
                with self.subTest(alias=alias):
                    status, stdout, stderr = run_cli(
                        [
                            "--omj-home",
                            str(paths.omj_home),
                            "--hermes-home",
                            str(paths.hermes_home),
                            "hermes",
                            alias,
                            str(artifact_path),
                        ]
                    )
                    self.assertEqual((status, stderr), (0, ""))
                    self.assertEqual(json.loads(stdout)["artifact"]["status"], expected_status)

    def test_selected_home_policy_changes_actual_wrapper_capability_offering(self) -> None:
        """The wrapper must load capability policy from its selected OMJ home."""
        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            write_setup_profile(paths, ["codex-lifecycle"], default_executor="codex", memory_mode="review-first")
            self._persist_capability_policy(paths, ["create_materials_and_visuals"])
            from omj.wrapper.contract import build_chat_interaction_payload

            payload = build_chat_interaction_payload("what can OMJ do?", mode="route", paths=paths)
        primer = payload["chat_response"]["state"]["context_primer"]
        families = {str(item["id"]): item for item in primer["capability_families"]}
        self.assertNotIn("create_materials_and_visuals", families)
        self.assertIn("delegate_coding_and_ship", families)
        self.assertIn("team", families["delegate_coding_and_ship"]["primary_workflows"])
        response = payload["chat_response"]
        self.assertNotIn("Create materials and visuals", response["body"])
        self.assertNotIn("materials-package", response["body"])
        picker_families = {
            str(item["id"]): item for item in response["state"]["skill_picker"]["capability_families"]
        }
        self.assertNotIn("create_materials_and_visuals", picker_families)
        summary_families = {
            str(item["id"]): item
            for item in response["state"]["capability_summary"]["capability_families"]
        }
        disabled_summary = summary_families["create_materials_and_visuals"]
        self.assertEqual(disabled_summary["availability"], "disabled_by_policy")
        self.assertFalse(disabled_summary["enabled"])
        self.assertEqual(disabled_summary["primary_workflows"], [])
    def test_disabled_materials_refuses_wrapper_route_and_plan_preparation(self) -> None:
        """A disabled family must block actual wrapper preparation in route and plan modes."""
        from omj.wrapper.contract import build_chat_interaction_payload

        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            write_setup_profile(
                paths,
                ["codex-lifecycle"],
                default_executor="codex",
                capability_policy={"disabled_families": ["create_materials_and_visuals"]},
            )
            for mode, message in (
                ("route", "Create a presentation deck and export the PDF"),
                ("plan", "/materials-package prepare a presentation deck"),
            ):
                with self.subTest(mode=mode):
                    with self.assertRaisesRegex(ValueError, "disabled"):
                        build_chat_interaction_payload(message, mode=mode, paths=paths)

    def test_disabled_materials_refuses_native_workflow_preparation_gate(self) -> None:
        """The shared native gate must refuse a disabled prepared workflow."""
        from omj.profiles.setup import require_enabled_workflow

        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            write_setup_profile(
                paths,
                ["codex-lifecycle"],
                default_executor="codex",
                capability_policy={"disabled_families": ["create_materials_and_visuals"]},
            )
            with self.assertRaisesRegex(ValueError, "disabled"):
                require_enabled_workflow("materials-package", paths=paths)
    def test_disabled_materials_refuses_native_interaction_without_recording_session(self) -> None:
        """The real plugin interaction returns a refusal and writes no session state."""
        from omj.plugin_bundle.omj.tools.chat_tool import omj_interact_handler

        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            write_setup_profile(
                paths,
                ["codex-lifecycle"],
                default_executor="codex",
                capability_policy={"disabled_families": ["create_materials_and_visuals"]},
            )
            result = json.loads(
                omj_interact_handler(
                    {
                        "message": "Create a presentation deck and export the PDF",
                        "mode": "route",
                        "record_session": False,
                        "omj_home": str(paths.omj_home),
                        "hermes_home": str(paths.hermes_home),
                    }
                )
            )

            self.assertEqual(result["status"], "error")
            self.assertEqual(result["error"], "package_backend_error")
            self.assertEqual(result["error_type"], "ValueError")
            self.assertFalse((paths.omj_home / "runtime").exists())


    def test_disabled_materials_is_absent_from_native_summary_lane(self) -> None:
        """Native capability summaries must not offer a disabled preparation lane."""
        from omj.capabilities.registry import capability_summary

        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            write_setup_profile(
                paths,
                ["codex-lifecycle"],
                default_executor="codex",
                capability_policy={"disabled_families": ["create_materials_and_visuals"]},
            )
            summary = capability_summary(paths)

        materials_lane = next(lane for lane in summary["lanes"] if lane["id"] == "materials_and_visuals")
        self.assertNotIn("materials-package", materials_lane["primary_skills"])
        self.assertNotIn("report-package", materials_lane["primary_skills"])
        self.assertNotIn("deliverable-package", materials_lane["primary_skills"])

    def test_disabling_plan_and_ops_keeps_reviewed_core_front_door_and_floor(self) -> None:
        """Optional family filters must not remove the required front-door floor."""
        from omj.wrapper.contract import build_chat_interaction_payload

        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            write_setup_profile(
                paths,
                ["codex-lifecycle"],
                default_executor="codex",
                capability_policy={
                    "disabled_families": ["plan_and_decide", "operate_and_observe"],
                },
            )
            payload = build_chat_interaction_payload("what can OMJ do?", mode="route", paths=paths)

        state = payload["chat_response"]["state"]
        option_ids = {str(option["id"]) for option in state["skill_picker"]["options"]}
        self.assertTrue({"oh-my-jeo", "agent-ops-review", "doctor"} <= option_ids)
        self.assertNotIn("deep-interview", option_ids)
        self.assertNotIn("ralplan", option_ids)
        self.assertNotIn("automation-blueprint", option_ids)
        family_cards = {
            str(item["id"]): item for item in state["capability_summary"]["capability_families"]
        }
        self.assertEqual(family_cards["plan_and_decide"]["retained_core_workflows"], ["oh-my-jeo"])
        self.assertEqual(
            family_cards["operate_and_observe"]["retained_core_workflows"],
            ["agent-ops-review", "cancel", "doctor", "skill"],
        )
    def test_disabled_planning_family_refuses_plan_stage_before_material_preparation(self) -> None:
        """A disabled planning family must block plan-mode scaffolding before any material plan."""
        from omj.wrapper.contract import build_chat_interaction_payload

        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            write_setup_profile(
                paths,
                ["codex-lifecycle"],
                default_executor="codex",
                capability_policy={"disabled_families": ["plan_and_decide"]},
            )
            with self.assertRaisesRegex(ValueError, "disabled"):
                build_chat_interaction_payload(
                    "/materials-package prepare a presentation deck",
                    mode="plan",
                    paths=paths,
                )

    def test_disabled_plan_workflow_cannot_migrate_to_enabled_family(self) -> None:
        """A disabled workflow keeps its canonical family and cannot be prepared elsewhere."""
        from omj.wrapper.contract import build_chat_interaction_payload

        projection = capability_family_projection(
            disabled_families={"plan_and_decide", "operate_and_observe"}
        )
        self.assertNotIn("strategy-brief", projection["workflow_to_family"])
        self.assertIn("strategy-brief", projection["disabled_workflows"])

        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            write_setup_profile(
                paths,
                ["codex-lifecycle"],
                default_executor="codex",
                capability_policy={
                    "disabled_families": ["plan_and_decide", "operate_and_observe"],
                },
            )
            for mode, message in (
                ("route", "strategy-brief: Make onboarding smoother"),
                ("plan", "/strategy-brief Make onboarding smoother"),
            ):
                with self.subTest(mode=mode):
                    with self.assertRaisesRegex(ValueError, "disabled"):
                        build_chat_interaction_payload(message, mode=mode, paths=paths)


    def test_selected_home_parallelism_reaches_actual_prepared_handoffs_for_all_owners(self) -> None:
        """Wrapper delegation reads owner policy from selected home without a policy argument."""
        policy = {
            "codex": {"max_workers": 2},
            "claude-code": {"max_workers": 3},
            "hermes": {"max_workers": 1},
            "generic": {"max_workers": 4},
        }
        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            write_setup_profile(
                paths,
                ["codex-lifecycle"],
                default_executor="codex",
                memory_mode="review-first",
                parallelism_policy=policy,
            )
            from omj.wrapper.contract import build_chat_interaction_payload

            for owner, expected in policy.items():
                with self.subTest(owner=owner):
                    payload = build_chat_interaction_payload(
                        "risky refactor",
                        source="discord",
                        mode="delegate",
                        executor_target=owner,
                        paths=paths,
                    )
                    handoff = next(
                        value
                        for key, value in payload["delegation"].items()
                        if key.endswith("_handoff") and isinstance(value, dict)
                    )
                    self.assertEqual(handoff["parallelism_policy"], expected)
                    self.assertEqual(handoff["status"], "prepared_not_observed")
                    self.assertNotIn("worker_launch", handoff)

    def test_disabled_known_family_changes_offered_workflows_without_removing_coding_core(self) -> None:
        """Disabling one known family removes its prepared workflows but keeps coding handoff routes."""
        projection = capability_family_projection(
            ["report-package", "team", "request-to-handoff"],
            disabled_families={"create_materials_and_visuals"},
        )
        families = {str(item["id"]): item for item in projection["families"]}

        self.assertEqual(families["create_materials_and_visuals"]["primary_workflows"], [])
        self.assertIn("team", families["delegate_coding_and_ship"]["primary_workflows"])
        self.assertEqual(projection["workflow_to_family"].get("team"), "delegate_coding_and_ship")

    def test_optional_parallelism_policy_survives_transport_and_rerun(self) -> None:
        """Owner-specific parallelism is portable state, not a one-run local default."""
        policy = {
            "codex": {"max_workers": 2},
            "claude-code": {"max_workers": 3},
            "hermes": {"max_workers": 1},
            "generic": {"max_workers": 4},
        }
        with TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            write_setup_profile(
                paths,
                ["codex-lifecycle"],
                default_executor="codex",
                memory_mode="review-first",
                parallelism_policy=policy,
            )
            pack = build_setup_profile_pack(paths)
            write_setup_profile(paths, ["codex-lifecycle"], default_executor="codex")
            stored = read_setup_profile(paths)

        self.assertEqual(pack["profile"]["parallelism_policy"], policy)
        self.assertEqual(stored["parallelism_policy"], policy)

    def test_parallelism_reaches_every_prepared_executor_handoff_without_launching_workers(self) -> None:
        """Each executor receives only its own prepared policy; building a handoff launches nothing."""
        policy = {
            "codex": {"max_workers": 2},
            "claude-code": {"max_workers": 3},
            "hermes": {"max_workers": 1},
            "generic": {"max_workers": 4},
        }
        for owner in policy:
            with self.subTest(owner=owner):
                payload = build_coding_delegation_payload(
                    "risky refactor",
                    source="discord",
                    executor_target=owner,
                    parallelism_policy=policy,
                )
                handoff = next(
                    value
                    for key, value in payload.items()
                    if key.endswith("_handoff") and isinstance(value, dict)
                )
                self.assertEqual(handoff["parallelism_policy"], policy[owner])
                self.assertEqual(handoff["status"], "prepared_not_observed")
                self.assertNotIn("worker_launch", handoff)

    def _prepared_handoff(self, payload: dict[str, object]) -> dict[str, object]:
        handoffs = [
            value
            for key, value in payload.items()
            if key.endswith("_handoff") and isinstance(value, dict)
        ]
        self.assertEqual(len(handoffs), 1)
        return handoffs[0]

    def test_canonical_parallelism_defaults_reach_each_selected_owner_handoff(self) -> None:
        """Canonical defaults are projected into each owner-only prepared handoff."""
        policy = {
            "schema_version": "parallelism_policy/v1",
            "default_concurrency": 7,
            "global_concurrency": 11,
            "lane_budget_default": 13,
        }
        expected = {
            "default_concurrency": 7,
            "global_concurrency": 11,
            "lane_budget_default": 13,
        }
        for owner in ("codex", "claude-code", "hermes", "generic"):
            with self.subTest(owner=owner):
                payload = build_coding_delegation_payload(
                    "risky refactor",
                    source="discord",
                    executor_target=owner,
                    parallelism_policy=policy,
                )
                handoff = self._prepared_handoff(payload)
                self.assertEqual(handoff["parallelism_policy"], expected)
                self.assertEqual(handoff["status"], "prepared_not_observed")
                self.assertNotIn("per_owner", handoff["parallelism_policy"])
                self.assertNotIn("worker_launch", handoff)

    def test_mixed_parallelism_projects_only_selected_owner_limits_over_canonical_defaults(self) -> None:
        """Selected-owner limits override local defaults without leaking other owners."""
        policy = {
            "schema_version": "parallelism_policy/v1",
            "default_concurrency": 5,
            "global_concurrency": 8,
            "lane_budget_default": 6,
            "per_owner": {
                "codex": {"max_workers": 2, "global_limit": 3},
                "claude-code": {"max_workers": 3, "global_limit": 4},
                "hermes": {"max_workers": 4, "lane_budget": 5},
                "generic": {"max_workers": 6, "concurrency": 7},
            },
        }
        canonical = {
            "default_concurrency": 5,
            "global_concurrency": 8,
            "lane_budget_default": 6,
        }
        for owner, explicit in policy["per_owner"].items():
            with self.subTest(owner=owner):
                payload = build_coding_delegation_payload(
                    "risky refactor",
                    source="discord",
                    executor_target=owner,
                    parallelism_policy=policy,
                )
                handoff = self._prepared_handoff(payload)
                projected = handoff["parallelism_policy"]
                self.assertEqual(
                    projected,
                    {**canonical, **explicit},
                )
                self.assertEqual(projected["global_concurrency"], canonical["global_concurrency"])
                for other_owner, other_limits in policy["per_owner"].items():
                    if other_owner != owner:
                        for setting, value in other_limits.items():
                            self.assertNotEqual(projected.get(setting), value)
                self.assertNotIn("per_owner", projected)
                self.assertEqual(handoff["status"], "prepared_not_observed")
                self.assertNotIn("worker_launch", handoff)


    def test_each_canonical_parallelism_field_alone_reaches_handoff(self) -> None:
        """Each accepted canonical policy field is independently projected."""
        for owner in ("codex", "claude-code", "hermes", "generic"):
            for field in ("default_concurrency", "global_concurrency", "lane_budget_default"):
                with self.subTest(owner=owner, field=field):
                    policy = {"schema_version": "parallelism_policy/v1", field: 9}
                    payload = build_coding_delegation_payload(
                        "risky refactor",
                        source="discord",
                        executor_target=owner,
                        parallelism_policy=policy,
                    )
                handoff = self._prepared_handoff(payload)
                self.assertEqual(handoff["parallelism_policy"], {field: 9})

    def test_canonical_baseline_does_not_leak_unselected_nested_owner_limits(self) -> None:
        """An unselected nested owner cannot alter the selected owner's baseline."""
        policy = {
            "schema_version": "parallelism_policy/v1",
            "default_concurrency": 5,
            "global_concurrency": 8,
            "lane_budget_default": 6,
            "per_owner": {"hermes": {"max_workers": 99}},
        }
        payload = build_coding_delegation_payload(
            "risky refactor",
            source="discord",
            executor_target="codex",
            parallelism_policy=policy,
        )
        handoff = self._prepared_handoff(payload)
        self.assertEqual(
            handoff["parallelism_policy"],
            {
                "default_concurrency": 5,
                "global_concurrency": 8,
                "lane_budget_default": 6,
            },
        )
        self.assertNotEqual(handoff["parallelism_policy"].get("max_workers"), 99)

    def test_nested_per_owner_only_policy_keeps_existing_owner_only_handoff_shape(self) -> None:
        """Nested per-owner policy remains a direct selected-owner handoff dict."""
        policy = {
            "schema_version": "parallelism_policy/v1",
            "per_owner": {"codex": {"max_workers": 2, "global_limit": 3}},
        }
        payload = build_coding_delegation_payload(
            "risky refactor",
            source="discord",
            executor_target="codex",
            parallelism_policy=policy,
        )
        handoff = self._prepared_handoff(payload)
        self.assertEqual(
            handoff["parallelism_policy"],
            {"max_workers": 2, "global_limit": 3},
        )
        self.assertNotIn("per_owner", handoff["parallelism_policy"])

if __name__ == "__main__":
    unittest.main()
