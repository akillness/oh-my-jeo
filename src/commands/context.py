from __future__ import annotations

import argparse
import dataclasses
import os
import stat
import sys
from pathlib import Path

from ..context import build_context_brief
from ..installer import OmjError
from ..workflows.project_terms import (
    MAX_PROJECT_TERMS_SOURCE_BYTES,
    PROJECT_TERMS_BOUNDARY,
    build_project_terms_capture_inputs,
    parse_project_terms,
)
from .common import _print_json, _wants_json


def _read_project_terms_source(path: str) -> bytes:
    if path == "-":
        stream = getattr(sys.stdin, "buffer", sys.stdin)
        raw = stream.read(MAX_PROJECT_TERMS_SOURCE_BYTES + 1)
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
    else:
        source = Path(path).expanduser()
        flags = os.O_RDONLY | os.O_NONBLOCK
        try:
            fd = os.open(source, flags)
        except FileNotFoundError:
            raise
        except OSError as exc:
            raise ValueError("project_terms_source_not_regular_file") from exc
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise ValueError("project_terms_source_not_regular_file")
            if info.st_size > MAX_PROJECT_TERMS_SOURCE_BYTES:
                raise ValueError("project_terms_source_too_large")
            raw = os.read(fd, MAX_PROJECT_TERMS_SOURCE_BYTES + 1)
        finally:
            os.close(fd)
    if len(raw) > MAX_PROJECT_TERMS_SOURCE_BYTES:
        raise ValueError("project_terms_source_too_large")
    return raw


def _project_terms_payload(path: str) -> dict[str, object]:
    source = _read_project_terms_source(path)
    document = parse_project_terms(source)
    captures = build_project_terms_capture_inputs(document)
    return {
        "document": dataclasses.asdict(document),
        "captures": [dataclasses.asdict(capture) for capture in captures],
        "source": {"path": path, "bytes": len(source), "raw_persisted": False},
        "prepared_state": "prepared_not_observed",
        "claim_boundary": PROJECT_TERMS_BOUNDARY,
    }


def cmd_context_terms_capture(args: argparse.Namespace) -> int:
    try:
        payload = _project_terms_payload(args.source)
    except (OSError, ValueError, TypeError) as exc:
        raise OmjError(str(exc)) from exc
    payload["schema_version"] = "omj_project_terms_capture/v1"
    if _wants_json(args):
        _print_json(payload)
    else:
        document = payload["document"]
        domains = document.get("domains", []) if isinstance(document, dict) else []
        print("OMJ project terminology capture")
        print(f"  Schema: {document.get('schema_version') if isinstance(document, dict) else ''}")
        print(f"  Source digest: {document.get('source_sha256') if isinstance(document, dict) else ''}")
        print(f"  Domains: {len(domains) if isinstance(domains, list) else 0}")
        print("  Raw source persisted: no")
        print(f"Boundary: {PROJECT_TERMS_BOUNDARY}")
    return 0


def cmd_context_terms_inspect(args: argparse.Namespace) -> int:
    try:
        payload = _project_terms_payload(args.source)
    except (OSError, ValueError, TypeError) as exc:
        raise OmjError(str(exc)) from exc
    payload["schema_version"] = "omj_project_terms_inspect/v1"
    if _wants_json(args):
        _print_json(payload)
    else:
        document = payload["document"]
        domains = document.get("domains", []) if isinstance(document, dict) else []
        print("OMJ project terminology inspection")
        print(f"  Source digest: {document.get('source_sha256') if isinstance(document, dict) else ''}")
        for domain in domains if isinstance(domains, list) else []:
            if not isinstance(domain, dict):
                continue
            print(f"  - {domain.get('domain_id')}: {len(domain.get('mappings', []))} mappings")
        print("  Prepared state: prepared_not_observed")
        print(f"Boundary: {PROJECT_TERMS_BOUNDARY}")
    return 0




def cmd_context_brief(args: argparse.Namespace) -> int:
    message = " ".join(args.message).strip()
    payload = build_context_brief(
        message,
        source=args.source,
        max_hints=args.limit,
        include_prompt_context=args.prompt_context,
    )
    if _wants_json(args):
        _print_json(payload)
    else:
        _print_context_brief_summary(payload)
    return 0


def _print_context_brief_summary(payload: dict[str, object]) -> None:
    print("OMJ context brief")
    print("Summary")
    print(f"  Purpose: {payload['purpose']}")
    print(f"  Chat rule: {payload['chat_rule']}")
    route_hint = payload.get("route_hint")
    if isinstance(route_hint, dict):
        primary = str(route_hint.get("primary_workflow") or "")
        action = str(route_hint.get("primary_next_action") or "")
        if primary:
            print(f"  Route hint: {primary} -> {action}")
        else:
            print("  Route hint: no strong message-specific hint")
    catalog_question = payload.get("catalog_question")
    if isinstance(catalog_question, dict) and catalog_question.get("status") == "matched":
        print(
            "  Catalog question: "
            f"{catalog_question.get('next_action')} via {catalog_question.get('recommended_tool')}"
        )
    print("Workflow lanes")
    lanes = payload.get("lanes", [])
    if isinstance(lanes, list):
        for lane in lanes:
            if not isinstance(lane, dict):
                continue
            skills = [str(skill) for skill in lane.get("skills", [])[:5]]
            print(f"  - {lane.get('label')}")
            print(f"    Use for: {lane.get('use_for')}")
            print(f"    Key workflows: {', '.join(skills)}")
    checkpoint = payload.get("generic_tool_checkpoint")
    if isinstance(checkpoint, dict):
        print("Generic tool checkpoint")
        print(f"  {checkpoint.get('body')}")
    print("Response contract")
    contract = payload.get("normal_response_contract")
    if isinstance(contract, dict):
        print(f"  - {contract.get('when_user_asks_capabilities')}")
        print(f"  - {contract.get('when_request_matches_lane')}")
        print(f"  - {contract.get('when_generic_tool_is_available')}")
    print("Boundary")
    print(f"  {payload['claim_boundary']}")
    print("For machine-readable output, rerun with `--json`.")


def _add_context_commands(sub) -> None:
    context = sub.add_parser("context", help="Build compact Hermes-facing OMJ context for wrappers or plugin hosts.")
    context_sub = context.add_subparsers(dest="context_command", required=True)

    brief = context_sub.add_parser("brief", help="Show the OMJ mental model and optional message route hint.")
    brief.add_argument("message", nargs="*", help="Optional current user request to route without echoing raw prompt text.")
    brief.add_argument("--source", default="generic", help="Host or wrapper source label.")
    brief.add_argument("--limit", type=int, default=2, help="Maximum message-specific route hints.")
    brief.add_argument(
        "--prompt-context",
        action="store_true",
        help="Include compact prompt-context text for a Hermes hook or wrapper injection.",
    )
    brief.add_argument("--json", action="store_true", help="Print machine-readable context payload.")
    brief.set_defaults(func=cmd_context_brief)
    def _add_terms_parser(parser: argparse.ArgumentParser, handler) -> None:
        parser.add_argument("--source", "--source-file", required=True, dest="source", help="PROJECT_TERMS.md path, or '-' for stdin.")
        parser.add_argument("--json", action="store_true", help="Print the full machine-readable payload.")
        parser.set_defaults(func=handler)

    terms = context_sub.add_parser(
        "terms",
        aliases=("project-terms",),
        help="Capture or inspect bounded project terminology metadata.",
    )
    terms_sub = terms.add_subparsers(dest="terms_command", required=True)
    capture = terms_sub.add_parser("capture", help="Parse terminology metadata-only capture inputs.")
    _add_terms_parser(capture, cmd_context_terms_capture)
    inspect = terms_sub.add_parser("inspect", help="Inspect terminology metadata without retaining source text.")
    _add_terms_parser(inspect, cmd_context_terms_inspect)

    for alias, handler, help_text in (
        ("terms-capture", cmd_context_terms_capture, "Capture bounded project terminology metadata."),
        ("terms-inspect", cmd_context_terms_inspect, "Inspect bounded project terminology metadata."),
    ):
        flat = context_sub.add_parser(alias, help=help_text)
        _add_terms_parser(flat, handler)
