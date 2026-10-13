"""Copy-only host boundaries for portable Agent Skills projection.

These rows describe destination layout and source-assessed caveats only.  A
successful copy is not evidence that a host discovered, loaded, or executed a
skill.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import PurePosixPath
from typing import TypedDict

from .catalog import installable_skill_names, portable_skill_names, portability_for_skill
from .packaging import builtin_skill_reference_templates
from .render import (
    SkillReferenceTemplate,
    SkillTemplate,
    portable_procedure_reference_templates,
    portable_workflow_registry_reference,
    router_skill,
    workflow_skill,
)


@dataclass(frozen=True)
class HostAdapter:
    host: str
    repo_path: str
    user_path: str
    evidence: str = "docs/AGENT-SKILLS.md#host-support-matrix"
    caveat: str = ""
    transform: str = "copy-only"


HOST_ADAPTERS = (
    HostAdapter("cursor", ".agents/skills", ".agents/skills", caveat="User-scope scanning not independently verified."),
    HostAdapter("claude", ".claude/skills", ".claude/skills", caveat="Historical upstream OMH repo discovery observed in Claude Code 2.1.270, 2026-09-13; OMJ repo discovery not_observed; not workflow execution."),
    HostAdapter("codex", ".agents/skills", ".agents/skills"),
    HostAdapter("opencode", ".agents/skills", ".agents/skills", caveat="Skill tool is permission-gated."),
    HostAdapter("openclaw", ".agents/skills", ".agents/skills", caveat="Custom OPENCLAW_STATE_DIR skips the standard user path; workspace skills can take precedence."),
    HostAdapter("pi", ".agents/skills", ".agents/skills", caveat="Trusted projects only; first duplicate name wins."),
)


class HostAdapterManifest(TypedDict):
    schema_version: str
    host: str
    targets: dict[str, str]
    transform: str
    evidence: str
    caveat: str
    source: str
    source_digest: str
    digest_format: str
    files: dict[str, str]
    skills: list[str]
    source_path: str
    portability: dict[str, str]


def host_adapter(host: str) -> HostAdapter:
    for adapter in HOST_ADAPTERS:
        if adapter.host == host:
            return adapter
    raise ValueError(f"Unknown Agent Skills host: {host}")


def checksum_inventory(hashes: dict[str, str]) -> str:
    """Return a stable SHA256SUMS-compatible inventory with a final LF."""
    return "".join(f"{digest}  {path}\n" for path, digest in sorted(hashes.items()))


def host_adapter_manifest(host: str, files: dict[str, str], *, source: str = "agent-skills") -> HostAdapterManifest:
    adapter = host_adapter(host)
    if (
        not isinstance(source, str)
        or not source
        or PurePosixPath(source).is_absolute()
        or any(part in {"", ".", ".."} for part in source.split("/"))
        or any(char in source for char in "\\\r\n\0")
    ):
        raise ValueError(f"Unsafe Agent Skills source path: {source!r}")
    hashes = {
        path: hashlib.sha256(content.encode("utf-8")).hexdigest()
        for path, content in sorted(files.items())
    }
    return {
        "schema_version": "omj_host_adapter/v1",
        "host": adapter.host,
        "targets": {"repo": adapter.repo_path, "user": adapter.user_path},
        "transform": adapter.transform,
        "evidence": adapter.evidence,
        "caveat": adapter.caveat,
        "source": "agent-skills",
        "source_path": source,
        "portability": {name: portability_for_skill(name) for name in installable_skill_names()},
        "source_digest": hashlib.sha256(checksum_inventory(hashes).encode("utf-8")).hexdigest(),
        "digest_format": "sha256(sorted '<file-sha256>  <relative-posix-path>\\n' UTF-8 inventory)",
        "files": hashes,
        "skills": sorted({path.split("/", 1)[0] for path in files}),
    }


def portable_skill_name(canonical_name: str) -> str:
    """Return the collision-resistant portable folder/frontmatter name.

    Membership is read from the one canonical catalog producer
    (``omj.skills.catalog.installable_skill_names``); this module never
    keeps its own duplicated skill-name list.
    """
    if canonical_name not in installable_skill_names():
        raise ValueError(f"Portable producer received unknown skill: {canonical_name}")
    return "omj" if canonical_name == "oh-my-jeo" else f"omj-{canonical_name}"




def agent_skill_templates() -> list[SkillTemplate]:
    """Render only explicitly reviewed portable workflows from structured data."""
    return [
        SkillTemplate(portable_skill_name(name), (router_skill(portable=True) if name == "oh-my-jeo" else workflow_skill(name, portable=True)).content)
        for name in portable_skill_names()
    ]


def agent_skill_reference_templates() -> list[SkillReferenceTemplate]:
    """Package reviewed methods and preserve unchanged historical provenance."""
    names = set(portable_skill_names())
    native = [template for template in builtin_skill_reference_templates() if template.skill_name in names]
    rows = [
        "# Native and Historical Provenance", "",
        "These native contracts and historical source methods are non-operative provenance, not executable portable instructions.", "",
        "Native runtime tools, installers, roles, and hooks described below do not become prerequisites or host instructions. "
        "Raw source-pinned methods retain their exact bytes and historical attribution. Current portable instructions live in the reviewed SKILL.md files and their explicitly linked source-owned procedural guidance.", "",
        "## Reviewed Native and Portable Inventory", "",
    ]
    for name in installable_skill_names():
        classification = portability_for_skill(name)
        rows.append(f"- `{name}`: `{classification}`; {'excluded from portable output' if classification == 'hermes-only' else 'included as ' + portable_skill_name(name)}.")
    rows.extend(("", "## Preserved Reference Inventory", ""))
    for template in native:
        folder = portable_skill_name(template.skill_name)
        path = f"../../{folder}/{template.relative_path}"
        digest = hashlib.sha256(template.content.encode('utf-8')).hexdigest()
        rows.append(f"- [{folder}/{template.relative_path}]({path}) — SHA256 `{digest}`; native or historical provenance only.")
    provenance = SkillReferenceTemplate("oh-my-jeo", "references/native-provenance.md", "\n".join(rows) + "\n")
    return [
        SkillReferenceTemplate(portable_skill_name(template.skill_name), template.relative_path, template.content)
        for template in (*native, provenance, portable_workflow_registry_reference(), *portable_procedure_reference_templates())
    ]
