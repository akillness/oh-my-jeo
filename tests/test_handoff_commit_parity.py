from __future__ import annotations

import json
import unittest

from _local_package import load_local_package

load_local_package()

from omj.coding.coding_delegation import build_coding_delegation_payload
from omj.coding.commit_planning import (
    COMMIT_PLAN_SCHEMA_VERSION,
    ChangedFile,
    CommitPlanError,
    build_commit_plan,
    parse_status_porcelain_z,
)
from omj.coding.handoff_contract import (
    HANDOFF_CONTRACT_RECEIPT_SCHEMA_VERSION,
    HANDOFF_CONTRACT_SCHEMA_VERSION,
    HandoffContractError,
    build_handoff_contract,
    build_handoff_contract_receipt,
    contract_digest,
    contract_verification_observed,
    contract_verification_summary,
    handoff_contract_errors,
    require_valid_handoff_contract,
)


CODING_TASK = "risky refactor"
FORBIDDEN = "Push to the default branch or force-push any shared branch."


def declaration(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "inputs": [{"name": "test_path", "input_type": "file", "requirement": "required"}],
        "postconditions": [
            {"id": "parser-tests", "command": "PYTHONPATH=tests python -m unittest {test_path}"},
            {"id": "compile", "command": "python -m compileall -q src"},
        ],
        "forbidden_actions": [FORBIDDEN],
        "output_shape": {"format": "json", "required_fields": ["status", "changed_files"]},
    }
    value.update(overrides)
    return value


def handoff_of(payload: dict[str, object]) -> dict[str, object]:
    for key in ("executor_handoff", "prompt_handoff", "runtime_handoff"):
        handoff = payload.get(key)
        if isinstance(handoff, dict):
            return handoff
    raise AssertionError("payload carries no prepared handoff")


def all_planned_paths(plan: dict[str, object]) -> list[str]:
    return sorted(
        path
        for commit in plan["commits"]  # type: ignore[index]
        for path in commit["files"]  # type: ignore[union-attr]
    )


class HandoffContractTests(unittest.TestCase):
    def test_typed_inputs_and_postconditions_compile_with_stable_ids(self) -> None:
        typed_inputs = [
            {"name": "test_path", "input_type": "file", "requirement": "required"},
            {"name": "attempts", "input_type": "number", "requirement": "required"},
        ]
        first = build_handoff_contract(declaration(inputs=typed_inputs))
        second = build_handoff_contract(declaration(inputs=typed_inputs))

        self.assertEqual(first["schema_version"], HANDOFF_CONTRACT_SCHEMA_VERSION)
        self.assertEqual(first["status"], "prepared_not_observed")
        self.assertEqual(
            [(entry["name"], entry["input_type"]) for entry in first["inputs"]],
            [("message", "string"), ("test_path", "file"), ("attempts", "number")],
        )
        self.assertEqual([entry["id"] for entry in first["postconditions"]], ["parser-tests", "compile"])
        self.assertEqual(
            [entry["check_id"] for entry in first["postconditions"]],
            [entry["check_id"] for entry in second["postconditions"]],
        )
        self.assertNotEqual(
            first["postconditions"][0]["check_id"],  # type: ignore[index]
            build_handoff_contract(
                declaration(
                    postconditions=[
                        {"id": "parser-tests", "command": "python -m unittest {test_path}"},
                        {"id": "compile", "command": "python -m compileall -q src"},
                    ]
                )
            )["postconditions"][0]["check_id"],  # type: ignore[index]
        )
        self.assertEqual(first["forbidden_actions"], [FORBIDDEN])
        self.assertEqual(first["output_shape"], {"format": "json", "required_fields": ["status", "changed_files"]})

    def test_closed_declarations_and_template_variables_refuse_by_name(self) -> None:
        with self.assertRaises(HandoffContractError) as unknown:
            build_handoff_contract(declaration(unexpected="nope"))
        self.assertIn("unexpected", str(unknown.exception))
        with self.assertRaises(HandoffContractError) as bad_type:
            build_handoff_contract(
                declaration(inputs=[{"name": "target", "input_type": "path", "requirement": "required"}])
            )
        self.assertIn("target", str(bad_type.exception))

        with self.assertRaises(HandoffContractError) as duplicate_message:
            build_handoff_contract(declaration(inputs=[{"name": "message", "input_type": "string"}]))
        self.assertIn("message", str(duplicate_message.exception))

        contract = build_handoff_contract(declaration(inputs=[{"name": "test_path", "input_type": "file"}]))
        unused = {
            "handoff_contract": contract,
            "prompt_template": "Task: {message}; run {test_path}",
        }
        self.assertEqual(handoff_contract_errors(unused), [])
        unused["prompt_template"] = "Task: {message}"
        with self.assertRaises(HandoffContractError) as unused_error:
            require_valid_handoff_contract(unused)
        self.assertIn("'test_path' is declared but no handoff template uses it", str(unused_error.exception))

        undeclared = {
            "handoff_contract": contract,
            "prompt_template": "Task: {message}; run {test_path}; branch {branch}",
        }
        with self.assertRaises(HandoffContractError) as undeclared_error:
            require_valid_handoff_contract(undeclared)
        self.assertIn("template variable 'branch' has no input declaration", str(undeclared_error.exception))

    def test_receipts_require_integer_declared_statuses_and_preserve_observation_boundary(self) -> None:
        contract = build_handoff_contract(declaration())
        for bad in (True, "0", "tests passed"):
            with self.subTest(bad=bad):
                with self.assertRaises(HandoffContractError) as caught:
                    build_handoff_contract_receipt(contract, {"parser-tests": bad, "compile": 0})
                self.assertIn("'parser-tests' exit status must be an integer", str(caught.exception))

        with self.assertRaises(HandoffContractError) as unknown:
            build_handoff_contract_receipt(contract, {"unknown": 0})
        self.assertIn("unknown", str(unknown.exception))

        missing = build_handoff_contract_receipt(contract, {})
        self.assertEqual(
            (missing["status"], missing["verdict"], missing["unobserved_postconditions"]),
            ("prepared_not_observed", "not_observed", ["parser-tests", "compile"]),
        )
        failed = build_handoff_contract_receipt(contract, {"parser-tests": 1, "compile": 0})
        self.assertEqual((failed["status"], failed["verdict"]), ("observed", "failed"))
        passed = build_handoff_contract_receipt(contract, {"parser-tests": 0, "compile": 0})
        self.assertEqual((passed["status"], passed["verdict"]), ("observed", "passed"))
        self.assertTrue(contract_verification_observed(contract, passed))

    def test_receipt_digest_binds_contract_and_changed_contract_cannot_verify(self) -> None:
        contract = build_handoff_contract(declaration())
        receipt = build_handoff_contract_receipt(contract, {"parser-tests": 0, "compile": 0})
        changed = build_handoff_contract(
            declaration(forbidden_actions=["Never rewrite the release tag."])
        )

        self.assertEqual(receipt["schema_version"], HANDOFF_CONTRACT_RECEIPT_SCHEMA_VERSION)
        self.assertEqual(receipt["contract_digest"], contract_digest(contract))
        self.assertNotEqual(contract_digest(contract), contract_digest(changed))
        self.assertFalse(contract_verification_observed(changed, receipt))
        self.assertEqual(
            contract_verification_summary(changed, receipt),
            {
                "schema_version": HANDOFF_CONTRACT_SCHEMA_VERSION,
                "status": "prepared_not_observed",
                "verdict": "not_observed",
                "reason": "no_exit_status_recorded",
                "unobserved_postconditions": ["parser-tests", "compile"],
            },
        )

    def test_delegation_without_contract_preserves_existing_handoff_bytes(self) -> None:
        first = build_coding_delegation_payload(CODING_TASK, executor_target="codex")
        second = build_coding_delegation_payload(CODING_TASK, executor_target="codex")
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        handoff = handoff_of(first)
        self.assertNotIn("handoff_contract", handoff)
        self.assertNotIn("Forbidden:", str(handoff["prompt_template"]))
        self.assertNotIn("Postcondition `", str(handoff["prompt_template"]))

    def test_delegation_contract_reaches_executor_prompt_not_only_metadata(self) -> None:
        payload = build_coding_delegation_payload(
            CODING_TASK,
            executor_target="codex",
            handoff_contract=declaration(),
        )
        handoff = handoff_of(payload)
        prompt = str(handoff["prompt_template"])
        self.assertIn(f"- Forbidden: {FORBIDDEN}", prompt)
        self.assertIn("Postcondition `parser-tests`: run", prompt)
        self.assertIn("Postcondition `compile`: run", prompt)
        self.assertIn("status", prompt)
        self.assertIn("changed_files", prompt)
        self.assertEqual(handoff_contract_errors(handoff), [])


class CommitPlanningTests(unittest.TestCase):
    def test_porcelain_z_accepts_status_only_entries_and_preserves_rename_sides(self) -> None:
        payload = " M src/a.py\0R  src/new.py\0src/old.py\0?? notes with spaces.txt\0"
        files = parse_status_porcelain_z(payload)
        self.assertEqual(
            [(entry.path, entry.status, entry.renamed_from) for entry in files],
            [
                ("src/a.py", "M", None),
                ("src/new.py", "R", "src/old.py"),
                ("notes with spaces.txt", "?", None),
            ],
        )
        with self.assertRaises(CommitPlanError):
            parse_status_porcelain_z("not porcelain metadata\0")
        with self.assertRaises(CommitPlanError):
            parse_status_porcelain_z("R  src/new.py\0")

    def test_plan_has_complete_nonoverlapping_coverage_and_rejects_invalid_paths(self) -> None:
        files = [
            ChangedFile("src/app.py", "M"),
            ChangedFile("tests/test_unrelated.py", "M"),
            ChangedFile("docs/guide.md", "M"),
            ChangedFile("config.yaml", "M"),
            ChangedFile("package.json", "M"),
        ]
        original = list(files)
        plan = build_commit_plan(files)
        self.assertEqual(plan["schema_version"], COMMIT_PLAN_SCHEMA_VERSION)
        self.assertEqual(all_planned_paths(plan), sorted(entry.path for entry in files))
        self.assertEqual(plan["changed_file_count"], len(files))
        planned_paths = all_planned_paths(plan)
        self.assertEqual(len(planned_paths), len(set(planned_paths)))
        self.assertTrue(all(commit["rationale"] for commit in plan["commits"]))  # type: ignore[index]
        self.assertIn("not a commit", str(plan["claim_boundary"]))
        self.assertEqual(files, original)
        with self.assertRaises(CommitPlanError):
            build_commit_plan([ChangedFile("src/app.py", "M"), ChangedFile("src/app.py", "A")])
        with self.assertRaises(CommitPlanError):
            build_commit_plan([ChangedFile("", "M")])
        with self.assertRaises(CommitPlanError):
            build_commit_plan([ChangedFile(f"src/file-{index}.py", "M") for index in range(2001)])

    def test_planner_consumes_captured_metadata_without_filesystem_reads(self) -> None:
        plan = build_commit_plan([ChangedFile("path-that-does-not-exist/src.py", "M")])
        self.assertEqual(plan["changed_file_count"], 1)
        self.assertEqual(all_planned_paths(plan), ["path-that-does-not-exist/src.py"])

    def test_manifest_lockfiles_pair_and_groups_follow_fixed_order(self) -> None:
        files = [
            ChangedFile("config.yaml", "M"),
            ChangedFile("docs/guide.md", "M"),
            ChangedFile("tests/test_unrelated.py", "M"),
            ChangedFile("src/app.py", "M"),
            ChangedFile("package-lock.json", "M"),
            ChangedFile("package.json", "M"),
        ]
        plan = build_commit_plan(files)
        deps = [commit for commit in plan["commits"] if commit["category"] == "deps"]  # type: ignore[index]
        self.assertEqual(len(deps), 1)
        self.assertEqual(sorted(deps[0]["files"]), ["package-lock.json", "package.json"])
        self.assertEqual(
            [commit["category"] for commit in plan["commits"]],  # type: ignore[index]
            ["deps", "source", "tests", "docs", "config"],
        )

    def test_test_source_pairing_and_rename_manifest_are_preserved(self) -> None:
        plan = build_commit_plan(
            [
                ChangedFile("src/router.py", "R", renamed_from="src/old_router.py"),
                ChangedFile("tests/test_router.py", "M"),
            ]
        )
        source_commit = next(commit for commit in plan["commits"] if "src/router.py" in commit["files"])  # type: ignore[index]
        self.assertIn("tests/test_router.py", source_commit["files"])
        self.assertEqual(source_commit["renames"], {"src/router.py": "src/old_router.py"})

    def test_identical_inputs_are_byte_identical_and_reversed_inputs_are_not_a_mutation(self) -> None:
        files = [
            ChangedFile("src/b.py", "M"),
            ChangedFile("src/a.py", "M"),
            ChangedFile("docs/x.md", "M"),
        ]
        first = json.dumps(build_commit_plan(files), sort_keys=True, separators=(",", ":"))
        second = json.dumps(build_commit_plan(list(reversed(files))), sort_keys=True, separators=(",", ":"))
        self.assertEqual(first, second)
        self.assertEqual(files, [ChangedFile("src/b.py", "M"), ChangedFile("src/a.py", "M"), ChangedFile("docs/x.md", "M")])


if __name__ == "__main__":
    unittest.main()
