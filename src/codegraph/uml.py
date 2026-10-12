"""Interface-level PlantUML projection of a local codegraph.

`omj codegraph build` already knows every Python file, the symbols each one
defines, and which files import which. This module folds that graph up to the
level a person can read on one image -- packages (or modules), each showing
only its public top-level symbols -- and emits PlantUML source that is shaped
to render cleanly: bounded node and edge counts, a fixed direction rule,
orthogonal lines, hidden empty compartments, and a theme so the picture reads
like one system rather than a Graphviz default.

Everything here is pure computation over the codegraph payload. Rendering to
PNG/SVG is a separate, observed step: `render_plan()` only reports which local
renderer *would* run and the exact command, using `shutil.which` and path
checks; nothing is spawned and nothing touches the network.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from .schema import CLAIM_BOUNDARY


CODEBASE_UML_SCHEMA_VERSION = "codebase_uml/v1"
UML_RENDER_PLAN_SCHEMA_VERSION = "uml_render_plan/v1"

UML_LEVELS = ("package", "module")
UML_LAYOUT_ENGINES = ("auto", "dot", "smetana")
UML_THEMES = ("omh", "mono")

DEFAULT_DEPTH = 2
DEFAULT_MAX_NODES = 16
DEFAULT_MAX_INTERFACE = 6
# Beyond this many nodes a top-to-bottom layout becomes a tall ribbon that
# no chat surface previews legibly; left-to-right keeps it inside one screen.
LEFT_TO_RIGHT_NODE_THRESHOLD = 8
# Edge budget relative to node count. Above this ratio dot starts crossing
# lines through boxes, and ortho routing gives up on labels entirely.
EDGE_BUDGET_PER_NODE = 2
# Import edges at or above this weight draw solid; lighter coupling draws
# dotted so the eye finds the load-bearing dependencies first. A module
# is one file, so its counts run lower than a package's.
STRONG_EDGE_WEIGHT_BY_LEVEL = {"package": 4, "module": 2}
PLANTUML_LIMIT_SIZE = 8192
ROOT_UNIT_ID = "(root)"
OTHER_UNIT_ID = "(other)"

PLANTUML_JAR_ENV = "PLANTUML_JAR"
GRAPHVIZ_DOT_ENV = "GRAPHVIZ_DOT"

_THEMES: dict[str, dict[str, str]] = {
    "omh": {
        "background": "#FFFFFF",
        "font": "Helvetica",
        "node_bg": "#F8FAFC",
        "node_border": "#94A3B8",
        "node_header": "#E2E8F0",
        "node_text": "#0F172A",
        "member_text": "#334155",
        "stereotype_text": "#64748B",
        "entrypoint_bg": "#E0F2FE",
        "other_bg": "#F1F5F9",
        "package_border": "#CBD5E1",
        "package_text": "#475569",
        "arrow": "#5B6B7F",
        "legend_bg": "#F8FAFC",
        "legend_border": "#CBD5E1",
    },
    "mono": {
        "background": "#FFFFFF",
        "font": "Helvetica",
        "node_bg": "#FFFFFF",
        "node_border": "#111111",
        "node_header": "#EEEEEE",
        "node_text": "#111111",
        "member_text": "#222222",
        "stereotype_text": "#555555",
        "entrypoint_bg": "#EEEEEE",
        "other_bg": "#F5F5F5",
        "package_border": "#333333",
        "package_text": "#333333",
        "arrow": "#333333",
        "legend_bg": "#FFFFFF",
        "legend_border": "#333333",
    },
}


def build_uml_model(
    graph: dict[str, Any],
    *,
    level: str = "package",
    depth: int = DEFAULT_DEPTH,
    focus: str = "",
    max_nodes: int = DEFAULT_MAX_NODES,
    max_interface: int = DEFAULT_MAX_INTERFACE,
    include_tests: bool = False,
) -> dict[str, Any]:
    """Fold a codegraph into a bounded, interface-level unit graph."""
    if level not in UML_LEVELS:
        raise ValueError(f"unknown uml level: {level!r} (expected one of {', '.join(UML_LEVELS)})")
    if depth < 1:
        raise ValueError("depth must be at least 1")
    if max_nodes < 2:
        raise ValueError("max-nodes must be at least 2")
    if max_interface < 0:
        raise ValueError("max-interface must be zero or more")
    focus_prefix = _normalize_focus(focus)

    files = [record for record in graph.get("files", []) if isinstance(record, dict)]
    unit_by_path: dict[str, str] = {}
    skipped_test_files = 0
    for record in files:
        path = str(record.get("path", ""))
        if not path:
            continue
        if not include_tests and "test" in record.get("entrypoint_tags", []):
            skipped_test_files += 1
            continue
        unit_by_path[path] = _unit_id(path, level=level, depth=depth)

    units: dict[str, dict[str, Any]] = {}
    for record in files:
        path = str(record.get("path", ""))
        unit_id = unit_by_path.get(path)
        if unit_id is None:
            continue
        unit = units.setdefault(unit_id, _new_unit(unit_id))
        unit["file_count"] += 1
        unit["symbol_count"] += len(record.get("defines", []))
        unit["_paths"].append(path)
        for tag in record.get("entrypoint_tags", []):
            if tag not in unit["entrypoint_tags"]:
                unit["entrypoint_tags"].append(tag)

    interface_hidden = _collect_interfaces(graph, units, unit_by_path, max_interface=max_interface)

    edge_weights: dict[tuple[str, str], int] = {}
    for edge in graph.get("edges", []):
        if not isinstance(edge, dict) or edge.get("kind") != "imports_internal":
            continue
        source = unit_by_path.get(str(edge.get("from", "")))
        target = unit_by_path.get(str(edge.get("to", "")))
        if source is None or target is None or source == target:
            continue
        edge_weights[(source, target)] = edge_weights.get((source, target), 0) + 1

    omissions: dict[str, Any] = {
        "test_files_skipped": skipped_test_files,
        "interface_symbols_hidden": interface_hidden,
        "units_outside_focus": 0,
        "units_folded": [],
        "edges_pruned": 0,
        "edges_into_folded_units": 0,
        "min_kept_edge_weight": 0,
    }

    priority: set[str] = set()
    if focus_prefix:
        inside, kept = _focus_units(units, edge_weights, focus_prefix)
        priority = inside
        omissions["units_outside_focus"] = len(units) - len(kept)
        units = {unit_id: unit for unit_id, unit in units.items() if unit_id in kept}
        edge_weights = {key: weight for key, weight in edge_weights.items() if key[0] in kept and key[1] in kept}

    units, edge_weights, folded, folded_edges = _fold_to_budget(
        units, edge_weights, max_nodes=max_nodes, priority=priority
    )
    omissions["units_folded"] = folded
    omissions["edges_into_folded_units"] = folded_edges

    edges, pruned, min_weight = _prune_edges(units, edge_weights)
    omissions["edges_pruned"] = pruned
    omissions["min_kept_edge_weight"] = min_weight

    nodes = []
    aliases = _aliases_for(sorted(units))
    for unit_id in sorted(units):
        unit = units[unit_id]
        nodes.append(
            {
                "id": unit_id,
                "alias": aliases[unit_id],
                "label": unit_id,
                "group": _group_of(unit_id, level=level, depth=depth),
                "file_count": unit["file_count"],
                "symbol_count": unit["symbol_count"],
                "entrypoint_tags": sorted(unit["entrypoint_tags"]),
                "interface": unit["interface"],
                "interface_hidden": unit["interface_hidden"],
                "folded_unit_count": unit.get("folded_unit_count", 0),
            }
        )

    direction = "left to right" if len(nodes) > LEFT_TO_RIGHT_NODE_THRESHOLD else "top to bottom"
    return {
        "schema_version": CODEBASE_UML_SCHEMA_VERSION,
        "repo_root": graph.get("repo_root", ""),
        "generated_at": graph.get("generated_at", ""),
        "source_schema_version": graph.get("schema_version", ""),
        "view": {
            "level": level,
            "depth": depth,
            "focus": focus_prefix,
            "max_nodes": max_nodes,
            "max_interface": max_interface,
            "include_tests": include_tests,
        },
        "nodes": nodes,
        "edges": edges,
        "layout": {
            "direction": direction,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "strong_edge_weight": STRONG_EDGE_WEIGHT_BY_LEVEL[level],
            "hardening": _hardening_directives(direction),
        },
        "omissions": omissions,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def render_plantuml(
    model: dict[str, Any],
    *,
    theme: str = "omh",
    layout_engine: str = "dot",
    title: str = "",
) -> str:
    """Emit PlantUML source for a uml model. Deterministic for a given model."""
    if theme not in _THEMES:
        raise ValueError(f"unknown uml theme: {theme!r} (expected one of {', '.join(UML_THEMES)})")
    if layout_engine not in ("dot", "smetana"):
        raise ValueError(f"unknown layout engine: {layout_engine!r} (expected dot or smetana)")
    colors = _THEMES[theme]
    view = model["view"]
    layout = model["layout"]
    repo_name = Path(str(model.get("repo_root") or "")).name or "repository"
    heading = title or f"{repo_name} — {view['level']} view"

    lines = [
        "@startuml",
        f"' generated by omj codegraph uml — {CODEBASE_UML_SCHEMA_VERSION}",
        "' prepared local context; not architecture proof, review, CI, or merge evidence",
    ]
    if layout_engine == "smetana":
        lines.append("!pragma layout smetana")
    lines.extend(
        [
            f"title {_escape(heading)}",
            f"{layout['direction']} direction",
            "",
            f"skinparam backgroundColor {colors['background']}",
            "skinparam shadowing false",
            "skinparam roundCorner 10",
            f"skinparam defaultFontName {colors['font']}",
            "skinparam defaultFontSize 12",
            "skinparam linetype ortho",
            "skinparam nodesep 40",
            "skinparam ranksep 70",
            "skinparam wrapWidth 220",
            "skinparam packageStyle rectangle",
            f"skinparam ArrowColor {colors['arrow']}",
            "skinparam ArrowThickness 1.2",
            "skinparam class {",
            f"  BackgroundColor {colors['node_bg']}",
            f"  BorderColor {colors['node_border']}",
            f"  FontColor {colors['node_text']}",
            f"  HeaderBackgroundColor {colors['node_header']}",
            f"  AttributeFontColor {colors['member_text']}",
            f"  StereotypeFontColor {colors['stereotype_text']}",
            "}",
            "skinparam package {",
            f"  BackgroundColor {colors['background']}",
            f"  BorderColor {colors['package_border']}",
            f"  FontColor {colors['package_text']}",
            "}",
            "skinparam legend {",
            f"  BackgroundColor {colors['legend_bg']}",
            f"  BorderColor {colors['legend_border']}",
            "}",
            "skinparam classAttributeIconSize 0",
            "hide circle",
            "hide empty members",
            "",
        ]
    )

    groups: dict[str, list[dict[str, Any]]] = {}
    for node in sorted(model["nodes"], key=lambda item: (item["id"] == OTHER_UNIT_ID, item["id"])):
        groups.setdefault(node["group"], []).append(node)
    multi_group = len(groups) > 1 or (len(groups) == 1 and "" not in groups)
    # Grouped packages first, loose units after, so the fold lands at the end.
    for group in sorted(groups, key=lambda name: (name == "", name)):
        indent = ""
        if multi_group and group:
            lines.append(f'package "{_escape(group)}" {{')
            indent = "  "
        for node in groups[group]:
            lines.extend(indent + line for line in _node_lines(node, colors))
        if multi_group and group:
            lines.append("}")
        lines.append("")

    alias_by_id = {node["id"]: node["alias"] for node in model["nodes"]}
    for edge in model["edges"]:
        arrow = "-->" if edge["weight"] >= layout["strong_edge_weight"] else "..>"
        lines.append(f"{alias_by_id[edge['from']]} {arrow} {alias_by_id[edge['to']]}")
    if model["edges"]:
        lines.append("")

    lines.extend(_legend_lines(model))
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def render_plan(
    *,
    source_path: str,
    output_format: str = "png",
    layout_engine: str = "auto",
    environ: dict[str, str] | None = None,
    which=shutil.which,
) -> dict[str, Any]:
    """Report which local renderer would run and the exact command, without running it."""
    if output_format not in ("png", "svg"):
        raise ValueError(f"unknown output format: {output_format!r} (expected png or svg)")
    if layout_engine not in UML_LAYOUT_ENGINES:
        raise ValueError(f"unknown layout engine: {layout_engine!r} (expected one of {', '.join(UML_LAYOUT_ENGINES)})")
    env = os.environ if environ is None else environ

    plantuml_cli = which("plantuml")
    java = which("java")
    jar = env.get(PLANTUML_JAR_ENV, "").strip()
    jar_present = bool(jar) and Path(jar).expanduser().is_file()
    dot_env = env.get(GRAPHVIZ_DOT_ENV, "").strip()
    if dot_env:
        dot = dot_env if Path(dot_env).expanduser().is_file() else ""
    else:
        dot = which("dot") or ""
    dot_present = bool(dot)

    resolved_engine = layout_engine
    if layout_engine == "auto":
        resolved_engine = "dot" if dot_present else "smetana"

    size_flag = f"-DPLANTUML_LIMIT_SIZE={PLANTUML_LIMIT_SIZE}"
    format_flag = f"-t{output_format}"
    command: list[str] = []
    renderer = "missing"
    if plantuml_cli:
        renderer = "plantuml"
        command = ["plantuml", size_flag, format_flag, "-charset", "UTF-8", source_path]
    elif java and jar_present:
        renderer = "java_jar"
        command = [
            "java",
            "-Djava.awt.headless=true",
            size_flag,
            "-jar",
            jar,
            format_flag,
            "-charset",
            "UTF-8",
            source_path,
        ]

    blockers: list[str] = []
    if renderer == "missing":
        blockers.append(
            "no PlantUML renderer found: install `plantuml` on PATH (brew install plantuml / apt install plantuml) "
            f"or set {PLANTUML_JAR_ENV} to a downloaded plantuml.jar with `java` on PATH"
        )
    if layout_engine == "dot" and not dot_present:
        blockers.append("layout engine `dot` requested but Graphviz `dot` is not on PATH; use --layout smetana or install graphviz")
    notes: list[str] = []
    if resolved_engine == "smetana":
        notes.append("Graphviz `dot` not available; the source carries `!pragma layout smetana` so PlantUML lays out without it")
    if renderer == "java_jar" and java == "/usr/bin/java":
        notes.append(
            "/usr/bin/java on macOS is a launcher stub that fails without an installed JDK; "
            "`java -version` must succeed before this command can render"
        )
    if output_format == "svg":
        notes.append("SVG does not preview inline on Slack or Discord; attach PNG when the diagram must show as a picture")

    # String surgery, not Path.with_suffix: pathlib re-renders the separators
    # of the host OS, so a caller's `/tmp/x.puml` came back as `\tmp\x.png`
    # on Windows and the plan named a file the render command never writes.
    if source_path.endswith(".puml"):
        output_path = source_path[: -len("puml")] + output_format
    else:
        output_path = f"{source_path}.{output_format}"
    return {
        "schema_version": UML_RENDER_PLAN_SCHEMA_VERSION,
        "status": "ready" if not blockers else "blocked",
        "renderer": renderer,
        "layout_engine": resolved_engine,
        "output_format": output_format,
        "source_path": source_path,
        "expected_output_path": output_path,
        "command": command,
        "probes": {
            "plantuml_cli": plantuml_cli or "",
            "java": java or "",
            "plantuml_jar": jar if jar_present else "",
            "dot": dot if dot_present else "",
        },
        "blockers": blockers,
        "notes": notes,
        "claim_boundary": (
            "A render plan names a command; it is not render evidence. "
            "The image exists only when the command's exit status and output file are observed."
        ),
    }


def render_uml_text(payload: dict[str, Any]) -> str:
    """Human summary printed after the source when stdout is not a pipe target."""
    model = payload["model"]
    plan = payload["render_plan"]
    layout = model["layout"]
    omissions = model["omissions"]
    lines = [
        "OMJ codebase UML",
        f"Repo: {model['repo_root']}",
        f"View: {model['view']['level']} (depth {model['view']['depth']}"
        + (f", focus {model['view']['focus']}" if model["view"]["focus"] else "")
        + ")",
        f"Nodes: {layout['node_count']}  Edges: {layout['edge_count']}  Direction: {layout['direction']}",
        "Omitted: "
        f"{len(omissions['units_folded'])} units folded, {omissions['edges_pruned']} edges pruned, "
        f"{omissions['interface_symbols_hidden']} interface symbols hidden, "
        f"{omissions['units_outside_focus']} units outside focus, "
        f"{omissions['test_files_skipped']} test files skipped",
    ]
    if payload.get("source_path"):
        lines.append(f"Source: {payload['source_path']}")
    lines.append(f"Render: {plan['status']} via {plan['renderer']} ({plan['layout_engine']} layout)")
    if plan["command"]:
        lines.append("  " + " ".join(plan["command"]))
    for blocker in plan["blockers"]:
        lines.append(f"  blocker: {blocker}")
    for note in plan["notes"]:
        lines.append(f"  note: {note}")
    lines.extend(["Boundary", f"  {model['claim_boundary']}", f"  {plan['claim_boundary']}"])
    return "\n".join(lines)


# --- model helpers -----------------------------------------------------------


def _new_unit(unit_id: str) -> dict[str, Any]:
    return {
        "id": unit_id,
        "file_count": 0,
        "symbol_count": 0,
        "entrypoint_tags": [],
        "interface": [],
        "interface_hidden": 0,
        "_paths": [],
    }


def _normalize_focus(focus: str) -> str:
    cleaned = focus.strip().replace("\\", "/").strip("/")
    return cleaned


def _unit_id(path: str, *, level: str, depth: int) -> str:
    parts = path.split("/")
    directory = parts[:-1]
    if level == "module":
        stem = parts[-1].removesuffix(".py")
        if stem == "__init__":
            return "/".join(directory) if directory else ROOT_UNIT_ID
        return "/".join([*directory, stem])
    if not directory:
        return ROOT_UNIT_ID
    return "/".join(directory[:depth])


def _group_of(unit_id: str, *, level: str, depth: int) -> str:
    if unit_id in (ROOT_UNIT_ID, OTHER_UNIT_ID):
        return ""
    parts = unit_id.split("/")
    if level == "package" and depth <= 1:
        return ""
    if len(parts) <= 1:
        return ""
    return parts[0]


def _aliases_for(unit_ids: list[str]) -> dict[str, str]:
    """Sanitized PlantUML aliases, deterministically deduplicated.

    Sanitizing maps every non-alphanumeric character to `_`, so distinct unit
    ids like `src/a-b` and `src/a_b` collapse to one alias -- and PlantUML
    silently merges same-alias nodes. Suffix the collisions instead.
    """
    aliases: dict[str, str] = {}
    used: dict[str, int] = {}
    for unit_id in unit_ids:
        cleaned = "".join(ch if ch.isalnum() else "_" for ch in unit_id)
        base = f"u_{cleaned.strip('_') or 'root'}"
        count = used.get(base, 0)
        used[base] = count + 1
        aliases[unit_id] = base if count == 0 else f"{base}_{count + 1}"
    return aliases


def _collect_interfaces(
    graph: dict[str, Any],
    units: dict[str, dict[str, Any]],
    unit_by_path: dict[str, str],
    *,
    max_interface: int,
) -> int:
    """Attach public top-level symbols to units; return how many were hidden by the cap.

    The symbols a unit exposes are ranked by cross-unit fan-in -- how many
    files in *other* units import them by name -- so the listed interface is
    the one the rest of the codebase actually uses, not an alphabetical
    sample. Ties fall back to facade (`__init__`) first, classes before
    functions, error types last, then name.
    """
    symbols = [
        symbol
        for symbol in graph.get("symbols", [])
        if isinstance(symbol, dict) and str(symbol.get("path", "")) in unit_by_path
    ]
    # A nested definition always sits under a top-level one, so the shortest
    # qualified name in a file is the top-level depth for that file -- which
    # holds however pyproject maps the file to a dotted module name.
    top_level_depth: dict[str, int] = {}
    for symbol in symbols:
        path = str(symbol["path"])
        depth = len(str(symbol.get("qualified_name", "")).split("."))
        top_level_depth[path] = min(depth, top_level_depth.get(path, depth))

    unit_by_qualified: dict[str, str] = {}
    public: list[tuple[str, str, str, str]] = []  # (unit, qualified, kind, name)
    for symbol in symbols:
        path = str(symbol["path"])
        name = str(symbol.get("name", ""))
        qualified = str(symbol.get("qualified_name", ""))
        if not name or name.startswith("_"):
            continue
        if len(qualified.split(".")) != top_level_depth[path]:
            continue
        unit_by_qualified[qualified] = unit_by_path[path]
        public.append((unit_by_path[path], qualified, str(symbol.get("kind", "")), name, path))

    importers: dict[str, set[str]] = {}
    for record in graph.get("files", []):
        if not isinstance(record, dict):
            continue
        source_path = str(record.get("path", ""))
        source_unit = unit_by_path.get(source_path)
        if source_unit is None:
            continue
        for item in record.get("imports", []):
            if not isinstance(item, dict) or item.get("kind") != "from_import" or not item.get("name"):
                continue
            qualified = f"{item.get('module', '')}.{item['name']}"
            target_unit = unit_by_qualified.get(qualified)
            if target_unit is not None and target_unit != source_unit:
                importers.setdefault(qualified, set()).add(source_path)
    fan_in = {qualified: len(paths) for qualified, paths in importers.items()}

    candidates: dict[str, list[tuple[int, int, int, int, str, str]]] = {}
    for unit_id, qualified, kind, name, path in public:
        facade_rank = 0 if path.endswith("/__init__.py") else 1
        kind_rank = 0 if kind == "class" else 1
        error_rank = 1 if name.endswith(("Error", "Exception")) else 0
        rendered = name if kind == "class" else f"{name}()"
        candidates.setdefault(unit_id, []).append(
            (-fan_in.get(qualified, 0), facade_rank, kind_rank, error_rank, name, rendered)
        )

    hidden_total = 0
    for unit_id, unit in units.items():
        ordered = sorted(set(candidates.get(unit_id, [])))
        deduped = list(dict.fromkeys(item[5] for item in ordered))
        unit["interface"] = deduped[:max_interface]
        unit["interface_hidden"] = max(0, len(deduped) - max_interface)
        hidden_total += unit["interface_hidden"]
    return hidden_total


def _focus_units(
    units: dict[str, dict[str, Any]],
    edge_weights: dict[tuple[str, str], int],
    focus_prefix: str,
) -> tuple[set[str], set[str]]:
    """Return (units inside the focus prefix, those plus their direct import neighbours)."""
    inside = {unit_id for unit_id in units if unit_id == focus_prefix or unit_id.startswith(focus_prefix + "/")}
    neighbours: set[str] = set()
    for (source, target) in edge_weights:
        if source in inside:
            neighbours.add(target)
        if target in inside:
            neighbours.add(source)
    return inside, inside | neighbours


def _fold_to_budget(
    units: dict[str, dict[str, Any]],
    edge_weights: dict[tuple[str, str], int],
    *,
    max_nodes: int,
    priority: set[str],
) -> tuple[dict[str, dict[str, Any]], dict[tuple[str, str], int], list[str], int]:
    """Keep the highest-degree units (focus units first) and fold the rest into one node.

    Edges that land on the folded node are counted, not kept: drawing them
    turns the fold into a hub every box points at, which is the layout
    failure the fold exists to prevent.
    """
    if len(units) <= max_nodes:
        return units, edge_weights, [], 0
    degree: dict[str, int] = {unit_id: 0 for unit_id in units}
    for (source, target), weight in edge_weights.items():
        degree[source] += weight
        degree[target] += weight
    ranked = sorted(
        units,
        key=lambda unit_id: (unit_id not in priority, -degree[unit_id], -units[unit_id]["symbol_count"], unit_id),
    )
    keep = set(ranked[: max_nodes - 1])
    folded = sorted(unit_id for unit_id in units if unit_id not in keep)

    other = _new_unit(OTHER_UNIT_ID)
    other["folded_unit_count"] = len(folded)
    for unit_id in folded:
        other["file_count"] += units[unit_id]["file_count"]
        other["symbol_count"] += units[unit_id]["symbol_count"]
    kept_units = {unit_id: unit for unit_id, unit in units.items() if unit_id in keep}
    kept_units[OTHER_UNIT_ID] = other

    kept_edges: dict[tuple[str, str], int] = {}
    folded_edges = 0
    for (source, target), weight in edge_weights.items():
        if source in keep and target in keep:
            kept_edges[(source, target)] = weight
        elif source in keep or target in keep:
            folded_edges += 1
    return kept_units, kept_edges, folded, folded_edges


def _prune_edges(
    units: dict[str, dict[str, Any]],
    edge_weights: dict[tuple[str, str], int],
) -> tuple[list[dict[str, Any]], int, int]:
    budget = EDGE_BUDGET_PER_NODE * len(units)
    ordered = sorted(edge_weights.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
    kept = ordered[:budget]
    pruned = len(ordered) - len(kept)
    min_weight = min((weight for _, weight in kept), default=0)
    edges = [
        {"from": source, "to": target, "weight": weight}
        for (source, target), weight in sorted(kept, key=lambda item: (item[0][0], item[0][1]))
    ]
    return edges, pruned, min_weight


def _hardening_directives(direction: str) -> list[str]:
    return [
        f"{direction} direction",
        "skinparam linetype ortho",
        "skinparam nodesep 40",
        "skinparam ranksep 70",
        "skinparam wrapWidth 220",
        "skinparam packageStyle rectangle",
        "hide circle",
        "hide empty members",
        f"node cap {DEFAULT_MAX_NODES} (override --max-nodes); overflow folds into {OTHER_UNIT_ID}",
        f"edge budget {EDGE_BUDGET_PER_NODE} per node; lightest import edges pruned first",
        f"PLANTUML_LIMIT_SIZE={PLANTUML_LIMIT_SIZE} on the render command",
    ]


# --- PlantUML helpers ---------------------------------------------------------


def _escape(text: str) -> str:
    return text.replace('"', "'")


def _node_lines(node: dict[str, Any], colors: dict[str, str]) -> list[str]:
    stereotype = "package"
    color = ""
    if node["id"] == OTHER_UNIT_ID:
        stereotype = "folded"
        color = f" {colors['other_bg']}"
    elif node["entrypoint_tags"]:
        stereotype = "entrypoint"
        color = f" {colors['entrypoint_bg']}"
    label = node["label"]
    if node["id"] == OTHER_UNIT_ID:
        label = f"+{node['folded_unit_count']} more units"
    lines = [f'class "{_escape(label)}" as {node["alias"]} <<{stereotype}>>{color} {{']
    lines.append(f"  {{field}} {node['file_count']} files · {node['symbol_count']} symbols")
    if node["interface"]:
        lines.append("  ..")
        for member in node["interface"]:
            lines.append(f"  {{method}} +{member}")
        if node["interface_hidden"]:
            lines.append(f"  {{method}} … +{node['interface_hidden']} more")
    lines.append("}")
    return lines


def _legend_lines(model: dict[str, Any]) -> list[str]:
    omissions = model["omissions"]
    layout = model["layout"]
    parts = [
        f"{layout['node_count']} units, {layout['edge_count']} import edges",
        f"solid arrow ≥ {layout['strong_edge_weight']} imports, dotted below",
    ]
    if omissions["units_folded"]:
        parts.append(f"{len(omissions['units_folded'])} units folded")
    if omissions["edges_pruned"]:
        parts.append(f"{omissions['edges_pruned']} light edges pruned")
    if omissions["edges_into_folded_units"]:
        parts.append(f"{omissions['edges_into_folded_units']} edges into folded units not drawn")
    if omissions["interface_symbols_hidden"]:
        parts.append(f"{omissions['interface_symbols_hidden']} public symbols hidden")
    return [
        "legend right",
        *[f"  {part}" for part in parts],
        "endlegend",
        "caption prepared local context by omj codegraph uml — not architecture proof",
    ]
