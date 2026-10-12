"""Bounded, source-digested project terminology capture.

The document is vocabulary only.  Parsed records are immutable metadata and do
not become instructions, routing rules, approvals, execution, or evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re
import unicodedata
from typing import Literal

PROJECT_TERMS_SCHEMA_VERSION = "omj-project-terms/v1"
MAX_PROJECT_TERMS_SOURCE_BYTES = 65_536
PROJECT_TERMS_BOUNDARY = (
    "Project terminology only. This file is not agent instructions, routing rules, "
    "approval, execution, or evidence. Changes affect OMJ only after explicit review."
)

_TERM_ROW = re.compile(r"^- term: `([^`]+)` = `([^`]+)`$")
_HINT_ROW = re.compile(r"^- workflow-hint: `([^`]+)`$")
_DOMAIN_ROW = re.compile(r"^## domain: (.+)$")
_LOCALIZED_ROW = re.compile(r"^  localized\[([^]]+)\]: (.+)$")
_DISTINCT_ROW = re.compile(r"^  distinct-from: `([^`]+)` - (.+)$")
_VERSION_ROW = re.compile(r"^<!-- omj-project-terms/v[^ ]+ -->$")
_LOCALE = re.compile(r"^(?P<language>[A-Za-z]{2,3})(?:-(?P<script>[A-Za-z]{4}))?(?:-(?P<region>[A-Za-z]{2}|[0-9]{3}))?$")


class ProjectTermsParseError(ValueError):
    """Stable fail-closed PROJECT_TERMS.md parse refusal."""


@dataclass(frozen=True)
class ProjectTermsLocalizedLabel:
    locale: str
    label: str


@dataclass(frozen=True)
class ProjectTermsDistinctFrom:
    canonical: str
    note: str


@dataclass(frozen=True)
class ProjectTermsMapping:
    phrase: str
    canonical: str
    definition: str | None
    say_instead: tuple[str, ...]
    localized: tuple[ProjectTermsLocalizedLabel, ...]
    distinct_from: ProjectTermsDistinctFrom | None


@dataclass(frozen=True)
class ProjectTermsDomain:
    domain_id: str
    mappings: tuple[ProjectTermsMapping, ...]
    workflow_hints: tuple[str, ...]


@dataclass(frozen=True)
class ProjectTermsDocument:
    schema_version: str
    source_sha256: str
    domains: tuple[ProjectTermsDomain, ...]


@dataclass(frozen=True)
class ProjectTermsCaptureInput:
    domain_id: str
    mappings: tuple[tuple[str, str], ...]
    workflow_hints: tuple[str, ...]
    source_class: Literal["omj_local"]
    source_ref: str


@dataclass
class _MappingBuilder:
    phrase: str
    canonical: str
    definition: str | None = None
    say_instead: list[str] = field(default_factory=list)
    localized: dict[str, str] = field(default_factory=dict)
    distinct_from: ProjectTermsDistinctFrom | None = None


@dataclass
class _DomainBuilder:
    domain_id: str
    mappings: list[_MappingBuilder] = field(default_factory=list)
    workflow_hints: list[str] = field(default_factory=list)


def parse_project_terms(source: bytes) -> ProjectTermsDocument:
    """Parse exact bounded UTF-8 bytes and retain only a source digest."""
    text = _decode_source(source)
    lines = _validate_preamble_and_split(text)
    domains = _parse_domains(lines)
    return ProjectTermsDocument(
        schema_version=PROJECT_TERMS_SCHEMA_VERSION,
        source_sha256=hashlib.sha256(source).hexdigest(),
        domains=tuple(_freeze_domain(domain) for domain in sorted(domains, key=lambda item: item.domain_id)),
    )


def build_project_terms_capture_inputs(document: ProjectTermsDocument) -> tuple[ProjectTermsCaptureInput, ...]:
    """Project machine-consumed mappings/hints with metadata-only provenance."""
    if not isinstance(document, ProjectTermsDocument):
        raise TypeError("document must be a ProjectTermsDocument")
    source_ref = f"pt_sha256:{document.source_sha256}"
    return tuple(
        ProjectTermsCaptureInput(
            domain_id=domain.domain_id,
            mappings=tuple((mapping.phrase, mapping.canonical) for mapping in domain.mappings),
            workflow_hints=domain.workflow_hints,
            source_class="omj_local",
            source_ref=source_ref,
        )
        for domain in document.domains
    )


def _decode_source(source: bytes) -> str:
    if not isinstance(source, bytes):
        raise ProjectTermsParseError("invalid_project_terms_source_type")
    if len(source) > MAX_PROJECT_TERMS_SOURCE_BYTES:
        raise ProjectTermsParseError("project_terms_source_too_large")
    if source.startswith((b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")):
        raise ProjectTermsParseError("unsupported_project_terms_encoding")
    try:
        text = source.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProjectTermsParseError("unsupported_project_terms_encoding") from exc
    if "\r" in text:
        if "\n" in text.replace("\r\n", "") or "\r" in text.replace("\r\n", ""):
            raise ProjectTermsParseError("invalid_project_terms_line_endings")
        text = text.replace("\r\n", "\n")
    return text


def _validate_preamble_and_split(text: str) -> list[str]:
    lines = text.split("\n")
    if not lines or lines[0] != "# Project Terms":
        raise ProjectTermsParseError("invalid_project_terms_header")
    if len(lines) < 7:
        raise ProjectTermsParseError("invalid_project_terms_structure")
    if lines[2] != PROJECT_TERMS_BOUNDARY:
        raise ProjectTermsParseError("invalid_project_terms_boundary")
    if lines[4] != f"<!-- {PROJECT_TERMS_SCHEMA_VERSION} -->":
        if _VERSION_ROW.fullmatch(lines[4]):
            raise ProjectTermsParseError("unsupported_project_terms_version")
        raise ProjectTermsParseError("invalid_project_terms_version_marker")
    if lines[1] or lines[3] or lines[5]:
        raise ProjectTermsParseError("invalid_project_terms_structure")
    return lines[6:]


def _parse_domains(lines: list[str]) -> list[_DomainBuilder]:
    domains: list[_DomainBuilder] = []
    domain_ids: set[str] = set()
    current_domain: _DomainBuilder | None = None
    current_mapping: _MappingBuilder | None = None
    for line in lines:
        if not line:
            current_mapping = None
            continue
        domain_match = _DOMAIN_ROW.fullmatch(line)
        if domain_match:
            domain_id = _normalize_identifier_value(domain_match.group(1), "domain_id")
            if domain_id in domain_ids:
                raise ProjectTermsParseError("duplicate_project_terms_domain")
            if current_domain is not None:
                _validate_domain_counts(current_domain)
            current_domain = _DomainBuilder(domain_id)
            domains.append(current_domain)
            domain_ids.add(domain_id)
            current_mapping = None
            continue
        if current_domain is None:
            raise ProjectTermsParseError("project_terms_content_before_domain")
        term_match = _TERM_ROW.fullmatch(line)
        if term_match:
            current_mapping = _new_mapping(term_match.group(1), term_match.group(2), current_domain)
            current_domain.mappings.append(current_mapping)
            if len(current_domain.mappings) > 1000:
                raise ProjectTermsParseError("too_many_project_terms_mappings")
            continue
        hint_match = _HINT_ROW.fullmatch(line)
        if hint_match:
            hint = _normalize_workflow_hint(hint_match.group(1))
            if hint in current_domain.workflow_hints:
                raise ProjectTermsParseError("duplicate_project_terms_workflow_hint")
            current_domain.workflow_hints.append(hint)
            if len(current_domain.workflow_hints) > 256:
                raise ProjectTermsParseError("too_many_project_terms_workflow_hints")
            current_mapping = None
            continue
        if line.startswith("  "):
            if current_mapping is None:
                raise ProjectTermsParseError("project_terms_metadata_without_term")
            _parse_metadata(line, current_mapping)
            continue
        raise ProjectTermsParseError("unknown_project_terms_line")
    if current_domain is not None:
        _validate_domain_counts(current_domain)
    if not domains:
        raise ProjectTermsParseError("project_terms_has_no_domains")
    return domains


def _new_mapping(phrase: str, canonical: str, domain: _DomainBuilder) -> _MappingBuilder:
    normalized_phrase, normalized_canonical = _normalize_mapping_pair(phrase, canonical)
    for existing in domain.mappings:
        if existing.phrase.casefold() != normalized_phrase.casefold():
            continue
        if existing.canonical == normalized_canonical:
            raise ProjectTermsParseError("duplicate_project_terms_mapping")
        raise ProjectTermsParseError("conflicting_project_terms_mapping")
    return _MappingBuilder(normalized_phrase, normalized_canonical)


def _parse_metadata(line: str, mapping: _MappingBuilder) -> None:
    if line.startswith("  definition: "):
        if mapping.definition is not None:
            raise ProjectTermsParseError("duplicate_project_terms_metadata")
        mapping.definition = _normalize_human_value(line.removeprefix("  definition: "), 240)
        return
    if line.startswith("  say-instead: "):
        value = _normalize_human_value(line.removeprefix("  say-instead: "), 80)
        if value.casefold() in {item.casefold() for item in mapping.say_instead}:
            raise ProjectTermsParseError("duplicate_project_terms_metadata")
        mapping.say_instead.append(value)
        return
    localized_match = _LOCALIZED_ROW.fullmatch(line)
    if localized_match:
        locale = _normalize_locale(localized_match.group(1))
        if locale in mapping.localized:
            raise ProjectTermsParseError("duplicate_project_terms_metadata")
        mapping.localized[locale] = _normalize_human_value(localized_match.group(2), 80)
        return
    distinct_match = _DISTINCT_ROW.fullmatch(line)
    if distinct_match:
        if mapping.distinct_from is not None:
            raise ProjectTermsParseError("duplicate_project_terms_metadata")
        mapping.distinct_from = ProjectTermsDistinctFrom(
            canonical=_normalize_identifier_value(distinct_match.group(1), "canonical_term"),
            note=_normalize_human_value(distinct_match.group(2), 240),
        )
        return
    raise ProjectTermsParseError("unknown_project_terms_metadata")


def _normalize_mapping_pair(phrase: str, canonical: str) -> tuple[str, str]:
    return _normalize_human_value(phrase, 80), _normalize_identifier_value(canonical, "canonical_term")


def _normalize_identifier_value(value: str, label: str) -> str:
    normalized = _normalize_human_value(value, 80)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", normalized):
        raise ProjectTermsParseError(f"invalid_project_terms_{label}")
    return normalized.lower()

def _normalize_workflow_hint(value: str) -> str:
    normalized = _normalize_identifier_value(value, "workflow_hint")
    from ..skills.catalog import installable_skill_names

    if normalized not in installable_skill_names():
        raise ProjectTermsParseError("unknown_project_terms_workflow_hint")
    return normalized


def _normalize_locale(value: str) -> str:
    normalized = _normalize_human_value(value, 35)
    match = _LOCALE.fullmatch(normalized)
    if not match:
        raise ProjectTermsParseError("unknown_project_terms_locale")
    parts = [match.group("language").lower()]
    if match.group("script"):
        parts.append(match.group("script").title())
    if match.group("region"):
        parts.append(match.group("region").upper())
    return "-".join(parts)


def _normalize_human_value(value: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise ProjectTermsParseError("invalid_project_terms_value_length")
    normalized = " ".join(unicodedata.normalize("NFKC", value).strip().split())
    if not normalized or len(normalized) > maximum:
        raise ProjectTermsParseError("invalid_project_terms_value_length")
    # Refuse control/bidi characters and prompt-like content: this is metadata only.
    if any(unicodedata.category(character).startswith("C") for character in normalized):
        raise ProjectTermsParseError("unsafe_project_terms_value")
    lowered = normalized.casefold()
    if (
        re.search(r"\b(?:developer|system|user|assistant)\s*:", normalized, re.IGNORECASE)
        or "ignore previous instructions" in lowered
        or "traceback (most recent call last)" in lowered
        or re.search(r"\b(?:password|api[_ -]?key|token)\s*=", lowered)
    ):
        raise ProjectTermsParseError("unsafe_project_terms_value")
    return normalized

def _validate_domain_counts(domain: _DomainBuilder) -> None:
    if not domain.mappings:
        raise ProjectTermsParseError("project_terms_domain_has_no_mappings")


def _freeze_domain(domain: _DomainBuilder) -> ProjectTermsDomain:
    mappings = tuple(
        ProjectTermsMapping(
            phrase=mapping.phrase,
            canonical=mapping.canonical,
            definition=mapping.definition,
            say_instead=tuple(mapping.say_instead),
            localized=tuple(ProjectTermsLocalizedLabel(locale, label) for locale, label in sorted(mapping.localized.items())),
            distinct_from=mapping.distinct_from,
        )
        for mapping in sorted(domain.mappings, key=lambda item: (item.phrase.casefold(), item.canonical))
    )
    return ProjectTermsDomain(
        domain_id=domain.domain_id,
        mappings=mappings,
        workflow_hints=tuple(sorted(domain.workflow_hints)),
    )
