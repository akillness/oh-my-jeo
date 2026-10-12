"""Offline user-authored tool-call rule matcher used by OMJ policy seams.

The matcher is deliberately pure with respect to process execution: it only reads
an explicitly selected local rules file.  Rehearsal and the enforcing plugin hook
must call this module rather than maintain separate pattern conventions.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import threading
from typing import Final

TOOLCALL_RULES_SCHEMA_VERSION: Final = "omj_toolcall_rules/v1"
TOOLCALL_RULES_FILE: Final = "toolcall-rules.json"
RULE_REPEAT_MODES: Final = ("once", "always")
MAX_RULES: Final = 64
MAX_RULE_NAME_CHARS: Final = 64
MAX_PATTERN_CHARS: Final = 512
MAX_MESSAGE_CHARS: Final = 1000
MAX_TOOL_SCOPE_ITEMS: Final = 16
MAX_RULES_FILE_BYTES: Final = 262_144
MAX_MATCH_TEXT_CHARS: Final = 20_000


@dataclass(frozen=True, slots=True)
class ToolcallRule:
    name: str
    pattern: re.Pattern[str]
    message: str
    tools: tuple[str, ...]
    repeat: str


_claim_lock = threading.Lock()
_claimed: set[tuple[str, str, str]] = set()


def toolcall_rules_path(omj_home: str | Path = "") -> Path:
    """Return the documented OMJ rules path for an explicit local home."""
    root = Path(omj_home).expanduser() if omj_home else Path.home() / ".omj"
    return root / "rules" / TOOLCALL_RULES_FILE


def load_toolcall_rules(path: Path) -> tuple[ToolcallRule, ...]:
    """Load valid rules, failing open for a broken policy file."""
    try:
        if path.stat().st_size > MAX_RULES_FILE_BYTES:
            return ()
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ()
    if not isinstance(raw, dict) or raw.get("schema_version") != TOOLCALL_RULES_SCHEMA_VERSION:
        return ()
    entries = raw.get("rules")
    if not isinstance(entries, list):
        return ()
    accepted: list[ToolcallRule] = []
    seen: set[str] = set()
    for entry in entries[:MAX_RULES]:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        pattern_text = entry.get("pattern")
        message = entry.get("message")
        tools = entry.get("tools", [])
        repeat = entry.get("repeat", "once")
        if (
            not isinstance(name, str)
            or not name.strip()
            or len(name.strip()) > MAX_RULE_NAME_CHARS
            or name.strip() in seen
            or not isinstance(pattern_text, str)
            or not pattern_text
            or len(pattern_text) > MAX_PATTERN_CHARS
            or not isinstance(message, str)
            or not message.strip()
            or len(message.strip()) > MAX_MESSAGE_CHARS
            or not isinstance(tools, list)
            or len(tools) > MAX_TOOL_SCOPE_ITEMS
            or not all(isinstance(tool, str) and tool.strip() for tool in tools)
            or repeat not in RULE_REPEAT_MODES
        ):
            continue
        try:
            pattern = re.compile(pattern_text)
        except re.error:
            continue
        clean_name = name.strip()
        seen.add(clean_name)
        accepted.append(
            ToolcallRule(
                clean_name,
                pattern,
                message.strip(),
                tuple(str(tool).strip() for tool in tools),
                str(repeat),
            )
        )
    return tuple(accepted)


def validate_toolcall_rules_document(raw: object) -> tuple[list[str], int]:
    """Return validation diagnostics and accepted rule count."""
    if not isinstance(raw, dict):
        return (["rules document must be a JSON object"], 0)
    if raw.get("schema_version") != TOOLCALL_RULES_SCHEMA_VERSION:
        return ([f"schema_version must be {TOOLCALL_RULES_SCHEMA_VERSION}; no rule is loaded"], 0)
    entries = raw.get("rules")
    if not isinstance(entries, list):
        return (["rules must be a list"], 0)
    errors: list[str] = []
    accepted = 0
    seen: set[str] = set()
    for index, entry in enumerate(entries[:MAX_RULES]):
        if not isinstance(entry, dict):
            errors.append(f"rules[{index}]: rule must be an object")
            continue
        name = entry.get("name")
        pattern = entry.get("pattern")
        message = entry.get("message")
        tools = entry.get("tools", [])
        repeat = entry.get("repeat", "once")
        valid = (
            isinstance(name, str)
            and bool(name.strip())
            and len(name.strip()) <= MAX_RULE_NAME_CHARS
            and name.strip() not in seen
            and isinstance(pattern, str)
            and bool(pattern)
            and len(pattern) <= MAX_PATTERN_CHARS
            and isinstance(message, str)
            and bool(message.strip())
            and len(message.strip()) <= MAX_MESSAGE_CHARS
            and isinstance(tools, list)
            and len(tools) <= MAX_TOOL_SCOPE_ITEMS
            and all(isinstance(tool, str) and bool(tool.strip()) for tool in tools)
            and repeat in RULE_REPEAT_MODES
        )
        if valid:
            try:
                re.compile(pattern)
            except re.error:
                valid = False
        if valid:
            seen.add(name.strip())
            accepted += 1
        else:
            errors.append(f"rules[{index}]: invalid rule")
    if len(entries) > MAX_RULES:
        errors.append(f"at most {MAX_RULES} rules are read; extra entries are ignored")
    return errors, accepted


def matched_toolcall_rule(
    *,
    tool_name: object,
    tool_input: object,
    session_id: str = "",
    omj_home: str | Path = "",
) -> ToolcallRule | None:
    """Return the single rule that blocks a call, if one matches."""
    name = str(tool_name or "").strip()
    if not name:
        return None
    path = toolcall_rules_path(omj_home)
    for rule in load_toolcall_rules(path):
        if rule.tools and name not in rule.tools:
            continue
        if rule.pattern.search(_match_text(name, tool_input)) is None:
            continue
        if rule.repeat == "once":
            key = (str(path.resolve()), str(session_id or ""), rule.name)
            with _claim_lock:
                if key in _claimed:
                    continue
                _claimed.add(key)
        return rule
    return None


def toolcall_rule_directive(
    *,
    tool_name: object,
    tool_input: object,
    session_id: str = "",
    omj_home: str | Path = "",
) -> dict[str, str] | None:
    """Return the enforcing block directive, or ``None``."""
    rule = matched_toolcall_rule(
        tool_name=tool_name,
        tool_input=tool_input,
        session_id=session_id,
        omj_home=omj_home,
    )
    if rule is None:
        return None
    return {
        "action": "block",
        "message": (
            f"[OMJ Rule] {rule.name}: {rule.message}\n"
            "This tool call was blocked by a user-defined OMJ rule before execution. "
            "Adjust the approach instead of retrying the same call. A blocked call did not run."
        ),
    }


def _match_text(tool_name: str, tool_input: object) -> str:
    if isinstance(tool_input, str):
        args_text = tool_input
    else:
        try:
            args_text = json.dumps(tool_input, ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError):
            args_text = str(tool_input)
    return f"{tool_name}\n{args_text}"[:MAX_MATCH_TEXT_CHARS]


def _reset_state() -> None:
    """Clear once-claims for process-local tests and lifecycle resets."""
    with _claim_lock:
        _claimed.clear()
