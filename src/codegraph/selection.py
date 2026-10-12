"""Reverse-import test selection over a local codegraph.

`omj codegraph build` records which Python file imports which
(`imports_internal` edges). Walking those edges backwards from a changed file
gives every file the recorded edges reach, and the test modules among them are
the smallest set a static reader can name as "the tests that exercise this
change".

Everything here is pure traversal over the codegraph payload: nothing is
imported, executed, or spawned. The result is a starting point for the
smallest test that proves a claim. It is not a substitute for the full suite,
and its blind spots ship inside the payload rather than being left to the
reader to remember.
"""

from __future__ import annotations

import os
from collections import deque
from pathlib import Path
from typing import Any

from .schema import CLAIM_BOUNDARY


CODEGRAPH_TEST_SELECTION_SCHEMA_VERSION = "codegraph_test_selection/v1"

TEST_SELECTION_CLAIM_BOUNDARY = (
    "A selected subset is a starting point for the smallest test that proves a claim; "
    "it is never a substitute for the full suite before claiming done. " + CLAIM_BOUNDARY
)

# The predicate is a name-and-directory rule: basename `test*.py` (unittest's
# default discovery pattern) under a directory named tests or test. The
# directory component keeps a source module that happens to start with `test`
# out of the selection. The rule says nothing about whether the suite's
# discovery enters that directory, so a selected path is run by file.
TEST_MODULE_PREFIX = "test"
TEST_DIRECTORY_NAMES = frozenset({"tests", "test"})
TEST_MODULE_RULE = (
    "a scanned Python file under a directory named tests or test whose basename matches "
    "unittest's default discovery pattern test*.py; run a selected path by file, since the rule "
    "does not check whether the suite's discovery enters its directory"
)

# Importing any module under a package executes the package's __init__.py, and
# the scanner records no edge for that, so a changed __init__.py is credited
# with the importers of every scanned file under its own directory.
PACKAGE_INIT_NAME = "__init__.py"

# Fixed by design: the same block ships with every payload, so a reader who
# sees an empty selection also sees what this traversal cannot see.
TEST_SELECTION_BLIND_SPOTS: tuple[str, ...] = (
    "dynamic imports: a module reached through importlib, __import__, spec_from_file_location, "
    "or runpy at run time is not an import edge",
    "fixtures loaded by path: a file a test reads with open(), Path.read_text, json.load, or through "
    "a subprocess is not an import edge",
    "generated artifacts gated by byte comparison: a file whose gate diffs it against its producer "
    "(a docs --check target) is reached by regeneration, not by an import",
    "extra import roots: a module importable only through a PYTHONPATH entry other than the repository "
    "root, such as a helper under tests/ imported by its bare name under PYTHONPATH=tests, resolves "
    "to no edge",
    "package roots that extend __path__: a package __init__.py is credited with the importers of the "
    "scanned files under its own directory, not with importers of other directories it appends to "
    "__path__ (a src-layout root)",
    "spawned commands: a test that drives a console script or a `python -m` module never imports the "
    "code it exercises",
    "non-Python changes: a changed file that is not a Python module (config, YAML, JSON, Markdown) has "
    "no importer to trace",
)

CHANGED_PATH_STATUSES = ("scanned", "not_python", "directory", "missing", "not_scanned")
_STATUS_REASONS = {
    "not_python": "not a Python module; no import edge can reach it",
    "directory": "a directory; pass the changed files under it",
    "missing": (
        "no such file under the repository root; the graph is built from the current tree, "
        "so a deleted module's former importers are not edges"
    ),
    "not_scanned": "a Python file the scanner did not index (under an excluded directory such as build/ or .venv/)",
}
_UNREFERENCED_REASON = "nothing in the graph imports this module"
_CHANGED_TEST_REASON = "a changed test module is selected itself at distance 0"

MAX_TEXT_REACHED_SOURCE_FILES = 12
MAX_TEXT_SCANNER_WARNINGS = 10


def select_tests_for_changes(graph: dict[str, Any], changed: list[str]) -> dict[str, Any]:
    repo_root = Path(str(graph["repo_root"]))
    scanned_paths = {str(record["path"]) for record in graph.get("files", []) if isinstance(record, dict)}
    folded_index = {path.lower(): path for path in sorted(scanned_paths)}
    reverse = _reverse_import_index(graph)

    reached: dict[str, dict[str, Any]] = {}
    entries: dict[str, dict[str, Any]] = {}
    for raw in changed:
        resolution = _resolve_changed_path(repo_root, raw)
        text = str(resolution["path"])
        if text in entries:
            continue
        notes = list(resolution["notes"])
        if resolution["unresolvable"]:
            status, canonical = "missing", str(resolution["resolved_path"])
            notes.append(f"the path cannot be resolved ({resolution['unresolvable']}); treated as missing")
        else:
            status, canonical, spelling_note = _classify(
                repo_root, str(resolution["resolved_path"]), scanned_paths, folded_index
            )
            if spelling_note:
                notes.append(spelling_note)
        entry: dict[str, Any] = {
            "path": text,
            "resolved_path": canonical,
            "status": status,
            "is_test_module": False,
            "direct_importer_count": 0,
            "reached_file_count": 0,
            "selected_test_count": 0,
            "reason": "; ".join([*notes, *([_STATUS_REASONS[status]] if status in _STATUS_REASONS else [])]),
        }
        if status != "scanned":
            entries[text] = entry
            continue
        is_test = _is_test_module(canonical)
        is_package_init = Path(canonical).name == PACKAGE_INIT_NAME
        if is_package_init:
            seeds, member_count = _package_init_seeds(reverse, scanned_paths, canonical)
            package_dir = canonical[: -len(PACKAGE_INIT_NAME)] or "./"
            notes.append(
                f"a package {PACKAGE_INIT_NAME}, credited with the importers of the {member_count} "
                f"scanned files under {package_dir}"
            )
            if not seeds:
                notes.append("none has a recorded importer")
        else:
            seeds = set(reverse.get(canonical, ()))
        distances = _reverse_closure(reverse, canonical, seeds)
        entry["is_test_module"] = is_test
        entry["direct_importer_count"] = len(seeds)
        entry["reached_file_count"] = len(distances)
        if is_test:
            distances = {canonical: 0, **distances}
            notes.append(_CHANGED_TEST_REASON)
        elif not seeds and not is_package_init:
            notes.append(_UNREFERENCED_REASON)
        entry["selected_test_count"] = sum(1 for path in distances if _is_test_module(path))
        entry["reason"] = "; ".join(notes)
        for path, distance in distances.items():
            record = reached.setdefault(path, {"distance": distance, "changed_paths": set()})
            record["distance"] = min(int(record["distance"]), distance)
            record["changed_paths"].add(text)
        entries[text] = entry

    ordered_entries = [entries[key] for key in sorted(entries)]
    selected_tests = sorted(
        (
            {
                "path": path,
                "distance": int(record["distance"]),
                "changed_paths": sorted(record["changed_paths"]),
            }
            for path, record in reached.items()
            if _is_test_module(path)
        ),
        key=lambda item: str(item["path"]),
    )
    reached_source_files = sorted(path for path in reached if not _is_test_module(path))
    unreferenced_paths = sorted(
        entry["path"] for entry in ordered_entries if _UNREFERENCED_REASON in str(entry["reason"])
    )
    unscanned_paths = sorted(entry["path"] for entry in ordered_entries if entry["status"] != "scanned")
    scanner_warnings = [str(warning) for warning in graph.get("warnings", [])]
    return {
        "schema_version": CODEGRAPH_TEST_SELECTION_SCHEMA_VERSION,
        "repo_root": str(repo_root),
        "generated_at": graph["generated_at"],
        "changed_paths": ordered_entries,
        "selected_tests": selected_tests,
        "selected_test_paths": [str(item["path"]) for item in selected_tests],
        "reached_source_files": reached_source_files,
        "unreferenced_paths": unreferenced_paths,
        "unscanned_paths": unscanned_paths,
        "scanner_warnings": scanner_warnings,
        "test_module_rule": TEST_MODULE_RULE,
        "stats": {
            "changed_path_count": len(ordered_entries),
            "scanned_changed_path_count": sum(1 for entry in ordered_entries if entry["status"] == "scanned"),
            "selected_test_count": len(selected_tests),
            "reached_source_file_count": len(reached_source_files),
            "unreferenced_path_count": len(unreferenced_paths),
            "unscanned_path_count": len(unscanned_paths),
            "scanner_warning_count": len(scanner_warnings),
        },
        "blind_spots": list(TEST_SELECTION_BLIND_SPOTS),
        "claim_boundary": TEST_SELECTION_CLAIM_BOUNDARY,
    }


def render_test_selection_text(payload: dict[str, Any]) -> str:
    stats = payload["stats"]
    lines = [
        "OMJ codegraph test selection",
        f"Repo: {payload['repo_root']}",
        f"Changed paths ({stats['changed_path_count']})",
    ]
    for entry in payload["changed_paths"]:
        lines.append(f"  - {entry['path']}: {_changed_entry_summary(entry)}")
    selected = payload["selected_tests"]
    lines.append(f"Selected tests ({len(selected)})")
    if selected:
        for item in selected:
            lines.append(f"  - {item['path']} (distance {item['distance']})")
    else:
        lines.append("  - none")
    reached = payload["reached_source_files"]
    if reached:
        lines.append(f"Reached source files ({len(reached)})")
        for path in reached[:MAX_TEXT_REACHED_SOURCE_FILES]:
            lines.append(f"  - {path}")
        if len(reached) > MAX_TEXT_REACHED_SOURCE_FILES:
            lines.append(f"  - ... {len(reached) - MAX_TEXT_REACHED_SOURCE_FILES} more")
    warnings = payload.get("scanner_warnings", [])
    if warnings:
        lines.append(f"Scanner warnings ({len(warnings)})")
        for warning in warnings[:MAX_TEXT_SCANNER_WARNINGS]:
            lines.append(f"  - {warning}")
        if len(warnings) > MAX_TEXT_SCANNER_WARNINGS:
            lines.append(f"  - ... {len(warnings) - MAX_TEXT_SCANNER_WARNINGS} more")
    lines.append("Blind spots")
    for spot in payload["blind_spots"]:
        lines.append(f"  - {spot}")
    lines.extend(
        [
            "Boundary",
            f"  {payload['claim_boundary']}",
            "For machine-readable output, rerun with `--json`.",
        ]
    )
    return "\n".join(lines)


def _changed_entry_summary(entry: dict[str, Any]) -> str:
    if entry["status"] != "scanned":
        return f"{entry['reason']}; no test selected"
    counts = (
        f"direct importers {entry['direct_importer_count']}, files reached {entry['reached_file_count']}, "
        f"tests selected {entry['selected_test_count']}"
    )
    if entry["reason"]:
        return f"{entry['reason']}; {counts}"
    return counts


def _reverse_import_index(graph: dict[str, Any]) -> dict[str, set[str]]:
    reverse: dict[str, set[str]] = {}
    for edge in graph.get("edges", []):
        if not isinstance(edge, dict) or edge.get("kind") != "imports_internal":
            continue
        reverse.setdefault(str(edge["to"]), set()).add(str(edge["from"]))
    return reverse


def _package_init_seeds(
    reverse: dict[str, set[str]], scanned_paths: set[str], init_path: str
) -> tuple[set[str], int]:
    package_dir = init_path[: -len(PACKAGE_INIT_NAME)]
    members = sorted(path for path in scanned_paths if path != init_path and path.startswith(package_dir))
    seeds = set(reverse.get(init_path, ()))
    for member in members:
        seeds.update(reverse.get(member, ()))
    seeds.discard(init_path)
    return seeds, len(members)


def _reverse_closure(reverse: dict[str, set[str]], start: str, seeds: set[str]) -> dict[str, int]:
    distances: dict[str, int] = {}
    queue: deque[tuple[str, int]] = deque()
    for seed in sorted(seeds):
        if seed == start:
            continue
        distances[seed] = 1
        queue.append((seed, 1))
    while queue:
        path, distance = queue.popleft()
        for importer in sorted(reverse.get(path, ())):
            if importer == start or importer in distances:
                continue
            distances[importer] = distance + 1
            queue.append((importer, distance + 1))
    return distances


def _is_test_module(rel_path: str) -> bool:
    path = Path(rel_path)
    if not any(part in TEST_DIRECTORY_NAMES for part in path.parts[:-1]):
        return False
    return path.name.startswith(TEST_MODULE_PREFIX) and path.name.endswith(".py")


def _resolve_changed_path(repo_root: Path, raw: str) -> dict[str, Any]:
    text = str(raw).strip()
    if not text:
        raise ValueError("changed path must not be empty")
    candidate = Path(text.replace("\\", "/")).expanduser()
    target = candidate if candidate.is_absolute() else repo_root / candidate
    lexical = _relative_or_none(repo_root, Path(os.path.normpath(str(target))), text)
    try:
        resolved = _relative_or_none(repo_root, target.resolve(), text)
    except (RuntimeError, OSError) as exc:
        if lexical is None:
            raise ValueError(f"changed path is outside the repository root: {text}") from exc
        return {"path": text, "resolved_path": lexical, "unresolvable": f"{type(exc).__name__}: {exc}", "notes": []}
    if resolved is None:
        raise ValueError(f"changed path is outside the repository root: {text}")
    notes: list[str] = []
    if lexical != resolved:
        # `resolve()` also canonicalises letter case on a case-insensitive
        # filesystem (Windows returns the on-disk spelling), so a differing
        # result is a symlink only when a component on the way is one.
        if _crosses_symlink(repo_root, target):
            notes.append(f"resolved through a symlink to {resolved}")
        elif lexical is not None and lexical.lower() == resolved.lower():
            notes.append(f"spelled differently from the scanned path {resolved}")
        else:
            notes.append(f"resolved to {resolved}")
    return {"path": text, "resolved_path": resolved, "unresolvable": "", "notes": notes}


def _crosses_symlink(repo_root: Path, target: Path) -> bool:
    """True when the lexical path or any of its parents inside the repo is a symlink."""
    probe = Path(os.path.normpath(str(target)))
    while True:
        try:
            if probe.is_symlink():
                return True
        except OSError:
            return False
        if probe == repo_root or probe.parent == probe:
            return False
        probe = probe.parent


def _relative_or_none(repo_root: Path, target: Path, text: str) -> str | None:
    try:
        rel = target.relative_to(repo_root)
    except ValueError:
        return None
    if not rel.parts:
        raise ValueError(f"changed path must name a file, not the repository root: {text}")
    return rel.as_posix()


def _classify(
    repo_root: Path, resolved: str, scanned_paths: set[str], folded_index: dict[str, str]
) -> tuple[str, str, str]:
    if resolved in scanned_paths:
        return "scanned", resolved, ""
    target = repo_root / resolved
    canonical = folded_index.get(resolved.lower())
    if canonical is not None and target.is_file():
        return "scanned", canonical, f"spelled differently from the scanned path {canonical}"
    if target.is_dir():
        return "directory", resolved, ""
    if not resolved.endswith(".py"):
        return "not_python", resolved, ""
    if not target.exists():
        return "missing", resolved, ""
    return "not_scanned", resolved, ""
