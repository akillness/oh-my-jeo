from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import threading
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from ..local_store import (
    atomic_write_json,
    read_json_object_result,
    read_jsonl_objects,
    utc_now,
)

PAPER_LEARNING_CARD_SCHEMA_VERSION = "paper_learning_card/v1"
PAPER_LEARNING_LEVELS = ("very_easy", "moderate", "expert", "choose")
PAPER_LEARNING_SOURCE_STATES = (
    "metadata_only",
    "excerpt_text_observed",
    "file_text_extraction_observed",
    "full_text_observed",
    "unknown_or_missing",
)
PAPER_LEARNING_COVERAGE_POLICY = "coverage_preserving_not_lossy_summary"
DEFAULT_PAPER_SECTIONS = (
    "Abstract",
    "Introduction",
    "Related work / prior context",
    "Method",
    "Data or experimental setup",
    "Results",
    "Figures, tables, and equations",
    "Limitations",
    "Implications",
    "Reproducibility notes",
)
PAPER_LEARNING_NOT_OBSERVED = (
    "full_pdf_extraction",
    "figure_ocr",
    "external_citation_check",
    "math_proof_validation",
    "code_or_benchmark_reproduction",
    "peer_review_or_claim_correctness",
)
PAPER_LEARNING_ACTIONS = (
    "choose_explanation_level",
    "show_paper_source_requirements",
    "record_paper_metadata",
    "record_paper_excerpt_observed",
    "record_file_text_extraction_observed",
    "show_paper_learning",
    "continue_next_section",
    "revise_explanation_level",
    "show_coverage_ledger",
    "record_user_review",
    "show_status",
)
PAPER_LEARNING_LEVEL_CONTRACT = {
    "very_easy": {
        "label": "Very easy",
        "style": "plain language, prerequisite concepts inline, glossary, analogies, and slow build-up",
        "coverage_rule": "Do not drop sections, claims, equations, figures, or limitations; simplify scaffolding only.",
    },
    "moderate": {
        "label": "Moderate",
        "style": "practitioner or graduate-friendly language with technical terms retained and explained",
        "coverage_rule": "Preserve all substantive content while balancing intuition, mechanism, and implications.",
    },
    "expert": {
        "label": "Expert",
        "style": "technical terminology, assumptions, equations, method critique, result critique, and reproducibility notes",
        "coverage_rule": "Preserve section coverage and distinguish paper claims from independently verified truth.",
    },
    "choose": {
        "label": "Choose level",
        "style": "ask the user to choose very_easy, moderate, or expert before drafting the explanation",
        "coverage_rule": "Prepare the scope and source boundary; do not guess the user's desired explanation level.",
    },
}


def normalize_paper_learning_level(level: str | None) -> str:
    """Normalize user-facing level aliases without changing explanation content."""
    if not level:
        return "choose"
    normalized = level.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "easy": "very_easy",
        "very_easy": "very_easy",
        "beginner": "very_easy",
        "plain": "very_easy",
        "쉽게": "very_easy",
        "아주_쉽게": "very_easy",
        "moderate": "moderate",
        "medium": "moderate",
        "normal": "moderate",
        "intermediate": "moderate",
        "적당한": "moderate",
        "expert": "expert",
        "advanced": "expert",
        "technical": "expert",
        "전문가급": "expert",
        "choose": "choose",
        "ask": "choose",
    }
    return aliases.get(normalized, "choose")


def normalize_paper_source_state(
    state: str | None,
    *,
    observed_sections: Iterable[str] = (),
    missing_sections: Iterable[str] = (),
    evidence_ref: str = "",
) -> dict[str, object]:
    normalized = (state or "unknown_or_missing").strip().lower()
    if normalized not in PAPER_LEARNING_SOURCE_STATES:
        normalized = "unknown_or_missing"
    observed = _clean_unique(observed_sections)
    missing = _clean_unique(missing_sections)
    if normalized == "full_text_observed" and missing:
        normalized = "file_text_extraction_observed"
    if normalized in {"metadata_only", "unknown_or_missing"} and observed:
        normalized = "excerpt_text_observed"
    return {
        "state": normalized,
        "observed_sections": observed,
        "missing_sections": missing,
        "evidence_ref": evidence_ref.strip(),
    }


def build_coverage_ledger(
    *,
    observed_sections: Iterable[str] = (),
    missing_sections: Iterable[str] = (),
    sections: Iterable[str] = DEFAULT_PAPER_SECTIONS,
) -> list[dict[str, str]]:
    observed_keys = {_key(section) for section in observed_sections}
    missing_keys = {_key(section) for section in missing_sections}
    ledger: list[dict[str, str]] = []
    for section in _clean_unique(sections) or list(DEFAULT_PAPER_SECTIONS):
        key = _key(section)
        if key in observed_keys:
            status = "observed"
            explanation_status = "pending"
        elif key in missing_keys:
            status = "missing"
            explanation_status = "pending"
        else:
            status = "prepared"
            explanation_status = "pending"
        ledger.append(
            {
                "paper_section": section,
                "status": status,
                "explanation_status": explanation_status,
            }
        )
    return ledger


def build_paper_learning_card(
    *,
    title: str = "unknown or supplied",
    authors: Iterable[str] = (),
    source_ref: str = "",
    level: str | None = "choose",
    source_state: str | None = "unknown_or_missing",
    observed_sections: Iterable[str] = (),
    missing_sections: Iterable[str] = (),
    evidence_ref: str = "",
    sections: Iterable[str] = DEFAULT_PAPER_SECTIONS,
    output_language: str = "source",
) -> dict[str, object]:
    observed = _clean_unique(observed_sections)
    missing = _clean_unique(missing_sections)
    level_id = normalize_paper_learning_level(level)
    card = {
        "schema_version": PAPER_LEARNING_CARD_SCHEMA_VERSION,
        "card_id": _card_id(title, source_ref, level_id),
        "paper_identity": {
            "title": title.strip() or "unknown or supplied",
            "authors": _clean_unique(authors),
            "source_ref": source_ref.strip(),
        },
        "source_state": normalize_paper_source_state(
            source_state,
            observed_sections=observed,
            missing_sections=missing,
            evidence_ref=evidence_ref,
        ),
        "level": level_id,
        "level_contract": PAPER_LEARNING_LEVEL_CONTRACT[level_id],
        "output_language": output_language.strip() or "source",
        "coverage_policy": PAPER_LEARNING_COVERAGE_POLICY,
        "coverage_ledger": build_coverage_ledger(
            observed_sections=observed,
            missing_sections=missing,
            sections=sections,
        ),
        "chunking_policy": {
            "mode": "section_by_section",
            "part_index": 1,
            "part_count_when_known": None,
            "chunk_stop_rule": "End each chunk with covered / next / missing; say done only when the ledger is complete.",
        },
        "explanation_outline": (
            "What problem the paper studies",
            "What the paper claims",
            "Prior work / gap",
            "Method",
            "Data or experimental setup",
            "Results",
            "Figures, tables, and equations",
            "Limitations",
            "Implications",
            "Reproducibility notes",
            "Glossary / concept ladder",
        ),
        "not_observed": list(PAPER_LEARNING_NOT_OBSERVED),
        "available_actions": list(PAPER_LEARNING_ACTIONS),
        "next_actions": list(PAPER_LEARNING_ACTIONS[:8]),
    }
    return card


def validate_paper_learning_card(card: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if card.get("schema_version") != PAPER_LEARNING_CARD_SCHEMA_VERSION:
        errors.append("schema_version must be paper_learning_card/v1")
    if card.get("level") not in PAPER_LEARNING_LEVELS:
        errors.append("level must be one of very_easy, moderate, expert, choose")
    source_state = card.get("source_state")
    if not isinstance(source_state, dict):
        errors.append("source_state must be an object")
    elif source_state.get("state") not in PAPER_LEARNING_SOURCE_STATES:
        errors.append("source_state.state is unsupported")
    if card.get("coverage_policy") != PAPER_LEARNING_COVERAGE_POLICY:
        errors.append("coverage_policy must preserve coverage")
    ledger = card.get("coverage_ledger")
    if not isinstance(ledger, list) or not ledger:
        errors.append("coverage_ledger must be a non-empty list")
    if not set(PAPER_LEARNING_NOT_OBSERVED).issubset(set(card.get("not_observed", []))):
        errors.append(
            "not_observed must include paper extraction and validation boundaries"
        )
    return errors


def _clean_unique(values: Iterable[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        key = _key(text)
        if text and key not in seen:
            cleaned.append(text)
            seen.add(key)
    return cleaned


def _key(value: str) -> str:
    return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())


def _card_id(title: str, source_ref: str, level: str) -> str:
    seed = "|".join((title.strip().lower(), source_ref.strip().lower(), level))
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"paper-learning-{digest}"


PAPER_LEARNING_RECORD_SCHEMA_VERSION = "omj_paper_learning_record/v1"
PAPER_LEARNING_PROGRESS_SCHEMA_VERSION = "omj_paper_learning_progress/v1"
PAPER_LEARNING_INDEX_SCHEMA_VERSION = "omj_paper_learning_index/v1"
PAPER_LEARNING_READING_STATUSES = (
    "not_started",
    "in_progress",
    "waiting_for_missing_sections",
    "complete",
)
PAPER_SOURCE_KINDS = ("none", "file", "url", "reference")
PAPER_LEARNING_NOTE_CHAR_LIMIT = 500
PAPER_LEARNING_CARD_FILENAME = "card.json"
PAPER_LEARNING_LEDGER_FILENAME = "ledger.jsonl"
PAPER_LEARNING_STORE_REASON_CODES = (
    "record_not_found",
    "record_corrupt",
    "source_unreadable",
)
PAPER_SOURCE_HASH_BYTE_BUDGET = 256 * 1024 * 1024
_PAPER_STORE_LOCK = threading.RLock()


class PaperLearningStoreError(ValueError):
    def __init__(self, reason_code: str, detail: str, *, paper_id: str = "") -> None:
        if reason_code not in PAPER_LEARNING_STORE_REASON_CODES:
            raise ValueError(
                f"unsupported paper learning store reason_code: {reason_code}"
            )
        super().__init__(detail)
        self.reason_code, self.detail, self.paper_id = reason_code, detail, paper_id


_SLUG_RE = re.compile(r"[^a-z0-9]+")
_PAPER_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,159}$")


def _store_dir(paths: Any) -> Path:
    value = getattr(paths, "paper_learning_dir", None)
    return Path(value) if value is not None else Path(paths.omj_home) / "paper-learning"


def _index_path(paths: Any) -> Path:
    value = getattr(paths, "paper_learning_index_path", None)
    return Path(value) if value is not None else _store_dir(paths) / "index.json"


_PAPER_LEARNING_CACHE_WARNING_LIMIT = 200


def _report_index_cache_warning(paths: Any, exc: OSError) -> None:
    detail = str(exc).strip() or type(exc).__name__
    if len(detail) > _PAPER_LEARNING_CACHE_WARNING_LIMIT:
        detail = detail[: _PAPER_LEARNING_CACHE_WARNING_LIMIT - 1] + "…"
    warnings.warn(
        f"paper-learning index cache update failed at {_index_path(paths)}: {detail}; "
        "the authoritative paper record remains committed",
        RuntimeWarning,
        stacklevel=3,
    )


def _valid_paper_id(value: str) -> bool:
    return (
        bool(_PAPER_ID_RE.fullmatch(str(value)))
        and "/" not in str(value)
        and "\\" not in str(value)
        and ".." not in str(value)
    )


def _paper_dir(paths: Any, paper_id: str) -> Path:
    if not _valid_paper_id(paper_id):
        raise ValueError(
            "paper_id must contain only letters, digits, and hyphens, and must not contain path separators"
        )
    root = _store_dir(paths)
    if root.is_symlink():
        raise PaperLearningStoreError(
            "record_corrupt",
            "refusing symlinked paper-learning root",
            paper_id=paper_id,
        )
    path = root / paper_id
    try:
        if path.resolve().parent != root.resolve():
            raise ValueError("paper_id escapes paper-learning storage")
    except OSError as exc:
        raise PaperLearningStoreError(
            "record_corrupt", str(exc), paper_id=paper_id
        ) from exc
    return path


def paper_learning_card_path(paths: Any, paper_id: str) -> Path:
    return _paper_dir(paths, paper_id) / PAPER_LEARNING_CARD_FILENAME


def paper_learning_ledger_path(paths: Any, paper_id: str) -> Path:
    return _paper_dir(paths, paper_id) / PAPER_LEARNING_LEDGER_FILENAME


def _stamp(value: datetime | str | None) -> str:
    if value is None:
        value = datetime.now(timezone.utc)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return _slugify(value)[:32] or datetime.now(timezone.utc).strftime(
                "%Y%m%dT%H%M%SZ"
            )
        return _stamp(parsed)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _slugify(value: str) -> str:
    return (_SLUG_RE.sub("-", str(value).lower()).strip("-") or "paper")[:48].strip("-")


def new_paper_id(title: str, now: datetime | str | None = None) -> str:
    return f"{_stamp(now)}-{_slugify(title)}-{secrets.token_hex(3)}"


def describe_paper_source(source_ref: str) -> dict[str, Any]:
    ref = str(source_ref).strip()
    if not ref:
        return {
            "ref": "",
            "kind": "none",
            "path": "",
            "exists": False,
            "sha256": "",
            "size_bytes": None,
        }
    if ref.lower().startswith(("http://", "https://")):
        return {
            "ref": ref,
            "kind": "url",
            "path": "",
            "exists": False,
            "sha256": "",
            "size_bytes": None,
        }
    candidate = Path(ref).expanduser()
    if not candidate.is_file():
        return {
            "ref": ref,
            "kind": "reference",
            "path": "",
            "exists": False,
            "sha256": "",
            "size_bytes": None,
        }
    try:
        size = candidate.stat().st_size
        resolved = str(candidate.resolve())
        if size > PAPER_SOURCE_HASH_BYTE_BUDGET:
            return {
                "ref": ref,
                "kind": "file",
                "path": resolved,
                "exists": True,
                "sha256": "",
                "size_bytes": size,
                "hash_skipped": "over_budget",
                "hash_budget_bytes": PAPER_SOURCE_HASH_BYTE_BUDGET,
            }
        digest = hashlib.sha256()
        seen = 0
        with candidate.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
                seen += len(chunk)
    except OSError as exc:
        raise PaperLearningStoreError("source_unreadable", f"{ref}: {exc}") from exc
    if seen != size:
        raise PaperLearningStoreError(
            "source_unreadable", f"{ref}: file changed while hashed"
        )
    return {
        "ref": ref,
        "kind": "file",
        "path": resolved,
        "exists": True,
        "sha256": digest.hexdigest(),
        "size_bytes": size,
        "hash_skipped": "",
        "hash_budget_bytes": PAPER_SOURCE_HASH_BYTE_BUDGET,
    }


def _reading_state(
    card: dict[str, Any],
    *,
    progress_count: int,
    next_section: str | None,
    last_note: str,
) -> dict[str, Any]:
    ledger = card["coverage_ledger"]
    covered = [
        item["paper_section"]
        for item in ledger
        if item["explanation_status"] == "explained"
    ]
    missing = [item["paper_section"] for item in ledger if item["status"] == "missing"]
    pending = [
        item["paper_section"]
        for item in ledger
        if item["explanation_status"] == "pending" and item["status"] != "missing"
    ]
    if next_section is None:
        next_section = pending[0] if pending else ""
    status = (
        "complete"
        if len(covered) == len(ledger)
        else "not_started"
        if progress_count == 0
        else "waiting_for_missing_sections"
        if not pending
        else "in_progress"
    )
    return {
        "status": status,
        "covered": covered,
        "next": next_section,
        "missing": missing,
        "explained_count": len(covered),
        "section_count": len(ledger),
        "last_note": last_note,
    }


def build_paper_learning_record(
    *,
    title: str,
    source_ref: str = "",
    authors: Iterable[str] = (),
    level: str | None = "choose",
    source_state: str | None = "metadata_only",
    sections: Iterable[str] | None = None,
    observed_sections: Iterable[str] = (),
    missing_sections: Iterable[str] = (),
    evidence_ref: str = "",
    output_language: str = "source",
    paper_id: str | None = None,
    created_at: str | None = None,
    created_at_ns: int | None = None,
) -> dict[str, Any]:
    clean_title = str(title).strip()
    if not clean_title:
        raise ValueError("title is required")
    section_names = (
        list(DEFAULT_PAPER_SECTIONS)
        if sections is None
        else [str(name) for name in sections]
    )
    if not section_names or any(not name.strip() for name in section_names):
        raise ValueError("section must name a non-empty section")
    created = created_at or utc_now()
    card = build_paper_learning_card(
        title=clean_title,
        authors=authors,
        source_ref=source_ref,
        level=level,
        source_state=source_state,
        observed_sections=observed_sections,
        missing_sections=missing_sections,
        evidence_ref=evidence_ref,
        sections=section_names,
        output_language=output_language,
    )
    record = {
        "schema_version": PAPER_LEARNING_RECORD_SCHEMA_VERSION,
        "paper_id": paper_id or new_paper_id(clean_title, created),
        "card": card,
        "source": describe_paper_source(source_ref),
        "reading": _reading_state(
            card, progress_count=0, next_section=None, last_note=""
        ),
        "progress_count": 0,
        "created_at": created,
        "created_at_ns": time.time_ns()
        if created_at_ns is None
        else int(created_at_ns),
        "updated_at": created,
    }
    errors = validate_paper_learning_record(record)
    if errors:
        raise ValueError("; ".join(errors))
    return record


def validate_paper_learning_record(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be an object"]
    if record.get("schema_version") != PAPER_LEARNING_RECORD_SCHEMA_VERSION:
        errors.append(f"schema_version must be {PAPER_LEARNING_RECORD_SCHEMA_VERSION}")
    raw_id = str(record.get("paper_id", ""))
    if not raw_id.strip():
        errors.append("paper_id is required")
    elif not _valid_paper_id(raw_id):
        errors.append(
            "paper_id must contain only letters, digits, and hyphens, and must not contain path separators"
        )
    card = record.get("card")
    if not isinstance(card, dict):
        errors.append("card must be an object")
    else:
        errors.extend(f"card: {error}" for error in validate_paper_learning_card(card))
    source = record.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    elif source.get("kind") not in PAPER_SOURCE_KINDS:
        errors.append("source.kind is unsupported")
    reading = record.get("reading")
    if not isinstance(reading, dict):
        errors.append("reading must be an object")
    elif reading.get("status") not in PAPER_LEARNING_READING_STATUSES:
        errors.append("reading.status is unsupported")
    progress_count = record.get("progress_count")
    if (
        not isinstance(progress_count, int)
        or isinstance(progress_count, bool)
        or progress_count < 0
    ):
        errors.append("progress_count must be a non-negative integer")
    created_ns = record.get("created_at_ns")
    if (
        not isinstance(created_ns, int)
        or isinstance(created_ns, bool)
        or created_ns < 0
    ):
        errors.append("created_at_ns must be a non-negative integer")
    return errors


def _deep_copy(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _deep_copy(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_deep_copy(item) for item in value]
    return value


def _resolve_sections(
    ledger: list[dict[str, str]], names: Iterable[str], *, flag: str
) -> list[str]:
    by_key = {_key(item["paper_section"]): item["paper_section"] for item in ledger}
    resolved: list[str] = []
    for name in names:
        key = _key(str(name))
        if not key:
            continue
        if key not in by_key:
            raise ValueError(
                f"{flag} {name!r} is not a section of this paper's coverage ledger"
            )
        if by_key[key] not in resolved:
            resolved.append(by_key[key])
    return resolved


def apply_paper_progress(
    record: dict[str, Any],
    *,
    covered: Iterable[str] = (),
    next_section: str | None = None,
    missing: Iterable[str] = (),
    observed: Iterable[str] = (),
    note: str = "",
    source_state: str | None = None,
    evidence_ref: str | None = None,
    recorded_at: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    errors = validate_paper_learning_record(record)
    if errors:
        raise PaperLearningStoreError(
            "record_corrupt",
            "; ".join(errors),
            paper_id=str(record.get("paper_id", "")),
        )
    card = record["card"]
    ledger = card["coverage_ledger"]
    covered_names = _resolve_sections(ledger, covered, flag="covered")
    missing_names = _resolve_sections(ledger, missing, flag="missing")
    observed_names = _resolve_sections(ledger, observed, flag="observed")
    overlap = [name for name in covered_names + observed_names if name in missing_names]
    if overlap:
        raise ValueError("a section cannot be both covered or observed and missing")
    clean_note = " ".join(str(note).split())
    if len(clean_note) > PAPER_LEARNING_NOTE_CHAR_LIMIT:
        raise ValueError(
            f"note must be at most {PAPER_LEARNING_NOTE_CHAR_LIMIT} characters"
        )
    if source_state is not None and source_state not in PAPER_LEARNING_SOURCE_STATES:
        raise ValueError("source_state is unsupported")
    if (
        not covered_names
        and not missing_names
        and not observed_names
        and next_section is None
        and not clean_note
        and source_state is None
        and evidence_ref is None
    ):
        raise ValueError("nothing to record")
    previous_state = card["source_state"]
    effective_evidence = (
        evidence_ref
        if evidence_ref is not None
        else str(previous_state.get("evidence_ref", ""))
    )
    if (observed_names or source_state is not None) and not effective_evidence.strip():
        raise ValueError("observed sections and source state need evidence_ref")
    updated = _deep_copy(record)
    card = updated["card"]
    ledger = card["coverage_ledger"]
    for item in ledger:
        if item["paper_section"] in missing_names:
            item["status"], item["explanation_status"] = "missing", "pending"
        elif item["paper_section"] in observed_names:
            item["status"] = "observed"
    if any(
        item["paper_section"] in covered_names and item["status"] == "missing"
        for item in ledger
    ):
        raise ValueError("cannot cover a section the ledger records as missing")
    for item in ledger:
        if item["paper_section"] in covered_names:
            item["explanation_status"] = "explained"
    resolved_next = (
        None
        if next_section is None
        else _resolve_sections(ledger, [next_section], flag="next")[0]
    )
    observed_now = [
        item["paper_section"] for item in ledger if item["status"] == "observed"
    ]
    missing_now = [
        item["paper_section"] for item in ledger if item["status"] == "missing"
    ]
    card["source_state"] = normalize_paper_source_state(
        source_state if source_state is not None else previous_state["state"],
        observed_sections=observed_now,
        missing_sections=missing_now,
        evidence_ref=effective_evidence,
    )
    progress_count = int(record["progress_count"]) + 1
    stamp = recorded_at or utc_now()
    card["chunking_policy"]["part_index"] = progress_count + 1
    updated["reading"] = _reading_state(
        card,
        progress_count=progress_count,
        next_section=resolved_next,
        last_note=clean_note or str(record["reading"].get("last_note", "")),
    )
    updated["progress_count"], updated["updated_at"] = progress_count, stamp
    entry = {
        "schema_version": PAPER_LEARNING_PROGRESS_SCHEMA_VERSION,
        "paper_id": record["paper_id"],
        "part_index": progress_count,
        "covered": covered_names,
        "observed": observed_names,
        "next": updated["reading"]["next"],
        "missing": missing_names,
        "note": clean_note,
        "source_state": card["source_state"]["state"],
        "evidence_ref": card["source_state"]["evidence_ref"],
        "reading_status": updated["reading"]["status"],
        "recorded_at": stamp,
    }
    return updated, entry


def _append_jsonl(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise PaperLearningStoreError(
            "record_corrupt", "refusing symlinked paper progress ledger"
        )
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(data, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def write_paper_learning_record(paths: Any, record: dict[str, Any]) -> dict[str, Any]:
    with _PAPER_STORE_LOCK:
        errors = validate_paper_learning_record(record)
        if errors:
            raise ValueError("; ".join(errors))
        card_path = paper_learning_card_path(paths, str(record["paper_id"]))
        if card_path.exists():
            raise ValueError(
                f"paper learning record already exists: {record['paper_id']}"
            )
        card_path.parent.mkdir(parents=True, exist_ok=True)
        existing, _ = scan_paper_learning_store(paths)
        newest = max((int(item["created_at_ns"]) for item in existing), default=-1)
        if int(record["created_at_ns"]) <= newest:
            record = dict(record, created_at_ns=newest + 1)
        atomic_write_json(card_path, record, private=True)
        try:
            _write_index_cache(paths)
        except OSError as exc:
            _report_index_cache_warning(paths, exc)
        return record


def _card_path_or_not_found(paths: Any, paper_id: str) -> Path:
    if not _valid_paper_id(paper_id):
        raise PaperLearningStoreError("record_not_found", paper_id, paper_id=paper_id)
    path = paper_learning_card_path(paths, paper_id)
    if not path.exists():
        raise PaperLearningStoreError("record_not_found", paper_id, paper_id=paper_id)
    return path


def _read_valid_record(path: Path, paper_id: str) -> dict[str, Any]:
    record, error = read_json_object_result(path)
    if error or not record:
        raise PaperLearningStoreError(
            "record_corrupt",
            f"{paper_id}: {error or 'empty record'}",
            paper_id=paper_id,
        )
    errors = validate_paper_learning_record(record)
    if errors:
        raise PaperLearningStoreError(
            "record_corrupt", f"{paper_id}: {'; '.join(errors)}", paper_id=paper_id
        )
    return record


def record_paper_progress(
    paths: Any, paper_id: str, **kwargs: Any
) -> tuple[dict[str, Any], dict[str, Any]]:
    with _PAPER_STORE_LOCK:
        path = _card_path_or_not_found(paths, paper_id)
        record = _read_valid_record(path, paper_id)
        updated, entry = apply_paper_progress(record, **kwargs)
        _append_jsonl(paper_learning_ledger_path(paths, paper_id), entry)
        try:
            atomic_write_json(path, updated, private=True)
        except OSError:
            # The append-only event is durable; retry the denormalized card once so
            # transient replacement failures do not strand a committed revision.
            atomic_write_json(path, updated, private=True)
        try:
            _write_index_cache(paths)
        except OSError as exc:
            _report_index_cache_warning(paths, exc)
        return updated, entry


def _unreadable(
    paper_id: str, card_path: Path, reason_code: str, detail: str
) -> dict[str, str]:
    return {
        "paper_id": paper_id,
        "path_name": card_path.name,
        "reason_code": reason_code,
        "detail": detail,
    }


def scan_paper_learning_store(
    paths: Any,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    records: list[dict[str, Any]] = []
    unreadable: list[dict[str, str]] = []
    root = _store_dir(paths)
    if not root.is_dir():
        return records, unreadable
    for entry in sorted(root.iterdir()):
        if entry.is_symlink() or not entry.is_dir():
            continue
        card_path = entry / PAPER_LEARNING_CARD_FILENAME
        if not card_path.exists():
            unreadable.append(
                _unreadable(
                    entry.name, card_path, "record_corrupt", "missing card.json"
                )
            )
            continue
        record, error = read_json_object_result(card_path)
        if error or not record:
            unreadable.append(
                _unreadable(
                    entry.name, card_path, "record_corrupt", error or "empty record"
                )
            )
            continue
        errors = validate_paper_learning_record(record)
        if errors or str(record.get("paper_id", "")) != entry.name:
            unreadable.append(
                _unreadable(
                    entry.name,
                    card_path,
                    "record_corrupt",
                    "; ".join(errors) or "paper_id does not match directory",
                )
            )
            continue
        records.append(record)
    records.sort(
        key=lambda item: (
            int(item["created_at_ns"]),
            str(item["created_at"]),
            str(item["paper_id"]),
        )
    )
    return records, unreadable


def list_paper_learning_records(
    paths: Any, *, limit: int | None = None
) -> list[dict[str, Any]]:
    records, _ = scan_paper_learning_store(paths)
    if limit is not None:
        records = [] if limit < 1 else records[-limit:]
    return records


def show_paper_learning_record(paths: Any, paper_id: str) -> dict[str, Any]:
    return _read_valid_record(_card_path_or_not_found(paths, paper_id), paper_id)


def read_paper_progress_ledger(
    paths: Any, paper_id: str
) -> tuple[list[dict[str, Any]], list[str]]:
    _card_path_or_not_found(paths, paper_id)
    return read_jsonl_objects(paper_learning_ledger_path(paths, paper_id))


def paper_learning_record_exists(paths: Any, paper_id: str) -> bool:
    return (
        _valid_paper_id(paper_id)
        and paper_learning_card_path(paths, paper_id).is_file()
    )


def summarize_paper_learning_record(record: dict[str, Any]) -> dict[str, Any]:
    card = record.get("card", {})
    identity = card.get("paper_identity", {})
    state = card.get("source_state", {})
    reading = record.get("reading", {})
    return {
        "paper_id": str(record.get("paper_id", "")),
        "title": str(identity.get("title", "")),
        "level": str(card.get("level", "")),
        "source_state": str(state.get("state", "")),
        "reading_status": str(reading.get("status", "")),
        "explained_count": int(reading.get("explained_count", 0) or 0),
        "section_count": int(reading.get("section_count", 0) or 0),
        "next": str(reading.get("next", "")),
        "missing_count": len(
            reading.get("missing", [])
            if isinstance(reading.get("missing"), list)
            else []
        ),
        "progress_count": int(record.get("progress_count", 0) or 0),
        "updated_at": str(record.get("updated_at", "")),
    }


def _write_index_cache(paths: Any) -> None:
    records = list_paper_learning_records(paths)
    root = _store_dir(paths)
    root.mkdir(parents=True, exist_ok=True)
    atomic_write_json(
        _index_path(paths),
        {
            "schema_version": PAPER_LEARNING_INDEX_SCHEMA_VERSION,
            "updated_at": utc_now(),
            "authority": "cache_only",
            "papers": [summarize_paper_learning_record(record) for record in records],
        },
        private=True,
    )


def validate_paper_learning_store(paths: Any) -> dict[str, Any]:
    errors: list[str] = []
    records, unreadable = scan_paper_learning_store(paths)
    errors.extend(
        f"{item['paper_id']}: {item['reason_code']}: {item['detail']}"
        for item in unreadable
    )
    for record in records:
        entries, ledger_errors = read_jsonl_objects(
            paper_learning_ledger_path(paths, str(record["paper_id"]))
        )
        errors.extend(ledger_errors)
        if len(entries) != record["progress_count"]:
            errors.append(
                f"{record['paper_id']}: progress_count {record['progress_count']} but the ledger holds {len(entries)} entries"
            )
        for index, entry in enumerate(entries, 1):
            if entry.get("schema_version") != PAPER_LEARNING_PROGRESS_SCHEMA_VERSION:
                errors.append(
                    f"{record['paper_id']}: ledger entry {index} has unsupported schema_version"
                )
            if entry.get("paper_id") != record["paper_id"]:
                errors.append(
                    f"{record['paper_id']}: ledger entry {index} names another paper"
                )
    index, index_error = read_json_object_result(_index_path(paths))
    if index_error:
        errors.append(f"paper-learning index cache is unreadable: {index_error}")
    elif index and index.get("schema_version") != PAPER_LEARNING_INDEX_SCHEMA_VERSION:
        errors.append("paper-learning index cache has unsupported schema_version")
    return {
        "schema_version": "omj_paper_learning_validation/v1",
        "ok": not errors,
        "paper_count": len(records),
        "unreadable_count": len(unreadable),
        "unreadable_records": unreadable,
        "errors": errors,
        "index_authority": "cache_only",
    }


def render_paper_learning_record_text(
    record: dict[str, Any], ledger_entries: Iterable[dict[str, Any]] = ()
) -> str:
    card = record["card"]
    identity = card["paper_identity"]
    reading = record["reading"]
    source = record["source"]
    lines = [
        f"Paper: {identity['title']}",
        f"  id: {record['paper_id']}",
        f"  level: {card['level']}",
        f"  source: {source['ref'] or 'not supplied'} ({source['kind']})",
        f"  source state: {card['source_state']['state']}",
        f"  reading: {reading['status']} ({reading['explained_count']}/{reading['section_count']} sections explained, {record['progress_count']} chunk(s) recorded)",
        f"  covered: {', '.join(reading['covered']) or 'none yet'}",
        f"  next: {reading['next'] or 'none'}",
        f"  missing: {', '.join(reading['missing']) or 'none'}",
        "",
        "Coverage ledger:",
    ]
    lines.extend(
        f"  - {item['paper_section']}: {item['status']} / {item['explanation_status']}"
        for item in card["coverage_ledger"]
    )
    entries = list(ledger_entries)
    if entries:
        lines.append("")
        lines.append("Progress ledger:")
        lines.extend(
            f"  part {entry.get('part_index')}: covered {', '.join(entry.get('covered', [])) or '-'}; next {entry.get('next') or '-'}"
            for entry in entries
        )
    lines.extend(("", f"Not observed: {', '.join(card['not_observed'])}"))
    return "\n".join(lines)


def render_paper_learning_list_text(
    summaries: Iterable[dict[str, Any]],
    unreadable: Iterable[dict[str, str]] = (),
    *,
    total_count: int | None = None,
) -> str:
    rows = list(summaries)
    lines = (
        [
            "No paper learning records yet. Start one with: omj paper plan --title <title> --source <path or url>"
        ]
        if not rows
        else ["Paper learning records:"]
    )
    lines.extend(
        f"  {row['paper_id']}  {row['title']}  [{row['reading_status']}, {row['explained_count']}/{row['section_count']} explained, next {row['next'] or '-'}]"
        for row in rows
    )
    broken = list(unreadable)
    if total_count is not None and total_count > len(rows):
        lines.append(f"Showing the latest {len(rows)} of {total_count} records.")
    if broken:
        lines.append(f"Unreadable records ({len(broken)}), not shown above:")
        lines.extend(
            f"  {item['paper_id']}: {item['reason_code']}: {item['detail']}"
            for item in broken
        )
    return "\n".join(lines)
