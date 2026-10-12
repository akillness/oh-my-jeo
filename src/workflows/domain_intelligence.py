from __future__ import annotations

"""Reviewed domain intelligence, kept separate from generic project memory.

The store is intentionally local and metadata-only.  It records bounded
vocabulary candidates, operator review decisions, and the resulting profile
revision chain; it never stores prompts, transcripts, credentials, or runtime
authority.
"""

import hashlib
import json
import math
import os
import re
import threading
import unicodedata
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from ..system.local_store import atomic_write_json, ensure_dir, read_json_object_result, utc_now
from ..system.paths import OmjPaths

DOMAIN_CANDIDATE_SCHEMA_VERSION = "domain_intelligence_candidate/v1"
DOMAIN_PROFILE_SCHEMA_VERSION = "domain_intelligence_profile/v1"
DOMAIN_REVIEW_RECORD_SCHEMA_VERSION = "domain_intelligence_review_record/v1"
DOMAIN_STATUS_SCHEMA_VERSION = "domain_intelligence_status/v1"
DOMAIN_REVIEW_QUEUE_SCHEMA_VERSION = "domain_intelligence_review_queue/v1"
DOMAIN_LIST_SCHEMA_VERSION = "domain_intelligence_profile_listing/v1"

ALLOWED_SCOPE_KINDS = {"user", "organization", "project"}
ALLOWED_SOURCE_CLASSES = {"operator_supplied", "wrapper_supplied", "omj_local"}
ALLOWED_REVIEW_REASON_CODES = {
    "duplicate",
    "incorrect_scope",
    "insufficient_evidence",
    "operator_request",
    "scope_error",
    "superseded",
}
DEFAULT_REVIEW_REASON_CODE = "operator_request"
CLAIM_BOUNDARY = (
    "Domain intelligence is reviewed OMJ-local prepared context only. It is a future "
    "routing_prior_not_override and is not routing behavior, execution, review, CI, "
    "merge, authentication, or Hermes internal-memory evidence."
)
REDUCTION_POLICY = "bounded_reviewed_vocabulary_only_no_raw_prompts_or_transcripts"

_SAFE_REF = re.compile(r"^[A-Za-z0-9_.:-]{1,120}$")
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9_.:-]{0,79}$")
_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_SAFE_CANDIDATE_ID = re.compile(r"^dicand_[a-f0-9]{16}$")
_SAFE_PROFILE_ID = re.compile(r"^dprof_[a-f0-9]{24}$")
_FORBIDDEN_KEYS = {
    "message", "messages", "prompt", "raw", "text", "body", "content",
    "transcript", "conversation", "hidden_reasoning", "log", "logs",
}
_PROMPTISH_WORDS = {"message", "prompt", "raw", "text", "body", "content", "transcript", "hidden_reasoning"}
_ROLE_MARKER = re.compile(r"^\s*(?:user|assistant|system|developer|human|agent)\s*:", re.I | re.M)
_SECRET_ASSIGNMENT = re.compile(
    r"(?<![a-z0-9])(?:api[-_ ]?key|password|passwd|pwd|token|access[-_ ]?token|"
    r"authorization|auth[-_ ]?header|bearer|secret)[^\S\r\n]*[:=][^\S\r\n]*\S+",
    re.I,
)
_SECRET_SHAPE = re.compile(
    r"(?:gh[pousr]_[a-z0-9]{20,}|github_pat_[a-z0-9_]{20,}|"
    r"(?:AKIA|ASIA)[A-Z0-9]{16}|sk-(?:proj-)?[a-z0-9_-]{20,}|"
    r"xox[baprs]-[a-z0-9-]{20,}|eyJ[a-z0-9_-]+\.eyJ[a-z0-9_-]+\.[a-z0-9_-]+)",
    re.I,
)
_INJECTION_PATTERN = re.compile(
    r"\b(?:ignore|disregard|override|forget)\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|above|system|developer)\b|"
    r"\b(?:do\s+not|don't)\s+follow\s+(?:these\s+)?instructions\b",
    re.I,
)
_RAW_LOG_PATTERN = re.compile(r"traceback \(most recent call last\)|(?:^|\n)(?:stdout|stderr)|\[error\]|raw log|raw transcript|full transcript|chat transcript", re.I)
_BIDI_CATEGORIES = {"Cc", "Cf", "Cs", "Zl", "Zp"}

CANDIDATE_BASE_KEYS = frozenset(
    "schema_version candidate_id status profile_id scope domain_id vocabulary_mappings workflow_hints confidence provenance "
    "base_profile_revision created_at updated_at redaction_policy claim_boundary".split()
)
CANDIDATE_KEYS = {
    "pending_review": CANDIDATE_BASE_KEYS,
    "approved": CANDIDATE_BASE_KEYS | {"reviewed_at", "reviewed_by", "review_id", "revision"},
    "rejected": CANDIDATE_BASE_KEYS | {"reviewed_at", "reviewed_by", "review_id", "rejection_reason_code"},
}
PROFILE_ACTIVE_KEYS = frozenset(
    "schema_version profile_id revision status scope domain_id vocabulary_mappings workflow_hints confidence provenance "
    "base_profile_revision candidate_id approved_by approved_at created_at updated_at redaction_policy claim_boundary payload_digest".split()
)
PROFILE_KEYS = {
    "active": PROFILE_ACTIVE_KEYS,
    "retired": PROFILE_ACTIVE_KEYS | {"retired_at", "retired_by", "retirement_reason_code"},
}
PROFILE_REVIEW_KEYS = frozenset(
    "schema_version review_id candidate_id profile_id revision decision reviewer_claim payload_digest reviewed_at reason_code claim_boundary".split()
)
REJECTED_REVIEW_KEYS = frozenset(
    "schema_version review_id candidate_id profile_id revision decision reviewer_claim reviewed_at reason_code claim_boundary".split()
)

_LOCKS: dict[str, threading.RLock] = {}
_LOCKS_GUARD = threading.Lock()


def _root(paths: OmjPaths) -> Path:
    return paths.memory_dir / "domain-intelligence"


def _dir(paths: OmjPaths, name: str) -> Path:
    root = _root(paths).resolve(strict=False)
    target = (root / name).resolve(strict=False)
    if target.parent != root:
        raise ValueError("unsafe_domain_store_path")
    return target


def _path(paths: OmjPaths, name: str, identifier: str) -> Path:
    if not _SAFE_REF.fullmatch(identifier):
        raise ValueError(f"unsafe_{name}_id")
    directory = _dir(paths, name)
    target = (directory / f"{identifier}.json").resolve(strict=False)
    if target.parent != directory:
        raise ValueError("unsafe_domain_store_path")
    return target


@contextmanager
def _store_lock(paths: OmjPaths) -> Iterator[None]:
    key = str(_root(paths).resolve(strict=False))
    with _LOCKS_GUARD:
        lock = _LOCKS.setdefault(key, threading.RLock())
    with lock:
        ensure_dir(_root(paths))
        yield


def _read(path: Path) -> dict[str, Any] | None:
    if path.is_symlink():
        raise ValueError("escaping_snapshot")
    value, error = read_json_object_result(path)
    if error:
        raise ValueError("corrupt_snapshot")
    return value


def _write(path: Path, value: dict[str, object]) -> None:
    atomic_write_json(path, value)


def _safe_text(value: object, label: str, *, prompt_request: bool = False) -> str:
    if not isinstance(value, str):
        raise ValueError(f"invalid_{label}")
    normalized = unicodedata.normalize("NFKC", value)
    if any(unicodedata.category(ch) in _BIDI_CATEGORIES for ch in value + normalized):
        raise ValueError(f"unsafe_{label}")
    if _ROLE_MARKER.search(normalized) or _SECRET_ASSIGNMENT.search(normalized) or _SECRET_SHAPE.search(normalized) or _INJECTION_PATTERN.search(normalized) or _RAW_LOG_PATTERN.search(normalized):
        raise ValueError(f"unsafe_{label}")
    if prompt_request and re.match(r"^\s*(?:please|kindly)(?:\s+\S+){4,}", normalized, re.I):
        raise ValueError(f"unsafe_{label}")
    return normalized


def _ensure_no_forbidden(value: object) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).strip().lower() in _FORBIDDEN_KEYS:
                raise ValueError("raw_prompt_transcript_fields_forbidden")
            _ensure_no_forbidden(nested)
    elif isinstance(value, list):
        for nested in value:
            _ensure_no_forbidden(nested)
    elif isinstance(value, str):
        _safe_text(value, "payload")


def _normalize_scope(kind: object, ref: object) -> dict[str, object]:
    kind_text = _safe_text(kind, "scope_kind").strip().lower()
    if kind_text not in ALLOWED_SCOPE_KINDS:
        raise ValueError("invalid_scope_kind")
    ref_text = _safe_text(ref, "scope_ref").strip()
    if not _SAFE_REF.fullmatch(ref_text):
        raise ValueError("unsafe_scope_ref")
    return {
        "kind": kind_text,
        "ref": ref_text,
        "ref_authority": "operator_or_wrapper_supplied",
        "identity_claim": "not_authenticated_identity_evidence",
    }


def _normalize_scope_value(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"kind", "ref", "ref_authority", "identity_claim"}:
        raise ValueError("scope_schema_mismatch")
    result = _normalize_scope(value.get("kind"), value.get("ref"))
    if value.get("ref_authority") != result["ref_authority"] or value.get("identity_claim") != result["identity_claim"]:
        raise ValueError("scope_authority_mismatch")
    return result


def _normalize_identifier(value: object, label: str) -> str:
    text = _safe_text(value, label).strip().lower()
    if not _IDENTIFIER.fullmatch(text):
        raise ValueError(f"invalid_{label}")
    return text


def _normalize_mappings(mappings: object) -> list[dict[str, str]]:
    if not isinstance(mappings, list) or not mappings or len(mappings) > 40:
        raise ValueError("invalid_mapping_count")
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for item in mappings:
        if not isinstance(item, tuple) or len(item) != 2:
            raise ValueError("invalid_mapping")
        phrase = _safe_text(item[0], "phrase", prompt_request=True)
        phrase = " ".join(phrase.strip().split())
        canonical = _normalize_identifier(item[1], "canonical_term")
        if phrase.casefold() in _PROMPTISH_WORDS:
            raise ValueError("promptish_phrase")
        if canonical.replace("-", " ").casefold() in _PROMPTISH_WORDS:
            raise ValueError("unsafe_domain_vocabulary")
        if not phrase or len(phrase) > 80 or phrase.casefold() in seen:
            raise ValueError("invalid_phrase" if not phrase or len(phrase) > 80 else "duplicate_phrase")
        if phrase.lstrip().startswith(("{", "[", "<")):
            raise ValueError("promptish_structured_phrase")
        seen.add(phrase.casefold())
        result.append({"phrase": phrase, "canonical": canonical})
    return sorted(result, key=lambda item: (item["phrase"].casefold(), item["canonical"]))


def _normalize_mappings_value(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list):
        raise ValueError("vocabulary_mappings must be a list")
    pairs: list[tuple[str, str]] = []
    for item in value:
        if not isinstance(item, dict) or set(item) != {"phrase", "canonical"}:
            raise ValueError("mapping_schema_mismatch")
        if not isinstance(item.get("phrase"), str) or not isinstance(item.get("canonical"), str):
            raise ValueError("invalid_mapping_value")
        pairs.append((item["phrase"], item["canonical"]))
    return _normalize_mappings(pairs)


def _normalize_hints(value: object) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("workflow_hints must be a list")
    if len(value) > 20:
        raise ValueError("too_many_workflow_hints")
    result: set[str] = set()
    for item in value:
        text = _safe_text(item, "workflow_hint").strip().lower().replace(" ", "-")
        if not _IDENTIFIER.fullmatch(text):
            raise ValueError("invalid_workflow_hint")
        result.add(text)
    return sorted(result)


def _normalize_provenance(source_class: object, source_ref: object, observation_count: object) -> dict[str, object]:
    source = _safe_text(source_class, "source_class").strip().lower()
    if source not in ALLOWED_SOURCE_CLASSES:
        raise ValueError("invalid_source_class")
    ref = _safe_text(source_ref, "source_ref").strip()
    if ref and not _SAFE_REF.fullmatch(ref):
        raise ValueError("unsafe_source_ref")
    if isinstance(observation_count, bool) or not isinstance(observation_count, int) or not 1 <= observation_count <= 10000:
        raise ValueError("invalid_observation_count")
    return {"source_class": source, "source_ref": ref, "observation_count": observation_count, "raw_persisted": False}


def _normalize_provenance_value(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"source_class", "source_ref", "observation_count", "raw_persisted"}:
        raise ValueError("provenance_schema_mismatch")
    if value.get("raw_persisted") is not False:
        raise ValueError("raw_persisted_forbidden")
    return _normalize_provenance(value.get("source_class"), value.get("source_ref"), value.get("observation_count"))


def _normalize_confidence(confidence: object, observation_count: int) -> dict[str, object]:
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError("invalid_confidence_estimate")
    if not math.isfinite(float(confidence)) or not 0 <= float(confidence) <= 1:
        raise ValueError("confidence_out_of_range")
    return {
        "estimate": round(float(confidence), 4),
        "evidence_strength": "bounded_operator_review",
        "observation_count": observation_count,
        "routing_authority": "none",
    }


def _normalize_confidence_value(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"estimate", "evidence_strength", "observation_count", "routing_authority"}:
        raise ValueError("confidence_schema_mismatch")
    count = value.get("observation_count")
    if isinstance(count, bool) or not isinstance(count, int):
        raise ValueError("invalid_confidence_observation_count")
    result = _normalize_confidence(value.get("estimate"), count)
    if value.get("evidence_strength") != "bounded_operator_review" or value.get("routing_authority") != "none":
        raise ValueError("invalid_routing_authority")
    return result


def _normalize_reason(value: object) -> str:
    if value == "":
        return DEFAULT_REVIEW_REASON_CODE
    text = _safe_text(value, "review_reason_code").strip().lower().replace("-", "_")
    if text not in ALLOWED_REVIEW_REASON_CODES:
        raise ValueError("invalid_review_reason_code")
    return text


def _normalize_reviewer(value: object, label: str) -> str:
    text = _safe_text(value, label).strip()
    if not _SAFE_REF.fullmatch(text):
        raise ValueError(f"unsafe_{label}")
    return text


def _validate_timestamp(value: object, label: str) -> str:
    if not isinstance(value, str) or not _TIMESTAMP.fullmatch(value):
        raise ValueError(f"invalid_{label}")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ValueError(f"invalid_{label}") from exc
    return value


def _validate_base_revision(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("invalid_base_profile_revision")
    return value


def validate_candidate_contract(candidate: dict[str, object]) -> str:
    if not isinstance(candidate, dict) or candidate.get("schema_version") != DOMAIN_CANDIDATE_SCHEMA_VERSION:
        raise ValueError("unsupported_candidate_schema")
    status = candidate.get("status")
    if status not in CANDIDATE_KEYS:
        raise ValueError("invalid_candidate_status")
    if set(candidate) != CANDIDATE_KEYS[status]:
        raise ValueError("candidate_schema_mismatch")
    if not isinstance(candidate.get("candidate_id"), str) or not _SAFE_CANDIDATE_ID.fullmatch(candidate["candidate_id"]):
        raise ValueError("unsafe_candidate_id")
    if not isinstance(candidate.get("profile_id"), str) or not _SAFE_PROFILE_ID.fullmatch(candidate["profile_id"]):
        raise ValueError("unsafe_profile_id")
    normalized_scope = _normalize_scope_value(candidate.get("scope"))
    normalized_domain = _normalize_identifier(candidate.get("domain_id"), "domain_id")
    if stable_profile_id(normalized_scope, normalized_domain) != candidate.get("profile_id"):
        raise ValueError("profile_identity_mismatch")
    _normalize_mappings_value(candidate.get("vocabulary_mappings"))
    _normalize_hints(candidate.get("workflow_hints"))
    _normalize_confidence_value(candidate.get("confidence"))
    _normalize_provenance_value(candidate.get("provenance"))
    _validate_base_revision(candidate.get("base_profile_revision"))
    _validate_timestamp(candidate.get("created_at"), "candidate_created_at")
    updated = _validate_timestamp(candidate.get("updated_at"), "candidate_updated_at")
    if candidate["created_at"] > updated:
        raise ValueError("candidate_timestamp_order_invalid")
    if candidate.get("redaction_policy") != REDUCTION_POLICY:
        raise ValueError("invalid_redaction_policy")
    if candidate.get("claim_boundary") != CLAIM_BOUNDARY:
        raise ValueError("invalid_claim_boundary")
    _ensure_no_forbidden(candidate)
    if status == "pending_review":
        if candidate["created_at"] != updated:
            raise ValueError("candidate_timestamp_mismatch")
    else:
        reviewed = _validate_timestamp(candidate.get("reviewed_at"), "candidate_reviewed_at")
        if reviewed != updated:
            raise ValueError("candidate_timestamp_mismatch")
        _normalize_reviewer(candidate.get("reviewed_by"), "reviewer_claim")
        if status == "approved":
            if not isinstance(candidate.get("revision"), int) or isinstance(candidate.get("revision"), bool) or candidate["revision"] < 1:
                raise ValueError("invalid_revision")
        else:
            _normalize_reason(candidate.get("rejection_reason_code"))
    return status


def validate_profile_contract(profile: dict[str, object]) -> str:
    if not isinstance(profile, dict) or profile.get("schema_version") != DOMAIN_PROFILE_SCHEMA_VERSION:
        raise ValueError("unsupported_profile_schema")
    status = profile.get("status")
    if status not in PROFILE_KEYS:
        raise ValueError("invalid_profile_status")
    if set(profile) != PROFILE_KEYS[status]:
        raise ValueError("profile_schema_mismatch")
    if not isinstance(profile.get("profile_id"), str) or not _SAFE_PROFILE_ID.fullmatch(profile["profile_id"]):
        raise ValueError("unsafe_profile_id")
    revision = profile.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise ValueError("invalid_revision")
    normalized_scope = _normalize_scope_value(profile.get("scope"))
    normalized_domain = _normalize_identifier(profile.get("domain_id"), "domain_id")
    if stable_profile_id(normalized_scope, normalized_domain) != profile.get("profile_id"):
        raise ValueError("profile_identity_mismatch")
    _normalize_mappings_value(profile.get("vocabulary_mappings"))
    _normalize_hints(profile.get("workflow_hints"))
    _normalize_confidence_value(profile.get("confidence"))
    _normalize_provenance_value(profile.get("provenance"))
    _validate_base_revision(profile.get("base_profile_revision"))
    _validate_timestamp(profile.get("created_at"), "profile_created_at")
    approved = _validate_timestamp(profile.get("approved_at"), "profile_approved_at")
    updated = _validate_timestamp(profile.get("updated_at"), "profile_updated_at")
    if profile["created_at"] > approved or approved > updated:
        raise ValueError("profile_timestamp_order_invalid")
    if status == "active" and approved != updated:
        raise ValueError("profile_timestamp_mismatch")
    if status == "retired":
        retired = _validate_timestamp(profile.get("retired_at"), "profile_retired_at")
        if retired != updated:
            raise ValueError("profile_timestamp_mismatch")
        _normalize_reviewer(profile.get("retired_by"), "retired_by")
        _normalize_reason(profile.get("retirement_reason_code"))
    _normalize_reviewer(profile.get("approved_by"), "approved_by")
    if not isinstance(profile.get("candidate_id"), str) or not _SAFE_CANDIDATE_ID.fullmatch(profile["candidate_id"]):
        raise ValueError("unsafe_candidate_id")
    if not isinstance(profile.get("payload_digest"), str) or not re.fullmatch(r"[a-f0-9]{64}", profile["payload_digest"]):
        raise ValueError("invalid_payload_digest")
    if profile["payload_digest"] != canonical_profile_digest(profile):
        raise ValueError("payload_digest_mismatch")
    if profile.get("redaction_policy") != REDUCTION_POLICY or profile.get("claim_boundary") != CLAIM_BOUNDARY:
        raise ValueError("invalid_profile_boundary")
    _ensure_no_forbidden(profile)
    return status


def validate_review_contract(review: dict[str, object], expected_keys: frozenset[str]) -> None:
    if not isinstance(review, dict) or review.get("schema_version") != DOMAIN_REVIEW_RECORD_SCHEMA_VERSION:
        raise ValueError("unsupported_review_schema")
    if set(review) != expected_keys:
        raise ValueError("review_schema_mismatch")
    if review.get("claim_boundary") != CLAIM_BOUNDARY:
        raise ValueError("invalid_claim_boundary")
    _validate_timestamp(review.get("reviewed_at"), "reviewed_at")


def stable_profile_id(scope: dict[str, object], domain_id: str) -> str:
    normalized_scope = _normalize_scope_value(scope)
    normalized_domain = _normalize_identifier(domain_id, "domain_id")
    payload = {"scope": {"kind": normalized_scope["kind"], "ref": normalized_scope["ref"], "ref_authority": "operator_or_wrapper_supplied"}, "domain_id": normalized_domain}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "dprof_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _digest_payload(profile: dict[str, object]) -> dict[str, object]:
    revision = profile.get("revision")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise ValueError("invalid_revision")
    return {
        "schema_version": DOMAIN_PROFILE_SCHEMA_VERSION,
        "profile_id": profile.get("profile_id"),
        "revision": revision,
        "status": profile.get("status"),
        "scope": _normalize_scope_value(profile.get("scope")),
        "domain_id": _normalize_identifier(profile.get("domain_id"), "domain_id"),
        "vocabulary_mappings": _normalize_mappings_value(profile.get("vocabulary_mappings")),
        "workflow_hints": _normalize_hints(profile.get("workflow_hints")),
        "confidence": _normalize_confidence_value(profile.get("confidence")),
        "provenance": _normalize_provenance_value(profile.get("provenance")),
        "base_profile_revision": _validate_base_revision(profile.get("base_profile_revision")),
    }


def canonical_profile_digest(profile: dict[str, object]) -> str:
    _ensure_no_forbidden(profile)
    raw = json.dumps(_digest_payload(profile), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _current_profile(paths: OmjPaths, profile_id: str) -> dict[str, object] | None:
    profile = _read(_path(paths, "profiles", profile_id))
    if profile is None:
        return None
    validate_profile_contract(profile)
    review = _read(_path(paths, "reviews", f"direview_{profile_id}_r{profile['revision']}"))
    if review is None:
        raise ValueError("matching_review_required")
    validate_review_contract(review, PROFILE_REVIEW_KEYS)
    expected_decision = "retired" if profile.get("status") == "retired" else "approved"
    if (
        review.get("payload_digest") != profile.get("payload_digest")
        or review.get("profile_id") != profile_id
        or review.get("revision") != profile.get("revision")
        or review.get("decision") != expected_decision
        or review.get("review_id") != f"direview_{profile_id}_r{profile['revision']}"
        or review.get("reviewer_claim") != (profile.get("retired_by") if expected_decision == "retired" else profile.get("approved_by"))
        or review.get("reviewed_at") != (profile.get("retired_at") if expected_decision == "retired" else profile.get("approved_at"))
        or review.get("reason_code") != (profile.get("retirement_reason_code") if expected_decision == "retired" else DEFAULT_REVIEW_REASON_CODE)
    ):
        raise ValueError("matching_review_required")
    return profile


def _candidate(paths: OmjPaths, candidate_id: str) -> dict[str, object]:
    if not _SAFE_CANDIDATE_ID.fullmatch(candidate_id):
        raise ValueError("unsafe_candidate_id")
    candidate = _read(_path(paths, "candidates", candidate_id))
    if candidate is None:
        raise FileNotFoundError(candidate_id)
    validate_candidate_contract(candidate)
    if candidate.get("candidate_id") != candidate_id:
        raise ValueError("candidate_identity_mismatch")
    return candidate
def capture_domain_candidate(
    paths: OmjPaths,
    *,
    scope_kind: str,
    scope_ref: str,
    domain_id: str,
    mappings: list[tuple[str, str]],
    workflow_hints: list[str] | None = None,
    source_class: str = "operator_supplied",
    source_ref: str = "",
    observation_count: int = 1,
    confidence: float = 0.5,
) -> dict[str, object]:
    _ensure_no_forbidden(locals())
    scope = _normalize_scope(scope_kind, scope_ref)
    normalized_domain = _normalize_identifier(domain_id, "domain_id")
    normalized_mappings = _normalize_mappings(mappings)
    normalized_hints = _normalize_hints(workflow_hints or [])
    provenance = _normalize_provenance(source_class, source_ref, observation_count)
    confidence_metadata = _normalize_confidence(confidence, observation_count)
    profile_id = stable_profile_id(scope, normalized_domain)
    now = utc_now()
    candidate_id = "dicand_" + os.urandom(8).hex()
    with _store_lock(paths):
        current = _current_profile(paths, profile_id)
        base_revision = int(current["revision"]) if current else 0
        candidate = {
            "schema_version": DOMAIN_CANDIDATE_SCHEMA_VERSION,
            "candidate_id": candidate_id,
            "status": "pending_review",
            "profile_id": profile_id,
            "scope": scope,
            "domain_id": normalized_domain,
            "vocabulary_mappings": normalized_mappings,
            "workflow_hints": normalized_hints,
            "confidence": confidence_metadata,
            "provenance": provenance,
            "base_profile_revision": base_revision,
            "created_at": now,
            "updated_at": now,
            "redaction_policy": REDUCTION_POLICY,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        validate_candidate_contract(candidate)
        _write(_path(paths, "candidates", candidate_id), candidate)
    return {"schema_version": "domain_intelligence_capture/v1", "candidate": candidate, "claim_boundary": CLAIM_BOUNDARY}


def approve_domain_candidate(paths: OmjPaths, candidate_id: str, *, approved_by: str = "operator") -> dict[str, object]:
    reviewer = _normalize_reviewer(approved_by, "reviewer_claim")
    with _store_lock(paths):
        candidate = _candidate(paths, candidate_id)
        if candidate["status"] != "pending_review":
            raise ValueError("candidate_not_pending")
        current = _current_profile(paths, str(candidate["profile_id"]))
        current_revision = int(current["revision"]) if current else 0
        if int(candidate["base_profile_revision"]) != current_revision:
            raise ValueError("stale_candidate")
        now = utc_now()
        revision = current_revision + 1
        profile = {
            "schema_version": DOMAIN_PROFILE_SCHEMA_VERSION,
            "profile_id": candidate["profile_id"],
            "revision": revision,
            "status": "active",
            "scope": dict(candidate["scope"]),
            "domain_id": candidate["domain_id"],
            "vocabulary_mappings": list(candidate["vocabulary_mappings"]),
            "workflow_hints": list(candidate["workflow_hints"]),
            "confidence": dict(candidate["confidence"]),
            "provenance": dict(candidate["provenance"]),
            "base_profile_revision": candidate["base_profile_revision"],
            "candidate_id": candidate["candidate_id"],
            "approved_by": reviewer,
            "approved_at": now,
            "created_at": current["created_at"] if current else now,
            "updated_at": now,
            "redaction_policy": REDUCTION_POLICY,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        profile["payload_digest"] = canonical_profile_digest(profile)
        review = {
            "schema_version": DOMAIN_REVIEW_RECORD_SCHEMA_VERSION,
            "review_id": f"direview_{profile['profile_id']}_r{revision}",
            "candidate_id": candidate["candidate_id"],
            "profile_id": profile["profile_id"],
            "revision": revision,
            "decision": "approved",
            "reviewer_claim": reviewer,
            "payload_digest": profile["payload_digest"],
            "reviewed_at": now,
            "reason_code": DEFAULT_REVIEW_REASON_CODE,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        validate_profile_contract(profile)
        validate_review_contract(review, PROFILE_REVIEW_KEYS)
        if current is not None:
            history_path = _path(paths, "history", f"{current['profile_id']}_r{current['revision']}")
            existing = _read(history_path)
            if existing is not None and existing != current:
                raise ValueError("corrupt_snapshot")
            _write(history_path, current)
        approved_candidate = {
            **candidate,
            "status": "approved",
            "reviewed_at": now,
            "reviewed_by": reviewer,
            "review_id": review["review_id"],
            "revision": revision,
            "updated_at": now,
        }
        validate_candidate_contract(approved_candidate)
        _write(_path(paths, "reviews", str(review["review_id"])), review)
        _write(_path(paths, "profiles", str(profile["profile_id"])), profile)
        _write(_path(paths, "candidates", candidate_id), approved_candidate)
    return {"schema_version": DOMAIN_REVIEW_RECORD_SCHEMA_VERSION, "decision": "approved", "candidate": approved_candidate, "profile": profile, "review": review, "claim_boundary": CLAIM_BOUNDARY}


def reject_domain_candidate(
    paths: OmjPaths,
    candidate_id: str,
    *,
    rejected_by: str = "operator",
    reason_code: str = "operator_request"
) -> dict[str, object]:
    reviewer = _normalize_reviewer(rejected_by, "reviewer_claim")
    reason = _normalize_reason(reason_code)
    with _store_lock(paths):
        candidate = _candidate(paths, candidate_id)
        if candidate["status"] != "pending_review":
            raise ValueError("candidate_not_pending")
        current = _current_profile(paths, str(candidate["profile_id"]))
        if current is not None and current.get("candidate_id") == candidate_id:
            raise ValueError("candidate_already_approved")
        now = utc_now()
        review = {
            "schema_version": DOMAIN_REVIEW_RECORD_SCHEMA_VERSION,
            "review_id": f"direview_{candidate_id}",
            "candidate_id": candidate_id,
            "profile_id": candidate["profile_id"],
            "revision": None,
            "decision": "rejected",
            "reviewer_claim": reviewer,
            "reviewed_at": now,
            "reason_code": reason,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        rejected = {
            **candidate,
            "status": "rejected",
            "reviewed_at": now,
            "reviewed_by": reviewer,
            "review_id": review["review_id"],
            "rejection_reason_code": reason,
            "updated_at": now,
        }
        validate_review_contract(review, REJECTED_REVIEW_KEYS)
        validate_candidate_contract(rejected)
        _write(_path(paths, "reviews", str(review["review_id"])), review)
        _write(_path(paths, "candidates", candidate_id), rejected)
    return {"schema_version": DOMAIN_REVIEW_RECORD_SCHEMA_VERSION, "decision": "rejected", "candidate": rejected, "review": review, "claim_boundary": CLAIM_BOUNDARY}


def retire_domain_profile(
    paths: OmjPaths,
    *,
    profile_id: str,
    scope_kind: str,
    scope_ref: str,
    revision: int,
    retired_by: str = "operator",
    reason_code: str = "operator_request"
) -> dict[str, object]:
    if not _SAFE_PROFILE_ID.fullmatch(profile_id):
        raise ValueError("unsafe_profile_id")
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise ValueError("invalid_revision")
    reviewer = _normalize_reviewer(retired_by, "retired_by")
    reason = _normalize_reason(reason_code)
    scope = _normalize_scope(scope_kind, scope_ref)
    with _store_lock(paths):
        current = _current_profile(paths, profile_id)
        if current is None:
            raise FileNotFoundError(profile_id)
        if current.get("scope") != scope:
            raise ValueError("scope_mismatch")
        expected_id = stable_profile_id(scope, str(current["domain_id"]))
        if expected_id != profile_id:
            raise ValueError("scope_mismatch")
        if current.get("status") != "active":
            raise ValueError("already_retired")
        if current.get("revision") != revision:
            raise ValueError("stale_profile")
        now = utc_now()
        target = {
            **current,
            "revision": revision + 1,
            "status": "retired",
            "base_profile_revision": revision,
            "updated_at": now,
            "retired_at": now,
            "retired_by": reviewer,
            "retirement_reason_code": reason,
        }
        target["payload_digest"] = canonical_profile_digest(target)
        review = {
            "schema_version": DOMAIN_REVIEW_RECORD_SCHEMA_VERSION,
            "review_id": f"direview_{profile_id}_r{target['revision']}",
            "candidate_id": "",
            "profile_id": profile_id,
            "revision": target["revision"],
            "decision": "retired",
            "reviewer_claim": reviewer,
            "payload_digest": target["payload_digest"],
            "reviewed_at": now,
            "reason_code": reason,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        validate_profile_contract(target)
        validate_review_contract(review, PROFILE_REVIEW_KEYS)
        history_path = _path(paths, "history", f"{profile_id}_r{revision}")
        existing = _read(history_path)
        if existing is not None and existing != current:
            raise ValueError("corrupt_snapshot")
        _write(history_path, current)
        _write(_path(paths, "reviews", str(review["review_id"])), review)
        _write(_path(paths, "profiles", profile_id), target)
    return {"schema_version": DOMAIN_REVIEW_RECORD_SCHEMA_VERSION, "decision": "retired", "profile": target, "review": review, "claim_boundary": CLAIM_BOUNDARY}


def build_domain_review(paths: OmjPaths) -> dict[str, object]:
    cards: list[dict[str, object]] = []
    diagnostics: list[dict[str, str]] = []
    directory = _dir(paths, "candidates")
    if directory.exists():
        for path in sorted(directory.glob("*.json")):
            try:
                candidate = _read(path)
                if candidate is None or candidate.get("status") != "pending_review":
                    continue
                validate_candidate_contract(candidate)
                cards.append({
                    "schema_version": "domain_intelligence_review_card/v1",
                    "candidate_id": candidate["candidate_id"],
                    "status": candidate["status"],
                    "profile_id": candidate["profile_id"],
                    "scope": candidate["scope"],
                    "domain_id": candidate["domain_id"],
                    "mapping_count": len(candidate["vocabulary_mappings"]),
                    "workflow_hints": candidate["workflow_hints"],
                    "confidence": candidate["confidence"],
                    "provenance": candidate["provenance"],
                    "base_profile_revision": candidate["base_profile_revision"],
                    "claim_boundary": CLAIM_BOUNDARY,
                })
            except (OSError, ValueError) as exc:
                diagnostics.append({"path": str(path), "reason": str(exc)})
    return {"schema_version": DOMAIN_REVIEW_QUEUE_SCHEMA_VERSION, "cards": cards, "card_count": len(cards), "pending_count": len(cards), "diagnostics": diagnostics, "claim_boundary": CLAIM_BOUNDARY}


def list_domain_profiles(
    paths: OmjPaths,
    *,
    scope_kind: str | None = None,
    scope_ref: str | None = None,
    domain_id: str | None = None,
) -> dict[str, object]:
    profiles: list[dict[str, object]] = []
    diagnostics: list[dict[str, str]] = []
    expected_scope = _normalize_scope(scope_kind, scope_ref) if scope_kind is not None or scope_ref is not None else None
    expected_domain = _normalize_identifier(domain_id, "domain_id") if domain_id is not None else None
    directory = _dir(paths, "profiles")
    if directory.exists():
        for path in sorted(directory.glob("*.json")):
            try:
                profile = _read(path)
                if profile is None:
                    continue
                validate_profile_contract(profile)
                if profile["status"] != "active":
                    continue
                if expected_scope is not None and profile["scope"] != expected_scope:
                    continue
                if expected_domain is not None and profile["domain_id"] != expected_domain:
                    continue
                profiles.append(profile)
            except (OSError, ValueError) as exc:
                diagnostics.append({"path": str(path), "reason": str(exc)})
    return {"schema_version": DOMAIN_LIST_SCHEMA_VERSION, "profiles": profiles, "counts": {"profiles": len(profiles)}, "diagnostics": diagnostics, "claim_boundary": CLAIM_BOUNDARY}


def build_domain_status(paths: OmjPaths) -> dict[str, object]:
    listing = list_domain_profiles(paths)
    review = build_domain_review(paths)
    candidates = 0
    rejected = 0
    approved = 0
    directory = _dir(paths, "candidates")
    if directory.exists():
        for path in directory.glob("*.json"):
            try:
                candidate = _read(path)
                if candidate is None:
                    continue
                validate_candidate_contract(candidate)
                candidates += 1
                if candidate["status"] == "rejected":
                    rejected += 1
                elif candidate["status"] == "approved":
                    approved += 1
            except (OSError, ValueError):
                pass
    return {
        "schema_version": DOMAIN_STATUS_SCHEMA_VERSION,
        "counts": {
            "candidates": candidates,
            "pending_review": int(review["pending_count"]),
            "approved_candidates": approved,
            "rejected_candidates": rejected,
            "active_profiles": len(listing["profiles"]),
            "malformed_artifacts": len(review["diagnostics"]) + len(listing["diagnostics"]),
        },
        "redaction_policy": REDUCTION_POLICY,
        "claim_boundary": CLAIM_BOUNDARY,
    }


__all__ = [
    "ALLOWED_REVIEW_REASON_CODES", "ALLOWED_SCOPE_KINDS", "ALLOWED_SOURCE_CLASSES", "CLAIM_BOUNDARY",
    "DEFAULT_REVIEW_REASON_CODE", "DOMAIN_CANDIDATE_SCHEMA_VERSION", "DOMAIN_LIST_SCHEMA_VERSION",
    "DOMAIN_PROFILE_SCHEMA_VERSION", "DOMAIN_REVIEW_QUEUE_SCHEMA_VERSION", "DOMAIN_REVIEW_RECORD_SCHEMA_VERSION",
    "DOMAIN_STATUS_SCHEMA_VERSION", "REDUCTION_POLICY", "approve_domain_candidate", "build_domain_review",
    "build_domain_status", "canonical_profile_digest", "capture_domain_candidate", "list_domain_profiles",
    "reject_domain_candidate", "retire_domain_profile", "stable_profile_id", "validate_candidate_contract",
    "validate_profile_contract", "validate_review_contract",
]
