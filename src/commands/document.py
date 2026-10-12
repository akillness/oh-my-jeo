from __future__ import annotations

import argparse
from pathlib import Path
import shlex
from typing import Any

from ..document_chunk_plan import (
    CLAIM_BOUNDARY,
    CHUNK_STATES,
    HERMES_READ_LINE_LIMIT,
    DocumentPlanError,
    DocumentPlanMissing,
    build_document_plan,
    document_plan_lock,
    fingerprint_source,
    mark_document_plan_chunk,
    next_chunk,
    normalize_plan_request,
    read_document_plan,
    result_view,
    validate_document_plan,
    write_document_plan,
)
from ..installer import OmjError
from .common import _paths, _print_json, _wants_json


DEFAULT_DOCUMENT_LIST_LIMIT = 20
DEFAULT_DOCUMENT_RANGE_LIMIT = 10
_REQUIRED_PLAN_FIELDS = frozenset(
    {
        "schema_version",
        "plan_id",
        "created_at",
        "updated_at",
        "source",
        "inputs",
        "provenance",
        "assumptions",
        "unit",
        "range_count",
        "ranges",
        "ledger",
        "claim_boundary",
        "delegation_hint",
    }
)


def _source_path(value: str) -> Path | None:
    candidate = Path(str(value)).expanduser()
    try:
        if candidate.is_file():
            return candidate.resolve()
    except OSError:
        return None
    return None


def _source_fingerprint(value: str) -> dict[str, Any]:
    return fingerprint_source(str(value), _source_path(str(value)))


def _source_status(plan: dict[str, Any], provided: str = "") -> dict[str, Any]:
    stored = plan.get("source") if isinstance(plan.get("source"), dict) else {}
    stored_path = str(stored.get("path") or "")
    candidate = str(provided or stored_path).strip()
    if not candidate or stored.get("kind") != "file":
        return {
            "status": "unbound",
            "checked": False,
            "reason": "source identity is label-only; no local file digest is available",
        }
    current = _source_fingerprint(candidate)
    if current.get("kind") != "file":
        return {"status": "missing", "checked": True, "path": candidate}
    identity_basis = str(stored.get("identity_basis") or "label")
    if identity_basis == "sha256":
        unchanged = bool(stored.get("sha256")) and current.get("sha256") == stored.get(
            "sha256"
        )
    elif identity_basis == "size_and_mtime":
        stored_canonical = Path(stored_path).expanduser().resolve(strict=False)
        current_canonical = Path(candidate).expanduser().resolve(strict=False)
        path_matches = stored_canonical == current_canonical
        unchanged = path_matches and (
            current.get("size_bytes") == stored.get("size_bytes")
            and current.get("mtime_ns") == stored.get("mtime_ns")
        )
    else:
        unchanged = current.get("label") == stored.get("label")
    return {
        "status": "unchanged" if unchanged else "changed",
        "checked": True,
        "path": candidate,
        "identity_basis": identity_basis,
        "stored_sha256": str(stored.get("sha256") or ""),
        "current_sha256": str(current.get("sha256") or ""),
        "stored_size_bytes": stored.get("size_bytes"),
        "current_size_bytes": current.get("size_bytes"),
    }


def _require_source_unchanged(
    plan: dict[str, Any], provided: str = ""
) -> dict[str, Any]:
    status = _source_status(plan, provided)
    if status["status"] in {"changed", "missing"}:
        raise DocumentPlanError(
            f"source identity {status['status']}; refusing to write progress for plan {plan['plan_id']}"
        )
    return status


def _assert_reused_source_identity(plan: dict[str, Any], provided: str) -> None:
    stored = plan.get("source") if isinstance(plan.get("source"), dict) else {}
    if stored.get("kind") != "file" or stored.get("identity_basis") == "sha256":
        return
    stored_raw = str(stored.get("path") or "").strip()
    if not stored_raw:
        raise DocumentPlanError("unhashed document plan has no canonical source path")
    stored_path = Path(stored_raw).expanduser().resolve(strict=False)
    provided_path = Path(str(provided)).expanduser().resolve(strict=False)
    if stored_path != provided_path:
        raise DocumentPlanError(
            "unhashed document plan source path differs; refusing to reuse the existing plan"
        )


def _outline(value: str) -> dict[str, Any]:
    title, separator, page = str(value).rpartition(":")
    if not separator or not title.strip() or not page.strip().isdigit():
        raise argparse.ArgumentTypeError("--outline must use TITLE:PAGE")
    return {"title": title.strip(), "page": int(page.strip())}


def _plan_id(args: argparse.Namespace) -> str:
    positional = str(getattr(args, "plan_id", "") or "").strip()
    option = str(getattr(args, "plan_id_option", "") or "").strip()
    if positional and option and positional != option:
        raise OmjError("positional plan_id disagrees with --plan-id")
    value = option or positional
    if not value:
        raise OmjError("plan_id is required")
    return value


def _chunk(args: argparse.Namespace) -> object:
    positional = getattr(args, "chunk", None)
    option = getattr(args, "range_option", None)
    if positional is not None and option is not None:
        try:
            if int(positional) != int(option):
                raise OmjError("positional range disagrees with --range")
        except (TypeError, ValueError) as exc:
            raise OmjError("range must be a whole number") from exc
    return option if option is not None else positional


def _state(args: argparse.Namespace) -> object:
    positional = getattr(args, "state", None)
    option = getattr(args, "state_option", None)
    if (
        positional
        and option
        and str(positional).strip().lower() != str(option).strip().lower()
    ):
        raise OmjError("positional state disagrees with --state")
    return option if option is not None else positional


def _assert_plan_payload(plan: dict[str, Any]) -> None:
    missing = sorted(field for field in _REQUIRED_PLAN_FIELDS if field not in plan)
    if missing:
        raise DocumentPlanError(
            "document plan is missing required fields: " + ", ".join(missing)
        )
    ranges = plan.get("ranges")
    if not isinstance(ranges, list):
        raise DocumentPlanError("document plan ranges are malformed")
    inputs = plan.get("inputs") if isinstance(plan.get("inputs"), dict) else {}
    assumptions = (
        plan.get("assumptions") if isinstance(plan.get("assumptions"), dict) else {}
    )
    total_lines = inputs.get("lines")
    if total_lines is None:
        total_info = assumptions.get("total_lines")
        total_lines = total_info.get("value") if isinstance(total_info, dict) else None
    for index, entry in enumerate(ranges, start=1):
        window = entry.get("read_window") if isinstance(entry, dict) else None
        offset = window.get("offset") if isinstance(window, dict) else None
        limit = window.get("limit") if isinstance(window, dict) else None
        end_line = window.get("end_line") if isinstance(window, dict) else None
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (offset, limit, end_line)
        ):
            raise DocumentPlanError(
                f"document plan range {index} has invalid read window bounds"
            )
        span = end_line - offset + 1
        if offset < 1 or limit != min(HERMES_READ_LINE_LIMIT, span):
            raise DocumentPlanError(
                f"document plan range {index} has inconsistent read window bounds"
            )
        if (
            isinstance(total_lines, int)
            and not isinstance(total_lines, bool)
            and end_line > total_lines
        ):
            raise DocumentPlanError(
                f"document plan range {index} ends beyond total lines"
            )


def _store(paths, plan_id: str) -> dict[str, str]:
    root = Path(paths.omj_home) / "documents"
    return {
        "omj_home": str(paths.omj_home),
        "documents_root": str(root),
        "plan_path": str(root / plan_id / "plan.json"),
        "authority": "document_chunk_plan_store",
    }


def _boundary() -> dict[str, Any]:
    return {
        "prepared_is_not_observed": True,
        "source_digest_is_identity_only": True,
        "covered_mark_is_caller_statement": True,
        "extraction_or_ocr_performed": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _emit(args: argparse.Namespace, payload: dict[str, Any], *, text: str = "") -> int:
    if _wants_json(args):
        _print_json(payload)
    elif text:
        print(text)
    else:
        print(payload)
    return 0


def _document_command(paths: Any, args: argparse.Namespace, *tokens: str) -> str:
    command = ["omj", "--omj-home", str(paths.omj_home)]
    if getattr(args, "hermes_home", None):
        command.extend(("--hermes-home", str(paths.hermes_home)))
    command.extend(("document", *tokens))
    return shlex.join(command)


def cmd_document_plan(args: argparse.Namespace) -> int:
    try:
        source = str(args.source).strip()
        request = normalize_plan_request(
            {
                "source": source,
                "pages": args.pages,
                "chars": args.chars,
                "lines": args.lines,
                "budget_chars": args.budget_chars,
                "chars_per_page": args.chars_per_page,
                "outline": [_outline(value) for value in (args.outline or [])],
            }
        )
        plan = build_document_plan(request, _source_fingerprint(source))
        paths = _paths(args)
        reused = False
        with document_plan_lock(paths.omj_home, plan["plan_id"], create=True):
            try:
                plan = read_document_plan(paths.omj_home, plan["plan_id"])
                reused = True
                _assert_plan_payload(plan)
                _assert_reused_source_identity(plan, source)
                destination = Path(_store(paths, plan["plan_id"])["plan_path"])
            except DocumentPlanMissing:
                destination = write_document_plan(paths.omj_home, plan)
        view = result_view(plan)
        hint = view.get("delegation_hint")
        if isinstance(hint, dict):
            hint["after_each_range"] = _document_command(
                paths,
                args,
                "mark",
                "--plan-id",
                plan["plan_id"],
                "--range",
                "<n>",
                "--state",
                "covered",
            )
    except (DocumentPlanError, OSError, ValueError, argparse.ArgumentTypeError) as exc:
        raise OmjError(str(exc)) from exc
    return _emit(
        args,
        {
            "schema_version": "omj_document_plan_result/v1",
            "plan": view,
            "path": str(destination),
            "store": _store(paths, plan["plan_id"]),
            "boundary": _boundary(),
        },
        text=f"document plan {plan['plan_id']} {'reused' if reused else 'written'} at {destination}",
    )


def _read_for_cli(paths, plan_id: str) -> dict[str, Any]:
    try:
        plan = read_document_plan(paths.omj_home, plan_id)
        _assert_plan_payload(plan)
        return plan
    except (DocumentPlanMissing, DocumentPlanError, OSError) as exc:
        raise OmjError(str(exc)) from exc


def _summary(plan: dict[str, Any], paths) -> dict[str, Any]:
    _assert_plan_payload(plan)
    source = plan.get("source") if isinstance(plan.get("source"), dict) else {}
    return {
        "plan_id": plan["plan_id"],
        "schema_version": plan["schema_version"],
        "created_at": plan["created_at"],
        "updated_at": plan["updated_at"],
        "source": source,
        "source_digest": str(source.get("sha256") or ""),
        "range_count": plan["range_count"],
        "ledger_summary": result_view(plan, limit=1)["ledger_summary"],
        "path": str(Path(paths.omj_home) / "documents" / plan["plan_id"] / "plan.json"),
    }


def cmd_document_list(args: argparse.Namespace) -> int:
    paths = _paths(args)
    root = Path(paths.omj_home) / "documents"
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    if root.exists():
        try:
            children = sorted(
                (item for item in root.iterdir() if item.is_dir()),
                key=lambda item: item.name,
            )
        except OSError as exc:
            raise OmjError(
                f"document store is unreadable: {exc.__class__.__name__}"
            ) from exc
        for child in children:
            try:
                records.append(
                    _summary(read_document_plan(paths.omj_home, child.name), paths)
                )
            except (
                DocumentPlanMissing,
                DocumentPlanError,
                OmjError,
                OSError,
                KeyError,
            ) as exc:
                errors.append(f"{child.name}: {exc}")
    limit = (
        None
        if args.all
        else (args.limit if args.limit is not None else DEFAULT_DOCUMENT_LIST_LIMIT)
    )
    if limit is not None and limit < 1:
        raise OmjError("--limit must be at least 1")
    selected = records if limit is None else records[-limit:]
    payload = {
        "schema_version": "omj_document_plan_list/v1",
        "count": len(selected),
        "total_count": len(records),
        "limit": limit if limit is not None else "all",
        "truncated": limit is not None and len(records) > len(selected),
        "plans": selected,
        "errors": errors,
        "store": {
            "omj_home": str(paths.omj_home),
            "documents_root": str(root),
            "authority": "document_chunk_plan_store",
        },
        "boundary": _boundary(),
    }
    return _emit(
        args,
        payload,
        text="\n".join(
            f"{item['plan_id']} {item['source'].get('label', '')}" for item in selected
        ),
    )


def cmd_document_show(args: argparse.Namespace) -> int:
    paths = _paths(args)
    plan = _read_for_cli(paths, _plan_id(args))
    start = args.range_from if args.range_from is not None else 1
    limit = args.limit if args.limit is not None else DEFAULT_DOCUMENT_RANGE_LIMIT
    if start < 1 or limit < 1:
        raise OmjError("--from and --limit must be at least 1")
    view = result_view(plan, start=start, limit=limit)
    view["source_status"] = _source_status(plan, args.source or "")
    payload = {
        "schema_version": "omj_document_plan_show/v1",
        "plan": view,
        "store": _store(paths, plan["plan_id"]),
        "boundary": _boundary(),
    }
    return _emit(
        args,
        payload,
        text=f"document plan {plan['plan_id']} ({plan['range_count']} ranges)",
    )


def cmd_document_resume(args: argparse.Namespace) -> int:
    paths = _paths(args)
    plan = _read_for_cli(paths, _plan_id(args))
    pending = next_chunk(plan["ledger"])
    view = result_view(plan, start=pending or 1, limit=1)
    view["source_status"] = _source_status(plan, args.source or "")
    view["resume_command"] = (
        _document_command(
            paths,
            args,
            "mark",
            "--plan-id",
            plan["plan_id"],
            "--range",
            str(pending),
            "--state",
            "covered",
        )
        if pending
        else ""
    )
    payload = {
        "schema_version": "omj_document_plan_resume/v1",
        "plan": view,
        "store": _store(paths, plan["plan_id"]),
        "boundary": _boundary(),
    }
    return _emit(
        args, payload, text=f"next range: {pending if pending is not None else 'none'}"
    )


def cmd_document_mark(args: argparse.Namespace) -> int:
    paths = _paths(args)
    plan_id = _plan_id(args)
    try:
        with document_plan_lock(paths.omj_home, plan_id):
            before = read_document_plan(paths.omj_home, plan_id)
            _assert_plan_payload(before)
            source_status = _require_source_unchanged(before, args.source or "")
            chunk = _chunk(args)
            try:
                index = int(chunk)
            except (TypeError, ValueError) as exc:
                raise DocumentPlanError("range must be a whole number") from exc
            state = str(_state(args) or "").strip().lower()
            updated = mark_document_plan_chunk(
                paths.omj_home,
                plan_id,
                index,
                state,
                args.note or "",
                _lock_held=True,
            )
            view = result_view(updated)
            view["source_status"] = source_status
    except (DocumentPlanMissing, DocumentPlanError, OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    payload = {
        "schema_version": "omj_document_plan_mark_result/v1",
        "plan": view,
        "store": _store(paths, plan_id),
        "boundary": _boundary(),
    }
    return _emit(
        args, payload, text=f"document plan {plan_id} range {chunk} marked {state}"
    )


def cmd_document_validate(args: argparse.Namespace) -> int:
    paths = _paths(args)
    plan_ids = (
        [_plan_id(args)]
        if (getattr(args, "plan_id_option", "") or getattr(args, "plan_id", ""))
        else []
    )
    errors: list[str] = []
    summaries: list[dict[str, Any]] = []
    if not plan_ids and str(getattr(args, "source", "") or "").strip():
        raise OmjError("document validate --source requires --plan-id")
    if plan_ids:
        candidates = plan_ids
    else:
        root = Path(paths.omj_home) / "documents"
        try:
            candidates = (
                sorted(item.name for item in root.iterdir() if item.is_dir())
                if root.exists()
                else []
            )
        except OSError as exc:
            raise OmjError(
                f"document store is unreadable: {exc.__class__.__name__}"
            ) from exc
    for plan_id in candidates:
        try:
            plan = read_document_plan(paths.omj_home, plan_id)
            _assert_plan_payload(plan)
            validate_document_plan(plan, expected_plan_id=plan_id)
            source_status = _source_status(plan, args.source or "")
            if source_status["status"] in {"changed", "missing"}:
                errors.append(f"{plan_id}: source identity {source_status['status']}")
            summary = _summary(plan, paths)
            summary["source"] = {
                **summary["source"],
                "ok": source_status["status"] in {"unchanged", "unbound"},
            }
            summaries.append({**summary, "source_status": source_status})
        except (
            DocumentPlanMissing,
            DocumentPlanError,
            OSError,
            ValueError,
            KeyError,
        ) as exc:
            errors.append(f"{plan_id}: {exc}")
    payload = {
        "schema_version": "omj_document_plan_validate/v1",
        "ok": not errors,
        "plan_count": len(summaries),
        "plans": summaries,
        "errors": errors,
        "store": {
            "omj_home": str(paths.omj_home),
            "documents_root": str(Path(paths.omj_home) / "documents"),
            "authority": "document_chunk_plan_store",
        },
        "boundary": _boundary(),
    }
    return (
        _emit(
            args,
            payload,
            text=("document store ok" if not errors else "document store has errors"),
        )
        if not errors
        else (_emit(args, payload, text="document store has errors") or 1)
    )


def _add_document_commands(sub) -> None:
    document = sub.add_parser(
        "document",
        help="Create and resume persistent metadata-only document chunk plans.",
    )
    document_sub = document.add_subparsers(dest="document_command", required=True)

    plan = document_sub.add_parser(
        "plan", help="Create and persist a document chunk plan."
    )
    plan.add_argument(
        "--source",
        "--file",
        dest="source",
        required=True,
        help="Document path or metadata-only source label.",
    )
    plan.add_argument("--pages", "--page-count", dest="pages", type=int)
    plan.add_argument("--chars", type=int)
    plan.add_argument("--lines", type=int)
    plan.add_argument("--budget-chars", type=int)
    plan.add_argument("--chars-per-page", type=int)
    plan.add_argument(
        "--outline", action="append", help="Page anchor in TITLE:PAGE form."
    )
    plan.add_argument("--json", action="store_true")
    plan.set_defaults(func=cmd_document_plan)

    listing = document_sub.add_parser("list", help="List persisted document plans.")
    listing.add_argument("--limit", type=int, default=None)
    listing.add_argument("--all", action="store_true")
    listing.add_argument("--json", action="store_true")
    listing.set_defaults(func=cmd_document_list)

    show = document_sub.add_parser("show", help="Show one persisted document plan.")
    show.add_argument("plan_id", nargs="?")
    show.add_argument("--plan-id", dest="plan_id_option", default="")
    show.add_argument("--source", "--file", dest="source", default="")
    show.add_argument("--from", dest="range_from", type=int, default=None)
    show.add_argument("--limit", type=int, default=None)
    show.add_argument("--json", action="store_true")
    show.set_defaults(func=cmd_document_show)

    resume = document_sub.add_parser(
        "resume", help="Show the persisted next document range."
    )
    resume.add_argument("plan_id", nargs="?")
    resume.add_argument("--plan-id", dest="plan_id_option", default="")
    resume.add_argument("--source", "--file", dest="source", default="")
    resume.add_argument("--json", action="store_true")
    resume.set_defaults(func=cmd_document_resume)

    mark = document_sub.add_parser(
        "mark", help="Persist covered, next, or missing state for one range."
    )
    mark.add_argument("plan_id", nargs="?")
    mark.add_argument("chunk", nargs="?")
    mark.add_argument("state", nargs="?", choices=CHUNK_STATES)
    mark.add_argument("--plan-id", dest="plan_id_option", default="")
    mark.add_argument("--range", dest="range_option", type=int, default=None)
    mark.add_argument(
        "--state", dest="state_option", choices=CHUNK_STATES, default=None
    )
    mark.add_argument("--source", "--file", dest="source", default="")
    mark.add_argument("--note", default="")
    mark.add_argument("--json", action="store_true")
    mark.set_defaults(func=cmd_document_mark)

    validate = document_sub.add_parser(
        "validate", help="Validate persisted document plans and source identities."
    )
    validate.add_argument("plan_id", nargs="?")
    validate.add_argument("--plan-id", dest="plan_id_option", default="")
    validate.add_argument("--source", "--file", dest="source", default="")
    validate.add_argument("--json", action="store_true")
    validate.set_defaults(func=cmd_document_validate)
