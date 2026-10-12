"""Deterministic, metadata-only document chunk plans."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import secrets
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

try:  # pragma: no cover - POSIX hosts provide fcntl; fallback keeps imports portable.
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore[assignment]

from .long_document import pages_per_range_for_budget

DOCUMENT_CHUNK_PLAN_SCHEMA_VERSION = "document_chunk_plan/v1"
DEFAULT_BUDGET_CHARS = 100_000
HERMES_READ_LINE_LIMIT = 2_000
DEFAULT_CHARS_PER_PAGE = 1_600
ASSUMED_CHARS_PER_LINE = 80
CHARS_PER_TOKEN = 4
FAN_OUT_RANGE_THRESHOLD = 4
MIN_BUDGET_CHARS = 1_000
MAX_BUDGET_CHARS = 10_000_000
MIN_CHARS_PER_PAGE = 50
MAX_CHARS_PER_PAGE = 100_000
MAX_PAGES = 100_000
MAX_CHARS = 1_000_000_000
MAX_LINES = 100_000_000
MAX_OUTLINE_ENTRIES = 500
MAX_TITLE_CHARS = 200
MAX_SOURCE_CHARS = 1_000
MAX_NOTE_CHARS = 500
MAX_PROGRESS_HISTORY = 4096
MAX_RANGES = 1_000
MAX_HASHED_BYTES = 1024 * 1024 * 1024
_HASH_BLOCK_BYTES = 1024 * 1024
CHUNK_STATES = ("covered", "next", "missing")
RESULT_RANGE_LIMIT_DEFAULT = 10
RESULT_RANGE_LIMIT_MAX = 16
LEDGER_ID_LIST_LIMIT = 64
MAX_PLAUSIBLE_CHARS_PER_LINE = 4_000
DELEGATION_HINT_STATUS = "prepared_not_observed"
DELEGATION_HINT_CLAIM_BOUNDARY = (
    "The delegation hint is a prepared recommendation with a brief template; it is not a dispatch, "
    "not evidence that any child was spawned, and not evidence that any range was read."
)
LEDGER_BINDING_WARNING = (
    "This plan's identity is not bound to the document's content ({basis}): covered marks record the "
    "caller's statements about whatever carried this label or size, and a changed document under the "
    "same identity keeps them. Plan from a local path under the hash cap to bind the ledger to a sha256."
)
PLAN_ID_HEX_CHARS = 12
_PLAN_ID = re.compile(r"\A[0-9a-f]{12}\Z")
_MAX_PLAN_FILE_BYTES = 4 * 1024 * 1024
_SENSITIVE_NAME_PATTERNS = (
    re.compile(r"\A\.env(?:\..*)?\Z"),
    re.compile(r"\Aauth\.json\Z"),
    re.compile(r"\Aid_(?:rsa|dsa|ecdsa|ed25519)(?:\..*)?\Z"),
    re.compile(r"\.(?:pem|key|p12|pfx|keystore|jks)\Z"),
)
_CONTROL_CHARACTERS = {
    code: None for code in (*range(0x00, 0x20), 0x7F, *range(0x80, 0xA0))
}
CLAIM_BOUNDARY = (
    "A document chunk plan is a prepared reading schedule derived from sizes the caller stated. "
    "OMJ performs no parsing, extraction, or OCR; it may read source bytes only to fingerprint "
    "source identity. Every page and character count is caller_supplied, and a covered mark "
    "records that the caller said the range was read, not that OMJ observed the read."
)


class DocumentPlanError(ValueError):
    """The request cannot become a plan, or a stored plan cannot be trusted."""


class DocumentPlanMissing(DocumentPlanError):
    """No plan file exists for this id."""


def strip_control_characters(value: object) -> str:
    return str(value or "").translate(_CONTROL_CHARACTERS).strip()


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _optional_count(args: dict[str, Any], key: str, *, maximum: int) -> int | None:
    value = args.get(key)
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise DocumentPlanError(f"{key} must be a whole number, not a boolean")
    if isinstance(value, float):
        if not value.is_integer():
            raise DocumentPlanError(f"{key} must be a whole number")
        value = int(value)
    if isinstance(value, str) and value.strip().isdigit():
        value = int(value.strip())
    if not isinstance(value, int):
        raise DocumentPlanError(f"{key} must be a whole number")
    if value < 1:
        raise DocumentPlanError(f"{key} must be at least 1")
    if value > maximum:
        raise DocumentPlanError(f"{key} is capped at {maximum}")
    return value


def _bounded_setting(
    args: dict[str, Any], key: str, *, default: int, minimum: int, maximum: int
) -> tuple[int, str]:
    value = _optional_count(args, key, maximum=maximum)
    if value is None:
        return default, "default"
    if value < minimum:
        raise DocumentPlanError(f"{key} must be at least {minimum}")
    return value, "caller_supplied"


def _normalize_outline(raw: object, pages: int | None) -> list[dict[str, Any]]:
    if raw is None or raw == "" or raw == []:
        return []
    if not isinstance(raw, list):
        raise DocumentPlanError("outline must be a list of {title, page} entries")
    if pages is None:
        raise DocumentPlanError(
            "an outline needs pages: outline entries are page anchors"
        )
    if len(raw) > MAX_OUTLINE_ENTRIES:
        raise DocumentPlanError(f"outline is capped at {MAX_OUTLINE_ENTRIES} entries")
    entries: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise DocumentPlanError(
                f"outline[{index}] must be an object with title and page"
            )
        title = strip_control_characters(item.get("title", ""))
        if not title:
            raise DocumentPlanError(f"outline[{index}] needs a non-empty title")
        if len(title) > MAX_TITLE_CHARS:
            raise DocumentPlanError(
                f"outline[{index}] title is capped at {MAX_TITLE_CHARS} characters"
            )
        page = _optional_count(item, "page", maximum=MAX_PAGES)
        if page is None or page > pages:
            raise DocumentPlanError(f"outline[{index}] needs a page within 1..{pages}")
        entries.append({"title": title, "page": page})
    entries.sort(key=lambda entry: (entry["page"], entry["title"]))
    out: list[dict[str, Any]] = []
    for entry in entries:
        if out and out[-1] == entry:
            continue
        out.append(entry)
    return out


def normalize_plan_request(args: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(args, dict):
        raise DocumentPlanError("plan request must be an object")
    raw_source = args.get("source", "")
    if raw_source is not None and not isinstance(raw_source, str):
        raise DocumentPlanError(
            f"source must be a string, not {type(raw_source).__name__}"
        )
    source = strip_control_characters(raw_source)
    if not source:
        raise DocumentPlanError(
            "source is required: a file path or a label naming the document"
        )
    if len(source) > MAX_SOURCE_CHARS:
        raise DocumentPlanError(f"source is capped at {MAX_SOURCE_CHARS} characters")
    pages = _optional_count(args, "pages", maximum=MAX_PAGES)
    chars = _optional_count(args, "chars", maximum=MAX_CHARS)
    lines = _optional_count(args, "lines", maximum=MAX_LINES)
    if pages is None and chars is None:
        raise DocumentPlanError(
            "plan needs pages or chars: state the page count or extracted text length (OMJ never opens the document to measure it)"
        )
    budget_chars, budget_basis = _bounded_setting(
        args,
        "budget_chars",
        default=DEFAULT_BUDGET_CHARS,
        minimum=MIN_BUDGET_CHARS,
        maximum=MAX_BUDGET_CHARS,
    )
    chars_per_page, density_basis = _bounded_setting(
        args,
        "chars_per_page",
        default=DEFAULT_CHARS_PER_PAGE,
        minimum=MIN_CHARS_PER_PAGE,
        maximum=MAX_CHARS_PER_PAGE,
    )
    outline = _normalize_outline(args.get("outline"), pages)
    if lines is not None:
        total_chars = chars if chars is not None else pages * chars_per_page
        if lines > total_chars:
            raise DocumentPlanError(
                f"lines ({lines}) exceed the document's characters ({total_chars}); pass total_lines for the whole extraction"
            )
        if total_chars / lines > MAX_PLAUSIBLE_CHARS_PER_LINE:
            raise DocumentPlanError(
                f"lines ({lines}) is implausible for {total_chars} characters; pass total_lines for the whole extraction"
            )
    return {
        "source": source,
        "pages": pages,
        "chars": chars,
        "lines": lines,
        "outline": outline,
        "budget_chars": budget_chars,
        "chars_per_page": chars_per_page,
        "provenance": {
            "pages": "caller_supplied" if pages is not None else "not_supplied",
            "chars": "caller_supplied" if chars is not None else "not_supplied",
            "lines": "caller_supplied" if lines is not None else "not_supplied",
            "outline": "caller_supplied" if outline else "not_supplied",
            "budget_chars": budget_basis,
            "chars_per_page": density_basis,
        },
    }


def _sensitive_name(name: str) -> bool:
    lowered = name.casefold()
    return any(pattern.search(lowered) for pattern in _SENSITIVE_NAME_PATTERNS)


def fingerprint_source(label: str, path: Path | None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "label": str(label),
        "kind": "label",
        "size_bytes": None,
        "mtime_ns": None,
        "sha256": "",
        "fingerprint_basis": "label",
        "identity_basis": "label",
    }
    if path is None:
        return record
    try:
        if not path.is_file():
            return record
        stat = path.stat()
    except OSError:
        return record
    record.update(
        {
            "kind": "file",
            "path": str(path),
            "size_bytes": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "identity_basis": "size_and_mtime",
        }
    )
    if _sensitive_name(path.name):
        record["fingerprint_basis"] = "refused_sensitive_name"
        return record
    if stat.st_size > MAX_HASHED_BYTES:
        record["fingerprint_basis"] = "size_only_over_hash_cap"
        return record
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            while block := handle.read(_HASH_BLOCK_BYTES):
                digest.update(block)
    except OSError:
        record["fingerprint_basis"] = "size_only_unreadable"
        return record
    record["sha256"] = digest.hexdigest()
    record["fingerprint_basis"] = "sha256"
    record["identity_basis"] = "sha256"
    return record


def _canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def plan_id_for(request: dict[str, Any], fingerprint: dict[str, Any]) -> str:
    identity = {
        "schema_version": DOCUMENT_CHUNK_PLAN_SCHEMA_VERSION,
        "fingerprint": fingerprint.get("sha256") or fingerprint.get("label"),
        "size_bytes": fingerprint.get("size_bytes"),
        "mtime_ns": None if fingerprint.get("sha256") else fingerprint.get("mtime_ns"),
        "pages": request["pages"],
        "chars": request["chars"],
        "lines": request["lines"],
        "outline": request["outline"],
        "budget_chars": request["budget_chars"],
        "chars_per_page": request["chars_per_page"],
    }
    return _canonical_digest(identity)[:PLAN_ID_HEX_CHARS]


def _segments_from_outline(
    pages: int, outline: list[dict[str, Any]]
) -> list[tuple[int, int, tuple[str, ...]]]:
    if not outline:
        return [(1, pages, ())]
    starts: list[int] = []
    titles: dict[int, list[str]] = {}
    for item in outline:
        if item["page"] not in titles:
            starts.append(item["page"])
        titles.setdefault(item["page"], []).append(item["title"])
    segments: list[tuple[int, int, tuple[str, ...]]] = []
    if starts[0] > 1:
        segments.append((1, starts[0] - 1, ()))
    for index, start in enumerate(starts):
        end = starts[index + 1] - 1 if index + 1 < len(starts) else pages
        segments.append((start, max(start, end), tuple(titles[start])))
    return segments


def _page_ranges(
    pages: int, pages_per_chunk: int, outline: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    pieces: list[tuple[int, int, tuple[str, ...]]] = []
    for start, end, titles in _segments_from_outline(pages, outline):
        cursor = start
        while cursor <= end:
            piece_end = min(end, cursor + pages_per_chunk - 1)
            pieces.append((cursor, piece_end, titles))
            cursor = piece_end + 1
    ranges: list[dict[str, Any]] = []
    current: list[tuple[int, int, tuple[str, ...]]] = []
    current_pages = 0
    for piece in pieces:
        piece_pages = piece[1] - piece[0] + 1
        if current and current_pages + piece_pages > pages_per_chunk:
            ranges.append(_page_range(current))
            current, current_pages = [], 0
        current.append(piece)
        current_pages += piece_pages
    if current:
        ranges.append(_page_range(current))
    return ranges


def _page_range(pieces: list[tuple[int, int, tuple[str, ...]]]) -> dict[str, Any]:
    sections: list[str] = []
    for _, _, titles in pieces:
        for title in titles:
            if title not in sections:
                sections.append(title)
    return {"start": pieces[0][0], "end": pieces[-1][1], "sections": sections}


def _read_window(
    char_start: int, char_end: int, total_chars: int, total_lines: int, basis: str
) -> dict[str, Any]:
    offset = 1 + (char_start * total_lines) // total_chars
    end_line = max(offset, math.ceil(char_end * total_lines / total_chars))
    end_line = min(end_line, total_lines)
    offset = min(offset, end_line)
    span = end_line - offset + 1
    return {
        "offset": offset,
        "end_line": end_line,
        "limit": min(HERMES_READ_LINE_LIMIT, span),
        "read_calls_estimated": max(1, math.ceil(span / HERMES_READ_LINE_LIMIT)),
        "basis": basis,
    }


def derive_ranges(
    request: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    pages, chars, lines = request["pages"], request["chars"], request["lines"]
    budget = request["budget_chars"]
    if pages is not None:
        if chars is not None:
            density, density_basis = (
                chars / pages,
                "derived_from_caller_chars_and_pages",
            )
        else:
            density, density_basis = (
                float(request["chars_per_page"]),
                request["provenance"]["chars_per_page"],
            )
        total_chars = chars if chars is not None else pages * request["chars_per_page"]
        if density > budget:
            raise DocumentPlanError(
                "budget_chars must cover at least one estimated page"
            )
        budget_density = max(1, math.ceil(density))
        exact_pages = max(1, int(budget // density))
        pages_per_chunk = (
            pages
            if pages <= exact_pages
            else pages_per_range_for_budget(budget, budget_density)
        )
        page_ranges = _page_ranges(pages, pages_per_chunk, request["outline"])
        if len(page_ranges) > MAX_RANGES:
            raise DocumentPlanError(
                f"the plan would need {len(page_ranges)} ranges, over the cap of {MAX_RANGES}; raise budget_chars"
            )
        spans = [
            (
                round((entry["start"] - 1) * density),
                min(total_chars, round(entry["end"] * density)),
                {"start": entry["start"], "end": entry["end"]},
                entry["sections"],
            )
            for entry in page_ranges
        ]
        unit = "pages"
        if any(end - start > budget for start, end, _page_span, _sections in spans):
            raise DocumentPlanError("derived page range exceeds budget_chars")
    else:
        total_chars, density, density_basis = chars, None, "not_applicable"
        count = math.ceil(chars / budget)
        if count > MAX_RANGES:
            raise DocumentPlanError(
                f"the plan would need {count} ranges, over the cap of {MAX_RANGES}; raise budget_chars"
            )
        spans = [
            (index * budget, min(chars, (index + 1) * budget), None, [])
            for index in range(count)
        ]
        unit = "chars"
    if lines is not None:
        total_lines, window_basis = lines, "caller_lines"
    else:
        total_lines, window_basis = (
            max(1, math.ceil(total_chars / ASSUMED_CHARS_PER_LINE)),
            "estimated_lines",
        )
    ranges: list[dict[str, Any]] = []
    for index, (char_start, char_end, page_span, sections) in enumerate(spans, start=1):
        estimated_chars = max(0, char_end - char_start)
        spec = {
            "chunk": index,
            "pages": page_span,
            "chars": {"start": char_start, "end": char_end},
            "sections": sections,
        }
        window = _read_window(
            char_start, char_end, max(1, total_chars), total_lines, window_basis
        )
        window["read_calls_estimated"] = max(
            window["read_calls_estimated"], max(1, math.ceil(estimated_chars / budget))
        )
        ranges.append(
            {
                **spec,
                "estimated_chars": estimated_chars,
                "estimated_tokens": math.ceil(estimated_chars / CHARS_PER_TOKEN),
                "read_window": window,
                "digest": _canonical_digest(spec)[:PLAN_ID_HEX_CHARS],
            }
        )
    if lines is not None and len(
        {entry["read_window"]["offset"] for entry in ranges}
    ) < len(ranges):
        raise DocumentPlanError(
            "lines cannot address distinct ranges: pass total_lines for the whole extraction or raise budget_chars"
        )
    assumptions = {
        "unit": unit,
        "chars_per_page": {"value": density, "basis": density_basis},
        "chars_per_line": {
            "value": None if lines is not None else ASSUMED_CHARS_PER_LINE,
            "basis": "not_applicable" if lines is not None else "assumed",
        },
        "total_chars": {
            "value": total_chars,
            "basis": "caller_supplied" if chars is not None else "estimated_from_pages",
        },
        "total_lines": {"value": total_lines, "basis": window_basis},
        "chars_per_token": CHARS_PER_TOKEN,
        "hermes_read_line_limit": HERMES_READ_LINE_LIMIT,
        "budget_chars": budget,
    }
    return ranges, assumptions


def initial_ledger(range_count: int) -> dict[str, dict[str, str]]:
    if (
        isinstance(range_count, bool)
        or not isinstance(range_count, int)
        or range_count < 0
        or range_count > MAX_RANGES
    ):
        raise DocumentPlanError("range_count must be a non-negative bounded integer")
    return {
        str(index): {
            "state": "next" if index == 1 else "missing",
            "note": "",
            "marked_at": "",
        }
        for index in range(1, range_count + 1)
    }


def ledger_summary(ledger: dict[str, dict[str, str]]) -> dict[str, Any]:
    ids: dict[str, list[int]] = {state: [] for state in CHUNK_STATES}
    for key, entry in sorted(ledger.items(), key=lambda item: int(item[0])):
        ids.setdefault(entry.get("state", "missing"), []).append(int(key))
    return {
        "counts": {state: len(ids[state]) for state in CHUNK_STATES},
        "ids_truncated": any(
            len(ids[state]) > LEDGER_ID_LIST_LIMIT for state in CHUNK_STATES
        ),
        "id_list_limit": LEDGER_ID_LIST_LIMIT,
        **{state: ids[state][:LEDGER_ID_LIST_LIMIT] for state in CHUNK_STATES},
    }


def next_chunk(ledger: dict[str, dict[str, str]]) -> int | None:
    for key, entry in sorted(ledger.items(), key=lambda item: int(item[0])):
        if entry.get("state") == "next":
            return int(key)
    return None


def _brief_template() -> str:
    return "Read {source} range {chunk}/{range_count} ({span}) with read_file(path, offset={offset}, limit={limit}); if the result is truncated, continue from its next_offset until line {end_line}. Cover that range only: explain or extract every claim, equation, figure, table, and limitation in it, quoting page or line anchors. Finish by reporting covered / next / missing for plan {plan_id} chunk {chunk}, and never report a range you did not read."


def _span_text(entry: dict[str, Any]) -> str:
    pages = entry.get("pages")
    if pages:
        text = f"pages {pages['start']}-{pages['end']}"
    else:
        chars = entry["chars"]
        text = f"chars {chars['start']}-{chars['end']}"
    sections = entry.get("sections") or []
    return text + ((": " + "; ".join(sections)) if sections else "")


def fill_brief(template: str, plan: dict[str, Any], entry: dict[str, Any]) -> str:
    window = entry["read_window"]
    return template.format(
        source=plan["source"]["label"],
        chunk=entry["chunk"],
        range_count=plan["range_count"],
        span=_span_text(entry),
        offset=window["offset"],
        limit=window["limit"],
        end_line=window["end_line"],
        plan_id=plan["plan_id"],
    )


def delegation_hint(plan: dict[str, Any]) -> dict[str, Any]:
    count = plan["range_count"]
    fan_out = count > FAN_OUT_RANGE_THRESHOLD
    return {
        "mode": "fan_out" if fan_out else "sequential",
        "fan_out_threshold": FAN_OUT_RANGE_THRESHOLD,
        "reason": f"{count} ranges exceed the fan-out threshold; one delegate_task child per range keeps each child's context to one read window and the parent's to the reports"
        if fan_out
        else f"{count} range(s) fit the parent context; read them in order and mark each",
        "tool": "delegate_task" if fan_out else "read_file",
        "per_range_brief_template": _brief_template(),
        "after_each_range": f"omj document mark --plan-id {plan['plan_id']} --range '<n>' --state covered",
        "status": DELEGATION_HINT_STATUS,
        "claim_boundary": DELEGATION_HINT_CLAIM_BOUNDARY,
    }


def range_view(plan: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    view = dict(entry)
    view["state"] = str(
        plan["ledger"].get(str(entry["chunk"]), {}).get("state", "missing")
    )
    view["brief"] = fill_brief(
        str(
            plan.get("delegation_hint", {}).get("per_range_brief_template")
            or _brief_template()
        ),
        plan,
        entry,
    )
    return view


def result_view(
    plan: dict[str, Any], *, start: int = 1, limit: int = RESULT_RANGE_LIMIT_DEFAULT
) -> dict[str, Any]:
    ranges = plan["ranges"]
    count = len(ranges)
    start = min(max(1, int(start)), max(1, count))
    limit = min(max(1, int(limit)), RESULT_RANGE_LIMIT_MAX)
    page = [range_view(plan, entry) for entry in ranges[start - 1 : start - 1 + limit]]
    end = start + len(page) - 1
    pending = next_chunk(plan["ledger"])
    view = {
        "plan_id": plan["plan_id"],
        "plan_schema_version": plan["schema_version"],
        "created_at": plan["created_at"],
        "updated_at": plan["updated_at"],
        "source": plan["source"],
        "inputs": plan["inputs"],
        "provenance": plan["provenance"],
        "assumptions": plan["assumptions"],
        "unit": plan["unit"],
        "range_count": count,
        "ranges": page,
        "ranges_from": start,
        "ranges_to": end,
        "ranges_returned": len(page),
        "truncated": end < count,
        "next_range": range_view(plan, ranges[pending - 1]) if pending else None,
        "ledger_summary": ledger_summary(plan["ledger"]),
        "delegation_hint": plan["delegation_hint"],
    }
    if end < count:
        view["page_hint"] = (
            f"ranges {end + 1}-{count} not returned; call `omj document show --plan-id {plan['plan_id']} --from {end + 1}` (limit up to {RESULT_RANGE_LIMIT_MAX}) to page through them"
        )
    basis = str(plan["source"].get("identity_basis") or "label")
    if basis != "sha256":
        view["ledger_binding_warning"] = LEDGER_BINDING_WARNING.format(basis=basis)
    return view


def build_document_plan(
    request: dict[str, Any], fingerprint: dict[str, Any], *, now: str | None = None
) -> dict[str, Any]:
    ranges, assumptions = derive_ranges(request)
    stamp = now or _utc_now()
    provenance = dict(request["provenance"])
    provenance["size_bytes"] = (
        "observed" if fingerprint.get("size_bytes") is not None else "not_observed"
    )
    provenance["sha256"] = "observed" if fingerprint.get("sha256") else "not_observed"
    plan = {
        "schema_version": DOCUMENT_CHUNK_PLAN_SCHEMA_VERSION,
        "plan_id": plan_id_for(request, fingerprint),
        "created_at": stamp,
        "updated_at": stamp,
        "source": fingerprint,
        "inputs": {
            "pages": request["pages"],
            "chars": request["chars"],
            "lines": request["lines"],
            "outline": request["outline"],
            "budget_chars": request["budget_chars"],
            "chars_per_page": request["chars_per_page"],
        },
        "provenance": provenance,
        "assumptions": assumptions,
        "unit": assumptions["unit"],
        "range_count": len(ranges),
        "ranges": ranges,
        "ledger": initial_ledger(len(ranges)),
        "progress_history": [],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    plan["delegation_hint"] = delegation_hint(plan)
    return plan


def documents_root(omj_home: Path) -> Path:
    return Path(omj_home) / "documents"


def plan_path(omj_home: Path, plan_id: str) -> Path:
    if not _PLAN_ID.match(str(plan_id)):
        raise DocumentPlanError("plan_id must be the 12-hex id a plan action returned")
    return documents_root(Path(omj_home)) / str(plan_id) / "plan.json"


@contextmanager
def document_plan_lock(
    omj_home: Path, plan_id: str, *, create: bool = False
) -> Iterator[None]:
    """Serialize one plan's read/validate/transition/write transaction."""
    root = Path(omj_home)
    destination = plan_path(root, plan_id)
    _reject_symlink_ancestry(destination, root=root)
    if not destination.parent.is_dir():
        if not create:
            raise DocumentPlanMissing(f"no document plan {plan_id} in this OMJ home")
        try:
            documents_root(root).mkdir(parents=True, exist_ok=True)
            _reject_symlink_ancestry(documents_root(root), root=root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            _reject_symlink_ancestry(destination, root=root)
        except OSError as error:
            raise DocumentPlanError(
                f"document plan lock is unavailable: {error.__class__.__name__}"
            ) from error
    lock_path = destination.with_name(".plan.lock")
    _reject_symlink_ancestry(lock_path, root=root)
    try:
        with lock_path.open("a+", encoding="utf-8") as handle:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                if fcntl is not None:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except OSError as error:
        raise DocumentPlanError(
            f"document plan lock is unavailable: {error.__class__.__name__}"
        ) from error


def _reject_symlink_ancestry(path: Path, *, root: Path) -> None:
    current = Path(path)
    root_path = Path(root)
    if root_path.is_symlink():
        raise DocumentPlanError("refusing a symlinked document plan root")
    while True:
        if current.is_symlink():
            raise DocumentPlanError("refusing a symlinked document plan path")
        if current == root_path or current == current.parent:
            return
        current = current.parent


def write_document_plan(omj_home: Path, plan: dict[str, Any]) -> Path:
    validated = validate_document_plan(plan)
    destination = plan_path(Path(omj_home), str(validated["plan_id"]))
    _reject_symlink_ancestry(destination, root=Path(omj_home))
    destination.parent.mkdir(parents=True, exist_ok=True)
    _reject_symlink_ancestry(destination, root=Path(omj_home))
    temporary = destination.with_name(
        f".{destination.name}.{os.getpid()}-{secrets.token_hex(8)}.tmp"
    )
    try:
        with temporary.open("x", encoding="utf-8") as handle:
            json.dump(validated, handle, sort_keys=True, indent=2)
            handle.write("\n")
        os.replace(temporary, destination)
    except OSError as error:
        raise DocumentPlanError(
            f"document plan destination is not writable: {error.__class__.__name__}"
        ) from error
    finally:
        if temporary.exists() and not temporary.is_symlink():
            try:
                temporary.unlink()
            except OSError:
                pass
    return destination


def read_document_plan(omj_home: Path, plan_id: str) -> dict[str, Any]:
    path = plan_path(Path(omj_home), plan_id)
    _reject_symlink_ancestry(path, root=Path(omj_home))
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise DocumentPlanMissing(
            f"no document plan {plan_id} in this OMJ home"
        ) from None
    except OSError as error:
        raise DocumentPlanError(
            f"document plan {plan_id} is unreadable: {error.__class__.__name__}"
        ) from error
    if len(raw) > _MAX_PLAN_FILE_BYTES:
        raise DocumentPlanError(
            f"document plan {plan_id} exceeds the plan file size cap"
        )
    try:
        data = json.loads(raw)
    except ValueError:
        raise DocumentPlanError(f"document plan {plan_id} is not valid JSON") from None
    return validate_document_plan(data, expected_plan_id=plan_id)


def validate_document_plan(
    data: object, *, expected_plan_id: str | None = None
) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise DocumentPlanError("a document plan is a JSON object")
    if data.get("schema_version") != DOCUMENT_CHUNK_PLAN_SCHEMA_VERSION:
        raise DocumentPlanError(
            f"expected schema_version {DOCUMENT_CHUNK_PLAN_SCHEMA_VERSION}"
        )
    plan_id = data.get("plan_id")
    if not isinstance(plan_id, str) or not _PLAN_ID.match(plan_id):
        raise DocumentPlanError("document plan carries no valid plan_id")
    if expected_plan_id is not None and plan_id != expected_plan_id:
        raise DocumentPlanError(
            "document plan file names a different plan_id than its directory"
        )
    ranges = data.get("ranges")
    if not isinstance(ranges, list) or not ranges:
        raise DocumentPlanError("document plan has no ranges")
    if data.get("range_count") != len(ranges):
        raise DocumentPlanError("document plan range_count disagrees with its ranges")
    previous_end = 0
    for index, entry in enumerate(ranges, start=1):
        if not isinstance(entry, dict) or entry.get("chunk") != index:
            raise DocumentPlanError(
                f"document plan range {index} is malformed or out of order"
            )
        chars = entry.get("chars")
        if not isinstance(chars, dict) or chars.get("start") != previous_end:
            raise DocumentPlanError(
                f"document plan range {index} has non-contiguous chars"
            )
        if not isinstance(chars.get("end"), int) or chars["end"] <= chars["start"]:
            raise DocumentPlanError(f"document plan range {index} has invalid chars")
        previous_end = chars["end"]
        window = entry.get("read_window")
        if (
            not isinstance(window, dict)
            or not isinstance(window.get("offset"), int)
            or not isinstance(window.get("limit"), int)
            or window["offset"] < 1
            or not (1 <= window["limit"] <= HERMES_READ_LINE_LIMIT)
        ):
            raise DocumentPlanError(f"document plan range {index} has no read window")
        for key in ("estimated_chars", "estimated_tokens"):
            if (
                not isinstance(entry.get(key), int)
                or isinstance(entry[key], bool)
                or entry[key] < 0
            ):
                raise DocumentPlanError(f"document plan range {index} has no {key}")
        if not isinstance(entry.get("digest"), str) or not entry["digest"]:
            raise DocumentPlanError(f"document plan range {index} has no digest")
    ledger = data.get("ledger")
    if not isinstance(ledger, dict) or set(ledger) != {
        str(index) for index in range(1, len(ranges) + 1)
    }:
        raise DocumentPlanError(
            "document plan ledger does not cover its ranges exactly"
        )
    next_count = 0
    for key, entry in ledger.items():
        if not isinstance(entry, dict) or entry.get("state") not in CHUNK_STATES:
            raise DocumentPlanError(
                f"document plan ledger entry {key} has no valid state"
            )
        if entry.get("state") == "next":
            next_count += 1
    if next_count > 1:
        raise DocumentPlanError("document plan ledger may name at most one next range")
    history = data.get("progress_history", [])
    if not isinstance(history, list) or len(history) > MAX_PROGRESS_HISTORY:
        raise DocumentPlanError(
            "document plan progress history is malformed or over its cap"
        )
    for event in history:
        if not isinstance(event, dict):
            raise DocumentPlanError(
                "document plan progress history has a malformed event"
            )
        if (
            isinstance(event.get("chunk"), bool)
            or not isinstance(event.get("chunk"), int)
            or not 1 <= event["chunk"] <= len(ranges)
            or event.get("state") not in CHUNK_STATES
            or not isinstance(event.get("note", ""), str)
            or len(event.get("note", "")) > MAX_NOTE_CHARS
            or not isinstance(event.get("marked_at", ""), str)
        ):
            raise DocumentPlanError(
                "document plan progress history has an invalid event"
            )
    source = data.get("source")
    if (
        not isinstance(source, dict)
        or not isinstance(source.get("label"), str)
        or not source["label"]
    ):
        raise DocumentPlanError("document plan names no source")
    if not isinstance(data.get("delegation_hint"), dict):
        raise DocumentPlanError("document plan carries no delegation_hint")
    return data


def _mark_document_plan_chunk_locked(
    omj_home: Path,
    plan_id: str,
    chunk: object,
    state: object,
    note: object = "",
    *,
    now: str | None = None,
) -> dict[str, Any]:
    plan = read_document_plan(omj_home, plan_id)
    state_text = strip_control_characters(state).casefold()
    if state_text not in CHUNK_STATES:
        raise DocumentPlanError("state must be one of " + ", ".join(CHUNK_STATES))
    index = _optional_count({"chunk": chunk}, "chunk", maximum=MAX_RANGES)
    if index is None:
        raise DocumentPlanError("mark needs the chunk number to update")
    if index > plan["range_count"]:
        raise DocumentPlanError(
            f"chunk {index} is past the last range {plan['range_count']}"
        )
    note_text = strip_control_characters(note)
    if len(note_text) > MAX_NOTE_CHARS:
        raise DocumentPlanError(f"note is capped at {MAX_NOTE_CHARS} characters")
    stamp = now or _utc_now()
    ledger = plan["ledger"]
    key = str(index)
    previous = ledger[key]
    previous_state = str(previous.get("state", "missing"))
    previous_note = str(previous.get("note", ""))
    if previous_state == state_text and previous_note == note_text:
        return plan
    if previous_state == "covered" and state_text != "covered":
        raise DocumentPlanError(f"covered range {index} cannot regress to {state_text}")
    pending = next_chunk(ledger)
    if state_text in {"covered", "next"} and previous_state != state_text:
        if pending is None or index != pending:
            target = pending if pending is not None else "none"
            raise DocumentPlanError(
                f"cannot mark range {index} {state_text} before next range {target}; refusing a progress gap"
            )

    history = list(plan.get("progress_history", []))
    if len(history) >= MAX_PROGRESS_HISTORY:
        raise DocumentPlanError(
            f"document plan progress history is capped at {MAX_PROGRESS_HISTORY} events"
        )
    ledger[key] = {"state": state_text, "note": note_text, "marked_at": stamp}
    if not any(entry.get("state") == "next" for entry in ledger.values()):
        for other_key in sorted(ledger, key=int):
            if other_key != key and ledger[other_key].get("state") == "missing":
                ledger[other_key]["state"] = "next"
                break
    history.append(
        {"chunk": index, "state": state_text, "note": note_text, "marked_at": stamp}
    )
    plan["progress_history"] = history
    plan["updated_at"] = stamp
    write_document_plan(omj_home, plan)
    return plan


def mark_document_plan_chunk(
    omj_home: Path,
    plan_id: str,
    chunk: object,
    state: object,
    note: object = "",
    *,
    now: str | None = None,
    _lock_held: bool = False,
) -> dict[str, Any]:
    if _lock_held:
        return _mark_document_plan_chunk_locked(
            omj_home, plan_id, chunk, state, note, now=now
        )
    with document_plan_lock(omj_home, plan_id):
        return _mark_document_plan_chunk_locked(
            omj_home, plan_id, chunk, state, note, now=now
        )
