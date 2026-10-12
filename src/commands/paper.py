from __future__ import annotations

import argparse

from ..installer import OmjError
from ..paper_learning import (
    PAPER_LEARNING_LEVELS,
    PAPER_LEARNING_SOURCE_STATES,
    PaperLearningStoreError,
    build_paper_learning_record,
    paper_learning_card_path,
    paper_learning_ledger_path,
    read_paper_progress_ledger,
    record_paper_progress,
    render_paper_learning_list_text,
    render_paper_learning_record_text,
    scan_paper_learning_store,
    show_paper_learning_record,
    summarize_paper_learning_record,
    validate_paper_learning_store,
    write_paper_learning_record,
)
from .common import _paths, _print_json, _wants_json

DEFAULT_PAPER_LIST_LIMIT = 20
PAPER_LEARNING_BOUNDARY = {
    "prepared_is_not_observed": True,
    "source_hash_is_not_extraction_evidence": True,
    "page_count_observed": False,
    "recorded_chunk_is_not_correctness_evidence": True,
    "normal_user_surface": "Hermes chat or installed skills; CLI is backend/verifier infrastructure.",
}


def _store_error_message(exc: PaperLearningStoreError) -> str:
    if exc.reason_code == "record_not_found":
        return f"paper learning record not found (record_not_found): {exc.detail}"
    if exc.reason_code == "source_unreadable":
        return f"paper source is unreadable (source_unreadable): {exc.detail}; nothing was recorded"
    return f"paper learning record is corrupt (record_corrupt): {exc.detail}; run `omj paper validate`"


def _level_argument(value: str) -> str:
    normalized = str(value).strip().lower().replace(" ", "_")
    aliases = {
        "very_easy": "very_easy",
        "easy": "very_easy",
        "moderate": "moderate",
        "medium": "moderate",
        "expert": "expert",
        "advanced": "expert",
        "choose": "choose",
    }
    if normalized not in aliases:
        raise argparse.ArgumentTypeError(
            f"unknown level {value!r}; use one of {', '.join(PAPER_LEARNING_LEVELS)}"
        )
    return aliases[normalized]


def _store_block(paths, paper_id: str) -> dict[str, str]:
    return {
        "omj_home": str(paths.omj_home),
        "paper_learning_dir": str(
            getattr(paths, "paper_learning_dir", paths.omj_home / "paper-learning")
        ),
        "card_path": str(paper_learning_card_path(paths, paper_id)),
        "ledger_path": str(paper_learning_ledger_path(paths, paper_id)),
        "index_path": str(
            getattr(
                paths,
                "paper_learning_index_path",
                paths.omj_home / "paper-learning" / "index.json",
            )
        ),
        "index_authority": "cache_only",
    }


def _limit_from_args(args: argparse.Namespace) -> int | None:
    if args.all:
        return None
    if args.limit is None:
        return DEFAULT_PAPER_LIST_LIMIT
    if args.limit < 1:
        raise ValueError("--limit must be at least 1")
    return args.limit


def _emit_record(
    args, paths, record: dict, *, schema_version: str, entry: dict | None = None
) -> int:
    if _wants_json(args):
        payload = {
            "schema_version": schema_version,
            "record": record,
            "store": _store_block(paths, record["paper_id"]),
            "boundary": PAPER_LEARNING_BOUNDARY,
        }
        if entry is not None:
            payload["entry"] = entry
        _print_json(payload)
        return 0
    print(
        render_paper_learning_record_text(record, [entry] if entry is not None else [])
    )
    print(f"Card: {paper_learning_card_path(paths, record['paper_id'])}")
    return 0


def cmd_paper_plan(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        record = build_paper_learning_record(
            title=args.title,
            source_ref=args.source or "",
            authors=args.author or [],
            level=args.level,
            source_state=args.source_state,
            sections=args.section,
            observed_sections=args.observed_section or [],
            missing_sections=args.missing_section or [],
            evidence_ref=args.evidence_ref or "",
            output_language=args.output_language or "source",
        )
        written = write_paper_learning_record(paths, record)
    except PaperLearningStoreError as exc:
        raise OmjError(_store_error_message(exc)) from exc
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    return _emit_record(
        args, paths, written, schema_version="omj_paper_learning_plan_result/v1"
    )


def cmd_paper_list(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        limit = _limit_from_args(args)
        all_records, unreadable = scan_paper_learning_store(paths)
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    records = all_records if limit is None else all_records[-limit:]
    summaries = [summarize_paper_learning_record(record) for record in records]
    if _wants_json(args):
        _print_json(
            {
                "schema_version": "omj_paper_learning_list/v1",
                "count": len(records),
                "total_count": len(all_records),
                "limit": limit if limit is not None else "all",
                "truncated": limit is not None and len(all_records) > len(records),
                "summary_only": True,
                "index_authority": "cache_only",
                "papers": summaries,
                "unreadable_count": len(unreadable),
                "unreadable_records": unreadable,
                "next_action": "run `omj paper validate` to see every store fault"
                if unreadable
                else "",
            }
        )
    else:
        print(
            render_paper_learning_list_text(
                summaries, unreadable, total_count=len(all_records)
            )
        )
    return 0


def cmd_paper_show(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        record = show_paper_learning_record(paths, args.paper_id)
        entries, ledger_errors = read_paper_progress_ledger(paths, args.paper_id)
    except PaperLearningStoreError as exc:
        raise OmjError(_store_error_message(exc)) from exc
    if _wants_json(args):
        _print_json(
            {
                "schema_version": "omj_paper_learning_show/v1",
                "record": record,
                "ledger": entries,
                "ledger_errors": ledger_errors,
                "store": _store_block(paths, record["paper_id"]),
                "boundary": PAPER_LEARNING_BOUNDARY,
            }
        )
    else:
        print(render_paper_learning_record_text(record, entries))
        if ledger_errors:
            print("\nLedger lines that could not be read:")
            print("\n".join(f"  - {error}" for error in ledger_errors))
    return 0


def cmd_paper_progress(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        updated, entry = record_paper_progress(
            paths,
            args.paper_id,
            covered=args.covered or [],
            next_section=args.next,
            missing=args.missing or [],
            observed=args.observed_section or [],
            note=args.note or "",
            source_state=args.source_state,
            evidence_ref=args.evidence_ref,
        )
    except PaperLearningStoreError as exc:
        raise OmjError(_store_error_message(exc)) from exc
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    return _emit_record(
        args,
        paths,
        updated,
        schema_version="omj_paper_learning_progress_result/v1",
        entry=entry,
    )


def cmd_paper_validate(args: argparse.Namespace) -> int:
    result = validate_paper_learning_store(_paths(args))
    if _wants_json(args):
        _print_json(result)
    elif result["ok"]:
        print(f"paper-learning store ok: {result['paper_count']} record(s), 0 errors")
    else:
        print(
            f"paper-learning store has {len(result['errors'])} error(s) across {result['paper_count']} readable record(s):"
        )
        for error in result["errors"]:
            print(f"  - {error}")
    return 0 if result["ok"] else 1


def _add_paper_commands(sub) -> None:
    paper = sub.add_parser(
        "paper", help="Record and resume paper-learning reading progress."
    )
    paper_sub = paper.add_subparsers(dest="paper_command", required=True)
    plan = paper_sub.add_parser("plan", help="Create a paper learning record.")
    plan.add_argument("--title", required=True)
    plan.add_argument("--source", default="")
    plan.add_argument("--author", action="append")
    plan.add_argument("--level", type=_level_argument, default="choose")
    plan.add_argument(
        "--source-state", choices=PAPER_LEARNING_SOURCE_STATES, default="metadata_only"
    )
    plan.add_argument("--section", action="append")
    plan.add_argument("--observed-section", action="append")
    plan.add_argument("--missing-section", action="append")
    plan.add_argument("--evidence-ref", default="")
    plan.add_argument("--output-language", default="source")
    plan.add_argument("--json", action="store_true")
    plan.set_defaults(func=cmd_paper_plan)
    listing = paper_sub.add_parser("list", help="List paper records.")
    listing.add_argument("--limit", type=int, default=None)
    listing.add_argument("--all", action="store_true")
    listing.add_argument("--json", action="store_true")
    listing.set_defaults(func=cmd_paper_list)
    show = paper_sub.add_parser("show", help="Show one paper record.")
    show.add_argument("paper_id")
    show.add_argument("--json", action="store_true")
    show.set_defaults(func=cmd_paper_show)
    progress = paper_sub.add_parser("progress", help="Record explained paper progress.")
    progress.add_argument("paper_id")
    progress.add_argument("--covered", action="append")
    progress.add_argument("--next", default=None)
    progress.add_argument("--missing", action="append")
    progress.add_argument("--observed-section", action="append")
    progress.add_argument("--note", default="")
    progress.add_argument(
        "--source-state", choices=PAPER_LEARNING_SOURCE_STATES, default=None
    )
    progress.add_argument("--evidence-ref", default=None)
    progress.add_argument("--json", action="store_true")
    progress.set_defaults(func=cmd_paper_progress)
    validate = paper_sub.add_parser("validate", help="Validate the paper store.")
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(func=cmd_paper_validate)
