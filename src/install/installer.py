from __future__ import annotations

import hashlib
import os
import shutil
import sys
from pathlib import Path
from typing import Iterable

from ..converter import convert_from_dir, convert_references_from_dir
from ..core.errors import OmjError
from ..hashutil import sha256_file
from ..local_store import atomic_write_bytes, read_json_object_result
from ..manifest import (
    IMPORTED_SKILLS_DIR_NAME,
    local_modifications,
    manifest_owned_files,
    new_manifest,
    read_manifest,
    skill_records,
    write_manifest,
)
from ..paths import OmjPaths
from ..plugin_pack import PLUGIN_MANAGED_MANIFEST, PLUGIN_SCHEMA_VERSION, read_plugin_manifest
from ..profiles.team import TEAM_PROFILE_SCHEMA_VERSION
from ..skill_pack import (
    SkillReferenceTemplate,
    SkillTemplate,
    builtin_skill_reference_templates,
    builtin_skill_templates,
)
from ..skills.catalog import CORE_PROFILE_SKILLS, CORE_SKILLS, builtin_definitions


SKILL_PROFILES = ("core", "full")
DEFAULT_SKILL_PROFILE = "full"
CORE_SKILL_PROFILE = "core"
NON_DESTRUCTIVE_DEFAULT_NOTE = (
    "omj setup, install, and update never delete installed skills; use explicit reconcile to shrink to core."
)
SKILL_PROFILE_STATE_SCHEMA_VERSION = "omj_skill_profile_state/v1"
SKILL_PROFILE_RECONCILE_SCHEMA_VERSION = "omj_skill_profile_reconcile/v1"
SKILL_PROFILE_RECONCILE_COMMAND = "omj skill-profile reconcile --to core"
SKILL_PROFILE_STATUS_COMMAND = "omj skill-profile status"


def _definition_categories() -> dict[str, str]:
    return {
        str(definition.name): str(definition.category or "workflow")
        for definition in builtin_definitions()
    }


def skill_directory_name(canonical: str) -> str:
    return canonical


def skill_install_relative_dir(canonical: str) -> Path:
    """Managed install path; repository/tap projections remain flat."""
    category = _definition_categories().get(canonical, "workflow")
    return Path(category) / skill_directory_name(canonical)


def _source_relative_dir(canonical: str, source_dir: Path | None) -> Path:
    # Explicit imports are caller-scoped and retain their source identity/path.
    return Path(canonical) if source_dir is not None else skill_install_relative_dir(canonical)


def _target_file(skills_dir: Path, skill_name: str, relative: str, source_dir: Path | None) -> Path:
    return skills_dir / _source_relative_dir(skill_name, source_dir) / relative


def _manifest_describes(manifest: dict | None, skills_dir: Path) -> bool:
    if not manifest:
        return False
    recorded = manifest.get("skills_dir")
    if not recorded:
        return True
    try:
        return os.path.realpath(str(recorded)) == os.path.realpath(str(skills_dir))
    except OSError:
        return False


def _without_installed_at(payload: dict) -> dict:
    return {key: value for key, value in payload.items() if key != "installed_at"}


def _carry_installed_at_when_nothing_moved(previous: dict | None, current: dict) -> dict:
    carried = previous.get("installed_at") if isinstance(previous, dict) else None
    if not isinstance(carried, str) or not carried:
        return current
    if _without_installed_at(current) == _without_installed_at(previous):
        return {**current, "installed_at": carried}
    return current


def _template_payloads(
    templates: Iterable[SkillTemplate],
    references: Iterable[SkillReferenceTemplate],
    *,
    skills_dir: Path,
    source_dir: Path | None,
) -> tuple[dict[str, bytes], dict[str, str]]:
    payloads: dict[str, bytes] = {}
    names: dict[str, str] = {}
    for template in templates:
        relative = (_source_relative_dir(template.name, source_dir) / "SKILL.md").as_posix()
        if relative in payloads:
            raise OmjError(f"duplicate generated target: {relative}")
        payloads[relative] = template.content.encode("utf-8")
        names[relative] = template.name
    for template in references:
        relative = (_source_relative_dir(template.skill_name, source_dir) / template.relative_path).as_posix()
        if relative in payloads:
            raise OmjError(f"duplicate generated target: {relative}")
        payloads[relative] = template.content.encode("utf-8")
        names[relative] = template.skill_name
    return payloads, names


def _existing_unowned_conflicts(
    skills_dir: Path,
    payloads: dict[str, bytes],
    manifest: dict | None,
    *,
    source_dir: Path | None,
) -> list[str]:
    owned = manifest_owned_files(manifest)
    conflicts: set[str] = set()
    # Every generated destination is checked before the first write. Existing
    # unowned targets are never adopted, even when their bytes happen to match.
    for relative, expected in payloads.items():
        target = skills_dir / relative
        parts = Path(relative).parts
        unsafe_ancestor = False
        for index in range(len(parts)):
            ancestor = skills_dir.joinpath(*parts[:index])
            ancestor_relative = Path(*parts[:index]).as_posix()
            if ancestor.is_symlink():
                conflicts.add(f"symlink target ancestor: {ancestor_relative}")
                unsafe_ancestor = True
                break
            if ancestor.exists() and not ancestor.is_dir():
                conflicts.add(f"unowned non-directory target ancestor: {ancestor_relative}")
                unsafe_ancestor = True
                break
        if unsafe_ancestor:
            continue
        if target.is_symlink():
            conflicts.add(f"symlink target: {relative}")
        elif target.exists() and not target.is_file():
            conflicts.add(f"unowned non-file target: {relative}")
        elif target.exists():
            recorded = owned.get(relative)
            if recorded is None:
                conflicts.add(f"unowned target: {relative}")
            else:
                try:
                    if sha256_file(target) != recorded:
                        conflicts.add(f"modified owned file: {relative}")
                except OSError:
                    conflicts.add(f"unreadable owned file: {relative}")
    if source_dir is None:
        # Extras under a managed producer directory are conflicts. Independent
        # imported/custom roots are deliberately outside the producer allowlist.
        roots = {str(Path(relative).parent) for relative in payloads}
        for root in roots:
            directory = skills_dir / root
            if not directory.is_dir() or directory.is_symlink():
                continue
            for path in directory.rglob("*"):
                if not path.is_file() or path.is_symlink():
                    continue
                relative = path.relative_to(skills_dir).as_posix()
                if relative not in payloads and relative not in owned:
                    conflicts.add(f"unowned file: {relative}")
    # Legacy manifests only recorded SKILL.md. Validate known owned files but
    # do not infer ownership for newly introduced references.
    for relative in local_modifications(manifest, skills_dir):
        if relative in payloads:
            conflicts.add(f"modified owned file: {relative}")
    return sorted(conflicts)


def _profile_templates(
    all_templates: list[SkillTemplate],
    all_references: list[SkillReferenceTemplate],
    profile: str,
    manifest: dict | None,
    skills_dir: Path,
    *,
    source_dir: Path | None,
) -> tuple[list[SkillTemplate], list[SkillReferenceTemplate]]:
    if source_dir is not None or profile == "full":
        return all_templates, all_references
    if profile != "core":
        raise OmjError(f"unknown skill profile {profile!r}; choose one of {', '.join(SKILL_PROFILES)}")
    installed_names = {
        str(record.get("name"))
        for record in (manifest or {}).get("skills", [])
        if isinstance(record, dict) and record.get("name")
    }
    # Core controls additions, not refresh: previously installed full members
    # remain present and are refreshed from the current producer.
    names = set(CORE_PROFILE_SKILLS) | installed_names
    names &= {template.name for template in all_templates}
    selected = [template for template in all_templates if template.name in names]
    return selected, [reference for reference in all_references if reference.skill_name in names]


def _migrate_flat_payloads(
    skills_dir: Path,
    previous: dict | None,
    *,
    source_dir: Path | None,
) -> dict[str, list[str]]:
    if source_dir is not None or not previous:
        return {"removed": [], "retained": []}
    owned = manifest_owned_files(previous)
    removed: list[str] = []
    retained: list[str] = []
    for record in previous.get("skills", []):
        if not isinstance(record, dict):
            continue
        old = str(record.get("path", ""))
        parts = Path(old).parts
        if len(parts) != 2 or parts[-1] != "SKILL.md":
            continue
        name = str(record.get("name", ""))
        old_file = skills_dir / old
        new_file = skills_dir / skill_install_relative_dir(name) / "SKILL.md"
        if not old_file.is_file() or old_file.is_symlink() or not new_file.is_file():
            continue
        try:
            if sha256_file(old_file) != str(record.get("sha256", "")):
                retained.append(old)
                continue
        except OSError:
            retained.append(old)
            continue
        # Remove only verified producer payload. User extras/references survive.
        old_file.unlink()
        removed.append(old)
        old_root = old_file.parent
        for path in sorted(old_root.rglob("*"), reverse=True):
            if not path.is_file() or path.is_symlink():
                continue
            rel = path.relative_to(skills_dir).as_posix()
            if rel in owned and sha256_file(path) == owned[rel]:
                path.unlink()
                removed.append(rel)
        for directory in sorted([p for p in old_root.rglob("*") if p.is_dir()], reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass
        try:
            old_root.rmdir()
        except OSError:
            pass
    return {"removed": sorted(removed), "retained": sorted(retained)}


def _owned_records(
    skills_dir: Path,
    source: str,
    payloads: dict[str, bytes],
    names: dict[str, str],
) -> list:
    skill_paths = [relative for relative in payloads if Path(relative).name == "SKILL.md"]
    records = skill_records(skills_dir, source, owned_paths=skill_paths)
    by_name: dict[str, list[dict[str, str]]] = {}
    for relative, content in payloads.items():
        if Path(relative).name == "SKILL.md":
            continue
        by_name.setdefault(names[relative], []).append(
            {"path": relative, "sha256": hashlib.sha256(content).hexdigest()}
        )
    output = []
    for record in records:
        files = tuple(sorted(by_name.get(record.name, []), key=lambda item: item["path"]))
        output.append(type(record)(record.name, record.path, record.sha256, record.source, files))
    return output


def install_skill_pack(
    paths: OmjPaths,
    *,
    source: str = "builtin",
    source_dir: Path | None = None,
    force: bool = False,
    dry_run: bool = False,
    profile: str = DEFAULT_SKILL_PROFILE,
) -> dict:
    if profile not in SKILL_PROFILES:
        raise OmjError(f"unknown skill profile {profile!r}; choose one of {', '.join(SKILL_PROFILES)}")
    source_dir = source_dir.expanduser() if source_dir is not None else None
    all_templates = convert_from_dir(source_dir) if source_dir else builtin_skill_templates()
    all_references = convert_references_from_dir(source_dir) if source_dir else builtin_skill_reference_templates()
    manifest = read_manifest(paths.manifest_path)
    if manifest is not None and not _manifest_describes(manifest, paths.skills_dir):
        manifest = None
    templates, references = _profile_templates(
        all_templates, all_references, profile, manifest, paths.skills_dir, source_dir=source_dir
    )
    payloads, names = _template_payloads(templates, references, skills_dir=paths.skills_dir, source_dir=source_dir)
    conflicts = _existing_unowned_conflicts(paths.skills_dir, payloads, manifest, source_dir=source_dir)
    hard_conflicts = [
        conflict for conflict in conflicts if conflict.startswith(("unowned ", "symlink "))
    ]
    if hard_conflicts or (conflicts and not force):
        raise OmjError("install preflight conflicts: " + ", ".join(conflicts))
    if dry_run:
        return {
            "dry_run": True,
            "skills_dir": str(paths.skills_dir),
            "skills": sorted(set(names.values())),
            "source": source,
            "skill_profile": profile,
            "files": sorted(payloads),
            "conflicts": conflicts,
        }
    # All checks above complete before the first mutation. Every target writes
    # through the shared atomic helper (exclusive tmp file + rename), never a
    # raw write_bytes, so a crash mid-loop cannot leave a half-written file
    # and a pre-planted predictable tmp name cannot be hijacked.
    for relative, content in payloads.items():
        atomic_write_bytes(paths.skills_dir / relative, content)
    migration = _migrate_flat_payloads(paths.skills_dir, manifest, source_dir=source_dir)
    records = _owned_records(paths.skills_dir, source, payloads, names)
    manifest_data = new_manifest(source, paths.skills_dir, records)
    manifest_data["profile"] = profile
    manifest_data["requested_profile"] = profile
    manifest_data["skill_profile"] = profile
    manifest_data["flat_layout_skills_removed"] = migration["removed"]
    manifest_data["flat_layout_skills_retained"] = migration["retained"]
    manifest_data["installed_skill_count"] = len(records)
    manifest_data["skill_profile_state"] = skill_profile_state(paths.skills_dir, manifest_data)
    manifest_data = _carry_installed_at_when_nothing_moved(manifest, manifest_data)
    write_manifest(paths.manifest_path, manifest_data)
    return manifest_data


def installed_skill_directories(skills_dir: Path) -> list[Path]:
    found: list[Path] = []
    if not skills_dir.is_dir():
        return found
    for path in sorted(skills_dir.rglob("SKILL.md")):
        if path.is_symlink() or not path.is_file() or IMPORTED_SKILLS_DIR_NAME in path.relative_to(skills_dir).parts:
            continue
        found.append(path.parent)
    return found


def installed_skill_names(skills_dir: Path) -> list[str]:
    known = {template.name for template in builtin_skill_templates()}
    names: set[str] = set()
    for directory in installed_skill_directories(skills_dir):
        leaf = directory.name
        names.add(leaf if leaf in known else leaf)
    return sorted(names)


def skill_profile_state(skills_dir: Path, manifest: dict | None) -> dict:
    catalog_names = {template.name for template in builtin_skill_templates()}
    core_names = set(CORE_PROFILE_SKILLS) & catalog_names
    installed = installed_skill_names(skills_dir)
    installed_catalog = sorted(name for name in installed if name in catalog_names)
    full_only = sorted(set(installed_catalog) - core_names)
    if not installed_catalog:
        effective = "none"
    elif catalog_names.issubset(installed_catalog):
        effective = "full"
    elif not full_only:
        effective = "core"
    else:
        effective = "mixed"
    requested = str((manifest or {}).get("requested_profile") or (manifest or {}).get("profile") or "")
    return {
        "schema_version": SKILL_PROFILE_STATE_SCHEMA_VERSION,
        "requested_profile": requested,
        "effective_profile": effective,
        "matches_requested_profile": bool(requested) and effective == requested,
        "core_profile_skill_count": len(core_names),
        "full_profile_skill_count": len(catalog_names),
        "installed_skill_count": len(installed),
        "installed_catalog_skill_count": len(installed_catalog),
        "installed_skills": installed,
        "full_only_installed_skills": full_only,
        "retained_exception": bool(requested == "core" and full_only),
        "next_action": SKILL_PROFILE_RECONCILE_COMMAND if full_only else "",
    }


def _catalog_skill_files() -> dict[str, dict[str, bytes]]:
    expected: dict[str, dict[str, bytes]] = {}
    for template in builtin_skill_templates():
        expected.setdefault(template.name, {})["SKILL.md"] = template.content.encode("utf-8")
    for template in builtin_skill_reference_templates():
        expected.setdefault(template.skill_name, {})[template.relative_path] = template.content.encode("utf-8")
    return expected


def _installed_skill_dir(skills_dir: Path, name: str) -> Path | None:
    candidate = skills_dir / skill_install_relative_dir(name)
    if (candidate / "SKILL.md").is_file() and not candidate.is_symlink():
        return candidate
    flat = skills_dir / name
    if (flat / "SKILL.md").is_file() and not flat.is_symlink():
        return flat
    return None


def _reconcile_plan(skills_dir: Path, manifest: dict) -> dict:
    expected = _catalog_skill_files()
    core = set(CORE_PROFILE_SKILLS)
    managed = {str(record.get("name")) for record in manifest.get("skills", []) if isinstance(record, dict)}
    removable: list[str] = []
    retained: list[dict[str, str]] = []
    # Every name installed_skill_names() reports lands in exactly one bucket
    # below, so callers can rely on installed_skill_count == len(removable) +
    # len(retained) without recomputing membership themselves.
    for name in installed_skill_names(skills_dir):
        if name in core:
            retained.append({"name": name, "reason": "core profile floor skill; reconcile never removes it"})
            continue
        if name not in expected:
            retained.append({"name": name, "reason": "not an OMJ catalog skill"})
            continue
        if name not in managed:
            retained.append({"name": name, "reason": "no OMJ install-manifest record; not OMJ-managed"})
            continue
        directory = _installed_skill_dir(skills_dir, name)
        if directory is None:
            retained.append({"name": name, "reason": "installed skill directory could not be resolved"})
            continue
        actual: dict[str, bytes] = {}
        unsafe = False
        try:
            for path in sorted(directory.rglob("*")):
                if path.is_symlink():
                    unsafe = True
                    break
                if path.is_dir():
                    continue
                if not path.is_file():
                    unsafe = True
                    break
                actual[path.relative_to(directory).as_posix()] = path.read_bytes()
        except OSError:
            unsafe = True
        if unsafe or actual != expected[name]:
            retained.append({"name": name, "reason": "locally modified or unreadable managed content"})
            continue
        removable.append(name)
    return {"removable_skills": sorted(removable), "retained_skills": retained}


def skill_profile_report(paths: OmjPaths) -> dict:
    """Public ``omj skill-profile status`` payload for CoreIntegrator's CLI.

    ``reconcilable_skills``/``retained_skills`` are the plain skill names
    installed_skill_names() reports, partitioned by _reconcile_plan(); every
    installed skill lands in exactly one of the two, so
    profile_state.installed_skill_count == len(reconcilable_skills) +
    len(retained_skills) always holds.
    """
    manifest = read_manifest(paths.manifest_path)
    plan = _reconcile_plan(paths.skills_dir, manifest or {})
    return {
        "schema_version": SKILL_PROFILE_STATE_SCHEMA_VERSION,
        "skills_dir": str(paths.skills_dir),
        "manifest_path": str(paths.manifest_path),
        "installed": manifest is not None,
        "profile_state": skill_profile_state(paths.skills_dir, manifest),
        "reconcilable_skills": plan["removable_skills"],
        "retained_skills": sorted(item["name"] for item in plan["retained_skills"]),
    }


def reconcile_skill_profile(paths: OmjPaths, *, target_profile: str = CORE_SKILL_PROFILE, dry_run: bool = False) -> dict:
    if target_profile != CORE_SKILL_PROFILE:
        raise OmjError("skill profile reconcile only supports target profile 'core'")
    manifest = read_manifest(paths.manifest_path)
    if manifest is None:
        raise OmjError(f"no OMJ skill manifest at {paths.manifest_path}; run `omj setup` first")
    plan = _reconcile_plan(paths.skills_dir, manifest)
    retained_details = plan["retained_skills"]
    retained_paths: list[str] = []
    for item in retained_details:
        name = str(item.get("name", ""))
        record = next(
            (entry for entry in manifest.get("skills", []) if isinstance(entry, dict) and entry.get("name") == name),
            None,
        )
        retained_paths.append(str(record.get("path", name)) if isinstance(record, dict) else name)
    result = {
        "schema_version": SKILL_PROFILE_RECONCILE_SCHEMA_VERSION,
        "target_profile": target_profile,
        "dry_run": dry_run,
        "profile_state_before": skill_profile_state(paths.skills_dir, manifest),
        "retained": retained_details,
        "retained_skills": retained_paths,
    }
    if dry_run:
        result["would_remove"] = plan["removable_skills"]
        result["would_remove_skills"] = plan["removable_skills"]
        result["removed"] = []
        result["removed_skills"] = []
        return result
    removed: list[str] = []
    removed_prefixes: list[str] = []
    for name in plan["removable_skills"]:
        directory = _installed_skill_dir(paths.skills_dir, name)
        if directory is None:
            continue
        shutil.rmtree(directory)
        removed.append(name)
        removed_prefixes.append(directory.relative_to(paths.skills_dir).as_posix() + "/")
    updated = dict(manifest)
    updated["skills"] = [
        record
        for record in manifest.get("skills", [])
        if not isinstance(record, dict)
        or not any(str(record.get("path", "")).startswith(prefix) for prefix in removed_prefixes)
    ]
    if isinstance(manifest.get("owned_files"), dict):
        updated["owned_files"] = {
            relative: digest
            for relative, digest in manifest["owned_files"].items()
            if not any(str(relative).startswith(prefix) for prefix in removed_prefixes)
        }
    updated["profile"] = target_profile
    updated["requested_profile"] = target_profile
    updated["skill_profile"] = target_profile
    updated["installed_skill_count"] = len(updated["skills"])
    updated["reconciled_skills"] = removed
    updated["skill_profile_state"] = skill_profile_state(paths.skills_dir, updated)
    write_manifest(paths.manifest_path, updated)
    result["removed"] = removed
    result["removed_skills"] = removed
    result["profile_state_after"] = updated["skill_profile_state"]
    return result


def owned_resource_inventory(paths: OmjPaths) -> dict:
    manifest = read_manifest(paths.manifest_path)
    owned = manifest_owned_files(manifest)
    observed = []
    missing = []
    modified = []
    for relative, expected in sorted(owned.items()):
        path = paths.skills_dir / relative
        if not path.exists():
            missing.append(relative)
            continue
        try:
            actual = sha256_file(path)
        except OSError:
            modified.append(relative)
            continue
        observed.append(relative)
        if actual != expected:
            modified.append(relative)
    return {
        "schema_version": "omj_owned_resource_inventory/v1",
        "skills_dir": str(paths.skills_dir),
        "owned_files": sorted(owned),
        "observed_files": observed,
        "missing_files": missing,
        "modified_files": modified,
        "content_fresh": not missing and not modified,
    }


def content_freshness(paths: OmjPaths, *, source: str = "builtin") -> dict:
    inventory = owned_resource_inventory(paths)
    manifest = read_manifest(paths.manifest_path)
    return {
        "schema_version": "omj_content_freshness/v1",
        "source": source,
        "manifest_present": manifest is not None,
        "content_fresh": bool(inventory["content_fresh"]),
        "missing_files": inventory["missing_files"],
        "modified_files": inventory["modified_files"],
        "owned_file_count": len(inventory["owned_files"]),
    }


def uninstall_skill_pack(
    paths: OmjPaths,
    *,
    remove_files: bool = False,
    remove_all: bool = False,
    dry_run: bool = False,
    force: bool = False,
    remove_command_package: bool = False,
) -> dict:
    removed: list[str] = []
    would_remove: list[str] = []
    kept: list[dict[str, str]] = []
    if remove_all:
        _collect_removal(paths.hermes_plugin_dir, removed=removed, would_remove=would_remove, kept=kept, dry_run=dry_run, force=force, managed_plugin=True)
        for team_file in _managed_team_profile_files(paths):
            _collect_removal(team_file, removed=removed, would_remove=would_remove, kept=kept, dry_run=dry_run, force=force)
    if remove_files or remove_all:
        _collect_removal(paths.omj_home, removed=removed, would_remove=would_remove, kept=kept, dry_run=dry_run, force=True)
    command_removed_at, command_would_remove_at, command_kept_at = len(removed), len(would_remove), len(kept)
    if remove_command_package:
        _collect_command_package_removal(removed=removed, would_remove=would_remove, kept=kept, dry_run=dry_run)
    return {
        "schema_version": "omj_uninstall/v1",
        "removed_files": bool(removed),
        "remove_files": remove_files or remove_all,
        "remove_all": remove_all,
        "dry_run": dry_run,
        "omj_home": str(paths.omj_home),
        "plugin_dir": str(paths.hermes_plugin_dir),
        "team_agents_dir": str(paths.hermes_agents_dir),
        "removed_paths": removed,
        "would_remove": would_remove,
        "kept_paths": kept,
        "command_package_remove_requested": remove_command_package,
        "command_package_removed": bool(removed[command_removed_at:]),
        "command_package_removed_paths": removed[command_removed_at:],
        "command_package_would_remove": would_remove[command_would_remove_at:],
        "command_package_kept": kept[command_kept_at:],
    }


def _collect_removal(path: Path, *, removed: list[str], would_remove: list[str], kept: list[dict[str, str]], dry_run: bool, force: bool, managed_plugin: bool = False) -> None:
    if not path.exists() and not path.is_symlink():
        return
    if managed_plugin:
        _collect_managed_plugin_removal(path, removed=removed, would_remove=would_remove, kept=kept, dry_run=dry_run, force=force)
        return
    if dry_run:
        would_remove.append(str(path))
        return
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    else:
        path.unlink()
    removed.append(str(path))


def _collect_managed_plugin_removal(path: Path, *, removed: list[str], would_remove: list[str], kept: list[dict[str, str]], dry_run: bool, force: bool) -> None:
    manifest = read_plugin_manifest(path)
    records = manifest.get("files") if manifest else None
    if (
        path.is_symlink()
        or not path.is_dir()
        or not manifest
        or manifest.get("schema_version") != PLUGIN_SCHEMA_VERSION
        or manifest.get("plugin_name") != "omj"
        or not isinstance(records, list)
        or (path / PLUGIN_MANAGED_MANIFEST).is_symlink()
    ):
        kept.append({"path": str(path), "reason": "plugin dir has no valid OMJ ownership manifest"})
        return
    owned: dict[Path, str] = {}
    for record in records:
        relative = record.get("path") if isinstance(record, dict) else None
        expected = record.get("sha256") if isinstance(record, dict) else None
        if (
            not isinstance(relative, str)
            or not relative
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or Path(relative) == Path(".")
            or relative == PLUGIN_MANAGED_MANIFEST
            or not isinstance(expected, str)
            or len(expected) != 64
            or any(char not in "0123456789abcdef" for char in expected)
        ):
            kept.append({"path": str(path), "reason": "plugin ownership manifest has an invalid file record"})
            return
        owned[path / relative] = expected
    retained_at = len(kept)
    removable: list[Path] = []
    for target, expected in owned.items():
        if not target.exists() and not target.is_symlink():
            continue
        if (
            not _is_relative_to(target.parent.resolve(), path)
            or any(parent.is_symlink() for parent in target.parents if parent == path or path in parent.parents)
            or (not target.is_file() and not target.is_symlink())
        ):
            kept.append({"path": str(target), "reason": "managed plugin file is not a local file"})
            continue
        try:
            modified = target.is_symlink() or sha256_file(target) != expected
        except OSError:
            modified = True
        if modified and not force:
            kept.append({"path": str(target), "reason": "managed plugin file changed; rerun with --force to remove it"})
            continue
        removable.append(target)
    if len(kept) == retained_at:
        removable.append(path / PLUGIN_MANAGED_MANIFEST)
    directories: set[Path] = {path}
    for target in removable:
        directories.update(parent for parent in target.parents if parent == path or path in parent.parents)
    entries = set(path.rglob("*"))
    for entry in sorted(entries - set(owned) - directories - {path / PLUGIN_MANAGED_MANIFEST}):
        kept.append({"path": str(entry), "reason": "not owned by the OMJ plugin manifest"})
    if dry_run:
        would_remove.extend(str(target) for target in removable)
        if entries <= set(removable) | directories:
            would_remove.append(str(path))
        return
    for target in removable:
        target.unlink()
        removed.append(str(target))
    for directory in sorted(directories, key=lambda item: len(item.parts), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            continue
        removed.append(str(directory))


def _collect_command_package_removal(*, removed: list[str], would_remove: list[str], kept: list[dict[str, str]], dry_run: bool) -> None:
    venv_dir = _managed_command_venv_dir()
    if venv_dir is None:
        kept.append({"path": "omj", "reason": "HOME is not available, so the install.sh-managed OMJ venv cannot be located"})
        return
    executable = Path(sys.executable).expanduser()
    if not _is_relative_to_without_resolving_symlinks(executable, venv_dir):
        kept.append({"path": str(executable.resolve()), "reason": "current omj command is not running from the install.sh-managed OMJ venv"})
        return
    for link in _managed_command_links(venv_dir):
        _collect_removal(link, removed=removed, would_remove=would_remove, kept=kept, dry_run=dry_run, force=True)
    _collect_removal(venv_dir, removed=removed, would_remove=would_remove, kept=kept, dry_run=dry_run, force=True)


def _managed_command_venv_dir() -> Path | None:
    explicit = os.environ.get("OMJ_VENV_DIR")
    if explicit:
        return Path(explicit).expanduser().resolve()
    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    if xdg_data_home:
        return (Path(xdg_data_home).expanduser() / "omj" / "venv").resolve()
    home = os.environ.get("HOME")
    if home:
        return (Path(home).expanduser() / ".local" / "share" / "omj" / "venv").resolve()
    return None


def _managed_command_links(venv_dir: Path) -> list[Path]:
    candidates: list[Path] = []
    explicit_bin = os.environ.get("OMJ_BIN_DIR")
    home = os.environ.get("HOME")
    if explicit_bin:
        candidates.append(Path(explicit_bin).expanduser() / "omj")
    elif home:
        candidates.append(Path(home).expanduser() / ".local" / "bin" / "omj")
    which = shutil.which("omj")
    if which:
        candidates.append(Path(which))
    if sys.argv and sys.argv[0]:
        candidates.append(Path(sys.argv[0]))
    links: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        path = candidate.expanduser()
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if path in seen or not path.is_symlink() or not _is_relative_to(resolved, venv_dir):
            continue
        seen.add(path)
        links.append(path)
    return links


def _managed_team_profile_files(paths: OmjPaths) -> list[Path]:
    manifest_files = _manifest_team_profile_files(paths)
    return manifest_files or _legacy_managed_team_profile_files(paths)


def _manifest_team_profile_files(paths: OmjPaths) -> list[Path]:
    if not paths.team_profile_manifest_dir.exists():
        return []
    files: list[Path] = []
    seen: set[Path] = set()
    for manifest_path in sorted(paths.team_profile_manifest_dir.glob("*.json")):
        manifest, _error = read_json_object_result(manifest_path)
        if manifest is None or manifest.get("schema_version") != TEAM_PROFILE_SCHEMA_VERSION:
            continue
        for raw_path in manifest.get("files", []):
            if not isinstance(raw_path, str):
                continue
            path = Path(raw_path).expanduser().resolve()
            if path in seen or not _is_relative_to(path, paths.hermes_agents_dir):
                continue
            seen.add(path)
            files.append(path)
    return files


def _legacy_managed_team_profile_files(paths: OmjPaths) -> list[Path]:
    if not paths.hermes_agents_dir.exists():
        return []
    files: list[Path] = []
    for path in sorted(paths.hermes_agents_dir.glob("omj-*.md")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if "schema_version: omj_team_profile_pack/v1" in text:
            files.append(path)
    return files


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _is_relative_to_without_resolving_symlinks(path: Path, parent: Path) -> bool:
    try:
        _normalize_without_final_symlink(path).relative_to(_normalize_without_final_symlink(parent))
    except ValueError:
        return False
    return True


def _normalize_without_final_symlink(path: Path) -> Path:
    expanded = path.expanduser()
    return expanded.parent.resolve() / expanded.name
    
