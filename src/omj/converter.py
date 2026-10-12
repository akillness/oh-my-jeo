from __future__ import annotations

import json
import re
from pathlib import Path

from .skill_pack import DESCRIPTIONS, SkillReferenceTemplate, SkillTemplate
from .skills.catalog import omj_description

FRONTMATTER_RE = re.compile(r"^---\n(?P<meta>.*?)\n---\n(?P<body>.*)$", re.DOTALL)
_SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")

# Only labels emitted by known source producers are canonicalized. Custom labels
# remain custom identities; broad prefix stripping would silently rename them.
KNOWN_SOURCE_ALIASES = {
    "ulw-work": "ultrawork",
    "ulw-interview": "deep-interview",
    "omh-decide": "plan",
}


def extract_name(raw: str, fallback: str) -> str:
    match = FRONTMATTER_RE.match(raw)
    rendered = fallback
    if match:
        for line in match.group("meta").splitlines():
            if line.startswith("name:"):
                rendered = line.split(":", 1)[1].strip().strip("'\"") or fallback
                break
    return KNOWN_SOURCE_ALIASES.get(rendered, rendered)


def _validate_name(name: str, *, source: Path | None = None) -> str:
    if not _SAFE_NAME.fullmatch(name):
        suffix = f" from {source}" if source is not None else ""
        raise ValueError(f"unsafe skill identity{suffix}: {name!r}")
    return name


def convert_skill(raw: str, fallback_name: str) -> SkillTemplate:
    name = _validate_name(extract_name(raw, fallback_name))
    description = DESCRIPTIONS.get(name, omj_description(f"Hermes workflow skill for {name}."))
    content = _replace_frontmatter_description(raw, name=name, description=description).rstrip() + f"""

## Hermes Compatibility Contract

This skill was imported by `omj` from a local skill source.

- Keep the upstream workflow intent, but adapt runtime behavior to Hermes Agent.
- Do not require runtime features that Hermes Agent does not expose.
- Use Hermes `skills_list`, `skill_view`, file tools, terminal tools, and Hermes delegation when available.
"""
    return SkillTemplate(name=name, content=content + "\n")


def _replace_frontmatter_description(raw: str, *, name: str, description: str) -> str:
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return f"---\nname: {name}\ndescription: {description}\n---\n\n{raw}"
    lines = match.group("meta").splitlines()
    output: list[str] = []
    saw_name = False
    saw_description = False
    for line in lines:
        if line.startswith("name:"):
            output.append(f"name: {name}")
            saw_name = True
        elif line.startswith("description:"):
            output.append(f"description: {description}")
            saw_description = True
        else:
            output.append(line)
    if not saw_name:
        output.insert(0, f"name: {name}")
    if not saw_description:
        output.insert(1, f"description: {description}")
    return "---\n" + "\n".join(output) + "\n---\n" + match.group("body")


def _inside_nested_repository(path: Path, source_dir: Path, memo: dict[Path, bool], *, exempt: Path) -> bool:
    for parent in path.parents:
        if parent == source_dir:
            return False
        if parent not in memo:
            memo[parent] = parent != exempt and (parent / ".git").exists()
        if memo[parent]:
            return True
    return False


def discover_skill_files(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        raise FileNotFoundError(f"source does not exist: {source_dir}")
    source_dir = source_dir.expanduser()
    # The repository root can contain generated portable projections and managed
    # outputs. Explicitly selected roots still work; only descendants are filtered.
    excluded = {".git", ".omc", ".omh", ".omj", "agent-skills", ".agents"}
    claude_mirror = source_dir / ".claude" / "skills"
    owned_paths: set[Path] = set()
    for manifest_name in ("skills-manifest.json", "agent-skills-manifest.json"):
        manifest_path = claude_mirror / manifest_name
        if not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            files = manifest.get("files", {}) if isinstance(manifest, dict) else {}
            if isinstance(files, dict):
                owned_paths.update(claude_mirror / str(value) for value in files)
            owned_paths.add(manifest_path)
        except (OSError, ValueError, TypeError):
            # An invalid manifest is not authority to exclude neighboring custom skills.
            continue
    nested: dict[Path, bool] = {}
    candidates: list[Path] = []
    for path in source_dir.rglob("SKILL.md"):
        relative = path.relative_to(source_dir)
        if excluded.intersection(relative.parts):
            continue
        if path in owned_paths or _inside_nested_repository(path, source_dir, nested, exempt=claude_mirror):
            continue
        # Reject symlinks inside the explicitly selected source root. Ancestors
        # above that root (for example /tmp -> /private/tmp on macOS) are not
        # source-owned and must not make ordinary files fail preflight.
        relative_parts = path.relative_to(source_dir).parts
        source_parents = [source_dir.joinpath(*relative_parts[:index]) for index in range(1, len(relative_parts))]
        if path.is_symlink() or any(parent.is_symlink() for parent in source_parents):
            raise ValueError(f"source skill path is a symlink: {path}")
        candidates.append(path)

    # Prefer native Hermes `skills/` over portable projections. Equal-priority
    # duplicate identities are only accepted when the payload is byte-identical.
    priority = {"skills": 0, ".claude": 1}
    selected: dict[str, Path] = {}
    for path in sorted(candidates):
        raw = path.read_text(encoding="utf-8")
        name = _validate_name(extract_name(raw, path.parent.name), source=path)
        current = selected.get(name)
        if current is None:
            selected[name] = path
            continue
        current_root = current.relative_to(source_dir).parts[0]
        candidate_root = path.relative_to(source_dir).parts[0]
        current_priority = priority.get(current_root, 2)
        candidate_priority = priority.get(candidate_root, 2)
        if current_priority == candidate_priority:
            if current.read_bytes() != path.read_bytes():
                raise ValueError(f"duplicate skill identity {name!r}: {current} and {path}")
            continue
        if candidate_priority < current_priority:
            selected[name] = path
    return sorted(selected.values())


def convert_from_dir(source_dir: Path) -> list[SkillTemplate]:
    return [
        convert_skill(path.read_text(encoding="utf-8"), path.parent.name)
        for path in discover_skill_files(source_dir)
    ]


def convert_references_from_dir(source_dir: Path) -> list[SkillReferenceTemplate]:
    templates: list[SkillReferenceTemplate] = []
    seen: dict[tuple[str, str], Path] = {}
    for skill_file in discover_skill_files(source_dir):
        raw = skill_file.read_text(encoding="utf-8")
        skill_name = _validate_name(extract_name(raw, skill_file.parent.name), source=skill_file)
        references_dir = skill_file.parent / "references"
        if not references_dir.is_dir():
            continue
        for reference_file in sorted(references_dir.rglob("*.md")):
            if ".git" in reference_file.parts:
                continue
            reference_parts = reference_file.relative_to(skill_file.parent).parts
            reference_parents = [skill_file.parent.joinpath(*reference_parts[:index]) for index in range(1, len(reference_parts))]
            if reference_file.is_symlink() or any(parent.is_symlink() for parent in reference_parents):
                raise ValueError(f"source reference path is a symlink: {reference_file}")
            relative = reference_file.relative_to(skill_file.parent).as_posix()
            key = (skill_name, relative)
            previous = seen.get(key)
            if previous is not None:
                if previous.read_bytes() != reference_file.read_bytes():
                    raise ValueError(f"duplicate reference target {skill_name}/{relative}: {previous} and {reference_file}")
                continue
            seen[key] = reference_file
            templates.append(
                SkillReferenceTemplate(skill_name, relative, reference_file.read_text(encoding="utf-8"))
            )
    return templates
