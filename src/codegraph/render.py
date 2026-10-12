from __future__ import annotations

import math
import re
from typing import Any

from .schema import (
    CLAIM_BOUNDARY,
    CODEGRAPH_CONTEXT_SCHEMA_VERSION,
    CODEGRAPH_SUMMARY_SCHEMA_VERSION,
)


MAX_SUMMARY_ENTRYPOINTS = 20
MAX_SUMMARY_WARNINGS = 10
MAX_HANDOFF_FILES = 12
MAX_HANDOFF_SYMBOLS = 20

# Personalized PageRank over the scanner's `imports_internal` edges. Rank flows
# from an importer to what it imports, so a module the seeds depend on collects
# rank even when it shares no word with the task. The constants are fixed so
# the same graph and seed always give the same order: iteration stops at the
# tolerance or the cap, whichever comes first, and equal ranks break by path.
PAGERANK_DAMPING = 0.85
PAGERANK_MAX_ITERATIONS = 100
PAGERANK_TOLERANCE = 1e-12


def summarize_codegraph(graph: dict[str, Any]) -> dict[str, Any]:
    entrypoint_files = [
        {
            "path": record["path"],
            "entrypoint_tags": record["entrypoint_tags"],
        }
        for record in graph.get("files", [])
        if isinstance(record, dict) and record.get("entrypoint_tags")
    ]
    return {
        "schema_version": CODEGRAPH_SUMMARY_SCHEMA_VERSION,
        "repo_root": graph["repo_root"],
        "generated_at": graph["generated_at"],
        "stats": graph["stats"],
        "entrypoint_files": entrypoint_files[:MAX_SUMMARY_ENTRYPOINTS],
        "entrypoint_file_count": len(entrypoint_files),
        "warnings": list(graph.get("warnings", []))[:MAX_SUMMARY_WARNINGS],
        "warning_count": len(graph.get("warnings", [])),
        "claim_boundary": graph.get("claim_boundary", CLAIM_BOUNDARY),
    }


def build_handoff_context(
    graph: dict[str, Any], *, task: str, changed_paths: list[str] | tuple[str, ...] = ()
) -> dict[str, Any]:
    terms = _task_terms(task)
    changed = sorted(dict.fromkeys(str(path) for path in changed_paths))
    focus_files = _ranked_focus_files(graph, terms, changed)
    focus_symbols = _ranked_focus_symbols(graph, terms)
    summary = summarize_codegraph(graph)
    return {
        "schema_version": CODEGRAPH_CONTEXT_SCHEMA_VERSION,
        "task": task,
        "repo_root": graph["repo_root"],
        "generated_at": graph["generated_at"],
        "summary": summary,
        "task_terms": terms,
        "changed_paths": changed,
        "focus_files": focus_files,
        "focus_symbols": focus_symbols,
        "entrypoint_files": summary["entrypoint_files"],
        "warnings": summary["warnings"],
        "claim_boundary": graph.get("claim_boundary", CLAIM_BOUNDARY),
    }


def render_summary_text(summary: dict[str, Any]) -> str:
    stats = summary["stats"]
    lines = [
        "OMJ codegraph summary",
        f"Repo: {summary['repo_root']}",
        f"Generated: {summary['generated_at']}",
        "Stats",
        f"  Files: {stats['file_count']} Python ({stats['parsed_file_count']} parsed, {stats['parse_error_count']} parse errors)",
        f"  Symbols: {stats['symbol_count']}",
        f"  Edges: {stats['edge_count']} ({stats['internal_import_edge_count']} internal imports)",
        f"  Entrypoint files: {stats['entrypoint_file_count']}",
    ]
    entrypoints = summary.get("entrypoint_files", [])
    if entrypoints:
        lines.append("Entrypoints")
        for record in entrypoints[:MAX_SUMMARY_ENTRYPOINTS]:
            lines.append(f"  - {record['path']}: {', '.join(record['entrypoint_tags'])}")
    if summary.get("warnings"):
        lines.append("Warnings")
        for warning in summary["warnings"]:
            lines.append(f"  - {warning}")
        if summary.get("warning_count", 0) > len(summary["warnings"]):
            lines.append(f"  - ... {summary['warning_count'] - len(summary['warnings'])} more")
    lines.extend(
        [
            "Boundary",
            f"  {summary['claim_boundary']}",
            "For machine-readable output, rerun with `--json`.",
        ]
    )
    return "\n".join(lines)


def render_build_text(graph: dict[str, Any]) -> str:
    summary = summarize_codegraph(graph)
    lines = render_summary_text(summary).splitlines()
    artifact_path = graph.get("artifact_path")
    if artifact_path:
        lines.insert(1, f"Artifact: {artifact_path}")
    return "\n".join(lines)


def render_handoff_text(context: dict[str, Any]) -> str:
    lines = [
        "OMJ codegraph handoff context",
        f"Task: {context['task']}",
        f"Repo: {context['repo_root']}",
        "Focus files",
    ]
    focus_files = context.get("focus_files", [])
    if focus_files:
        for record in focus_files:
            tags = ", ".join(record.get("entrypoint_tags", [])) or "no entrypoint tags"
            lines.append(f"  - {record['path']} ({tags})")
    else:
        lines.append("  - none")
    focus_symbols = context.get("focus_symbols", [])
    if focus_symbols:
        lines.append("Focus symbols")
        for record in focus_symbols[:MAX_HANDOFF_SYMBOLS]:
            lines.append(f"  - {record['qualified_name']} ({record['kind']}, {record['path']}:{record['line']})")
    if context.get("warnings"):
        lines.append("Warnings")
        for warning in context["warnings"]:
            lines.append(f"  - {warning}")
    lines.extend(
        [
            "Boundary",
            f"  {context['claim_boundary']}",
            "For machine-readable output, rerun with `--json`.",
        ]
    )
    return "\n".join(lines)


def _ranked_focus_files(graph: dict[str, Any], terms: list[str], changed: list[str]) -> list[dict[str, Any]]:
    records = {str(record["path"]): record for record in graph.get("files", []) if isinstance(record, dict)}
    haystacks = {path: _file_haystack(record) for path, record in records.items()}
    # A term found in every file names nothing; weighting each term by how few
    # files carry it keeps "the" from seeding the whole repository and handing
    # the walk to whatever module everything imports.
    term_weights = {}
    for term in terms:
        carriers = sum(1 for haystack in haystacks.values() if term in haystack)
        if carriers:
            term_weights[term] = math.log(len(records) / carriers)
    seeds: dict[str, float] = {}
    for path, haystack in haystacks.items():
        score = sum(weight for term, weight in term_weights.items() if term in haystack)
        if score > 0:
            seeds[path] = score
    seeds = dict(sorted(seeds.items(), key=lambda item: (-item[1], item[0]))[:MAX_HANDOFF_FILES])
    # A changed file is in play whatever the task says, so it seeds at least
    # as strongly as the best term match.
    changed_weight = max(seeds.values(), default=1)
    for path in changed:
        if path in records:
            seeds[path] = seeds.get(path, 0) + changed_weight
    ranks = personalized_pagerank(sorted(records), _internal_import_edges(records, graph), seeds)
    ordered = sorted((path for path, rank in ranks.items() if rank > 0), key=lambda path: (-ranks[path], path))
    return [_compact_file_record(records[path]) for path in ordered[:MAX_HANDOFF_FILES]]


def personalized_pagerank(nodes: list[str], edges: dict[str, list[str]], seeds: dict[str, float]) -> dict[str, float]:
    """Rank `nodes` by power iteration, restarting at `seeds` (uniform when none).

    A node with no outgoing edge hands its rank back through the restart
    vector, so ranks keep summing to one and a sink cannot absorb the walk.
    `nodes` and each edge list must already be sorted: the summation order is
    part of what makes the floats, and so the order, reproducible.
    """
    if not nodes:
        return {}
    weights = {node: float(seeds.get(node, 0)) for node in nodes}
    total = sum(weights.values())
    if total <= 0:
        weights = {node: 1.0 for node in nodes}
        total = float(len(nodes))
    restart = {node: weight / total for node, weight in weights.items()}
    ranks = dict(restart)
    for _ in range(PAGERANK_MAX_ITERATIONS):
        flowing = {node: 0.0 for node in nodes}
        dangling = 0.0
        for node in nodes:
            targets = edges.get(node, [])
            if not targets:
                dangling += ranks[node]
                continue
            share = ranks[node] / len(targets)
            for target in targets:
                flowing[target] += share
        updated = {
            node: (1 - PAGERANK_DAMPING) * restart[node] + PAGERANK_DAMPING * (flowing[node] + dangling * restart[node])
            for node in nodes
        }
        delta = sum(abs(updated[node] - ranks[node]) for node in nodes)
        ranks = updated
        if delta < PAGERANK_TOLERANCE:
            break
    return ranks


def _internal_import_edges(records: dict[str, Any], graph: dict[str, Any]) -> dict[str, list[str]]:
    edges: dict[str, set[str]] = {}
    for edge in graph.get("edges", []):
        if not isinstance(edge, dict) or edge.get("kind") != "imports_internal":
            continue
        source, target = str(edge.get("from", "")), str(edge.get("to", ""))
        if source != target and source in records and target in records:
            edges.setdefault(source, set()).add(target)
    return {source: sorted(targets) for source, targets in edges.items()}


def _ranked_focus_symbols(graph: dict[str, Any], terms: list[str]) -> list[dict[str, Any]]:
    scored: list[tuple[int, str, dict[str, Any]]] = []
    for symbol in graph.get("symbols", []):
        if not isinstance(symbol, dict):
            continue
        haystack = " ".join(str(symbol.get(key, "")) for key in ("name", "qualified_name", "kind", "path")).lower()
        score = _score_text(haystack, terms)
        if score:
            scored.append((score, str(symbol["qualified_name"]), symbol))
    if not scored:
        scored = [
            (1, str(symbol["qualified_name"]), symbol)
            for symbol in graph.get("symbols", [])[:MAX_HANDOFF_SYMBOLS]
            if isinstance(symbol, dict)
        ]
    return [
        {
            "name": symbol["name"],
            "qualified_name": symbol["qualified_name"],
            "kind": symbol["kind"],
            "path": symbol["path"],
            "line": symbol["line"],
        }
        for _, _, symbol in sorted(scored, key=lambda item: (-item[0], item[1]))[:MAX_HANDOFF_SYMBOLS]
    ]


def _compact_file_record(record: dict[str, Any]) -> dict[str, Any]:
    imports = []
    for item in record.get("imports", [])[:12]:
        if not isinstance(item, dict):
            continue
        target = str(item.get("module") or "")
        if item.get("name"):
            target = f"{target}:{item['name']}"
        imports.append(target)
    compact = {
        "path": record["path"],
        "kind": record["kind"],
        "entrypoint_tags": record.get("entrypoint_tags", []),
        "defines": record.get("defines", [])[:12],
        "imports": imports,
    }
    if record.get("parse_error"):
        compact["parse_error"] = record["parse_error"]
    return compact


def _file_haystack(record: dict[str, Any]) -> str:
    parts: list[str] = [str(record.get("path", ""))]
    parts.extend(str(tag) for tag in record.get("entrypoint_tags", []))
    parts.extend(str(name) for name in record.get("defines", []))
    for item in record.get("imports", []):
        if isinstance(item, dict):
            parts.append(str(item.get("module", "")))
            parts.append(str(item.get("name", "")))
    return " ".join(parts).lower()


def _task_terms(task: str) -> list[str]:
    return sorted(dict.fromkeys(term.lower() for term in re.findall(r"[A-Za-z0-9_]+", task) if len(term) >= 3))


def _score_text(text: str, terms: list[str]) -> int:
    if not terms:
        return 0
    score = 0
    for term in terms:
        if term in text:
            score += 1
    return score
