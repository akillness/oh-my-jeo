"""Offline, cited agent-debug reducers for supplied Hermes session records.

The module deliberately accepts only an operator-supplied JSON Lines record.  It
never opens a Hermes database, executes a source command, or retains prompt,
argument, and tool-output text.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
from typing import Any, BinaryIO, Iterator, Mapping, Sequence

AGENT_DEBUG_REPORT_SCHEMA_VERSION = "agent_debug_report/v1"
TOOL_ERROR = "tool_error"
IDENTICAL_RETRY_AFTER_ERROR = "identical_retry_after_error"
BACKGROUND_WITHOUT_NOTIFY = "background_without_notify"
COMPACTION_BOUNDARY = "compaction_boundary"
FINDING_KINDS = (TOOL_ERROR, IDENTICAL_RETRY_AFTER_ERROR, BACKGROUND_WITHOUT_NOTIFY, COMPACTION_BOUNDARY)
ERROR_CLASSES = ("nonzero_exit", "success_false", "error_field")
ARGUMENT_DIGEST_CHARS = 16
SOURCE_RECORD = "session_record"
LOCATOR_RECORD_LINE = "record_line"
DEFAULT_MAX_ROWS = 20_000
DEFAULT_MAX_ROW_BYTES = 256 * 1024
_MAX_LISTED_OVERSIZED = 20
_SKIP_CHUNK_BYTES = 64 * 1024
_SUMMARY_COLUMN = "_compressed_summary"
_TYPING_RESULT_KEYS = ("exit_code", "success", "pid", "notify_on_complete")
_CITATION_KEYS = ("session_id", "message_ids", "timestamps", "tool_call_ids", "tool_name", "error_class", "exit_code", "arguments_sha256")
CITATION_KEYS = _CITATION_KEYS
_REQUIRED = {
    TOOL_ERROR: (1, ("tool_call_ids", "tool_name", "error_class")),
    IDENTICAL_RETRY_AFTER_ERROR: (2, ("tool_call_ids", "tool_name", "error_class", "arguments_sha256")),
    BACKGROUND_WITHOUT_NOTIFY: (1, ("tool_call_ids", "tool_name")),
    COMPACTION_BOUNDARY: (1, ()),
}
UNAVAILABLE_REASONS = {
    SOURCE_RECORD: {
        IDENTICAL_RETRY_AFTER_ERROR: "no record line carries a tool_calls field",
        COMPACTION_BOUNDARY: f"no record line carries a {_SUMMARY_COLUMN} field",
    }
}
AGENT_DEBUG_REPORT_CLAIM_BOUNDARY = (
    "An agent debug report cites rows one supplied session record persisted, read without writing to it, and quotes no prompt, reply, argument, or tool output. "
    "A finding is an observed record, not a diagnosis: it does not show why the agent acted as it did, that a retry was wrong, that a compaction lost what mattered, or that any recovery worked, and it is not execution, review, CI, or merge evidence. "
    "A kind listed as unavailable was not checked, and rows listed as oversized or past the row budget were not read."
)

class AgentDebugReportError(ValueError):
    pass


def parse_turn_range(text: str | None) -> tuple[int, int | None] | None:
    if text is None:
        return None
    value = str(text).strip()
    head, sep, tail = value.partition(":")
    try:
        start = int(head)
        end = int(tail) if sep and tail.strip() else (None if sep else start)
    except ValueError:
        raise AgentDebugReportError(f"turn range {value!r} must be N, N:M, or N:") from None
    if start < 1 or (end is not None and end < start):
        raise AgentDebugReportError(f"turn range {value!r} must start at 1 or later and not end before it starts")
    return start, end


def build_agent_debug_report(
    hermes_home: str | Path | None,
    session_id: str | None,
    *,
    session_record: str | Path | None = None,
    turns: tuple[int, int | None] | None = None,
    max_rows: int = DEFAULT_MAX_ROWS,
    max_row_bytes: int = DEFAULT_MAX_ROW_BYTES,
) -> dict[str, Any]:
    if max_rows < 1 or max_row_bytes < 1:
        raise AgentDebugReportError("max_rows and max_row_bytes must be at least 1")
    if session_record is None:
        raise AgentDebugReportError("an operator-supplied session record is required; live Hermes state.db is not read")
    read = _read_record(Path(session_record), session_id, turns, max_rows, max_row_bytes)
    report = _report_from_rows(read, max_rows=max_rows, max_row_bytes=max_row_bytes)
    errors = agent_debug_report_errors(report)
    if errors:
        raise AgentDebugReportError("agent_debug_report/v1 failed validation: " + "; ".join(errors))
    return report


def _bounded_lines(handle: BinaryIO, max_row_bytes: int) -> Iterator[tuple[int, bytes, int]]:
    number = 0
    while True:
        raw = handle.readline(max_row_bytes + 1)
        if not raw:
            return
        number += 1
        if raw.endswith(b"\n") or len(raw) <= max_row_bytes:
            yield number, raw, 0
            continue
        skipped = len(raw)
        while not raw.endswith(b"\n"):
            raw = handle.readline(_SKIP_CHUNK_BYTES)
            if not raw:
                break
            skipped += len(raw)
        yield number, b"", skipped


def _json(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        value = bytes(value).decode("utf-8", "replace")
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return None


def _epoch(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
        return float(value)
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def _typed_result(content: Any) -> dict[str, Any] | None:
    value = _json(content)
    if not isinstance(value, Mapping):
        return None
    out = {key: value[key] for key in _TYPING_RESULT_KEYS if key in value}
    out["error_present"] = isinstance(value.get("error"), str) and bool(value.get("error", "").strip())
    return out


def _error_class(result: Mapping[str, Any] | None) -> tuple[str | None, int | None]:
    if result is None:
        return None, None
    code = result.get("exit_code")
    code = code if isinstance(code, int) and not isinstance(code, bool) else None
    if code is not None and code != 0:
        return "nonzero_exit", code
    if result.get("success") is False:
        return "success_false", code
    if result.get("error_present") is True:
        return "error_field", code
    return None, code


def _started_without_notify(result: Mapping[str, Any] | None) -> bool:
    if result is None:
        return False
    pid = result.get("pid")
    return isinstance(pid, int) and not isinstance(pid, bool) and result.get("notify_on_complete") is not True


def _argument_digests(calls: Any) -> dict[str, str]:
    calls = _json(calls)
    if not isinstance(calls, list):
        return {}
    out: dict[str, str] = {}
    for call in calls:
        if not isinstance(call, Mapping):
            continue
        call_id = call.get("id") or call.get("call_id")
        if not isinstance(call_id, str) or call_id in out:
            continue
        fn = call.get("function")
        args = fn.get("arguments") if isinstance(fn, Mapping) else None
        if isinstance(args, Mapping):
            canonical = json.dumps(args, sort_keys=True, separators=(",", ":"))
        elif isinstance(args, str):
            try:
                canonical = json.dumps(json.loads(args), sort_keys=True, separators=(",", ":"))
            except (ValueError, TypeError):
                canonical = args
        else:
            continue
        out[call_id] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:ARGUMENT_DIGEST_CHARS]
    return out


def _reduced_row(ref: int, message: Mapping[str, Any], *, oversized: bool = False) -> dict[str, Any]:
    has_calls = "tool_calls" in message
    calls = message.get("tool_calls") if has_calls else None
    role = str(message.get("role") or "")
    call_id = message.get("tool_call_id")
    return {
        "ref": ref,
        "session_id": str(message.get("session_id")) if isinstance(message.get("session_id"), str) else None,
        "role": role,
        "call_key": str(call_id) if isinstance(call_id, str) and call_id else f"row:{ref}",
        "tool_call_id": str(call_id) if isinstance(call_id, str) and call_id else None,
        "tool_name": str(message.get("tool_name") or ""),
        "result": _typed_result(message.get("content")) if role == "tool" else None,
        "digests": _argument_digests(calls) if role == "assistant" else {},
        "has_tool_calls_field": has_calls,
        "summary": bool(message.get(_SUMMARY_COLUMN)) if _SUMMARY_COLUMN in message else None,
        "timestamp": _epoch(message.get("timestamp")),
        "oversized": oversized,
    }


def _single_match(wanted: str, matches: list[str]) -> str:
    if not matches:
        raise AgentDebugReportError(f"no Hermes session {wanted}")
    if len(matches) > 1:
        listed = ", ".join(matches[:5]) + (", ..." if len(matches) > 5 else "")
        raise AgentDebugReportError(f"session {wanted!r} is ambiguous: it matches more than one session ({listed}); give the full id")
    return matches[0]


def _resolve_record_session(session_id: str | None, sessions: Mapping[str, float]) -> tuple[str, str]:
    if not sessions:
        raise AgentDebugReportError("the session record has no line that names a session_id")
    wanted = str(session_id or "").strip()
    if not wanted:
        if len(sessions) > 1:
            raise AgentDebugReportError("the session record holds more than one session; name one with --hermes-session")
        return next(iter(sessions)), "only_session"
    if wanted == "latest":
        latest = max(sessions.values())
        matches = sorted(item for item, stamp in sessions.items() if stamp == latest)
        return _single_match(wanted, matches), "latest"
    if wanted in sessions:
        return wanted, "exact"
    return _single_match(wanted, sorted(item for item in sessions if item.startswith(wanted))), "unique_prefix"


def _read_record(path: Path, session_id: str | None, turns: tuple[int, int | None] | None, max_rows: int, max_row_bytes: int) -> dict[str, Any]:
    try:
        info = path.stat()
    except OSError as exc:
        raise AgentDebugReportError(f"no session record at {path}: {exc.strerror or exc}") from exc
    if not path.is_file():
        raise AgentDebugReportError(f"session record {path} is not a regular file")
    rows: list[dict[str, Any]] = []
    oversized: list[int] = []
    malformed: list[int] = []
    bytes_read = bytes_skipped = lines_read = 0
    row_limit = False
    try:
        with path.open("rb") as handle:
            for line, raw, skipped in _bounded_lines(handle, max_row_bytes):
                if lines_read >= max_rows:
                    row_limit = True
                    break
                lines_read += 1
                bytes_read += len(raw)
                bytes_skipped += skipped
                if skipped:
                    oversized.append(line)
                    continue
                try:
                    value = json.loads(raw.decode("utf-8", "replace"))
                except (TypeError, ValueError, json.JSONDecodeError):
                    malformed.append(line)
                    continue
                if isinstance(value, Mapping):
                    rows.append(_reduced_row(line, value))
                else:
                    malformed.append(line)
    except OSError as exc:
        raise AgentDebugReportError(f"could not read {path}: {exc.strerror or exc}") from exc
    sessions: dict[str, float] = {}
    for row in rows:
        sid = row["session_id"]
        if sid:
            stamp = row["timestamp"] if row["timestamp"] is not None else -math.inf
            sessions[sid] = max(sessions.get(sid, -math.inf), stamp)
    resolved, selection = _resolve_record_session(session_id, sessions)
    if session_id is not None and str(session_id).strip() == "latest" and row_limit:
        raise AgentDebugReportError("latest selection is unavailable after the row budget was reached; provide an exact session id")
    selected = [row for row in rows if row["session_id"] == resolved]
    user_turn = 0
    windowed: list[dict[str, Any]] = []
    for row in selected:
        if row["role"] == "user" and not row["summary"]:
            user_turn += 1
        if turns is None or (user_turn >= turns[0] and (turns[1] is None or user_turn <= turns[1])):
            windowed.append(row)
    if turns is not None and turns[0] > user_turn:
        raise AgentDebugReportError(f"turn {turns[0]} is past the session's last turn ({user_turn})")
    stamps = [row["timestamp"] for row in selected if row["timestamp"] is not None]
    unavailable: list[dict[str, str]] = []
    if not any(row["has_tool_calls_field"] for row in selected):
        unavailable.append({"kind": IDENTICAL_RETRY_AFTER_ERROR, "reason": UNAVAILABLE_REASONS[SOURCE_RECORD][IDENTICAL_RETRY_AFTER_ERROR]})
    if not any(row["summary"] is not None for row in selected):
        unavailable.append({"kind": COMPACTION_BOUNDARY, "reason": UNAVAILABLE_REASONS[SOURCE_RECORD][COMPACTION_BOUNDARY]})
    if oversized:
        unavailable.append({"kind": "budget", "reason": f"{len(oversized)} oversized row(s) were not read"})
    if malformed:
        unavailable.append({"kind": "malformed_rows", "reason": f"{len(malformed)} malformed or non-object row(s) were not read"})
    return {
        "source": {"kind": SOURCE_RECORD, "label": path.name, "locator": LOCATOR_RECORD_LINE, "requested_session": None if session_id is None else str(session_id), "selection": selection, "snapshot": {"bytes": int(info.st_size), "mtime_ns": int(info.st_mtime_ns)}},
        "session": {"id": resolved, "source": None, "started_at": min(stamps) if stamps else None, "ended_at": None, "end_reason": None},
        "turns": {"start": None if turns is None else turns[0], "end": None if turns is None else turns[1], "turn_count": None if row_limit or oversized or malformed else user_turn},
        "rows": windowed,
        "rows_read": lines_read,
        "row_limit_reached": row_limit,
        "bytes_read": bytes_read,
        "bytes_skipped": bytes_skipped,
        "oversized_refs": oversized,
        "malformed_refs": malformed,
        "unavailable": unavailable,
    }


def _distinct_calls(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        key = str(row.get("call_key") or "")
        if key in seen:
            continue
        seen.add(key)
        out.append({"message_id": row["ref"], "timestamp": row["timestamp"], "tool_call_id": row["tool_call_id"], "tool_name": row["tool_name"], "result": row["result"]})
    return out


def _finding(kind: str, session_id: str, rows: Sequence[Mapping[str, Any]], *, error_class: str | None = None, exit_code: int | None = None, arguments_sha256: str | None = None) -> dict[str, Any]:
    ids = [int(row.get("message_id", row.get("ref"))) for row in rows]
    is_compaction = kind == COMPACTION_BOUNDARY
    return {"finding_id": f"{kind}:{ids[0]}", "kind": kind, "citation": {
        "session_id": session_id, "message_ids": ids, "timestamps": [row.get("timestamp") for row in rows],
        "tool_call_ids": [] if is_compaction else [str(row["tool_call_id"]) for row in rows if row.get("tool_call_id")],
        "tool_name": None if is_compaction else (rows[0].get("tool_name") or None),
        "error_class": error_class, "exit_code": exit_code, "arguments_sha256": arguments_sha256,
    }}


def _report_from_rows(read: Mapping[str, Any], *, max_rows: int, max_row_bytes: int) -> dict[str, Any]:
    rows = list(read["rows"])
    arguments: dict[str, str] = {}
    for row in rows:
        for call_id, digest in (row.get("digests") or {}).items():
            arguments.setdefault(call_id, digest)
    calls = _distinct_calls(row for row in rows if row.get("role") == "tool")
    findings: list[dict[str, Any]] = []
    previous: dict[str, dict[str, Any]] = {}
    for call in calls:
        call_id = call.get("tool_call_id")
        if call_id is None:
            continue
        error, exit_code = _error_class(call.get("result"))
        if error:
            findings.append(_finding(TOOL_ERROR, read["session"]["id"], [call], error_class=error, exit_code=exit_code))
        if _started_without_notify(call.get("result")):
            findings.append(_finding(BACKGROUND_WITHOUT_NOTIFY, read["session"]["id"], [call]))
        digest = arguments.get(str(call_id))
        tool = str(call.get("tool_name") or "")
        prior = previous.get(tool)
        if prior and prior["error"] and digest and digest == prior.get("digest"):
            findings.append(_finding(IDENTICAL_RETRY_AFTER_ERROR, read["session"]["id"], [prior["call"], call], error_class=prior["error"], exit_code=prior.get("exit_code"), arguments_sha256=digest))
        previous[tool] = {"call": call, "error": error, "exit_code": exit_code, "digest": digest}
    if COMPACTION_BOUNDARY not in {item["kind"] for item in read.get("unavailable", ())}:
        for row in rows:
            if row.get("summary"):
                findings.append(_finding(COMPACTION_BOUNDARY, read["session"]["id"], [row]))
    order = {kind: index for index, kind in enumerate(FINDING_KINDS)}
    findings.sort(key=lambda item: (item["citation"]["message_ids"][0], order[item["kind"]]))
    oversized = sorted({*read.get("oversized_refs", ()), *(row["ref"] for row in rows if row.get("oversized"))})
    malformed = sorted(set(read.get("malformed_refs", ())))
    budget = {"max_rows": max_rows, "max_row_bytes": max_row_bytes, "rows_read": int(read.get("rows_read", 0)), "bytes_read": int(read.get("bytes_read", 0)), "bytes_skipped": int(read.get("bytes_skipped", 0)), "row_limit_reached": bool(read.get("row_limit_reached")), "oversized_rows": len(oversized), "oversized_refs": oversized[:_MAX_LISTED_OVERSIZED], "malformed_rows": len(malformed), "malformed_refs": malformed[:_MAX_LISTED_OVERSIZED], "complete": not read.get("row_limit_reached") and not oversized and not malformed}
    unavailable = list(read.get("unavailable", ()))
    return {"schema_version": AGENT_DEBUG_REPORT_SCHEMA_VERSION, "source": dict(read["source"]), "session": dict(read["session"]), "turns": dict(read["turns"]), "budget": budget,
            "counts": {"tool_calls": len(calls), "tool_calls_without_id": sum(1 for call in calls if call.get("tool_call_id") is None), "tool_calls_with_arguments": sum(1 for call in calls if call.get("tool_call_id") in arguments)},
            "checked_kinds": [kind for kind in FINDING_KINDS if kind not in {item.get("kind") for item in unavailable}], "unavailable": unavailable, "findings": findings,
            "finding_counts": {kind: sum(1 for item in findings if item["kind"] == kind) for kind in FINDING_KINDS}, "observed": True, "claim_boundary": AGENT_DEBUG_REPORT_CLAIM_BOUNDARY}


def _citation_errors(kind: str, citation: Mapping[str, Any], session_id: Any) -> list[str]:
    errors: list[str] = []
    if set(citation) != set(_CITATION_KEYS):
        errors.append("citation must carry the closed citation shape")
    if citation.get("session_id") != session_id:
        errors.append("citation names another session")
    count, required = _REQUIRED[kind]
    ids = citation.get("message_ids")
    if not isinstance(ids, list) or len(ids) != count or not all(isinstance(v, int) and not isinstance(v, bool) for v in ids):
        errors.append(f"citation must cite {count} message id{'s' if count != 1 else ''}")
    stamps = citation.get("timestamps")
    if not isinstance(stamps, list) or len(stamps) != count or not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in stamps):
        errors.append(f"citation must carry {count} timestamp{'s' if count != 1 else ''}")
    ids2 = citation.get("tool_call_ids")
    if "tool_call_ids" in required and (not isinstance(ids2, list) or len(ids2) != count or not all(isinstance(v, str) and v for v in ids2)):
        errors.append("citation must cite tool call ids")
    elif "tool_call_ids" not in required and ids2:
        errors.append("citation cites tool ids this kind does not span")
    if "tool_name" in required and not isinstance(citation.get("tool_name"), str):
        errors.append("citation must name the tool")
    if "error_class" in required and citation.get("error_class") not in ERROR_CLASSES:
        errors.append("citation must carry a known error_class")
    if "arguments_sha256" in required:
        digest = citation.get("arguments_sha256")
        if not isinstance(digest, str) or len(digest) != ARGUMENT_DIGEST_CHARS or any(c not in "0123456789abcdef" for c in digest):
            errors.append("citation must carry the arguments sha256 prefix")
    code = citation.get("exit_code")
    if code is not None and (not isinstance(code, int) or isinstance(code, bool)):
        errors.append("citation exit_code must be an integer or null")
    return errors


def agent_debug_report_errors(report: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != AGENT_DEBUG_REPORT_SCHEMA_VERSION:
        errors.append(f"schema_version must be {AGENT_DEBUG_REPORT_SCHEMA_VERSION}")
    session = report.get("session")
    sid = session.get("id") if isinstance(session, Mapping) else None
    if not isinstance(sid, str) or not sid:
        errors.append("session.id is missing")
    source = report.get("source")
    if not isinstance(source, Mapping) or source.get("kind") != SOURCE_RECORD or source.get("locator") != LOCATOR_RECORD_LINE:
        errors.append("source must identify a session record by record_line")
    budget = report.get("budget")
    if isinstance(budget, Mapping) and budget.get("complete") != (not budget.get("row_limit_reached") and not budget.get("oversized_rows") and not budget.get("malformed_rows")):
        errors.append("budget.complete is inconsistent")
    if report.get("claim_boundary") != AGENT_DEBUG_REPORT_CLAIM_BOUNDARY:
        errors.append("claim_boundary must be the report boundary")
    unavailable = report.get("unavailable")
    unavailable_kinds: list[Any] = []
    if not isinstance(unavailable, list):
        errors.append("unavailable must be a list")
    else:
        for item in unavailable:
            if not isinstance(item, Mapping) or not isinstance(item.get("kind"), str) or not isinstance(item.get("reason"), str):
                errors.append("unavailable entries must carry kind and reason")
            else:
                unavailable_kinds.append(item["kind"])
    if report.get("checked_kinds") != [kind for kind in FINDING_KINDS if kind not in unavailable_kinds]:
        errors.append("checked_kinds is inconsistent")
    findings = report.get("findings")
    if not isinstance(findings, list):
        return errors + ["findings must be a list"]
    counts = {kind: 0 for kind in FINDING_KINDS}
    seen: set[str] = set()
    for index, finding in enumerate(findings):
        if not isinstance(finding, Mapping):
            errors.append(f"finding {index} is not an object")
            continue
        if set(finding) != {"finding_id", "kind", "citation"}:
            errors.append(f"finding {index} carries keys outside the finding shape")
        kind = finding.get("kind")
        if kind not in _REQUIRED:
            errors.append(f"finding {index} has unknown kind")
            continue
        counts[kind] += 1
        citation = finding.get("citation")
        if not isinstance(citation, Mapping):
            errors.append(f"finding {index} has no citation")
            continue
        errors.extend(_citation_errors(kind, citation, sid))
        ids = citation.get("message_ids")
        first = ids[0] if isinstance(ids, list) and ids else None
        expected = f"{kind}:{first}"
        if finding.get("finding_id") != expected:
            errors.append(f"finding {index} finding_id must be {expected}")
        if finding.get("finding_id") in seen:
            errors.append(f"finding {index} repeats finding_id")
        seen.add(str(finding.get("finding_id")))
    if report.get("finding_counts") != counts:
        errors.append("finding_counts must count findings by kind")
    return errors


def _cited_rows(report: Mapping[str, Any]) -> dict[int, list[tuple[str, dict[str, Any]]]]:
    out: dict[int, list[tuple[str, dict[str, Any]]]] = {}
    for finding in report.get("findings") or ():
        citation = finding["citation"]
        for index, ref in enumerate(citation["message_ids"]):
            out.setdefault(int(ref), []).append((str(finding["finding_id"]), {"timestamp": citation["timestamps"][index], "tool_call_id": (citation.get("tool_call_ids") or [None] * len(citation["message_ids"]))[index] if index < len(citation.get("tool_call_ids") or ()) else None, "tool_name": citation.get("tool_name") or "", "summary": finding["kind"] == COMPACTION_BOUNDARY}))
    return out


def agent_debug_reference_errors(report: Mapping[str, Any], *, hermes_home: str | Path | None = None, session_record: str | Path | None = None) -> list[str]:
    errors = agent_debug_report_errors(report)
    if errors:
        return errors
    if session_record is None:
        return ["the report was read from a session record; supply that record to check it"]
    path = Path(session_record)
    try:
        info = path.stat()
    except OSError as exc:
        return [f"no session record at {path}: {exc.strerror or exc}"]
    snapshot = (report.get("source") or {}).get("snapshot") or {}
    if (int(info.st_size), int(info.st_mtime_ns)) != (snapshot.get("bytes"), snapshot.get("mtime_ns")):
        return ["every reference is stale: the session record's size or modification time changed since the report"]
    refs = _cited_rows(report)
    if not refs:
        return []
    max_bytes = int((report.get("budget") or {}).get("max_row_bytes") or DEFAULT_MAX_ROW_BYTES)
    current: dict[int, dict[str, Any]] = {}
    try:
        with path.open("rb") as handle:
            for line, raw, skipped in _bounded_lines(handle, max_bytes):
                if line > max(refs):
                    break
                if line not in refs or skipped:
                    continue
                value = _json(raw.decode("utf-8", "replace"))
                if isinstance(value, Mapping):
                    current[line] = {"session_id": str(value.get("session_id") or ""), "role": str(value.get("role") or ""), "tool_call_id": str(value.get("tool_call_id")) if value.get("tool_call_id") else None, "tool_name": str(value.get("tool_name") or ""), "summary": bool(value.get(_SUMMARY_COLUMN)), "timestamp": _epoch(value.get("timestamp"))}
    except OSError as exc:
        return [f"could not read {path}: {exc.strerror or exc}"]
    sid = str((report.get("session") or {}).get("id"))
    for ref, expected_rows in sorted(refs.items()):
        row = current.get(ref)
        for finding_id, expected in expected_rows:
            label = f"{finding_id} reference {ref}"
            if row is None:
                errors.append(f"{label} is missing from the source")
                continue
            if row["session_id"] != sid:
                errors.append(f"{label} is foreign: it belongs to another session")
            elif row["timestamp"] != expected["timestamp"]:
                errors.append(f"{label} is stale: the row's timestamp changed since the report")
            elif expected["summary"] and not row["summary"]:
                errors.append(f"{label} is mismatched: the row is not a compaction summary")
            elif expected["tool_call_id"] is not None and (row["role"] != "tool" or row["tool_call_id"] != expected["tool_call_id"] or row["tool_name"] != expected["tool_name"]):
                errors.append(f"{label} is mismatched: the row is not the cited tool call")
    return errors


def _stamp(value: Any) -> str:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        return "(unknown)"
    return datetime.fromtimestamp(value, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_agent_debug_report(report: Mapping[str, Any]) -> str:
    source = report.get("source") or {}; session = report.get("session") or {}; counts = report.get("counts") or {}
    out = [f"Agent debug report: session {session.get('id')} (source {source.get('label') or '(unknown)'})", f"  started {_stamp(session.get('started_at'))}    ended {_stamp(session.get('ended_at'))}", f"  tool calls {int(counts.get('tool_calls', 0))}    findings {len(report.get('findings') or ())}", "Findings"]
    for item in report.get("findings") or ():
        cite = item.get("citation") or {}; refs = ",".join(f"{source.get('label')}:{ref}" for ref in cite.get("message_ids") or ())
        parts = [str(item.get("finding_id")), f"at {refs}"]
        if cite.get("tool_name"): parts.append(f"tool {cite['tool_name']}")
        if cite.get("error_class"): parts.append(str(cite["error_class"]))
        if cite.get("arguments_sha256"): parts.append(f"args sha256 {cite['arguments_sha256']}")
        out.append("  " + "  ".join(parts))
    if report.get("unavailable"):
        out.append("Unavailable")
        out.extend(f"  {item.get('kind')}: {item.get('reason')}" for item in report["unavailable"])
    budget = report.get("budget") or {}
    out.extend(["Budget", f"  rows read {budget.get('rows_read')} of at most {budget.get('max_rows')}    complete {'yes' if budget.get('complete') else 'no'}", "Boundary", f"  {report.get('claim_boundary', AGENT_DEBUG_REPORT_CLAIM_BOUNDARY)}"])
    return "\n".join(out)

# Incident layer is kept here so the offline public surface has one import boundary.
AGENT_FAILURE_CAPTURE_SCHEMA_VERSION = "agent_failure_capture/v1"
AGENT_FAILURE_PATTERN_HYPOTHESIS_SCHEMA_VERSION = "agent_failure_pattern_hypothesis/v1"
CONTAINED_RECOVERY_ACTION_SCHEMA_VERSION = "contained_recovery_action/v1"
AGENT_DEBUG_EXPORT_SCHEMA_VERSION = "agent_debug_export/v1"
OBSERVABLES = ("looping", "repeated_work", "goal_drift", "context_loss", "tool_stall", "unexpected_cost", "unspecified")
TOOL_ERROR_RETRY_LOOP = "tool_error_retry_loop"
CONTEXT_LOSS_AFTER_COMPACTION = "context_loss_after_compaction"
UNWATCHED_BACKGROUND_WORK = "unwatched_background_work"
OUTSIDE_RECORDED_EVIDENCE = "outside_recorded_evidence"
PATTERNS = {
    TOOL_ERROR_RETRY_LOOP: (IDENTICAL_RETRY_AFTER_ERROR, "a retry with changed arguments that succeeds, or the same arguments failing again after a change elsewhere"),
    CONTEXT_LOSS_AFTER_COMPACTION: (COMPACTION_BOUNDARY, "the same failure in a turn range with no compaction before it"),
    UNWATCHED_BACKGROUND_WORK: (BACKGROUND_WITHOUT_NOTIFY, "the run waiting on a process whose completion it was notified of"),
    OUTSIDE_RECORDED_EVIDENCE: (None, "a replay of the cited turns, or host evidence the record does not hold"),
}
_OBSERVABLE_PATTERNS = {
    "looping": (TOOL_ERROR_RETRY_LOOP, CONTEXT_LOSS_AFTER_COMPACTION, OUTSIDE_RECORDED_EVIDENCE),
    "repeated_work": (TOOL_ERROR_RETRY_LOOP, CONTEXT_LOSS_AFTER_COMPACTION, OUTSIDE_RECORDED_EVIDENCE),
    "goal_drift": (CONTEXT_LOSS_AFTER_COMPACTION, TOOL_ERROR_RETRY_LOOP, OUTSIDE_RECORDED_EVIDENCE),
    "context_loss": (CONTEXT_LOSS_AFTER_COMPACTION, OUTSIDE_RECORDED_EVIDENCE),
    "tool_stall": (UNWATCHED_BACKGROUND_WORK, TOOL_ERROR_RETRY_LOOP, OUTSIDE_RECORDED_EVIDENCE),
    "unexpected_cost": (TOOL_ERROR_RETRY_LOOP, CONTEXT_LOSS_AFTER_COMPACTION, UNWATCHED_BACKGROUND_WORK, OUTSIDE_RECORDED_EVIDENCE),
    "unspecified": tuple(PATTERNS),
}
RECOVERY_ACTIONS = {TOOL_ERROR_RETRY_LOOP: "change_arguments_before_next_retry", CONTEXT_LOSS_AFTER_COMPACTION: "restate_goal_after_compaction", UNWATCHED_BACKGROUND_WORK: "poll_or_notify_background_process", OUTSIDE_RECORDED_EVIDENCE: "collect_discriminating_evidence"}
RECOVERY_STEPS = {"change_arguments_before_next_retry": "Pause before the next call and change its arguments or approach.", "restate_goal_after_compaction": "Restate the goal and open plan after compaction, then continue.", "poll_or_notify_background_process": "Poll the process or start it with completion notification before waiting.", "collect_discriminating_evidence": "Change nothing yet; replay the cited turns or supply host evidence."}
NOT_PERFORMED = ("recovery", "executor_reset", "session_mutation", "runtime_repair", "export", "archive", "github_issue", "comment")
INCIDENT_CLAIM_BOUNDARY = "An agent-debug incident is built from one cited report. Hypotheses are inferred, not observed; recovery is a proposal requiring approval and was not executed. None of it is execution, review, CI, or merge evidence."
EXPORT_CLAIM_BOUNDARY = "An agent-debug export is a redacted incident package a person reviewed and chose to write; it was not uploaded, filed, or shared by OMJ."
class AgentDebugIncidentError(ValueError):
    pass
RECEIPT_SCHEMA_FANOUT_DISPATCH = "fanout_dispatch_summary/v1"
RECEIPT_IDENTITIES = ("session", "run", "unit", "configuration", "freshness")
RECEIPT_REJECTIONS = ("unreadable", "oversized", "ineligible_schema", "session_unbound", "foreign_session", "run_unbound", "unit_unbound", "configuration_unbound", "freshness_unbound", "stale", "identity_conflict")
MAX_RECEIPT_BYTES = 256 * 1024
_SAFE_RECEIPT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

class _RefusedReceipt:
    def __init__(self, reason: str) -> None:
        self.reason = reason

def _safe_receipt_id(value: Any) -> str | None:
    text = value if isinstance(value, str) else ""
    return text if _SAFE_RECEIPT_ID.fullmatch(text) else None

def _receipt_epoch(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
        return float(value)
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()

def read_receipt(path: str | Path) -> tuple[str, Any]:
    receipt_path = Path(path).expanduser()
    label = receipt_path.name
    try:
        size = receipt_path.stat().st_size
        if size > MAX_RECEIPT_BYTES:
            return label, _RefusedReceipt("oversized")
        with receipt_path.open("rb") as handle:
            raw = handle.read(MAX_RECEIPT_BYTES + 1)
    except OSError:
        return label, _RefusedReceipt("unreadable")
    if len(raw) > MAX_RECEIPT_BYTES:
        return label, _RefusedReceipt("oversized")
    try:
        return label, json.loads(raw.decode("utf-8"))
    except (TypeError, ValueError, UnicodeDecodeError):
        return label, _RefusedReceipt("unreadable")

def bind_receipts(report: Mapping[str, Any], receipts: Sequence[tuple[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    session = report.get("session") if isinstance(report.get("session"), Mapping) else {}
    session_id = str(session.get("id") or "")
    started_at = session.get("started_at")
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for item in receipts:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            rejected.append({"receipt": "(malformed)", "unit_id": None, "reason": "ineligible_schema"})
            continue
        label, payload = item
        label = Path(str(label)).name
        if isinstance(payload, _RefusedReceipt):
            rejected.append({"receipt": label, "unit_id": None, "reason": payload.reason})
            continue
        if not isinstance(payload, Mapping) or payload.get("schema_version") != RECEIPT_SCHEMA_FANOUT_DISPATCH:
            rejected.append({"receipt": label, "unit_id": None, "reason": "ineligible_schema"})
            continue
        configuration = payload.get("contract_digest")
        observed_at = _receipt_epoch(payload.get("observed_at"))
        fanout_id = _safe_receipt_id(payload.get("fanout_id"))
        units = payload.get("units") if isinstance(payload.get("units"), list) else ()
        for unit in units:
            if not isinstance(unit, Mapping):
                continue
            unit_id = _safe_receipt_id(unit.get("unit_id"))
            origin = unit.get("origin_session_id") or payload.get("origin_session_id")
            reason = None
            if not isinstance(origin, str) or not origin: reason = "session_unbound"
            elif origin != session_id: reason = "foreign_session"
            elif _safe_receipt_id(unit.get("run_ref")) is None: reason = "run_unbound"
            elif unit_id is None or fanout_id is None: reason = "unit_unbound"
            elif not isinstance(configuration, str) or not _SHA256.fullmatch(configuration): reason = "configuration_unbound"
            elif observed_at is None or not isinstance(started_at, (int, float)) or isinstance(started_at, bool): reason = "freshness_unbound"
            elif observed_at < float(started_at): reason = "stale"
            if reason:
                rejected.append({"receipt": label, "unit_id": unit_id, "reason": reason})
                continue
            exit_code = unit.get("exit_code")
            accepted.append({"ref": f"receipt:{RECEIPT_SCHEMA_FANOUT_DISPATCH}#{fanout_id}/{unit_id}", "receipt": label, "schema_version": RECEIPT_SCHEMA_FANOUT_DISPATCH, "session_id": session_id, "run_id": str(unit["run_ref"]), "unit_id": unit_id, "configuration_digest": configuration, "observed_at": observed_at, "status": _safe_receipt_id(unit.get("status")), "exit_code": exit_code if isinstance(exit_code, int) and not isinstance(exit_code, bool) else None})
    by_identity: dict[tuple[str, str], set[str]] = {}
    for item in accepted:
        by_identity.setdefault((item["run_id"], item["unit_id"]), set()).add(item["configuration_digest"])
    conflicts = {key for key, values in by_identity.items() if len(values) > 1}
    kept: list[dict[str, Any]] = []
    seen_refs: set[str] = set()
    for item in accepted:
        key = (item["run_id"], item["unit_id"])
        if key in conflicts:
            rejected.append({"receipt": item["receipt"], "unit_id": item["unit_id"], "reason": "identity_conflict"})
        elif item["ref"] not in seen_refs:
            seen_refs.add(item["ref"])
            kept.append(item)
    return {"accepted": kept, "rejected": rejected}


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def report_digest(report: Mapping[str, Any]) -> str:
    return _digest({"session": report.get("session"), "turns": report.get("turns"), "findings": report.get("findings"), "unavailable": report.get("unavailable"), "budget": report.get("budget")})

def build_agent_failure_capture(report: Mapping[str, Any], *, observable: str = "unspecified", receipts: Sequence[tuple[str, Any]] = ()) -> dict[str, Any]:
    if agent_debug_report_errors(report):
        raise AgentDebugIncidentError("the report is not a valid agent_debug_report/v1")
    if observable not in OBSERVABLES:
        raise AgentDebugIncidentError(f"observable must be one of {', '.join(OBSERVABLES)}")
    source = report.get("source") or {}
    unavailable = [{"evidence": x.get("kind"), "reason": x.get("reason")} for x in report.get("unavailable") or ()]
    budget = report.get("budget") or {}
    if budget.get("oversized_rows"):
        unavailable.append({"evidence": "oversized_rows", "reason": "rows over the byte budget were not read"})
    if budget.get("row_limit_reached"):
        unavailable.append({"evidence": "rows_after_limit", "reason": "rows after the row budget were not read"})
    if budget.get("malformed_rows"):
        unavailable.append({"evidence": "malformed_rows", "reason": "malformed or non-object rows were not read"})
    unavailable.append({"evidence": "host_runtime", "reason": "live Hermes process, provider, and model state is not in the supplied record"})
    capture = {"schema_version": AGENT_FAILURE_CAPTURE_SCHEMA_VERSION, "identity": {"session_id": report["session"]["id"], "source_kind": source.get("kind"), "source_label": source.get("label"), "selection": source.get("selection"), "turns": dict(report.get("turns") or {}), "snapshot": dict(source.get("snapshot") or {}), "report_sha256": report_digest(report)}, "observable": observable, "observed_findings": [{"finding_id": x["finding_id"], "kind": x["kind"]} for x in report.get("findings") or ()], "finding_counts": dict(report.get("finding_counts") or {}), "checked_kinds": list(report.get("checked_kinds") or ()), "reading_complete": bool(budget.get("complete")), "unavailable": unavailable, "receipts": bind_receipts(report, receipts), "observed": True, "claim_boundary": INCIDENT_CLAIM_BOUNDARY}
    return capture


def agent_failure_capture_errors(capture: Mapping[str, Any], report: Mapping[str, Any]) -> list[str]:
    errors = list(agent_debug_report_errors(report))
    if capture.get("schema_version") != AGENT_FAILURE_CAPTURE_SCHEMA_VERSION: errors.append("capture schema_version is invalid")
    if (capture.get("identity") or {}).get("report_sha256") != report_digest(report): errors.append("capture report digest does not match")
    if capture.get("checked_kinds") != report.get("checked_kinds"): errors.append("checked_kinds must equal report")
    if capture.get("finding_counts") != report.get("finding_counts"): errors.append("finding_counts must equal report")
    if capture.get("observed") is not True or capture.get("claim_boundary") != INCIDENT_CLAIM_BOUNDARY: errors.append("capture boundary is invalid")
    if capture.get("observable") not in OBSERVABLES: errors.append("observable is invalid")
    return errors


def _evidence(pattern: str, findings: list[Mapping[str, Any]], checked: set[str], complete: bool) -> tuple[list[str], list[str], list[str]]:
    by_kind = {kind: [x for x in findings if x.get("kind") == kind] for kind in FINDING_KINDS}
    absence = PATTERNS[pattern][0]; unavailable: list[str] = []; evidence_for: list[str] = []; evidence_against: list[str] = []
    if pattern == OUTSIDE_RECORDED_EVIDENCE: return [], [], ["unavailable:host_runtime"]
    if absence and absence not in checked: unavailable.append(f"unavailable:{absence}")
    if not complete: unavailable.append("unavailable:unread_rows")
    if pattern == TOOL_ERROR_RETRY_LOOP:
        error_starts = {x["citation"]["message_ids"][0] for x in by_kind[TOOL_ERROR]}
        for retry in by_kind[IDENTICAL_RETRY_AFTER_ERROR]:
            (evidence_for if retry["citation"]["message_ids"][1] in error_starts else evidence_against).append(f"finding:{retry['finding_id']}")
    elif pattern == CONTEXT_LOSS_AFTER_COMPACTION:
        failures = [x["citation"]["message_ids"][0] for x in by_kind[TOOL_ERROR]]
        for boundary in by_kind[COMPACTION_BOUNDARY]:
            (evidence_for if any(ref > boundary["citation"]["message_ids"][0] for ref in failures) else evidence_against).append(f"finding:{boundary['finding_id']}")
    elif pattern == UNWATCHED_BACKGROUND_WORK:
        evidence_for.extend(f"finding:{x['finding_id']}" for x in by_kind[BACKGROUND_WITHOUT_NOTIFY])
    if absence and not by_kind[absence] and absence in checked and complete: evidence_against.append(f"absence:{absence}")
    return evidence_for, evidence_against, unavailable


def build_agent_failure_pattern_hypothesis(capture: Mapping[str, Any], report: Mapping[str, Any]) -> dict[str, Any]:
    if agent_failure_capture_errors(capture, report): raise AgentDebugIncidentError("agent_failure_capture/v1 failed validation")
    findings = list(report.get("findings") or ()); checked = set(capture.get("checked_kinds") or ()); complete = bool(capture.get("reading_complete")); hypotheses = []
    for index, pattern in enumerate(_OBSERVABLE_PATTERNS[capture["observable"]], 1):
        fore, against, unavailable = _evidence(pattern, findings, checked, complete)
        status = "supported" if fore else ("ruled_out" if any(x.startswith("absence:") for x in against) else "unresolved")
        confidence = "medium" if status == "supported" and len(fore) > 1 and not against else ("none" if status == "ruled_out" else "low")
        hypotheses.append({"hypothesis_id": f"H{index}", "pattern": pattern, "status": status, "confidence": confidence, "evidence_for": fore, "evidence_against": against, "unavailable_evidence": unavailable, "discriminator": PATTERNS[pattern][1], "observed": False})
    open_items = [x for x in hypotheses if x["status"] != "ruled_out"]; supported = [x for x in hypotheses if x["status"] == "supported"]; leading = max(supported, key=lambda x: len(x["evidence_for"]), default=None)
    return {"schema_version": AGENT_FAILURE_PATTERN_HYPOTHESIS_SCHEMA_VERSION, "session_id": capture["identity"]["session_id"], "capture_sha256": _digest(capture), "observable": capture["observable"], "hypotheses": hypotheses, "resolution": "unresolved" if len(open_items) > 1 else "single_candidate", "leading_hypothesis": leading["hypothesis_id"] if leading else None, "claim_boundary": INCIDENT_CLAIM_BOUNDARY}


def agent_failure_pattern_hypothesis_errors(artifact: Mapping[str, Any], capture: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    items = artifact.get("hypotheses")
    if artifact.get("schema_version") != AGENT_FAILURE_PATTERN_HYPOTHESIS_SCHEMA_VERSION: errors.append("hypothesis schema_version is invalid")
    if not isinstance(items, list) or len(items) < 2: errors.append("at least two competing hypotheses are required")
    if artifact.get("capture_sha256") != _digest(capture): errors.append("capture_sha256 does not match")
    if artifact.get("claim_boundary") != INCIDENT_CLAIM_BOUNDARY: errors.append("hypothesis boundary is invalid")
    if isinstance(items, list):
        ids = [x.get("hypothesis_id") for x in items if isinstance(x, Mapping)]
        if len(set(ids)) != len(ids): errors.append("hypothesis ids must be unique")
        for item in items:
            if not isinstance(item, Mapping) or item.get("pattern") not in PATTERNS or item.get("observed") is not False: errors.append("hypothesis pattern/observed value is invalid")
    return errors


def build_contained_recovery_action(hypothesis: Mapping[str, Any]) -> dict[str, Any]:
    lead = next((x for x in hypothesis.get("hypotheses") or () if x.get("hypothesis_id") == hypothesis.get("leading_hypothesis")), None)
    pattern = lead["pattern"] if lead else OUTSIDE_RECORDED_EVIDENCE; action = RECOVERY_ACTIONS[pattern]
    return {"schema_version": CONTAINED_RECOVERY_ACTION_SCHEMA_VERSION, "session_id": hypothesis.get("session_id"), "hypothesis_sha256": _digest(hypothesis), "for_hypothesis": lead.get("hypothesis_id") if lead else None, "action": action, "step": RECOVERY_STEPS[action], "targets": list(lead.get("evidence_for") or ()) if lead else [], "reversible": True, "requires_approval": True, "executed": False, "not_performed": list(NOT_PERFORMED), "claim_boundary": INCIDENT_CLAIM_BOUNDARY}


def contained_recovery_action_errors(artifact: Mapping[str, Any], hypothesis: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if artifact.get("schema_version") != CONTAINED_RECOVERY_ACTION_SCHEMA_VERSION: errors.append("recovery schema_version is invalid")
    if artifact.get("hypothesis_sha256") != _digest(hypothesis): errors.append("hypothesis_sha256 does not match")
    if artifact.get("executed") is not False or artifact.get("requires_approval") is not True or artifact.get("reversible") is not True: errors.append("recovery must be reversible, approval-gated, and unexecuted")
    if set(NOT_PERFORMED) - set(artifact.get("not_performed") or ()): errors.append("not_performed is incomplete")
    return errors


def build_agent_debug_incident(report: Mapping[str, Any], *, observable: str = "unspecified", receipts: Sequence[tuple[str, Any]] = ()) -> dict[str, Any]:
    capture = build_agent_failure_capture(report, observable=observable, receipts=receipts)
    hypothesis = build_agent_failure_pattern_hypothesis(capture, report)
    recovery = build_contained_recovery_action(hypothesis)
    return {"agent_failure_capture": capture, "agent_failure_pattern_hypothesis": hypothesis, "contained_recovery_action": recovery}


def agent_debug_incident_errors(report: Mapping[str, Any], incident: Mapping[str, Any] | None = None) -> list[str]:
    if incident is None: return ["incident is required"]
    capture, hypothesis, recovery = (incident.get(name) for name in ("agent_failure_capture", "agent_failure_pattern_hypothesis", "contained_recovery_action"))
    if not all(isinstance(x, Mapping) for x in (capture, hypothesis, recovery)): return ["incident must carry capture, hypothesis, and recovery"]
    return agent_failure_capture_errors(capture, report) + agent_failure_pattern_hypothesis_errors(hypothesis, capture) + contained_recovery_action_errors(recovery, hypothesis)


def format_agent_debug_incident(incident: Mapping[str, Any]) -> str:
    hypothesis = incident["agent_failure_pattern_hypothesis"]; recovery = incident["contained_recovery_action"]
    out = [f"Incident (observable {hypothesis.get('observable')})", f"Hypotheses ({hypothesis.get('resolution')})"]
    out.extend(f"  {x['hypothesis_id']} {x['pattern']}: {x['status']}" for x in hypothesis.get("hypotheses") or ())
    out.extend(["Contained recovery (proposed, requires approval, not executed)", f"  {recovery['action']}: {recovery['step']}"])
    return "\n".join(out)


def build_agent_debug_export(payload: Mapping[str, Any], *, hermes_home: str | Path | None = None, session_record: str | Path | None = None) -> dict[str, Any]:
    incident = payload.get("incident")
    if not isinstance(incident, Mapping): raise AgentDebugIncidentError("the payload carries no incident")
    report = payload.get("report") if isinstance(payload.get("report"), Mapping) else {key: value for key, value in payload.items() if key != "incident"}
    if not isinstance(report, Mapping): raise AgentDebugIncidentError("the payload carries no report")
    if agent_debug_incident_errors(report, incident): raise AgentDebugIncidentError("the payload failed validation")
    allowed = {"report", "incident"} if "report" in payload else {"incident", "schema_version", "source", "session", "turns", "budget", "counts", "checked_kinds", "unavailable", "findings", "finding_counts", "observed", "claim_boundary"}
    outside = sorted(set(payload) - allowed)
    if outside: raise AgentDebugIncidentError("the payload carries keys outside the export shape: " + ", ".join(outside))
    refs = [] if hermes_home is None and session_record is None else agent_debug_reference_errors(report, hermes_home=hermes_home, session_record=session_record)
    if refs: raise AgentDebugIncidentError("the report's references no longer hold: " + "; ".join(refs))
    redacted_report = dict(report); source = dict(redacted_report.get("source") or {}); source.pop("requested_session", None); source.pop("path", None); redacted_report["source"] = source
    package = {"schema_version": AGENT_DEBUG_EXPORT_SCHEMA_VERSION, "report": redacted_report, "incident": dict(incident), "redaction": {"dropped": ["source.path", "source.requested_session"], "never_read": ["prompts", "replies", "tool arguments", "tool output", "other sessions' rows"]}, "approval": {"requires_user_review": True, "uploaded": False, "issue_filed": False}, "claim_boundary": EXPORT_CLAIM_BOUNDARY}
    leaks = agent_debug_export_leaks(package)
    if leaks: raise AgentDebugIncidentError("the export failed its leak scan: " + "; ".join(leaks))
    return package

_RAW_KEYS = frozenset({"content", "prompt", "prompts", "messages", "arguments", "output", "result", "results", "transcript", "path", "text"})
_SECRET = re.compile(r"(?:AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{12,})")
_ABS = re.compile(r"(?:^|[\s\"'=(])(?:/[A-Za-z0-9._-]+/|~/|[A-Za-z]:\\)")
def agent_debug_export_leaks(package: Any) -> list[str]:
    leaks: list[str] = []
    def walk(value: Any, where: str) -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                if str(key) in _RAW_KEYS and str(key) not in {"path"}: leaks.append(f"{where}.{key} is a raw-material key")
                walk(item, f"{where}.{key}")
        elif isinstance(value, (list, tuple)):
            for i, item in enumerate(value): walk(item, f"{where}[{i}]")
        elif isinstance(value, str):
            if _ABS.search(value) or _SECRET.search(value) or len(value) > 600 or "\n" in value: leaks.append(f"{where} carries private material")
    walk(package, "package")
    return leaks


def agent_debug_export_target_problem(output: str | Path, *, hermes_home: str | Path | None = None, session_record: str | Path | None = None) -> str | None:
    target = Path(output).expanduser(); parent = target.parent.resolve()
    if not parent.is_dir(): return f"the export directory {parent.name} does not exist"
    resolved = parent / target.name
    if session_record is not None and resolved == Path(session_record).expanduser().resolve(): return "the export may not replace the session record"
    if os.path.lexists(resolved): return f"{resolved.name} already exists; an export never overwrites"
    return None


def write_agent_debug_export(package: Mapping[str, Any], output: str | Path, *, hermes_home: str | Path | None = None, session_record: str | Path | None = None) -> Path:
    leaks = agent_debug_export_leaks(package)
    if leaks: raise AgentDebugIncidentError("the export failed its leak scan: " + "; ".join(leaks))
    problem = agent_debug_export_target_problem(output, hermes_home=hermes_home, session_record=session_record)
    if problem: raise AgentDebugIncidentError(problem)
    target = Path(output).expanduser().parent.resolve() / Path(output).name
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try: fd = os.open(target, flags, 0o600)
    except FileExistsError: raise AgentDebugIncidentError(f"{target.name} already exists; an export never overwrites") from None
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle: handle.write(json.dumps(package, sort_keys=True, indent=2) + "\n")
    except OSError:
        try: target.unlink()
        except OSError: pass
        raise
    return target
