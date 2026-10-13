from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Mapping
from urllib.parse import urlsplit
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
from ..coding.model_contracts import MODEL_CONTRACTS, model_contract_projection
from ..installer import OmjError
from ..system.paths import resolve_paths
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
_MODEL_CONFIG_MAX_BYTES = 512 * 1024
_MODEL_REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,159}$")
_MODEL_SECRET_RE = re.compile(
    r"^(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|gsk_[A-Za-z0-9_-]{20,})$",
    re.IGNORECASE,
)
_SENSITIVE_MODEL_MARKERS = ("secret", "token", "password", "credential", "authorization", "bearer")
_UNPINNED_PROVIDER_MARKERS = frozenset({"", "auto", "null", "~", "default", "none"})
MODEL_INSPECTION_CLAIM_BOUNDARY = (
    "Model inspection reads only the selected Hermes config and local OMJ contract metadata. "
    "It is read-only advisory evidence: known, discovered, or explicitly confirmed ids are not "
    "availability, entitlement, login, quota, routing, or execution evidence."
)


def _selected_hermes_home(args: argparse.Namespace) -> Path:
    explicit = getattr(args, "hermes_home", None)
    if explicit:
        return Path(os.path.expandvars(str(explicit))).expanduser()
    return resolve_paths(
        getattr(args, "omj_home", None),
        None,
        scope=getattr(args, "scope", None),
    ).hermes_home


def _read_model_source(path: Path) -> tuple[dict[str, object], str]:
    base = {"path": str(path), "found": False, "readable": False, "sha256": ""}
    try:
        if not path.exists():
            base["status"] = "absent"
            return base, ""
        if not path.is_file() or path.stat().st_size > _MODEL_CONFIG_MAX_BYTES:
            base["status"] = "unreadable"
            return base, ""
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        base.update({"found": True, "readable": True, "sha256": digest, "status": "present"})
        try:
            return base, raw.decode("utf-8")
        except UnicodeDecodeError:
            base.update({"readable": False, "status": "unreadable"})
            return base, ""
    except OSError:
        base["status"] = "unreadable"
        return base, ""


def _yaml_scalar(value: str) -> str:
    value = value.split(" #", 1)[0].strip()
    return value.strip("'\"")


def _safe_model_ref(value: object) -> str:
    if not isinstance(value, str):
        return ""
    ref = value.strip()
    lowered = ref.casefold()
    if not ref or not _MODEL_REF_RE.fullmatch(ref):
        return ""
    if _MODEL_SECRET_RE.fullmatch(ref) or any(marker in lowered for marker in _SENSITIVE_MODEL_MARKERS):
        return ""
    return ref


def _model_config_values(text: str) -> tuple[dict[str, str], dict[str, str]]:
    lines = text.splitlines()
    if "\x00" in text or "\t" in text:
        raise ValueError("model config shape is ambiguous")
    block_indexes = [index for index, line in enumerate(lines) if not line.startswith(" ") and line.rstrip() == "model:"]
    dotted: list[tuple[str, str]] = []
    for line in lines:
        if line.startswith(" "):
            continue
        key, separator, value = line.partition(":")
        if separator and key.startswith("model."):
            dotted.append((key[6:], _yaml_scalar(value)))
    if len(block_indexes) > 1 or (block_indexes and dotted) or (not block_indexes and not dotted):
        raise ValueError("model config shape is ambiguous")
    scalars: dict[str, str] = {}
    aliases: dict[str, str] = {}
    if dotted:
        for key, value in dotted:
            if key.startswith("aliases."):
                alias = _safe_model_ref(key[8:])
                target = _safe_model_ref(value)
                if alias and target:
                    aliases[alias] = target
            elif key in {"default", "provider", "base_url"}:
                scalars[key] = value
        return scalars, aliases
    model_index = block_indexes[0]
    in_aliases = False
    for line in lines[model_index + 1 :]:
        if line and not line.startswith(" "):
            break
        if line.startswith("  ") and not line.startswith("    "):
            key, separator, value = line.strip().partition(":")
            if not separator:
                continue
            in_aliases = key == "aliases" and not value.strip()
            if key != "aliases":
                scalars[key] = _yaml_scalar(value)
            continue
        if in_aliases and line.startswith("    "):
            key, separator, value = line.strip().partition(":")
            if separator:
                alias = _safe_model_ref(key)
                target = _safe_model_ref(_yaml_scalar(value))
                if alias and target:
                    aliases[alias] = target
    return scalars, aliases


def _model_source_payload(home: Path) -> tuple[dict[str, object], dict[str, str], dict[str, str]]:
    source, text = _read_model_source(home / "config.yaml")
    if not text:
        return source, {}, {}
    try:
        scalars, aliases = _model_config_values(text)
    except ValueError:
        source = {**source, "readable": False, "status": "unreadable"}
        return source, {}, {}
    return source, scalars, aliases


def _model_family(model_id: str) -> str:
    family, separator, rest = model_id.partition("/")
    return family.casefold() if separator and rest else ""


def _base_url_host(value: str) -> str:
    if not value:
        return ""
    candidate = value if "://" in value else f"//{value}"
    try:
        host = urlsplit(candidate).hostname or ""
    except ValueError:
        return ""
    return host if re.fullmatch(r"[A-Za-z0-9._:-]{1,253}", host) else ""


def _routing_disagreements(scalars: Mapping[str, str]) -> list[str]:
    default_model = _safe_model_ref(scalars.get("default", ""))
    family = _model_family(default_model)
    provider = _safe_model_ref(scalars.get("provider", "")).casefold()
    host = _base_url_host(scalars.get("base_url", ""))
    if not default_model or not family or not host or provider not in _UNPINNED_PROVIDER_MARKERS:
        return []
    host_core = host.casefold().rstrip(".").rsplit(".", 1)[0] if "." in host else host.casefold()
    if family in host_core:
        return []
    return [
        f"`model.default` is `{default_model}`, but `model.base_url` sends requests to `{host}` and `model.provider` is unset"
    ]


def _model_rows(scalars: Mapping[str, str], aliases: Mapping[str, str], confirmed: Sequence[str] = ()) -> list[dict[str, object]]:
    rows: dict[str, dict[str, object]] = {}
    confirmed_ids = {_safe_model_ref(value).casefold() for value in confirmed if _safe_model_ref(value)}
    default_model = _safe_model_ref(scalars.get("default", ""))

    for model_id in sorted(MODEL_CONTRACTS):
        projection = model_contract_projection(model_id) or {}
        rows[model_id.casefold()] = {
            "model_id": model_id,
            "provider": _model_family(model_id),
            "status": "known",
            "provenance": str(projection.get("provenance", "exact")),
            "contract_model_id": str(projection.get("contract_model_id", model_id)),
            "source": "local_contract_metadata",
        }
    observed: list[tuple[str, str]] = []
    if default_model:
        observed.append((default_model, "config"))
    observed.extend((target, "alias") for target in aliases.values())
    for model_id, source in observed:
        key = model_id.casefold()
        projection = model_contract_projection(model_id) or {}
        row = rows.get(key, {})
        row.update({
            "model_id": model_id,
            "provider": _model_family(model_id),
            "status": "explicitly_confirmed" if key in confirmed_ids else "discovered",
            "provenance": source,
            "contract_model_id": str(projection.get("contract_model_id", "")) or None,
            "contract_provenance": str(projection.get("provenance", "")) or None,
            "source": source,
        })
        rows[key] = row
    for model_id in confirmed:
        value = _safe_model_ref(model_id)
        if not value:
            continue
        key = value.casefold()
        row = rows.get(
            key,
            {
                "model_id": value,
                "provider": _model_family(value),
                "status": "explicitly_confirmed",
                "provenance": "user_confirmation",
                "contract_model_id": None,
                "contract_provenance": None,
                "source": "user_confirmation",
            },
        )
        row.update({
            "model_id": value,
            "status": "explicitly_confirmed",
            "provenance": "user_confirmation",
            "contract_model_id": row.get("contract_model_id"),
            "contract_provenance": row.get("contract_provenance"),
            "source": "user_confirmation",
        })
        rows[key] = row
    return [rows[key] for key in sorted(rows)]


def build_model_inventory(hermes_home: str | Path | None = None, *, confirmed_models: Sequence[str] = ()) -> dict[str, object]:
    home = Path(hermes_home).expanduser() if hermes_home is not None else resolve_paths().hermes_home
    source, scalars, aliases = _model_source_payload(home)
    return {
        "schema_version": "model_inventory/v1",
        "source_state": {"config": source},
        "config": {"path": source["path"], "found": source["found"], "readable": source["readable"], "digest": source["sha256"]},
        "models": _model_rows(scalars, aliases, confirmed_models),
        "claim_boundary": MODEL_INSPECTION_CLAIM_BOUNDARY,
    }


def build_model_status(hermes_home: str | Path | None = None) -> dict[str, object]:
    home = Path(hermes_home).expanduser() if hermes_home is not None else resolve_paths().hermes_home
    source, scalars, aliases = _model_source_payload(home)
    default_model = _safe_model_ref(scalars.get("default", ""))
    provider = _safe_model_ref(scalars.get("provider", "")).casefold()
    base_url = scalars.get("base_url", "")
    host = _base_url_host(base_url)
    return {
        "schema_version": "hermes_model_status/v1",
        "source_state": {"config": source},
        "config": {"path": source["path"], "found": source["found"], "readable": source["readable"], "digest": source["sha256"]},
        "default_model": {"value": default_model, "family": _model_family(default_model)},
        "provider": {"value": provider, "pinned": provider not in _UNPINNED_PROVIDER_MARKERS},
        "base_url": {"set": bool(base_url), "host": host},
        "models": _model_rows(scalars, aliases),
        "disagreements": _routing_disagreements(scalars),
        "claim_boundary": MODEL_INSPECTION_CLAIM_BOUNDARY,
    }


def _alias_changes(values: Sequence[str] | Mapping[str, str]) -> dict[str, str]:
    if isinstance(values, Mapping):
        items = values.items()
    else:
        items = (str(value).split("=", 1) for value in values)
    changes: dict[str, str] = {}
    for raw_alias, raw_target in items:
        alias = _safe_model_ref(raw_alias)
        target = _safe_model_ref(raw_target)
        if not alias or not target:
            raise ValueError("--model-alias requires NAME=MODEL with safe metadata references")
        changes[alias] = target
    return changes


def build_model_setup_preview(
    hermes_home: str | Path | None = None,
    *,
    confirm_models: Sequence[str] = (),
    model_aliases: Sequence[str] | Mapping[str, str] = (),
    expected_digest: str = "",
) -> dict[str, object]:
    home = Path(hermes_home).expanduser() if hermes_home is not None else resolve_paths().hermes_home
    source, scalars, aliases = _model_source_payload(home)
    changes = _alias_changes(model_aliases)
    collisions = {
        alias: {"existing": aliases[alias], "proposed": target}
        for alias, target in changes.items()
        if alias in aliases and aliases[alias] != target
    }
    current_digest = str(source.get("sha256", ""))
    digest_match = not expected_digest or expected_digest == current_digest
    return {
        "schema_version": "model_setup_preview/v1",
        "source_state": {"config": source},
        "config": {"path": source["path"], "found": source["found"], "readable": source["readable"], "digest": current_digest},
        "models": _model_rows(scalars, aliases, confirm_models),
        "confirmed_models": [_safe_model_ref(value) for value in confirm_models if _safe_model_ref(value)],
        "changes": changes,
        "proposed_aliases": {**aliases, **changes},
        "collisions": collisions,
        "drift": {"expected_digest": expected_digest, "current_digest": current_digest, "match": digest_match},
        "claim_boundary": MODEL_INSPECTION_CLAIM_BOUNDARY,
    }


def cmd_providers_model_inventory(args: argparse.Namespace) -> int:
    payload = build_model_inventory(_selected_hermes_home(args))
    if _wants_json(args):
        _print_json(payload)
    else:
        print("OMJ local model inventory")
        print(f"  Models: {len(payload['models'])}")
        print(f"Boundary: {payload['claim_boundary']}")
    return 0


def cmd_providers_model_status(args: argparse.Namespace) -> int:
    payload = build_model_status(_selected_hermes_home(args))
    if _wants_json(args):
        _print_json(payload)
    else:
        print("OMJ Hermes model status")
        print(f"  Default: {payload['default_model']['value'] or '(unset)'}")
        print(f"  Disagreements: {len(payload['disagreements'])}")
        print(f"Boundary: {payload['claim_boundary']}")
    return 0


def cmd_providers_model_setup_preview(args: argparse.Namespace) -> int:
    try:
        payload = build_model_setup_preview(
            _selected_hermes_home(args),
            confirm_models=args.confirm_model or (),
            model_aliases=args.model_alias or (),
            expected_digest=args.model_config_digest or "",
        )
    except ValueError as exc:
        raise OmjError(str(exc)) from exc
    if payload["collisions"]:
        raise OmjError("model alias collision in read-only preview")
    if _wants_json(args):
        _print_json(payload)
    else:
        print("OMJ Hermes model setup preview")
        print(f"  Changes: {len(payload['changes'])}")
        print(f"  Config digest: {payload['config']['digest'] or '(unavailable)'}")
        print(f"Boundary: {payload['claim_boundary']}")
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
    inventory = providers_sub.add_parser(
        "model-inventory",
        help="Read selected Hermes model identities and local contract provenance without provider access.",
    )
    inventory.add_argument("--json", action="store_true", help="Print machine-readable model inventory.")
    inventory.set_defaults(func=cmd_providers_model_inventory)

    status = providers_sub.add_parser(
        "model-status",
        help="Read selected Hermes model routing configuration without network or mutation.",
    )
    status.add_argument("--json", action="store_true", help="Print machine-readable model status.")
    status.set_defaults(func=cmd_providers_model_status)

    preview = providers_sub.add_parser(
        "model-setup-preview",
        help="Preview model confirmations and alias metadata without writing Hermes configuration.",
    )
    preview.add_argument("--confirm-model", action="append", default=[], help="Explicitly confirm one exact model id.")
    preview.add_argument("--model-alias", action="append", default=[], metavar="NAME=MODEL", help="Propose one alias change; repeatable.")
    preview.add_argument("--model-config-digest", default="", help="Expected config SHA-256 for drift reporting.")
    preview.add_argument("--json", action="store_true", help="Print machine-readable setup preview.")
    preview.set_defaults(func=cmd_providers_model_setup_preview)


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
