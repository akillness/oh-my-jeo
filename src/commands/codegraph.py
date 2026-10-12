from __future__ import annotations

import argparse
from pathlib import Path

from ..codegraph import (
    build_codegraph,
    build_handoff_context,
    build_uml_model,
    codegraph_artifact_path,
    render_build_text,
    render_handoff_text,
    render_plan,
    render_plantuml,
    render_summary_text,
    render_test_selection_text,
    render_uml_text,
    select_tests_for_changes,
    summarize_codegraph,
    write_codegraph_artifact,
)
from ..installer import OmjError
from .common import _print_json, _wants_json


def cmd_codegraph_build(args: argparse.Namespace) -> int:
    try:
        graph = build_codegraph(args.repo)
        if args.write:
            artifact_path = codegraph_artifact_path(Path(graph["repo_root"]))
            graph["artifact_path"] = str(artifact_path)
            write_codegraph_artifact(graph)
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    if _wants_json(args):
        _print_json(graph)
    else:
        print(render_build_text(graph))
    return 0


def cmd_codegraph_summary(args: argparse.Namespace) -> int:
    try:
        graph = build_codegraph(args.repo)
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    summary = summarize_codegraph(graph)
    if _wants_json(args):
        _print_json(summary)
    else:
        print(render_summary_text(summary))
    return 0


def cmd_codegraph_handoff(args: argparse.Namespace) -> int:
    try:
        graph = build_codegraph(args.repo)
        context = build_handoff_context(graph, task=args.task)
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    if _wants_json(args):
        _print_json(context)
    else:
        print(render_handoff_text(context))
    return 0


def cmd_codegraph_tests(args: argparse.Namespace) -> int:
    try:
        graph = build_codegraph(args.repo)
        payload = select_tests_for_changes(graph, args.changed or [])
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    if _wants_json(args):
        _print_json(payload)
    else:
        print(render_test_selection_text(payload))
    return 0


def cmd_codegraph_uml(args: argparse.Namespace) -> int:
    try:
        graph = build_codegraph(args.repo)
        model = build_uml_model(graph, level=args.level, depth=args.depth, max_nodes=args.max_nodes, max_interface=args.max_interface)
        plantuml = render_plantuml(model, theme=args.theme)
        plan = render_plan(source_path=args.source or "codegraph.puml", output_format=args.format, layout_engine=args.engine)
        payload = {"schema_version": "omj_codegraph_uml_result/v1", "model": model, "plantuml": plantuml, "render_plan": plan}
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    if _wants_json(args):
        _print_json(payload)
    else:
        print(render_uml_text(payload))
        print(plantuml)
    return 0


def _add_codegraph_commands(sub) -> None:
    codegraph = sub.add_parser(
        "codegraph",
        help="Build static local codegraph artifacts for prepared coding context.",
    )
    codegraph_sub = codegraph.add_subparsers(dest="codegraph_command", required=True)

    build = codegraph_sub.add_parser("build", help="Build a static local Python AST codegraph.")
    build.add_argument("--repo", default=".", help="Repository root to scan.")
    build.add_argument("--write", action="store_true", help="Write .omj/codegraph/codegraph.json.")
    build.add_argument("--json", action="store_true", help="Print the full codegraph artifact as JSON.")
    build.set_defaults(func=cmd_codegraph_build)

    summary = codegraph_sub.add_parser("summary", help="Print a compact static codegraph summary.")
    summary.add_argument("--repo", default=".", help="Repository root to scan.")
    summary.add_argument("--json", action="store_true", help="Print the summary payload as JSON.")
    summary.set_defaults(func=cmd_codegraph_summary)

    handoff = codegraph_sub.add_parser("handoff", help="Build compact prepared context for coding agents.")
    handoff.add_argument("--repo", default=".", help="Repository root to scan.")
    handoff.add_argument("--task", required=True, help="Task description used to rank relevant files and symbols.")
    handoff.add_argument("--json", action="store_true", help="Print the handoff context payload as JSON.")
    handoff.set_defaults(func=cmd_codegraph_handoff)

    tests = codegraph_sub.add_parser("tests", help="Select tests by reverse import reachability.")
    tests.add_argument("--repo", default=".", help="Repository root to scan.")
    tests.add_argument("--changed", action="append", required=True, help="Changed path (repeat for multiple files).")
    tests.add_argument("--json", action="store_true", help="Print the selection payload as JSON.")
    tests.set_defaults(func=cmd_codegraph_tests)

    uml = codegraph_sub.add_parser("uml", help="Build bounded interface-level PlantUML from the static graph.")
    uml.add_argument("--repo", default=".", help="Repository root to scan.")
    uml.add_argument("--level", choices=("package", "module"), default="package")
    uml.add_argument("--depth", type=int, default=2)
    uml.add_argument("--format", choices=("png", "svg"), default="png")
    uml.add_argument("--source", default=None)
    uml.add_argument("--engine", choices=("auto", "dot", "smetana"), default="auto")
    uml.add_argument("--theme", choices=("omh", "mono"), default="omh")
    uml.add_argument("--max-nodes", type=int, default=16)
    uml.add_argument("--max-interface", type=int, default=6)
    uml.add_argument("--json", action="store_true", help="Print the UML payload as JSON.")
    uml.set_defaults(func=cmd_codegraph_uml)
