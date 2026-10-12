from __future__ import annotations

import argparse
from pathlib import Path

from ..hermes_ops import (
    build_scheduled_ops_blueprint,
    list_hermes_ops_blueprints,
    show_hermes_ops_blueprint,
    summarize_hermes_ops_blueprint,
    validate_hermes_ops_store,
    write_hermes_ops_blueprint,
)
from ..install.agent_rules import (
    ExternalRuleImportError,
    apply_rule_import,
    plan_rule_import,
    public_plan,
)
from ..installer import OmjError
from ..operations import (
    ARTIFACT_STATUSES,
    KINDS_BY_SURFACE,
    SURFACES,
    build_operation_artifact,
    export_operations_bundle,
    list_operation_artifacts,
    show_operation_artifact,
    summarize_operation_artifact,
    validate_operations_store,
    write_operation_artifact,
)
from ..operator_productivity import (
    build_agent_operator_productivity_card,
    list_agent_operator_productivity_cards,
    show_agent_operator_productivity_card,
    summarize_agent_operator_productivity_card,
    validate_agent_operator_productivity_store,
    write_agent_operator_productivity_card,
)
from ..quality.agent_debug import (
    OBSERVABLES,
    build_agent_debug_export,
    build_agent_debug_incident,
    build_agent_debug_report,
    parse_turn_range,
    read_receipt,
)
from ..quality.session_file_activity import build_session_file_activity
from ..research_department import (
    build_research_department_plan,
    list_research_department_plans,
    show_research_department_plan,
    summarize_research_department_plan,
    validate_research_department_store,
    write_research_department_plan,
)
from ..workflows.permission_rehearsal import (
    PERMISSION_REHEARSAL_PLAN_SCHEMA_VERSION,
    read_planned_calls,
    rehearse_planned_calls,
)
from ..workflows.plugin_hook_contract import observe_host_version
from ..workflows.plugin_risk_audit import audit_plugin_risk
from ..workflows.research_source_recovery import plan_source_recovery
from .common import _paths, _print_json

DEFAULT_OPS_LIST_LIMIT = 20
DEFAULT_OPS_EXPORT_LIMIT = 20
DEFAULT_BLUEPRINT_LIST_LIMIT = 20
DEFAULT_RESEARCH_DEPARTMENT_LIST_LIMIT = 20
DEFAULT_AGENT_OPS_LIST_LIMIT = 20


def cmd_ops_write(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        artifact = build_operation_artifact(
            surface=args.surface,
            kind=args.kind,
            title=args.title,
            summary=args.summary,
            status=args.status,
            observation_status=_observation_status(args),
            source=args.source,
            inputs_summary=args.inputs_summary,
            sections=args.section or [],
            decisions=args.decision or [],
            action_items=args.action or [],
            metrics=args.metric or [],
            references=args.reference or [],
            assumptions=args.assumption or [],
        )
        written = write_operation_artifact(paths, artifact)
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    _print_json(
        {
            "schema_version": "omj_ops_write_result/v1",
            "artifact": written,
            "store": {
                "omj_home": str(paths.omj_home),
                "operations_dir": str(paths.operations_dir),
                "index_path": str(paths.operations_index_path),
                "index_authority": "cache_only",
            },
            "boundary": {
                "prepared_is_not_observed": written["observation_status"] in {"prepared", "not_observed"},
                "ppt_scope": "markdown_or_json_outline_only",
            },
        }
    )
    return 0


def cmd_ops_blueprint(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        blueprint = build_scheduled_ops_blueprint(
            " ".join(args.request),
            title=args.title,
            schedule=args.schedule,
            delivery=args.delivery,
            silence=args.silence,
            source=args.source,
        )
        written = blueprint if args.dry_run else write_hermes_ops_blueprint(paths, blueprint)
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    _print_json(
        {
            "schema_version": "omj_ops_blueprint_result/v1",
            "blueprint": written,
            "store": {
                "omj_home": str(paths.omj_home),
                "hermes_ops_dir": str(paths.hermes_ops_dir),
                "blueprints_dir": str(paths.hermes_ops_blueprints_dir),
                "index_path": str(paths.hermes_ops_index_path),
                "index_authority": "cache_only",
                "written": not args.dry_run,
            },
            "boundary": {
                "prepared_is_not_observed": True,
                "runtime_execution_observed": False,
                "gateway_delivery_observed": False,
                "source_retrieval_observed": False,
                "not_evidence_until_observed": list(written["not_evidence_until_observed"]),
                "observed_evidence_required": list(written["observed_evidence_required"]),
            },
        }
    )
    return 0


def cmd_ops_research_department(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        plan = build_research_department_plan(
            " ".join(args.request),
            title=args.title,
            topic=args.topic,
            cadence=args.cadence,
            delivery=args.delivery,
            storage=args.storage,
            knowledge_store=args.knowledge_store,
            synthesis_tool=args.synthesis_tool,
            source=args.source,
            sources=args.source_boundary or [],
            notebooklm=args.notebooklm,
            obsidian=args.obsidian,
        )
        written = plan if args.dry_run else write_research_department_plan(paths, plan)
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    _print_json(
        {
            "schema_version": "omj_ops_research_department_result/v1",
            "plan": written,
            "store": {
                "omj_home": str(paths.omj_home),
                "research_department_dir": str(paths.research_department_dir),
                "plans_dir": str(paths.research_department_plans_dir),
                "index_path": str(paths.research_department_index_path),
                "index_authority": "cache_only",
                "written": not args.dry_run,
            },
            "boundary": {
                "prepared_is_not_observed": True,
                "source_retrieval_observed": False,
                "synthesis_tool_query_observed": False,
                "knowledge_store_write_observed": False,
                "notebooklm_execution_observed": False,
                "obsidian_write_observed": False,
                "gateway_delivery_observed": False,
                "not_evidence_until_observed": list(written["not_evidence_until_observed"]),
                "observed_evidence_required": list(written["observed_evidence_required"]),
            },
        }
    )
    return 0


def cmd_ops_agent_review(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        card = build_agent_operator_productivity_card(
            " ".join(args.request),
            title=args.title,
            focus=args.focus,
            source=args.source,
        )
        written = card if args.dry_run else write_agent_operator_productivity_card(paths, card)
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    _print_json(
        {
            "schema_version": "omj_ops_agent_review_result/v1",
            "card": written,
            "store": {
                "omj_home": str(paths.omj_home),
                "agent_ops_dir": str(paths.agent_operator_productivity_dir),
                "cards_dir": str(paths.agent_operator_productivity_cards_dir),
                "index_path": str(paths.agent_operator_productivity_index_path),
                "index_authority": "cache_only",
                "written": not args.dry_run,
            },
            "boundary": {
                "prepared_is_not_observed": True,
                "source_retrieval_observed": False,
                "executor_dispatch_observed": False,
                "executor_session_attached": False,
                "implementation_observed": False,
                "verification_passed": False,
                "review_passed": False,
                "ci_passed": False,
                "merge_observed": False,
                "not_evidence_until_observed": list(written["not_evidence_until_observed"]),
                "observed_evidence_required": list(written["observed_evidence_required"]),
            },
        }
    )
    return 0


def cmd_ops_list(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        surface = args.surface or None
        limit = _limit_from_args(args, default=DEFAULT_OPS_LIST_LIMIT)
        all_records = list_operation_artifacts(paths, surface=surface)
        records = all_records if limit is None else all_records[-limit:]
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    _print_json(
        {
            "schema_version": "omj_ops_list/v1",
            "surface": args.surface or "all",
            "count": len(records),
            "total_count": len(all_records),
            "limit": limit if limit is not None else "all",
            "truncated": limit is not None and len(all_records) > len(records),
            "summary_only": True,
            "index_authority": "cache_only",
            "artifacts": [summarize_operation_artifact(record) for record in records],
        }
    )
    return 0


def cmd_ops_agent_review_list(args: argparse.Namespace) -> int:
    paths = _paths(args)
    try:
        limit = _limit_from_args(args, default=DEFAULT_AGENT_OPS_LIST_LIMIT)
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    all_records = list_agent_operator_productivity_cards(paths)
    records = all_records if limit is None else all_records[-limit:]
    _print_json(
        {
            "schema_version": "omj_ops_agent_review_list/v1",
            "count": len(records),
            "total_count": len(all_records),
            "limit": limit if limit is not None else "all",
            "truncated": limit is not None and len(all_records) > len(records),
            "summary_only": True,
            "index_authority": "cache_only",
            "cards": [summarize_agent_operator_productivity_card(record) for record in records],
        }
    )
    return 0


def cmd_ops_research_department_list(args: argparse.Namespace) -> int:
    paths = _paths(args)
    try:
        limit = _limit_from_args(args, default=DEFAULT_RESEARCH_DEPARTMENT_LIST_LIMIT)
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    all_records = list_research_department_plans(paths)
    records = all_records if limit is None else all_records[-limit:]
    _print_json(
        {
            "schema_version": "omj_ops_research_department_list/v1",
            "count": len(records),
            "total_count": len(all_records),
            "limit": limit if limit is not None else "all",
            "truncated": limit is not None and len(all_records) > len(records),
            "summary_only": True,
            "index_authority": "cache_only",
            "plans": [summarize_research_department_plan(record) for record in records],
        }
    )
    return 0


def cmd_ops_agent_review_show(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        card = show_agent_operator_productivity_card(paths, args.card_id)
    except (FileNotFoundError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json({"schema_version": "omj_ops_agent_review_show/v1", "card": card})
    return 0


def cmd_ops_show(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        artifact = show_operation_artifact(paths, args.artifact_id)
    except (FileNotFoundError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json({"schema_version": "omj_ops_show/v1", "artifact": artifact})
    return 0


def cmd_ops_research_department_show(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        plan = show_research_department_plan(paths, args.plan_id)
    except (FileNotFoundError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json({"schema_version": "omj_ops_research_department_show/v1", "plan": plan})
    return 0


def cmd_ops_blueprint_show(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        blueprint = show_hermes_ops_blueprint(paths, args.blueprint_id)
    except (FileNotFoundError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json({"schema_version": "omj_ops_blueprint_show/v1", "blueprint": blueprint})
    return 0


def cmd_ops_validate(args: argparse.Namespace) -> int:
    paths = _paths(args)
    result = validate_operations_store(paths)
    blueprint_result = validate_hermes_ops_store(paths)
    research_department_result = validate_research_department_store(paths)
    agent_ops_result = validate_agent_operator_productivity_store(paths)
    result["hermes_ops_blueprints"] = blueprint_result
    result["research_department_plans"] = research_department_result
    result["agent_ops_reviews"] = agent_ops_result
    result["ok"] = (
        bool(result["ok"])
        and bool(blueprint_result["ok"])
        and bool(research_department_result["ok"])
        and bool(agent_ops_result["ok"])
    )
    _print_json(result)
    return 0 if result["ok"] else 1


def cmd_ops_blueprint_list(args: argparse.Namespace) -> int:
    paths = _paths(args)
    try:
        limit = _limit_from_args(args, default=DEFAULT_BLUEPRINT_LIST_LIMIT)
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    all_records = list_hermes_ops_blueprints(paths)
    records = all_records if limit is None else all_records[-limit:]
    _print_json(
        {
            "schema_version": "omj_ops_blueprint_list/v1",
            "count": len(records),
            "total_count": len(all_records),
            "limit": limit if limit is not None else "all",
            "truncated": limit is not None and len(all_records) > len(records),
            "summary_only": True,
            "index_authority": "cache_only",
            "blueprints": [summarize_hermes_ops_blueprint(record) for record in records],
        }
    )
    return 0


def cmd_ops_export(args: argparse.Namespace) -> int:
    try:
        paths = _paths(args)
        surface = args.surface or None
        limit = _limit_from_args(args, default=DEFAULT_OPS_EXPORT_LIMIT)
        total_count = len(list_operation_artifacts(paths, surface=surface))
        exported = export_operations_bundle(paths, surface=surface, format=args.format, limit=limit)
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    _print_json(
        {
            "schema_version": "omj_ops_export_result/v1",
            "format": args.format,
            "surface": args.surface or "all",
            "limit": limit if limit is not None else "all",
            "total_count": total_count,
            "exported_count": total_count if limit is None else min(total_count, limit),
            "truncated": limit is not None and total_count > limit,
            "index_authority": "cache_only",
            "ppt_scope": "markdown_or_json_outline_only",
            "export": exported,
        }
    )
    return 0


def _observation_status(args: argparse.Namespace) -> str:
    if args.observed:
        return "observed"
    if args.mixed:
        return "mixed"
    if args.not_observed:
        return "not_observed"
    return "prepared"


def _optional_positive_int(value: int | None) -> int | None:
    if value is None:
        return None
    if value < 1:
        raise ValueError("--limit must be at least 1")
    return value


def _limit_from_args(args: argparse.Namespace, *, default: int) -> int | None:
    if args.all:
        return None
    return _optional_positive_int(args.limit) if args.limit is not None else default


def _add_artifact_args(parser: argparse.ArgumentParser, *, surface: str, default_kind: str) -> None:
    parser.set_defaults(func=cmd_ops_write, surface=surface)
    parser.add_argument("--kind", choices=KINDS_BY_SURFACE[surface], default=default_kind)
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", default="")
    parser.add_argument("--status", choices=ARTIFACT_STATUSES, default="draft")
    parser.add_argument("--source", default="")
    parser.add_argument("--inputs-summary", default="")
    parser.add_argument("--section", action="append")
    parser.add_argument("--decision", action="append")
    parser.add_argument("--action", action="append")
    parser.add_argument("--metric", action="append")
    parser.add_argument("--reference", action="append")
    parser.add_argument("--assumption", action="append")
    observation = parser.add_mutually_exclusive_group()
    observation.add_argument("--observed", action="store_true", help="Mark the artifact as observed with supplied evidence.")
    observation.add_argument("--mixed", action="store_true", help="Mark the artifact as a mix of prepared and observed content.")
    observation.add_argument("--not-observed", action="store_true", help="Mark the artifact as explicitly not observed.")


def cmd_ops_permission_rehearse(args: argparse.Namespace) -> int:
    paths = _paths(args)
    try:
        planned = read_planned_calls(Path(args.plan).expanduser())
        payload = rehearse_planned_calls(planned, omj_home=paths.omj_home, hermes_home=paths.hermes_home)
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    summary = payload.get("summary", {}) if isinstance(payload, dict) else {}
    rules = payload.get("rules", {}) if isinstance(payload, dict) else {}
    if isinstance(summary, dict) and summary.get("refused"):
        return 1
    if isinstance(rules, dict) and rules.get("defect_count"):
        return 3
    return 0


def cmd_ops_plugin_risk_audit(args: argparse.Namespace) -> int:
    try:
        host_version = observe_host_version(declared_version=args.hermes_version, install_dir=Path(args.hermes_install) if args.hermes_install else None)
        payload = audit_plugin_risk(Path(args.path), host_version=host_version)
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0

def cmd_ops_source_recovery(args: argparse.Namespace) -> int:
    try:
        payload = plan_source_recovery(
            canonical_url=args.url,
            failure_class=args.failure_class,
            capability_available=args.capability_available,
            retrieval_budget_remaining=args.budget,
            recovery_attempts_spent=args.attempts,
            source_requirement=args.source_requirement,
            freshness_constraint=args.freshness_constraint,
        )
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    _print_json(payload)
    return 0

def cmd_ops_incident_capsule(args: argparse.Namespace) -> int:
    paths = _paths(args)
    try:
        report = build_agent_debug_report(
            paths.hermes_home,
            args.hermes_session,
            session_record=Path(args.session_record).expanduser(),
            turns=parse_turn_range(args.turns),
            max_rows=args.max_rows,
            max_row_bytes=args.max_row_bytes,
        )
        receipts = tuple(read_receipt(path) for path in (args.receipt or ()))
        incident = build_agent_debug_incident(
            report,
            observable=args.observable,
            receipts=receipts,
        )
        export = build_agent_debug_export(
            {"report": report, "incident": incident},
            hermes_home=paths.hermes_home,
            session_record=Path(args.session_record).expanduser(),
        )
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    _print_json(
        {
            "schema_version": "omj_incident_capsule/v1",
            "report": report,
            "incident": incident,
            "export": export,
            "metadata": {
                "execution_status": "prepared",
                "historical_execution_observed": False,
                "recovery_execution_observed": False,
            },
        }
    )
    return 0


def cmd_ops_file_lineage(args: argparse.Namespace) -> int:
    paths = _paths(args)
    try:
        payload = build_session_file_activity(
            paths.hermes_home,
            args.hermes_session,
            session_record=Path(args.session_record).expanduser(),
            workspace=Path(args.workspace).expanduser() if args.workspace else None,
            max_files=args.max_files,
            focus=args.focus,
            max_rows=args.max_rows,
            max_row_bytes=args.max_row_bytes,
        )
    except (OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    payload["metadata"] = {
        "execution_status": "prepared",
        "historical_execution_observed": False,
        "file_contents_read": False,
    }
    _print_json(payload)
    return 0


def cmd_rules_import(args: argparse.Namespace) -> int:
    paths = _paths(args)
    repo_root = Path(args.repo_root).expanduser()
    skills_dir = Path(args.skills_dir).expanduser() if args.skills_dir else paths.skills_dir
    try:
        plan = plan_rule_import(
            repo_root,
            skills_dir=skills_dir,
            omj_home=paths.omj_home,
            only_sources=tuple(args.source or ()),
        )
        payload = (
            apply_rule_import(plan, skills_dir=skills_dir, omj_home=paths.omj_home)
            if args.apply
            else public_plan(plan)
        )
    except (ExternalRuleImportError, OSError, ValueError) as exc:
        raise OmjError(str(exc)) from exc
    payload["metadata"] = {
        "mode": "apply" if args.apply else "preview",
        "preview_default": True,
        "native_hooks_executed": False,
        "network_used": False,
        "source_ownership": "source-owned",
    }
    _print_json(payload)
    return 0

def _add_ops_commands(sub) -> None:
    ops = sub.add_parser("ops", help="Create, inspect, validate, and export local operations artifacts.")
    ops_sub = ops.add_subparsers(dest="ops_command", required=True)


    recovery = ops_sub.add_parser("source-recovery", help="Plan one bounded research-source recovery handoff without retrieval.")
    recovery.add_argument("--url", required=True, help="Canonical source URL.")
    recovery.add_argument("--failure-class", default="", help="Observed failure class, or empty for direct citation.")
    recovery.add_argument("--capability-available", action="store_true", help="State that the recovery capability is available.")
    recovery.add_argument("--budget", type=int, default=0, help="Remaining retrieval budget.")
    recovery.add_argument("--attempts", type=int, default=0, help="Recovery attempts already spent.")
    recovery.add_argument("--source-requirement", default="")
    recovery.add_argument("--freshness-constraint", default="")
    recovery.set_defaults(func=cmd_ops_source_recovery)
    rehearse = ops_sub.add_parser("permission-rehearse", help="Rehearse planned tool calls against local rules without execution.")
    rehearse.add_argument("--plan", required=True, help=f"Plan file ({PERMISSION_REHEARSAL_PLAN_SCHEMA_VERSION}).")
    rehearse.set_defaults(func=cmd_ops_permission_rehearse)

    audit = ops_sub.add_parser("plugin-risk-audit", help="Statically audit one explicit local plugin directory.")
    audit.add_argument("--path", required=True, help="Explicit local plugin root directory.")
    host = audit.add_mutually_exclusive_group()
    host.add_argument("--hermes-version", help="Hermes version stated by the operator.")
    host.add_argument("--hermes-install", help="Local Hermes installation directory to read version from.")
    audit.set_defaults(func=cmd_ops_plugin_risk_audit)

    incident = ops_sub.add_parser("incident-capsule", help="Build a cited incident capsule from one supplied local session record.")
    incident.add_argument("--session-record", required=True, help="Operator-supplied Hermes JSONL session record.")
    incident.add_argument("--hermes-session", default=None, help="Exact Hermes session id, unique prefix, or latest.")
    incident.add_argument("--observable", choices=OBSERVABLES, default="unspecified")
    incident.add_argument("--turns", default=None, help="User-turn range N, N:M, or N:.")
    incident.add_argument("--max-rows", type=int, default=20000)
    incident.add_argument("--max-row-bytes", type=int, default=262144)
    incident.add_argument("--receipt", action="append", default=None, help="Operator-supplied local receipt JSON (repeatable).")
    incident.set_defaults(func=cmd_ops_incident_capsule)

    lineage = ops_sub.add_parser("file-lineage", help="Project cited file-tool metadata from one supplied local session record.")
    lineage.add_argument("--session-record", required=True, help="Operator-supplied Hermes JSONL session record.")
    lineage.add_argument("--hermes-session", required=True, help="Exact Hermes session id, unique prefix, or latest.")
    lineage.add_argument("--workspace", default=None, help="Optional explicit workspace root for relative paths.")
    lineage.add_argument("--max-files", type=int, default=100)
    lineage.add_argument("--max-rows", type=int, default=20000)
    lineage.add_argument("--max-row-bytes", type=int, default=262144)
    lineage.add_argument("--focus", action="append", default=None, help="Workspace-relative path prefix (repeatable).")
    lineage.set_defaults(func=cmd_ops_file_lineage)

    rules_import = sub.add_parser("rules-import", help="Preview or apply external agent rules into managed imported skills.")
    rules_import.add_argument("--repo-root", required=True, help="Explicit local source repository root.")
    rules_import.add_argument("--source", action="append", default=None, help="Limit to a discovered source path (repeatable).")
    rules_import.add_argument("--skills-dir", default=None, help="Managed OMJ skills directory override.")
    rules_import.add_argument("--apply", action="store_true", help="Apply the prepared plan; preview is the default.")
    rules_import.set_defaults(func=cmd_rules_import)
    rhythm = ops_sub.add_parser("rhythm", help="Create an operating rhythm artifact such as a meeting or retro record.")
    _add_artifact_args(rhythm, surface="operating-rhythm", default_kind="meeting")

    report = ops_sub.add_parser("report", help="Create a report package or PPT-ready outline artifact.")
    _add_artifact_args(report, surface="report-package", default_kind="status-package")

    reliability = ops_sub.add_parser("reliability", help="Create a reliability review artifact such as an SLO or postmortem review.")
    _add_artifact_args(reliability, surface="reliability-review", default_kind="service-review")

    blueprint = ops_sub.add_parser("blueprint", help="Prepare a Hermes scheduled ops blueprint without creating runtime automation.")
    blueprint.add_argument("request", nargs="+", help="Natural-language scheduled ops request.")
    blueprint.add_argument("--title", default="")
    blueprint.add_argument("--schedule", default="", help="Explicit schedule/cadence hint.")
    blueprint.add_argument("--delivery", default="", help="Explicit delivery target hint.")
    blueprint.add_argument("--silence", default="", help="Explicit silence/no-change policy hint.")
    blueprint.add_argument("--source", default="", help="Optional metadata source label.")
    blueprint.add_argument("--dry-run", action="store_true", help="Print the prepared blueprint without writing it.")
    blueprint.set_defaults(func=cmd_ops_blueprint)

    research_department = ops_sub.add_parser(
        "research-department",
        help="Prepare a Scout/Analyst/Briefer research department workflow without running research.",
    )
    research_department.add_argument("request", nargs="+", help="Natural-language research operations request.")
    research_department.add_argument("--title", default="")
    research_department.add_argument("--topic", default="", help="Explicit research topic or watch area.")
    research_department.add_argument("--cadence", default="", help="Explicit cadence hint such as daily or weekly.")
    research_department.add_argument("--delivery", default="", help="Explicit delivery target hint.")
    research_department.add_argument("--storage", default="", help="Compatibility alias for --knowledge-store.")
    research_department.add_argument("--knowledge-store", default="", help="Knowledge store target such as markdown folder, note vault, or database.")
    research_department.add_argument("--synthesis-tool", default="", help="Knowledge synthesis tool hint such as Hermes synthesis, NotebookLM, or local RAG.")
    research_department.add_argument("--source", default="", help="Optional metadata source label.")
    research_department.add_argument("--source-boundary", action="append", help="Allowed source, source family, or scope boundary.")
    research_department.add_argument(
        "--notebooklm",
        choices=("unknown", "available", "unavailable", "preferred"),
        default="unknown",
        help="Compatibility alias for a NotebookLM synthesis-tool readiness hint; OMJ does not probe or invoke it.",
    )
    research_department.add_argument(
        "--obsidian",
        choices=("unknown", "available", "unavailable", "preferred"),
        default="unknown",
        help="Compatibility alias for an Obsidian knowledge-store readiness hint; OMJ does not probe or write to it.",
    )
    research_department.add_argument("--dry-run", action="store_true", help="Print the prepared plan without writing it.")
    research_department.set_defaults(func=cmd_ops_research_department)

    agent_review = ops_sub.add_parser(
        "agent-review",
        help="Prepare a manager-facing agent ops review card for research, coding, review, and status productivity.",
    )
    agent_review.add_argument("request", nargs="+", help="Natural-language agent operations management request.")
    agent_review.add_argument("--title", default="")
    agent_review.add_argument("--focus", choices=("auto", "mixed", "research", "coding", "review", "status"), default="auto")
    agent_review.add_argument("--source", default="", help="Optional metadata source label.")
    agent_review.add_argument("--dry-run", action="store_true", help="Print the prepared card without writing it.")
    agent_review.set_defaults(func=cmd_ops_agent_review)

    blueprint_list = ops_sub.add_parser("blueprint-list", help="List prepared Hermes scheduled ops blueprints.")
    blueprint_list.add_argument("--limit", type=int, default=None)
    blueprint_list.add_argument("--all", action="store_true", help="Return all blueprint summaries instead of the default bounded window.")
    blueprint_list.set_defaults(func=cmd_ops_blueprint_list)

    blueprint_show = ops_sub.add_parser("blueprint-show", help="Show one prepared Hermes scheduled ops blueprint by id.")
    blueprint_show.add_argument("blueprint_id")
    blueprint_show.set_defaults(func=cmd_ops_blueprint_show)

    research_department_list = ops_sub.add_parser("research-department-list", help="List prepared research department plans.")
    research_department_list.add_argument("--limit", type=int, default=None)
    research_department_list.add_argument("--all", action="store_true", help="Return all plan summaries instead of the default bounded window.")
    research_department_list.set_defaults(func=cmd_ops_research_department_list)

    research_department_show = ops_sub.add_parser("research-department-show", help="Show one research department plan by id.")
    research_department_show.add_argument("plan_id")
    research_department_show.set_defaults(func=cmd_ops_research_department_show)

    agent_review_list = ops_sub.add_parser("agent-review-list", help="List prepared agent ops review cards.")
    agent_review_list.add_argument("--limit", type=int, default=None)
    agent_review_list.add_argument("--all", action="store_true", help="Return all cards instead of the default bounded window.")
    agent_review_list.set_defaults(func=cmd_ops_agent_review_list)

    agent_review_show = ops_sub.add_parser("agent-review-show", help="Show one prepared agent ops review card by id.")
    agent_review_show.add_argument("card_id")
    agent_review_show.set_defaults(func=cmd_ops_agent_review_show)

    list_cmd = ops_sub.add_parser("list", help="List operations artifacts from local storage.")
    list_cmd.add_argument("--surface", choices=SURFACES, default="")
    list_cmd.add_argument("--limit", type=int, default=None)
    list_cmd.add_argument("--all", action="store_true", help="Return all artifact summaries instead of the default bounded window.")
    list_cmd.set_defaults(func=cmd_ops_list)

    show = ops_sub.add_parser("show", help="Show one operations artifact by id.")
    show.add_argument("artifact_id")
    show.set_defaults(func=cmd_ops_show)

    validate = ops_sub.add_parser("validate", help="Validate operations artifacts and cache metadata.")
    validate.set_defaults(func=cmd_ops_validate)

    export = ops_sub.add_parser("export", help="Export operations artifacts as JSON or Markdown content inside JSON output.")
    export.add_argument("--surface", choices=SURFACES, default="")
    export.add_argument("--format", choices=("json", "markdown"), default="json")
    export.add_argument("--limit", type=int, default=None)
    export.add_argument("--all", action="store_true", help="Export all matching artifacts instead of the default bounded window.")
    export.set_defaults(func=cmd_ops_export)
