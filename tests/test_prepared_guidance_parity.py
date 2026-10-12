from __future__ import annotations

from dataclasses import asdict, is_dataclass
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from typing import Any, Mapping

from omj.skills import prepared



REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "src" / "skills" / "prepared_sources.json"


def _manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
EXPECTED_MEMBER_IDS = frozenset(
    {
        "accessibility-audit",
        "adversarial-consensus",
        "agent-debug",
        "agent-evaluation",
        "failure-signal-audit",
        "agent-instructions",
        "app-debugging",
        "native-debugging",
        "build-failure-triage",
        "apple-design",
        "design-orchestration",
        "design-quality-gate",
        "award-bar-score",
        "frontend",
        "visual-qa",
        "application-threat-model",
        "security-safety-review",
        "security-event-response",
        "connector-operator",
        "browser-operator",
        "workspace-file-operator",
        "command-operator",
        "live-info-operator",
        "media-input-operator",
        "content-operator",
        "buzz",
        "model-setup",
        "websearch-setup",
        "parallel-tools",
        "morning-brief",
        "capability-toggle",
        "backend",
        "relational-db",
        "codebase-onboarding",
        "codebase-uml",
        "commit-pr-authoring",
        "git-workflow",
        "context-budget-review",
        "run-efficiency",
        "harness-session-inventory",
        "curriculum-design",
        "data-analysis",
        "data-pipelines",
        "decision-prototype",
        "decision-recall",
        "memory-sync",
        "product-docs",
        "external-connector-readiness",
        "provider-profile-posture",
        "physical-device-readiness",
        "prompt-import-readiness",
        "finance-analysis",
        "frontend-refactor",
        "refactor-plan",
        "tech-debt-audit",
        "github-issue-intake",
        "iac-change",
        "inference-serving",
        "instinct-ledger",
        "internal-audit",
        "jev-action-check",
        "jev-ask",
        "jev-done-check",
        "jev-failure-triage",
        "jev-review-gate",
        "jev-route",
        "jit-learn",
        "legal-compliance-review",
        "lifecycle-growth",
        "live-incident-response",
        "llm-app-dev",
        "localization-review",
        "long-document-reading",
        "model-optimization",
        "mobile-release",
        "model-finetuning",
        "people-ops",
        "product-brief",
        "product-discovery-validation",
        "production-audit",
        "release-cut",
        "rules-distill",
        "running-work-board",
        "rust",
        "sales-development",
        "sales-pipeline-review",
        "skill-health",
        "skill-scout",
        "support-operations",
        "todo-checklist",
        "verification-gate",
        "workspace-audit",
        "context",
        "maestro",
        "ultraperf",
        "research",
        "achievements",
        "meta-router",
    }
)

JEV_MEMBER_IDS = frozenset(
    {
        "jev-action-check",
        "jev-ask",
        "jev-done-check",
        "jev-failure-triage",
        "jev-review-gate",
        "jev-route",
    }
)

REQUIRED_MEMBER_FIELDS = (
    "canonical_id",
    "family_id",
    "description",
    "triggers",
    "category",
    "phase",
    "role",
    "source_folder",
    "source_path",
    "source_sha256",
    "required_inputs",
    "expected_outputs",
    "artifact_expectations",
    "acceptance_criteria",
    "handoff_policy",
    "catalog_rules",
    "local_contract_ids",
    "references",
    "source_gaps",
    "blocked_prerequisites",
    "evidence_boundary",
)
REQUIRED_REFERENCE_FIELDS = ("relative_path", "content", "source_path", "source_sha256")
NONEMPTY_MEMBER_FIELDS = frozenset(REQUIRED_MEMBER_FIELDS) - {"local_contract_ids", "references", "source_gaps", "blocked_prerequisites"}


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "skill_name") and hasattr(value, "relative_path") and hasattr(value, "content"):
        return {"skill_name": value.skill_name, "relative_path": value.relative_path, "content": value.content}
    if isinstance(value, Mapping):
        return dict(value)

def _members(index: Any) -> list[dict[str, Any]]:
    if isinstance(index, Mapping):
        if isinstance(index.get("entries"), (list, tuple)):
            return [_mapping(value) for value in index["entries"]]
        records = []
        for key, value in index.items():
            record = _mapping(value)
            if record:
                record.setdefault("canonical_id", key)
                records.append(record)
        return records
    return [_mapping(value) for value in index]


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, frozenset, dict)):
        return bool(value)
    return value is not None


class PreparedGuidanceParityTests(unittest.TestCase):
    def test_index_contains_exactly_the_frozen_98_member_ids_once(self) -> None:
        manifest = _manifest()
        self.assertEqual(manifest["schema_version"], "prepared_guidance_source_manifest/v1")
        self.assertEqual(manifest["source_commit"], "117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c")
        self.assertEqual(manifest["counts"], {"members": 98, "families": 60, "method_references": 97, "source_contracts": 41, "unique_source_paths": 138})
        self.assertEqual(manifest["counts"]["members"], 98)
        index = prepared.prepared_guidance_index()
        self.assertEqual(index["schema_version"], "prepared_guidance_index/v1")
        self.assertEqual(index["source_commit"], manifest["source_commit"])
        self.assertTrue(index["prepared_not_observed"])
        self.assertEqual(index["member_count"], 98)
        self.assertEqual(index["family_count"], 60)
        records = _members(index)
        ids = [record.get("canonical_id") for record in records]
        self.assertEqual(len(ids), 98)
        self.assertEqual(len(set(ids)), 98)
        self.assertEqual(set(ids), EXPECTED_MEMBER_IDS)
        for record in records:
            with self.subTest(index_member=record.get("canonical_id")):
                self.assertTrue(_nonempty(record.get("source_status")))
                self.assertTrue(_nonempty(record.get("reference_path")))

        for canonical_id in EXPECTED_MEMBER_IDS:
            with self.subTest(canonical_id=canonical_id):
                member = _mapping(prepared.prepared_guidance_member(canonical_id))
                self.assertEqual(member.get("canonical_id"), canonical_id)
                self.assertTrue(member["prepared_not_observed"])
                self.assertTrue(_nonempty(member.get("source_status")))
                self.assertTrue(_nonempty(member.get("reference_path")))

    def test_prepared_catalog_is_additive_to_existing_builtin_definitions(self) -> None:
        from omj.skills import builtin_definitions

        definitions = list(builtin_definitions())
        self.assertEqual(len(definitions), 50)
        definition_ids = [getattr(definition, "canonical_id", getattr(definition, "name", None)) for definition in definitions]
        self.assertEqual(len(set(definition_ids)), 50)

    def test_member_records_preserve_source_contract_and_acceptance_outcomes(self) -> None:
        for record in (_mapping(prepared.prepared_guidance_member(canonical_id)) for canonical_id in EXPECTED_MEMBER_IDS):
            canonical_id = record.get("canonical_id")
            with self.subTest(canonical_id=canonical_id):
                self.assertGreaterEqual(set(record), set(REQUIRED_MEMBER_FIELDS))
                for field in NONEMPTY_MEMBER_FIELDS:
                    self.assertTrue(_nonempty(record[field]), f"{canonical_id}: empty {field}")
                self.assertIsInstance(record["acceptance_criteria"], (list, tuple))
                self.assertGreaterEqual(len(record["acceptance_criteria"]), 1)
                self.assertIsInstance(record["local_contract_ids"], (list, tuple, set, frozenset))
                self.assertIsInstance(record["references"], (list, tuple))
                boundary = str(record["evidence_boundary"]).lower()
                self.assertRegex(boundary, r"prepared|not[_ -]?observed|no[_ -]?execution")

    def test_source_metadata_and_reference_content_match_frozen_manifest(self) -> None:
        manifest_members = _manifest()["members"]
        records = {record["canonical_id"]: record for record in (_mapping(prepared.prepared_guidance_member(canonical_id)) for canonical_id in manifest_members)}
        self.assertEqual(set(records), set(manifest_members))
        for canonical_id, manifest_record in manifest_members.items():
            record = _mapping(prepared.prepared_guidance_member(canonical_id))
            with self.subTest(canonical_id=canonical_id):
                self.assertEqual(record["family_id"], manifest_record["family_id"])
                self.assertEqual(record["source_path"], manifest_record["source_path"])
                self.assertEqual(record["source_sha256"], manifest_record["source_sha256"])
                self.assertEqual(record["expected_outputs"], manifest_record["expected_outputs"])
                self.assertEqual(record["acceptance_criteria"], manifest_record["acceptance_criteria"])
                self.assertTrue(str(record["source_path"]).startswith("skills/"))
                self.assertFalse(Path(str(record["source_path"])).is_absolute())
                refs = [_mapping(reference) for reference in record["references"]]
                self.assertEqual(
                    [(ref["relative_path"], ref["source_path"], ref["source_sha256"]) for ref in refs],
                    [(ref["relative_path"], ref["source_path"], ref["source_sha256"]) for ref in manifest_record["references"]],
                )
                for ref in refs:
                    self.assertEqual(hashlib.sha256(str(ref["content"]).encode("utf-8")).hexdigest(), ref["source_sha256"])
                    self.assertFalse(Path(str(ref["source_path"])).is_absolute())

    def test_member_reference_templates_are_installed_byte_for_byte(self) -> None:
        templates = prepared.prepared_guidance_reference_templates()
        template_records = [_mapping(template) for template in templates]
        for template in template_records:
            with self.subTest(relative_path=template.get("relative_path")):
                self.assertEqual(set(template), {"skill_name", "relative_path", "content"})
                relative_path = str(template["relative_path"])
                self.assertFalse(Path(relative_path).is_absolute())
                self.assertNotIn("..", Path(relative_path).parts)
                installed_path = REPO_ROOT / "skills" / "oh-my-jeo" / relative_path
                self.assertTrue(installed_path.is_file(), installed_path)
                self.assertEqual(installed_path.read_text(encoding="utf-8"), str(template["content"]))

    def test_reference_templates_route_members_and_real_methods(self) -> None:
        templates = tuple(_mapping(template) for template in prepared.prepared_guidance_reference_templates())
        by_path = {str(template["relative_path"]): template for template in templates}
        self.assertEqual(len(by_path), len(templates))
        contract_paths = [path for path in by_path if path.startswith("references/prepared/") and path.count("/") == 3]
        self.assertEqual(len(contract_paths), 98)

        records = {record["canonical_id"]: record for record in (_mapping(prepared.prepared_guidance_member(canonical_id)) for canonical_id in EXPECTED_MEMBER_IDS)}
        for canonical_id, record in records.items():
            expected_path = f"references/prepared/{record['family_id']}/{canonical_id}.md"
            with self.subTest(canonical_id=canonical_id):
                self.assertIn(expected_path, by_path)
                content = str(by_path[expected_path]["content"])
                self.assertIn(canonical_id, content)
                self.assertIn(str(record["family_id"]), content)
                self.assertIn(str(record["evidence_boundary"]), content)
                self.assertNotRegex(content, r"(?i)(lorem ipsum|coming soon|generic placeholder)")

        for canonical_id, manifest_record in _manifest()["members"].items():
            for reference in manifest_record["references"]:
                target = f"references/prepared/{manifest_record['family_id']}/{canonical_id}/{reference['relative_path']}"
                with self.subTest(method_target=target):
                    self.assertIn(target, by_path)
                    content = str(by_path[target]["content"])
                    self.assertEqual(hashlib.sha256(content.encode("utf-8")).hexdigest(), reference["source_sha256"])

    def test_jev_members_disclose_missing_procedure_without_fabricating_provider(self) -> None:
        records = {record["canonical_id"]: record for record in (_mapping(prepared.prepared_guidance_member(canonical_id)) for canonical_id in EXPECTED_MEMBER_IDS)}
        for canonical_id in JEV_MEMBER_IDS:
            record = records[canonical_id]
            serialized = json.dumps(record, sort_keys=True)
            with self.subTest(canonical_id=canonical_id):
                self.assertRegex(serialized, r"(?i)procedure\.md")
                self.assertRegex(serialized, r"(?i)(absent|missing|not available|not found)")
                self.assertNotRegex(serialized, r"(?i)provider\s+(?:exists|available|configured|present)")
                for reference in record["references"]:
                    self.assertNotRegex(
                        str(_mapping(reference)["relative_path"]),
                        r"(?i)(^|/)procedure\.md$",
                    )
                self.assertRegex(str(record["evidence_boundary"]), r"(?i)not[_ -]?observed|prepared|no[_ -]?execution")
    def test_unknown_duplicate_path_and_missing_source_refs_are_rejected(self) -> None:
        original = getattr(prepared, "PREPARED_MEMBERS")
        records = list(original)
        source_record = next(_mapping(record) for record in records if _mapping(record)["references"])
        broken_reference = _mapping(source_record["references"][0])
        broken_reference.pop("source_path", None)
        broken_record = dict(source_record)
        broken_record["references"] = [broken_reference]
        malformed_cases = (
            ("unknown member", records + [{"canonical_id": "not-in-audit"}], r"unknown|canonical"),
            ("duplicate member", records + [records[0]], r"duplicate"),
            (
                "member path traversal",
                [dict(_mapping(records[0]), source_path="../../outside.py")] + records[1:],
                r"source_path|path|upstream",
            ),
            (
                "reference path traversal",
                [dict(_mapping(records[0]), references=[dict(_mapping(records[0]["references"][0]), relative_path="../outside.md")])] + records[1:],
                r"reference|path|traversal",
            ),
            (
                "missing source reference",
                [broken_record] + records[1:],
                r"reference|source",
            ),
        )
        for case_name, malformed, message in malformed_cases:
            with self.subTest(case_name=case_name):
                with patch.object(prepared, "PREPARED_MEMBERS", malformed):
                    with self.assertRaisesRegex(ValueError, message):
                        prepared.prepared_guidance_index()

    def test_missing_member_lookup_is_rejected_without_path_resolution(self) -> None:
        with self.assertRaisesRegex((KeyError, ValueError), r"unknown|not found|member"):
            prepared.prepared_guidance_member("../outside")


if __name__ == "__main__":
    unittest.main()
