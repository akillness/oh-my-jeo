"""Read-only provenance and blast-radius index for OMJ project memory.

The index is deliberately separate from :mod:`workflows.memory`: it only reads
approved record metadata (and candidate metadata for status flags), never writes
or migrates the local memory store.  ``source`` is the admission channel and
``source_ref`` is the document/input reference; both axes are indexed
independently because one record may carry both labels.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..paths import OmjPaths
from .memory import (
    MAX_MEMORY_SCAN_FILES,
    _PROJECT_MEMORY_CANDIDATE_SCHEMAS,
    _PROJECT_MEMORY_RECORD_SCHEMAS,
    _bounded_memory_inventory,
    _memory_admission_state,
    _memory_status_label,
    _read_bounded_memory_json,
    _normalize_scope,
    _normalize_tags,
    _record_staleness,
    _redact,
)

MEMORY_SOURCE_INDEX_SCHEMA_VERSION = "memory_source_index/v1"
SOURCE_AXES = ("source", "source_ref")
SELECTOR_OUTCOMES = (
    "not_requested",
    "matched",
    "no_records_for_source",
    "source_never_recorded",
    "empty_store",
)

_CLAIM_BOUNDARY = (
    "A memory source index enumerates OMJ-local reviewed records by their recorded "
    "admission source and document reference. It is a read-only prepared-context "
    "report that changes nothing in the memory store: it does not mutate, migrate, "
    "quarantine, retire, prune, or prove Hermes internal memory, execution, review, CI, or merge."
)
_INDETERMINATE_BOUNDARY = (
    "Records without a recorded source are indeterminate, never clean. Unreadable "
    "record files are also indeterminate and remain for operator review."
)
_RECOVERY_SEQUENCE = (
    "Inspect each bounded record_id with the existing memory lineage/recall tools.",
    "Apply quarantine or correction only through an explicitly approved memory operation.",
    "Verify the same local store with a recall report after any approved change.",
)


def build_memory_source_index(
    paths: OmjPaths, *, source: str | None = None, limit: int | None = None
) -> dict[str, object]:
    """Build a metadata-only source index without changing the memory store.

    ``source`` selects records whose ``source`` *or* ``source_ref`` equals the
    requested label.  Matching is per axis, so a record matching both reports
    both entries in ``matched_axes``.  ``limit`` bounds returned cards only;
    ``selected.count`` remains the complete blast-radius count.
    """
    selector = str(source or "").strip()
    records, unreadable = _read_approved_records(paths)
    candidates, candidate_errors = _read_candidates(paths)
    unreadable.extend(candidate_errors)

    labels: dict[str, dict[str, Any]] = {}
    axis_values: dict[str, set[str]] = {axis: set() for axis in SOURCE_AXES}
    indeterminate: list[dict[str, object]] = []
    selected: list[dict[str, object]] = []

    for record, record_path in records:
        source_entries = _record_sources(record)
        if not source_entries:
            indeterminate.append(
                {
                    "record_id": _redact(str(record.get("record_id", ""))),
                    "reason": "source_not_recorded",
                    "archived": _is_archived(record, record_path, paths.memory_dir),
                }
            )
            continue

        for entry in source_entries:
            axis = entry["axis"]
            value = entry["value"]
            axis_values[axis].add(value)
            bucket = labels.setdefault(value, {"axes": set(), "record_ids": set()})
            bucket["axes"].add(axis)
            bucket["record_ids"].add(str(record.get("record_id", "")))

        if selector:
            matched_axes = [
                entry["axis"] for entry in source_entries if entry["value"] == selector
            ]
            if matched_axes:
                selected.append(
                    _source_card(
                        record,
                        record_path,
                        paths.memory_dir,
                        candidates,
                        matched_axes=matched_axes,
                    )
                )

    # Keep file order deterministic while avoiding a caller-controlled negative
    # limit turning into a surprising slice.  The full count is intentionally
    # retained for bounded blast-radius follow-up.
    selected_limit = _limited(selected, limit)
    unreadable_rows = list(unreadable)
    outcome = _selector_outcome(selector, selected, records, labels)
    complete = not unreadable_rows
    return {
        "schema_version": MEMORY_SOURCE_INDEX_SCHEMA_VERSION,
        "read_state": "read" if complete else "partial" if records else "refused",
        "complete": complete,
        "scan_budget": {"max_files_per_source": MAX_MEMORY_SCAN_FILES, "complete": complete},
        "record_count": len(records),
        "axes": [
            {
                "axis": axis,
                "populated": bool(axis_values[axis]),
                "distinct_values": len(axis_values[axis]),
            }
            for axis in SOURCE_AXES
        ],
        "sources": [
            {
                "label": _redact_metadata(label),
                "axes": sorted(bucket["axes"]),
                "record_count": len(bucket["record_ids"]),
            }
            for label, bucket in sorted(labels.items())
        ],
        "source_count": len(labels),
        "selector": {
            "requested": bool(selector),
            "value": _redact_metadata(selector),
            "outcome": outcome,
        },
        "selected": {
            "outcome": outcome,
            "count": len(selected),
            "records": selected_limit,
            "truncated": limit is not None and len(selected) > max(limit, 0),
            "complete": complete,
        },
        "indeterminate": {
            "records": indeterminate,
            "unreadable": unreadable_rows,
            "count": len(indeterminate) + len(unreadable_rows),
            "boundary": _INDETERMINATE_BOUNDARY,
        },
        "recovery": {
            "sequence": list(_RECOVERY_SEQUENCE),
            "quarantine_default": "No automatic quarantine is performed by this read-only index.",
            "completion_evidence": "A recall report over this same store after an approved operation.",
            "not_completion_evidence": "This index, an exit code, or a migration override is not completion evidence.",
        },
        "redaction_policy": "metadata_only",
        "claim_boundary": _CLAIM_BOUNDARY,
    }


def _read_approved_records(
    paths: OmjPaths,
) -> tuple[list[tuple[dict[str, Any], Path]], list[dict[str, object]]]:
    """Read only bounded active files, disclosing every unjudgeable source."""
    records_dir = paths.memory_dir / "records"
    rows: list[tuple[dict[str, Any], Path]] = []
    unreadable: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    files, state, _ = _bounded_memory_inventory(records_dir, max_entries=MAX_MEMORY_SCAN_FILES)
    if state not in {"read", "absent"}:
        unreadable.append({"path_name": "records", "reason": state})
    for path in files:
        path_name = _redact_metadata(path.name)
        data, error, _ = _read_bounded_memory_json(path)
        if error or data is None:
            unreadable.append({"path_name": path_name, "reason": error or "corrupt_json"})
            continue
        record_id = str(data.get("record_id", ""))
        schema = data.get("schema_version")
        if not isinstance(schema, str) or schema not in _PROJECT_MEMORY_RECORD_SCHEMAS:
            unreadable.append({"path_name": path_name, "record_id": _redact_metadata(record_id), "reason": "unsupported_record_schema"})
            continue
        if _memory_admission_state(data) not in {"approved_manual", "approved_auto_safe"}:
            unreadable.append({"path_name": path_name, "record_id": _redact_metadata(record_id), "reason": "not_approved"})
            continue
        if record_id and record_id in seen_ids:
            unreadable.append({"path_name": path_name, "record_id": _redact_metadata(record_id), "reason": "duplicate_record"})
            continue
        if record_id:
            seen_ids.add(record_id)
        rows.append((data, path))
    return rows, unreadable


def _read_candidates(paths: OmjPaths) -> tuple[dict[str, dict[str, Any]], list[dict[str, object]]]:
    """Read bounded candidates for non-authoritative status metadata."""
    directory = paths.memory_dir / "candidates"
    files, state, _ = _bounded_memory_inventory(directory, max_entries=MAX_MEMORY_SCAN_FILES)
    errors: list[dict[str, object]] = []
    if state not in {"read", "absent"}:
        errors.append({"path_name": "candidates", "reason": state})
    candidates: dict[str, dict[str, Any]] = {}
    for path in files:
        data, error, _ = _read_bounded_memory_json(path)
        if error or data is None:
            errors.append({"path_name": _redact_metadata(path.name), "reason": error or "corrupt_json"})
            continue
        schema = data.get("schema_version")
        if not isinstance(schema, str) or schema not in _PROJECT_MEMORY_CANDIDATE_SCHEMAS:
            errors.append({"path_name": _redact_metadata(path.name), "reason": "unsupported_record_schema"})
            continue
        candidate_id = str(data.get("candidate_id", ""))
        if candidate_id:
            candidates[candidate_id] = data
    return candidates, errors


def _record_sources(record: dict[str, Any]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for axis in SOURCE_AXES:
        value = str(record.get(axis, "") or "").strip()
        if value:
            entries.append({"axis": axis, "value": value})
    return entries


def _source_card(
    record: dict[str, Any],
    record_path: Path,
    memory_dir: Path,
    candidates: dict[str, dict[str, Any]],
    *,
    matched_axes: list[str],
) -> dict[str, object]:
    record_id = str(record.get("record_id", ""))
    candidate_id = str(record.get("candidate_id", ""))
    candidate = candidates.get(candidate_id)
    candidate_present = candidate is not None
    staleness = _record_staleness(record)
    archived = _is_archived(record, record_path, memory_dir)
    # The local reviewed-record schema has no conflict axis; do not infer one.
    conflict = False
    candidate_status = _memory_status_label(candidate.get("status")) if candidate else ""
    approved = _memory_admission_state(record) in {"approved_manual", "approved_auto_safe"}
    return {
        "record_id": _redact_metadata(record_id),
        "candidate_id": _redact_metadata(candidate_id),
        "revision": _revision(record.get("revision")),
        "record_type": _redact_metadata(str(record.get("record_type", ""))),
        "summary": _redact_metadata(str(record.get("summary", "")))[:500],
        "scope": _redacted_scope(record.get("scope", {})),
        "tags": [_redact_metadata(tag) for tag in _normalize_tags(record.get("tags", []))],
        "approved_at": _redact_metadata(str(record.get("approved_at", ""))),
        "source": _redact_metadata(str(record.get("source", ""))),
        "source_ref": _redact_metadata(str(record.get("source_ref", ""))),
        "sources": [
            {"axis": entry["axis"], "value": _redact_metadata(entry["value"])}
            for entry in _record_sources(record)
        ],
        "matched_axes": sorted(set(matched_axes)),
        "derived_from": [
            _redact_metadata(str(value))[:240]
            for value in _string_list(record.get("derived_from", []))[:12]
        ],
        "staleness": staleness,
        "flags": {
            "candidate": candidate_present,
            "approved": approved,
            "conflict": conflict,
            "stale": staleness.get("state") in {"stale", "expired"},
            "expired": staleness.get("state") == "expired",
            "archived": archived,
        },
        # Top-level flags keep this card usable by simple wrappers while the
        # nested object gives structured consumers one stable metadata axis.
        "candidate": candidate_present,
        "candidate_status": _redact_metadata(candidate_status),
        "approved": approved,
        "conflict": conflict,
        "stale": staleness.get("state") in {"stale", "expired"},
        "archived": archived,
    }


def _selector_outcome(
    selector: str,
    selected: list[dict[str, object]],
    records: list[tuple[dict[str, Any], Path]],
    labels: dict[str, dict[str, Any]],
) -> str:
    if not selector:
        return "not_requested"
    if selected:
        return "matched"
    if not records:
        return "empty_store"
    if not labels:
        return "source_never_recorded"
    return "no_records_for_source"


def _limited(items: list[dict[str, object]], limit: int | None) -> list[dict[str, object]]:
    if limit is None:
        return items
    return items[: max(limit, 0)]


_CREDENTIAL_RE = re.compile(
    r"(?:ghp_[A-Za-z0-9_\-]{12,}|github_pat_[A-Za-z0-9_\-]{12,}|"
    r"glpat-[A-Za-z0-9_\-]{12,}|xox[baprs]-[A-Za-z0-9_\-]{12,}|"
    r"(?:sk|rk)-[A-Za-z0-9_\-]{16,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_\-]{20,}|"
    r"ya29\.[0-9A-Za-z_\-]{12,}|Bearer\s+\S+|"
    r"(?:token|secret|password|api[_-]?key)\s*[:=]\s*\S+)",
    flags=re.IGNORECASE,
)


def _redact_metadata(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if _CREDENTIAL_RE.search(text):
        return "[redacted]"
    return _redact(text)






def _revision(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _redacted_scope(value: Any) -> dict[str, str]:
    scope = _normalize_scope(value)
    return {
        "kind": _redact_metadata(scope.get("kind", "project")),
        "ref": _redact_metadata(scope.get("ref", "default")),
    }


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple)):
        return []
    return [str(item) for item in value if str(item)]


def _is_archived(record: dict[str, Any], path: Path, memory_dir: Path) -> bool:
    if bool(record.get("archived")):
        return True
    retention = record.get("retention")
    if isinstance(retention, dict) and str(
        retention.get("state", retention.get("class", ""))
    ).lower() == "archived":
        return True
    try:
        return "archive" in path.relative_to(memory_dir).parts
    except ValueError:
        return False
