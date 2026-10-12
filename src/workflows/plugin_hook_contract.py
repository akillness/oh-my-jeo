"""Bounded static hook semantics for a Hermes-compatible plugin manifest."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Final, Literal

PLUGIN_HOOK_CONTRACT_HOST: Final = "hermes"
PLUGIN_HOOK_CONTRACT_RANGE: Final = ">=0.21.1,<0.22.0"
PLUGIN_HOOK_CONTRACT_VERSION: Final = "0.21.1"
PLUGIN_HOOK_CONTRACT_SOURCE: Final = "hermes-agent v2026.9.7"
MANIFEST_FILENAME: Final = "plugin.yaml"
CANONICAL_HOOK_FIELD: Final = "provides_hooks"
SECONDARY_HOOK_FIELD: Final = "hooks"
HERMES_RANGE_FIELD: Final = "requires_hermes"
MAX_DECLARED_HOOKS: Final = 64
MAX_DECLARED_RANGE_CHARS: Final = 64
MAX_HOST_VERSION_CHARS: Final = 32

HookEffect = Literal[
    "lifecycle_callback",
    "observer",
    "policy_gate",
    "prompt_context_contributor",
    "result_transformer",
    "unknown",
]
HookHostContract = Literal["bounded", "caller_thread", "queued_worker", "unknown"]
HookTimeoutSemantics = Literal["fail_closed", "fail_open", "not_applicable", "unknown"]
HostVersionStatus = Literal["compatible", "incompatible", "not_observed", "unreadable"]
HostVersionMethod = Literal["installation_version_module", "not_supplied", "operator_declared"]
RangeStatus = Literal["supported", "undeclared", "unparsable", "unsupported"]


class PluginHookDeclarationError(ValueError):
    """The manifest hook declaration is outside the bounded readable shape."""


class PluginManifestFormatError(ValueError):
    """The manifest is outside the intentionally small YAML subset."""


@dataclass(frozen=True, slots=True)
class HookContract:
    effect: HookEffect
    host_contract: HookHostContract
    timeout_semantics: HookTimeoutSemantics


@dataclass(frozen=True, slots=True)
class DeclaredHook:
    name: str
    field: str
    contract: HookContract


@dataclass(frozen=True, slots=True)
class HostVersionObservation:
    version: str | None
    method: HostVersionMethod
    status: HostVersionStatus


@dataclass(frozen=True, slots=True)
class HookDeclaration:
    hooks: tuple[DeclaredHook, ...]
    declared_range: str | None
    range_status: RangeStatus


NO_HOST_VERSION_OBSERVED: Final = HostVersionObservation(None, "not_supplied", "not_observed")
HOST_VERSION_HOLD_STATUSES: Final[frozenset[str]] = frozenset({"incompatible", "unreadable"})
_UNKNOWN = HookContract("unknown", "unknown", "unknown")
_HOOK_NAME = re.compile(r"[a-z][a-z0-9_]{0,63}")

HERMES_HOOK_CONTRACTS: Final[dict[str, HookContract]] = {
    "pre_tool_call": HookContract("policy_gate", "bounded", "fail_closed"),
    "pre_llm_call": HookContract("prompt_context_contributor", "bounded", "fail_open"),
    "on_session_start": HookContract("lifecycle_callback", "bounded", "fail_open"),
    "on_session_end": HookContract("lifecycle_callback", "bounded", "fail_open"),
    "on_stream_start": HookContract("observer", "queued_worker", "not_applicable"),
    "on_stream_delta": HookContract("observer", "queued_worker", "not_applicable"),
    "on_stream_end": HookContract("observer", "queued_worker", "not_applicable"),
    "post_tool_call": HookContract("observer", "bounded", "fail_open"),
    "post_llm_call": HookContract("observer", "bounded", "fail_open"),
    "pre_api_request": HookContract("observer", "bounded", "fail_open"),
    "post_api_request": HookContract("observer", "bounded", "fail_open"),
    "api_request_error": HookContract("observer", "bounded", "fail_open"),
    "transform_tool_result": HookContract("result_transformer", "bounded", "fail_open"),
    "transform_terminal_output": HookContract("result_transformer", "bounded", "fail_open"),
    "transform_llm_output": HookContract("result_transformer", "bounded", "fail_open"),
}


def hook_contract(name: str, *, range_status: RangeStatus = "supported") -> HookContract:
    if range_status in ("unparsable", "unsupported"):
        return _UNKNOWN
    return HERMES_HOOK_CONTRACTS.get(name, _UNKNOWN)


def observe_host_version(
    *, declared_version: str | None = None, install_dir: Path | None = None
) -> HostVersionObservation:
    if declared_version is not None and install_dir is not None:
        raise ValueError("inspect a Hermes version from a declared version or an installation, not both")
    if declared_version is None and install_dir is None:
        return NO_HOST_VERSION_OBSERVED
    if declared_version is not None:
        return _host_version_observation(declared_version, "operator_declared")
    try:
        text = (Path(install_dir) / "hermes_agent" / "version.py").read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return HostVersionObservation(None, "installation_version_module", "unreadable")
    match = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", text)
    return _host_version_observation(match.group(1) if match else "", "installation_version_module")


def _host_version_observation(version: str, method: HostVersionMethod) -> HostVersionObservation:
    if len(version) > MAX_HOST_VERSION_CHARS or not version:
        return HostVersionObservation(None, method, "unreadable")
    if re.fullmatch(r"\d+\.\d+\.\d+", version) is None:
        return HostVersionObservation(None, method, "unreadable")
    major, minor, patch = (int(part) for part in version.split("."))
    compatible = (major, minor, patch) >= (0, 21, 1) and (major, minor) == (0, 21)
    return HostVersionObservation(version, method, "compatible" if compatible else "incompatible")


def host_range_status(declared_range: str | None) -> RangeStatus:
    if declared_range is None:
        return "undeclared"
    if len(declared_range) > MAX_DECLARED_RANGE_CHARS:
        return "unparsable"
    value = declared_range.replace(" ", "")
    if not re.fullmatch(r">=\d+\.\d+\.\d+,<\d+\.\d+\.\d+", value):
        return "unparsable"
    return "supported" if _version_satisfies(PLUGIN_HOOK_CONTRACT_VERSION, value) else "unsupported"


def read_hook_declaration(manifest_text: str) -> HookDeclaration:
    entries = _read_manifest_entries(manifest_text)
    declared_range = entries.get(HERMES_RANGE_FIELD)
    range_status = host_range_status(declared_range)
    names: dict[str, str] = {}
    for field in (SECONDARY_HOOK_FIELD, CANONICAL_HOOK_FIELD):
        values = entries.get(field)
        if values is None:
            continue
        if not isinstance(values, list):
            raise PluginHookDeclarationError(f"{field} must be a bounded list of hook names")
        if len(values) > MAX_DECLARED_HOOKS:
            raise PluginHookDeclarationError(f"{field} declares at most {MAX_DECLARED_HOOKS} hook names")
        seen: set[str] = set()
        for name in values:
            if not isinstance(name, str) or _HOOK_NAME.fullmatch(name) is None or name in seen:
                raise PluginHookDeclarationError(f"{field} entries must be plain unique hook names")
            seen.add(name)
            names[name] = field
    hooks = tuple(
        DeclaredHook(name, field, hook_contract(name, range_status=range_status))
        for name, field in sorted(names.items())
    )
    return HookDeclaration(hooks, declared_range, range_status)


def _read_manifest_entries(text: str) -> dict[str, object]:
    if not isinstance(text, str):
        raise PluginManifestFormatError("plugin manifest must be text")
    lines = text.splitlines()
    if len(lines) > 512 or any(len(line) > 4096 for line in lines):
        raise PluginManifestFormatError("plugin manifest exceeds bounded read limits")
    result: dict[str, object] = {}
    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        if raw[:1].isspace():
            raise PluginManifestFormatError("plugin manifest has an unexpected indentation")
        if ":" not in raw:
            raise PluginManifestFormatError("plugin manifest contains an unreadable entry")
        key, rest_raw = raw.split(":", 1)
        if rest_raw and not rest_raw[:1].isspace():
            raise PluginManifestFormatError("plugin manifest contains an unreadable entry")
        raw_key = key
        key = key.strip()
        rest = rest_raw.strip()
        if raw_key != key or any(character.isspace() for character in key) or not re.fullmatch(r"[A-Za-z0-9_.-]+", key) or key in result:
            raise PluginManifestFormatError("plugin manifest repeats or omits a key")
        if rest:
            if rest.startswith(("[", "{", "|", ">", "&", "*")):
                raise PluginManifestFormatError("plugin manifest uses an unsupported value shape")
            result[key] = rest.strip("'\"")
            index += 1
            continue

        values: list[str] = []
        cursor = index + 1
        nested = False
        scalar_indent: int | None = None
        while cursor < len(lines):
            child = lines[cursor]
            if not child.strip() or child.lstrip().startswith("#"):
                cursor += 1
                continue
            indent = len(child) - len(child.lstrip())
            if scalar_indent is not None:
                if indent > scalar_indent:
                    cursor += 1
                    continue
                scalar_indent = None
            item = child.strip()
            if not child[:1].isspace() and not item.startswith("-"):
                break
            if item.startswith("-"):
                if len(item) > 1 and not item[1].isspace():
                    raise PluginManifestFormatError("plugin manifest sequence is unreadable")
                value = item[1:].strip()
                if not value or value.startswith(("[", "{", "&", "*")):
                    raise PluginManifestFormatError("plugin manifest sequence item is unreadable")
                values.append(value.strip("'\""))
                cursor += 1
                continue
            nested = True
            if re.search(r"(?:^|[\s:])[&*][A-Za-z0-9_-]+", child):
                raise PluginManifestFormatError("plugin manifest uses an unsupported anchor or alias")
            if ":" in item and item.rsplit(":", 1)[1].strip() in {"|", ">"}:
                scalar_indent = indent
            cursor += 1
        result[key] = None if nested else values
        index = cursor
    return result


def _version_satisfies(version: str, declared: str) -> bool:
    match = re.fullmatch(r">=(\d+)\.(\d+)\.(\d+),<(\d+)\.(\d+)\.(\d+)", declared)
    if not match:
        return False
    current = tuple(int(value) for value in version.split("."))
    lower = tuple(int(value) for value in match.groups()[:3])
    upper = tuple(int(value) for value in match.groups()[3:])
    return lower <= current < upper
