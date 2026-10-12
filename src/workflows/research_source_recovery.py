"""Offline metadata planner for blocked research-source recovery.

This module only classifies source-acquisition failures and prepares one typed
handoff for a host capability. It never retrieves a page, authenticates,
pays, bypasses access controls, or stores page content.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from urllib.parse import parse_qsl, urlsplit
import re
from typing import Any


RESEARCH_SOURCE_RECOVERY_SCHEMA_VERSION = "research_source_recovery/v1"
RECOVERY_CAPABILITY = "blocked-page-recovery"
RECOVERABLE_FAILURE_CLASSES = ("http_403", "http_429", "paywall", "waf", "bot_wall")
FAILURE_CLASSES = RECOVERABLE_FAILURE_CLASSES + (
    "authentication_required",
    "missing_archive",
    "network_failure",
    "unknown",
)
ROUTES = (RECOVERY_CAPABILITY, "none")
EVIDENCE_CLASSES = ("live_page", "historical_capture", "none")
OUTCOMES = ("recovered", "unresolved_gap")
GAP_REASONS = (
    "authentication_required",
    "unsupported_failure_class",
    "missing_capability",
    "budget_exhausted",
    "recovery_failed",
)
MAX_RECOVERY_ATTEMPTS = 1
RESEARCH_SOURCE_RECOVERY_KEYS = (
    "canonical_url",
    "captured_at",
    "claim_boundary",
    "evidence_class",
    "failure_class",
    "gap_reason",
    "outcome",
    "recovery_attempts",
    "residual_uncertainty",
    "retrieved_at",
    "route",
    "schema_version",
)
HANDOFF_KEYS = (
    "canonical_url",
    "capability",
    "failure_class",
    "freshness_constraint",
    "max_attempts",
    "retrieval_budget_remaining",
    "source_requirement",
)
CLAIM_BOUNDARY = (
    "A research source recovery record states what the host reported for one blocked source. OMJ "
    "performed no retrieval, bypassed no login, payment, or access control, and the record is not "
    "execution, review, CI, or publication evidence."
)
MAX_URL_CHARS = 2048
MAX_LINE_CHARS = 200
_LABEL = "research_source_recovery"

_VOCABULARIES = (
    ("failure_class", FAILURE_CLASSES),
    ("route", ROUTES),
    ("evidence_class", EVIDENCE_CLASSES),
    ("outcome", OUTCOMES),
)
_STRING_FIELDS = (
    "canonical_url",
    "captured_at",
    "evidence_class",
    "failure_class",
    "gap_reason",
    "outcome",
    "residual_uncertainty",
    "retrieved_at",
    "route",
)

# Keep the safety screen local: this recovery contract is deliberately usable
# without importing a runtime or an optional metadata subsystem.
_BODY_SHAPED = re.compile(r"[\r\n\t\f\v\x00]|```")
_COMMON_SECRET_PREFIX = re.compile(
    r"(?:^|[^a-z0-9])(?:sk|pk|rk|xox[a-z]?)[_-][a-z0-9_-]{8,}", re.IGNORECASE
)
_PLATFORM_SECRET_PREFIX = re.compile(
    r"(?:^|[^a-z0-9])(?:gh[oprs]|github_pat|npm|whsec|glpat)[_-][a-z0-9_-]{16,}",
    re.IGNORECASE,
)
_AWS_ACCESS_KEY = re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")
_GOOGLE_API_KEY = re.compile(r"\bAIza[A-Za-z0-9_-]{20,}\b", re.IGNORECASE)
_CREDENTIAL_QUERY_KEYS = frozenset(
    {
        "accesstoken",
        "apikey",
        "authorization",
        "auth",
        "clientsecret",
        "credential",
        "idtoken",
        "oauth",
        "oauthtoken",
        "password",
        "privatekey",
        "refreshtoken",
        "secret",
        "session",
        "sessionid",
        "sessiontoken",
        "token",
    }
)


class ResearchSourceRecoveryError(ValueError):
    """Raised when a recovery plan or record cannot be safely built."""


def plan_source_recovery(
    *,
    canonical_url: str,
    failure_class: str,
    capability_available: bool,
    retrieval_budget_remaining: int,
    recovery_attempts_spent: int = 0,
    source_requirement: str = "",
    freshness_constraint: str = "",
) -> dict[str, Any]:
    """Return exactly one safe next step for one source."""
    url = str(canonical_url or "").strip()
    url_errors = _url_errors(url)
    if url_errors:
        raise ResearchSourceRecoveryError(url_errors[0])
    if not isinstance(capability_available, bool):
        raise ResearchSourceRecoveryError(f"{_LABEL} capability_available must be a boolean")
    if not isinstance(retrieval_budget_remaining, int) or isinstance(retrieval_budget_remaining, bool):
        raise ResearchSourceRecoveryError(f"{_LABEL} retrieval_budget_remaining must be an integer")
    if not isinstance(recovery_attempts_spent, int) or isinstance(recovery_attempts_spent, bool) or recovery_attempts_spent < 0:
        raise ResearchSourceRecoveryError(
            f"{_LABEL} recovery_attempts_spent must be a non-negative integer"
        )
    if not failure_class:
        return {"action": "cite_direct", "handoff": None, "record": None}
    if failure_class not in FAILURE_CLASSES:
        raise ResearchSourceRecoveryError(
            f"{_LABEL} failure_class must be one of {', '.join(FAILURE_CLASSES)}"
        )
    if recovery_attempts_spent >= MAX_RECOVERY_ATTEMPTS:
        return {"action": "already_attempted", "handoff": None, "record": None}
    reason = _gap_reason_before_handoff(
        failure_class, capability_available, retrieval_budget_remaining
    )
    if reason:
        record = build_research_source_recovery(
            canonical_url=url,
            failure_class=failure_class,
            outcome="unresolved_gap",
            gap_reason=reason,
            residual_uncertainty=f"no recovery attempted: {reason}",
        )
        return {"action": "unresolved_gap", "handoff": None, "record": record}
    handoff = {
        "capability": RECOVERY_CAPABILITY,
        "canonical_url": url,
        "failure_class": failure_class,
        "source_requirement": str(source_requirement or "").strip(),
        "freshness_constraint": str(freshness_constraint or "").strip(),
        "retrieval_budget_remaining": retrieval_budget_remaining,
        "max_attempts": MAX_RECOVERY_ATTEMPTS,
    }
    for key in ("source_requirement", "freshness_constraint"):
        if _line_errors(handoff[key]):
            raise ResearchSourceRecoveryError(
                f"{_LABEL} {key} must be one bounded line without secrets"
            )
    return {"action": "handoff", "handoff": handoff, "record": None}


def build_research_source_recovery(
    *,
    canonical_url: str,
    failure_class: str,
    outcome: str,
    gap_reason: str = "",
    evidence_class: str = "none",
    retrieved_at: str = "",
    captured_at: str = "",
    residual_uncertainty: str = "",
) -> dict[str, Any]:
    """Mint and validate one metadata-only source-recovery record."""
    raw_uncertainty = str(residual_uncertainty or "")
    if _line_errors(raw_uncertainty):
        raise ResearchSourceRecoveryError(
            f"{_LABEL} residual_uncertainty must be one bounded line without secrets"
        )
    attempted = outcome == "recovered" or gap_reason == "recovery_failed"
    record = {
        "schema_version": RESEARCH_SOURCE_RECOVERY_SCHEMA_VERSION,
        "canonical_url": str(canonical_url or "").strip(),
        "failure_class": str(failure_class or ""),
        "route": RECOVERY_CAPABILITY if attempted else "none",
        "recovery_attempts": MAX_RECOVERY_ATTEMPTS if attempted else 0,
        "retrieved_at": str(retrieved_at or "").strip(),
        "evidence_class": str(evidence_class or ""),
        "captured_at": str(captured_at or "").strip(),
        "outcome": str(outcome or ""),
        "gap_reason": str(gap_reason or ""),
        "residual_uncertainty": " ".join(raw_uncertainty.split()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    errors = validate_research_source_recovery(record)
    if errors:
        raise ResearchSourceRecoveryError(errors[0])
    return record


def validate_research_source_recovery(record: Any) -> list[str]:
    """Return every structural and semantic violation in one record."""
    if not isinstance(record, Mapping):
        return [f"{_LABEL} must be an object"]
    errors: list[str] = []
    extra = sorted(set(record) - set(RESEARCH_SOURCE_RECOVERY_KEYS))
    if extra:
        errors.append(f"{_LABEL} has unsupported keys: {extra}")
    missing = sorted(set(RESEARCH_SOURCE_RECOVERY_KEYS) - set(record))
    if missing:
        errors.append(f"{_LABEL} is missing keys: {missing}")
    if record.get("schema_version") != RESEARCH_SOURCE_RECOVERY_SCHEMA_VERSION:
        errors.append(
            f"{_LABEL} schema_version must be {RESEARCH_SOURCE_RECOVERY_SCHEMA_VERSION}"
        )
    for key in _STRING_FIELDS:
        if not isinstance(record.get(key), str):
            errors.append(f"{_LABEL} {key} must be a string")
    attempts = record.get("recovery_attempts")
    if not isinstance(attempts, int) or isinstance(attempts, bool):
        errors.append(f"{_LABEL} recovery_attempts must be an integer")
    if errors:
        return errors
    for key, allowed in _VOCABULARIES:
        if record[key] not in allowed:
            errors.append(f"{_LABEL} {key} must be one of {', '.join(allowed)}")
    if record["claim_boundary"] != CLAIM_BOUNDARY:
        errors.append(f"{_LABEL} claim_boundary must state the record boundary")
    errors.extend(_url_errors(record["canonical_url"]))
    if _line_errors(record["residual_uncertainty"]):
        errors.append(
            f"{_LABEL} residual_uncertainty must be one bounded line without secrets"
        )
    for key in ("retrieved_at", "captured_at"):
        if record[key] and not _is_iso_timestamp(record[key]):
            errors.append(f"{_LABEL} {key} must be an ISO-8601 timestamp")
    if errors:
        return errors
    errors.extend(_attempt_errors(record))
    errors.extend(_outcome_errors(record))
    return errors


def research_source_recovery_errors(records: Sequence[Any]) -> list[str]:
    """Validate one run and reject duplicate attempted recovery handoffs."""
    errors: list[str] = []
    attempted: set[str] = set()
    for index, record in enumerate(records):
        issues = validate_research_source_recovery(record)
        errors.extend(f"record {index}: {issue}" for issue in issues)
        if issues or record["recovery_attempts"] == 0:
            continue
        if record["canonical_url"] in attempted:
            errors.append(
                f"record {index}: {_LABEL} retries {record['canonical_url']}; "
                f"a source gets at most {MAX_RECOVERY_ATTEMPTS} recovery handoff"
            )
        attempted.add(record["canonical_url"])
    return errors


def _gap_reason_before_handoff(
    failure_class: str, capability_available: bool, budget: int
) -> str:
    if failure_class == "authentication_required":
        return "authentication_required"
    if failure_class not in RECOVERABLE_FAILURE_CLASSES:
        return "unsupported_failure_class"
    if not capability_available:
        return "missing_capability"
    if budget <= 0:
        return "budget_exhausted"
    return ""


def _attempt_errors(record: Mapping[str, Any]) -> list[str]:
    attempts = record["recovery_attempts"]
    if attempts < 0 or attempts > MAX_RECOVERY_ATTEMPTS:
        return [
            f"{_LABEL} recovery_attempts must be 0 or {MAX_RECOVERY_ATTEMPTS}; "
            "a source is never retried in a loop"
        ]
    if (attempts == 0) != (record["route"] == "none"):
        return [
            f"{_LABEL} route {record['route']} disagrees with recovery_attempts {attempts}"
        ]
    if attempts and record["failure_class"] not in RECOVERABLE_FAILURE_CLASSES:
        return [
            f"{_LABEL} failure_class {record['failure_class']} is never handed to "
            f"{RECOVERY_CAPABILITY}"
        ]
    return []


def _outcome_errors(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    evidence = record["evidence_class"]
    reason = record["gap_reason"]
    if record["outcome"] == "recovered":
        if reason:
            errors.append(f"{_LABEL} a recovered source carries no gap_reason")
        if evidence == "none":
            errors.append(f"{_LABEL} a recovered source names its evidence_class")
        if not record["retrieved_at"]:
            errors.append(f"{_LABEL} a recovered source records when it was retrieved")
        if evidence == "historical_capture" and not record["captured_at"]:
            errors.append(
                f"{_LABEL} a historical capture carries its provider-reported captured_at"
            )
        if evidence == "live_page" and record["captured_at"]:
            errors.append(
                f"{_LABEL} a live page carries no captured_at; a capture is never the live page"
            )
        return errors
    if reason not in GAP_REASONS:
        errors.append(
            f"{_LABEL} an unresolved gap names one gap_reason: {', '.join(GAP_REASONS)}"
        )
    if evidence != "none" or record["captured_at"]:
        errors.append(f"{_LABEL} an unresolved gap carries no evidence; it is never a partial success")
    if not record["residual_uncertainty"]:
        errors.append(f"{_LABEL} an unresolved gap states its residual_uncertainty")
    if errors:
        return errors
    if (reason == "recovery_failed") != (record["recovery_attempts"] == MAX_RECOVERY_ATTEMPTS):
        errors.append(f"{_LABEL} only recovery_failed follows a spent handoff")
    expected = _gap_reason_before_handoff(record["failure_class"], True, 1)
    if expected and reason != expected:
        errors.append(f"{_LABEL} failure_class {record['failure_class']} leaves gap_reason {expected}")
    return errors


def _url_errors(value: str) -> list[str]:
    if not value:
        return [f"{_LABEL} canonical_url is required"]
    if len(value) > MAX_URL_CHARS:
        return [f"{_LABEL} canonical_url exceeds {MAX_URL_CHARS} characters"]
    if not (value.startswith("https://") or value.startswith("http://")):
        return [f"{_LABEL} canonical_url must be an http(s) URL"]
    if any(char.isspace() or ord(char) < 32 for char in value):
        return [f"{_LABEL} canonical_url must not contain whitespace or control characters"]
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
    except ValueError:
        return [f"{_LABEL} canonical_url must be an http(s) URL"]
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or not hostname:
        return [f"{_LABEL} canonical_url must be an http(s) URL"]
    if parsed.username is not None or parsed.password is not None or _is_secret_value_shaped(value):
        return [f"{_LABEL} canonical_url must not carry credentials"]
    for component in (parsed.query, parsed.fragment):
        for key, _ in parse_qsl(component, keep_blank_values=True):
            normalized_key = re.sub(r"[^a-z0-9]", "", key.lower())
            if normalized_key in _CREDENTIAL_QUERY_KEYS:
                return [f"{_LABEL} canonical_url must not carry credentials"]
    return []


def _line_errors(value: str) -> list[str]:
    if _is_body_shaped_metadata_text(value) or _is_secret_value_shaped(value):
        return ["not one bounded line without secrets"]
    return []


def _is_secret_value_shaped(value: str) -> bool:
    return bool(
        _COMMON_SECRET_PREFIX.search(value)
        or _PLATFORM_SECRET_PREFIX.search(value)
        or _AWS_ACCESS_KEY.search(value)
        or _GOOGLE_API_KEY.search(value)
    )


def _is_body_shaped_metadata_text(value: str) -> bool:
    return len(value) > MAX_LINE_CHARS or _BODY_SHAPED.search(value) is not None


def _is_iso_timestamp(value: str) -> bool:
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(text)
    except ValueError:
        return False
    return True
