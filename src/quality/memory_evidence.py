"""Read-only, metadata-only evidence for OMJ project memory.

This module deliberately does not inspect Hermes' native memory or state DB.  It
summarises the OMJ local store through the canonical memory scanner and, when
explicitly supplied, structured session JSONL traffic.  It never reports raw
summaries, arguments, message content, or arbitrary status strings.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

from ..paths import OmjPaths
from ..workflows.memory import _MAX_MEMORY_JSON_DEPTH

MEMORY_EVIDENCE_SCHEMA_VERSION = "memory_evidence/v1"
DEFAULT_WINDOW_DAYS = 7
DAY_SECONDS = 86_400
READ = "read"
PARTIAL = "partial"
MISSING = "missing"
UNREADABLE = "unreadable"
NOT_REQUESTED = "not_requested"
UNSUPPORTED = "unsupported"
NO_RESULT_LABEL = "(no_result)"
UNPARSED_LABEL = "(unparsed)"
OTHER_LABEL = "(other)"
MAX_SESSION_LINE_BYTES = 1_048_576
DEFAULT_MAX_ROWS = 20_000

# Only statuses emitted by OMJ's memory protocol are retained.  Keeping this
# closed prevents credentials or arbitrary tool output from entering reports.
_MEMORY_ACTIONS = frozenset({"capture", "status", "confirm", "demote", "correct", "retire"})
_MEMORY_STATUSES = frozenset({"remembered", "pending_review", "demoted", "confirmed", "corrected", "retired"})
_SAFE_LABEL = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,47}$")

MEMORY_EVIDENCE_CLAIM_BOUNDARY = (
    "Memory evidence is a read-only projection of OMJ-local record/candidate snapshots and, when explicitly supplied, "
    "structured session metadata. It does not prove native Hermes memory reads, prefetch, serving, model use, freed entries, "
    "answer improvement, execution, review, CI, merge, or correctness of any memory claim."
)


class MemoryEvidenceError(ValueError):
    """Raised when report arguments are malformed before any source is read."""


def build_memory_evidence(
    paths: OmjPaths,
    *,
    days: int | None = DEFAULT_WINDOW_DAYS,
    since: str | float | int | None = None,
    now: float | None = None,
    session_jsonl: str | Path | None = None,
    max_rows: int | None = None,
) -> dict[str, Any]:
    """Build a bounded memory evidence payload without writing any source.

    ``days`` and ``since`` are mutually exclusive at the CLI.  A direct caller
    may leave the default ``days`` in place when supplying ``since``; any other
    combination is rejected before source I/O.  Window boundaries are inclusive
    at ``since`` and bounded by ``until`` (the observation clock).
    """
    moment = _validate_now(now)
    row_limit = _validate_max_rows(max_rows)
    since_epoch, resolved_days = _resolve_window(days=days, since=since, now=moment)
    window = {
        "days": resolved_days,
        "since": _iso(since_epoch),
        "until": _iso(moment),
        "since_epoch": since_epoch,
        "until_epoch": moment,
        "boundary": "since_inclusive_until_inclusive",
    }

    store = _store_counts(paths, since_epoch, moment)
    traffic = _session_counts(session_jsonl, since_epoch, moment, max_rows=row_limit)
    native = {
        "read_state": UNSUPPORTED,
        "observed": False,
        "headroom": None,
        "freed_entries": None,
        "demotion": None,
        "prefetch": None,
        "claim_boundary": "Native Hermes memory/provider state is outside OMJ evidence scope.",
    }
    prepared = {
        "read_state": UNSUPPORTED,
        "observed": False,
        "prepared": None,
        "served": None,
        "used": None,
        "confirmed_status_observed": False,
        "claim_boundary": "Prepared attachments are not served/use evidence.",
    }

    unread_sources: list[dict[str, str]] = []
    if str(store.get("read_state")) != READ:
        unread_sources.append(_source_state("omj_store", store))
    if str(traffic.get("read_state")) not in {READ, NOT_REQUESTED}:
        unread_sources.append(_source_state("session_records", traffic))
    payload: dict[str, Any] = {
        "schema_version": MEMORY_EVIDENCE_SCHEMA_VERSION,
        "homes": {"omj_home": str(paths.omj_home)},
        "window": window,
        "omj_store": store,
        "session_records": traffic,
        "native_memory": native,
        "prepared_attachments": prepared,
        "unread_sources": unread_sources,
        "ok": not unread_sources,
        "redaction_policy": "metadata_only",
        "claim_boundary": MEMORY_EVIDENCE_CLAIM_BOUNDARY,
        "counting": {
            "records": "current admitted OMJ record snapshot; no historical event inference",
            "candidates": "current OMJ candidate snapshot, including status labels",
            "traffic": "distinct session_id + call_id; structured timestamp only",
            "writes": "closed memory action/status pairs observed in a result; confirm is status-only",
        },
    }
    payload["headline"] = memory_evidence_headline(payload)
    return payload


def memory_evidence_headline(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Derive honest headline claims from report counts, never stored prose."""
    window = payload.get("window") if isinstance(payload.get("window"), Mapping) else {}
    span = f"last {window.get('days')} days" if window.get("days") else f"since {window.get('since')}"
    store = payload.get("omj_store") if isinstance(payload.get("omj_store"), Mapping) else {}
    records = store.get("records") if isinstance(store.get("records"), Mapping) else {}
    candidates = store.get("candidates") if isinstance(store.get("candidates"), Mapping) else {}
    store_read = store.get("read_state") == READ
    claims = (
        ("OMJ records", "current admitted OMJ-local record snapshot", "omj_store.records.total", records, "total"),
        ("OMJ candidates", "current OMJ-local candidate snapshot; candidates are not admitted records", "omj_store.candidates.total", candidates, "total"),
        ("OMJ candidates created in window", "candidates with created_at inside the reported window; distinct from the current candidate snapshot", "omj_store.candidates.created_in_window", candidates, "created_in_window"),
    )
    output: list[dict[str, Any]] = []
    for label, meaning, derived_from, section, key in claims:
        value = section.get(key)
        count = int(value) if store_read and isinstance(value, int) and not isinstance(value, bool) else None
        observed = count is not None
        period = meaning if key == "total" else span
        output.append(
            {
                "claim": f"{count} {label} ({period})" if observed else f"{label}: not observed, the source was not fully read ({period})",
                "count": count,
                "observed": observed,
                "meaning": meaning,
                "derived_from": derived_from,
            }
        )
    return output


def format_memory_evidence_summary(payload: Mapping[str, Any]) -> str:
    """Render metadata-only text from the same payload used for JSON output."""
    window = payload.get("window") if isinstance(payload.get("window"), Mapping) else {}
    span = f"last {window.get('days')} days" if window.get("days") else f"since {window.get('since')}"
    store = payload.get("omj_store") if isinstance(payload.get("omj_store"), Mapping) else {}
    records = store.get("records") if isinstance(store.get("records"), Mapping) else {}
    candidates = store.get("candidates") if isinstance(store.get("candidates"), Mapping) else {}
    traffic = payload.get("session_records") if isinstance(payload.get("session_records"), Mapping) else {}
    calls = traffic.get("calls") if isinstance(traffic.get("calls"), Mapping) else {}
    lines = [
        f"OMJ memory evidence: {span}",
        f"  OMJ records ({store.get('read_state')}): {records.get('total')}",
        f"  OMJ candidates ({store.get('read_state')}): {candidates.get('total')}",
        f"  Session records ({traffic.get('read_state')}): {calls.get('total')}",
        "Headline",
    ]
    lines.extend(f"  {row.get('claim')}" for row in payload.get("headline") or () if isinstance(row, Mapping))
    if traffic.get("read_state") not in {READ, NOT_REQUESTED} and traffic.get("error"):
        lines.append(f"  session source: {traffic.get('read_state')}")
    lines.append("Boundary")
    lines.append(f"  {payload.get('claim_boundary', MEMORY_EVIDENCE_CLAIM_BOUNDARY)}")
    return "\n".join(lines)


def _store_counts(paths: OmjPaths, since_epoch: float, until_epoch: float) -> dict[str, Any]:
    """Count metadata snapshots returned by Memory's canonical scanner."""
    try:
        from ..workflows.memory import scan_governed_memory
    except ImportError as exc:  # pragma: no cover - central owner supplies this API
        return _unread_store("canonical scanner unavailable", error=type(exc).__name__)
    try:
        scanned = scan_governed_memory(
            paths,
            query=None,
            source=None,
            now=datetime.fromtimestamp(until_epoch, tz=timezone.utc),
            limit=None,
        )
    except (OSError, ValueError) as exc:
        return _unread_store("canonical scanner unreadable", error=type(exc).__name__)
    if not isinstance(scanned, Mapping):
        return _unread_store("canonical scanner returned invalid data", error="invalid_scanner_result")
    raw_state = scanned.get("read_state")
    scanner_states = {"complete", READ, "absent", "refused", PARTIAL, "budget_exceeded", MISSING, UNREADABLE}
    shape_invalid = raw_state not in scanner_states if isinstance(raw_state, str) else True
    scanner_state = raw_state if not shape_invalid else PARTIAL
    scanner_budget = scanned.get("budget") if isinstance(scanned.get("budget"), Mapping) else {}
    complete = (
        scanner_state in {"complete", READ, "absent"}
        and scanned.get("complete") is True
        and not scanned.get("limit_reached")
        and scanner_budget.get("complete") is True
        and not scanned.get("errors")
    )
    state = READ if complete else PARTIAL
    records_value = scanned.get("records")
    candidates_value = scanned.get("candidates")
    if not isinstance(records_value, list) or not isinstance(candidates_value, list):
        shape_invalid = True
    records = _mapping_list(records_value)
    candidates = _mapping_list(candidates_value)
    if isinstance(records_value, list) and len(records) != len(records_value):
        shape_invalid = True
    if isinstance(candidates_value, list) and len(candidates) != len(candidates_value):
        shape_invalid = True
    if any(not isinstance(record.get("admitted"), bool) for record in records):
        shape_invalid = True
    findings = _mapping_list(scanned.get("findings"))
    record_refusals = _mapping_list(scanned.get("record_refusals") or scanned.get("refused_records"))
    candidate_refusals = _mapping_list(scanned.get("candidate_refusals") or scanned.get("refused_candidates"))
    if not record_refusals:
        record_refusals = [{"reason": row.get("diagnostic")} for row in findings if row.get("kind") == "record"]
    if not candidate_refusals:
        candidate_refusals = [{"reason": row.get("diagnostic")} for row in findings if row.get("kind") == "candidate"]

    by_source: dict[str, int] = {}
    by_admission: dict[str, int] = {}
    record_total = 0
    pending_active = 0
    not_admitted = 0
    by_unadmitted: dict[str, int] = {}
    record_created = 0
    record_ambiguous = 0
    record_future = 0
    for record in records:
        admission_state = _store_label(record.get("admission_state"), "admission")
        if record.get("admitted") is not True:
            not_admitted += 1
            pending_active += admission_state == "pending_review"
            _increment(by_unadmitted, admission_state)
            continue
        record_total += 1
        _increment(by_source, _store_label(record.get("source"), "source"))
        _increment(by_admission, admission_state)
        timestamp = _epoch(record.get("created_at"))
        if timestamp is None:
            record_ambiguous += 1
            continue
        if timestamp > until_epoch:
            record_future += 1
            continue
        if timestamp < since_epoch:
            continue
        record_created += 1

    by_status: dict[str, int] = {}
    candidate_created = 0
    candidate_ambiguous = 0
    candidate_future = 0
    for candidate in candidates:
        timestamp = _epoch(candidate.get("created_at"))
        if timestamp is None:
            candidate_ambiguous += 1
            continue
        if timestamp > until_epoch:
            candidate_future += 1
            continue
        if timestamp < since_epoch:
            continue
        candidate_created += 1
        _increment(by_status, _store_label(candidate.get("status"), "status"))

    if shape_invalid:
        state = PARTIAL
    sources: dict[str, dict[str, Any]] = {}
    scanned_sources = scanned.get("sources")
    if isinstance(scanned_sources, Mapping):
        for kind in ("records", "candidates"):
            source = scanned_sources.get(kind)
            if not isinstance(source, Mapping):
                state = PARTIAL
                continue
            source_state = source.get("read_state")
            source_complete = source.get("complete") is True and isinstance(source_state, str) and source_state in {READ, "absent", "complete"}
            sources[kind] = {
                "read_state": source_state if isinstance(source_state, str) and source_state in scanner_states else PARTIAL,
                "complete": source_complete,
                **{key: value for key in ("entries_scanned", "files_inspected", "bytes_read")
                   if isinstance(value := source.get(key), int) and not isinstance(value, bool) and value >= 0},
            }
            if not source_complete:
                state = PARTIAL
    section: dict[str, Any] = {
        "read_state": state,
        "scanner_read_state": scanner_state,
        "complete": state == READ,
        "sources": sources,
        "budget": {
            **{key: value for key in ("max_files", "files_inspected", "entries_scanned", "max_file_bytes", "bytes_read")
               if isinstance(value := scanner_budget.get(key), int) and not isinstance(value, bool) and value >= 0},
            "complete": state == READ,
            "limit_reached": bool(scanned.get("limit_reached")),
        },
        "memory_dir": str(paths.memory_dir),
        "records": {
            "total": record_total if state == READ else None,
            "observed_total": record_total,
            "created_in_window": record_created if state == READ else None,
            "by_admission_state": dict(sorted(by_admission.items())),
            "by_source": dict(sorted(by_source.items())),
            "inspected_total": len(records),
            "pending_active": pending_active,
            "not_admitted": not_admitted,
            "by_unadmitted_state": dict(sorted(by_unadmitted.items())),
            "refused_files_by_reason": _refusal_counts(record_refusals),
            "ambiguous_timestamps": record_ambiguous,
            "future_timestamps": record_future,
        },
        "candidates": {
            "total": len(candidates) if state == READ else None,
            "observed_total": len(candidates),
            "created_in_window": candidate_created if state == READ else None,
            "by_status": dict(sorted(by_status.items())),
            "refused_files_by_reason": _refusal_counts(candidate_refusals),
            "ambiguous_timestamps": candidate_ambiguous,
            "future_timestamps": candidate_future,
        },
    }
    if state != READ:
        section["error"] = "canonical scanner returned incomplete source" if shape_invalid else "canonical scanner reported incomplete source"
    return section


def _session_counts(path_value: str | Path | None, since_epoch: float, until_epoch: float, *, max_rows: int) -> dict[str, Any]:
    if path_value is None:
        return {
            "read_state": NOT_REQUESTED,
            "path": None,
            "calls": {"total": None, "by_action_status": {}},
            "writes": {"observed": None, "confirmed_status_only": None},
            "results_without_call": None,
            "unknown_traffic": None,
            "window": {},
            "budget": {"complete": True, "row_limit_reached": False, "max_rows": max_rows, "malformed_rows": 0},
        }
    path = Path(path_value).expanduser()
    try:
        source_size = path.stat().st_size
        if not path.is_file():
            return _unread_session(path, UNREADABLE, "not a regular file", max_rows)
    except FileNotFoundError:
        return _unread_session(path, MISSING, "source not found", max_rows)
    except OSError as exc:
        return _unread_session(path, UNREADABLE, type(exc).__name__, max_rows)
    rows: list[Mapping[str, Any]] = []
    malformed: list[int] = []
    oversized: list[int] = []
    row_limit_reached = False
    byte_limit_reached = False
    bytes_read = 0
    try:
        with path.open("rb") as handle:
            line_no = 0
            while bytes_read < MAX_SESSION_LINE_BYTES:
                if line_no >= max_rows:
                    probe = handle.read(1)
                    bytes_read += len(probe)
                    row_limit_reached = bool(probe)
                    break
                remaining = MAX_SESSION_LINE_BYTES - bytes_read
                raw = handle.readline(remaining)
                bytes_read += len(raw)
                if not raw:
                    break
                line_no += 1
                if not raw.endswith(b"\n") and bytes_read == MAX_SESSION_LINE_BYTES and source_size > bytes_read:
                    byte_limit_reached = True
                    if len(raw) == MAX_SESSION_LINE_BYTES:
                        oversized.append(line_no)
                    break
                try:
                    value = _json_value(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError, RecursionError):
                    malformed.append(line_no)
                    continue
                if isinstance(value, Mapping):
                    rows.append(value)
                else:
                    malformed.append(line_no)
            if bytes_read == MAX_SESSION_LINE_BYTES and source_size > bytes_read:
                byte_limit_reached = True
    except OSError as exc:
        section = _unread_session(path, UNREADABLE, type(exc).__name__, max_rows)
        section["budget"].update({"bytes_read": bytes_read, "rows_read": len(rows), "max_bytes": MAX_SESSION_LINE_BYTES})
        return section
    calls, result_rows, unknown, window, refused_rows = _classify_session(rows, since_epoch, until_epoch)
    complete = not (malformed or refused_rows or oversized or row_limit_reached or byte_limit_reached or window["ambiguous_timestamps"])
    status = READ if complete else PARTIAL
    section: dict[str, Any] = {
        "read_state": status,
        "path": str(path),
        "calls": {"total": len(calls) if complete else None, "observed_total": len(calls), "by_action_status": _calls_by_action(calls)},
        "writes": {
            "observed": sum(1 for call in calls if call.write_observed) if complete else None,
            "confirmed_status_only": sum(1 for call in calls if call.confirmed_only) if complete else None,
        },
        "results_without_call": result_rows if complete else None,
        "unknown_traffic": unknown + len(malformed) + refused_rows,
        "window": window,
        "budget": {
            "complete": complete,
            "row_limit_reached": row_limit_reached,
            "byte_limit_reached": byte_limit_reached,
            "max_bytes": MAX_SESSION_LINE_BYTES,
            "max_rows": max_rows,
            "rows_read": len(rows),
            "bytes_read": bytes_read,
            "malformed_rows": len(malformed) + refused_rows,
            "oversized_rows": len(oversized),
        },
    }
    if status != READ:
        section["error"] = "session source was only partially read"
    return section


@dataclass
class _ObservedCall:
    session_id: str
    call_id: str
    action: str
    status: str
    timestamp: float | None
    result_present: bool
    write_observed: bool = False
    confirmed_only: bool = False


def _classify_session(rows: Iterable[Mapping[str, Any]], since_epoch: float, until_epoch: float) -> tuple[list[_ObservedCall], int, int, dict[str, int], int]:
    calls: dict[tuple[str, str], dict[str, Any]] = {}
    results: dict[tuple[str, str], tuple[str, Any, float | None]] = {}
    unknown_keys: dict[tuple[str, str], float | None] = {}
    ambiguous_keys: set[tuple[str, str]] = set()
    refused_rows: set[int] = set()
    included_boundary = 0
    excluded_before = 0
    excluded_after = 0
    for row_number, row in enumerate(rows):
        session = row.get("session_id")
        sid = str(session) if isinstance(session, str) and session else "(unknown_session)"
        stamp = _epoch(row.get("timestamp"))
        role = row.get("role")
        if role == "assistant":
            try:
                entries = _json_value(row.get("tool_calls"))
            except RecursionError:
                refused_rows.add(row_number)
                continue
            if not isinstance(entries, list):
                continue
            for entry in entries:
                try:
                    call_id, name, arguments, accepted = _extract_call(entry)
                except RecursionError:
                    refused_rows.add(row_number)
                    continue
                if not call_id:
                    continue
                key = (sid, call_id)
                if name == "omj_memory" and accepted:
                    if stamp is None:
                        ambiguous_keys.add(key)
                    if key not in calls:
                        calls[key] = {"action": _action(arguments), "timestamp": stamp}
                    continue
                unknown_keys.setdefault(key, stamp)
        elif role == "tool":
            call_id = row.get("tool_call_id")
            if not isinstance(call_id, str) or not call_id:
                continue
            key = (sid, call_id)
            name = row.get("tool_name")
            try:
                content = _json_value(row.get("content"))
            except RecursionError:
                refused_rows.add(row_number)
                continue
            results.setdefault(key, (str(name or ""), content, stamp))
            if name == "omj_memory" and stamp is None:
                ambiguous_keys.add(key)
            if str(name or "") not in {"omj_memory", "tool_call"}:
                unknown_keys.setdefault(key, stamp)
    observed: list[_ObservedCall] = []
    for key, item in calls.items():
        sid, call_id = key
        stamp = item.get("timestamp")
        result = results.get(key)
        status = NO_RESULT_LABEL
        result_present = False
        result_value: Any = None
        if result is not None:
            result_present = True
            result_value = result[1]
            if isinstance(result_value, Mapping):
                status = _status(result_value.get("status"))
            else:
                status = UNPARSED_LABEL
        # A refused generic wrapper is not a memory call, even when the tool
        # row says tool_call.  Its key remains unknown traffic only.  This is
        # checked ahead of the ambiguous/window filters below so a refusal is
        # still disclosed when the assistant row itself lacks a usable
        # timestamp; the tool row's own timestamp is used as a fallback.
        if result is not None and result[0] == "tool_call" and isinstance(result_value, Mapping) and "error" in result_value:
            unknown_keys.setdefault(key, stamp if stamp is not None else result[2])
            continue
        if stamp is None or key in ambiguous_keys or (result is not None and result[2] is None):
            ambiguous_keys.add(key)
            continue
        if stamp < since_epoch:
            excluded_before += 1
            continue
        if stamp > until_epoch:
            excluded_after += 1
            continue
        if stamp == since_epoch:
            included_boundary += 1
        action = _action(result_value.get("action")) if isinstance(result_value, Mapping) and "action" in result_value else item["action"]
        write_observed = (action, status) in {
            ("capture", "remembered"),
            ("capture", "pending_review"),
            ("demote", "demoted"),
            ("demote", "pending_review"),
            ("correct", "corrected"),
            ("correct", "pending_review"),
            ("retire", "retired"),
        }
        confirmed_only = action == "confirm" and status == "confirmed"
        observed.append(_ObservedCall(sid, call_id, action, status, stamp, result_present, write_observed, confirmed_only))
    # Result-only memory rows are disclosed separately and are never calls.
    results_without_call = sum(1 for (sid, call_id), (name, _value, stamp) in results.items() if name == "omj_memory" and (sid, call_id) not in calls and _in_bounds(stamp, since_epoch, until_epoch))
    for key in ambiguous_keys:
        unknown_keys[key] = None
    unknown = 0
    for key, unknown_stamp in unknown_keys.items():
        if key in ambiguous_keys:
            unknown += 1
            continue
        stamp = unknown_stamp
        if stamp is None:
            stamp = calls.get(key, {}).get("timestamp")
        if stamp is None and key in results:
            stamp = results[key][2]
        # Unrelated/refused traffic proves itself by existing in this scan; a
        # timestamp that cannot be resolved from the row, its call, or its
        # result must never silently drop the count to zero.
        if stamp is None or _in_bounds(stamp, since_epoch, until_epoch):
            unknown += 1
    return observed, results_without_call, unknown, {
        "included_at_boundary": included_boundary,
        "excluded_before_since": excluded_before,
        "excluded_after_until": excluded_after,
        "ambiguous_timestamps": len(ambiguous_keys),
    }, len(refused_rows)


def _extract_call(entry: Any) -> tuple[str | None, str | None, Any, bool]:
    if not isinstance(entry, Mapping):
        return None, None, None, False
    call_id = entry.get("id") or entry.get("call_id")
    if not isinstance(call_id, str) or not call_id:
        return None, None, None, False
    fn = entry.get("function") if isinstance(entry.get("function"), Mapping) else entry
    name = fn.get("name")
    arguments = fn.get("arguments")
    arguments = _json_value(arguments) if isinstance(arguments, str) else arguments
    if name == "tool_call":
        unwrapped = _unwrap_wrapper(arguments)
        if unwrapped is None:
            return call_id, None, None, False
        name, arguments = unwrapped
    return call_id, str(name) if isinstance(name, str) else None, arguments, str(name) == "omj_memory"


def _unwrap_wrapper(arguments: Any) -> tuple[Any, Any] | None:
    if not isinstance(arguments, Mapping):
        return None
    if "calls" in arguments:
        values = arguments.get("calls")
        if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], Mapping):
            return None
        inner = values[0]
    else:
        inner = arguments
    name = inner.get("name")
    args = inner.get("arguments")
    args = _json_value(args) if isinstance(args, str) else args
    return name, args


def _action(value: Any) -> str:
    if isinstance(value, Mapping):
        value = value.get("action")
    if value is None or value == "":
        return UNPARSED_LABEL
    text = str(value).strip().lower()
    return text if text in _MEMORY_ACTIONS else OTHER_LABEL


def _status(value: Any) -> str:
    if value is None or value == "":
        return "(none)"
    text = str(value).strip().lower()
    return text if text in _MEMORY_STATUSES else OTHER_LABEL


def _calls_by_action(calls: Iterable[_ObservedCall]) -> dict[str, dict[str, int]]:
    output: dict[str, dict[str, int]] = {}
    for call in calls:
        output.setdefault(call.action, {})[call.status] = output.setdefault(call.action, {}).get(call.status, 0) + 1
    return {action: dict(sorted(statuses.items())) for action, statuses in sorted(output.items())}


def _unread_store(reason: str, *, error: str) -> dict[str, Any]:
    return {
        "read_state": UNREADABLE,
        "error": reason,
        "records": {"total": None, "created_in_window": None, "by_admission_state": {}, "by_source": {}, "refused_files_by_reason": {}},
        "candidates": {"total": None, "created_in_window": None, "by_status": {}, "refused_files_by_reason": {}},
        "scanner_error": error,
    }


def _unread_session(path: Path, state: str, reason: str, max_rows: int) -> dict[str, Any]:
    return {
        "read_state": state,
        "path": str(path),
        "error": reason,
        "calls": {"total": None, "by_action_status": {}},
        "writes": {"observed": None, "confirmed_status_only": None},
        "results_without_call": None,
        "unknown_traffic": None,
        "window": {},
        "budget": {"complete": False, "row_limit_reached": False, "max_rows": max_rows, "malformed_rows": 0},
    }


def _source_state(name: str, section: Mapping[str, Any]) -> dict[str, str]:
    return {"source": name, "read_state": str(section.get("read_state") or UNREADABLE), "error": str(section.get("error") or "source incomplete")}


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _refusal_counts(rows: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    output: dict[str, int] = {}
    for row in rows:
        reason = _store_label(row.get("reason") or row.get("diagnostic"), "reason")
        _increment(output, reason)
    return dict(sorted(output.items()))


_STORE_LABELS: dict[str, frozenset[str]] = {
    "source": frozenset({"operator", "cli"}),
    "admission": frozenset({"approved", "approved_manual", "approved_auto_safe", "pending_review", "rejected", "blocked", "blocked_review_required", "expired", "superseded", "retired", "archived", "other"}),
    "status": frozenset({"pending_review", "rejected"}),
    "reason": frozenset({"corrupt_json", "unsupported_record_schema", "duplicate_record", "pending_review", "symlink_directory", "symlink_path", "nonregular_file", "unreadable_directory", "unreadable_file", "file_budget_exceeded", "scan_budget_exceeded"}),
}


def _store_label(value: Any, kind: str) -> str:
    if value is None or value == "":
        return "(none)"
    text = str(value).strip().lower()
    return text if text in _STORE_LABELS.get(kind, frozenset()) else OTHER_LABEL


def _increment(target: dict[str, int], key: str) -> None:
    target[key] = target.get(key, 0) + 1


def _closed_label(value: Any, *, allow_any: bool = False) -> str:
    if value is None or value == "":
        return "(none)"
    text = str(value).strip().lower()
    if allow_any and _SAFE_LABEL.fullmatch(text):
        return text
    return OTHER_LABEL


def _json_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    # Match the canonical reader's structural bound, independent of the
    # interpreter's JSON decoder recursion limit, at every session entry point.
    containers = [iter((parsed,))]
    while containers:
        try:
            item = next(containers[-1])
        except StopIteration:
            containers.pop()
            continue
        if isinstance(item, (dict, list)):
            if len(containers) > _MAX_MEMORY_JSON_DEPTH:
                raise RecursionError("session JSON structural depth exceeds the memory bound")
            containers.append(iter(item.values() if isinstance(item, dict) else item))
    return parsed


def _epoch(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            stamp = float(value)
        except (OverflowError, ValueError, TypeError):
            return None
        return stamp if math.isfinite(stamp) else None
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        number = float(text)
    except (OverflowError, ValueError, TypeError):
        number = math.nan
    if math.isfinite(number) and re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", text):
        return number
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except (OverflowError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    try:
        stamp = parsed.timestamp()
    except (OverflowError, OSError, ValueError):
        return None
    return stamp if math.isfinite(stamp) else None


def _validate_now(value: float | None) -> float:
    try:
        moment = float(value) if value is not None else datetime.now(tz=timezone.utc).timestamp()
    except (OverflowError, ValueError, TypeError) as exc:
        raise MemoryEvidenceError("now must be finite") from exc
    if not math.isfinite(moment):
        raise MemoryEvidenceError("now must be finite")
    _ensure_timestamp(moment, "now")
    return moment


def _validate_max_rows(value: int | None) -> int:
    if value is None:
        return DEFAULT_MAX_ROWS
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise MemoryEvidenceError("--max-rows must be a positive whole number")
    return value


def _resolve_window(*, days: int | None, since: str | float | int | None, now: float) -> tuple[float, int | None]:
    if since is not None:
        if days not in (None, DEFAULT_WINDOW_DAYS):
            raise MemoryEvidenceError("--days and --since are exclusive")
        stamp = _epoch(since)
        if stamp is None or not math.isfinite(stamp) or stamp > now:
            raise MemoryEvidenceError("--since must be a finite timestamp not in the future")
        _ensure_timestamp(stamp, "--since")
        return stamp, None
    if isinstance(days, bool) or not isinstance(days, int) or days < 1:
        raise MemoryEvidenceError(f"--days must be a positive whole number of days: {days}")
    try:
        stamp = now - days * DAY_SECONDS
    except (OverflowError, ValueError, TypeError) as exc:
        raise MemoryEvidenceError("--days produces an out-of-range timestamp") from exc
    if not math.isfinite(stamp):
        raise MemoryEvidenceError("--days produces an out-of-range timestamp")
    _ensure_timestamp(stamp, "--days")
    return stamp, days


def _iso(epoch: float) -> str:
    _ensure_timestamp(epoch, "timestamp")
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _ensure_timestamp(epoch: float, label: str) -> None:
    try:
        datetime.fromtimestamp(epoch, tz=timezone.utc)
    except (OverflowError, OSError, ValueError) as exc:
        raise MemoryEvidenceError(f"{label} is outside the supported timestamp range") from exc


def _in_bounds(stamp: float | None, since: float, until: float) -> bool:
    return stamp is not None and since <= stamp <= until
