from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ..hashutil import sha256_file
from ..local_store import atomic_write_json, read_json_object, utc_now
from ..version import __version__


IMPORTED_SKILLS_DIR_NAME = "imported"


@dataclass(frozen=True)
class SkillRecord:
    name: str
    path: str
    sha256: str
    source: str
    files: tuple[dict[str, str], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "path": self.path,
            "sha256": self.sha256,
            "source": self.source,
        }
        if self.files:
            payload["files"] = [dict(item) for item in self.files]
        return payload


def new_manifest(source: str, skills_dir: Path, records: list[SkillRecord]) -> dict[str, Any]:
    owned_files: dict[str, str] = {}
    for record in records:
        owned_files[record.path] = record.sha256
        for item in record.files:
            relative = str(item.get("path", ""))
            digest = str(item.get("sha256", ""))
            if relative and digest:
                owned_files[relative] = digest
    return {
        "schema_version": 1,
        "package": "oh-my-jeo",
        "version": __version__,
        "source": source,
        "installed_at": utc_now(),
        "skills_dir": str(skills_dir),
        "owned_files": dict(sorted(owned_files.items())),
        "skills": [record.to_dict() for record in sorted(records, key=lambda item: item.name)],
    }


def read_manifest(path: Path) -> dict[str, Any] | None:
    return read_json_object(path)


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    atomic_write_json(path, manifest)


def _safe_relative(path: Path, root: Path) -> str | None:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return None


def _owned_paths_from_records(manifest: dict[str, Any] | None) -> dict[str, str]:
    if not isinstance(manifest, dict):
        return {}
    owned = manifest.get("owned_files")
    result: dict[str, str] = {}
    if isinstance(owned, dict):
        result.update({str(path): str(digest) for path, digest in owned.items() if path and digest})
    for raw_record in manifest.get("skills", []):
        if not isinstance(raw_record, dict):
            continue
        path = str(raw_record.get("path", ""))
        digest = str(raw_record.get("sha256", ""))
        if path and digest:
            result.setdefault(path, digest)
        files = raw_record.get("files", [])
        if isinstance(files, list):
            for item in files:
                if isinstance(item, dict):
                    child = str(item.get("path", ""))
                    child_digest = str(item.get("sha256", ""))
                    if child and child_digest:
                        result.setdefault(child, child_digest)
    return result


def skill_records(
    skills_dir: Path,
    source: str,
    *,
    owned_paths: Iterable[str | Path] | None = None,
) -> list[SkillRecord]:
    """Build records from the producer's explicit output list.

    A missing ``owned_paths`` is a legacy compatibility mode used only by older
    callers; it excludes the independent ``imported/`` namespace. Installers
    pass an explicit list so arbitrary custom SKILL.md files are never adopted.
    """
    if not skills_dir.exists():
        return []
    if owned_paths is None:
        candidates = sorted(skills_dir.rglob("SKILL.md"))
        candidates = [
            path
            for path in candidates
            if IMPORTED_SKILLS_DIR_NAME not in path.relative_to(skills_dir).parts
        ]
    else:
        candidates = []
        for raw in owned_paths:
            candidate = Path(raw)
            if not candidate.is_absolute():
                candidate = skills_dir / candidate
            if candidate.name != "SKILL.md":
                continue
            candidates.append(candidate)
        candidates = sorted(dict.fromkeys(candidates))

    records: list[SkillRecord] = []
    for skill_file in candidates:
        if skill_file.is_symlink() or not skill_file.is_file():
            continue
        rel = _safe_relative(skill_file, skills_dir)
        if rel is None:
            continue
        records.append(
            SkillRecord(
                name=skill_file.parent.name,
                path=rel,
                sha256=sha256_file(skill_file),
                source=source,
            )
        )
    return records


def local_modifications(manifest: dict[str, Any] | None, skills_dir: Path) -> list[str]:
    """Return modified or missing files from the manifest's owned allowlist."""
    owned = _owned_paths_from_records(manifest)
    modified: list[str] = []
    for relative, expected in sorted(owned.items()):
        path = skills_dir / relative
        if path.is_symlink() or not path.exists() or not path.is_file():
            modified.append(relative)
            continue
        try:
            actual = sha256_file(path)
        except OSError:
            modified.append(relative)
            continue
        if actual != expected:
            modified.append(relative)
    return modified


def manifest_owned_files(manifest: dict[str, Any] | None) -> dict[str, str]:
    """Public immutable ownership view used by installer/profile/doctor consumers."""
    return dict(_owned_paths_from_records(manifest))


def installed_managed_skill_path(
    skills_dir: Path, manifest: dict[str, Any] | None, relative_path: Path
) -> Path | None:
    """Resolve a canonical member only when its recorded files remain intact."""
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version") != 1
        or manifest.get("package") != "oh-my-jeo"
        or relative_path.is_absolute()
        or ".." in relative_path.parts
        or relative_path.name != "SKILL.md"
    ):
        return None
    records = manifest.get("skills")
    if not isinstance(records, list):
        return None
    matches = [
        record
        for record in records
        if isinstance(record, dict) and record.get("name") == relative_path.parent.name
    ]
    if len(matches) != 1 or matches[0].get("path") != relative_path.as_posix():
        return None
    record = matches[0]
    references = record.get("files", [])
    if not isinstance(references, list):
        return None
    owned = manifest_owned_files(manifest)
    for item in [record, *references]:
        if not isinstance(item, dict):
            return None
        relative = item.get("path")
        digest = item.get("sha256")
        if not isinstance(relative, str) or not isinstance(digest, str) or not digest:
            return None
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts or not path.is_relative_to(relative_path.parent):
            return None
        if owned.get(relative) != digest:
            return None
        target = skills_dir / path
        try:
            if any(skills_dir.joinpath(*path.parts[:index]).is_symlink() for index in range(len(path.parts) + 1)):
                return None
            if not target.is_file() or sha256_file(target) != digest:
                return None
        except (OSError, ValueError):
            return None
    return skills_dir / relative_path


__all__ = [
    "IMPORTED_SKILLS_DIR_NAME",
    "SkillRecord",
    "installed_managed_skill_path",
    "local_modifications",
    "manifest_owned_files",
    "new_manifest",
    "read_manifest",
    "skill_records",
    "write_manifest",
]
