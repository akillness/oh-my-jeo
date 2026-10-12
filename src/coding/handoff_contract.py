"""Typed, executor-neutral contracts for prepared coding handoffs."""

from __future__ import annotations

import hashlib
import json
import re
import shlex
from typing import Any, Mapping, Sequence

HANDOFF_CONTRACT_SCHEMA_VERSION = "handoff_contract/v1"
HANDOFF_CONTRACT_RECEIPT_SCHEMA_VERSION = "handoff_contract_receipt/v1"
HANDOFF_CONTRACT_KEY = "handoff_contract"

INPUT_TYPES = ("string", "number", "boolean", "date", "file")
INPUT_REQUIREMENTS = ("required", "optional", "user_prompt")
OUTPUT_SHAPE_FORMATS = ("json", "markdown", "text")
TASK_INPUT_NAME = "message"
TASK_INPUT = {
    "name": TASK_INPUT_NAME,
    "input_type": "string",
    "requirement": "required",
    "default": None,
}

MAX_INPUTS = 16
MAX_POSTCONDITIONS = 16
MAX_FORBIDDEN_ACTIONS = 16
MAX_OUTPUT_FIELDS = 32
MAX_TEXT_CHARS = 300

HANDOFF_CONTRACT_CLAIM_BOUNDARY = (
    "A handoff contract declares typed inputs, postcondition commands, an output shape, and forbidden "
    "actions. It is prepared_not_observed until a receipt records an exit status for every postcondition; "
    "OMJ does not run the commands, and no wording in an executor report can stand in for an exit status."
)
HANDOFF_CONTRACT_RECEIPT_CLAIM_BOUNDARY = (
    "A handoff contract receipt records the exit status the executor or host reported for each declared "
    "postcondition. It is observed only when every postcondition has one, and passed only when every one is "
    "0. It is not review, CI, merge-readiness, or merge evidence."
)

_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")
_POSTCONDITION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
_TEMPLATE_VARIABLE_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
_ENV_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


class HandoffContractError(ValueError):
    """A declaration, rendered handoff, or receipt that fails validation."""


def build_handoff_contract(declaration: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize and validate a caller declaration into a v1 contract."""
    if not isinstance(declaration, Mapping):
        raise HandoffContractError("handoff_contract declaration must be a JSON object")
    known = {"inputs", "postconditions", "output_shape", "forbidden_actions"}
    unknown = sorted(str(key) for key in declaration if key not in known)
    if unknown:
        raise HandoffContractError(
            f"handoff_contract has unknown field(s): {', '.join(unknown)}"
        )
    contract: dict[str, Any] = {
        "schema_version": HANDOFF_CONTRACT_SCHEMA_VERSION,
        "status": "prepared_not_observed",
        "inputs": [dict(TASK_INPUT), *_inputs(declaration.get("inputs", []))],
        "postconditions": _postconditions(declaration.get("postconditions")),
        "forbidden_actions": _texts(
            declaration.get("forbidden_actions", []),
            "forbidden_actions",
            MAX_FORBIDDEN_ACTIONS,
        ),
        "claim_boundary": HANDOFF_CONTRACT_CLAIM_BOUNDARY,
    }
    output_shape = declaration.get("output_shape")
    if output_shape is not None:
        contract["output_shape"] = _output_shape(output_shape)
    return contract


def _inputs(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > MAX_INPUTS:
        raise HandoffContractError(
            f"handoff_contract inputs must be a list of at most {MAX_INPUTS} objects"
        )
    inputs: list[dict[str, Any]] = []
    seen = {TASK_INPUT_NAME}
    allowed = {"name", "input_type", "requirement", "default"}
    for index, entry in enumerate(value):
        if not isinstance(entry, Mapping):
            raise HandoffContractError(
                f"handoff_contract input at index {index} must be an object"
            )
        unknown = sorted(str(key) for key in entry if key not in allowed)
        if unknown:
            raise HandoffContractError(
                f"handoff_contract input at index {index} has unknown field(s): {', '.join(unknown)}"
            )
        name = entry.get("name")
        if not isinstance(name, str) or not _NAME_RE.fullmatch(name):
            raise HandoffContractError(
                f"handoff_contract input at index {index} has an invalid name: {name!r}"
            )
        if name in seen:
            reason = (
                "is supplied by OMJ" if name == TASK_INPUT_NAME else "is declared twice"
            )
            raise HandoffContractError(f"handoff_contract input {name!r} {reason}")
        seen.add(name)
        input_type = entry.get("input_type", "string")
        if input_type not in INPUT_TYPES:
            raise HandoffContractError(
                f"handoff_contract input {name!r} input_type must be one of {', '.join(INPUT_TYPES)}"
            )
        requirement = entry.get("requirement", "required")
        if requirement not in INPUT_REQUIREMENTS:
            raise HandoffContractError(
                f"handoff_contract input {name!r} requirement must be one of {', '.join(INPUT_REQUIREMENTS)}"
            )
        default = entry.get("default")
        if requirement == "optional" and default is None:
            raise HandoffContractError(
                f"handoff_contract optional input {name!r} must declare a default"
            )
        if requirement != "optional" and default is not None:
            raise HandoffContractError(
                f"handoff_contract {requirement} input {name!r} must not declare a default"
            )
        if default is not None and not _default_matches_type(default, str(input_type)):
            raise HandoffContractError(
                f"handoff_contract input {name!r} default does not match input_type {input_type!r}"
            )
        inputs.append(
            {
                "name": name,
                "input_type": input_type,
                "requirement": requirement,
                "default": default,
            }
        )
    return inputs


def _default_matches_type(value: object, input_type: str) -> bool:
    if input_type == "boolean":
        return isinstance(value, bool)
    if input_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, str)


def _postconditions(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value or len(value) > MAX_POSTCONDITIONS:
        raise HandoffContractError(
            f"handoff_contract postconditions must be a list of 1 to {MAX_POSTCONDITIONS} command objects"
        )
    commands: list[str] = []
    checks: list[dict[str, str]] = []
    allowed = {"id", "command"}
    for index, entry in enumerate(value):
        if not isinstance(entry, Mapping):
            raise HandoffContractError(
                f"handoff_contract postcondition at index {index} must be an object"
            )
        unknown = sorted(str(key) for key in entry if key not in allowed)
        if unknown:
            raise HandoffContractError(
                f"handoff_contract postcondition at index {index} has unknown field(s): {', '.join(unknown)}"
            )
        postcondition_id = entry.get("id")
        if not isinstance(postcondition_id, str) or not _POSTCONDITION_ID_RE.fullmatch(
            postcondition_id
        ):
            raise HandoffContractError(
                f"handoff_contract postcondition at index {index} has an invalid id: {postcondition_id!r}"
            )
        if any(check["id"] == postcondition_id for check in checks):
            raise HandoffContractError(
                f"handoff_contract postcondition {postcondition_id!r} is declared twice"
            )
        command = entry.get("command")
        if (
            not isinstance(command, str)
            or not command.strip()
            or len(command) > MAX_TEXT_CHARS
        ):
            raise HandoffContractError(
                f"handoff_contract postcondition {postcondition_id!r} command must be a non-empty string "
                f"of at most {MAX_TEXT_CHARS} chars"
            )
        normalized = " ".join(command.split())
        _parse_command(normalized, postcondition_id)
        commands.append(normalized)
        checks.append({"id": postcondition_id})
    compiled: list[dict[str, Any]] = []
    for index, (postcondition_id, command) in enumerate(
        zip((check["id"] for check in checks), commands)
    ):
        env, argv = _command_argv(command, postcondition_id)
        check_id = hashlib.sha256(
            json.dumps(
                [
                    HANDOFF_CONTRACT_SCHEMA_VERSION,
                    "postconditions",
                    index,
                    argv,
                    sorted(env.items()),
                ],
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:16]
        compiled.append(
            {
                "id": postcondition_id,
                "check_id": check_id,
                "command": command,
                "claim_scope": "unit_verification",
                "verdict_source": "exit_status",
            }
        )
    return compiled


def _parse_command(command: str, postcondition_id: str) -> None:
    try:
        _command_argv(command, postcondition_id)
    except HandoffContractError:
        raise


def _command_argv(
    command: str, postcondition_id: str
) -> tuple[dict[str, str], list[str]]:
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        raise HandoffContractError(
            f"handoff_contract postcondition {postcondition_id!r} command is not parseable: {exc}"
        ) from exc
    env: dict[str, str] = {}
    while tokens and _ENV_ASSIGNMENT_RE.fullmatch(tokens[0].split("=", 1)[0] + "="):
        name, _, value = tokens.pop(0).partition("=")
        env[name] = value
    if not tokens:
        raise HandoffContractError(
            f"handoff_contract postcondition {postcondition_id!r} command must name a program to run"
        )
    return env, tokens


def _texts(value: object, field: str, limit: int) -> list[str]:
    if not isinstance(value, list) or len(value) > limit:
        raise HandoffContractError(
            f"handoff_contract {field} must be a list of at most {limit} strings"
        )
    texts: list[str] = []
    for index, entry in enumerate(value):
        if (
            not isinstance(entry, str)
            or not entry.strip()
            or len(entry) > MAX_TEXT_CHARS
        ):
            raise HandoffContractError(
                f"handoff_contract {field} entry at index {index} must be a non-empty string "
                f"of at most {MAX_TEXT_CHARS} chars"
            )
        texts.append(" ".join(entry.split()))
    return texts


def _output_shape(value: object) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise HandoffContractError("handoff_contract output_shape must be an object")
    allowed = {"format", "required_fields"}
    unknown = sorted(str(key) for key in value if key not in allowed)
    if unknown:
        raise HandoffContractError(
            f"handoff_contract output_shape has unknown field(s): {', '.join(unknown)}"
        )
    output_format = value.get("format", "json")
    if output_format not in OUTPUT_SHAPE_FORMATS:
        raise HandoffContractError(
            f"handoff_contract output_shape format must be one of {', '.join(OUTPUT_SHAPE_FORMATS)}"
        )
    fields = value.get("required_fields")
    if not isinstance(fields, list) or not fields or len(fields) > MAX_OUTPUT_FIELDS:
        raise HandoffContractError(
            f"handoff_contract output_shape required_fields must list 1 to {MAX_OUTPUT_FIELDS} field names"
        )
    for field in fields:
        if not isinstance(field, str) or not _NAME_RE.fullmatch(field):
            raise HandoffContractError(
                f"handoff_contract output_shape has an invalid field name: {field!r}"
            )
    if len(set(fields)) != len(fields):
        raise HandoffContractError(
            "handoff_contract output_shape required_fields must not repeat a field"
        )
    return {"format": output_format, "required_fields": list(fields)}


def handoff_templates(handoff: Mapping[str, Any]) -> list[str]:
    templates = [str(handoff.get("prompt_template", ""))]
    for key in ("invocation", "codex_invocation"):
        invocation = handoff.get(key)
        if isinstance(invocation, Mapping):
            templates.append(str(invocation.get("dispatch_text_template", "")))
    return [template for template in templates if template]


def template_variables(templates: Sequence[str]) -> list[str]:
    return sorted(
        {
            match
            for template in templates
            for match in _TEMPLATE_VARIABLE_RE.findall(template)
        }
    )


def handoff_contract_errors(handoff: Mapping[str, Any]) -> list[str]:
    contract = handoff.get(HANDOFF_CONTRACT_KEY)
    if contract is None:
        return []
    if (
        not isinstance(contract, Mapping)
        or contract.get("schema_version") != HANDOFF_CONTRACT_SCHEMA_VERSION
    ):
        return [
            f"handoff_contract schema_version must be {HANDOFF_CONTRACT_SCHEMA_VERSION}"
        ]
    raw_inputs = contract.get("inputs")
    declared = [
        str(entry.get("name"))
        for entry in (raw_inputs if isinstance(raw_inputs, list) else [])
        if isinstance(entry, Mapping)
    ]
    used = template_variables(handoff_templates(handoff))
    errors = [
        f"handoff_contract input {name!r} is declared but no handoff template uses it"
        for name in declared
        if name not in used
    ]
    errors.extend(
        f"handoff_contract template variable {name!r} has no input declaration"
        for name in used
        if name not in declared
    )
    return errors


def require_valid_handoff_contract(handoff: Mapping[str, Any]) -> None:
    errors = handoff_contract_errors(handoff)
    if errors:
        raise HandoffContractError("; ".join(errors))


def contract_digest(contract: Mapping[str, Any]) -> str:
    canonical = json.dumps(contract, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_handoff_contract_receipt(
    contract: Mapping[str, Any], exit_statuses: Mapping[str, object]
) -> dict[str, Any]:
    if not isinstance(exit_statuses, Mapping):
        raise HandoffContractError(
            "exit statuses must be a mapping keyed by declared postcondition id"
        )
    postconditions = [
        entry
        for entry in contract.get("postconditions", [])
        if isinstance(entry, Mapping)
    ]
    declared_ids = [str(entry.get("id")) for entry in postconditions]
    unknown = sorted(str(key) for key in exit_statuses if key not in declared_ids)
    if unknown:
        raise HandoffContractError(
            f"exit status recorded for undeclared postcondition(s): {', '.join(unknown)}"
        )
    rows: list[dict[str, Any]] = []
    for entry in postconditions:
        postcondition_id = str(entry.get("id"))
        exit_status = exit_statuses.get(postcondition_id)
        if exit_status is not None and (
            isinstance(exit_status, bool) or not isinstance(exit_status, int)
        ):
            raise HandoffContractError(
                f"postcondition {postcondition_id!r} exit status must be an integer, got {exit_status!r}"
            )
        status = (
            "not_observed"
            if exit_status is None
            else ("passed" if exit_status == 0 else "failed")
        )
        rows.append(
            {
                "id": postcondition_id,
                "check_id": str(entry.get("check_id", "")),
                "exit_status": exit_status,
                "status": status,
            }
        )
    unobserved = [row["id"] for row in rows if row["status"] == "not_observed"]
    observed = bool(rows) and not unobserved
    verdict = (
        "failed"
        if any(row["status"] == "failed" for row in rows)
        else ("passed" if observed else "not_observed")
    )
    return {
        "schema_version": HANDOFF_CONTRACT_RECEIPT_SCHEMA_VERSION,
        "contract_digest": contract_digest(contract),
        "status": "observed" if observed else "prepared_not_observed",
        "verdict": verdict,
        "verdict_source": "exit_status",
        "postconditions": rows,
        "unobserved_postconditions": unobserved,
        "claim_boundary": HANDOFF_CONTRACT_RECEIPT_CLAIM_BOUNDARY,
    }


def _receipt_rows_match_contract(
    contract: Mapping[str, Any], receipt: Mapping[str, Any]
) -> bool:
    expected = [
        entry
        for entry in contract.get("postconditions", [])
        if isinstance(entry, Mapping)
    ]
    rows = receipt.get("postconditions")
    if not isinstance(rows, list) or len(rows) != len(expected):
        return False
    if any(
        not isinstance(row, Mapping) or not isinstance(row.get("id"), str)
        for row in rows
    ):
        return False
    expected_ids = {str(entry.get("id")) for entry in expected}
    row_ids = [row["id"] for row in rows]
    if len(set(row_ids)) != len(row_ids) or set(row_ids) != expected_ids:
        return False
    by_id = {row["id"]: row for row in rows}
    for entry in expected:
        postcondition_id = str(entry.get("id"))
        row = by_id[postcondition_id]
        status = row.get("status")
        exit_status = row.get("exit_status")
        if not isinstance(status, str) or status not in {
            "passed",
            "failed",
            "not_observed",
        }:
            return False
        if status == "not_observed":
            if exit_status is not None:
                return False
        elif isinstance(exit_status, bool) or not isinstance(exit_status, int):
            return False
        if not isinstance(row.get("check_id"), str) or row["check_id"] != str(
            entry.get("check_id", "")
        ):
            return False
        expected_status = (
            "not_observed"
            if exit_status is None
            else ("passed" if exit_status == 0 else "failed")
        )
        if status != expected_status:
            return False
    return True


def _receipt_fields_from_rows(receipt: Mapping[str, Any]) -> tuple[str, str, list[str]]:
    rows = receipt["postconditions"]
    unobserved = [str(row["id"]) for row in rows if row.get("exit_status") is None]
    observed = bool(rows) and not unobserved
    verdict = (
        "failed"
        if any(
            row.get("exit_status") != 0
            for row in rows
            if row.get("exit_status") is not None
        )
        else ("passed" if observed else "not_observed")
    )
    return ("observed" if observed else "prepared_not_observed", verdict, unobserved)


def contract_verification_observed(
    contract: Mapping[str, Any], receipt: object
) -> bool:
    if (
        not isinstance(receipt, Mapping)
        or receipt.get("schema_version") != HANDOFF_CONTRACT_RECEIPT_SCHEMA_VERSION
        or receipt.get("contract_digest") != contract_digest(contract)
        or not _receipt_rows_match_contract(contract, receipt)
    ):
        return False
    status, verdict, unobserved = _receipt_fields_from_rows(receipt)
    return (
        receipt.get("status") == status
        and receipt.get("verdict") == verdict
        and receipt.get("unobserved_postconditions") == unobserved
        and status == "observed"
        and verdict == "passed"
        and not unobserved
    )


def contract_verification_summary(
    contract: Mapping[str, Any], receipt: object
) -> dict[str, Any]:
    unobserved = [
        str(entry.get("id"))
        for entry in contract.get("postconditions", [])
        if isinstance(entry, Mapping)
    ]
    if (
        not isinstance(receipt, Mapping)
        or receipt.get("schema_version") != HANDOFF_CONTRACT_RECEIPT_SCHEMA_VERSION
        or receipt.get("contract_digest") != contract_digest(contract)
        or not _receipt_rows_match_contract(contract, receipt)
    ):
        return {
            "schema_version": HANDOFF_CONTRACT_SCHEMA_VERSION,
            "status": "prepared_not_observed",
            "verdict": "not_observed",
            "reason": "no_exit_status_recorded",
            "unobserved_postconditions": unobserved,
        }
    status, verdict, derived_unobserved = _receipt_fields_from_rows(receipt)
    if (
        not isinstance(receipt.get("status"), str)
        or not isinstance(receipt.get("verdict"), str)
        or receipt.get("status") != status
        or receipt.get("verdict") != verdict
        or receipt.get("unobserved_postconditions") != derived_unobserved
    ):
        return {
            "schema_version": HANDOFF_CONTRACT_SCHEMA_VERSION,
            "status": "prepared_not_observed",
            "verdict": "not_observed",
            "reason": "no_exit_status_recorded",
            "unobserved_postconditions": unobserved,
        }
    return {
        "schema_version": HANDOFF_CONTRACT_SCHEMA_VERSION,
        "status": status,
        "verdict": verdict,
        "unobserved_postconditions": derived_unobserved,
    }


__all__ = [
    "HANDOFF_CONTRACT_SCHEMA_VERSION",
    "HANDOFF_CONTRACT_RECEIPT_SCHEMA_VERSION",
    "HANDOFF_CONTRACT_KEY",
    "HandoffContractError",
    "build_handoff_contract",
    "handoff_templates",
    "template_variables",
    "handoff_contract_errors",
    "require_valid_handoff_contract",
    "contract_digest",
    "build_handoff_contract_receipt",
    "contract_verification_observed",
    "contract_verification_summary",
]
