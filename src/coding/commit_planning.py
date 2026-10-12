"""Deterministic commit-split planning over observed working-tree metadata.

The planner consumes either captured ``git status --porcelain=v1 -z`` metadata
or a caller-owned list of :class:`ChangedFile` records.  It never reads file
contents, invokes Git, writes the index, or creates commits.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any, Final

COMMIT_PLAN_SCHEMA_VERSION: Final = "commit_plan/v1"
COMMIT_PLAN_CLAIM_BOUNDARY: Final = (
    "This is a prepared commit plan derived from observed working-tree metadata. "
    "It is not a commit, and it is not execution, review, CI, or merge evidence."
)

MAX_PLAN_FILES: Final = 2000


class CommitPlanError(ValueError):
    """Raised when captured status metadata cannot produce a safe plan."""


@dataclass(frozen=True)
class ChangedFile:
    """One changed path from an observed status snapshot.

    ``path`` is the current/new path.  For a rename or copy, ``renamed_from``
    carries the original path that must be staged alongside it.
    """

    path: str
    status: str  # one of M A D R C ? (porcelain XY collapsed to one letter)
    renamed_from: str | None = None


_MANIFEST_LOCKFILES: Final = {
    "package.json": (
        "package-lock.json",
        "bun.lock",
        "bun.lockb",
        "yarn.lock",
        "pnpm-lock.yaml",
    ),
    "pyproject.toml": ("uv.lock", "poetry.lock", "pdm.lock"),
    "Cargo.toml": ("Cargo.lock",),
    "go.mod": ("go.sum",),
    "Gemfile": ("Gemfile.lock",),
    "composer.json": ("composer.lock",),
}
_LOCKFILE_NAMES: Final = frozenset(
    name for names in _MANIFEST_LOCKFILES.values() for name in names
)
_MANIFEST_NAMES: Final = frozenset(_MANIFEST_LOCKFILES)

_DOC_SUFFIXES: Final = frozenset({".md", ".markdown", ".rst", ".adoc", ".txt"})
_CONFIG_SUFFIXES: Final = frozenset(
    {".json", ".jsonc", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".editorconfig"}
)
_TEST_DIR_MARKERS: Final = ("tests", "test", "__tests__", "spec")
_VALID_STATUS_CODES: Final = frozenset(" MADRCUT?")
_COLLAPSED_STATUSES: Final = frozenset("MADRC?")


def parse_status_porcelain_z(payload: str) -> list[ChangedFile]:
    """Parse ``git status --porcelain=v1 -z`` output into changed files.

    Rename/copy entries carry two NUL-separated fields (new path, then
    original path); every other entry carries one.  Empty fields are accepted
    only as the trailing NUL terminator.  Paths are preserved exactly; no file
    system access or path canonicalization is performed.
    """

    if not isinstance(payload, str):
        raise CommitPlanError("porcelain payload must be text")

    if payload and not payload.endswith("\0"):
        raise CommitPlanError("porcelain -z payload must end with NUL")
    fields = payload.split("\0")
    files: list[ChangedFile] = []
    index = 0
    while index < len(fields):
        field = fields[index]
        index += 1
        if not field:
            if index != len(fields):
                raise CommitPlanError("porcelain -z payload contains an empty entry")
            continue
        if len(field) < 4 or field[2] != " ":
            raise CommitPlanError(f"unrecognized porcelain entry: {field!r}")
        xy, path = field[:2], field[3:]
        status = _collapse_status(xy)
        _validate_path(path, label="changed")
        renamed_from = None
        if "R" in xy or "C" in xy:
            if index >= len(fields) or not fields[index]:
                raise CommitPlanError(
                    f"rename/copy entry missing original path: {field!r}"
                )
            renamed_from = fields[index]
            index += 1
            _validate_path(renamed_from, label="original")
            if path == renamed_from:
                raise CommitPlanError(
                    f"rename/copy entry has identical paths: {path!r}"
                )
        files.append(ChangedFile(path=path, status=status, renamed_from=renamed_from))
    return files


def build_commit_plan(files: list[ChangedFile]) -> dict[str, Any]:
    """Build a deterministic, complete, non-overlapping commit plan.

    Every current/new input path lands in exactly one commit.  Dependency
    manifests and lockfiles share one repository-wide ``deps`` commit, and
    commits follow the fixed ``deps -> source -> tests -> docs -> config``
    category order.  Only metadata is used.
    """

    if not isinstance(files, list):
        raise CommitPlanError("changed files must be provided as a list")
    if len(files) > MAX_PLAN_FILES:
        raise CommitPlanError(
            f"commit planning is bounded to {MAX_PLAN_FILES} changed files"
        )

    deduped: dict[str, ChangedFile] = {}
    rename_sources: dict[str, str] = {}
    for entry in files:
        if not isinstance(entry, ChangedFile):
            raise CommitPlanError("changed files must contain ChangedFile entries")
        _validate_changed_file(entry)
        if entry.path in deduped:
            raise CommitPlanError(f"duplicate changed-file path: {entry.path}")
        deduped[entry.path] = entry
        if entry.status == "R" and entry.renamed_from:
            if entry.renamed_from in rename_sources:
                raise CommitPlanError(
                    f"duplicate renamed-from path: {entry.renamed_from}"
                )
            rename_sources[entry.renamed_from] = entry.path

    overlapping_paths = sorted(set(deduped).intersection(rename_sources))
    if overlapping_paths:
        raise CommitPlanError(
            f"rename source also appears as a changed path: {overlapping_paths[0]}"
        )

    ordered_paths = sorted(deduped)
    assigned: dict[str, str] = {}
    groups: dict[str, dict[str, Any]] = {}

    def _put(path: str, key: str, category: str, reason: str) -> None:
        if path in assigned:
            return
        assigned[path] = key
        group = groups.setdefault(
            key,
            {"category": category, "files": [], "reasons": []},
        )
        group["files"].append(path)
        if reason not in group["reasons"]:
            group["reasons"].append(reason)

    # Pass 1 — every manifest and lockfile shares ONE repo-wide deps commit.
    for path in ordered_paths:
        name = PurePosixPath(path).name
        if name in _MANIFEST_NAMES or name in _LOCKFILE_NAMES:
            _put(
                path,
                "deps",
                "deps",
                "dependency manifests and lockfiles land together, never split",
            )

    # Pass 2 — tests pair with same-stem source files when both changed.
    stems_by_name: dict[str, list[str]] = {}
    for path in ordered_paths:
        if path in assigned:
            continue
        stems_by_name.setdefault(PurePosixPath(path).stem, []).append(path)
    for path in ordered_paths:
        if path in assigned or not _is_test_path(path):
            continue
        stem = _test_stem(path)
        sources = [
            candidate
            for candidate in stems_by_name.get(stem, [])
            if candidate != path
            and not _is_test_path(candidate)
            and _category_for(candidate) == "source"
        ]
        if sources:
            source = sources[0]
            key = f"source:{_group_dir(source)}"
            _put(
                source,
                key,
                "source",
                "source change and the test that proves it share a commit",
            )
            _put(
                path,
                key,
                "source",
                "source change and the test that proves it share a commit",
            )

    # Pass 3 — remaining files bucket by category, grouped by top directory.
    for path in ordered_paths:
        if path in assigned:
            continue
        category = _category_for(path)
        _put(
            path,
            f"{category}:{_group_dir(path)}",
            category,
            _CATEGORY_REASONS[category],
        )

    category_rank = {"deps": 0, "source": 1, "tests": 2, "docs": 3, "config": 4}
    ordered_keys = sorted(
        groups,
        key=lambda key: (category_rank[groups[key]["category"]], key),
    )
    commits = []
    for order, key in enumerate(ordered_keys, start=1):
        group = groups[key]
        group_files = sorted(group["files"])
        renames = {
            path: deduped[path].renamed_from
            for path in group_files
            if deduped[path].renamed_from
        }
        commit: dict[str, Any] = {
            "order": order,
            "category": group["category"],
            "title": _suggested_title(group["category"], key, group_files, deduped),
            "files": group_files,
            "rationale": "; ".join(group["reasons"]),
        }
        if renames:
            # ``files`` carries the new path; this map names the old path to
            # stage with it.  No staging is performed by this module.
            commit["renames"] = renames
        commits.append(commit)

    covered = sorted(path for commit in commits for path in commit["files"])
    if covered != ordered_paths or len(covered) != len(set(covered)):
        raise CommitPlanError(
            "internal error: plan coverage is not complete and non-overlapping"
        )

    return {
        "schema_version": COMMIT_PLAN_SCHEMA_VERSION,
        "changed_file_count": len(ordered_paths),
        "commit_count": len(commits),
        "commits": commits,
        "rules": [
            "complete, non-overlapping coverage: every changed file belongs to exactly one commit (renamed files list their old path in the commit's renames map)",
            "lockfile-manifest pairing: all dependency manifests and lockfiles share one commit, so a lockfile never lands apart from its manifest",
            "fixed dependency order: deps -> source -> tests -> docs -> config",
            "bounded diffs: one reviewable idea per commit; split further by hand if a group reads as two ideas",
        ],
        "claim_boundary": COMMIT_PLAN_CLAIM_BOUNDARY,
    }


def _validate_changed_file(entry: ChangedFile) -> None:
    if not isinstance(entry.path, str):
        raise CommitPlanError("changed file path must be text")
    _validate_path(entry.path, label="changed")
    if not isinstance(entry.status, str) or entry.status not in _COLLAPSED_STATUSES:
        raise CommitPlanError(f"unknown changed-file status: {entry.status!r}")
    if entry.status in {"R", "C"}:
        if not isinstance(entry.renamed_from, str) or not entry.renamed_from:
            raise CommitPlanError(
                f"{entry.status} entry missing original path: {entry.path!r}"
            )
        _validate_path(entry.renamed_from, label="original")
        if entry.path == entry.renamed_from:
            raise CommitPlanError(f"rename entry has identical paths: {entry.path!r}")
    elif entry.renamed_from is not None:
        raise CommitPlanError(
            f"non-rename changed file carries original path: {entry.path!r}"
        )


def _validate_path(path: str, *, label: str) -> None:
    if not isinstance(path, str):
        raise CommitPlanError(f"{label} path must be text")
    if not path or not path.strip():
        raise CommitPlanError(f"{label} path is empty")
    if "\0" in path:
        raise CommitPlanError(f"{label} path contains NUL")
    pure = PurePosixPath(path)
    if pure.is_absolute() or any(part == ".." for part in pure.parts):
        raise CommitPlanError(f"unknown {label} path: {path!r}")
    if pure.name in {"", "."} or str(pure) != path:
        raise CommitPlanError(f"unknown {label} path: {path!r}")


def _collapse_status(xy: str) -> str:
    if (
        not isinstance(xy, str)
        or len(xy) != 2
        or any(char not in _VALID_STATUS_CODES for char in xy)
    ):
        raise CommitPlanError(f"unknown porcelain status: {xy!r}")
    if xy == "  " or ("?" in xy and xy != "??"):
        raise CommitPlanError(f"unknown porcelain status: {xy!r}")
    if "U" in xy or xy in ("AA", "DD"):
        raise CommitPlanError(
            f"unmerged entry {xy!r}: resolve the merge before planning commits"
        )
    for letter in (xy[0], xy[1]):
        if letter in "MADRC":
            return letter
        if letter == "T":
            return "M"
    if xy == "??":
        return "?"
    raise CommitPlanError(f"unknown porcelain status: {xy!r}")


def _is_test_path(path: str) -> bool:
    parts = PurePosixPath(path).parts
    if any(part in _TEST_DIR_MARKERS for part in parts[:-1]):
        return True
    name = PurePosixPath(path).stem
    return (
        name.startswith("test_")
        or name.endswith("_test")
        or name.endswith(".test")
        or name.endswith(".spec")
    )


def _test_stem(path: str) -> str:
    stem = PurePosixPath(path).stem
    for prefix in ("test_",):
        if stem.startswith(prefix):
            return stem[len(prefix) :]
    for suffix in ("_test", ".test", ".spec"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def _category_for(path: str) -> str:
    pure = PurePosixPath(path)
    suffix = pure.suffix.lower()
    # File type outranks directory ancestry: docs/spec/api.md is a doc and
    # spec/openapi.yaml is config, even though a `spec` ancestor also names a
    # test convention elsewhere.
    if suffix in _DOC_SUFFIXES:
        return "docs"
    if suffix in _CONFIG_SUFFIXES or pure.name.startswith("."):
        return "config"
    if _is_test_path(path):
        return "tests"
    return "source"


def _group_dir(path: str) -> str:
    parts = PurePosixPath(path).parts
    if len(parts) <= 1:
        return "."
    return "/".join(parts[:2]) if len(parts) > 2 else parts[0]


_CATEGORY_REASONS: Final = {
    "source": "one reviewable source change grouped by directory",
    "tests": "standalone test changes grouped by directory",
    "docs": "documentation-only changes grouped by directory",
    "config": "configuration and tooling changes grouped by directory",
    "deps": "dependency manifest and lockfile land together, never split",
}


def _suggested_title(
    category: str, key: str, files: list[str], entries: dict[str, ChangedFile]
) -> str:
    scope = key.split(":", 1)[1] if ":" in key else key
    scope = scope.strip("/").replace("/", "-") or "repo"
    statuses = {entries[path].status for path in files}
    if category == "source":
        source_kind = (
            "feat" if "A" in statuses else "chore" if statuses == {"D"} else "refactor"
        )
    else:
        source_kind = ""
    kind = {
        "deps": "chore(deps)",
        "source": source_kind,
        "tests": "test",
        "docs": "docs",
        "config": "chore",
    }[category]
    verb = "remove" if statuses == {"D"} else "add" if statuses == {"A"} else "update"
    noun = PurePosixPath(files[0]).name if len(files) == 1 else f"{len(files)} files"
    return f"{kind}({scope}): {verb} {noun}"
