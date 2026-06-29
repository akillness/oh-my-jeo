from __future__ import annotations

import argparse

from ..catalogs.provider_auth import (
    diagnose_provider_auth,
    get_provider_auth,
    list_provider_auth,
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
