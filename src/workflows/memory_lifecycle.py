from __future__ import annotations

"""Revision-bound, offline lifecycle and retrieval evidence for OMJ memory.

This module deliberately owns planning and validation only.  It never discovers
or runs an executor, calls a model, or claims that a host/provider observed a
side effect.  Mutation is possible only through the caller-supplied transaction
executor after the plan's revision and manifest guards still match.
"""

import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..local_store import read_json_object_result
from ..paths import OmjPaths
from .memory import (
    PROJECT_MEMORY_RECORD_SCHEMA_VERSION,
    _contains_sensitive_text,
    _normalize_scope,
    _redact,
)

MAX_MANIFEST_TARGETS = 128
RECEIPT_SCHEMA_VERSION = "memory_lifecycle_receipt/v1"
LIFECYCLE_REPORT_SCHEMA_VERSION = "memory_lifecycle_report/v1"
RETRIEVAL_EVALUATION_SCHEMA_VERSION = "omj_memory_retrieval_evaluation/v1"
RETRIEVAL_COMPARISON_SCHEMA_VERSION = "omj_memory_retrieval_comparison/v1"
RETRIEVAL_EVALUATOR_VERSION = "omj-memory-retrieval-evaluator/v2"
RETRIEVAL_IDENTITY_FIELDS = (
    "schema_version",
    "evaluator_version",
    "corpus_version",
    "fixture_digest",
    "retrieval_config_digest",
    "clock",
    "target_revision",
)
_RECEIPT_FIELDS = frozenset({"schema_version", "operation_id", "operation_type", "record_id", "revision", "scope", "actor_class", "created_at", "completed_at", "state", "outcomes"})
_OUTCOME_FIELDS = frozenset({"target_id", "artifact_kind", "outcome", "reason_code"})
_ALLOWED_OUTCOMES = frozenset({"written", "moved", "rewritten", "removed", "already_absent", "rejected", "unlinked_preserved", "unsupported_or_corrupt", "external_excluded"})
_SAFE_TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}$")
_CREDENTIAL_SHAPES = (re.compile(r"gh[puo]_[A-Za-z0-9]{20,}", re.I), re.compile(r"sk-[A-Za-z0-9_-]{16,}", re.I), re.compile(r"xox[baprs]-[A-Za-z0-9-]{16,}", re.I))


@dataclass(frozen=True)
class LifecycleMutation:
    name: str
    action: str
    target: str
    target_id: str
    artifact_kind: str
    source: str | None = None
    payload: Mapping[str, object] | Sequence[Mapping[str, object]] | None = None


@dataclass(frozen=True)
class LifecyclePlan:
    operation_id: str
    operation_type: str
    record_id: str
    revision: int
    scope: Mapping[str, object]
    now: datetime
    report: Mapping[str, object]
    mutations: tuple[LifecycleMutation, ...]
    preserved: tuple[Mapping[str, object], ...] = ()


LifecycleTransactionExecutor = Callable[[OmjPaths, LifecyclePlan], Mapping[str, object]]


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


def _stamp(value: datetime) -> str:
    return _utc(value).replace(microsecond=0).isoformat().replace("+00:00", "Z")
def _valid_record_schema(value: Mapping[str, object]) -> bool:
    return str(value.get("schema_version", "")) in {PROJECT_MEMORY_RECORD_SCHEMA_VERSION, "project_memory_record/v2", "project_memory_record/v3"}



def _parse_time(value: object) -> datetime | None:
    if not isinstance(value, (str, datetime)):
        return None
    try:
        parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    return _utc(parsed)


def _safe_token(value: object) -> bool:
    if not isinstance(value, str) or not _SAFE_TOKEN.fullmatch(value):
        return False
    lowered = value.lower()
    if any(marker in lowered for marker in ("secret", "token", "password", "private-key", "api_key", "apikey")):
        return False
    return not any(pattern.fullmatch(value) for pattern in _CREDENTIAL_SHAPES)


def _redact_public(value: object) -> str:
    text = str(value or "")
    if not _safe_token(text) or _contains_sensitive_text(text) or any(pattern.search(text) for pattern in _CREDENTIAL_SHAPES):
        return "redacted"
    return text[:240]


def _scope(value: object) -> dict[str, str]:
    try:
        normalized = _normalize_scope(value)
    except (TypeError, ValueError):
        raise ValueError("scope_invalid") from None
    if not isinstance(normalized, Mapping):
        raise ValueError("scope_invalid")
    kind, ref = str(normalized.get("kind", "")), str(normalized.get("ref", ""))
    if kind not in {"project", "target", "thread", "run"} or not _safe_token(ref):
        raise ValueError("scope_invalid")
    return {"kind": kind, "ref": ref}


def _scope_public(value: object) -> dict[str, str]:
    try:
        scope = _scope(value)
    except ValueError:
        return {"kind": "redacted", "ref": "redacted"}
    return {"kind": _redact_public(scope["kind"]), "ref": _redact_public(scope["ref"])}


def _record_revision(record: Mapping[str, object]) -> int:
    revision = record.get("revision", 1)
    return revision if isinstance(revision, int) and not isinstance(revision, bool) and revision >= 1 else 0


def _admission_state(record: Mapping[str, object]) -> str:
    admission = record.get("admission")
    if isinstance(admission, Mapping):
        state = str(admission.get("state", ""))
        if state:
            return state
    status = str(record.get("review_status", ""))
    return {"approved": "approved_manual", "approved_manual": "approved_manual", "auto-safe": "approved_auto_safe", "approved_auto_safe": "approved_auto_safe", "pending_review": "pending_review"}.get(status, status)


def _retention_class(record: Mapping[str, object]) -> str:
    retention = record.get("retention")
    if isinstance(retention, Mapping) and retention.get("class"):
        return str(retention["class"])
    return str(record.get("retention_class", "") or "") or "standard"


def _retention_origin(record: Mapping[str, object]) -> str:
    retention = record.get("retention")
    if isinstance(retention, Mapping) and retention.get("origin"):
        return str(retention["origin"])
    return str(record.get("retention_origin", "") or "") or "unknown"


def _tier(record: Mapping[str, object]) -> str:
    attention = record.get("attention")
    if isinstance(attention, Mapping) and attention.get("tier"):
        return str(attention["tier"])
    return str(record.get("tier", "") or "") or "active"


def _staleness(record: Mapping[str, object]) -> Mapping[str, object]:
    value = record.get("staleness")
    return value if isinstance(value, Mapping) else {}


def _resolution(record: Mapping[str, object]) -> str:
    value = str(_staleness(record).get("resolution", "") or "")
    return value if value in {"open", "resolved"} else ""


def _source_issue(record: Mapping[str, object], *, paths: OmjPaths | None = None) -> str:
    for key in ("source_status", "source_state", "source_health"):
        value = str(record.get(key, "") or "").lower()
        if value in {"changed", "source_changed"}:
            return "source_changed"
        if value in {"unreadable", "missing", "corrupt", "source_unreadable"}:
            return "source_unreadable"
    evidence = record.get("source_evidence")
    if isinstance(evidence, Mapping):
        status = str(evidence.get("status", "") or "").lower()
        if status in {"changed", "source_changed"}:
            return "source_changed"
        if status in {"unreadable", "missing", "corrupt", "source_unreadable"}:
            return "source_unreadable"
        if paths is not None and evidence.get("path") and evidence.get("sha256"):
            candidate = Path(str(evidence["path"]))
            if not candidate.is_absolute():
                candidate = paths.omj_home.parent / candidate
            try:
                root, resolved = paths.omj_home.parent.resolve(), candidate.resolve(strict=False)
                if root != resolved and root not in resolved.parents:
                    return "source_unreadable"
                digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
            except (OSError, ValueError):
                return "source_unreadable"
            if digest != str(evidence["sha256"]):
                return "source_changed"
    return ""


def _expiry_reason(record: Mapping[str, object], now: datetime, *, paths: OmjPaths | None = None) -> str:
    deadlines: list[tuple[datetime, str]] = []
    malformed = False
    retention_value = record.get("retention")
    if isinstance(retention_value, Mapping) and str(retention_value.get("class", "")) not in {"volatile", "standard", "durable"}:
        return "retention_invalid"
    for container in (retention_value, record.get("ttl")):
        if not isinstance(container, Mapping):
            continue
        if container.get("expires_at"):
            parsed = _parse_time(container.get("expires_at"))
            if parsed is None:
                malformed = True
            else:
                deadlines.append((parsed, f"expired_{_retention_class(record)}"))
        elif container.get("ttl_days") is not None:
            admitted = _parse_time(container.get("admitted_at", container.get("created_at", record.get("created_at"))))
            try:
                ttl_days = int(container.get("ttl_days"))
            except (TypeError, ValueError):
                admitted, ttl_days = None, 0
            if admitted is None or ttl_days < 0:
                malformed = True
            else:
                deadlines.append((admitted + timedelta(days=ttl_days), f"expired_{_retention_class(record)}"))
    if malformed and not deadlines:
        return "unreadable_expiry"
    if deadlines:
        deadline, reason = min(deadlines, key=lambda item: item[0])
        if _utc(now) >= deadline:
            return reason
    source = _source_issue(record, paths=paths)
    if source:
        return source
    stale_after = _staleness(record).get("stale_after")
    if stale_after:
        parsed = _parse_time(stale_after)
        if parsed is None:
            return "unreadable_staleness"
        if _utc(now) >= parsed:
            return "stale_review_required"
    return "eligible"


def _unresolved_marker(record: Mapping[str, object], now: datetime) -> tuple[str, int | None]:
    if _resolution(record) != "open":
        return "", None
    since = _parse_time(_staleness(record).get("open_since"))
    days = max(0, (_utc(now) - since).days) if since else None
    return ("open" if days is None else f"open · {days} days unresolved"), days


def lifecycle_replay_status(record: Mapping[str, object], *, now: datetime) -> dict[str, object]:
    if not isinstance(record, Mapping):
        record = {}
    reason = _expiry_reason(record, now)
    state = _admission_state(record)
    marker, open_days = _unresolved_marker(record, now)
    approved = state in {"approved_manual", "approved_auto_safe"}
    reason_code = reason if reason != "eligible" else ("unresolved_open" if marker else ("eligible" if approved else "review_required"))
    staleness = _staleness(record)
    return {"record_id": _redact_public(record.get("record_id", "")), "revision": _record_revision(record) or None, "scope": _scope_public(record.get("scope", {})), "admission_state": _redact_public(state), "retention_class": _redact_public(_retention_class(record)), "retention_origin": _redact_public(_retention_origin(record)), "tier": _redact_public(_tier(record)), "resolution": _resolution(record), "review_deadline": str(staleness.get("open_expires_at", staleness.get("review_due_at", "")) or ""), "resolution_marker": marker, "open_days": open_days, "replay_eligible": reason == "eligible" and approved, "reason_code": reason_code}


def _read_json(root: Path, relative: str) -> tuple[dict[str, object] | None, str | None]:
    path = root / relative
    try:
        root_resolved, path_resolved = root.resolve(strict=False), path.resolve(strict=False)
        if root_resolved != path_resolved and root_resolved not in path_resolved.parents:
            return None, "path_escape"
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != root):
            return None, "symlink_target"
        value, error = read_json_object_result(path)
    except (OSError, ValueError) as exc:
        return None, str(exc)
    if error:
        return None, "corrupt_json"
    return value, None if value is not None else "already_absent"


def _safe_identity(record_id: object, revision: object) -> tuple[str, int] | None:
    if not _safe_token(record_id) or not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        return None
    return str(record_id), revision


def _current_record(paths: OmjPaths, record_id: object, revision: object) -> tuple[dict[str, object], str | None]:
    identity = _safe_identity(record_id, revision)
    if identity is None:
        return {}, "unsafe_record_identity"
    rid, rev = identity
    value, error = _read_json(paths.memory_dir / "records", f"{rid}.json")
    if error or value is None:
        return {}, error or "record_not_found"
    if not _valid_record_schema(value):
        return {}, "unsupported_record_schema"
    if value.get("record_id") != rid or _record_revision(value) != rev:
        return {}, "exact_revision_not_current"
    if value.get("source_class") in {"provider", "external", "hermes_native"}:
        return {}, "external_target"
    try:
        _scope(value.get("scope", {}))
    except ValueError:
        return {}, "scope_invalid"
    return value, None


def _archived_record(paths: OmjPaths, record_id: object, revision: object) -> tuple[dict[str, object], str, str | None]:
    identity = _safe_identity(record_id, revision)
    if identity is None:
        return {}, "", "unsafe_record_identity"
    rid, rev = identity
    archive_dir = paths.memory_dir / "archive"
    if not archive_dir.exists() or archive_dir.is_symlink():
        return {}, "", "archive_exact_revision_not_found"
    matches: list[tuple[dict[str, object], str]] = []
    for path in sorted(archive_dir.glob("*.json")):
        if path.is_symlink() or not path.is_file():
            continue
        value, error = _read_json(archive_dir, path.name)
        if error or value is None:
            continue
        if not _valid_record_schema(value):
            continue
        if value.get("record_id") == rid and _record_revision(value) == rev:
            matches.append((value, f"archive/{path.name}"))
    if len(matches) != 1:
        return {}, "", "archive_exact_revision_not_found" if not matches else "archive_exact_revision_ambiguous"
    value, relative = matches[0]
    try:
        _scope(value.get("scope", {}))
    except ValueError:
        return {}, relative, "scope_invalid"
    return value, relative, None


def _record_digest(record: Mapping[str, object]) -> str:
    return hashlib.sha256(json.dumps(dict(record), sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _candidate_id(operation: str, record_id: str, revision: int) -> str:
    return f"cand-{operation}-" + hashlib.sha256(f"{operation}:{record_id}:{revision}".encode()).hexdigest()[:24]


def _pending_candidate(record: Mapping[str, object], candidate_id: str, revision: int, lifecycle: str) -> dict[str, object]:
    keys = ("record_type", "summary", "scope", "tags", "source", "source_ref", "source_class", "source_evidence", "ttl", "staleness", "retention", "retention_class", "retention_origin", "attention", "tier", "safety", "redaction_policy", "claim_boundary")
    replacement = {key: record[key] for key in keys if key in record}
    return {"schema_version": "project_memory_candidate/v2", "candidate_id": candidate_id, "candidate_revision": revision, "record_id": str(record.get("record_id", "")), "artifact_kind": "record", "status": "pending_review", "admission": {"state": "pending_review"}, "origin": {"record_id": str(record.get("record_id", "")), "revision": _record_revision(record), "digest": _record_digest(record)}, "lifecycle": lifecycle, "replacement": replacement}


def _review(record: Mapping[str, object], review_id: str, reviewer: str) -> dict[str, object]:
    return {"schema_version": "project_memory_review_record/v1", "review_id": review_id, "record_id": str(record.get("record_id", "")), "revision": _record_revision(record), "decision": "approved_manual", "reviewer_claim": _redact_public(reviewer), "payload_digest": _record_digest(record), "redaction_policy": "metadata_only"}


def _approved_record(replacement: Mapping[str, object], record_id: str, revision: int, reviewer: str, now: datetime) -> dict[str, object]:
    record: dict[str, object] = {key: value for key, value in replacement.items() if key not in {"admission", "review_status", "record_id", "revision", "candidate_id"}}
    record.update({"schema_version": PROJECT_MEMORY_RECORD_SCHEMA_VERSION, "record_id": record_id, "revision": revision, "review_status": "approved", "approved_by": reviewer, "approved_at": _stamp(now), "updated_at": _stamp(now), "redaction_policy": "metadata_only"})
    previous = replacement.get("admission")
    admission = dict(previous) if isinstance(previous, Mapping) else {}
    admission.update({"state": "approved_manual", "review_id": f"review-{record_id}-r{revision}", "reviewer": reviewer, "reviewed_at": _stamp(now), "payload_digest": _record_digest(record)})
    record["admission"] = admission
    return record


def _manifest(items: Sequence[tuple[str, str, str]]) -> list[dict[str, object]]:
    return [{"target_id": target_id, "artifact_kind": kind, "relative_path": relative} for target_id, kind, relative in items]


def _plan(operation: str, record_id: str, revision: int, scope: Mapping[str, object], now: datetime, manifest: Sequence[Mapping[str, object]], mutations: Sequence[LifecycleMutation], *, preserved: Sequence[Mapping[str, object]] = (), guard_digest: str = "") -> LifecyclePlan:
    next_actions = {"retire": "Apply only after review: archive the exact expired standard revision; it is not deleted.", "restore": "Review/reactivate the pending restored revision; the archive remains unchanged.", "prune": "Apply only with --confirm-hard-delete-local; the receipt is not deletion or erasure proof.", "correct": "Review and approve the pending replacement revision.", "reapprove": "The new active revision remains governed by its immutable review record.", "confirm": "Review and approve the pending replacement revision.", "keep_open": "Apply only after review; only the reminder clock changes."}
    report = {"schema_version": LIFECYCLE_REPORT_SCHEMA_VERSION, "operation_type": operation, "record_id": record_id, "revision": revision, "scope": dict(scope), "eligible": True, "applied": False, "reason_code": "planned", "manifest": list(manifest), "guard_digest": guard_digest, "outcomes": [], "exclusions": ["backups", "filesystem_snapshots", "trash", "synced_copies", "hermes_native", "external_providers", "vector_stores", "executors", "unlinked_artifacts", "recall_usage_counters", "pin_markers"], "next_action": next_actions.get(operation, "Review the prepared plan before applying it."), "claim_boundary": "This is an OMJ-local prepared target-set plan, not deletion, erasure, backup, provider, native-memory, executor, or legal-erasure proof."}
    return LifecyclePlan(f"memory-{operation}-{record_id}-r{revision}", operation, record_id, revision, dict(scope), now, report, tuple(mutations), tuple(preserved))


def _rejected(operation: str, record_id: object, revision: object, now: datetime, reason: str) -> LifecyclePlan:
    safe_id = str(record_id) if _safe_token(record_id) else "invalid"
    safe_revision = int(revision) if isinstance(revision, int) and not isinstance(revision, bool) and revision > 0 else 1
    report = {"schema_version": LIFECYCLE_REPORT_SCHEMA_VERSION, "operation_type": operation, "record_id": safe_id, "revision": safe_revision, "scope": {"kind": "project", "ref": "default"}, "eligible": False, "applied": False, "reason_code": reason, "manifest": [], "outcomes": [{"target_id": "rejected:0", "artifact_kind": "local_target", "outcome": "rejected", "reason_code": reason}], "exclusions": [], "next_action": "No apply action: resolve the reported lifecycle guard.", "claim_boundary": "No mutation was planned. This report does not claim deletion, erasure, or any provider/native/executor effect."}
    return LifecyclePlan(f"memory-{operation}-{safe_id}-r{safe_revision}", operation, safe_id, safe_revision, report["scope"], now, report, ())


def _validate_build_identity(operation: str, record_id: object, revision: object, now: datetime) -> LifecyclePlan | None:
    if not _safe_token(record_id):
        raise ValueError("unsafe_record_identity")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        return _rejected(operation, record_id, revision, now, "invalid_revision")
    return None


def build_memory_retirement(paths: OmjPaths, record_id: str = "", revision: int | None = None, *, now: datetime) -> LifecyclePlan:
    invalid = _validate_build_identity("retire", record_id, revision, now)
    if invalid:
        return invalid
    record, error = _current_record(paths, record_id, revision)
    if error:
        return _rejected("retire", record_id, revision, now, error)
    reason = _expiry_reason(record, now, paths=paths)
    if _retention_class(record) != "standard" or reason != "expired_standard":
        return _rejected("retire", record_id, revision, now, "retire_requires_expired_standard")
    archive = f"archive/{record_id}.r{revision}.json"
    tombstone_id = f"retired-{record_id}-r{revision}"
    if (paths.memory_dir / archive).exists() or (paths.memory_dir / f"tombstones/{tombstone_id}.json").exists():
        return _rejected("retire", record_id, revision, now, "archive_conflict")
    try:
        scope = _scope(record.get("scope", {}))
    except ValueError as exc:
        return _rejected("retire", record_id, revision, now, str(exc))
    tombstone = {"schema_version": "memory_tombstone/v1", "tombstone_id": tombstone_id, "record_id": record_id, "revision": revision, "scope": scope, "operation_id": f"memory-retire-{record_id}-r{revision}", "reason_code": "retired_archive", "actor_class": "operator", "tombstoned_at": _stamp(now)}
    manifest = _manifest(((f"record:{record_id}:r{revision}", "record", f"records/{record_id}.json"), (f"tombstone:{tombstone_id}", "tombstone", f"tombstones/{tombstone_id}.json")))
    mutations = (LifecycleMutation("archive_current", "move", archive, f"record:{record_id}:r{revision}", "record", f"records/{record_id}.json"), LifecycleMutation("write_retired_tombstone", "write", f"tombstones/{tombstone_id}.json", f"tombstone:{tombstone_id}", "tombstone", payload=tombstone))
    return _plan("retire", record_id, revision, scope, now, manifest, mutations, guard_digest=_record_digest(record))


def build_memory_restore(paths: OmjPaths, record_id: str = "", revision: int | None = None, *, now: datetime, candidate_id: str | None = None) -> LifecyclePlan:
    invalid = _validate_build_identity("restore", record_id, revision, now)
    if invalid:
        return invalid
    archived, relative, error = _archived_record(paths, record_id, revision)
    if error:
        return _rejected("restore", record_id, revision, now, error)
    current, current_error = _read_json(paths.memory_dir / "records", f"{record_id}.json")
    if current_error not in {None, "already_absent", "record_not_found"}:
        return _rejected("restore", record_id, revision, now, "current_record_unreadable")
    if current is not None and _record_revision(current) >= revision:
        return _rejected("restore", record_id, revision, now, "newer_live_revision_conflict")
    if (paths.memory_dir / f"tombstones/hard-deleted-{record_id}-r{revision}.json").exists():
        return _rejected("restore", record_id, revision, now, "tombstoned_identity")
    candidate_id = candidate_id or _candidate_id("restore", record_id, revision)
    if not _safe_token(candidate_id):
        raise ValueError("unsafe_candidate_id")
    if _contains_sensitive_text(dict(archived)) or any(pattern.search(json.dumps(dict(archived), default=str)) for pattern in _CREDENTIAL_SHAPES):
        return _rejected("restore", record_id, revision, now, "safety_blocked_in_source")
    try:
        scope = _scope(archived.get("scope", {}))
    except ValueError as exc:
        return _rejected("restore", record_id, revision, now, str(exc))
    candidate = _pending_candidate(archived, candidate_id, revision + 1, "restore")
    manifest = _manifest(((f"archive:{record_id}:r{revision}", "archive", relative), (f"candidate:{candidate_id}", "candidate", f"candidates/{candidate_id}.json")))
    return _plan("restore", record_id, revision, scope, now, manifest, (LifecycleMutation("write_restore_candidate", "write", f"candidates/{candidate_id}.json", f"candidate:{candidate_id}", "candidate", payload=candidate),), guard_digest=_record_digest(archived))


def build_memory_reapproval(paths: OmjPaths, candidate_id: str, *, reviewer_claim: str, now: datetime) -> LifecyclePlan:
    if not _safe_token(candidate_id):
        raise ValueError("unsafe_candidate_id")
    candidate, error = _read_json(paths.memory_dir / "candidates", f"{candidate_id}.json")
    if error or candidate is None or str(candidate.get("schema_version", "")) != "project_memory_candidate/v2" or str(candidate.get("status", "")) != "pending_review" or not isinstance(candidate.get("admission"), Mapping) or str(candidate["admission"].get("state", "")) != "pending_review":
        return _rejected("reapprove", candidate_id, 1, now, "restore_candidate_not_pending")
    reviewer = str(reviewer_claim or "")
    if not _safe_token(reviewer) or _contains_sensitive_text(reviewer) or any(pattern.search(reviewer) for pattern in _CREDENTIAL_SHAPES):
        return _rejected("reapprove", candidate.get("record_id", candidate_id), candidate.get("candidate_revision", 1), now, "unsafe_reviewer_claim")
    record_id = str(candidate.get("record_id", ""))
    revision = candidate.get("candidate_revision", 2)
    if not _safe_token(record_id) or not isinstance(revision, int) or isinstance(revision, bool) or revision < 2:
        return _rejected("reapprove", candidate_id, 1, now, "restore_candidate_invalid")
    current, current_error = _current_record(paths, record_id, revision)
    if current_error is None and current:
        return _rejected("reapprove", record_id, revision, now, "newer_live_revision_conflict")
    replacement = candidate.get("replacement") if isinstance(candidate.get("replacement"), Mapping) else candidate
    if _contains_sensitive_text(dict(replacement)) or any(pattern.search(json.dumps(dict(replacement), default=str)) for pattern in _CREDENTIAL_SHAPES):
        return _rejected("reapprove", record_id, revision, now, "safety_blocked_in_summary")
    current, current_error = _read_json(paths.memory_dir / "records", f"{record_id}.json")
    if current_error not in {None, "already_absent"} or (current is not None and _record_revision(current) >= revision):
        return _rejected("reapprove", record_id, revision, now, "newer_live_revision_conflict")
    record = _approved_record(replacement, record_id, revision, reviewer, now)
    scope = _scope(record.get("scope", {"kind": "project", "ref": "default"}))
    review_id = str(record["admission"]["review_id"])
    review = _review(record, review_id, reviewer)
    updated = {**candidate, "status": "approved", "reviewed_at": _stamp(now), "admission": record["admission"]}
    manifest = _manifest(((f"candidate:{candidate_id}", "candidate", f"candidates/{candidate_id}.json"), (f"record:{record_id}:r{revision}", "record", f"records/{record_id}.json"), (f"review:{review_id}", "review", f"reviews/{review_id}.json")))
    mutations = (LifecycleMutation("write_reapproved_record", "write", f"records/{record_id}.json", f"record:{record_id}:r{revision}", "record", payload=record), LifecycleMutation("write_reapproval_review", "write", f"reviews/{review_id}.json", f"review:{review_id}", "review", payload=review), LifecycleMutation("mark_candidate_reapproved", "write", f"candidates/{candidate_id}.json", f"candidate:{candidate_id}", "candidate", payload=updated))
    return _plan("reapprove", record_id, revision, scope, now, manifest, mutations, guard_digest=_record_digest(candidate))


def build_memory_correction(paths: OmjPaths, record_id: str = "", revision: int | None = None, summary: str = "", *, now: datetime, candidate_id: str | None = None) -> LifecyclePlan:
    invalid = _validate_build_identity("correct", record_id, revision, now)
    if invalid:
        return invalid
    record, error = _current_record(paths, record_id, revision)
    if error:
        return _rejected("correct", record_id, revision, now, error)
    candidate_id = candidate_id or _candidate_id("correct", record_id, revision)
    if not _safe_token(candidate_id):
        raise ValueError("unsafe_candidate_id")
    clean_summary = str(summary or "").strip()[:500]
    if _contains_sensitive_text(clean_summary) or any(pattern.search(clean_summary) for pattern in _CREDENTIAL_SHAPES):
        return _rejected("correct", record_id, revision, now, "safety_blocked_in_summary")
    source_issue = _source_issue(record, paths=paths)
    if source_issue:
        return _rejected("correct", record_id, revision, now, source_issue)
    replacement: dict[str, object] = dict(record)
    replacement["summary"] = _redact(clean_summary)
    staleness = dict(_staleness(record))
    if staleness.get("resolution") == "open":
        staleness.pop("open_expires_at", None)
        staleness.update({"resolution": "resolved", "resolved_at": _stamp(now)})
        replacement["staleness"] = staleness
    candidate = _pending_candidate(replacement, candidate_id, revision + 1, "correction")
    history = {**record, "superseded_by": {"schema_version": PROJECT_MEMORY_RECORD_SCHEMA_VERSION, "record_id": record_id, "revision": revision + 1, "scope": record.get("scope", {"kind": "project", "ref": "default"})}}
    scope = _scope(record.get("scope", {}))
    manifest = _manifest(((f"record:{record_id}:r{revision}", "record", f"records/{record_id}.json"), (f"history:{record_id}:r{revision}", "history", f"history/{record_id}.r{revision}.json"), (f"candidate:{candidate_id}", "candidate", f"candidates/{candidate_id}.json")))
    mutations = (LifecycleMutation("write_superseded_history", "write", f"history/{record_id}.r{revision}.json", f"history:{record_id}:r{revision}", "history", payload=history), LifecycleMutation("remove_current_revision", "delete", f"records/{record_id}.json", f"record:{record_id}:r{revision}", "record"), LifecycleMutation("write_correction_candidate", "write", f"candidates/{candidate_id}.json", f"candidate:{candidate_id}", "candidate", payload=candidate))
    return _plan("correct", record_id, revision, scope, now, manifest, mutations, guard_digest=_record_digest(record))


def build_memory_confirmation(paths: OmjPaths, record_id: str, revision: int, *, now: datetime, candidate_id: str | None = None) -> LifecyclePlan:
    record, error = _current_record(paths, record_id, revision)
    if error:
        return _rejected("confirm", record_id, revision, now, error)
    if _resolution(record) != "open":
        return _rejected("confirm", record_id, revision, now, "not_open")
    return build_memory_correction(paths, record_id, revision, str(record.get("summary", "")), now=now, candidate_id=candidate_id)


build_memory_confirm = build_memory_confirmation


def build_memory_keep_open(paths: OmjPaths, record_id: str, revision: int, *, now: datetime) -> LifecyclePlan:
    record, error = _current_record(paths, record_id, revision)
    if error:
        return _rejected("keep_open", record_id, revision, now, error)
    if _resolution(record) != "open":
        return _rejected("keep_open", record_id, revision, now, "not_open")
    updated = dict(record)
    updated["staleness"] = {**dict(_staleness(record)), "reminded_at": _stamp(now)}
    scope = _scope(record.get("scope", {}))
    mutation = LifecycleMutation("reset_open_reminder", "write", f"records/{record_id}.json", f"record:{record_id}:r{revision}", "record", payload=updated)
    return _plan("keep_open", record_id, revision, scope, now, _manifest(((f"record:{record_id}:r{revision}", "record", f"records/{record_id}.json"),)), (mutation,), guard_digest=_record_digest(record))


def build_memory_prune(paths: OmjPaths, record_id: str = "", revision: int | None = None, *, now: datetime) -> LifecyclePlan:
    invalid = _validate_build_identity("prune", record_id, revision, now)
    if invalid:
        return invalid
    record, error = _current_record(paths, record_id, revision)
    if error:
        return _rejected("prune", record_id, revision, now, error)
    if _retention_class(record) != "volatile" or _expiry_reason(record, now, paths=paths) != "expired_volatile" or _admission_state(record) not in {"approved_manual", "approved_auto_safe", "approved"}:
        return _rejected("prune", record_id, revision, now, "prune_requires_expired_approved_volatile")
    try:
        scope = _scope(record.get("scope", {}))
    except ValueError as exc:
        return _rejected("prune", record_id, revision, now, str(exc))
    tombstone_id = f"hard-deleted-{record_id}-r{revision}"
    tombstone = {"schema_version": "memory_tombstone/v1", "tombstone_id": tombstone_id, "record_id": record_id, "revision": revision, "scope": scope, "operation_id": f"memory-prune-{record_id}-r{revision}", "reason_code": "hard_deleted_local", "actor_class": "operator", "tombstoned_at": _stamp(now)}
    manifest = _manifest(((f"record:{record_id}:r{revision}", "record", f"records/{record_id}.json"), (f"tombstone:{tombstone_id}", "tombstone", f"tombstones/{tombstone_id}.json")))
    mutations = (LifecycleMutation("remove_expired_record", "delete", f"records/{record_id}.json", f"record:{record_id}:r{revision}", "record"), LifecycleMutation("write_hard_delete_tombstone", "write", f"tombstones/{tombstone_id}.json", f"tombstone:{tombstone_id}", "tombstone", payload=tombstone))
    return _plan("prune", record_id, revision, scope, now, manifest, mutations, guard_digest=_record_digest(record))


def _require_plan_guard(paths: OmjPaths, plan: LifecyclePlan) -> None:
    if not plan.report.get("eligible"):
        raise ValueError(str(plan.report.get("reason_code", "operation_rejected")))
    manifest = plan.report.get("manifest")
    expected = str(plan.report.get("guard_digest", ""))
    guard_kind = "archive" if plan.operation_type == "restore" else "candidate" if plan.operation_type == "reapprove" else "record"
    source = next((item for item in manifest if isinstance(item, Mapping) and str(item.get("artifact_kind", "")) == guard_kind), None)
    if not isinstance(source, Mapping):
        raise ValueError("operation_guard_missing")
    value, error = _read_json(paths.memory_dir, str(source.get("relative_path", "")))
    if error or value is None or _record_digest(value) != expected:
        raise ValueError("operation_guard_mismatch")
    if guard_kind in {"record", "archive"} and (value.get("record_id") != plan.record_id or _record_revision(value) != plan.revision):
        raise ValueError("operation_guard_mismatch")
    if plan.operation_type == "retire" and (paths.memory_dir / f"archive/{plan.record_id}.r{plan.revision}.json").exists():
        raise ValueError("operation_guard_mismatch")
    if plan.operation_type == "restore":
        if (paths.memory_dir / f"tombstones/hard-deleted-{plan.record_id}-r{plan.revision}.json").exists():
            raise ValueError("operation_guard_mismatch")
        current, current_error = _read_json(paths.memory_dir / "records", f"{plan.record_id}.json")
        if current_error not in {None, "already_absent"} or (current is not None and _record_revision(current) >= plan.revision):
            raise ValueError("operation_guard_mismatch")


def _execute(paths: OmjPaths, plan: LifecyclePlan, transaction_executor: LifecycleTransactionExecutor | None) -> dict[str, object]:
    _require_plan_guard(paths, plan)
    if transaction_executor is None:
        raise ValueError("transaction_executor_required")
    result = transaction_executor(paths, plan)
    receipt = result.get("receipt") if isinstance(result, Mapping) else None
    if not isinstance(receipt, Mapping) or validate_lifecycle_receipt(receipt):
        raise ValueError("invalid_transaction_receipt")
    expected = {mutation.target_id for mutation in plan.mutations}
    actual = {str(item.get("target_id", "")) for item in receipt.get("outcomes", []) if isinstance(item, Mapping)}
    if not expected.issubset(actual):
        raise ValueError("transaction_receipt_missing_target")
    return {"operation_id": plan.operation_id, "applied": True, "receipt": dict(receipt), "next_action": plan.report.get("next_action", ""), "claim_boundary": "Receipt records only what the supplied transaction executor reported for named OMJ-local targets; it never proves deletion or erasure outside that set."}


def apply_memory_retirement(paths: OmjPaths, plan: LifecyclePlan, *, transaction_executor: LifecycleTransactionExecutor | None = None) -> dict[str, object]:
    return _execute(paths, plan, transaction_executor)


def apply_memory_restore(paths: OmjPaths, plan: LifecyclePlan, *, transaction_executor: LifecycleTransactionExecutor | None = None) -> dict[str, object]:
    return _execute(paths, plan, transaction_executor)


def apply_memory_reapproval(paths: OmjPaths, plan: LifecyclePlan, *, transaction_executor: LifecycleTransactionExecutor | None = None) -> dict[str, object]:
    return _execute(paths, plan, transaction_executor)


def apply_memory_correction(paths: OmjPaths, plan: LifecyclePlan, *, transaction_executor: LifecycleTransactionExecutor | None = None) -> dict[str, object]:
    return _execute(paths, plan, transaction_executor)


def apply_memory_confirmation(paths: OmjPaths, plan: LifecyclePlan, *, transaction_executor: LifecycleTransactionExecutor | None = None) -> dict[str, object]:
    return _execute(paths, plan, transaction_executor)


apply_memory_confirm = apply_memory_confirmation


def apply_memory_keep_open(paths: OmjPaths, plan: LifecyclePlan, *, transaction_executor: LifecycleTransactionExecutor | None = None) -> dict[str, object]:
    return _execute(paths, plan, transaction_executor)


def apply_memory_prune(paths: OmjPaths, plan: LifecyclePlan, *, transaction_executor: LifecycleTransactionExecutor | None = None, confirm_hard_delete_local: bool = False, resume: bool = False) -> dict[str, object]:
    if not confirm_hard_delete_local:
        raise ValueError("hard_delete_confirmation_required")
    return _execute(paths, plan, transaction_executor)


def make_lifecycle_receipt(plan: LifecyclePlan, outcomes: Sequence[Mapping[str, object]]) -> dict[str, object]:
    bounded = [dict(item) for item in [*outcomes, *plan.preserved]][:MAX_MANIFEST_TARGETS]
    return {"schema_version": RECEIPT_SCHEMA_VERSION, "operation_id": plan.operation_id, "operation_type": plan.operation_type, "record_id": plan.record_id, "revision": plan.revision, "scope": dict(plan.scope), "actor_class": "operator", "created_at": _stamp(plan.now), "completed_at": _stamp(plan.now), "state": "completed", "outcomes": bounded}


def validate_lifecycle_receipt(receipt: Mapping[str, object]) -> list[str]:
    if not isinstance(receipt, Mapping):
        return ["invalid_receipt"]
    errors = [f"unsupported:{key}" for key in sorted(set(receipt) - _RECEIPT_FIELDS)]
    if receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION or receipt.get("state") != "completed":
        errors.append("invalid_receipt_state")
    if not all(_safe_token(receipt.get(key)) for key in ("operation_id", "operation_type", "record_id", "actor_class")):
        errors.append("invalid_receipt_identifier")
    revision = receipt.get("revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        errors.append("invalid_receipt_revision")
    try:
        _scope(receipt.get("scope", {}))
    except ValueError:
        errors.append("invalid_receipt_scope")
    if _parse_time(receipt.get("created_at")) is None or _parse_time(receipt.get("completed_at")) is None:
        errors.append("invalid_receipt_timestamp")
    outcomes = receipt.get("outcomes")
    if not isinstance(outcomes, list) or len(outcomes) > MAX_MANIFEST_TARGETS:
        errors.append("invalid_receipt_outcomes")
        return errors
    for outcome in outcomes:
        if not isinstance(outcome, Mapping) or set(outcome) != _OUTCOME_FIELDS or not _safe_token(outcome.get("target_id")) or not _safe_token(outcome.get("artifact_kind")) or outcome.get("outcome") not in _ALLOWED_OUTCOMES or not _safe_token(outcome.get("reason_code")):
            errors.append("invalid_receipt_outcome")
    return errors


def retrieval_report_identity(report: Mapping[str, object]) -> dict[str, object]:
    return {field: report.get(field) for field in RETRIEVAL_IDENTITY_FIELDS}


def _case_rows(report: Mapping[str, object]) -> list[dict[str, object]]:
    cases = report.get("cases")
    return [dict(row) for row in cases if isinstance(row, Mapping)] if isinstance(cases, list) else []


def compare_retrieval_reports(left: Mapping[str, object], right: Mapping[str, object]) -> dict[str, object]:
    left_identity, right_identity = retrieval_report_identity(left), retrieval_report_identity(right)
    mismatched = sorted(field for field in RETRIEVAL_IDENTITY_FIELDS if left_identity[field] != right_identity[field])
    base = {"schema_version": RETRIEVAL_COMPARISON_SCHEMA_VERSION, "comparable": not mismatched, "mismatched_identity_fields": mismatched, "left_identity": left_identity, "right_identity": right_identity, "executor_neutral": True, "fairness": {"method": "case-id paired comparison", "executor_neutral": True}}
    if mismatched:
        return {**base, "reason": "retrieval reports are comparable only when every identity field matches"}
    left_cases = {str(case.get("case_id", "")): case for case in _case_rows(left)}
    right_cases = {str(case.get("case_id", "")): case for case in _case_rows(right)}
    return {**base, "identical_results": left.get("cases") == right.get("cases"), "regressed_cases": sorted(case_id for case_id, before in left_cases.items() if bool(before.get("passed", False)) and not bool(right_cases.get(case_id, {}).get("passed", False))), "improved_cases": sorted(case_id for case_id, after in right_cases.items() if bool(after.get("passed", False)) and not bool(left_cases.get(case_id, {}).get("passed", False))), "reason": "same retrieval identity"}


def make_retrieval_report(*, cases: Sequence[Mapping[str, object]] = (), target_revision: str = "", fixture_digest: str = "", evaluator_version: str = RETRIEVAL_EVALUATOR_VERSION, corpus_version: str = "", retrieval_configuration: Mapping[str, object] | None = None, clock: str = "", baseline: Mapping[str, object] | None = None, variant: Mapping[str, object] | None = None, fairness: Mapping[str, object] | None = None) -> dict[str, object]:
    configuration = dict(retrieval_configuration or {})
    fixture = fixture_digest or hashlib.sha256(json.dumps([dict(case) for case in cases], sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()
    config_digest = hashlib.sha256(json.dumps(configuration, sort_keys=True, default=str, separators=(",", ":")).encode()).hexdigest()
    rows = [dict(case) for case in cases]
    return {"schema_version": RETRIEVAL_EVALUATION_SCHEMA_VERSION, "evaluator_version": evaluator_version, "corpus_version": corpus_version, "fixture_digest": fixture, "retrieval_configuration": configuration, "retrieval_config_digest": config_digest, "clock": clock, "target_revision": str(target_revision or ""), "cases": rows, "case_count": len(rows), "baseline": dict(baseline or {}), "variant": dict(variant or {}), "fairness": {"executor_neutral": True, **dict(fairness or {})}, "execution_boundary": "Offline local metadata only: no model call, provider call, network request, credential read, or executor run.", "claim_boundary": "Prepared retrieval regression evidence only; it is not execution, review, CI, merge, provider-quality, or Hermes internal-memory evidence."}


def run_memory_retrieval_evaluation(*, target_revision: str = "", cases: Sequence[Mapping[str, object]] = (), pack_builder: object = None, live_arms: object = None) -> dict[str, object]:
    """Build a deterministic local report from supplied case metadata only.

    ``pack_builder`` and ``live_arms`` are accepted for API compatibility but
    deliberately not invoked: this wrapper is executor-neutral and cannot
    observe a provider, host delivery, or model execution.
    """
    return make_retrieval_report(cases=cases, target_revision=target_revision)
