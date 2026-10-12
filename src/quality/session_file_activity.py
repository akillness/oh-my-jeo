"""Offline, bounded file-activity lineage for supplied Hermes JSONL records.

Only metadata from assistant tool calls and recorded tool outcomes is retained.
No named workspace file is opened, no Hermes state database is queried, and no
human author or source attribution is inferred.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import unicodedata
from typing import Any, Mapping, Sequence

SESSION_FILE_ACTIVITY_SCHEMA_VERSION = "session_file_activity/v1"
FILE_ACTIVITY_TOOLS = ("read_file", "write_file", "patch")
OUTCOMES = ("succeeded", "failed", "unknown")
OPERATIONS = ("read", "write", "update", "add", "delete", "move_from", "move_to")
OMISSION_REASONS = ("outside_workspace", "symlink_escape", "workspace_unknown", "relative_without_cwd", "home_relative", "url_like", "control_characters", "oversized", "malformed", "extension_guard", "focus")
DEFAULT_MAX_FILES = 100
DEFAULT_MAX_ROWS = 20_000
MAX_PATH_CHARS = 4096
ALLOWED_EXTENSIONS = frozenset({".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt", ".swift", ".c", ".h", ".cpp", ".json", ".yaml", ".yml", ".toml", ".md", ".txt", ".html", ".css", ".scss", ".sql", ".sh", ".bat", ".ps1"})
SESSION_FILE_ACTIVITY_CLAIM_BOUNDARY = (
    "Session file activity is a read-only projection of file-tool calls one supplied Hermes session persisted. "
    "A path is shown workspace-relative only when lexical and real-path containment both hold at query time; no named file is opened or read. "
    "Succeeded means Hermes recorded an outcome whose own fields report success; it is not file-content, diff, test, review, CI, or merge evidence. "
    "No human author or origin is inferred."
)
_OUTCOME_RULES = {
    "call": "one distinct tool call id per session; first assistant row decides arguments and first tool row decides result",
    "unknown": "no recorded result, an unknown effect, malformed result, or missing success field",
    "failed": "effect disposition none, truthy error, or patch success false",
    "succeeded": "read_file content; write_file bytes_written; patch success true, without an error",
    "patch_files": "a V4A patch applies its outcome to each file it declares",
    "timestamps": "the issuing assistant row timestamp, as UTC",
    "workspace": "the supplied workspace root; paths are never read",
}
_V4A_MARKERS = (("update", re.compile(r"^\*\*\*\s*Update\s+File:\s*(.+)$")), ("add", re.compile(r"^\*\*\*\s*Add\s+File:\s*(.+)$")), ("delete", re.compile(r"^\*\*\*\s*Delete\s+File:\s*(.+)$")))
_V4A_MOVE = re.compile(r"^\*\*\*\s*Move\s+File:\s*(.+?)\s*->\s*(.+)$")

class SessionFileActivityError(ValueError):
    pass


def _epoch(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)): return float(value)
    if not isinstance(value, str) or not value.strip(): return None
    try: parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError: return None
    if parsed.tzinfo is None: parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.timestamp()


def _stamp(value: Any) -> str | None:
    epoch = _epoch(value)
    return None if epoch is None else datetime.fromtimestamp(epoch, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _json(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)): value = bytes(value).decode("utf-8", "replace")
    if not isinstance(value, str): return value
    try: return json.loads(value)
    except (ValueError, TypeError): return None


def _bounded_lines(path: Path, max_bytes: int, max_rows: int = DEFAULT_MAX_ROWS) -> tuple[list[tuple[int, Mapping[str, Any]]], bool, int, int, list[int], list[int]]:
    rows: list[tuple[int, Mapping[str, Any]]] = []; truncated = False; bytes_read = bytes_skipped = 0; oversized: list[int] = []; malformed: list[int] = []
    try: handle = path.open("rb")
    except OSError as exc: raise SessionFileActivityError(f"could not read session record {path}: {exc.strerror or exc}") from exc
    try:
        number = 0
        while True:
            raw = handle.readline(max_bytes + 1)
            if not raw: break
            number += 1
            if number > max_rows: truncated = True; break
            if raw.endswith(b"\n") or len(raw) <= max_bytes:
                bytes_read += len(raw)
                try:
                    value = json.loads(raw.decode("utf-8", "replace"))
                except (TypeError, ValueError, json.JSONDecodeError):
                    malformed.append(number)
                    continue
                if isinstance(value, Mapping): rows.append((number, value))
                else: malformed.append(number)
            else:
                skipped = len(raw)
                while not raw.endswith(b"\n"):
                    raw = handle.readline(64 * 1024)
                    if not raw: break
                    skipped += len(raw)
                bytes_skipped += skipped; oversized.append(number)
    finally: handle.close()
    return rows, truncated, bytes_read, bytes_skipped, oversized, malformed


def _session(rows: Sequence[tuple[int, Mapping[str, Any]]], requested: str) -> tuple[str, str, list[tuple[int, Mapping[str, Any]]]]:
    sessions: dict[str, float] = {}
    for _, row in rows:
        sid = row.get("session_id")
        if isinstance(sid, str) and sid: sessions[sid] = max(sessions.get(sid, -math.inf), _epoch(row.get("timestamp")) or -math.inf)
    if not sessions: raise SessionFileActivityError("no Hermes session in supplied record")
    wanted = str(requested or "").strip()
    if wanted == "latest":
        latest = max(sessions.values()); matches = sorted(sid for sid, stamp in sessions.items() if stamp == latest)
        if len(matches) != 1: raise SessionFileActivityError("session 'latest' is ambiguous")
        resolved, basis = matches[0], "latest"
    elif wanted in sessions: resolved, basis = wanted, "exact"
    else:
        matches = sorted(sid for sid in sessions if sid.startswith(wanted))
        if len(matches) == 0: raise SessionFileActivityError(f"no Hermes session {wanted}")
        if len(matches) > 1: raise SessionFileActivityError(f"session {wanted!r} is ambiguous")
        resolved, basis = matches[0], "unique_prefix"
    return resolved, basis, [(line, row) for line, row in rows if row.get("session_id") == resolved]


def _calls(rows: Sequence[tuple[int, Mapping[str, Any]]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    calls: list[dict[str, Any]] = []; seen: set[str] = set(); results: dict[str, dict[str, Any]] = {}
    for line, row in rows:
        if row.get("role") == "tool":
            call_id = row.get("tool_call_id")
            if isinstance(call_id, str) and call_id and call_id not in results:
                results[call_id] = {"tool": str(row.get("tool_name") or ""), "content": row.get("content"), "effect": row.get("effect_disposition")}
        if row.get("role") != "assistant": continue
        raw_calls = _json(row.get("tool_calls")); raw_calls = raw_calls if isinstance(raw_calls, list) else []
        for call in raw_calls:
            if not isinstance(call, Mapping): continue
            call_id = call.get("id") or call.get("call_id")
            fn = call.get("function") if isinstance(call.get("function"), Mapping) else {}
            tool = str(fn.get("name") or call.get("name") or "")
            if not isinstance(call_id, str) or not call_id or tool not in FILE_ACTIVITY_TOOLS or call_id in seen: continue
            seen.add(call_id)
            args = fn.get("arguments", call.get("arguments")); args = _json(args) if isinstance(args, str) else args
            calls.append({"key": call_id, "id": call_id, "tool": tool, "arguments": args if isinstance(args, Mapping) else None, "at": _epoch(row.get("timestamp"))})
    return calls, results


def _patch_targets(value: Any) -> list[tuple[Any, str]]:
    if not isinstance(value, str): return []
    targets: list[tuple[Any, str]] = []
    for line in value.splitlines():
        move = _V4A_MOVE.match(line)
        if move: targets.extend(((move.group(1), "move_from"), (move.group(2), "move_to"))); continue
        for operation, pattern in _V4A_MARKERS:
            match = pattern.match(line)
            if match: targets.append((match.group(1).strip(), operation)); break
    return targets


def _targets(tool: str, arguments: Mapping[str, Any] | None) -> list[tuple[Any, str]]:
    if not isinstance(arguments, Mapping): return []
    if tool == "read_file": return [(arguments.get("path"), "read")] if "path" in arguments else []
    if tool == "write_file": return [(arguments.get("path"), "write")] if "path" in arguments else []
    patch = arguments.get("patch") or arguments.get("content")
    parsed = _patch_targets(patch)
    if parsed: return parsed
    return [(arguments.get("path"), "update")] if "path" in arguments else []


def _outcome(tool: str, result: Mapping[str, Any] | None) -> str:
    if not isinstance(result, Mapping): return "unknown"
    data = _json(result.get("content")); data = data if isinstance(data, Mapping) else result
    if result.get("effect") in {"unknown", "none"}: return "unknown" if result.get("effect") == "unknown" else "failed"
    if isinstance(data, Mapping) and data.get("error"): return "failed"
    if tool == "read_file": return "succeeded" if isinstance(data, Mapping) and "content" in data else "unknown"
    if tool == "write_file": return "succeeded" if isinstance(data, Mapping) and "bytes_written" in data else "unknown"
    if tool == "patch":
        if isinstance(data, Mapping) and data.get("success") is False: return "failed"
        return "succeeded" if isinstance(data, Mapping) and data.get("success") is True else "unknown"
    return "unknown"


def _normalize_root(value: str | Path | None) -> tuple[Path | None, str]:
    if value is None: return None, "unknown"
    text = unicodedata.normalize("NFKC", str(value)).strip()
    if not text or "\x00" in text: return None, "unknown"
    path = Path(os.path.abspath(os.path.expanduser(text)))
    if not path.is_absolute(): return None, "unknown"
    return path, "provided_workspace"


def _focus_values(focus: str | Sequence[str] | None, focus_prefix: str | Sequence[str] | None) -> tuple[str, ...] | None:
    value = focus if focus is not None else focus_prefix
    if value is None: return None
    vals = [value] if isinstance(value, str) else list(value)
    out: list[str] = []
    for item in vals:
        if not isinstance(item, str): raise SessionFileActivityError("focus must be a workspace-relative path prefix")
        raw_normalized = unicodedata.normalize("NFKC", item).replace("\\", "/").strip()
        if raw_normalized.startswith(("/", "~")): raise SessionFileActivityError("focus must be workspace-relative")
        normalized = raw_normalized.strip("/")
        if not normalized or ".." in normalized.split("/"):
            raise SessionFileActivityError("focus must be workspace-relative")
        out.append(normalized)
    return tuple(dict.fromkeys(out))


def _relative(raw: Any, root: Path | None, real_root: Path | None, *, focus: tuple[str, ...] | None) -> tuple[str | None, str]:
    if not isinstance(raw, str) or not raw.strip(): return None, "malformed"
    text = unicodedata.normalize("NFKC", raw.strip()).replace("\\", "/")
    if len(text) > MAX_PATH_CHARS: return None, "oversized"
    if any(ord(ch) < 32 for ch in text): return None, "control_characters"
    if re.match(r"^(?:[a-z]+:|//)", text, re.I): return None, "url_like"
    if text.startswith("~"): return None, "home_relative"
    if root is None: return None, "workspace_unknown"
    candidate = Path(text)
    lexical = Path(os.path.normpath(text)) if candidate.is_absolute() else Path(os.path.normpath(str(root / candidate)))
    try:
        relative = lexical.relative_to(root).as_posix()
    except ValueError:
        return None, "outside_workspace"
    if focus is not None and not any(relative == prefix or relative.startswith(prefix + "/") for prefix in focus): return None, "focus"
    extension = Path(relative).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS: return None, "extension_guard"
    try:
        resolved = Path(os.path.realpath(lexical))
        resolved.relative_to(real_root or Path(os.path.realpath(root)))
    except ValueError: return None, "symlink_escape"
    return relative, ""


def _record(files: dict[str, dict[str, Any]], path: str, extension: str, operation: str, outcome: str, at: float | None) -> None:
    entry = files.setdefault(path, {"path": path, "extension": extension, "path_sha256": hashlib.sha256(path.encode("utf-8")).hexdigest()[:16], "activity": {}, "first_epoch": None, "last_epoch": None})
    if at is not None:
        entry["first_epoch"] = at if entry["first_epoch"] is None else min(entry["first_epoch"], at)
        entry["last_epoch"] = at if entry["last_epoch"] is None else max(entry["last_epoch"], at)
    key = (operation, outcome); item = entry["activity"].setdefault(key, {"operation": operation, "outcome": outcome, "calls": 0}); item["calls"] += 1


def build_session_file_activity(
    hermes_home: str | Path | None,
    session_id: str,
    *,
    session_record: str | Path | None = None,
    workspace: str | Path | None = None,
    max_files: int = DEFAULT_MAX_FILES,
    focus: str | Sequence[str] | None = None,
    focus_prefix: str | Sequence[str] | None = None,
    max_rows: int = DEFAULT_MAX_ROWS,
    max_row_bytes: int = 256 * 1024,
) -> dict[str, Any]:
    if max_files < 1: raise SessionFileActivityError("--max-files must be at least 1")
    if max_rows < 1 or max_row_bytes < 1: raise SessionFileActivityError("row and byte budgets must be at least 1")
    if session_record is None: raise SessionFileActivityError("an operator-supplied session record is required; live Hermes state.db is not read")
    path = Path(session_record)
    try: info = path.stat()
    except OSError as exc: raise SessionFileActivityError(f"no session record at {path}: {exc.strerror or exc}") from exc
    if not path.is_file(): raise SessionFileActivityError(f"session record {path} is not a regular file")
    rows, truncated, bytes_read, bytes_skipped, oversized, malformed = _bounded_lines(path, max_row_bytes, max_rows)
    if str(session_id or "").strip() == "latest" and truncated:
        raise SessionFileActivityError("latest selection is unavailable after the row budget was reached; provide an exact session id")
    resolved, selection, selected = _session(rows, session_id)
    focus_values = _focus_values(focus, focus_prefix)
    root, basis = _normalize_root(workspace)
    real_root = Path(os.path.realpath(root)) if root is not None else None
    calls, results = _calls(selected)
    files: dict[str, dict[str, Any]] = {}
    omitted = {reason: 0 for reason in OMISSION_REASONS}; by_tool = {name: 0 for name in FILE_ACTIVITY_TOOLS}; by_outcome = {name: 0 for name in OUTCOMES}
    for call in calls:
        by_tool[call["tool"]] += 1
        result = results.get(call["id"]); outcome = _outcome(call["tool"], result); by_outcome[outcome] += 1
        targets = _targets(call["tool"], call.get("arguments"))
        if not targets: omitted["malformed"] += 1; continue
        for raw, operation in targets:
            relative, reason = _relative(raw, root, real_root, focus=focus_values)
            if relative is None: omitted[reason] += 1; continue
            _record(files, relative, Path(relative).suffix.lower(), operation, outcome, call.get("at"))
    ordered = sorted(files.values(), key=lambda x: (x["first_epoch"] is None, x["first_epoch"] or 0.0, x["path"]))
    focus_output = list(focus_values or ())
    shown = []
    for item in ordered[:max_files]:
        shown.append({"path": item["path"], "extension": item["extension"], "path_sha256": item["path_sha256"], "activity": [item["activity"][key] for key in sorted(item["activity"], key=lambda pair: (OPERATIONS.index(pair[0]) if pair[0] in OPERATIONS else 99, pair[1]))], "first_at": _stamp(item["first_epoch"]), "last_at": _stamp(item["last_epoch"])})
    digests = {item["path"]: item["path_sha256"] for item in shown}
    return {"schema_version": SESSION_FILE_ACTIVITY_SCHEMA_VERSION, "source": {"kind": "session_record", "label": path.name, "session_id": resolved, "selection": selection, "snapshot": {"bytes": int(info.st_size), "mtime_ns": int(info.st_mtime_ns)}}, "workspace": {"basis": basis, "established": root is not None}, "focus": focus_output, "tools": list(FILE_ACTIVITY_TOOLS), "calls": {"total": len(calls), "by_tool": by_tool, "by_outcome": by_outcome, "results_without_call": sum(1 for key in results if key not in {call["id"] for call in calls})}, "files": shown, "digests": {"paths": digests}, "file_count": len(ordered), "shown_file_count": len(shown), "max_files": max_files, "truncated": len(ordered) > max_files, "omitted_file_count": len(ordered) - len(shown), "omitted_paths": {"count": sum(omitted.values()), "by_reason": omitted}, "budget": {"max_rows": max_rows, "max_row_bytes": max_row_bytes, "rows_read": len(rows), "bytes_read": bytes_read, "bytes_skipped": bytes_skipped, "oversized_rows": len(oversized), "truncated": truncated}, "rules": dict(_OUTCOME_RULES), "observed": True, "claim_boundary": SESSION_FILE_ACTIVITY_CLAIM_BOUNDARY}


def format_session_file_activity_summary(payload: Mapping[str, Any]) -> str:
    source = payload.get("source") or {}; workspace = payload.get("workspace") or {}; calls = payload.get("calls") or {}
    out = [f"Session file activity: session {source.get('session_id')}", f"  workspace basis: {workspace.get('basis')}    files: {int(payload.get('file_count', 0))}    calls: {int(calls.get('total', 0))}", "Files"]
    for entry in payload.get("files") or ():
        activity = ", ".join(f"{item['operation']} {item['outcome']} x{item['calls']}" for item in entry.get("activity") or ())
        out.append(f"  {entry['path']}: {activity}    {entry.get('first_at')} .. {entry.get('last_at')}")
    omitted = payload.get("omitted_paths") or {}; reasons = {key: value for key, value in (omitted.get("by_reason") or {}).items() if value}
    if reasons: out.append("Omitted: " + "  ".join(f"{key} {value}" for key, value in reasons.items()))
    if payload.get("truncated"): out.append(f"  truncated: showing {payload.get('shown_file_count')} of {payload.get('file_count')} files")
    out.extend(["Boundary", f"  {payload.get('claim_boundary', SESSION_FILE_ACTIVITY_CLAIM_BOUNDARY)}"])
    return "\n".join(out)
