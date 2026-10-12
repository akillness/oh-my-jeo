"""Metadata-only long-document page/range planning contract."""
from __future__ import annotations

import hashlib
from typing import Any, Iterable

LONG_DOCUMENT_CARD_SCHEMA_VERSION = "long_document_card/v1"
LONG_DOCUMENT_COVERAGE_POLICY = "page_anchored_coverage_not_lossy_summary"
LONG_DOCUMENT_SOURCE_STATES = (
    "metadata_only", "page_count_observed", "range_text_observed", "full_text_observed", "unknown_or_missing",
)
LONG_DOCUMENT_CHUNK_STATES = ("covered", "next", "missing")
LONG_DOCUMENT_DOCUMENT_KINDS = ("contract", "manual", "annual_report", "specification", "book_or_thesis", "transcript_or_minutes", "other")
LONG_DOCUMENT_NOT_OBSERVED = ("page_count", "text_extraction", "scanned_page_ocr", "range_delegation", "hosted_ocr", "cross_range_consistency")
LONG_DOCUMENT_ACTIONS = ("prepare_long_document_reading", "record_page_count_observed", "record_range_text_observed", "show_chunk_ledger", "continue_next_range", "record_scanned_range", "record_range_delegation", "show_status")
HERMES_READ_FILE_CHAR_BUDGET = 100_000
HERMES_READ_FILE_LINE_LIMIT = 2_000
HERMES_DOCUMENT_BYTE_CAP = 50 * 1024 * 1024
HERMES_TUI_ATTACH_PAGE_LIMIT = 25
DEFAULT_CHARS_PER_PAGE = 1_600
DEFAULT_PAGES_PER_RANGE = 60
DELEGATION_RANGE_THRESHOLD = 4
PER_RANGE_BRIEF = (
    "Read pages {pages} only. Return: page-anchored key points, every defined "
    "term or obligation with its page, open questions, and the exact pages you "
    "could not read. Do not summarize pages outside this range."
)


def _is_positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _require_positive(name: str, value: object) -> None:
    if not _is_positive_int(value):
        raise ValueError(f"{name} must be a positive integer")


def pages_per_range_for_budget(char_budget: int = HERMES_READ_FILE_CHAR_BUDGET, chars_per_page: int = DEFAULT_CHARS_PER_PAGE) -> int:
    _require_positive("char_budget", char_budget)
    _require_positive("chars_per_page", chars_per_page)
    return max(1, (char_budget * 96 // 100) // chars_per_page)


def plan_page_ranges(page_count: int, pages_per_range: int = DEFAULT_PAGES_PER_RANGE) -> list[tuple[int, int]]:
    if not _is_positive_int(page_count):
        if page_count == 0:
            return []
        raise ValueError("page_count must be a positive integer")
    _require_positive("pages_per_range", pages_per_range)
    ranges: list[tuple[int, int]] = []
    start = 1
    while start <= page_count:
        end = min(page_count, start + pages_per_range - 1)
        ranges.append((start, end))
        start = end + 1
    return ranges


def parse_page_range(value: str) -> tuple[int, int] | None:
    text = str(value).strip().replace("–", "-")
    if not text:
        return None
    if "-" in text:
        left, _, right = text.partition("-")
        if not (left.strip().isdigit() and right.strip().isdigit()):
            return None
        start, end = int(left), int(right)
    elif text.isdigit():
        start = end = int(text)
    else:
        return None
    if start < 1 or end < start:
        return None
    return start, end


def format_page_range(start: int, end: int) -> str:
    _require_positive("start", start)
    _require_positive("end", end)
    if end < start:
        raise ValueError("end must be >= start")
    return f"{start}" if start == end else f"{start}-{end}"


def _parsed_ranges(values: Iterable[str]) -> list[tuple[int, int]]:
    parsed: list[tuple[int, int]] = []
    for value in values:
        item = parse_page_range(str(value))
        if item is not None and item not in parsed:
            parsed.append(item)
    return sorted(parsed)


def _merged_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _ranges_cover(ranges: list[tuple[int, int]], page_count: int) -> bool:
    merged = _merged_ranges(ranges)
    return bool(merged) and merged[0][0] == 1 and merged[0][1] >= page_count


def build_chunk_ledger(page_count: int, *, pages_per_range: int = DEFAULT_PAGES_PER_RANGE, chars_per_page: int = DEFAULT_CHARS_PER_PAGE, covered_ranges: Iterable[str] = (), scanned_ranges: Iterable[str] = ()) -> list[dict[str, object]]:
    _require_positive("pages_per_range", pages_per_range)
    _require_positive("chars_per_page", chars_per_page)
    if page_count == 0:
        return []
    _require_positive("page_count", page_count)
    covered = _merged_ranges(_parsed_ranges(covered_ranges))
    scanned = _parsed_ranges(scanned_ranges)
    ledger: list[dict[str, object]] = []
    next_assigned = False
    for index, (start, end) in enumerate(plan_page_ranges(page_count, pages_per_range), start=1):
        is_covered = any(c_start <= start and end <= c_end for c_start, c_end in covered)
        if is_covered:
            state = "covered"
        elif not next_assigned:
            state = "next"
            next_assigned = True
        else:
            state = "missing"
        ledger.append({
            "chunk_index": index,
            "pages": format_page_range(start, end),
            "page_start": start,
            "page_end": end,
            "offset": (start - 1) * chars_per_page,
            "chars": (end - start + 1) * chars_per_page,
            "state": state,
            "scanned": any(s_start <= end and start <= s_end for s_start, s_end in scanned),
        })
    return ledger


def normalize_long_document_source_state(state: str | None, *, page_count: int | None = None, covered_ranges: Iterable[str] = (), evidence_ref: str = "") -> dict[str, object]:
    normalized = (state or "unknown_or_missing").strip().lower()
    if normalized not in LONG_DOCUMENT_SOURCE_STATES:
        normalized = "unknown_or_missing"
    pages = page_count if _is_positive_int(page_count) else None
    covered = _merged_ranges(_parsed_ranges(covered_ranges))
    if covered and normalized in {"metadata_only", "page_count_observed", "unknown_or_missing"}:
        normalized = "range_text_observed"
    if normalized == "full_text_observed" and (pages is None or not _ranges_cover(covered, pages)):
        normalized = "range_text_observed"
    if normalized == "range_text_observed" and not covered:
        normalized = "page_count_observed" if pages else "unknown_or_missing"
    if normalized in {"metadata_only", "unknown_or_missing"} and pages:
        normalized = "page_count_observed"
    return {"state": normalized, "page_count": pages, "covered_ranges": [format_page_range(start, end) for start, end in covered], "evidence_ref": str(evidence_ref).strip()}


def build_long_document_card(*, title: str = "unknown or supplied", source_ref: str = "", document_kind: str = "other", page_count: int | None = None, source_state: str | None = "unknown_or_missing", covered_ranges: Iterable[str] = (), scanned_ranges: Iterable[str] = (), reading_goal: str = "", evidence_ref: str = "", char_budget: int = HERMES_READ_FILE_CHAR_BUDGET, chars_per_page: int = DEFAULT_CHARS_PER_PAGE, output_language: str = "source") -> dict[str, object]:
    kind = str(document_kind).strip().lower().replace("-", "_").replace(" ", "_") or "other"
    if kind not in LONG_DOCUMENT_DOCUMENT_KINDS:
        kind = "other"
    if page_count is not None and not _is_positive_int(page_count):
        raise ValueError("page_count must be a positive integer or None")
    pages_per_range = pages_per_range_for_budget(char_budget, chars_per_page)
    pages = page_count or 0
    ledger = build_chunk_ledger(pages, pages_per_range=pages_per_range, chars_per_page=chars_per_page, covered_ranges=covered_ranges, scanned_ranges=scanned_ranges)
    range_count = len(ledger)
    return {
        "schema_version": LONG_DOCUMENT_CARD_SCHEMA_VERSION,
        "card_id": _card_id(title, source_ref),
        "document_identity": {"title": str(title).strip() or "unknown or supplied", "source_ref": str(source_ref).strip(), "document_kind": kind},
        "reading_goal": str(reading_goal).strip(),
        "output_language": str(output_language).strip() or "source",
        "source_state": normalize_long_document_source_state(source_state, page_count=page_count, covered_ranges=covered_ranges, evidence_ref=evidence_ref),
        "coverage_policy": LONG_DOCUMENT_COVERAGE_POLICY,
        "read_budget": {"char_budget_per_call": char_budget, "chars_per_page_estimate": chars_per_page, "pages_per_range": pages_per_range, "estimated_total_chars": pages * chars_per_page, "estimated_read_calls": range_count, "single_read_fits": bool(pages) and pages <= pages_per_range},
        "chunk_ledger": ledger,
        "chunking_policy": {"mode": "page_ranges", "range_count_when_known": range_count or None, "chunk_stop_rule": "End each range with covered / next / missing page anchors; say done only when every range is covered and every scanned range is either read or declined."},
        "delegation_policy": {"mode": "delegate_ranges" if range_count > DELEGATION_RANGE_THRESHOLD else "sequential_ranges", "threshold_ranges": DELEGATION_RANGE_THRESHOLD, "per_range_brief": PER_RANGE_BRIEF, "merge_rule": "Merge per-range notes in page order and keep each claim's page anchor."},
        "scanned_policy": {"per_page_recovery": "pdf_page_image.py --pages <n> then vision_analyze, one page per call", "hosted_ocr": "read_file runs hosted OCR by itself when FIRECRAWL_API_KEY is set (file_tools.hosted_ocr: false turns it off); otherwise not observed", "decline_rule": "Decline scanned ranges the reading goal does not need; a page-by-page scan is a separate approved job, not a side effect."},
        "not_observed": list(LONG_DOCUMENT_NOT_OBSERVED),
        "available_actions": list(LONG_DOCUMENT_ACTIONS),
        "next_actions": list(LONG_DOCUMENT_ACTIONS[:5]),
    }


def validate_long_document_card(card: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(card, dict):
        return ["card must be an object"]
    if card.get("schema_version") != LONG_DOCUMENT_CARD_SCHEMA_VERSION:
        errors.append("schema_version must be long_document_card/v1")
    source_state = card.get("source_state")
    if not isinstance(source_state, dict):
        errors.append("source_state must be an object")
    elif source_state.get("state") not in LONG_DOCUMENT_SOURCE_STATES:
        errors.append("source_state.state is unsupported")
    if card.get("coverage_policy") != LONG_DOCUMENT_COVERAGE_POLICY:
        errors.append("coverage_policy must preserve page-anchored coverage")
    ledger = card.get("chunk_ledger")
    if not isinstance(ledger, list):
        errors.append("chunk_ledger must be a list")
    else:
        for entry in ledger:
            if not isinstance(entry, dict) or entry.get("state") not in LONG_DOCUMENT_CHUNK_STATES:
                errors.append("chunk_ledger entries must carry a covered, next, or missing state")
                break
            if not isinstance(entry.get("pages"), str) or parse_page_range(str(entry["pages"])) is None:
                errors.append("chunk_ledger entries must carry a page anchor")
                break
        if ledger and sum(1 for entry in ledger if isinstance(entry, dict) and entry.get("state") == "next") > 1:
            errors.append("chunk_ledger may name at most one next range")
    if not set(LONG_DOCUMENT_NOT_OBSERVED).issubset(set(card.get("not_observed", []))):
        errors.append("not_observed must include page count, extraction, OCR, and delegation boundaries")
    errors.extend(_coverage_consistency_errors(card))
    return errors


def _coverage_consistency_errors(card: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    source_state = card.get("source_state")
    ledger = card.get("chunk_ledger")
    if not isinstance(source_state, dict) or not isinstance(ledger, list):
        return errors
    state = source_state.get("state")
    page_count = source_state.get("page_count")
    if page_count is not None and not _is_positive_int(page_count):
        errors.append("source_state.page_count must be a positive integer when present")
        page_count = None
    covered = _parsed_ranges(str(value) for value in source_state.get("covered_ranges", []) if isinstance(value, str))
    if page_count is not None and any(end > page_count for _, end in covered):
        errors.append("source_state.covered_ranges must not run past page_count")
    ledger_states = [entry.get("state") for entry in ledger if isinstance(entry, dict)]
    if state == "full_text_observed" and (not ledger_states or any(value != "covered" for value in ledger_states)):
        errors.append("full_text_observed requires every ledger range to be covered")
    if state == "range_text_observed" and not covered:
        errors.append("range_text_observed requires at least one covered range")
    if state in {"metadata_only", "page_count_observed", "unknown_or_missing"} and "covered" in ledger_states:
        errors.append(f"{state} cannot carry covered ledger ranges")
    return errors


def _card_id(title: str, source_ref: str) -> str:
    seed = "|".join((str(title).strip().lower(), str(source_ref).strip().lower()))
    return f"long-document-{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:12]}"
