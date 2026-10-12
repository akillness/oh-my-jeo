from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path

from ..catalogs.provider_auth import (
    diagnose_provider_auth,
    get_provider_auth,
    list_provider_auth,
)
from ..coding.request_verdicts import (
    COMPLEXITY_TIER_EFFORTS,
    build_model_contract_coverage,
    coverage_exit_code,
    data_handling_filtered_chain,
    model_data_handling_verdict,
    recommend_model_for_complexity,
    score_request_complexity,
)
from ..installer import OmjError
from .common import _print_json, _wants_json


def cmd_providers_list(args: argparse.Namespace) -> int:
    payload = list_provider_auth()
    if _wants_json(args):
        _print_json(payload)
    else:
        _print_providers_list_summary(payload)
    return 0


def cmd_providers_inspect(args: argparse.Namespace) -> int:
    try:
        payload = get_provider_auth(args.id)
    except KeyError as exc:
        raise OmjError(f"unknown provider: {args.id}") from exc
    if _wants_json(args):
        _print_json(payload)
    else:
        _print_provider_summary(payload["provider"])
    return 0


def cmd_providers_doctor(args: argparse.Namespace) -> int:
    payload = diagnose_provider_auth()
    if _wants_json(args):
        _print_json(payload)
    else:
        _print_providers_doctor_summary(payload)
    return 0

_MAX_JSON_INPUT_BYTES = 256 * 1024


def _read_bounded_provider_file(path: Path, label: str) -> str:
    flags = os.O_RDONLY | os.O_NONBLOCK
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise ValueError(f"{label} must be a JSON object or readable JSON path") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError(f"{label} path must be a regular file")
        if info.st_size > _MAX_JSON_INPUT_BYTES:
            raise ValueError(f"{label} exceeds maximum size of {_MAX_JSON_INPUT_BYTES} bytes")
        raw = os.read(fd, _MAX_JSON_INPUT_BYTES + 1)
    except OSError as exc:
        raise ValueError(f"{label} must be a JSON object or readable JSON path") from exc
    finally:
        os.close(fd)
    if len(raw) > _MAX_JSON_INPUT_BYTES:
        raise ValueError(f"{label} exceeds maximum size of {_MAX_JSON_INPUT_BYTES} bytes")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} must be valid UTF-8 JSON") from exc


def _read_json_object(value: str, label: str) -> dict[str, object]:
    if value == "-":
        stream = getattr(sys.stdin, "buffer", sys.stdin)
        raw_value = stream.read(_MAX_JSON_INPUT_BYTES + 1)
        if isinstance(raw_value, bytes):
            try:
                raw = raw_value.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError(f"{label} must be valid UTF-8 JSON") from exc
        else:
            raw = str(raw_value)
    else:
        raw = value
        if value not in {"", "-"} and not value.lstrip().startswith(("{", "[")):
            candidate = Path(value).expanduser()
            if candidate.exists():
                raw = _read_bounded_provider_file(candidate, label)
    if len(raw.encode("utf-8")) > _MAX_JSON_INPUT_BYTES:
        raise ValueError(f"{label} exceeds maximum size of {_MAX_JSON_INPUT_BYTES} bytes")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} must be a JSON object or readable JSON path") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def _read_chain_config(path: str) -> dict[str, list[tuple[str, str]]]:
    if not path:
        return {}
    payload = _read_json_object(path, "chain config")
    chains: dict[str, list[tuple[str, str]]] = {}
    for model_class, values in payload.items():
        model_class_text = str(model_class).strip()
        if not model_class_text:
            raise ValueError("chain config model classes must not be blank")
        if not isinstance(values, list):
            raise ValueError("chain config values must be arrays")
        rows: list[tuple[str, str]] = []
        for value in values:
            if isinstance(value, (list, tuple)) and len(value) >= 2:
                model, effort = str(value[0]).strip(), str(value[1]).strip()
            elif isinstance(value, dict):
                model = str(value.get("model", value.get("model_id", ""))).strip()
                effort = str(value.get("reasoning_effort", value.get("effort", ""))).strip()
            else:
                raise ValueError("chain entries must be [model, effort] pairs or objects")
            if not model or not effort:
                raise ValueError("chain entries must include model and effort")
            if effort not in set(COMPLEXITY_TIER_EFFORTS.values()):
                raise ValueError(f"chain effort must be one of {tuple(COMPLEXITY_TIER_EFFORTS.values())}")
            rows.append((model, effort))
        chains[model_class_text] = rows
    return chains


def _chain_option(value: str) -> tuple[str, str, str]:
    if "=" not in value:
        raise ValueError("--chain must use MODEL_CLASS=MODEL:EFFORT")
    model_class, pair = value.split("=", 1)
    if ":" not in pair:
        raise ValueError("--chain must use MODEL_CLASS=MODEL:EFFORT")
    model, effort = pair.rsplit(":", 1)
    model_text, effort_text, class_text = model.strip(), effort.strip(), model_class.strip()
    if not model_text or not effort_text or not class_text:
        raise ValueError("--chain must include class, model, and effort")
    if effort_text not in set(COMPLEXITY_TIER_EFFORTS.values()):
        raise ValueError(f"--chain effort must be one of {tuple(COMPLEXITY_TIER_EFFORTS.values())}")
    return class_text, model_text, effort_text


def cmd_providers_complexity(args: argparse.Namespace) -> int:
    message = " ".join(args.message).strip()
    if not message:
        raise OmjError("providers complexity requires a request message")
    try:
        complexity = score_request_complexity(message, routed_skill=args.routed_skill)
        chains = _read_chain_config(args.chain_json)
        for value in args.chain or []:
            model_class, model, effort = _chain_option(value)
            chains.setdefault(model_class, []).append((model, effort))
        recommendation = recommend_model_for_complexity(
            complexity,
            chains=chains if chains else None,
            requested_model=args.model,
            requested_effort=args.effort,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise OmjError(str(exc)) from exc
    payload = {**complexity, "recommendation": recommendation}
    if _wants_json(args):
        _print_json(payload)
    else:
        print("OMJ offline request complexity")
        print(f"  Tier: {complexity.get('tier')} (score {complexity.get('score')})")
        print(f"  Model class: {recommendation.get('model_class')}")
        print(f"  Chain status: {recommendation.get('chain_status')}")
        print(f"Boundary: {complexity.get('claim_boundary')}")
    return 0


def cmd_providers_model_coverage(args: argparse.Namespace) -> int:
    try:
        inventory = _read_json_object(args.inventory, "inventory")
        report = build_model_contract_coverage(
            inventory,
            required_models=args.required_model or [],
            recommended_models=args.recommended_model or [],
            intentional_exclusions=args.exclude_model or [],
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise OmjError(str(exc)) from exc
    exit_code = coverage_exit_code(report)
    payload = {**report, "exit_code": exit_code}
    if _wants_json(args):
        _print_json(payload)
    else:
        summary = report.get("comparison", {}).get("summary", {})
        print("OMJ offline model-contract coverage")
        print(f"  Outcome: {summary.get('outcome')}")
        print(f"  Models: {summary.get('total_models', 0)}")
        print(f"  Required gaps: {summary.get('required_missing', 0)}")
        print(f"Boundary: {report.get('claim_boundary')}")
    return exit_code


def _contracts(args: argparse.Namespace) -> dict[str, dict[str, object]] | None:
    if not args.contracts:
        return None
    payload = _read_json_object(args.contracts, "contracts")
    return {str(key): value for key, value in payload.items() if isinstance(value, dict)}


def cmd_providers_model_verdict(args: argparse.Namespace) -> int:
    model_id = str(args.model_id or args.model_option or "").strip()
    if not model_id:
        raise OmjError("model-verdict requires a model id")
    try:
        contracts = _contracts(args)
        result = model_data_handling_verdict(model_id, **({"contracts": contracts} if contracts is not None else {}))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise OmjError(str(exc)) from exc
    if _wants_json(args):
        _print_json(result)
    else:
        print("OMJ offline model data-handling verdict")
        print(f"  Model: {result.get('model')}")
        print(f"  Verdict: {result.get('verdict')}")
        print(f"  Reason: {result.get('reason')}")
        print(f"Boundary: {result.get('claim_boundary')}")
    return 0


def cmd_providers_sensitive_chain(args: argparse.Namespace) -> int:
    try:
        contracts = _contracts(args)
        kwargs = {"work_is_sensitive": bool(args.work_is_sensitive)}
        if contracts is not None:
            kwargs["contracts"] = contracts
        result = data_handling_filtered_chain(args.model_ids, **kwargs)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise OmjError(str(exc)) from exc
    if _wants_json(args):
        _print_json(result)
    else:
        summary = result.get("summary", {})
        print("OMJ offline sensitive-work chain")
        print(f"  Sensitive declaration: {result.get('work_is_sensitive')}")
        print(f"  Permitted: {summary.get('permitted', 0)} / {summary.get('requested', 0)}")
        print(f"Boundary: {result.get('claim_boundary')}")
    return 0


def _print_providers_list_summary(payload: dict[str, object]) -> None:
    providers = payload.get("providers", [])
    if not isinstance(providers, list):
        providers = []
    print("OMJ provider-auth catalog")
    print("Summary")
    print(f"  Providers: {len(providers)}")
    for kind in ("oauth", "local_endpoint", "api_key"):
        rows = [p for p in providers if isinstance(p, dict) and p.get("auth_kind") == kind]
        if not rows:
            continue
        print(f"  {kind} ({len(rows)})")
        for provider in rows:
            consumed = ", ".join(str(item) for item in provider.get("consumed_by", []))
            print(f"    - {provider.get('id')}: {provider.get('label')} [{consumed}]")
    print("Boundary")
    print(f"  {payload.get('boundary')}")
    print("Next")
    print("  Inspect one with `omj providers inspect anthropic`.")
    print("  Check host configuration with `omj providers doctor`.")
    print("  For machine-readable output, rerun with `--json`.")


def _print_provider_summary(provider: dict[str, object]) -> None:
    print(f"OMJ provider-auth: {provider.get('id')} - {provider.get('label')}")
    print("Shape")
    print(f"  Auth kind: {provider.get('auth_kind')}")
    print(f"  Provider family: {provider.get('provider_family')}")
    print(f"  Consumed by: {', '.join(str(item) for item in provider.get('consumed_by', []))}")
    print(f"  Requires secret: {provider.get('requires_secret')}")
    print("Host signals")
    api_env = provider.get("api_key_env", [])
    print(f"  API key env: {', '.join(str(item) for item in api_env) if api_env else '(none)'}")
    endpoint_env = provider.get("endpoint_env", [])
    print(f"  Endpoint env: {', '.join(str(item) for item in endpoint_env) if endpoint_env else '(none)'}")
    print(f"  Default endpoint: {provider.get('default_endpoint') or '(none)'}")
    print("Login")
    print(f"  {provider.get('login_hint')}")
    if provider.get("note"):
        print(f"  Note: {provider.get('note')}")
    print("Boundary")
    print(f"  {provider.get('boundary_rule')}")
    print("  For machine-readable output, rerun with `--json`.")


def _print_providers_doctor_summary(payload: dict[str, object]) -> None:
    providers = payload.get("providers", [])
    if not isinstance(providers, list):
        providers = []
    summary = payload.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    print("OMJ provider-auth host diagnostic")
    print("Summary")
    print(f"  Providers: {summary.get('total')}")
    print(f"  Configured: {summary.get('configured')}")
    print(f"  Missing required key: {summary.get('missing_required')}")
    print(f"  Host-managed (OAuth): {summary.get('host_managed')}")
    print("Providers")
    for provider in providers:
        if not isinstance(provider, dict):
            continue
        present = provider.get("api_key_env_present", [])
        marker = ", ".join(str(item) for item in present) if present else "no api-key env"
        print(f"  - {provider.get('id')}: {provider.get('status')} ({marker})")
    print("Boundary")
    print(f"  {payload.get('boundary')}")
    print("Next")
    print("  Set the missing host env var for the coding owner you selected, or run OAuth login in that runtime.")
    print("  For machine-readable output, rerun with `--json`.")


def _add_providers_commands(sub) -> None:
    providers = sub.add_parser(
        "providers",
        help="List provider-auth descriptors or diagnose host credential configuration (metadata-only).",
    )
    providers_sub = providers.add_subparsers(dest="providers_command", required=True)

    list_cmd = providers_sub.add_parser("list")
    list_cmd.add_argument("--json", action="store_true", help="Print the full machine-readable provider-auth catalog.")
    list_cmd.set_defaults(func=cmd_providers_list)

    inspect_cmd = providers_sub.add_parser("inspect")
    inspect_cmd.add_argument("id", help="Provider id such as anthropic, antigravity, lmstudio, ollama, or groq.")
    inspect_cmd.add_argument("--json", action="store_true", help="Print the full machine-readable provider descriptor.")
    inspect_cmd.set_defaults(func=cmd_providers_inspect)

    doctor_cmd = providers_sub.add_parser("doctor")
    doctor_cmd.add_argument("--json", action="store_true", help="Print machine-readable host provider-auth diagnostic.")
    doctor_cmd.set_defaults(func=cmd_providers_doctor)

    complexity = providers_sub.add_parser(
        "complexity",
        aliases=("request-complexity",),
        help="Score request complexity and expose an executor-neutral offline recommendation.",
    )
    complexity.add_argument("message", nargs="*", help="Request text; raw text is never echoed in the output payload.")
    complexity.add_argument("--routed-skill", default="", help="Optional routed skill family used only as a scoring signal.")
    complexity.add_argument("--chain", action="append", default=[], metavar="CLASS=MODEL:EFFORT", help="Declared local chain metadata; repeatable.")
    complexity.add_argument("--chain-json", "--chain-file", default="", dest="chain_json", help="JSON object or path containing class -> chain entries.")
    complexity.add_argument("--model", default="", help="Explicit caller-owned model metadata; no default is selected.")
    complexity.add_argument("--effort", default="", help="Explicit caller-owned reasoning effort metadata.")
    complexity.add_argument("--json", action="store_true", help="Print the full machine-readable verdict.")
    complexity.set_defaults(func=cmd_providers_complexity)

    coverage = providers_sub.add_parser(
        "model-coverage",
        aliases=("coverage", "contract-coverage"),
        help="Compare a local model inventory with declared offline contract metadata.",
    )
    coverage.add_argument("--inventory", "--inventory-json", required=True, dest="inventory", help="JSON object, inline or file path; '-' reads stdin.")
    coverage.add_argument("--required-model", action="append", default=[], dest="required_model")
    coverage.add_argument("--recommended-model", action="append", default=[], dest="recommended_model")
    coverage.add_argument("--exclude-model", action="append", default=[], dest="exclude_model")
    coverage.add_argument("--json", action="store_true", help="Print the full machine-readable coverage report.")
    coverage.set_defaults(func=cmd_providers_model_coverage)

    verdict = providers_sub.add_parser(
        "model-verdict",
        aliases=("verdict", "data-handling"),
        help="Read one model's documented data-handling metadata without provider access.",
    )
    verdict.add_argument("model_id", nargs="?", default="")
    verdict.add_argument("--model", dest="model_option", default="", help="Model id; positional form is also accepted.")
    verdict.add_argument("--contracts", "--contracts-json", default="", dest="contracts", help="Optional JSON object or path overriding local contracts.")
    verdict.add_argument("--json", action="store_true", help="Print the full machine-readable verdict.")
    verdict.set_defaults(func=cmd_providers_model_verdict)

    sensitive = providers_sub.add_parser(
        "sensitive-chain",
        aliases=("sensitive", "filter-chain"),
        help="Filter a declared model chain only when the caller declares sensitive work.",
    )
    sensitive.add_argument("model_ids", nargs="+")
    sensitive.add_argument("--sensitive", "--work-is-sensitive", action="store_true", dest="work_is_sensitive")
    sensitive.add_argument("--contracts", "--contracts-json", default="", dest="contracts", help="Optional JSON object or path overriding local contracts.")
    sensitive.add_argument("--json", action="store_true", help="Print the full machine-readable chain verdict.")
    sensitive.set_defaults(func=cmd_providers_sensitive_chain)
