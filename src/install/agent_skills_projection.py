"""Catalog-generated portable Agent Skills projection.

The producer renders from packaged OMJ catalog data; it never discovers or
copies a source checkout.  Installation is copy-only and reports only local
receipt state, not native host discovery or execution.
"""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re
import tempfile
from typing import Any

from ..hashutil import sha256_file, sha256_text

MANIFEST_NAME = ".omj-agent-skills-manifest.json"
SCHEMA_VERSION = "omj_agent_skills_projection/v1"
CLAIM_BOUNDARY = (
    "Generated local guidance only. Fresh files do not prove host discovery, "
    "selection, loading, execution, review, CI, or merge."
)


def agent_skill_files() -> dict[str, str]:
    """Return exact packaged portable files keyed by POSIX relative path."""
    from ..skills.catalog import portable_skill_names
    from ..skills.host_adapters import agent_skill_reference_templates, agent_skill_templates

    templates = agent_skill_templates()
    references = agent_skill_reference_templates()
    files = {f"{template.name}/SKILL.md": template.content for template in templates}
    files.update(
        {
            f"{template.skill_name}/{template.relative_path}": template.content
            for template in references
        }
    )
    # Membership comes from the one canonical catalog; a mismatch here means
    # the portable producer and the catalog producer drifted apart.
    expected = len(portable_skill_names())
    if len(templates) != expected:
        raise ValueError(f"Portable producer catalog drift: expected {expected} installable skills, got {len(templates)}")
    if not files:
        raise ValueError("Portable Agent Skills producer returned no files")
    for relative in files:
        _validate_relative(relative)
    return dict(sorted(files.items()))


def agent_skills_targets(scope: str, *, host: str, base: Path | None = None) -> tuple[Path, None]:
    """Resolve one host-selected target without probing native host state."""
    from ..skills.host_adapters import host_adapter

    if scope not in {"project", "user"}:
        raise ValueError("Agent Skills scope must be project or user")
    adapter = host_adapter(host)
    root = (Path.home() if scope == "user" else (base or Path.cwd())).resolve()
    relative = adapter.user_path if scope == "user" else adapter.repo_path
    return root / relative, None


def _validate_relative(relative: str) -> None:
    path = PurePosixPath(relative)
    if (
        path.is_absolute()
        or "\\" in relative
        or ":" in relative
        or any(part in {"", ".", ".."} for part in relative.split("/"))
    ):
        raise ValueError(f"Unsafe Agent Skills manifest path: {relative!r}")


def _checked_path(root: Path, relative: str) -> Path:
    _validate_relative(relative)
    root = root.absolute()
    # A symlink in the authorized root or any parent would redirect writes.
    for item in (root.parent, root):
        if item.is_symlink():
            raise ValueError(f"Agent Skills refuses symlink destination: {item}")
    candidate = root / relative
    current = root
    for part in PurePosixPath(relative).parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Agent Skills refuses symlink destination: {current}")
    if candidate.is_symlink():
        raise ValueError(f"Agent Skills refuses symlink destination: {candidate}")
    return candidate


def _read_manifest(root: Path) -> dict[str, Any] | None:
    path = _checked_path(root, MANIFEST_NAME)
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError(f"Invalid Agent Skills manifest: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid Agent Skills manifest: {path}") from exc
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") != SCHEMA_VERSION
        or not isinstance(payload.get("files"), dict)
        or not isinstance(payload.get("catalog_revision"), str)
        or not isinstance(payload.get("target_dirs"), list)
        or not all(isinstance(item, str) for item in payload["target_dirs"])
    ):
        raise ValueError(f"Invalid Agent Skills manifest: {path}")
    for relative, digest in payload["files"].items():
        if not isinstance(relative, str):
            raise ValueError(f"Invalid Agent Skills manifest path: {relative!r}")
        _checked_path(root, relative)
        if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
            raise ValueError(f"Invalid Agent Skills digest: {relative}")
    return payload


def agent_skills_manifest(files: dict[str, str], *, roots: tuple[Path, ...] = ()) -> dict[str, Any]:
    hashes = {name: sha256_text(content) for name, content in sorted(files.items())}
    revision = sha256_text("\n".join(f"{name}\0{digest}" for name, digest in hashes.items()))
    return {
        "schema_version": SCHEMA_VERSION,
        "catalog_revision": revision,
        "target_dirs": [str(root.absolute()) for root in roots] or ["."],
        "files": hashes,
    }


def _roots_status(target: Path, mirror: Path | None) -> tuple[Path, ...]:
    roots = (target.absolute(),) if mirror is None else (target.absolute(), mirror.absolute())
    if len(set(roots)) != len(roots):
        raise ValueError("Agent Skills target roots must be distinct")
    return roots


def agent_skills_status(target: Path, *, mirror: Path | None = None) -> dict[str, Any]:
    roots = _roots_status(target, mirror)
    files = agent_skill_files()
    expected = agent_skills_manifest(files, roots=roots)
    modified: list[str] = []
    states: list[str] = []
    installed_revisions: list[str] = []
    for index, root in enumerate(roots):
        manifest = _read_manifest(root)
        installed_revisions.append(manifest["catalog_revision"] if manifest else "")
        if manifest is None:
            states.append("missing")
            continue
        for relative, digest in manifest["files"].items():
            path = _checked_path(root, relative)
            if not path.is_file() or sha256_file(path) != digest:
                modified.append(relative if index == 0 else f"mirror:{relative}")
        # Static wrappers bind this one-root marker to the directory that owns
        # the receipt. All other receipt fields still require exact equality.
        current = (
            {**manifest, "target_dirs": [str(root)]}
            if len(roots) == 1 and manifest["target_dirs"] == ["."]
            else manifest
        )
        matches = current == expected and all(
            _checked_path(root, relative).is_file() and sha256_file(root / relative) == digest
            for relative, digest in expected["files"].items()
        )
        states.append("fresh" if matches else "stale")
    projection = "missing" if "missing" in states else "stale" if "stale" in states else "fresh"
    return {
        "schema_version": SCHEMA_VERSION,
        "catalog_revision": expected["catalog_revision"],
        "installed_revisions": installed_revisions,
        "target_dirs": [str(root) for root in roots],
        "projection": projection,
        "drift": "locally_modified" if modified else "unknown" if "missing" in states else "clean",
        "locally_modified": sorted(modified),
        "next_action": (
            "Review or back up locally-modified files; rerun the same install command to replace them."
            if modified
            else "Rerun the same install command to generate the current catalog."
            if projection != "fresh"
            else "No repair needed; host use remains not_observed."
        ),
        "host_observation": "not_observed",
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
        handle.flush()
    try:
        temporary.replace(path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise


def install_agent_skills(target: Path, *, mirror: Path | None = None) -> dict[str, Any]:
    roots = _roots_status(target, mirror)
    files = agent_skill_files()
    manifests = [_read_manifest(root) for root in roots]

    # Complete preflight for every destination before the first write.
    for root, previous in zip(roots, manifests):
        previous_files = previous.get("files", {}) if previous else {}
        if not isinstance(previous_files, dict):
            raise ValueError(f"Invalid Agent Skills manifest: {root}")
        for relative, content in files.items():
            path = _checked_path(root, relative)
            if path.exists():
                if relative not in previous_files:
                    raise ValueError(f"Agent Skills refuses unowned file collision: {path}")
                if not path.is_file() or sha256_file(path) != previous_files[relative]:
                    raise ValueError(f"Agent Skills refuses modified owned file: {path}")
        receipt = _checked_path(root, MANIFEST_NAME)
        if receipt.exists() and not receipt.is_file():
            raise ValueError(f"Agent Skills refuses non-file receipt: {receipt}")
        # Retired owned files are pruned only when their observed bytes still match.
        for relative, digest in previous_files.items():
            if relative not in files:
                path = _checked_path(root, relative)
                if path.exists() and (not path.is_file() or sha256_file(path) != digest):
                    raise ValueError(f"Agent Skills refuses modified retired file: {path}")

    manifest = agent_skills_manifest(files, roots=roots)
    manifest_text = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    for root, previous in zip(roots, manifests):
        previous_files = previous.get("files", {}) if previous else {}
        for relative, content in files.items():
            _atomic_write(_checked_path(root, relative), content.encode("utf-8"))
        for relative in set(previous_files) - set(files):
            path = _checked_path(root, relative)
            if path.exists():
                path.unlink()
            parent = path.parent
            while parent != root and parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
        _atomic_write(_checked_path(root, MANIFEST_NAME), manifest_text)
    return agent_skills_status(target, mirror=mirror)
