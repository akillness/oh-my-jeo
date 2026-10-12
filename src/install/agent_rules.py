"""Safely discover and import external agent rule files as OMJ skills.

The module is deliberately local and offline.  Discovery is explicit-root only;
source text is read as data, converted to an imported skill document, and
recorded in a manifest independent from the normal managed-skill manifest.
Importing is never evidence that Hermes loaded or followed the rule.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal, TypeAlias

from ..system.local_store import (
    atomic_write_json,
    atomic_write_text,
    ensure_dir,
    read_json_object_result,
    utc_now,
)

EXTERNAL_RULE_IMPORT_SCHEMA_VERSION: Final = "external_rule_import/v1"
IMPORT_MANIFEST_FILE: Final = "skills-import-manifest.json"
IMPORTED_SKILLS_DIR_NAME: Final = "imported"
IMPORTED_CATEGORY_DIR: Final = IMPORTED_SKILLS_DIR_NAME
IMPORTED_NAME_PREFIX: Final = "omj-imported-"

MAX_IMPORT_SOURCES: Final = 40
MAX_SOURCE_BYTES: Final = 131_072
MAX_DESCRIPTION_CHARS: Final = 200
MAX_SLUG_CHARS: Final = 60
_MISSING_TARGET: Final = "__missing__"

EXTERNAL_RULE_IMPORT_CLAIM_BOUNDARY: Final = (
    "An imported rule skill is registered content only. Import is not evidence "
    "that Hermes loaded the skill, followed it, or that the rule changed any outcome."
)

RuleFormat: TypeAlias = Literal[
    "cursorrules",
    "cursor-mdc",
    "clinerules",
    "windsurfrules",
    "copilot-instructions",
]

_PROMPT_INJECTION: Final = re.compile(
    r"(?:"
    r"\b(?:ignore|disregard|forget|override|bypass|supersede)\b"
    r"\s+(?:all\s+)?(?:the\s+)?(?:previous|prior|earlier|above|system|developer)"
    r"\s+(?:instructions?|messages?|rules?)\b"
    r"|\b(?:reveal|exfiltrate|dump|disclose)\b"
    r"\s+(?:the\s+)?(?:hidden|system|developer|private)?\s*"
    r"(?:prompt|instructions?|secrets?|tokens?|credentials?)\b"
    r")",
    re.IGNORECASE,
)
_SLUG_SANITIZE: Final = re.compile(r"[^a-z0-9]+")
_MDC_KEY: Final = re.compile(r"^(description|globs|alwaysApply)\s*:\s*(.*)$")
_FRONTMATTER_LINE: Final = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*\s*:")

# These predicates intentionally identify issued credential values, not words
# such as ``secrets`` or environment-variable names such as ``GITHUB_TOKEN``.
_COMMON_SECRET_PREFIX: Final = re.compile(
    r"(?:^|[^a-z0-9])(?:sk|pk|rk|xox[a-z]?)[_-][a-z0-9_-]{8,}",
    re.IGNORECASE,
)
_PLATFORM_SECRET_PREFIX: Final = re.compile(
    r"(?:^|[^a-z0-9])(?:gh[oprs]|github_pat|npm|whsec|glpat)[_-][a-z0-9_-]{16,}",
    re.IGNORECASE,
)
_AWS_ACCESS_KEY: Final = re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")
_GOOGLE_API_KEY: Final = re.compile(r"\bAIza[A-Za-z0-9_-]{20,}\b", re.IGNORECASE)
_PRIVATE_KEY: Final = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
_JWT: Final = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
_AUTH_URL: Final = re.compile(r"[a-z][a-z0-9+.-]*://[^\s:/]+:[^\s@]+@", re.IGNORECASE)
_SECRET_ASSIGNMENT: Final = re.compile(
    r"\b(?:api[_-]?key|access[_-]?token|secret|password|passwd|private[_-]?key|credential)"
    r"\s*[:=]\s*['\"]?([^\s'\"]{8,})",
    re.IGNORECASE,
)
_PLACEHOLDER_VALUE: Final = re.compile(
    r"^(?:from\s+env|env|environment|os\.getenv|os\.environ|none|null|example|placeholder|"
    r"changeme|your[_-].*|<.*>|\$\{.*\})$",
    re.IGNORECASE,
)


class ExternalRuleImportError(ValueError):
    """Raised when an external-rule discovery or import request is unsafe."""


@dataclass(frozen=True)
class DiscoveredRuleSource:
    relative_path: str
    format_name: RuleFormat


@dataclass(frozen=True)
class RuleImportItem:
    slug: str
    source_relative_path: str
    format_name: RuleFormat
    source_sha256: str
    byte_count: int
    target_relative_path: str
    status: str  # planned | unchanged | refused
    refusal_reasons: tuple[str, ...]
    description: str
    body: str

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "source": self.source_relative_path,
            "format": self.format_name,
            "source_sha256": self.source_sha256,
            "byte_count": self.byte_count,
            "target": self.target_relative_path,
            "status": self.status,
            "refusal_reasons": list(self.refusal_reasons),
        }


def import_manifest_path(omj_home: Path) -> Path:
    """Return the independent manifest path for imported rule skills."""
    return omj_home / IMPORT_MANIFEST_FILE


def discover_rule_sources(repo_root: Path) -> list[DiscoveredRuleSource]:
    """Discover only known external rule locations below an explicit root."""
    if not repo_root.is_dir():
        raise ExternalRuleImportError(f"repo root is not a directory: {repo_root}")

    sources: list[DiscoveredRuleSource] = []

    def add_file(relative: str, format_name: RuleFormat) -> None:
        path = repo_root / relative
        # Symlink files are not trusted as discovered sources.  A symlinked
        # directory is allowed to enumerate so plan-time containment can report
        # a refusal instead of silently importing data outside the root.
        if path.is_file() and not path.is_symlink():
            sources.append(DiscoveredRuleSource(relative, format_name))

    add_file(".cursorrules", "cursorrules")

    cursor_rules_dir = repo_root / ".cursor" / "rules"
    if cursor_rules_dir.is_dir():
        for entry in sorted(cursor_rules_dir.glob("*.mdc")):
            if entry.is_file() and not entry.is_symlink():
                sources.append(
                    DiscoveredRuleSource(str(entry.relative_to(repo_root)), "cursor-mdc")
                )

    cline_rules = repo_root / ".clinerules"
    if cline_rules.is_file() and not cline_rules.is_symlink():
        sources.append(DiscoveredRuleSource(".clinerules", "clinerules"))
    elif cline_rules.is_dir():
        for entry in sorted(cline_rules.glob("*.md")):
            if entry.is_file() and not entry.is_symlink():
                sources.append(
                    DiscoveredRuleSource(str(entry.relative_to(repo_root)), "clinerules")
                )

    add_file(".windsurfrules", "windsurfrules")
    add_file(".github/copilot-instructions.md", "copilot-instructions")

    if len(sources) > MAX_IMPORT_SOURCES:
        raise ExternalRuleImportError(
            f"{len(sources)} rule sources discovered; import is bounded to {MAX_IMPORT_SOURCES}"
        )
    for source in sources:
        if any(ord(char) < 32 or char == "\x7f" for char in source.relative_path):
            raise ExternalRuleImportError(
                "rule source path contains control characters; refusing the whole import: "
                f"{source.relative_path!r}"
            )
    return sources


def plan_rule_import(
    repo_root: Path,
    *,
    skills_dir: Path,
    omj_home: Path,
    only_sources: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Prepare a complete import plan without writing any files."""
    _validate_destination_root(skills_dir, label="skills_dir")
    _validate_destination_root(omj_home, label="omj_home")
    manifest_path = import_manifest_path(omj_home)
    if manifest_path.is_symlink():
        raise ExternalRuleImportError("import manifest path is a symlink; refusing")
    manifest_sha256 = _manifest_snapshot(manifest_path)
    discovered = discover_rule_sources(repo_root)
    if only_sources:
        wanted = set(only_sources)
        discovered = [source for source in discovered if source.relative_path in wanted]
        missing = wanted - {source.relative_path for source in discovered}
        if missing:
            raise ExternalRuleImportError(
                f"--source paths not discovered under {repo_root}: {', '.join(sorted(missing))}"
            )

    manifest, manifest_error = read_json_object_result(import_manifest_path(omj_home))
    if manifest_error:
        raise ExternalRuleImportError(
            f"import manifest is unreadable ({manifest_error}); fix or delete it and re-run"
        )
    manifest = manifest or {}
    prior_entries = [entry for entry in manifest.get("entries", []) if isinstance(entry, dict)]
    recorded = {
        str(entry.get("source", "")): str(entry.get("source_sha256", ""))
        for entry in prior_entries
    }

    # Preserve existing slugs for the same source (idempotence), while avoiding
    # collisions with any other imported entry or newly discovered source.
    prior_by_source = {
        str(entry.get("source", "")): entry
        for entry in prior_entries
        if str(entry.get("source", ""))
    }
    used_slugs = {
        str(entry.get("slug", ""))
        for entry in prior_entries
        if str(entry.get("slug", ""))
    }
    items: list[RuleImportItem] = []
    for source in discovered:
        prior = prior_by_source.get(source.relative_path)
        reserved = str(prior.get("slug", "")) if prior else ""
        if reserved:
            used_slugs.discard(reserved)
        items.append(
            _plan_item(
                repo_root,
                source,
                skills_dir=skills_dir,
                recorded=recorded,
                prior_entry=prior,
                used_slugs=used_slugs,
                reserved_slug=reserved,
            )
        )

    discovered_sources = {source.relative_path for source in discovered}
    orphaned = (
        []
        if only_sources
        else [
            entry
            for entry in prior_entries
            if str(entry.get("source", "")) not in discovered_sources
        ]
    )
    target_states: dict[str, str] = {}
    for item in items:
        target = _target_path(skills_dir, item.target_relative_path)
        if target is None or not target.exists():
            target_states[item.slug] = _MISSING_TARGET
            continue
        try:
            target_states[item.slug] = _sha256_file(target)
        except OSError:
            target_states[item.slug] = "__unreadable__"
    return {
        "schema_version": EXTERNAL_RULE_IMPORT_SCHEMA_VERSION,
        "repo_root": str(repo_root),
        "skills_dir": str(skills_dir),
        "omj_home": str(omj_home),
        "discovered_count": len(items),
        "planned": [item.to_public_dict() for item in items if item.status == "planned"],
        "unchanged": [item.to_public_dict() for item in items if item.status == "unchanged"],
        "refused": [item.to_public_dict() for item in items if item.status == "refused"],
        "orphaned": [
            {
                "slug": entry.get("slug", ""),
                "source": entry.get("source", ""),
                "target": entry.get("target", ""),
            }
            for entry in orphaned
        ],
        "claim_boundary": EXTERNAL_RULE_IMPORT_CLAIM_BOUNDARY,
        "_items": items,
        "_prior_entries": prior_entries,
        "_scoped": bool(only_sources),
        "_manifest_sha256": manifest_sha256,
        "_target_states": target_states,
        "_skills_dir_identity": _destination_identity(skills_dir),
        "_omj_home_identity": _destination_identity(omj_home),
        "_orphaned_sources": tuple(sorted(str(entry.get("source", "")) for entry in orphaned)),
    }


def apply_rule_import(
    plan: dict[str, Any], *, skills_dir: Path, omj_home: Path
) -> dict[str, Any]:
    """Apply a prepared plan and update only the independent import manifest."""
    if not isinstance(plan, dict) or plan.get("schema_version") != EXTERNAL_RULE_IMPORT_SCHEMA_VERSION:
        raise ExternalRuleImportError("apply requires a prepared external-rule import plan")
    required_private = (
        "_items",
        "_prior_entries",
        "_scoped",
        "_manifest_sha256",
        "_target_states",
        "_skills_dir_identity",
        "_omj_home_identity",
        "_orphaned_sources",
    )
    if any(key not in plan for key in required_private):
        raise ExternalRuleImportError("apply requires an unstripped plan produced by plan_rule_import")
    if plan.get("_skills_dir_identity") != _destination_identity(skills_dir):
        raise ExternalRuleImportError("prepared plan skills_dir does not match apply destination")
    if plan.get("_omj_home_identity") != _destination_identity(omj_home):
        raise ExternalRuleImportError("prepared plan omj_home does not match apply destination")
    _validate_destination_root(skills_dir, label="skills_dir")
    _validate_destination_root(omj_home, label="omj_home")
    manifest_path = import_manifest_path(omj_home)
    if _manifest_snapshot(manifest_path) != str(plan.get("_manifest_sha256", "")):
        raise ExternalRuleImportError("import manifest changed after planning; re-plan before apply")
    raw_items = plan.get("_items")
    raw_prior_entries = plan.get("_prior_entries")
    if not isinstance(raw_items, list) or any(not isinstance(item, RuleImportItem) for item in raw_items):
        raise ExternalRuleImportError("prepared plan items are invalid")
    if not isinstance(raw_prior_entries, list) or any(not isinstance(entry, dict) for entry in raw_prior_entries):
        raise ExternalRuleImportError("prepared plan manifest entries are invalid")
    if (
        not isinstance(plan.get("_scoped"), bool)
        or not isinstance(plan.get("_target_states"), dict)
        or not isinstance(plan.get("_orphaned_sources"), tuple)
        or any(not isinstance(source, str) for source in plan["_orphaned_sources"])
    ):
        raise ExternalRuleImportError("prepared plan metadata is invalid")
    items = list(raw_items)
    prior_entries = [dict(entry) for entry in raw_prior_entries]
    scoped = bool(plan["_scoped"])
    target_states = {str(key): str(value) for key, value in plan["_target_states"].items()}
    written: list[str] = []
    preserved: list[str] = []
    planned_targets: list[tuple[RuleImportItem, Path]] = []
    for item in items:
        if item.status != "planned":
            continue
        target = _target_path(skills_dir, item.target_relative_path)
        expected = target_states.get(item.slug)
        if target is None or expected is None:
            raise ExternalRuleImportError(f"prepared target metadata is missing: {item.slug}")
        _assert_target_snapshot(target, expected, slug=item.slug)
        _assert_write_slot(target)
        planned_targets.append((item, target))

    for item, _planned_target in planned_targets:
        target = _target_path(skills_dir, item.target_relative_path)
        expected = target_states[item.slug]
        if target is None:
            raise ExternalRuleImportError(f"prepared target path became unsafe: {item.slug}")
        _assert_target_snapshot(target, expected, slug=item.slug)
        _assert_write_slot(target)
        ensure_dir(target.parent)
        target = _target_path(skills_dir, item.target_relative_path)
        if target is None:
            raise ExternalRuleImportError(f"prepared target path became unsafe: {item.slug}")
        _assert_target_snapshot(target, expected, slug=item.slug)
        _assert_write_slot(target)
        atomic_write_text(target, _render_skill_document(item))
        written.append(item.slug)

    removed: list[str] = []
    orphaned_sources = set(plan["_orphaned_sources"])
    if not scoped:
        for entry in prior_entries:
            if str(entry.get("source", "")) not in orphaned_sources:
                continue
            target_rel = str(entry.get("target", ""))
            target = _target_path(skills_dir, target_rel)
            target_dir = target.parent if target is not None else None
            if target_dir is None or not target_dir.is_dir() or target_dir.is_symlink():
                continue
            # Never remove a directory containing user additions, or a target
            # whose digest is absent/mismatched.  Fresh manifests carry the
            # target digest; old/handwritten manifests are preserved safely.
            expected_target_sha = str(entry.get("target_sha256", ""))
            if not expected_target_sha or not target.is_file():
                preserved.append(str(entry.get("slug", "")))
                continue
            try:
                actual_target_sha = _sha256_file(target)
            except OSError:
                preserved.append(str(entry.get("slug", "")))
                continue
            if actual_target_sha != expected_target_sha:
                preserved.append(str(entry.get("slug", "")))
                continue
            try:
                children = list(target_dir.iterdir())
            except OSError:
                preserved.append(str(entry.get("slug", "")))
                continue
            if children != [target]:
                preserved.append(str(entry.get("slug", "")))
                continue
            shutil.rmtree(target_dir)
            removed.append(str(entry.get("slug", "")))

    handled_sources = {item.source_relative_path for item in items}
    kept_entries = [
        entry
        for entry in prior_entries
        if str(entry.get("source", "")) not in handled_sources
        and str(entry.get("source", "")) not in (orphaned_sources if not scoped else set())
    ]

    fresh_entries: list[dict[str, Any]] = []
    for item in items:
        if item.status not in ("planned", "unchanged"):
            continue
        target = _target_path(skills_dir, item.target_relative_path)
        if target is None or not target.is_file():
            preserved.append(item.slug)
            continue
        prior_for_item = next(
            (
                entry
                for entry in prior_entries
                if str(entry.get("source", "")) == item.source_relative_path
                and str(entry.get("target", "")) == item.target_relative_path
            ),
            None,
        )
        try:
            target_sha = _sha256_file(target)
        except OSError:
            preserved.append(item.slug)
            continue
        if item.status == "unchanged" and prior_for_item is not None:
            # An unchanged source may have an operator-edited imported document;
            # retain the prior ownership digest so orphan cleanup will preserve
            # that custom text rather than treating it as freshly managed.
            target_sha = str(prior_for_item.get("target_sha256", ""))
        fresh_entries.append(
            {
                "slug": item.slug,
                "source": item.source_relative_path,
                "source_sha256": item.source_sha256,
                "format": item.format_name,
                "target": item.target_relative_path,
                "target_sha256": target_sha,
                "imported_at": utc_now(),
            }
        )

    refused_sources = {item.source_relative_path for item in items if item.status == "refused"}
    carried_refused = [
        entry for entry in prior_entries if str(entry.get("source", "")) in refused_sources
    ]
    # Keep entries whose orphan target was intentionally preserved; they remain
    # independent and visible instead of being silently lost.
    preserved_sources = {
        str(entry.get("source", ""))
        for entry in prior_entries
        if str(entry.get("slug", "")) in set(preserved)
    }
    carried_preserved = [
        entry for entry in prior_entries if str(entry.get("source", "")) in preserved_sources
    ]
    manifest_entries = sorted(
        _dedupe_entries(kept_entries + carried_refused + carried_preserved + fresh_entries),
        key=lambda entry: str(entry.get("source", "")),
    )
    if _manifest_snapshot(manifest_path) != str(plan["_manifest_sha256"]):
        raise ExternalRuleImportError("import manifest changed during apply; refusing manifest update")
    _assert_write_slot(manifest_path)
    atomic_write_json(
        import_manifest_path(omj_home),
        {"schema_version": EXTERNAL_RULE_IMPORT_SCHEMA_VERSION, "entries": manifest_entries},
    )
    public = public_plan(plan)
    public["written"] = sorted(written)
    public["removed"] = sorted(removed)
    if preserved:
        public["preserved"] = sorted(set(preserved))
    return public


def public_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Strip private objects used to carry plan state into ``apply``."""
    return {key: value for key, value in plan.items() if not key.startswith("_")}


def _plan_item(
    repo_root: Path,
    source: DiscoveredRuleSource,
    *,
    skills_dir: Path,
    recorded: dict[str, str],
    prior_entry: dict[str, Any] | None,
    used_slugs: set[str],
    reserved_slug: str = "",
) -> RuleImportItem:
    refusals: list[str] = []
    text = ""
    try:
        raw = _read_contained_source(repo_root, source.relative_path)
    except ExternalRuleImportError as exc:
        refusals.append(str(exc))
        raw = b""

    source_sha256 = hashlib.sha256(raw).hexdigest()
    slug = reserved_slug or _slug_for(source.relative_path, source_sha256, used_slugs)
    used_slugs.add(slug)
    target_rel = f"{IMPORTED_CATEGORY_DIR}/{slug}/SKILL.md"
    if raw:
        text = raw.decode("utf-8", errors="replace")
        scan_text = _normalize_scan_text(text)
        if _PROMPT_INJECTION.search(scan_text):
            refusals.append("prompt-injection phrasing requires human review before import")
        for line_number, line in enumerate(scan_text.splitlines(), start=1):
            if _is_secret_value_shaped(line):
                refusals.append(
                    f"line {line_number} looks like an issued credential value; refused"
                )
                break

    description, body = _describe(source.format_name, source.relative_path, text)
    target = _target_path(skills_dir, target_rel)
    if target is None:
        refusals.append("import target path is unsafe or contains a symlink; refusing")
    if target is not None and not target.exists() and target.parent.is_dir():
        try:
            has_existing_files = any(target.parent.iterdir())
        except OSError:
            has_existing_files = True
        if has_existing_files:
            refusals.append("import target directory contains existing user files; refusing overwrite")
    same_source = recorded.get(source.relative_path) == source_sha256
    if refusals:
        status = "refused"
    elif same_source and target is not None and target.is_file():
        # Never rewrite an unchanged source, even if an operator customized the
        # imported document after the previous apply.
        status = "unchanged"
    elif target is not None and target.exists():
        if prior_entry is None or str(prior_entry.get("target", "")) != target_rel:
            refusals.append("import target already exists and is not owned by this source; refusing overwrite")
        else:
            expected = str(prior_entry.get("target_sha256", ""))
            if not expected or not target.is_file() or _sha256_file(target) != expected:
                refusals.append("import target has local modifications; refusing overwrite")
        status = "refused" if refusals else "planned"
    else:
        status = "planned"
    return RuleImportItem(
        slug=slug,
        source_relative_path=source.relative_path,
        format_name=source.format_name,
        source_sha256=source_sha256,
        byte_count=len(raw),
        target_relative_path=target_rel,
        status=status,
        refusal_reasons=tuple(refusals),
        description=description,
        body=body,
    )


def _read_contained_source(repo_root: Path, relative_path: str) -> bytes:
    """Read a source only when every below-root component is non-symlink."""
    root = repo_root.resolve()
    current = root
    rel = Path(relative_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise ExternalRuleImportError(
            f"rule source path is not a relative allowed path; refusing: {relative_path}"
        )
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ExternalRuleImportError(
                f"rule source path component is a symlink; refusing: {relative_path}"
            )
    resolved = current.resolve()
    if resolved != root and root not in resolved.parents:
        raise ExternalRuleImportError(
            f"rule source escapes the repository root; refusing: {relative_path}"
        )
    if not resolved.is_file():
        raise ExternalRuleImportError(f"rule source is not a regular file: {relative_path}")
    try:
        size = resolved.stat().st_size
    except OSError as exc:
        raise ExternalRuleImportError(f"rule source cannot be inspected; refusing: {relative_path}") from exc
    if size > MAX_SOURCE_BYTES:
        raise ExternalRuleImportError(
            f"rule source exceeds {MAX_SOURCE_BYTES} bytes: {relative_path}"
        )
    try:
        with resolved.open("rb") as handle:
            data = handle.read(MAX_SOURCE_BYTES + 1)
    except OSError as exc:
        raise ExternalRuleImportError(f"rule source cannot be read; refusing: {relative_path}") from exc
    if len(data) > MAX_SOURCE_BYTES:
        raise ExternalRuleImportError(
            f"rule source exceeds {MAX_SOURCE_BYTES} bytes: {relative_path}"
        )
    return data


def _slug_for(relative_path: str, sha256: str, used_slugs: set[str]) -> str:
    stem = Path(relative_path).stem or Path(relative_path).name
    base = _SLUG_SANITIZE.sub("-", stem.lower()).strip("-") or "rule"
    slug = base[:MAX_SLUG_CHARS]
    suffix_width = 8
    while slug in used_slugs:
        slug = f"{base[: MAX_SLUG_CHARS - suffix_width - 1]}-{sha256[:suffix_width]}"
        suffix_width += 4
        if suffix_width > len(sha256):
            slug = f"{slug}-x"
    return slug


def _describe(format_name: RuleFormat, relative_path: str, text: str) -> tuple[str, str]:
    body = text
    description = ""
    if format_name == "cursor-mdc":
        frontmatter, remainder = _split_frontmatter(text)
        for line in frontmatter.splitlines():
            match = _MDC_KEY.match(line.strip())
            if match and match.group(1) == "description":
                description = match.group(2).strip().strip("\"'")
        body = remainder if remainder.strip() else text
    if not description:
        for line in body.splitlines():
            stripped = line.strip().lstrip("#").strip()
            if stripped:
                description = stripped
                break
    label = {
        "cursorrules": "Cursor rules",
        "cursor-mdc": "Cursor MDC rule",
        "clinerules": "Cline rules",
        "windsurfrules": "Windsurf rules",
        "copilot-instructions": "Copilot instructions",
    }[format_name]
    description = f"[imported {label}] {description}"[:MAX_DESCRIPTION_CHARS].rstrip()
    fallback = f"[imported {label}] {relative_path}"[:MAX_DESCRIPTION_CHARS].rstrip()
    return (description or fallback, body)


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split a valid leading MDC frontmatter block without eating prose."""
    if not text.startswith("---"):
        return ("", text)
    closing = text.find("\n---", 3)
    if closing < 0:
        return ("", text)
    frontmatter = text[3:closing]
    inner_lines = [line for line in frontmatter.splitlines() if line.strip()]
    if not inner_lines or not all(_FRONTMATTER_LINE.match(line.strip()) for line in inner_lines):
        return ("", text)
    remainder = text[closing + 4 :]
    if remainder.startswith(("\n", "\r")):
        remainder = remainder[1:]
    return (frontmatter, remainder)


def _render_skill_document(item: RuleImportItem) -> str:
    quoted_description = json.dumps(item.description, ensure_ascii=False)
    quoted_source = json.dumps(item.source_relative_path, ensure_ascii=False)
    return (
        "---\n"
        f"name: {IMPORTED_NAME_PREFIX}{item.slug}\n"
        f"description: {quoted_description}\n"
        "metadata:\n"
        "  omj:\n"
        "    imported:\n"
        f"      format: {item.format_name}\n"
        f"      source: {quoted_source}\n"
        f"      source_sha256: {item.source_sha256}\n"
        "---\n\n"
        f"# Imported rule: {item.slug}\n\n"
        f"{EXTERNAL_RULE_IMPORT_CLAIM_BOUNDARY}\n\n"
        "The content below was imported verbatim from "
        f"`{item.source_relative_path}` and is maintained there; re-run "
        "`omj rules-import --apply` after the source changes.\n\n"
        "---\n\n"
        f"{item.body.rstrip()}\n"
    )


def _normalize_scan_text(value: str) -> str:
    return unicodedata.normalize("NFKC", value).translate(
        {ord(char): None for char in "\u200b\u200c\u200d\ufeff"}
    )


def _is_secret_value_shaped(value: str) -> bool:
    if (
        _COMMON_SECRET_PREFIX.search(value)
        or _PLATFORM_SECRET_PREFIX.search(value)
        or _AWS_ACCESS_KEY.search(value)
        or _GOOGLE_API_KEY.search(value)
        or _PRIVATE_KEY.search(value)
        or _JWT.search(value)
        or _AUTH_URL.search(value)
    ):
        return True
    assignment = _SECRET_ASSIGNMENT.search(value)
    if assignment is None:
        return False
    candidate = assignment.group(1).strip()
    return _PLACEHOLDER_VALUE.fullmatch(candidate) is None


def _destination_identity(path: Path) -> str:
    return str(path.expanduser().resolve(strict=False))


def _validate_destination_root(path: Path, *, label: str) -> None:
    candidate = path.expanduser()
    if not candidate.is_absolute():
        candidate = Path.cwd() / candidate
    current = Path(candidate.anchor)
    for part in candidate.parts[1:]:
        current /= part
        if current.is_symlink():
            raise ExternalRuleImportError(f"{label} contains a symlink component; refusing")
    if candidate.exists() and not candidate.is_dir():
        raise ExternalRuleImportError(f"{label} is not a directory; refusing")


def _manifest_snapshot(path: Path) -> str:
    if path.is_symlink():
        raise ExternalRuleImportError("import manifest path is a symlink; refusing")
    if not path.exists():
        return ""
    if not path.is_file():
        raise ExternalRuleImportError("import manifest path is not a regular file; refusing")
    try:
        return _sha256_file(path)
    except OSError as exc:
        raise ExternalRuleImportError(f"cannot read import manifest: {exc}") from exc


def _assert_target_snapshot(target: Path, expected: str, *, slug: str) -> None:
    if expected == _MISSING_TARGET:
        if target.exists() or target.is_symlink():
            raise ExternalRuleImportError(f"prepared target changed before apply: {slug}")
        return
    if expected == "__unreadable__" or not target.is_file():
        raise ExternalRuleImportError(f"prepared target is unreadable before apply: {slug}")
    try:
        actual = _sha256_file(target)
    except OSError as exc:
        raise ExternalRuleImportError(f"prepared target cannot be read before apply: {slug}") from exc
    if actual != expected:
        raise ExternalRuleImportError(f"prepared target changed before apply: {slug}")


def _assert_write_slot(target: Path) -> None:
    parent = target.parent
    if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
        raise ExternalRuleImportError("import target parent is unsafe; refusing")


def _target_path(skills_dir: Path, target_relative_path: str) -> Path | None:
    """Validate an imported target path without following symlink components."""
    rel = Path(target_relative_path)
    if rel.is_absolute() or ".." in rel.parts:
        return None
    expected_prefix = (IMPORTED_CATEGORY_DIR,)
    if len(rel.parts) != 3 or rel.parts[:1] != expected_prefix or rel.parts[-1] != "SKILL.md":
        return None
    current = skills_dir
    for index, part in enumerate(rel.parts):
        current = current / part
        if current.is_symlink():
            return None
        if index < len(rel.parts) - 1 and current.exists() and not current.is_dir():
            return None
    return current


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dedupe_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_source: dict[str, dict[str, Any]] = {}
    for entry in entries:
        source = str(entry.get("source", ""))
        if source:
            by_source[source] = entry
    return list(by_source.values())


__all__ = [
    "EXTERNAL_RULE_IMPORT_CLAIM_BOUNDARY",
    "EXTERNAL_RULE_IMPORT_SCHEMA_VERSION",
    "IMPORTED_CATEGORY_DIR",
    "IMPORTED_NAME_PREFIX",
    "IMPORTED_SKILLS_DIR_NAME",
    "IMPORT_MANIFEST_FILE",
    "MAX_DESCRIPTION_CHARS",
    "MAX_IMPORT_SOURCES",
    "MAX_SLUG_CHARS",
    "MAX_SOURCE_BYTES",
    "DiscoveredRuleSource",
    "ExternalRuleImportError",
    "RuleImportItem",
    "apply_rule_import",
    "discover_rule_sources",
    "import_manifest_path",
    "plan_rule_import",
    "public_plan",
]
