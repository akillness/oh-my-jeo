from __future__ import annotations

import copy
import hashlib
import json
import socket
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from _local_package import load_local_package

load_local_package()

from omj.codegraph import build_handoff_context  # noqa: E402
from omj.codegraph.selection import (  # noqa: E402
    CODEGRAPH_TEST_SELECTION_SCHEMA_VERSION,
    render_test_selection_text,
    select_tests_for_changes,
)
from omj.codegraph.uml import (  # noqa: E402
    CODEBASE_UML_SCHEMA_VERSION,
    UML_RENDER_PLAN_SCHEMA_VERSION,
    build_uml_model,
    render_plan,
    render_plantuml,
)
from omj.coding.request_verdicts import (  # noqa: E402
    COMPLEXITY_TIER_EFFORTS,
    COMPLEXITY_TIER_MODEL_CLASSES,
    MODEL_CONTRACT_COVERAGE_SCHEMA_VERSION,
    REASON_AXIS_NOT_DECLARED,
    REASON_NO_DOCUMENTED_CONTRACT,
    REASON_POLICY_NOT_RECORDED,
    REASON_RETENTION_INDEFINITE,
    REASON_TRAINING_USE_INCLUDES,
    VERDICT_CONFLICTING,
    VERDICT_PERMITTING,
    VERDICT_UNKNOWN,
    build_model_contract_coverage,
    coverage_exit_code,
    data_handling_filtered_chain,
    model_data_handling_verdict,
    recommend_model_for_complexity,
    score_request_complexity,
)
from omj.workflows.plan_variants import (  # noqa: E402
    PLAN_VARIANT_CLAIM_BOUNDARY,
    PLAN_VARIANT_HANDOFF_BOUNDARY,
    PLAN_VARIANT_NOT_OBSERVED,
    PLAN_VARIANT_SCHEMA_VERSION,
    build_plan_variant,
    build_plan_variant_delta,
    build_plan_variant_ref,
    render_plan_variant_text,
    validate_plan_variant,
)
from omj.workflows.project_terms import (  # noqa: E402
    PROJECT_TERMS_BOUNDARY,
    ProjectTermsParseError,
    build_project_terms_capture_inputs,
    parse_project_terms,
)


def _graph(root: Path) -> dict[str, object]:
    """One static graph fixture shared by selection, UML, and handoff tests."""
    return {
        "schema_version": "omj_codegraph/v1",
        "repo_root": str(root),
        "generated_at": "2026-01-01T00:00:00Z",
        "files": [
            {
                "path": "src/pkg/leaf.py",
                "kind": "python",
                "defines": ["pkg.leaf.leaf"],
                "imports": [],
                "entrypoint_tags": [],
            },
            {
                "path": "src/pkg/importer.py",
                "kind": "python",
                "defines": ["pkg.importer.importer"],
                "imports": [],
                "entrypoint_tags": [],
            },
            {
                "path": "tests/test_leaf.py",
                "kind": "python",
                "defines": ["tests.test_leaf.test_leaf"],
                "imports": [],
                "entrypoint_tags": ["test"],
            },
            {
                "path": "tests/test_importer.py",
                "kind": "python",
                "defines": ["tests.test_importer.test_importer"],
                "imports": [],
                "entrypoint_tags": ["test"],
            },
            {
                "path": "src/pkg/orphan.py",
                "kind": "python",
                "defines": ["pkg.orphan.orphan"],
                "imports": [],
                "entrypoint_tags": [],
            },
            {
                "path": "src/other/extra.py",
                "kind": "python",
                "defines": ["other.extra"],
                "imports": [],
                "entrypoint_tags": [],
            },
            {
                "path": "src/third/extra.py",
                "kind": "python",
                "defines": ["third.extra"],
                "imports": [],
                "entrypoint_tags": [],
            },
        ],
        "symbols": [
            {
                "qualified_name": "pkg.leaf.leaf",
                "name": "leaf",
                "kind": "function",
                "path": "src/pkg/leaf.py",
                "line": 1,
            },
            {
                "qualified_name": "pkg.importer.importer",
                "name": "importer",
                "kind": "function",
                "path": "src/pkg/importer.py",
                "line": 1,
            },
            {
                "qualified_name": "tests.test_leaf.test_leaf",
                "name": "test_leaf",
                "kind": "function",
                "path": "tests/test_leaf.py",
                "line": 1,
            },
            {
                "qualified_name": "tests.test_importer.test_importer",
                "name": "test_importer",
                "kind": "function",
                "path": "tests/test_importer.py",
                "line": 1,
            },
            {
                "qualified_name": "other.extra",
                "name": "extra",
                "kind": "function",
                "path": "src/other/extra.py",
                "line": 1,
            },
            {
                "qualified_name": "third.extra",
                "name": "extra",
                "kind": "function",
                "path": "src/third/extra.py",
                "line": 1,
            },
        ],
        "stats": {
            "file_count": 7,
            "python_file_count": 7,
            "parsed_file_count": 7,
            "parse_error_count": 0,
            "symbol_count": 6,
            "edge_count": 3,
            "internal_import_edge_count": 3,
            "entrypoint_file_count": 2,
            "warning_count": 1,
        },
        "claim_boundary": "Static local analysis is not execution/review/CI/merge evidence.",
        "edges": [
            {"from": "src/pkg/importer.py", "to": "src/pkg/leaf.py", "kind": "imports_internal"},
            {"from": "tests/test_leaf.py", "to": "src/pkg/leaf.py", "kind": "imports_internal"},
            {"from": "tests/test_importer.py", "to": "src/pkg/importer.py", "kind": "imports_internal"},
        ],
        "warnings": ["parse_error: ignored.py: SyntaxError"],
    }

def _materialize_graph(root: Path) -> None:
    for record in _graph(root)["files"]:
        path = root / str(record["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fixture\n", encoding="utf-8")


class GraphSelectionAndUmlTests(unittest.TestCase):
    def test_changed_source_selects_reachable_tests_and_keeps_source_refs(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            _materialize_graph(root)
            payload = select_tests_for_changes(_graph(root), ["src/pkg/leaf.py"])

        self.assertEqual(payload["schema_version"], CODEGRAPH_TEST_SELECTION_SCHEMA_VERSION)
        self.assertEqual(
            payload["selected_tests"],
            [
                {"path": "tests/test_importer.py", "distance": 2, "changed_paths": ["src/pkg/leaf.py"]},
                {"path": "tests/test_leaf.py", "distance": 1, "changed_paths": ["src/pkg/leaf.py"]},
            ],
        )
        self.assertEqual(payload["reached_source_files"], ["src/pkg/importer.py"])
        self.assertEqual(payload["changed_paths"][0]["resolved_path"], "src/pkg/leaf.py")
        self.assertEqual(payload["scanner_warnings"], ["parse_error: ignored.py: SyntaxError"])
        text = render_test_selection_text(payload)
        self.assertIn("Scanner warnings (1)", text)
        self.assertIn("parse_error: ignored.py: SyntaxError", text)
        self.assertIn("never a substitute for the full suite", payload["claim_boundary"])

    def test_unreferenced_change_reports_no_tests_reached_instead_of_expanding_suite(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            _materialize_graph(root)
            payload = select_tests_for_changes(_graph(root), ["src/pkg/orphan.py"])

        self.assertEqual(payload["selected_tests"], [])
        self.assertEqual(payload["selected_test_paths"], [])
        self.assertEqual(payload["reached_source_files"], [])
        self.assertEqual(payload["changed_paths"][0]["selected_test_count"], 0)
        text = render_test_selection_text(payload)
        self.assertIn("Selected tests (0)\n  - none", text)
        self.assertIn("nothing in the graph imports this module", text)

    def test_selection_is_read_only_and_never_executes_or_contacts_external_services(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            _materialize_graph(root)
            (root / "keep.txt").write_text("unchanged", encoding="utf-8")
            before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

            def refuse(*args: object, **kwargs: object) -> None:
                raise AssertionError("selection reached an execution or network boundary")

            with (
                mock.patch.object(subprocess, "run", refuse),
                mock.patch.object(subprocess, "Popen", refuse),
                mock.patch.object(socket, "socket", refuse),
            ):
                payload = select_tests_for_changes(_graph(root), ["src/pkg/leaf.py"])

            after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

        self.assertEqual(payload["selected_test_paths"], ["tests/test_importer.py", "tests/test_leaf.py"])

    def test_uml_and_handoff_consume_same_graph_with_bounded_outputs(self) -> None:
        with TemporaryDirectory() as tmp:
            graph = _graph(Path(tmp).resolve())
            uml = build_uml_model(graph, max_nodes=2, max_interface=1)
            handoff = build_handoff_context(graph, task="update leaf importer")

        self.assertEqual(uml["schema_version"], CODEBASE_UML_SCHEMA_VERSION)
        self.assertEqual(uml["source_schema_version"], graph["schema_version"])
        self.assertLessEqual(len(uml["nodes"]), 2)
        self.assertGreaterEqual(len(uml["omissions"]["units_folded"]), 1)
        self.assertEqual(uml["view"]["max_interface"], 1)
        self.assertLessEqual(len(handoff["focus_files"]), 12)
        self.assertLessEqual(len(handoff["focus_symbols"]), 20)
        self.assertEqual(
            {record["path"] for record in handoff["focus_files"][:2]},
            {"src/pkg/importer.py", "src/pkg/leaf.py"},
        )
        self.assertIn("Static local analysis is not execution/review/CI/merge evidence", handoff["claim_boundary"])

    def test_uml_escaping_and_prepare_only_render_plan_are_exact_and_bounded(self) -> None:
        graph = _graph(Path("/tmp/repo"))
        model = build_uml_model(graph, max_nodes=2)
        source = render_plantuml(model, title='Unsafe "diagram"')
        self.assertIn("title Unsafe 'diagram'", source)
        self.assertNotIn('title Unsafe "diagram"', source)

        which = {"plantuml": "/opt/plantuml", "dot": "/opt/dot"}.get
        plan = render_plan(source_path="/tmp/diagram.puml", output_format="svg", environ={}, which=which)
        self.assertEqual(plan["schema_version"], UML_RENDER_PLAN_SCHEMA_VERSION)
        self.assertEqual(plan["status"], "ready")
        self.assertEqual(plan["renderer"], "plantuml")
        self.assertEqual(plan["layout_engine"], "dot")
        self.assertEqual(plan["expected_output_path"], "/tmp/diagram.svg")
        self.assertIn("-tsvg", plan["command"])
        self.assertIn("not render evidence", plan["claim_boundary"])

        missing = render_plan(source_path="/tmp/diagram.puml", environ={}, which=lambda _: None)
        self.assertEqual(missing["status"], "blocked")
        self.assertEqual(missing["command"], [])
        self.assertTrue(any("brew install plantuml" in blocker for blocker in missing["blockers"]))


_PARENT = {
    "schema_version": "hermes_plan/v1",
    "status": "accepted",
    "path": "/tmp/hermes/plans/accepted.md",
    "sha256": "a" * 64,
    "task_statement_sha256": "b" * 64,
}


class PlanningVariantAndTerminologyTests(unittest.TestCase):
    def test_variant_is_deterministic_metadata_and_leaves_accepted_parent_unchanged(self) -> None:
        parent = copy.deepcopy(_PARENT)
        delta = build_plan_variant_delta(
            dimension="scope",
            label="docs",
            parent_value="same PR",
            variant_value="follow-up",
            reason="reduce release risk",
        )
        first = build_plan_variant(parent_artifact=parent, name="docs-later", deltas=[delta], created_at="2026-01-01T00:00:00Z")
        second = build_plan_variant(parent_artifact=parent, name="docs-later", deltas=[delta], created_at="2027-01-01T00:00:00Z")

        self.assertEqual(parent, _PARENT)
        self.assertEqual(first["variant_id"], second["variant_id"])
        self.assertEqual(first["variant_digest"], second["variant_digest"])
        self.assertEqual(first["schema_version"], PLAN_VARIANT_SCHEMA_VERSION)
        self.assertEqual(first["prepared_state"], "prepared_not_observed")
        self.assertEqual(first["next_handoff"]["decision"], "undecided")
        self.assertTrue(first["next_handoff"]["requires_user_choice"])
        self.assertEqual([candidate["kind"] for candidate in first["next_handoff"]["candidates"]], ["parent_plan", "variant"])
        self.assertEqual(validate_plan_variant(first), [])

    def test_variant_inherits_only_reviewed_refs_and_routes_changed_context_to_reevaluation(self) -> None:
        variant = build_plan_variant(
            parent_artifact=_PARENT,
            name="policy-check",
            deltas=[build_plan_variant_delta(dimension="policy", label="data", parent_value="internal", variant_value="sensitive")],
            refs=[
                build_plan_variant_ref(kind="context_pack", ref="reviewed.json", reviewed=True),
                build_plan_variant_ref(kind="source", ref="unreviewed.md", reviewed=False),
            ],
        )

        self.assertEqual([ref["ref"] for ref in variant["inherited_refs"]], [_PARENT["path"], "reviewed.json"])
        self.assertEqual([ref["ref"] for ref in variant["refs_requiring_reevaluation"]], ["unreviewed.md"])
        self.assertEqual(variant["not_evidence_until_observed"], list(PLAN_VARIANT_NOT_OBSERVED))
        self.assertIn("not the accepted plan", PLAN_VARIANT_CLAIM_BOUNDARY)
        self.assertIn("dispatch", PLAN_VARIANT_CLAIM_BOUNDARY)
        self.assertEqual(validate_plan_variant(variant), [])
        rendered = render_plan_variant_text(variant)
        self.assertIn("Re-evaluate before any handoff:", rendered)
        self.assertIn("Which plan should become the next handoff", rendered)

    def test_terminology_capture_is_bounded_versioned_digest_metadata_not_instructions(self) -> None:
        source = (
            "# Project Terms\n\n"
            f"{PROJECT_TERMS_BOUNDARY}\n\n"
            "<!-- omj-project-terms/v1 -->\n\n"
            "## domain: delivery\n\n"
            "- term: `dispatch packet` = `handoff`\n"
            "  definition: A prepared package of coding work.\n"
            "  say-instead: prepared handoff\n"
            "  localized[ko]: 핸드오프\n"
            "  distinct-from: `dispatch` - observed execution.\n"
            "- workflow-hint: `ralplan`\n"
        ).encode()
        document = parse_project_terms(source)
        captures = build_project_terms_capture_inputs(document)

        self.assertEqual(document.schema_version, "omj-project-terms/v1")
        self.assertEqual(document.source_sha256, hashlib.sha256(source).hexdigest())
        self.assertEqual(captures[0].mappings, (("dispatch packet", "handoff"),))
        self.assertEqual(captures[0].workflow_hints, ("ralplan",))
        self.assertEqual(captures[0].source_ref, f"pt_sha256:{hashlib.sha256(source).hexdigest()}")
        self.assertEqual(captures[0].source_class, "omj_local")
        self.assertNotIn("approval", json.dumps(captures[0].__dict__).lower())
        self.assertIn("not agent instructions", PROJECT_TERMS_BOUNDARY)
        self.assertIn("routing rules", PROJECT_TERMS_BOUNDARY)

        with self.assertRaisesRegex(ProjectTermsParseError, "invalid_project_terms_version_marker"):
            parse_project_terms(source.replace(b"omj-project-terms/v1", b"omh-project-terms/v2"))


_FIXTURE_CONTRACTS = {
    "permitting-model": {
        "data_handling": {"training_use": "excluded", "retention": "bounded", "account_scope": "published default; not account-level evidence"}
    },
    "trains-model": {
        "data_handling": {"training_use": "included", "retention": "bounded", "account_scope": "published default; not account-level evidence"}
    },
    "retains-model": {
        "data_handling": {"training_use": "excluded", "retention": "indefinite", "account_scope": "published default; not account-level evidence"}
    },
    "unread-model": {
        "data_handling": {"training_use": "not_recorded", "retention": "not_recorded", "account_scope": "published default; not account-level evidence"}
    },
    "no-axis-model": {},
}


class RequestComplexityAndModelVerdictTests(unittest.TestCase):
    def test_complexity_is_offline_explainable_and_missing_chain_never_invents_a_model(self) -> None:
        heavy = score_request_complexity(
            "Audit every usage across all services, migrate the schema, preserve compatibility, and verify each package."
        )
        self.assertEqual(heavy["tier"], "deep")
        self.assertEqual(heavy["score"], sum(signal["weight"] for signal in heavy["signals"]))
        self.assertTrue(all(signal["evidence"] and signal["describe"] for signal in heavy["signals"]))
        recommendation = recommend_model_for_complexity(heavy)
        self.assertEqual(recommendation["chain_status"], "no_chain_config")
        self.assertEqual(recommendation["resolved"], {})
        self.assertEqual(recommendation["model_class"], COMPLEXITY_TIER_MODEL_CLASSES["deep"])

        vague = score_request_complexity("help")
        vague_recommendation = recommend_model_for_complexity(vague, chains={"deep": (("heavy-model", "high"),)})
        self.assertEqual(vague_recommendation["chain_status"], "class_not_in_chains")
        self.assertEqual(vague_recommendation["resolved"], {})
        self.assertIn(vague_recommendation["reasoning_effort"], tuple(COMPLEXITY_TIER_EFFORTS.values()))

    def test_sensitive_verdicts_distinguish_permitting_conflicting_and_unknown_policy(self) -> None:
        cases = (
            ("permitting-model", VERDICT_PERMITTING, "documented_default_permits"),
            ("trains-model", VERDICT_CONFLICTING, REASON_TRAINING_USE_INCLUDES),
            ("retains-model", VERDICT_CONFLICTING, REASON_RETENTION_INDEFINITE),
            ("unread-model", VERDICT_UNKNOWN, REASON_POLICY_NOT_RECORDED),
            ("no-axis-model", VERDICT_UNKNOWN, REASON_AXIS_NOT_DECLARED),
            ("missing-model", VERDICT_UNKNOWN, REASON_NO_DOCUMENTED_CONTRACT),
        )
        for model, verdict, reason in cases:
            with self.subTest(model=model):
                result = model_data_handling_verdict(model, contracts=_FIXTURE_CONTRACTS)
                self.assertEqual((result["verdict"], result["reason"]), (verdict, reason))
                self.assertTrue(result["reason_text"])

        report = data_handling_filtered_chain(
            ("trains-model", "permitting-model", "unread-model", "missing-model"),
            work_is_sensitive=True,
            contracts=_FIXTURE_CONTRACTS,
        )
        self.assertIn("not account", report["claim_boundary"])
        self.assertEqual(report["summary"]["excluded_conflicting_policy"], 1)
        self.assertEqual(report["summary"]["excluded_unknown_policy"], 2)
        self.assertIn("account", report["claim_boundary"])

    def test_model_coverage_separates_exact_inherited_and_unknown_without_served_claims(self) -> None:
        inventory = {
            "models": [
                {"model_id": "gpt-6-sol", "provider": "fixture-provider", "source": "fixture", "status": "observed"},
                {"model_id": "deepseek-flash", "provider": "fixture-provider", "source": "fixture", "status": "cold"},
            ],
            "inventory_status": "observed",
            "provenance": {"source": "fixture_inventory", "digest": "fixture_digest"},
        }
        report = build_model_contract_coverage(
            inventory,
            required_models=("gpt-6-sol", "deepseek-flash", "unknown-model"),
        )
        rows = {row["requested_model"]: row for row in report["comparison"]["models"]}

        self.assertEqual(report["schema_version"], MODEL_CONTRACT_COVERAGE_SCHEMA_VERSION)
        self.assertEqual(report["comparison"]["summary"]["outcome"], "required_gaps")
        self.assertIn(rows["deepseek-flash"]["status"], {"declared_inheritance", "dated_snapshot", "exact"})
        self.assertEqual(rows["unknown-model"]["status"], "missing")
        self.assertEqual(rows["unknown-model"]["actionability"], "required_missing")
        self.assertEqual(coverage_exit_code(report), 1)
        self.assertIn("not evidence of provider availability", report["claim_boundary"])
        self.assertNotIn("selected_owner", json.dumps(report))
        self.assertNotIn("router", json.dumps(report).lower())

    def test_model_coverage_and_sensitive_verdicts_are_network_free_and_not_execution_evidence(self) -> None:
        def refuse(*args: object, **kwargs: object) -> None:
            raise AssertionError("offline coverage reached a network or paid model boundary")

        with (
            mock.patch.object(subprocess, "run", refuse),
            mock.patch.object(subprocess, "Popen", refuse),
            mock.patch.object(socket, "socket", refuse),
        ):
            report = build_model_contract_coverage({"models": ["unknown-model"], "inventory_status": "cold"})
            verdict = model_data_handling_verdict("unknown-model")

        self.assertEqual(report["comparison"]["summary"]["outcome"], "cold_inventory")
        self.assertEqual(verdict["verdict"], VERDICT_UNKNOWN)
        self.assertIn("not evidence", report["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
