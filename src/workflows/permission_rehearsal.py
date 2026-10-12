"""Offline rehearsal of planned tool calls against the OMJ policy matcher."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Final
from uuid import uuid4

from ..plugin_bundle.omj.toolcall_rules import (
    MAX_RULES_FILE_BYTES,
    load_toolcall_rules,
    matched_toolcall_rule,
    toolcall_rules_path,
    validate_toolcall_rules_document,
)

PERMISSION_REHEARSAL_SCHEMA_VERSION: Final = "omj_permission_rehearsal/v1"
PERMISSION_REHEARSAL_PLAN_SCHEMA_VERSION: Final = "omj_permission_rehearsal_plan/v1"
MAX_PLANNED_CALLS: Final = 256
MAX_PLAN_FILE_BYTES: Final = 262_144
VERDICT_REFUSED: Final = "refused"
VERDICT_UNKNOWN: Final = "unknown"
PERMISSION_REHEARSAL_VERDICTS: Final = (VERDICT_REFUSED, VERDICT_UNKNOWN)
REASON_REFUSED_BY_RULE: Final = "refused_by_rule"
REASON_NEEDS_APPROVAL_NOT_READABLE: Final = "needs_approval_not_readable"
REASON_TEXT: Final[dict[str, str]] = {
    REASON_REFUSED_BY_RULE: (
        "A toolcall rule matches this call; the enforcing pre_tool_call hook would block it before execution."
    ),
    REASON_NEEDS_APPROVAL_NOT_READABLE: (
        "No toolcall rule refuses this call. Hermes per-tool approval declarations are not readable here, "
        "so this result is unknown rather than permission."
    ),
}
PERMISSION_REHEARSAL_CLAIM_BOUNDARY: Final = (
    "A rehearsal reads the local rules file and observed approval-bypass state; it executes nothing, writes nothing, "
    "and reaches no network. Unknown is not permission, and no result claims approval, execution, review, CI, or safety evidence."
)


@dataclass(frozen=True, slots=True)
class PlannedCall:
    tool: str
    args: Any


def read_planned_calls(path: Path) -> tuple[PlannedCall, ...]:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValueError(f"could not read plan file {path}: {exc}") from exc
    if size > MAX_PLAN_FILE_BYTES:
        raise ValueError(f"plan file is {size} bytes; at most {MAX_PLAN_FILE_BYTES} are read")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"could not parse plan file {path}: {exc}") from exc
    return parse_planned_calls(raw)


def parse_planned_calls(raw: object) -> tuple[PlannedCall, ...]:
    if not isinstance(raw, dict):
        raise ValueError("plan document must be a JSON object")
    if raw.get("schema_version") != PERMISSION_REHEARSAL_PLAN_SCHEMA_VERSION:
        raise ValueError(f"plan schema_version must be {PERMISSION_REHEARSAL_PLAN_SCHEMA_VERSION}")
    entries = raw.get("calls")
    if not isinstance(entries, list) or not entries:
        raise ValueError("plan calls must be a nonempty list")
    if len(entries) > MAX_PLANNED_CALLS:
        raise ValueError(f"plan lists {len(entries)} calls; at most {MAX_PLANNED_CALLS} are rehearsed")
    calls: list[PlannedCall] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f"calls[{index}] must be an object")
        tool = entry.get("tool")
        if not isinstance(tool, str) or not tool.strip():
            raise ValueError(f"calls[{index}] tool must be a nonempty string")
        calls.append(PlannedCall(tool.strip(), entry.get("args", {})))
    return tuple(calls)


def rehearse_planned_calls(
    planned_calls: tuple[PlannedCall, ...],
    *,
    omj_home: str | Path = "",
    hermes_home: str | Path = "",
    now: float | None = None,
) -> dict[str, Any]:
    if len(planned_calls) > MAX_PLANNED_CALLS:
        raise ValueError(f"planned_calls exceeds {MAX_PLANNED_CALLS} calls")
    home = str(omj_home or "")
    rules_path = toolcall_rules_path(home)
    present = rules_path.exists()
    loaded = len(load_toolcall_rules(rules_path))
    defect_count = _rules_defect_count(rules_path) if present else 0
    session_id = f"omj-permission-rehearsal-{uuid4().hex}"
    calls = [_rehearse_one(index, call, session_id, home) for index, call in enumerate(planned_calls)]
    bypass = _read_approval_bypass(str(hermes_home or ""))
    refused = sum(1 for row in calls if row["verdict"] == VERDICT_REFUSED)
    return {
        "schema_version": PERMISSION_REHEARSAL_SCHEMA_VERSION,
        "rules": {
            "path": str(rules_path),
            "present": present,
            "loaded": loaded,
            "defect_count": defect_count,
        },
        "approval_bypass": bypass,
        "calls": calls,
        "summary": {
            "planned": len(calls),
            "refused": refused,
            "unknown": len(calls) - refused,
            "approval_bypass_active": bypass.get("status") == "observed" and bypass.get("enabled") is True,
        },
        "reason_codes": dict(REASON_TEXT),
        "claim_boundary": PERMISSION_REHEARSAL_CLAIM_BOUNDARY,
    }


def _rehearse_one(index: int, call: PlannedCall, session_id: str, omj_home: str) -> dict[str, Any]:
    rule = matched_toolcall_rule(
        tool_name=call.tool,
        tool_input=call.args,
        session_id=session_id,
        omj_home=omj_home,
    )
    if rule is None:
        return {
            "index": index,
            "tool": call.tool,
            "verdict": VERDICT_UNKNOWN,
            "reason": REASON_NEEDS_APPROVAL_NOT_READABLE,
            "rule": "",
        }
    return {
        "index": index,
        "tool": call.tool,
        "verdict": VERDICT_REFUSED,
        "reason": REASON_REFUSED_BY_RULE,
        "rule": rule.name,
    }


def _rules_defect_count(path: Path) -> int:
    try:
        if path.stat().st_size > MAX_RULES_FILE_BYTES:
            return 1
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 1
    errors, _accepted = validate_toolcall_rules_document(raw)
    return len(errors)


def _read_approval_bypass(hermes_home: str) -> dict[str, Any]:
    if not hermes_home:
        return {"status": "not_observed", "enabled": False, "source": "not_supplied"}
    config = Path(hermes_home).expanduser() / "config.yaml"
    try:
        if not config.is_file() or config.stat().st_size > MAX_PLAN_FILE_BYTES:
            return {"status": "not_observed", "enabled": False, "source": "hermes_config"}
        text = config.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return {"status": "not_observed", "enabled": False, "source": "hermes_config"}
    mode_value: str | None = None
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line or line[0].isspace() or line.startswith("#"):
            continue
        key, separator, _rest = line.partition(":")
        if separator != ":" or key.strip() != "approvals":
            continue
        child_indent: int | None = None
        for child in lines[index + 1 :]:
            if not child.strip() or child.lstrip().startswith("#"):
                continue
            if not child[0].isspace():
                break
            indent = len(child) - len(child.lstrip())
            if child_indent is None:
                child_indent = indent
            if indent != child_indent:
                continue
            stripped = child.strip()
            if stripped.startswith("mode:"):
                mode_value = stripped.partition(":")[2].split("#", 1)[0].strip()
                break
        if mode_value is not None:
            break
    if mode_value is None:
        return {"status": "observed", "enabled": False, "source": "hermes_config"}
    quoted = len(mode_value) >= 2 and mode_value[0] in {"'", '"'} and mode_value[-1] == mode_value[0]
    value = mode_value[1:-1] if quoted else mode_value
    enabled = value.casefold() == "off" if quoted else value.casefold() in {"off", "false", "no"}
    return {"status": "observed", "enabled": enabled, "source": "hermes_config"}
