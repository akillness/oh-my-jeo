from __future__ import annotations

"""Revision-bound, offline lifecycle and retrieval evidence for OMJ memory.

This module deliberately owns planning and validation only.  It never discovers
or runs an executor, calls a model, or claims that a host/provider observed a
side effect.  Mutation is possible only through the caller-supplied transaction
executor after the plan's revision and manifest guards still match.
"""

import hashlib
import inspect
import json
import os
import re
import stat
import threading
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

try:
    import fcntl
except ImportError:
    fcntl = None

from ..local_store import atomic_write_bytes, read_json_object_result
from ..paths import OmjPaths, resolve_paths
from .memory import (
    MAX_MEMORY_JSON_BYTES,
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
_LIFECYCLE_LOCKS: dict[str, threading.RLock] = {}
_LIFECYCLE_LOCKS_GUARD = threading.Lock()
_LIFECYCLE_LOCK_LOCAL = threading.local()


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
        return _utc(parsed)
    except (TypeError, ValueError, OverflowError):
        return None


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
    if isinstance(admission, Mapping) and "state" in admission:
        state = admission["state"]
    else:
        state = record.get("admission_state", record.get("review_status", ""))
    status = state if isinstance(state, str) else ""
    return {"approved": "approved_manual", "auto-safe": "approved_auto_safe"}.get(status, status)


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
    unreadable = {"unreadable", "missing", "corrupt", "source_unreadable", "failed", "unknown", "unavailable", "indeterminate"}
    if paths is not None and not str(record.get("source", "") or "").strip():
        return "source_unreadable"
    for key in ("source_status", "source_state", "source_health"):
        value = str(record.get(key, "") or "").strip().lower()
        if value in {"changed", "source_changed"}:
            return "source_changed"
        if value in unreadable:
            return "source_unreadable"
    evidence = record.get("source_evidence")
    if evidence is not None and not isinstance(evidence, Mapping):
        return "source_unreadable"
    if isinstance(evidence, Mapping):
        status = str(evidence.get("status", "") or "").strip().lower()
        if status in {"changed", "source_changed"}:
            return "source_changed"
        if status in unreadable:
            return "source_unreadable"
        if paths is not None and (evidence.get("path") or evidence.get("sha256")):
            if not isinstance(evidence.get("path"), str) or not re.fullmatch(r"[0-9a-fA-F]{64}", str(evidence.get("sha256", ""))):
                return "source_unreadable"
            candidate = Path(evidence["path"])
            if not candidate.is_absolute():
                candidate = paths.omj_home.parent / candidate
            descriptor = None
            try:
                root, resolved = paths.omj_home.parent.resolve(), candidate.resolve(strict=False)
                if root != resolved and root not in resolved.parents:
                    return "source_unreadable"
                ancestor = candidate
                while True:
                    if ancestor.is_symlink():
                        return "source_unreadable"
                    if ancestor.resolve(strict=False) == root:
                        break
                    if ancestor.parent == ancestor:
                        return "source_unreadable"
                    ancestor = ancestor.parent
                descriptor = os.open(candidate, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
                info = os.fstat(descriptor)
                if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_MEMORY_JSON_BYTES:
                    return "source_unreadable"
                with os.fdopen(descriptor, "rb") as stream:
                    descriptor = None
                    content = stream.read(MAX_MEMORY_JSON_BYTES + 1)
                if len(content) > MAX_MEMORY_JSON_BYTES:
                    return "source_unreadable"
                digest = hashlib.sha256(content).hexdigest()
            except (OSError, ValueError):
                return "source_unreadable"
            finally:
                if descriptor is not None:
                    os.close(descriptor)
            if digest != str(evidence["sha256"]).lower():
                return "source_changed"
    return ""


def _expiry_reason(record: Mapping[str, object], now: datetime, *, paths: OmjPaths | None = None) -> str:
    deadlines: list[tuple[datetime, str]] = []
    retention_class = _retention_class(record)
    if retention_class not in {"volatile", "standard", "durable"}:
        return "retention_invalid"
    expiry_reason = f"expired_{retention_class}"
    for container in (record, record.get("retention"), record.get("ttl"), _staleness(record)):
        if not isinstance(container, Mapping):
            continue
        for key in ("expires_at", "open_expires_at"):
            if container.get(key) not in (None, ""):
                parsed = _parse_time(container[key])
                if parsed is None:
                    return "unreadable_expiry"
                deadlines.append((parsed, expiry_reason))
        if container.get("expires_at") in (None, "") and container.get("ttl_days") is not None:
            admitted = _parse_time(container.get("admitted_at", container.get("created_at", record.get("created_at"))))
            raw_days = container.get("ttl_days")
            try:
                ttl_days = int(raw_days)
                if isinstance(raw_days, bool) or str(ttl_days) != str(raw_days) or admitted is None or ttl_days < 0:
                    return "unreadable_expiry"
                deadline = admitted + timedelta(days=ttl_days)
            except (TypeError, ValueError, OverflowError):
                return "unreadable_expiry"
            deadlines.append((deadline, expiry_reason))
    stale_deadlines: list[datetime] = []
    for container in (record, _staleness(record)):
        for key in ("stale_after", "review_due_at"):
            if container.get(key) not in (None, ""):
                parsed = _parse_time(container[key])
                if parsed is None:
                    return "unreadable_staleness"
                stale_deadlines.append(parsed)
    if deadlines and _utc(now) >= min(deadline for deadline, _ in deadlines):
        return expiry_reason
    source = _source_issue(record, paths=paths)
    if source:
        return source
    if stale_deadlines and _utc(now) >= min(stale_deadlines):
        return "stale_review_required"
    return "eligible"


def _unresolved_marker(record: Mapping[str, object], now: datetime) -> tuple[str, int | None]:
    if _resolution(record) != "open":
        return "", None
    since = _parse_time(_staleness(record).get("open_since"))
    days = max(0, (_utc(now) - since).days) if since else None
    return ("open" if days is None else f"open · {days} days unresolved"), days


def lifecycle_replay_status(record: Mapping[str, object], *, now: datetime, paths: OmjPaths | None = None, include_stale: bool = False) -> dict[str, object]:
    if not isinstance(record, Mapping):
        record = {}
    reason = _expiry_reason(record, now, paths=paths)
    state = _admission_state(record)
    marker, open_days = _unresolved_marker(record, now)
    approved = state in {"approved_manual", "approved_auto_safe"}
    contamination = record.get("contamination")
    safety = record.get("safety")
    if not _record_revision(record):
        reason = "invalid_revision"
    elif record.get("superseded_by"):
        reason = "superseded"
    elif (
        record.get("contaminated")
        or record.get("contamination_class") not in (None, "", "none", "clean")
        or (isinstance(contamination, Mapping) and contamination.get("state", contamination.get("status")) not in (None, "", "none", "clean"))
        or (contamination and not isinstance(contamination, Mapping))
        or (isinstance(safety, Mapping) and safety.get("status") == "blocked")
    ):
        reason = "contaminated"
    replay_eligible = approved and (reason == "eligible" or (include_stale and reason == "stale_review_required"))
    refused_states = {"rejected", "blocked", "blocked_review_required", "expired", "superseded", "retired", "archived"}
    reason_code = reason if reason != "eligible" else (state if state in refused_states else "review_required" if not approved else "unresolved_open" if marker else "eligible")
    staleness = _staleness(record)
    deadline_value = staleness.get("open_expires_at", staleness.get("review_due_at"))
    deadline = _parse_time(deadline_value)
    review_deadline = _stamp(deadline) if deadline is not None else "" if deadline_value in (None, "") else "invalid"
    return {"record_id": _redact_public(record.get("record_id", "")), "revision": _record_revision(record) or None, "scope": _scope_public(record.get("scope", {})), "admission_state": _redact_public(state), "retention_class": _redact_public(_retention_class(record)), "retention_origin": _redact_public(_retention_origin(record)), "tier": _redact_public(_tier(record)), "resolution": _resolution(record), "review_deadline": review_deadline, "resolution_marker": marker, "open_days": open_days, "replay_eligible": replay_eligible, "reason_code": reason_code}


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


def _target_guard(paths: OmjPaths, relative: str) -> dict[str, object]:
    value, error = _read_json(paths.memory_dir, relative)
    if error not in {None, "already_absent"}:
        raise ValueError("operation_guard_mismatch")
    return {"relative_path": relative, "state": "present" if value is not None else "absent", "digest": _record_digest(value) if value is not None else ""}


def _lifecycle_guards(paths: OmjPaths, record_id: str, current: Mapping[str, object] | None, origin_revision: int, next_revision: int, *, restore: bool = False) -> dict[str, object]:
    destination = {"relative_path": f"records/{record_id}.json", "state": "present" if current is not None else "absent", "digest": _record_digest(current) if current is not None else ""}
    tombstones = []
    for revision in sorted({origin_revision, next_revision}):
        for kind in ("retired", "hard-deleted"):
            guard = _target_guard(paths, f"tombstones/{kind}-{record_id}-r{revision}.json")
            if guard["state"] == "present" and not (restore and kind == "retired" and revision == origin_revision):
                raise ValueError("tombstoned_identity")
            tombstones.append(guard)
    return {"destination_guard": destination, "tombstone_guards": tombstones}


def _candidate_id(operation: str, record_id: str, revision: int) -> str:
    return f"cand-{operation}-" + hashlib.sha256(f"{operation}:{record_id}:{revision}".encode()).hexdigest()[:24]




def _pending_candidate(origin: Mapping[str, object], candidate_id: str, revision: int, lifecycle: str, *, replacement_source: Mapping[str, object] | None = None) -> dict[str, object]:
    source = replacement_source if replacement_source is not None else origin
    keys = ("record_type", "summary", "scope", "tags", "source", "source_ref", "source_class", "source_evidence", "ttl", "staleness", "retention", "retention_class", "retention_origin", "attention", "tier", "safety", "redaction_policy", "claim_boundary")
    replacement = {key: source[key] for key in keys if key in source}
    candidate: dict[str, object] = {
        "schema_version": "project_memory_candidate/v2",
        "candidate_id": candidate_id,
        "candidate_revision": revision,
        "revision": revision,
        "record_id": str(origin.get("record_id", "")),
        "artifact_kind": "record",
        "status": "pending_review",
        "admission": {"state": "pending_review"},
        "origin": {"record_id": str(origin.get("record_id", "")), "revision": _record_revision(origin), "digest": _record_digest(origin)},
        "lifecycle": lifecycle,
        "replacement": replacement,
    }
    candidate.update(replacement)
    return candidate


def _review(record: Mapping[str, object], review_id: str, reviewer: str) -> dict[str, object]:
    return {"schema_version": "project_memory_review_record/v1", "review_id": review_id, "record_id": str(record.get("record_id", "")), "revision": _record_revision(record), "decision": "approved_manual", "reviewer_claim": _redact_public(reviewer), "payload_digest": _record_digest(record), "redaction_policy": "metadata_only"}


def _approved_record(replacement: Mapping[str, object], record_id: str, revision: int, reviewer: str, now: datetime, *, candidate_id: str = "") -> dict[str, object]:
    record: dict[str, object] = {key: value for key, value in replacement.items() if key not in {"admission", "review_status", "record_id", "revision", "candidate_id"}}
    record.update({"schema_version": PROJECT_MEMORY_RECORD_SCHEMA_VERSION, "record_id": record_id, "revision": revision, "review_status": "approved", "approved_by": reviewer, "approved_at": _stamp(now), "updated_at": _stamp(now), "redaction_policy": "metadata_only"})
    if candidate_id:
        record["candidate_id"] = candidate_id
    previous = replacement.get("admission")
    admission = dict(previous) if isinstance(previous, Mapping) else {}
    admission.update({"state": "approved_manual", "review_id": f"review-{record_id}-r{revision}", "reviewer": reviewer, "reviewed_at": _stamp(now), "payload_digest": _record_digest(record)})
    record["admission"] = admission
    return record


def _manifest(items: Sequence[tuple[str, str, str]]) -> list[dict[str, object]]:
    return [{"target_id": target_id, "artifact_kind": kind, "relative_path": relative} for target_id, kind, relative in items]


def _plan(operation: str, record_id: str, revision: int, scope: Mapping[str, object], now: datetime, manifest: Sequence[Mapping[str, object]], mutations: Sequence[LifecycleMutation], *, preserved: Sequence[Mapping[str, object]] = (), guard_digest: str = "", origin_guard: Mapping[str, object] | None = None, state_guards: Mapping[str, object] | None = None) -> LifecyclePlan:
    next_actions = {"retire": "Apply only after review: archive the exact expired standard revision; it is not deleted.", "restore": "Review/reactivate the pending restored revision; the archive remains unchanged.", "prune": "Apply only with --confirm-hard-delete-local; the receipt is not deletion or erasure proof.", "correct": "Review and approve the pending replacement revision.", "reapprove": "The new active revision remains governed by its immutable review record.", "confirm": "Review and approve the pending replacement revision.", "keep_open": "Apply only after review; only the reminder clock changes."}
    report = {"schema_version": LIFECYCLE_REPORT_SCHEMA_VERSION, "operation": operation, "operation_type": operation, "record_id": record_id, "revision": revision, "scope": dict(scope), "eligible": True, "applied": False, "reason_code": "planned", "reason": "planned", "manifest": list(manifest), "guard_digest": guard_digest, "outcomes": [], "exclusions": ["backups", "filesystem_snapshots", "trash", "synced_copies", "hermes_native", "external_providers", "vector_stores", "executors", "unlinked_artifacts", "recall_usage_counters", "pin_markers"], "next_action": next_actions.get(operation, "Review the prepared plan before applying it."), "claim_boundary": "This is an OMJ-local prepared target-set plan, not deletion, erasure, backup, provider, native-memory, executor, or legal-erasure proof."}
    if origin_guard is not None:
        report["origin_guard"] = dict(origin_guard)
    if state_guards is not None:
        report.update(state_guards)
    return LifecyclePlan(f"memory-{operation}-{record_id}-r{revision}", operation, record_id, revision, dict(scope), now, report, tuple(mutations), tuple(preserved))


def _rejected(operation: str, record_id: object, revision: object, now: datetime, reason: str) -> LifecyclePlan:
    safe_id = str(record_id) if _safe_token(record_id) else "invalid"
    safe_revision = int(revision) if isinstance(revision, int) and not isinstance(revision, bool) and revision > 0 else 1
    report = {"schema_version": LIFECYCLE_REPORT_SCHEMA_VERSION, "operation": operation, "operation_type": operation, "record_id": safe_id, "revision": safe_revision, "scope": {"kind": "project", "ref": "default"}, "eligible": False, "applied": False, "reason_code": reason, "reason": reason.replace("_", " "), "manifest": [], "outcomes": [{"target_id": "rejected:0", "artifact_kind": "local_target", "outcome": "rejected", "reason_code": reason}], "exclusions": [], "next_action": "No apply action: resolve the reported lifecycle guard.", "claim_boundary": "No mutation was planned. This report does not claim deletion, erasure, or any provider/native/executor effect."}
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
    try:
        state_guards = _lifecycle_guards(paths, record_id, current, revision, revision + 1, restore=True)
    except ValueError as exc:
        return _rejected("restore", record_id, revision, now, str(exc))
    manifest = _manifest(((f"archive:{record_id}:r{revision}", "archive", relative), (f"candidate:{candidate_id}", "candidate", f"candidates/{candidate_id}.json")))
    return _plan("restore", record_id, revision, scope, now, manifest, (LifecycleMutation("write_restore_candidate", "write", f"candidates/{candidate_id}.json", f"candidate:{candidate_id}", "candidate", payload=candidate),), guard_digest=_record_digest(archived), state_guards=state_guards)


def build_memory_reapproval(paths: OmjPaths, candidate_id: str, *, reviewer_claim: str, now: datetime) -> LifecyclePlan:
    if not _safe_token(candidate_id):
        raise ValueError("unsafe_candidate_id")
    candidate, error = _read_json(paths.memory_dir / "candidates", f"{candidate_id}.json")
    if error or candidate is None or str(candidate.get("schema_version", "")) != "project_memory_candidate/v2" or str(candidate.get("status", "")) != "pending_review" or not isinstance(candidate.get("admission"), Mapping) or str(candidate["admission"].get("state", "")) != "pending_review":
        return _rejected("reapprove", candidate_id, 1, now, "restore_candidate_not_pending")
    reviewer = str(reviewer_claim or "")
    if not _safe_token(reviewer) or _contains_sensitive_text(reviewer) or any(pattern.search(reviewer) for pattern in _CREDENTIAL_SHAPES):
        return _rejected("reapprove", candidate.get("record_id", candidate_id), candidate.get("revision", candidate.get("candidate_revision", 1)), now, "unsafe_reviewer_claim")
    record_id = str(candidate.get("record_id", ""))
    revision = candidate.get("revision", candidate.get("candidate_revision", 2))
    if not _safe_token(record_id) or not isinstance(revision, int) or isinstance(revision, bool) or revision < 2:
        return _rejected("reapprove", candidate_id, 1, now, "restore_candidate_invalid")
    lifecycle = str(candidate.get("lifecycle", ""))
    origin = candidate.get("origin") if isinstance(candidate.get("origin"), Mapping) else {}
    origin_record: dict[str, object] = {}
    origin_revision = origin.get("revision")
    if not isinstance(origin_revision, int) or isinstance(origin_revision, bool) or origin_revision < 1 or origin_revision + 1 != revision:
        return _rejected("reapprove", record_id, revision, now, "restore_candidate_invalid")
    origin_guard: dict[str, object] | None = None
    if lifecycle == "correction":
        origin_revision = origin.get("revision") if isinstance(origin.get("revision"), int) and not isinstance(origin.get("revision"), bool) else None
        origin_digest = str(origin.get("digest", ""))
        live_origin, live_error = _read_json(paths.memory_dir / "records", f"{record_id}.json")
        retired_tombstone = paths.memory_dir / f"tombstones/retired-{record_id}-r{origin_revision}.json"
        if retired_tombstone.exists():
            return _rejected("reapprove", record_id, revision, now, "retired_origin_refused")
        if (
            origin_revision is None
            or not origin_digest
            or live_error is not None
            or live_origin is None
            or _record_revision(live_origin) != origin_revision
            or _record_digest(live_origin) != origin_digest
        ):
            return _rejected("reapprove", record_id, revision, now, "stale_origin_digest_mismatch")
        origin_record = live_origin
        origin_guard = {"record_id": record_id, "revision": origin_revision, "digest": origin_digest}
    current, current_error = _current_record(paths, record_id, revision)
    if current_error is None and current:
        return _rejected("reapprove", record_id, revision, now, "newer_live_revision_conflict")
    replacement = candidate.get("replacement") if isinstance(candidate.get("replacement"), Mapping) else candidate
    if _contains_sensitive_text(dict(replacement)) or any(pattern.search(json.dumps(dict(replacement), default=str)) for pattern in _CREDENTIAL_SHAPES):
        return _rejected("reapprove", record_id, revision, now, "safety_blocked_in_summary")
    current, current_error = _read_json(paths.memory_dir / "records", f"{record_id}.json")
    if current_error not in {None, "already_absent"} or (current is not None and _record_revision(current) >= revision):
        return _rejected("reapprove", record_id, revision, now, "newer_live_revision_conflict")
    if lifecycle == "correction" and (current is None or _record_digest(current) != str(origin.get("digest", ""))):
        return _rejected("reapprove", record_id, revision, now, "stale_origin_digest_mismatch")
    try:
        state_guards = _lifecycle_guards(paths, record_id, current, origin_revision, revision, restore=lifecycle == "restore")
    except ValueError as exc:
        return _rejected("reapprove", record_id, revision, now, str(exc))
    record = _approved_record(replacement, record_id, revision, reviewer, now, candidate_id=candidate_id)
    scope = _scope(record.get("scope", {"kind": "project", "ref": "default"}))
    review_id = str(record["admission"]["review_id"])
    review = _review(record, review_id, reviewer)
    updated = {**candidate, "status": "approved", "reviewed_at": _stamp(now), "admission": record["admission"]}
    manifest_items: list[tuple[str, str, str]] = [
        (f"candidate:{candidate_id}", "candidate", f"candidates/{candidate_id}.json"),
        (f"record:{record_id}:r{revision}", "record", f"records/{record_id}.json"),
        (f"review:{review_id}", "review", f"reviews/{review_id}.json"),
    ]
    mutations: list[LifecycleMutation] = []
    if lifecycle == "correction":
        if origin_revision is None or not origin_record:
            return _rejected("reapprove", record_id, revision, now, "stale_origin_digest_mismatch")
        archive = f"archive/{record_id}.r{origin_revision}.json"
        if (paths.memory_dir / archive).exists():
            return _rejected("reapprove", record_id, revision, now, "archive_conflict")
        manifest_items.insert(1, (f"archive:{record_id}:r{origin_revision}", "archive", archive))
        mutations.append(LifecycleMutation("archive_reapproved_origin", "move", archive, f"archive:{record_id}:r{origin_revision}", "archive", f"records/{record_id}.json"))
    mutations.extend(
        (
            LifecycleMutation("write_reapproved_record", "write", f"records/{record_id}.json", f"record:{record_id}:r{revision}", "record", payload=record),
            LifecycleMutation("write_reapproval_review", "write", f"reviews/{review_id}.json", f"review:{review_id}", "review", payload=review),
            LifecycleMutation("mark_candidate_reapproved", "write", f"candidates/{candidate_id}.json", f"candidate:{candidate_id}", "candidate", payload=updated),
        )
    )
    manifest = _manifest(manifest_items)
    return _plan("reapprove", record_id, revision, scope, now, manifest, tuple(mutations), guard_digest=_record_digest(candidate), origin_guard=origin_guard, state_guards=state_guards)


def build_memory_correction(paths: OmjPaths, record_id: str = "", revision: int | None = None, summary: str = "", *, now: datetime, candidate_id: str | None = None) -> LifecyclePlan:
    """Stage a pending correction candidate. The live revision is never deleted or
    rewritten here -- it stays readable/recallable until a reviewer runs the
    revision-bound reapproval (``build_memory_reapproval``). The one prior
    approved candidate this record pointed to (if any) is archived (moved, not
    deleted) so at most one open candidate represents this record at a time.
    """
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
    candidate = _pending_candidate(record, candidate_id, revision + 1, "correction", replacement_source=replacement)
    try:
        state_guards = _lifecycle_guards(paths, record_id, record, revision, revision + 1)
    except ValueError as exc:
        return _rejected("correct", record_id, revision, now, str(exc))
    scope = _scope(record.get("scope", {}))
    manifest_items = [(f"record:{record_id}:r{revision}", "record", f"records/{record_id}.json"), (f"candidate:{candidate_id}", "candidate", f"candidates/{candidate_id}.json")]
    mutations = [LifecycleMutation("write_correction_candidate", "write", f"candidates/{candidate_id}.json", f"candidate:{candidate_id}", "candidate", payload=candidate)]
    prior_candidate_id = str(record.get("candidate_id", ""))
    if prior_candidate_id and prior_candidate_id != candidate_id and _safe_token(prior_candidate_id):
        prior_path = paths.memory_dir / "candidates" / f"{prior_candidate_id}.json"
        if prior_path.is_file() and not prior_path.is_symlink():
            archived_relative = f"candidates/superseded/{prior_candidate_id}.json"
            manifest_items.append((f"candidate:{prior_candidate_id}", "candidate", archived_relative))
            mutations.append(LifecycleMutation("archive_superseded_candidate", "move", archived_relative, f"candidate:{prior_candidate_id}", "candidate", f"candidates/{prior_candidate_id}.json"))
    manifest = _manifest(manifest_items)
    return _plan("correct", record_id, revision, scope, now, manifest, tuple(mutations), guard_digest=_record_digest(record), state_guards=state_guards)


def build_memory_confirmation(paths: OmjPaths, record_id: str, revision: int, *, now: datetime, candidate_id: str | None = None) -> LifecyclePlan:
    """Renew an ordinary (or explicitly open) record's review deadline in place.

    Unlike ``build_memory_correction`` this never stages a candidate or bumps
    the revision -- the same revision is rewritten with its staleness/review
    deadline pushed forward. ``candidate_id`` is accepted for CLI-signature
    compatibility only; confirmation never produces a candidate artifact.
    """
    record, error = _current_record(paths, record_id, revision)
    if error:
        return _rejected("confirm", record_id, revision, now, error)
    source_issue = _source_issue(record, paths=paths)
    if source_issue:
        return _rejected("confirm", record_id, revision, now, source_issue)
    staleness = dict(_staleness(record))
    was_open = staleness.get("resolution") == "open"
    stale_days = staleness.get("stale_after_days")
    previous_due = _parse_time(staleness.get("review_due_at"))
    renewed_at = (
        now + timedelta(days=stale_days)
        if isinstance(stale_days, int) and not isinstance(stale_days, bool) and stale_days > 0
        else now
    )
    renewed_due = _stamp(renewed_at)
    if previous_due is not None and _parse_time(renewed_due) <= previous_due:
        renewed_due = _stamp(previous_due + timedelta(seconds=1))
    if was_open:
        staleness.pop("open_expires_at", None)
        staleness.update({"resolution": "resolved", "resolved_at": _stamp(now)})
    staleness["review_due_at"] = renewed_due
    if stale_days:
        staleness["stale_after"] = renewed_due
    updated = dict(record)
    updated["staleness"] = staleness
    updated["revision"] = revision
    updated["updated_at"] = _stamp(now)
    scope = _scope(record.get("scope", {}))
    manifest = _manifest(((f"record:{record_id}:r{revision}", "record", f"records/{record_id}.json"),))
    mutation = LifecycleMutation("renew_confirmation_deadline", "write", f"records/{record_id}.json", f"record:{record_id}:r{revision}", "record", payload=updated)
    return _plan("confirm", record_id, revision, scope, now, manifest, (mutation,), guard_digest=_record_digest(record))


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
    if plan.operation_type in {"restore", "correct", "reapprove"}:
        destination = plan.report.get("destination_guard")
        tombstones = plan.report.get("tombstone_guards")
        if not isinstance(destination, Mapping) or destination.get("relative_path") != f"records/{plan.record_id}.json" or not isinstance(tombstones, list) or not tombstones:
            raise ValueError("operation_guard_missing")
        for guard in (destination, *tombstones):
            if not isinstance(guard, Mapping) or _target_guard(paths, str(guard.get("relative_path", ""))) != dict(guard):
                raise ValueError("operation_guard_mismatch")
    if plan.operation_type == "reapprove":
        origin_guard = plan.report.get("origin_guard")
        if isinstance(origin_guard, Mapping):
            origin_id = origin_guard.get("record_id")
            origin_revision = origin_guard.get("revision")
            origin_digest = str(origin_guard.get("digest", ""))
            if origin_id != plan.record_id or not isinstance(origin_revision, int) or isinstance(origin_revision, bool) or origin_revision < 1 or not origin_digest:
                raise ValueError("operation_guard_mismatch")
            if (paths.memory_dir / f"tombstones/retired-{plan.record_id}-r{origin_revision}.json").exists():
                raise ValueError("operation_guard_mismatch")
            origin_record, origin_error = _read_json(paths.memory_dir / "records", f"{plan.record_id}.json")
            archive = paths.memory_dir / f"archive/{plan.record_id}.r{origin_revision}.json"
            if origin_error is not None or origin_record is None or _record_revision(origin_record) != origin_revision or _record_digest(origin_record) != origin_digest or archive.exists():
                raise ValueError("operation_guard_mismatch")
    if plan.operation_type == "retire" and (paths.memory_dir / f"archive/{plan.record_id}.r{plan.revision}.json").exists():
        raise ValueError("operation_guard_mismatch")
    if plan.operation_type == "restore":
        if (paths.memory_dir / f"tombstones/hard-deleted-{plan.record_id}-r{plan.revision}.json").exists():
            raise ValueError("operation_guard_mismatch")
        current, current_error = _read_json(paths.memory_dir / "records", f"{plan.record_id}.json")
        if current_error not in {None, "already_absent"} or (current is not None and _record_revision(current) >= plan.revision):
            raise ValueError("operation_guard_mismatch")


@contextmanager
def memory_lifecycle_lock(paths: OmjPaths) -> Iterator[None]:
    """Serialize cooperating local writers, not a multi-file crash transaction."""
    root = paths.memory_dir
    lock_path = root / ".lifecycle.lock"
    if lock_path.is_symlink() or any(parent.is_symlink() for parent in lock_path.parents):
        raise ValueError("operation_guard_mismatch")
    if fcntl is None:
        raise ValueError("lifecycle_lock_unavailable")
    key = str(root.resolve(strict=False))
    with _LIFECYCLE_LOCKS_GUARD:
        lock = _LIFECYCLE_LOCKS.setdefault(key, threading.RLock())
    with lock:
        held = getattr(_LIFECYCLE_LOCK_LOCAL, "roots", set())
        if key in held:
            yield
            return
        root.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise ValueError("operation_guard_mismatch")
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            _LIFECYCLE_LOCK_LOCAL.roots = held | {key}
            try:
                yield
            finally:
                _LIFECYCLE_LOCK_LOCAL.roots = held
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def _execute(paths: OmjPaths, plan: LifecyclePlan, transaction_executor: LifecycleTransactionExecutor | None) -> dict[str, object]:
    with memory_lifecycle_lock(paths):
        return _execute_locked(paths, plan, transaction_executor)


def _execute_locked(paths: OmjPaths, plan: LifecyclePlan, transaction_executor: LifecycleTransactionExecutor | None) -> dict[str, object]:
    _require_plan_guard(paths, plan)
    if transaction_executor is None:
        raise ValueError("transaction_executor_required")
    previous: dict[Path, tuple[bytes, int] | None] = {}
    if plan.operation_type == "reapprove":
        root = paths.memory_dir.resolve(strict=False)
        for mutation in plan.mutations:
            for relative in (mutation.target, mutation.source):
                if relative is None:
                    continue
                path = paths.memory_dir / relative
                if path in previous:
                    continue
                if root not in path.resolve(strict=False).parents or path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != paths.memory_dir):
                    raise ValueError("operation_guard_mismatch")
                try:
                    previous[path] = (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
                except FileNotFoundError:
                    previous[path] = None
    try:
        result = transaction_executor(paths, plan)
        receipt = result.get("receipt") if isinstance(result, Mapping) else None
        if not isinstance(receipt, Mapping) or validate_lifecycle_receipt(receipt):
            raise ValueError("invalid_transaction_receipt")
        identity = {"operation_id": plan.operation_id, "operation_type": plan.operation_type, "record_id": plan.record_id, "revision": plan.revision, "scope": dict(plan.scope)}
        if any(receipt.get(key) != value for key, value in identity.items()):
            raise ValueError("transaction_receipt_identity_mismatch")
        outcomes = {item["target_id"]: item for item in receipt["outcomes"]}
        if len(outcomes) != len(receipt["outcomes"]):
            raise ValueError("invalid_transaction_receipt")
        success = {"write": {"written", "rewritten"}, "move": {"moved"}, "delete": {"removed", "already_absent"}}
        for mutation in plan.mutations:
            outcome = outcomes.get(mutation.target_id)
            if outcome is None:
                raise ValueError("transaction_receipt_missing_target")
            if outcome["artifact_kind"] != mutation.artifact_kind or outcome["outcome"] not in success.get(mutation.action, set()):
                raise ValueError("transaction_receipt_unsuccessful_mutation")
    except BaseException:
        # Exception rollback only; separate file renames are not crash-atomic.
        for path, original in reversed(previous.items()):
            if original is None:
                path.unlink(missing_ok=True)
            else:
                content, mode = original
                if not path.is_file() or path.read_bytes() != content:
                    atomic_write_bytes(path, content)
                if stat.S_IMODE(path.stat().st_mode) != mode:
                    path.chmod(mode)
        raise
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


_EVAL_RECORD_SCHEMA_VERSION = PROJECT_MEMORY_RECORD_SCHEMA_VERSION
_EVAL_UNBOUNDED_LIMIT = 10_000


def _eval_record(spec: Mapping[str, object]) -> dict[str, object]:
    """Materialise declared fixture facts without granting them approval."""
    passthrough = {"schema_version", "revision", "candidate_id", "record_type", "summary", "scope", "tags", "source", "source_ref", "source_class", "source_status", "source_state", "source_health", "source_evidence", "admission", "admission_state", "review_status", "approved_by", "approved_at", "created_at", "updated_at", "ttl", "expires_at", "ttl_days", "retention", "retention_class", "retention_origin", "staleness", "stale_after", "review_due_at", "attention", "tier", "superseded_by", "contamination_class", "contaminated", "contamination", "safety", "redaction_policy", "claim_boundary"}
    if not isinstance(spec, Mapping) or set(spec) - (passthrough | {"record_id", "scope_kind", "scope_ref", "attention_tier"}):
        raise ValueError("unsupported_retrieval_fixture_shape")
    record_id = spec.get("record_id")
    if not _safe_token(record_id):
        raise ValueError("invalid_retrieval_fixture_identity")
    for key in ("scope", "source_evidence", "admission", "ttl", "retention", "staleness", "attention", "safety"):
        if key in spec and not isinstance(spec[key], Mapping):
            raise ValueError("unsupported_retrieval_fixture_shape")
    if "tags" in spec and (not isinstance(spec["tags"], (list, tuple)) or any(not isinstance(tag, str) for tag in spec["tags"])):
        raise ValueError("unsupported_retrieval_fixture_shape")
    approved_at = str(spec.get("approved_at", "") or "")
    record: dict[str, object] = {
        "schema_version": _EVAL_RECORD_SCHEMA_VERSION,
        "record_id": record_id,
        "record_type": "fact",
        "summary": "",
        "scope": {"kind": str(spec.get("scope_kind", "project") or "project"), "ref": str(spec.get("scope_ref", "default") or "default")},
        "tags": [],
        "source": "retrieval-fixture",
        "source_ref": record_id,
        "review_status": spec.get("admission_state", "approved"),
        "approved_by": "retrieval-fixture",
        "approved_at": approved_at,
        "created_at": approved_at,
        "updated_at": approved_at,
        "ttl": {},
        "staleness": {},
        "retention": {"class": str(spec.get("retention_class", "") or "standard")},
        "attention": {"tier": str(spec.get("attention_tier", "") or "normal")},
        "redaction_policy": "metadata_only",
        "claim_boundary": "Bounded retrieval-fixture record; not a captured or operator-reviewed memory.",
    }
    record.update({key: value for key, value in spec.items() if key in passthrough})
    return record


def _eval_case(case: Mapping[str, object], *, pack_builder: Callable[..., Mapping[str, object]]) -> dict[str, object]:
    """Recompute one bounded case's outcome from the real production recall path.

    Each case's ``records`` fixtures are materialised into an isolated,
    throwaway OMJ store and recalled through the caller-supplied
    ``pack_builder`` (normally ``build_project_memory_recall_pack``) -- never
    through the case's own caller-supplied ``passed`` flag.
    """
    for key in ("lens", "budget", "flags", "expected", "configuration", "retrieval_configuration"):
        if key in case and not isinstance(case[key], Mapping):
            raise ValueError("unsupported_retrieval_fixture_shape")
    case_id = str(case.get("case_id", ""))
    query = str(case.get("query", "") or "")
    lens = case.get("lens") if isinstance(case.get("lens"), Mapping) else {}
    budget = case.get("budget") if isinstance(case.get("budget"), Mapping) else {}
    flags = case.get("flags") if isinstance(case.get("flags"), Mapping) else {}
    expected = case.get("expected") if isinstance(case.get("expected"), Mapping) else {}
    configured: dict[str, object] = {}
    configurable = ("executor_target", "session_id", "scope_kind", "scope_ref", "limit", "include_stale", "filters", "source", "time", "time_range", "since", "until", "as_of", "clock")
    for container in (case, lens, budget, flags, case.get("configuration"), case.get("retrieval_configuration")):
        if not isinstance(container, Mapping):
            continue
        for key in configurable:
            if key in container:
                configured[key] = container[key]
    if "scope_kind" not in configured and "scope_kind" in lens:
        configured["scope_kind"] = lens["scope_kind"]
    if "scope_ref" not in configured and "scope_ref" in lens:
        configured["scope_ref"] = lens["scope_ref"]
    try:
        limit = int(configured.get("limit", 6) or 6)
    except (TypeError, ValueError):
        limit = 6
    configured["limit"] = limit
    try:
        parameters = inspect.signature(pack_builder).parameters
        accepts_kwargs = any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in parameters.values())
        accepted = None if accepts_kwargs else set(parameters)
    except (TypeError, ValueError):
        accepted = None

    def invoke(local_paths: OmjPaths, local_limit: int) -> Mapping[str, object]:
        kwargs = {key: value for key, value in configured.items() if accepted is None or key in accepted}
        kwargs["limit"] = local_limit
        return pack_builder(local_paths, query, **kwargs)

    with TemporaryDirectory() as tmp:
        eval_paths = resolve_paths(Path(tmp) / ".omj", Path(tmp) / ".hermes")
        records_dir = eval_paths.memory_dir / "records"
        records_dir.mkdir(parents=True, exist_ok=True)
        records = case.get("records", [])
        if not isinstance(records, (list, tuple)):
            raise ValueError("unsupported_retrieval_fixture_shape")
        seen: set[str] = set()
        for spec in records:
            record = _eval_record(spec)
            if record["record_id"] in seen:
                raise ValueError("duplicate_retrieval_fixture_identity")
            seen.add(record["record_id"])
            (records_dir / f"{record['record_id']}.json").write_text(json.dumps(record), encoding="utf-8")
        bounded = invoke(eval_paths, limit)
        unbounded = invoke(eval_paths, _EVAL_UNBOUNDED_LIMIT)
    included_order = [str(row.get("record_id", "")) for row in bounded.get("included_records", [])]
    excluded_reasons = {str(row.get("record_id", "")): str(row.get("reason", "")) for row in bounded.get("excluded_records", [])}
    truncated = len(unbounded.get("included_records", [])) > len(bounded.get("included_records", []))
    actual = {"included_order": included_order, "excluded_reasons": excluded_reasons, "truncated": truncated}
    expected_order = list(expected.get("included_order", []))
    expected_reasons = dict(expected.get("excluded_reasons", {}))
    expected_truncated = bool(expected.get("truncated", False))
    passed = included_order == expected_order and excluded_reasons == expected_reasons and truncated == expected_truncated
    return {"case_id": case_id, "query": query, "retrieval_configuration": dict(configured), "expected": dict(expected), "actual": actual, "passed": passed}


def run_memory_retrieval_evaluation(*, target_revision: str = "", cases: Sequence[Mapping[str, object]] = (), pack_builder: object = None, live_arms: object = None) -> dict[str, object]:
    """Build a deterministic local report, recomputing outcomes from bounded
    production recall whenever a callable ``pack_builder`` is supplied (never
    from a case's own caller-supplied ``passed`` flag).

    ``live_arms`` is accepted for API compatibility but deliberately not
    invoked: this wrapper is executor-neutral and cannot observe a provider,
    host delivery, or model execution.
    """
    if not isinstance(cases, Sequence) or isinstance(cases, (str, bytes, bytearray)):
        raise ValueError("unsupported_retrieval_fixture_shape")
    rows: list[dict[str, object]] = []
    for case in cases:
        if not isinstance(case, Mapping):
            raise ValueError("unsupported_retrieval_fixture_shape")
        if callable(pack_builder):
            rows.append(_eval_case(case, pack_builder=pack_builder))
        else:
            rows.append(dict(case))
    report = make_retrieval_report(cases=rows, target_revision=target_revision)
    report["passed"] = all(bool(row.get("passed", False)) for row in rows) if rows else True
    return report
