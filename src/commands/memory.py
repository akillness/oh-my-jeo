from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

from ..installer import OmjError
from ..local_store import atomic_write_json
from ..memory import (
    apply_memory_update_batch,
    approve_project_memory_candidate,
    build_handoff_context_pack,
    build_memory_inspection,
    build_project_memory_recall_pack,
    build_project_memory_review,
    build_project_memory_status,
    capture_project_memory_candidate,
    capture_project_memory_failed_attempt,
    read_memory_snapshot_file,
    reject_project_memory_candidate,
)
from ..paths import OmjPaths
from ..workflows.domain_intelligence import (
    approve_domain_candidate,
    build_domain_review,
    capture_domain_candidate,
    list_domain_profiles,
    reject_domain_candidate,
    retire_domain_profile,
)
from ..workflows.memory_lifecycle import (
    LifecyclePlan,
    apply_memory_confirmation,
    apply_memory_correction,
    apply_memory_keep_open,
    apply_memory_prune,
    apply_memory_reapproval,
    apply_memory_restore,
    apply_memory_retirement,
    build_memory_confirmation,
    build_memory_correction,
    build_memory_keep_open,
    build_memory_prune,
    build_memory_reapproval,
    build_memory_restore,
    build_memory_retirement,
    compare_retrieval_reports,
    lifecycle_replay_status,
    make_lifecycle_receipt,
    run_memory_retrieval_evaluation,
)
from ..workflows.memory_provenance import build_memory_source_index
from .common import _paths, _print_json


def cmd_memory_status(args: argparse.Namespace) -> int:
    try:
        payload = build_project_memory_status(_paths(args))
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def cmd_memory_capture(args: argparse.Namespace) -> int:
    try:
        summary = " ".join(args.summary).strip()
        content = sys.stdin.read() if args.stdin else str(args.content or "")
        if not summary:
            raise ValueError("memory capture requires a summary")
        payload = capture_project_memory_candidate(
            _paths(args),
            summary,
            content=content,
            record_type=args.type,
            scope_kind=args.scope_kind,
            scope_ref=args.scope_ref,
            source=args.source,
            source_ref=args.source_ref,
            tags=args.tag or [],
            ttl_days=args.ttl_days,
            stale_after_days=args.stale_after_days,
        )
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0

def cmd_memory_record_failure(args: argparse.Namespace) -> int:
    try:
        approach = " ".join(args.approach).strip()
        if not approach:
            raise ValueError("memory record-failure requires an approach description")
        payload = capture_project_memory_failed_attempt(
            _paths(args),
            approach,
            cause=str(args.cause or ""),
            scope_kind=args.scope_kind,
            scope_ref=args.scope_ref,
            source=args.source,
            source_ref=args.source_ref,
            tags=args.tag or [],
            stale_after_days=args.stale_after_days,
        )
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0



def cmd_memory_review(args: argparse.Namespace) -> int:
    try:
        payload = build_project_memory_review(
            _paths(args),
            candidate_id=args.candidate,
            limit=_optional_positive_int(args.limit, "--limit") or 20,
        )
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def cmd_memory_approve(args: argparse.Namespace) -> int:
    try:
        payload = approve_project_memory_candidate(_paths(args), args.candidate_id, approved_by=args.approved_by)
    except FileNotFoundError as exc:
        raise OmjError(f"memory candidate not found: {args.candidate_id}") from exc
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def cmd_memory_reject(args: argparse.Namespace) -> int:
    try:
        payload = reject_project_memory_candidate(
            _paths(args),
            args.candidate_id,
            rejected_by=args.rejected_by,
            reason=args.reason,
        )
    except FileNotFoundError as exc:
        raise OmjError(f"memory candidate not found: {args.candidate_id}") from exc
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def cmd_memory_recall(args: argparse.Namespace) -> int:
    try:
        query = " ".join(args.query).strip()
        payload = build_project_memory_recall_pack(
            _paths(args),
            query,
            executor_target=args.executor,
            session_id=args.session_id,
            scope_kind=args.scope_kind,
            scope_ref=args.scope_ref,
            limit=_optional_positive_int(args.limit, "--limit") or 6,
            include_stale=args.include_stale,
        )
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def cmd_memory_inspect(args: argparse.Namespace) -> int:
    try:
        inspection = build_memory_inspection(
            _paths(args),
            wrapper_snapshot=_read_optional_json(args.fixture),
            scope_kind=args.scope_kind,
            scope_ref=args.scope_ref,
            session_limit=_optional_positive_int(args.session_limit, "--session-limit"),
            summary=args.summary,
            review_item_limit=_optional_positive_int(args.review_item_limit, "--review-item-limit"),
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(inspection)
    return 0


def cmd_memory_pack(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        inspection = None
        wrapper_snapshot = _read_optional_json(args.fixture)
        if wrapper_snapshot is not None:
            inspection = build_memory_inspection(
                paths,
                wrapper_snapshot=wrapper_snapshot,
                scope_kind=args.scope_kind,
                scope_ref=args.scope_ref,
                session_limit=_optional_positive_int(args.session_limit, "--session-limit"),
                review_item_limit=_optional_positive_int(args.review_item_limit, "--review-item-limit"),
            )
        pack = build_handoff_context_pack(
            paths,
            inspection=inspection,
            executor_target=args.executor,
            session_id=args.session_id,
            scope_kind=args.scope_kind,
            scope_ref=args.scope_ref,
            session_limit=_optional_positive_int(args.session_limit, "--session-limit"),
            context_limit=_optional_positive_int(args.context_limit, "--context-limit") or 12,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(pack)
    return 0


def cmd_memory_apply(args: argparse.Namespace) -> int:
    try:
        batch = _read_required_json(args.batch)
        result = apply_memory_update_batch(_paths(args), batch, dry_run=args.dry_run)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(result)
    return 0

def cmd_memory_sources(args: argparse.Namespace) -> int:
    try:
        payload = build_memory_source_index(_paths(args), source=args.source, limit=_optional_nonnegative_int(args.limit, "--limit"))
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0

def _memory_record_metadata(
    paths,
    record_id: str,
    revision: int | None = None,
    *,
    record: dict[str, object] | None = None,
) -> dict[str, object]:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,159}", str(record_id or "")):
        raise ValueError("unsafe_record_id")
    path = paths.memory_dir / "records" / f"{record_id}.json"
    if path.is_symlink():
        raise FileNotFoundError(record_id)
    if record is None:
        try:
            record = _read_required_json(str(path))
        except FileNotFoundError:
            raise FileNotFoundError(record_id) from None
    if not isinstance(record, dict) or record.get("record_id") != record_id:
        raise ValueError("record_identity_mismatch")
    current_revision = record.get("revision", 1)
    if not isinstance(current_revision, int) or isinstance(current_revision, bool) or current_revision < 1:
        raise ValueError("invalid_revision")
    if revision is not None and revision != current_revision:
        raise ValueError("stale_revision")
    return {
        "record_id": record_id,
        "revision": current_revision,
        "scope": record.get("scope", {}),
        "source": str(record.get("source", "") or ""),
        "source_ref": str(record.get("source_ref", "") or ""),
        "source_class": str(record.get("source_class", "") or ""),
        "derived_from": record.get("derived_from", []),
        "admission": record.get("admission", {}),
        "retention": record.get("retention", {}),
        "staleness": record.get("staleness", {}),
        "record_path": str(path),
    }


def cmd_memory_lineage(args: argparse.Namespace) -> int:
    try:
        metadata = _memory_record_metadata(_paths(args), args.record_id, args.revision)
        metadata["lineage"] = {
            "source": metadata.get("source", ""),
            "source_ref": metadata.get("source_ref", ""),
            "source_class": metadata.get("source_class", ""),
            "derived_from": metadata.get("derived_from", []),
        }
        metadata["claim_boundary"] = "Read-only OMJ-local record lineage metadata; no provenance is inferred beyond recorded fields."
    except (OSError, json.JSONDecodeError, ValueError, FileNotFoundError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(metadata)
    return 0
def cmd_memory_recall_incident(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        record_path = paths.memory_dir / "records" / f"{args.record_id}.json"
        record = _read_required_json(str(record_path))
        metadata = _memory_record_metadata(paths, args.record_id, args.revision, record=record)
        replay = lifecycle_replay_status(record, now=datetime.now(timezone.utc))
        payload = {
            "schema_version": "memory_recall_incident/v1",
            "record": metadata,
            "stages": {
                "stored": True,
                "eligible": bool(replay.get("replay_eligible", False)),
                "selected": bool(replay.get("replay_eligible", False)),
            },
            "replay": replay,
            "claim_boundary": "Prepared local recall evidence only; it does not prove executor, provider, Hermes-native, or delivery observation.",
        }
    except (OSError, json.JSONDecodeError, ValueError, FileNotFoundError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def _read_retrieval_fixture(path: str | None) -> list[dict[str, object]]:
    if not path:
        return []
    data = _read_required_json(path)
    cases = data.get("cases", data)
    if not isinstance(cases, list) or any(not isinstance(item, dict) for item in cases):
        raise ValueError("retrieval fixture cases must be a list of objects")
    return [dict(item) for item in cases]


def cmd_memory_recall_suite(args: argparse.Namespace) -> int:
    try:
        report = run_memory_retrieval_evaluation(target_revision=str(args.target_revision or ""), cases=_read_retrieval_fixture(args.fixture))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(report)
    return 0


def _mapping_values(values: list[str] | None) -> list[tuple[str, str]]:
    mappings: list[tuple[str, str]] = []
    for value in values or []:
        key, separator, mapped = str(value).partition("=")
        if not separator or not key.strip() or not mapped.strip():
            raise ValueError("--mapping values must use key=value")
        mappings.append((key.strip(), mapped.strip()))
    return mappings


def cmd_memory_domain_capture(args: argparse.Namespace) -> int:
    try:
        payload = capture_domain_candidate(
            _paths(args), scope_kind=args.scope_kind, scope_ref=args.scope_ref,
            domain_id=args.domain_id, mappings=_mapping_values(args.mapping),
            workflow_hints=args.workflow_hint or [], source_class=args.source_class,
            source_ref=args.source_ref, observation_count=args.observation_count,
            confidence=args.confidence,
        )
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def cmd_memory_domain_review(args: argparse.Namespace) -> int:
    try:
        payload = build_domain_review(_paths(args))
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def cmd_memory_domain_approve(args: argparse.Namespace) -> int:
    try:
        payload = approve_domain_candidate(_paths(args), args.candidate_id, approved_by=args.approved_by)
    except (OSError, ValueError, FileNotFoundError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def cmd_memory_domain_reject(args: argparse.Namespace) -> int:
    try:
        payload = reject_domain_candidate(_paths(args), args.candidate_id, rejected_by=args.rejected_by, reason_code=args.reason_code)
    except (OSError, ValueError, FileNotFoundError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def cmd_memory_domain_inspect(args: argparse.Namespace) -> int:
    try:
        payload = list_domain_profiles(_paths(args), scope_kind=args.scope_kind, scope_ref=args.scope_ref, domain_id=args.domain_id)
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def cmd_memory_domain_retire(args: argparse.Namespace) -> int:
    try:
        payload = retire_domain_profile(
            _paths(args), profile_id=args.profile_id or args.profile_identifier, scope_kind=args.scope_kind, scope_ref=args.scope_ref,
            revision=args.revision, retired_by=args.retired_by, reason_code=args.reason_code,
        )
    except (OSError, ValueError, FileNotFoundError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def _lifecycle_executor(paths: OmjPaths, plan: LifecyclePlan) -> dict[str, object]:
    outcomes: list[dict[str, object]] = []
    for mutation in plan.mutations:
        target = paths.memory_dir / mutation.target
        source = paths.memory_dir / mutation.source if mutation.source else None
        if mutation.action == "write":
            payload = mutation.payload
            if not isinstance(payload, dict):
                raise ValueError("invalid_lifecycle_payload")
            atomic_write_json(target, dict(payload))
            outcome = "written"
        elif mutation.action == "move":
            if source is None or not source.exists() or source.is_symlink():
                raise ValueError("operation_guard_mismatch")
            target.parent.mkdir(parents=True, exist_ok=True)
            source.replace(target)
            outcome = "moved"
        elif mutation.action == "delete":
            if target.exists() and not target.is_symlink():
                target.unlink()
                outcome = "removed"
            else:
                outcome = "already_absent"
        else:
            raise ValueError("unsupported_lifecycle_mutation")
        outcomes.append({"target_id": mutation.target_id, "artifact_kind": mutation.artifact_kind, "outcome": outcome, "reason_code": "applied"})
    return {"receipt": make_lifecycle_receipt(plan, outcomes)}


def _build_lifecycle_plan(paths: OmjPaths, args: argparse.Namespace) -> LifecyclePlan:
    now = datetime.now(timezone.utc)
    operation = args.operation.replace("-", "_")
    record_id = str(args.record_id or args.identity or "")
    candidate_id = args.candidate_id or (args.identity if operation == "reapprove" else None)
    if operation == "retire":
        return build_memory_retirement(paths, record_id, args.revision, now=now)
    if operation == "restore":
        return build_memory_restore(paths, record_id, args.revision, now=now, candidate_id=candidate_id)
    if operation == "reapprove":
        return build_memory_reapproval(paths, candidate_id or "", reviewer_claim=args.reviewer_claim, now=now)
    if operation == "correct":
        return build_memory_correction(paths, record_id, args.revision, args.summary, now=now, candidate_id=candidate_id)
    if operation == "confirm":
        return build_memory_confirmation(paths, record_id, args.revision, now=now, candidate_id=candidate_id)
    if operation == "keep_open":
        return build_memory_keep_open(paths, record_id, args.revision, now=now)
    if operation == "prune":
        return build_memory_prune(paths, record_id, args.revision, now=now)
    raise ValueError(f"unsupported lifecycle operation: {args.operation}")


def cmd_memory_lifecycle(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        plan = _build_lifecycle_plan(paths, args)
        payload = {"schema_version": "memory_lifecycle_preview/v1", "plan": plan.report, "operation_id": plan.operation_id, "claim_boundary": plan.report.get("claim_boundary", "")}
        if args.apply:
            operation = plan.operation_type
            if operation == "retire":
                result = apply_memory_retirement(paths, plan, transaction_executor=_lifecycle_executor)
            elif operation == "restore":
                result = apply_memory_restore(paths, plan, transaction_executor=_lifecycle_executor)
            elif operation == "reapprove":
                result = apply_memory_reapproval(paths, plan, transaction_executor=_lifecycle_executor)
            elif operation == "correct":
                result = apply_memory_correction(paths, plan, transaction_executor=_lifecycle_executor)
            elif operation == "confirm":
                result = apply_memory_confirmation(paths, plan, transaction_executor=_lifecycle_executor)
            elif operation == "keep_open":
                result = apply_memory_keep_open(paths, plan, transaction_executor=_lifecycle_executor)
            else:
                result = apply_memory_prune(paths, plan, transaction_executor=_lifecycle_executor, confirm_hard_delete_local=args.confirm_hard_delete_local)
            payload = {**payload, "apply": result}
    except (OSError, ValueError, FileNotFoundError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def cmd_memory_evaluate(args: argparse.Namespace) -> int:
    return cmd_memory_recall_suite(args)


def cmd_memory_compare(args: argparse.Namespace) -> int:
    try:
        payload = compare_retrieval_reports(_read_required_json(args.left), _read_required_json(args.right))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0


def _read_optional_json(path: str | None) -> dict[str, object] | None:
    if not path:
        return None
    return read_memory_snapshot_file(path)


_MAX_MEMORY_JSON_BYTES = 1_000_000

def _read_required_json(path: str) -> dict[str, object]:
    if path == "-":
        stream = getattr(sys.stdin, "buffer", sys.stdin)
        raw_value = stream.read(_MAX_MEMORY_JSON_BYTES + 1)
        if isinstance(raw_value, bytes):
            try:
                raw = raw_value.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError("memory JSON input must be valid UTF-8 JSON") from exc
        else:
            raw = str(raw_value)
    else:
        source = Path(path).expanduser()
        flags = os.O_RDONLY | os.O_NONBLOCK
        try:
            fd = os.open(source, flags)
        except FileNotFoundError:
            raise
        except OSError as exc:
            raise ValueError("memory JSON input must be a regular file") from exc
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise ValueError("memory JSON input must be a regular file")
            if info.st_size > _MAX_MEMORY_JSON_BYTES:
                raise ValueError(f"memory JSON input exceeds {_MAX_MEMORY_JSON_BYTES} bytes")
            raw_value = os.read(fd, _MAX_MEMORY_JSON_BYTES + 1)
        finally:
            os.close(fd)
        try:
            raw = raw_value.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("memory JSON input must be valid UTF-8 JSON") from exc
    if len(raw.encode("utf-8")) > _MAX_MEMORY_JSON_BYTES:
        raise ValueError(f"memory JSON input exceeds {_MAX_MEMORY_JSON_BYTES} bytes")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("memory JSON input must be an object")
    return data


def _optional_positive_int(value: int | None, flag: str) -> int | None:
    if value is None:
        return None
    if value < 1:
        raise ValueError(f"{flag} must be at least 1")
    return value

def _optional_nonnegative_int(value: int | None, flag: str) -> int | None:
    if value is None:
        return None
    if value < 0:
        raise ValueError(f"{flag} must be at least 0")
    return value


def _add_memory_commands(sub) -> None:
    memory = sub.add_parser("memory", help="Capture, review, recall, inspect, or pack OMJ project memory/context artifacts.")
    memory_sub = memory.add_subparsers(dest="memory_command", required=True)

    status = memory_sub.add_parser("status", help="Show OMJ project-memory policy, store paths, and review counts.")
    status.set_defaults(func=cmd_memory_status)

    capture = memory_sub.add_parser("capture", help="Capture an OMJ project-memory candidate for review.")
    capture.add_argument("summary", nargs="*", help="Short reviewed-memory summary to capture.")
    capture.add_argument("--type", choices=("fact", "decision", "lesson", "procedure", "episode", "failed_attempt"), default="fact", help="Typed memory record category.")
    capture.add_argument("--content", default="", help="Optional raw source text. It is hashed/length-counted, not persisted raw.")
    capture.add_argument("--stdin", action="store_true", help="Read optional raw source text from stdin without persisting it raw.")
    capture.add_argument("--scope-kind", choices=("project", "target", "thread", "run"), default="project")
    capture.add_argument("--scope-ref", default="default")
    capture.add_argument("--source", default="cli")
    capture.add_argument("--source-ref", default="")
    capture.add_argument("--tag", action="append", default=[])
    capture.add_argument("--ttl-days", type=int, default=None)
    capture.add_argument("--stale-after-days", type=int, default=None)
    capture.set_defaults(func=cmd_memory_capture)

    record_failure = memory_sub.add_parser(
        "record-failure",
        help="Deterministically capture ONE dead end (approach + cause) as a failed_attempt so later recall surfaces it first.",
    )
    record_failure.add_argument("approach", nargs="*", help="The specific approach/action that stalled or failed.")
    record_failure.add_argument("--cause", default="", help="Why it failed (symptom, error class, or root cause).")
    record_failure.add_argument("--scope-kind", choices=("project", "target", "thread", "run"), default="project")
    record_failure.add_argument("--scope-ref", default="default")
    record_failure.add_argument("--source", default="runtime")
    record_failure.add_argument("--source-ref", default="")
    record_failure.add_argument("--tag", action="append", default=[])
    record_failure.add_argument("--stale-after-days", type=int, default=None)
    record_failure.set_defaults(func=cmd_memory_record_failure)

    review = memory_sub.add_parser("review", help="Return review cards for pending OMJ project-memory candidates.")
    review.add_argument("--candidate", default=None, help="Limit review output to one candidate id.")
    review.add_argument("--limit", type=int, default=20)
    review.set_defaults(func=cmd_memory_review)

    approve = memory_sub.add_parser("approve", help="Approve a reviewed project-memory candidate.")
    approve.add_argument("candidate_id")
    approve.add_argument("--approved-by", default="operator")
    approve.set_defaults(func=cmd_memory_approve)

    reject = memory_sub.add_parser("reject", help="Reject a project-memory candidate.")
    reject.add_argument("candidate_id")
    reject.add_argument("--rejected-by", default="operator")
    reject.add_argument("--reason", default="")
    reject.set_defaults(func=cmd_memory_reject)

    recall = memory_sub.add_parser("recall", help="Recall reviewed OMJ project memory for a task as prepared context.")
    recall.add_argument("query", nargs="*", help="Task/query text used for deterministic keyword recall.")
    recall.add_argument("--executor", default="generic", help="Executor target label to record in the recall pack.")
    recall.add_argument("--session-id", default="", help="Optional wrapper session id to bind to the recall pack.")
    recall.add_argument("--scope-kind", choices=("project", "target", "thread", "run"), default=None)
    recall.add_argument("--scope-ref", default=None)
    recall.add_argument("--limit", type=int, default=6)
    recall.add_argument("--include-stale", action="store_true")
    recall.set_defaults(func=cmd_memory_recall)

    inspect = memory_sub.add_parser("inspect")
    inspect.add_argument(
        "--fixture",
        default=None,
        help="Optional memory_snapshot/v1 JSON fixture supplied by a wrapper for deterministic inspection.",
    )
    inspect.add_argument("--scope-kind", choices=("project", "target", "thread", "run"), default=None, help="Only inspect snapshots from this scope kind.")
    inspect.add_argument("--scope-ref", default=None, help="Only inspect snapshots with this scope reference.")
    inspect.add_argument("--session-limit", type=int, default=None, help="Maximum recent wrapper session snapshots to inspect.")
    inspect.add_argument("--review-item-limit", type=int, default=None, help="Maximum review items to return.")
    inspect.add_argument("--summary", action="store_true", help="Return snapshot summaries instead of full snapshot items.")
    inspect.set_defaults(func=cmd_memory_inspect)

    pack = memory_sub.add_parser("pack")
    pack.add_argument(
        "--fixture",
        default=None,
        help="Optional memory_snapshot/v1 JSON fixture supplied by a wrapper before packing handoff context.",
    )
    pack.add_argument("--executor", default="generic", help="Executor target label to record in the context pack.")
    pack.add_argument("--session-id", default="", help="Optional wrapper session id to bind to the context pack.")
    pack.add_argument("--scope-kind", choices=("project", "target", "thread", "run"), default=None, help="Only pack context from this scope kind.")
    pack.add_argument("--scope-ref", default=None, help="Only pack context with this scope reference.")
    pack.add_argument("--session-limit", type=int, default=None, help="Maximum recent wrapper session snapshots to inspect.")
    pack.add_argument("--review-item-limit", type=int, default=None, help="Maximum review items to build when a fixture is supplied.")
    pack.add_argument("--context-limit", type=int, default=12, help="Maximum context items to include in the handoff pack.")
    pack.set_defaults(func=cmd_memory_pack)

    sources = memory_sub.add_parser("sources", help="Index reviewed records by recorded source and source_ref axes.")
    sources.add_argument("--source", default=None)
    sources.add_argument("--limit", type=int, default=None)
    sources.set_defaults(func=cmd_memory_sources)

    lineage = memory_sub.add_parser("lineage", help="Inspect one record's recorded source lineage metadata.")
    lineage.add_argument("record_id")
    lineage.add_argument("--revision", type=int, default=None)
    lineage.set_defaults(func=cmd_memory_lineage)

    recall_incident = memory_sub.add_parser("recall-incident", help="Report stored, eligible, and selected stages for one record.")
    recall_incident.add_argument("--record-id", required=True, dest="record_id")
    recall_incident.add_argument("--revision", type=int, default=None)
    recall_incident.set_defaults(func=cmd_memory_recall_incident)

    recall_suite = memory_sub.add_parser("recall-suite", help="Run deterministic offline retrieval regression cases.")
    recall_suite.add_argument("--fixture", default=None)
    recall_suite.add_argument("--target-revision", default="")
    recall_suite.set_defaults(func=cmd_memory_recall_suite)

    domain = memory_sub.add_parser("domain", help="Capture and review scoped domain-intelligence profiles.")
    domain_sub = domain.add_subparsers(dest="domain_command", required=True)
    domain_capture = domain_sub.add_parser("capture")
    domain_capture.add_argument("--scope-kind", required=True, choices=("project", "target", "thread", "run"))
    domain_capture.add_argument("--scope-ref", required=True)
    domain_capture.add_argument("--domain-id", required=True)
    domain_capture.add_argument("--mapping", action="append", default=[])
    domain_capture.add_argument("--workflow-hint", action="append", default=[])
    domain_capture.add_argument("--source-class", default="operator_supplied")
    domain_capture.add_argument("--source-ref", default="")
    domain_capture.add_argument("--observation-count", type=int, default=1)
    domain_capture.add_argument("--confidence", type=float, default=0.5)
    domain_capture.set_defaults(func=cmd_memory_domain_capture)
    domain_review = domain_sub.add_parser("review")
    domain_review.set_defaults(func=cmd_memory_domain_review)
    domain_approve = domain_sub.add_parser("approve")
    domain_approve.add_argument("candidate_id")
    domain_approve.add_argument("--approved-by", default="operator")
    domain_approve.set_defaults(func=cmd_memory_domain_approve)
    domain_reject = domain_sub.add_parser("reject")
    domain_reject.add_argument("candidate_id")
    domain_reject.add_argument("--rejected-by", default="operator")
    domain_reject.add_argument("--reason-code", default="operator_request")
    domain_reject.set_defaults(func=cmd_memory_domain_reject)
    domain_inspect = domain_sub.add_parser("inspect")
    domain_inspect.add_argument("--scope-kind", choices=("project", "target", "thread", "run"), default=None)
    domain_inspect.add_argument("--scope-ref", default=None)
    domain_inspect.add_argument("--domain-id", default=None)
    domain_inspect.set_defaults(func=cmd_memory_domain_inspect)
    domain_retire = domain_sub.add_parser("retire")
    domain_retire.add_argument("profile_identifier", nargs="?", default="")
    domain_retire.add_argument("--profile-id", default=None)
    domain_retire.add_argument("--scope-kind", required=True, choices=("project", "target", "thread", "run"))
    domain_retire.add_argument("--scope-ref", required=True)
    domain_retire.add_argument("--revision", required=True, type=int)
    domain_retire.add_argument("--retired-by", default="operator")
    domain_retire.add_argument("--reason-code", default="operator_request")
    domain_retire.set_defaults(func=cmd_memory_domain_retire)

    def _add_lifecycle_parser(name: str, operation: str | None = None):
        parser = memory_sub.add_parser(name, help=f"Preview or apply a revision-bound memory {name} operation.")
        if operation is None:
            parser.add_argument("operation", choices=("retire", "restore", "reapprove", "correct", "confirm", "keep-open", "prune"))
        else:
            parser.set_defaults(operation=operation)
        parser.add_argument("identity", nargs="?", default="", help="Record id (or candidate id for reapprove).")
        parser.add_argument("--record-id", default="")
        parser.add_argument("--revision", type=int, default=None)
        parser.add_argument("--candidate-id", default=None)
        parser.add_argument("--summary", default="")
        parser.add_argument("--reviewer-claim", default="operator")
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--confirm-hard-delete-local", action="store_true")
        parser.set_defaults(func=cmd_memory_lifecycle)
        return parser

    _add_lifecycle_parser("lifecycle")
    for _name in ("retire", "restore", "reapprove", "correct", "confirm", "keep-open", "prune"):
        _add_lifecycle_parser(_name, _name)

    evaluate = memory_sub.add_parser("evaluate", help="Evaluate deterministic retrieval fixture metadata offline.")
    evaluate.add_argument("--fixture", default=None)
    evaluate.add_argument("--target-revision", default="")
    evaluate.set_defaults(func=cmd_memory_evaluate)
    compare = memory_sub.add_parser("compare", help="Compare two retrieval reports with identity guards.")
    compare.add_argument("--left", required=True)
    compare.add_argument("--right", required=True)
    compare.set_defaults(func=cmd_memory_compare)

    apply = memory_sub.add_parser("apply")
    apply.add_argument(
        "--batch",
        required=True,
        help="Path to memory_update_batch/v1 JSON, or '-' to read from stdin.",
    )
    apply.add_argument("--dry-run", action="store_true", help="Validate and preview the batch without writing .omj/memory.")
    apply.set_defaults(func=cmd_memory_apply)
