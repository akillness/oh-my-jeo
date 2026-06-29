from __future__ import annotations

from pathlib import Path
import unittest

from _local_package import load_local_package

load_local_package()
from omj import (
    chat_router,
    cli,
    coding_lifecycle,
    playbooks,
    recommend,
    roles,
    runtime_artifacts,
    runtime_records,
    setup_profiles,
    team_profiles,
    wrapper_contract,
    wrapper_sessions,
)
from omj.catalogs import playbooks as catalog_playbooks
from omj.catalogs import roles as catalog_roles
from omj.commands import main as command_main
from omj.ingress import compact_source_metadata, extract_message_text, extract_source_metadata
from omj.profiles import setup as profile_setup
from omj.profiles import team as profile_team
from omj.routing import chat as routing_chat
from omj.routing import recommend as routing_recommend
from omj.runtime import artifacts as runtime_artifacts_module
from omj.runtime import records as runtime_records_module
from omj.skills import builtin_skill_templates
from omj.skills import packaging as skills_packaging
from omj.wrapper import contract as wrapper_contract_module
from omj.wrapper import lifecycle as wrapper_lifecycle_module
from omj.wrapper import sessions as wrapper_sessions_module


class ArchitectureLayoutTests(unittest.TestCase):
    def test_src_root_uses_only_package_directories(self) -> None:
        src_root = Path(__file__).resolve().parents[1] / "src"

        ignored_generated = {"__pycache__"}
        entries = sorted(
            path.name
            for path in src_root.iterdir()
            if path.name not in ignored_generated and not path.name.endswith(".egg-info")
        )
        package_root = src_root / "omj"
        domain_packages = (
            "capabilities",
            "catalogs",
            "codegraph",
            "coding",
            "commands",
            "core",
            "install",
            "maintenance",
            "mcp",
            "plugin_bundle",
            "profiles",
            "quality",
            "routing",
            "runtime",
            "skills",
            "surfaces",
            "system",
            "workflows",
            "wrapper",
        )

        # ``omj`` is the canonical implementation package; ``omj`` is the
        # jeo-brand alias package introduced by the staged rename.
        brand_packages = ("omj", "omh")
        self.assertEqual(entries, sorted([*domain_packages, *brand_packages]))
        self.assertFalse((src_root / "__init__.py").exists())
        self.assertTrue((package_root / "__init__.py").is_file())
        self.assertTrue((src_root / "omj" / "__init__.py").is_file())
        self.assertTrue((package_root / "cli" / "__init__.py").is_file())
        self.assertFalse((package_root / "routing").exists())
        self.assertFalse((package_root / "coding").exists())

        for package_name in domain_packages:
            with self.subTest(package_name=package_name):
                self.assertTrue((src_root / package_name / "__init__.py").is_file())
        for grouped_module in (
            "maintenance/doctor.py",
            "mcp/bridge.py",
            "quality/parity.py",
            "surfaces/hud.py",
            "system/paths.py",
        ):
            with self.subTest(grouped_module=grouped_module):
                self.assertTrue((src_root / grouped_module).is_file())

        # Domain packages must carry real modules; an ``__init__.py``-only
        # directory signals an empty stub.  The ``omh`` brand alias is exempt:
        # it is intentionally a pure import shim that re-exports ``omj``.
        init_only_dirs = sorted(
            path.name
            for path in src_root.iterdir()
            if path.is_dir()
            and path.name not in brand_packages
            and sorted(
                child.name
                for child in path.iterdir()
                if child.name not in ignored_generated
            )
            == ["__init__.py"]
        )
        self.assertEqual(init_only_dirs, [])

        representative_groups = {
            "coding": {"coding_delegation.py", "executors.py", "worktree_creator.py"},
            "routing": {"chat.py", "recommend.py", "route_plan.py"},
            "runtime": {"artifacts.py", "records.py"},
            "wrapper": {"contract.py", "sessions.py", "lifecycle.py"},
        }
        for package_name, expected_modules in representative_groups.items():
            with self.subTest(package_name=package_name):
                files = {path.name for path in (src_root / package_name).glob("*.py")}
                self.assertLessEqual(expected_modules, files)

    def test_compatibility_adapters_point_to_deep_modules(self) -> None:
        self.assertIs(cli.main, command_main.main)
        self.assertIs(chat_router.route_chat_message, routing_chat.route_chat_message)
        self.assertIs(recommend.recommend_skills, routing_recommend.recommend_skills)
        self.assertIs(runtime_artifacts.create_run, runtime_artifacts_module.create_run)
        self.assertIs(runtime_records.validate_run_record, runtime_records_module.validate_run_record)
        self.assertIs(wrapper_contract.build_chat_interaction_payload, wrapper_contract_module.build_chat_interaction_payload)
        self.assertIs(wrapper_sessions.create_or_resume_wrapper_session, wrapper_sessions_module.create_or_resume_wrapper_session)
        self.assertIs(coding_lifecycle.start_codex_delegation_lifecycle, wrapper_lifecycle_module.start_codex_delegation_lifecycle)
        self.assertIs(builtin_skill_templates, skills_packaging.builtin_skill_templates)
        self.assertIs(playbooks.list_playbooks, catalog_playbooks.list_playbooks)
        self.assertIs(roles.role_definitions, catalog_roles.role_definitions)
        self.assertIs(setup_profiles.build_setup_profile, profile_setup.build_setup_profile)
        self.assertIs(team_profiles.list_team_profile_packs, profile_team.list_team_profile_packs)

    def test_root_compatibility_facades_stay_thin(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        facades = {
            "src/omj/chat_router.py": "from .routing.chat import *  # noqa: F401,F403",
            "src/omj/recommend.py": "from .routing.recommend import *  # noqa: F401,F403",
            "src/omj/runtime_artifacts.py": "from .runtime.artifacts import *  # noqa: F401,F403",
            "src/omj/runtime_records.py": "from .runtime.records import *  # noqa: F401,F403",
            "src/omj/wrapper_contract.py": "from .wrapper.contract import *  # noqa: F401,F403",
            "src/omj/wrapper_sessions.py": "from .wrapper.sessions import *  # noqa: F401,F403",
            "src/omj/coding_lifecycle.py": "from .wrapper.lifecycle import *  # noqa: F401,F403",
            "src/omj/playbooks.py": "from .catalogs.playbooks import *  # noqa: F401,F403",
            "src/omj/roles.py": "from .catalogs.roles import *  # noqa: F401,F403",
            "src/omj/setup_profiles.py": "from .profiles.setup import *  # noqa: F401,F403",
            "src/omj/team_profiles.py": "from .profiles.team import *  # noqa: F401,F403",
            "src/omj/materials.py": "from .workflows.materials import *  # noqa: F401,F403",
            "src/omj/operations.py": "from .workflows.operations import *  # noqa: F401,F403",
            "src/omj/paper_learning.py": "from .workflows.paper_learning import *  # noqa: F401,F403",
            "src/omj/source_finder.py": "from .workflows.source_finder import *  # noqa: F401,F403",
            "src/omj/visual_summary.py": "from .workflows.visual_summary import *  # noqa: F401,F403",
            "src/omj/research_department.py": "from .workflows.research_department import *  # noqa: F401,F403",
            "src/omj/hermes_ops.py": "from .workflows.hermes_ops import *  # noqa: F401,F403",
            "src/omj/goal_loop.py": "from .workflows.goal_loop import *  # noqa: F401,F403",
            "src/omj/goal_ledger.py": "from .workflows.goal_ledger import *  # noqa: F401,F403",
            "src/omj/loopability.py": "from .workflows.loopability import *  # noqa: F401,F403",
            "src/omj/memory.py": "from .workflows.memory import *  # noqa: F401,F403",
            "src/omj/workflow_learning.py": "from .workflows.workflow_learning import *  # noqa: F401,F403",
            "src/omj/operator_productivity.py": "from .workflows.operator_productivity import *  # noqa: F401,F403",
            "src/omj/use_cases.py": "from .workflows.use_cases import *  # noqa: F401,F403",
            "src/omj/observation_journal.py": "from .workflows.observation_journal import *  # noqa: F401,F403",
            "src/omj/hermes_planning.py": "from .workflows.hermes_planning import *  # noqa: F401,F403",
            "src/omj/coding_contracts.py": "from .coding.coding_contracts import *  # noqa: F401,F403",
            "src/omj/coding_delegation.py": "from .coding.coding_delegation import *  # noqa: F401,F403",
            "src/omj/codex_progress.py": "from .coding.codex_progress import *  # noqa: F401,F403",
            "src/omj/context_safety.py": "from .coding.context_safety import *  # noqa: F401,F403",
            "src/omj/executor_progress.py": "from .coding.executor_progress import *  # noqa: F401,F403",
            "src/omj/executor_readiness.py": "from .coding.executor_readiness import *  # noqa: F401,F403",
            "src/omj/executors.py": "from .coding.executors import *  # noqa: F401,F403",
            "src/omj/isolation.py": "from .coding.isolation import *  # noqa: F401,F403",
            "src/omj/team_readiness.py": "from .coding.team_readiness import *  # noqa: F401,F403",
            "src/omj/work_reporting.py": "from .coding.work_reporting import *  # noqa: F401,F403",
            "src/omj/worktree_creator.py": "from .coding.worktree_creator import *  # noqa: F401,F403",
            "src/omj/installer.py": "from .install.installer import *  # noqa: F401,F403",
            "src/omj/manifest.py": "from .install.manifest import *  # noqa: F401,F403",
            "src/omj/plugin_pack.py": "from .install.plugin_pack import *  # noqa: F401,F403",
            "src/omj/plugin_observations.py": "from .install.plugin_observations import *  # noqa: F401,F403",
            "src/omj/config_adapter.py": "from .install.config_adapter import *  # noqa: F401,F403",
            "src/omj/command_path.py": "from .install.command_path import *  # noqa: F401,F403",
            "src/omj/release_install_smoke.py": "from .install.release_install_smoke import *  # noqa: F401,F403",
            "src/omj/release_smoke_core.py": "from .install.release_smoke_core import *  # noqa: F401,F403",
            "src/omj/paths.py": "from .system.paths import *  # noqa: F401,F403",
            "src/omj/local_store.py": "from .system.local_store import *  # noqa: F401,F403",
            "src/omj/hashutil.py": "from .system.hashutil import *  # noqa: F401,F403",
            "src/omj/workflow_state.py": "from .system.workflow_state import *  # noqa: F401,F403",
            "src/omj/targets.py": "from .system.targets import *  # noqa: F401,F403",
            "src/omj/ingress.py": "from .system.ingress import *  # noqa: F401,F403",
            "src/omj/capability_roadmap.py": "from .quality.capability_roadmap import *  # noqa: F401,F403",
            "src/omj/grounded_score.py": "from .quality.grounded_score import *  # noqa: F401,F403",
            "src/omj/harness_quality.py": "from .quality.harness_quality import *  # noqa: F401,F403",
            "src/omj/parity.py": "from .quality.parity import *  # noqa: F401,F403",
            "src/omj/context.py": "from .surfaces.context import *  # noqa: F401,F403",
            "src/omj/demo.py": "from .surfaces.demo import *  # noqa: F401,F403",
            "src/omj/hud.py": "from .surfaces.hud import *  # noqa: F401,F403",
            "src/omj/menubar_status.py": "from .surfaces.menubar_status import *  # noqa: F401,F403",
            "src/omj/quickstart.py": "from .surfaces.quickstart import *  # noqa: F401,F403",
            "src/omj/doctor.py": "from .maintenance.doctor import *  # noqa: F401,F403",
            "src/omj/probe.py": "from .maintenance.probe import *  # noqa: F401,F403",
            "src/omj/release.py": "from .maintenance.release import *  # noqa: F401,F403",
            "src/omj/mcp_bridge.py": "from .mcp.bridge import *  # noqa: F401,F403",
        }
        for relative_path, import_line in facades.items():
            with self.subTest(relative_path=relative_path):
                lines = [
                    line
                    for line in (repo_root / relative_path).read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                self.assertEqual(lines, ["from __future__ import annotations", import_line])

        module_alias_facades = {
            "src/omj/menubar_app.py": [
                "from __future__ import annotations",
                "import sys",
                "from .surfaces import menubar_app as _implementation",
                "sys.modules[__name__] = _implementation",
            ],
        }
        for relative_path, expected_lines in module_alias_facades.items():
            with self.subTest(relative_path=relative_path):
                lines = [
                    line
                    for line in (repo_root / relative_path).read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
                self.assertEqual(lines, expected_lines)

    def test_ingress_owns_message_and_metadata_extraction(self) -> None:
        event = {"event": {"text": "risky refactor", "id": "m1", "channel": "c1", "user": "u1", "ts": "123.4"}}

        self.assertEqual(extract_message_text(event), "risky refactor")
        self.assertEqual(
            extract_source_metadata(event),
            {"source_event_id": "m1", "channel_ref": "c1", "user_ref": "u1", "timestamp": "123.4"},
        )
        self.assertEqual(compact_source_metadata({"source_event_id": "m1", "raw": "drop"}), {"source_event_id": "m1"})


if __name__ == "__main__":
    unittest.main()
