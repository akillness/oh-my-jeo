"""Safe, local transport for OMJ setup profiles.

The transport is deliberately a file format, not a runtime bridge.  It exports
portable routing metadata, removes credentials and machine-local values, and
applies only fields understood by :mod:`omj.profiles.setup`.
"""

from __future__ import annotations

import json
import os
import re
import stat
from pathlib import Path
from typing import Any, Iterable

from ..executors import CODING_EXECUTOR_TARGETS
from ..local_store import (
    atomic_write_json,
    atomic_write_text,
    read_json_object_result,
    utc_now,
)
from ..paths import OmjPaths
from ..system.hashutil import sha256_text
from ..version import __version__
from .setup import (
    PROJECT_MEMORY_MODES,
    SETUP_PROFILE_SCHEMA_VERSION,
    read_setup_profile,
    setup_profile_choices,
    write_setup_profile,
)
from .team import operating_model_ids


SETUP_PROFILE_PACK_SCHEMA_VERSION = "omj_setup_profile_pack/v1"
SETUP_PROFILE_PACK_MANIFEST_SCHEMA_VERSION = "omj_setup_profile_pack_manifest/v1"
SETUP_PROFILE_PACK_MCP_SCHEMA_VERSION = "omj_setup_profile_pack_mcp/v1"
SETUP_PROFILE_PACK_MODEL_ALIASES_SCHEMA_VERSION = (
    "omj_setup_profile_pack_model_aliases/v1"
)
SETUP_PROFILE_PACK_EXPORT_SCHEMA_VERSION = "omj_setup_profile_pack_export/v1"
SETUP_PROFILE_PACK_APPLY_SCHEMA_VERSION = "omj_setup_profile_pack_apply/v1"
SETUP_PROFILE_PACK_SECTIONS = ("profile", "capability_policy", "mcp", "model_aliases")
SETUP_PROFILE_PACK_CLAIM_BOUNDARY = (
    "A setup profile pack records local OMJ routing metadata. It carries no credentials, "
    "moves itself nowhere, and is not execution, review, CI, or merge evidence."
)

WITHHELD_RAW_OR_HIDDEN = "field name carries a raw or hidden payload"
WITHHELD_SENSITIVE_NAME = "field name marks credential material"
WITHHELD_CREDENTIAL = (
    "value is credential-shaped; a pack never carries issued secret material"
)
WITHHELD_MACHINE_LOCAL = (
    "machine-local path or link; it does not resolve on another machine"
)

_MACHINE_LOCAL_LOCATION = re.compile(r"^(?:~|/|[A-Za-z]:[\\/]|\\\\)")
_SCHEMA_GENERATION = re.compile(r"^(?P<name>.+)/v(?P<generation>\d+)$")
_SECRET_VALUE = re.compile(
    r"(?i)(?:^|[^a-z0-9])(?:sk-[a-z0-9_-]{8,}|gh[pousr]_[a-z0-9_-]{8,}|github_pat_[a-z0-9_-]{8,}|xox[baprs]-[a-z0-9-]{8,}|eyj[a-z0-9_-]{8,}|akia[a-z0-9]{8,})"
)
_SENSITIVE_KEY = re.compile(
    r"(?:^|[_-])(api[_-]?key|password|secret|token|credential|authorization|private[_-]?key|refresh[_-]?token)(?:$|[_-])",
    re.IGNORECASE,
)
_RAW_OR_HIDDEN_KEYS = {
    "analysis",
    "chain_of_thought",
    "cot",
    "hidden",
    "hidden_value",
    "raw",
    "raw_prompt",
    "raw_message",
    "raw_transcript",
    "reasoning",
    "transcript",
}
_PROFILE_WRITER_FIELDS = {
    "selected_categories",
    "default_executor",
    "operating_model_id",
    "dispatch_policy",
    "memory_mode",
    "memory_policy",
}
_MAX_PACK_BYTES = 1_000_000
_MAX_PACK_DEPTH = 16
_MAX_COLLECTION_ITEMS = 2_000
_MAX_STRING_LENGTH = 50_000
_DROP = object()


class SetupProfileTransportError(ValueError):
    """Raised when a setup profile pack cannot be safely read or applied."""


# Historical callers used the shorter pack-error name; keep it as a type alias.
SetupProfilePackError = SetupProfileTransportError


# --- Export -----------------------------------------------------------------


def build_setup_profile_pack(paths: OmjPaths) -> dict[str, Any]:
    """Build one redacted, content-addressed local setup-profile pack."""
    try:
        stored = read_setup_profile(paths)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SetupProfilePackError(
            f"cannot read setup profile at {paths.setup_profile_path}: {error}"
        ) from error
    if not isinstance(stored, dict):
        raise SetupProfilePackError(
            "no configured setup profile to export; run `omj setup` first"
        )

    withheld: list[dict[str, str]] = []
    profile = _redact(stored, path="profile", withheld=withheld)
    if not isinstance(profile, dict):
        profile = {}
    sections: dict[str, Any] = {
        "profile": profile,
        "capability_policy": _capability_policy(stored, withheld=withheld),
        "mcp": _mcp_section(paths, stored, withheld=withheld),
        "model_aliases": _model_alias_section(paths, withheld=withheld),
    }
    pack = {
        "schema_version": SETUP_PROFILE_PACK_SCHEMA_VERSION,
        **sections,
        "withheld": sorted(withheld, key=lambda item: item["field"]),
    }
    pack["manifest"] = _manifest(sections, withheld_count=len(withheld))
    return pack


def write_setup_profile_pack(paths: OmjPaths, output_path: Path) -> dict[str, Any]:
    """Build and atomically write a pack without following symlinks or overwriting."""
    pack = build_setup_profile_pack(paths)
    target = Path(output_path).expanduser()
    try:
        _assert_safe_export_target(target)
        atomic_write_text(target, json.dumps(pack, indent=2, sort_keys=True) + "\n")
    except SetupProfilePackError:
        raise
    except OSError as error:
        raise SetupProfilePackError(
            f"cannot write setup profile pack: {error}"
        ) from error
    return pack


def setup_profile_pack_export_report(
    pack: dict[str, Any], *, output_path: str = ""
) -> dict[str, Any]:
    """Return a compact account of one export for CLI or wrapper presentation."""
    manifest = (
        pack.get("manifest", {}) if isinstance(pack.get("manifest"), dict) else {}
    )
    withheld = (
        pack.get("withheld", []) if isinstance(pack.get("withheld"), list) else []
    )
    model_aliases = (
        pack.get("model_aliases", {})
        if isinstance(pack.get("model_aliases"), dict)
        else {}
    )
    mcp = pack.get("mcp", {}) if isinstance(pack.get("mcp"), dict) else {}
    return {
        "schema_version": SETUP_PROFILE_PACK_EXPORT_SCHEMA_VERSION,
        "pack_schema_version": str(pack.get("schema_version", "")),
        "pack_id": str(manifest.get("pack_id", "")),
        "source_omj_version": str(manifest.get("source_omj_version", "")),
        "output_path": str(output_path or ""),
        "sections": list(SETUP_PROFILE_PACK_SECTIONS),
        "configured": configured_field_summary(
            pack.get("profile"), capability_policy=pack.get("capability_policy")
        ),
        "model_alias_status": str(model_aliases.get("status", "")),
        "model_alias_count": len(model_aliases.get("aliases", {}) or {}),
        "mcp_status": str(mcp.get("status", "")),
        "withheld": list(withheld),
        "withheld_field_count": len(withheld),
        "apply_command": "omj setup-profile apply --from <pack.json> --apply",
        "transport_boundary": "Moving this file to another machine is your own file copy; OMJ makes no network calls.",
        "claim_boundary": SETUP_PROFILE_PACK_CLAIM_BOUNDARY,
    }


def _manifest(sections: dict[str, Any], *, withheld_count: int) -> dict[str, Any]:
    digests = {
        name: sha256_text(json.dumps(value, sort_keys=True))
        for name, value in sorted(sections.items())
    }
    return {
        "schema_version": SETUP_PROFILE_PACK_MANIFEST_SCHEMA_VERSION,
        "pack_id": "pack-"
        + sha256_text("".join(digests[name] for name in sorted(digests)))[:12],
        "created_at": utc_now(),
        "source_omj_version": __version__,
        "sections": sorted(sections),
        "section_digests": digests,
        "withheld_field_count": int(withheld_count),
        "claim_boundary": SETUP_PROFILE_PACK_CLAIM_BOUNDARY,
    }


def _withheld_reason(key: str, value: Any) -> str:
    lowered = str(key).casefold()
    if (
        lowered in _RAW_OR_HIDDEN_KEYS
        or lowered.startswith("raw_")
        or lowered.startswith("hidden_")
    ):
        return WITHHELD_RAW_OR_HIDDEN
    if _SENSITIVE_KEY.search(str(key)):
        return WITHHELD_SENSITIVE_NAME
    if isinstance(value, str) and value:
        if _SECRET_VALUE.search(value):
            return WITHHELD_CREDENTIAL
        if _MACHINE_LOCAL_LOCATION.match(value) or "://" in value:
            return WITHHELD_MACHINE_LOCAL
    return ""


def _redact(value: Any, *, path: str, withheld: list[dict[str, str]]) -> Any:
    if isinstance(value, dict):
        kept: dict[str, Any] = {}
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            reason = _withheld_reason(str(key), child)
            if reason:
                withheld.append({"field": child_path, "reason": reason})
                continue
            redacted = _redact(child, path=child_path, withheld=withheld)
            if redacted is not _DROP:
                kept[str(key)] = redacted
        return kept
    if isinstance(value, list):
        kept_items: list[Any] = []
        for index, item in enumerate(value):
            redacted = _redact(item, path=f"{path}[{index}]", withheld=withheld)
            if redacted is not _DROP:
                kept_items.append(redacted)
        return kept_items
    if isinstance(value, str) and value:
        if _SECRET_VALUE.search(value):
            withheld.append({"field": path, "reason": WITHHELD_CREDENTIAL})
            return _DROP
        if _MACHINE_LOCAL_LOCATION.match(value) or "://" in value:
            withheld.append({"field": path, "reason": WITHHELD_MACHINE_LOCAL})
            return _DROP
    return value


def _portable_scalar(field: str, value: Any, *, withheld: list[dict[str, str]]) -> str:
    text = str(value or "")
    reason = _withheld_reason(field, text)
    if reason:
        withheld.append({"field": field, "reason": reason})
        return ""
    return text


def _capability_policy(
    profile: dict[str, Any], *, withheld: list[dict[str, str]]
) -> dict[str, Any]:
    candidate = profile.get("capability_policy")
    if isinstance(candidate, dict):
        redacted = _redact(candidate, path="capability_policy", withheld=withheld)
        if isinstance(redacted, dict):
            redacted.setdefault("schema_version", "omj_capability_policy/v1")
            redacted.setdefault("disabled_families", [])
            return redacted
    return {
        "schema_version": "omj_capability_policy/v1",
        "disabled_families": [],
        "source": "setup_profile/default",
        "claim_boundary": "Capability policy is local routing metadata; it is not proof of execution or host configuration.",
    }


def _mcp_section(
    paths: OmjPaths, profile: dict[str, Any], *, withheld: list[dict[str, str]]
) -> dict[str, Any]:
    empty = {
        "schema_version": SETUP_PROFILE_PACK_MCP_SCHEMA_VERSION,
        "status": "not_configured",
        "host": "",
        "command": "",
        "server_args": [],
        "scope": "",
        "reason": "this machine recorded no MCP host recipe",
    }
    state, error = read_json_object_result(paths.runtime_state_path)
    if error:
        return {
            **empty,
            "status": "unreadable",
            "reason": f"runtime state could not be read: {error}",
        }
    candidates: list[Any] = [profile.get("mcp")]
    if isinstance(state, dict):
        candidates.extend(
            [
                state.get("last_mcp_host_config_install"),
                state.get("mcp_setup"),
                (state.get("last_setup") or {}).get("mcp_setup")
                if isinstance(state.get("last_setup"), dict)
                else None,
            ]
        )
    record = next(
        (
            item
            for item in candidates
            if isinstance(item, dict)
            and (item.get("host") or item.get("requested") or item.get("status"))
        ),
        None,
    )
    if not isinstance(record, dict):
        return empty
    if str(record.get("path", "") or ""):
        withheld.append({"field": "mcp.path", "reason": WITHHELD_MACHINE_LOCAL})
    bridge = record.get("bridge") if isinstance(record.get("bridge"), dict) else {}
    args = record.get("server_args", record.get("args", bridge.get("server_args", [])))
    redacted_args = _redact(
        args if isinstance(args, list) else [],
        path="mcp.server_args",
        withheld=withheld,
    )
    if not isinstance(redacted_args, list):
        redacted_args = []
    host = _portable_scalar(
        "mcp.host", record.get("host", record.get("mcp_host", "")), withheld=withheld
    )
    command = (
        _portable_scalar(
            "mcp.command",
            record.get("command", bridge.get("command", "omj")),
            withheld=withheld,
        )
        or "omj"
    )
    scope = (
        _portable_scalar("mcp.scope", record.get("scope", "user"), withheld=withheld)
        or "user"
    )
    status = (
        "recorded"
        if host
        or bool(record.get("requested"))
        or str(record.get("status", "")) not in {"", "not_requested"}
        else "not_configured"
    )
    return {
        "schema_version": SETUP_PROFILE_PACK_MCP_SCHEMA_VERSION,
        "status": status,
        "host": host,
        "command": command,
        "server_args": redacted_args,
        "scope": scope,
        "reason": ""
        if status == "recorded"
        else str(record.get("reason", empty["reason"])),
    }


def _model_alias_section(
    paths: OmjPaths, *, withheld: list[dict[str, str]]
) -> dict[str, Any]:
    empty = {
        "schema_version": SETUP_PROFILE_PACK_MODEL_ALIASES_SCHEMA_VERSION,
        "status": "no_hermes_config",
        "aliases": {},
        "reason": "no Hermes config on this machine",
    }
    try:
        text = paths.hermes_config_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return empty
    except (OSError, UnicodeDecodeError) as error:
        return {
            **empty,
            "status": "unreadable",
            "reason": f"Hermes config could not be read: {type(error).__name__}",
        }
    aliases = _parse_model_aliases(text)
    safe = _redact(aliases, path="model_aliases.aliases", withheld=withheld)
    if not isinstance(safe, dict):
        safe = {}
    return {
        "schema_version": SETUP_PROFILE_PACK_MODEL_ALIASES_SCHEMA_VERSION,
        "status": "configured" if safe else "unset",
        "aliases": dict(sorted((str(k), str(v)) for k, v in safe.items())),
        "reason": "" if safe else "Hermes config declares no portable model aliases",
    }


def _parse_model_aliases(text: str) -> dict[str, str]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict):
        found = _find_alias_mapping(data)
        if found:
            return found
    aliases: dict[str, str] = {}
    active_indent: int | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if active_indent is None:
            if stripped.rstrip(":").casefold() in {
                "model_aliases",
                "model-aliases",
                "aliases",
            } and stripped.endswith(":"):
                active_indent = indent
            continue
        if indent <= active_indent:
            active_indent = None
            continue
        if ":" not in stripped:
            continue
        key, raw = stripped.split(":", 1)
        key = key.strip().strip("'\"")
        raw = raw.strip().strip("'\"")
        if key and raw and not raw.startswith("{"):
            aliases[key] = raw
    return aliases


def _find_alias_mapping(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).casefold().replace("-", "_") in {
                "model_aliases",
                "modelaliases",
                "aliases",
            } and isinstance(child, dict):
                return {
                    str(k): str(v)
                    for k, v in child.items()
                    if isinstance(k, str) and isinstance(v, (str, int, float))
                }
            found = _find_alias_mapping(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_alias_mapping(child)
            if found:
                return found
    return {}


# --- Version and integrity gates --------------------------------------------


def pack_version_refusal(pack: dict[str, Any]) -> str:
    """Return a refusal explanation, or an empty string when versions are supported."""
    if not isinstance(pack, dict):
        return "setup profile pack must be a JSON object"
    reason = _version_reason(
        str(pack.get("schema_version", "") or ""),
        SETUP_PROFILE_PACK_SCHEMA_VERSION,
        "setup profile pack",
    )
    if reason:
        return reason
    profile = pack.get("profile")
    if not isinstance(profile, dict):
        return "setup profile pack carries no profile section"
    reason = _version_reason(
        str(profile.get("schema_version", "") or ""),
        SETUP_PROFILE_SCHEMA_VERSION,
        "profile section",
    )
    if reason:
        return reason
    manifest = pack.get("manifest")
    if not isinstance(manifest, dict):
        return "setup profile pack carries no manifest"
    return _version_reason(
        str(manifest.get("schema_version", "") or ""),
        SETUP_PROFILE_PACK_MANIFEST_SCHEMA_VERSION,
        "pack manifest",
    )


def _schema_parts(value: str) -> tuple[str, int]:
    match = _SCHEMA_GENERATION.match(value)
    return (
        (match.group("name"), int(match.group("generation"))) if match else (value, -1)
    )


def _version_reason(declared: str, supported: str, label: str) -> str:
    if declared == supported:
        return ""
    if not declared:
        return f"the {label} declares no schema version; OMJ {__version__} applies {supported} only"
    declared_name, declared_generation = _schema_parts(declared)
    supported_name, supported_generation = _schema_parts(supported)
    if declared_name == supported_name and declared_generation > supported_generation:
        return f"the {label} is {declared}, written by a newer OMJ; OMJ {__version__} applies {supported} only -- update OMJ before applying this pack"
    return f"the {label} is {declared}; OMJ {__version__} applies {supported} only"


def read_setup_profile_pack(path: str | Path) -> dict[str, Any]:
    source = Path(path).expanduser()
    if source.is_symlink():
        raise SetupProfilePackError("setup profile pack must not be a symlink")
    flags = os.O_RDONLY | os.O_NONBLOCK
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(source, flags)
    except OSError as error:
        raise SetupProfilePackError(
            f"cannot read setup profile pack: {error}"
        ) from error
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise SetupProfilePackError("setup profile pack must be a regular file")
        if info.st_size > _MAX_PACK_BYTES:
            raise SetupProfilePackError("setup profile pack exceeds the maximum size")
        raw_bytes = os.read(fd, _MAX_PACK_BYTES + 1)
    except OSError as error:
        raise SetupProfilePackError(
            f"cannot read setup profile pack: {error}"
        ) from error
    finally:
        os.close(fd)
    if len(raw_bytes) > _MAX_PACK_BYTES:
        raise SetupProfilePackError("setup profile pack exceeds the maximum size")
    try:
        raw = raw_bytes.decode("utf-8")
        data = json.loads(raw)
    except UnicodeDecodeError as error:
        raise SetupProfilePackError(
            f"cannot read setup profile pack: {error}"
        ) from error
    except json.JSONDecodeError as error:
        raise SetupProfilePackError(
            f"setup profile pack is not valid JSON: {error}"
        ) from error
    if not isinstance(data, dict):
        raise SetupProfilePackError("setup profile pack must be a JSON object")
    _validate_bounds(data)
    return data


def _validate_pack(pack: dict[str, Any]) -> None:
    _validate_bounds(pack)
    refusal = pack_version_refusal(pack)
    if refusal:
        raise SetupProfilePackError(f"{refusal}. Nothing was written.")
    expected_top = {
        "schema_version",
        *SETUP_PROFILE_PACK_SECTIONS,
        "withheld",
        "manifest",
    }
    unknown = sorted(set(pack) - expected_top)
    if unknown:
        raise SetupProfilePackError(
            f"setup profile pack contains unsupported fields: {', '.join(unknown)}. Nothing was written."
        )
    sections = {name: pack.get(name) for name in SETUP_PROFILE_PACK_SECTIONS}
    if any(not isinstance(value, dict) for value in sections.values()):
        raise SetupProfilePackError(
            "setup profile pack sections must be objects. Nothing was written."
        )
    unsafe: list[dict[str, str]] = []
    for name, value in sections.items():
        _redact(value, path=name, withheld=unsafe)
    if unsafe:
        fields = ", ".join(item["field"] for item in unsafe[:5])
        suffix = "..." if len(unsafe) > 5 else ""
        raise SetupProfilePackError(
            f"setup profile pack contains withheld or machine-local values ({fields}{suffix}); refusing import. Nothing was written."
        )
    manifest = pack["manifest"]
    if manifest.get("sections") != sorted(SETUP_PROFILE_PACK_SECTIONS):
        raise SetupProfilePackError(
            "setup profile pack manifest sections do not match the pack. Nothing was written."
        )
    declared_digests = manifest.get("section_digests")
    if not isinstance(declared_digests, dict):
        raise SetupProfilePackError(
            "setup profile pack manifest carries no section digests. Nothing was written."
        )
    actual_digests = {
        name: sha256_text(json.dumps(value, sort_keys=True))
        for name, value in sorted(sections.items())
    }
    if declared_digests != actual_digests:
        raise SetupProfilePackError(
            "setup profile pack section digest mismatch; refusing tampered content. Nothing was written."
        )
    expected_id = (
        "pack-"
        + sha256_text("".join(actual_digests[name] for name in sorted(actual_digests)))[
            :12
        ]
    )
    if manifest.get("pack_id") != expected_id:
        raise SetupProfilePackError(
            "setup profile pack manifest pack_id mismatch; refusing tampered content. Nothing was written."
        )
    withheld = pack.get("withheld")
    if not isinstance(withheld, list) or any(
        not isinstance(row, dict) or not row.get("field") or not row.get("reason")
        for row in withheld
    ):
        raise SetupProfilePackError(
            "setup profile pack withheld entries are malformed. Nothing was written."
        )
    if manifest.get("withheld_field_count") != len(withheld):
        raise SetupProfilePackError(
            "setup profile pack withheld count mismatch; refusing tampered content. Nothing was written."
        )


def _validate_bounds(value: Any, *, depth: int = 0, path: str = "pack") -> None:
    if depth > _MAX_PACK_DEPTH:
        raise SetupProfilePackError(f"{path} exceeds the maximum pack nesting depth")
    if isinstance(value, dict):
        if len(value) > _MAX_COLLECTION_ITEMS:
            raise SetupProfilePackError(f"{path} contains too many fields")
        for key, child in value.items():
            if not isinstance(key, str) or len(key) > 200:
                raise SetupProfilePackError(f"{path} contains an invalid field name")
            _validate_bounds(child, depth=depth + 1, path=f"{path}.{key}")
    elif isinstance(value, list):
        if len(value) > _MAX_COLLECTION_ITEMS:
            raise SetupProfilePackError(f"{path} contains too many entries")
        for index, child in enumerate(value):
            _validate_bounds(child, depth=depth + 1, path=f"{path}[{index}]")
    elif isinstance(value, str) and len(value) > _MAX_STRING_LENGTH:
        raise SetupProfilePackError(f"{path} contains an oversized string")
    try:
        if depth == 0 and len(json.dumps(value, sort_keys=True)) > _MAX_PACK_BYTES:
            raise SetupProfilePackError("setup profile pack exceeds the maximum size")
    except (TypeError, ValueError) as error:
        raise SetupProfilePackError(
            f"setup profile pack contains unsupported JSON values: {error}"
        ) from error


# --- Apply ------------------------------------------------------------------


def apply_setup_profile_pack(
    paths: OmjPaths,
    pack: dict[str, Any],
    *,
    dry_run: bool = True,
    with_mcp: bool = False,
    mcp_config_path: str | Path | None = None,
) -> dict[str, Any]:
    """Validate a pack, then apply supported fields through the setup writer.

    No Hermes config or host configuration is written.  MCP and model aliases
    remain explicit handoff rows because those belong to the host's own config
    surface, not OMJ's setup-profile writer.
    """
    _validate_pack(pack)
    profile = pack["profile"]
    status = "would_apply" if dry_run else "applied"
    existing = read_setup_profile(paths)
    existing = existing if isinstance(existing, dict) else None
    fields: list[dict[str, Any]] = []

    executor, executor_reason = _accepted_value(
        "default_executor", profile.get("default_executor"), CODING_EXECUTOR_TARGETS
    )
    operating_model, operating_model_reason = _accepted_value(
        "operating_model_id", profile.get("operating_model_id"), operating_model_ids()
    )
    memory_mode, memory_mode_reason = _accepted_value(
        "memory_mode", profile.get("memory_mode"), PROJECT_MEMORY_MODES
    )
    categories, category_reason = _accepted_categories(
        profile.get("selected_categories")
    )
    disabled, family_reason = _accepted_families(pack.get("capability_policy"))
    for field, value, reason in (
        ("default_executor", executor, executor_reason),
        ("operating_model_id", operating_model, operating_model_reason),
        ("memory_mode", memory_mode, memory_mode_reason),
        ("selected_categories", list(categories), category_reason),
        ("capability_policy.disabled_families", list(disabled), family_reason),
    ):
        fields.append(_field_row(field, value, reason, status=status))

    mcp = pack.get("mcp", {})
    aliases = pack.get("model_aliases", {})
    fields.append(
        _external_field_row(
            "model_aliases",
            aliases,
            "Hermes model aliases require an explicit host-config digest and are not written by OMJ setup-profile apply",
        )
    )
    fields.append(
        _external_field_row(
            "mcp.host_config",
            mcp,
            "MCP host configuration belongs to the host; OMJ setup-profile apply never overwrites it",
        )
    )
    if with_mcp and mcp_config_path:
        fields[-1]["reason"] = (
            "MCP host configuration remains source-bound; inspect the recipe and merge it in the host config explicitly"
        )

    accepted_any = bool(
        executor_reason == ""
        or operating_model_reason == ""
        or memory_mode_reason == ""
        or category_reason == ""
        or family_reason == ""
    )
    profile_after: dict[str, Any] | None = None
    if not dry_run and accepted_any:
        _assert_owned_profile_path(paths.setup_profile_path, paths.omj_home)
        categories_to_write = (
            list(categories)
            if not category_reason
            else _string_list((existing or {}).get("selected_categories")) or None
        )
        executor_to_write = (
            executor
            if not executor_reason
            else str((existing or {}).get("default_executor", "")) or None
        )
        operating_model_to_write = (
            operating_model
            if not operating_model_reason
            else str((existing or {}).get("operating_model_id", "")) or None
        )
        memory_mode_to_write = (
            memory_mode
            if not memory_mode_reason
            else str((existing or {}).get("memory_mode", "")) or None
        )
        try:
            written = write_setup_profile(
                paths,
                categories_to_write,
                default_executor=executor_to_write,
                operating_model=operating_model_to_write,
                memory_mode=memory_mode_to_write,
            )
        except (OSError, ValueError, json.JSONDecodeError) as error:
            raise SetupProfilePackError(
                f"setup profile writer refused the pack: {error}. Nothing was written."
            ) from error
        preserved = {
            key: value
            for key, value in (existing or {}).items()
            if key not in written and key not in _PROFILE_WRITER_FIELDS
        }
        written.update(preserved)
        if not family_reason:
            policy = dict(pack.get("capability_policy", {}))
            policy["disabled_families"] = list(disabled)
            written["capability_policy"] = policy
        # The setup writer already performed one atomic write.  This second
        # atomic write only restores opaque, unrelated local profile fields.
        if preserved or not family_reason:
            atomic_write_json(paths.setup_profile_path, written, private=True)
        profile_after = read_setup_profile(paths)
    else:
        profile_after = existing

    return {
        "schema_version": SETUP_PROFILE_PACK_APPLY_SCHEMA_VERSION,
        "applied": bool(not dry_run and accepted_any),
        "dry_run": bool(dry_run),
        "pack_id": str(pack.get("manifest", {}).get("pack_id", "")),
        "pack_schema_version": str(pack.get("schema_version", "")),
        "source_omj_version": str(
            pack.get("manifest", {}).get("source_omj_version", "")
        ),
        "target_omj_version": __version__,
        "fields": fields,
        "applied_fields": [
            row["field"] for row in fields if row["status"] != "not_applied"
        ],
        "not_applied_fields": [
            row["field"] for row in fields if row["status"] == "not_applied"
        ],
        "profile_after": profile_after,
        "configured_in_pack": configured_field_summary(
            profile, capability_policy=pack.get("capability_policy")
        ),
        "configured_after": configured_field_summary(profile_after),
        "setup_profile_path": str(paths.setup_profile_path),
        "withheld": list(pack.get("withheld", [])),
        "next_actions": [
            "Review model_aliases locally and apply them through the Hermes host's own digest-bound configuration flow.",
            "Review the MCP recipe locally and merge it into the host config without replacing unrelated entries.",
        ],
        "claim_boundary": "Applying a setup profile pack records local OMJ routing defaults only; it does not prove Hermes used a skill or any executor ran.",
    }


def _accepted_value(field: str, value: Any, allowed: Iterable[str]) -> tuple[str, str]:
    text = str(value or "").strip()
    allowed_values = tuple(str(item) for item in allowed)
    if not text:
        return "", f"the pack carries no {field}"
    if text not in allowed_values:
        return (
            "",
            f"this OMJ does not accept {field} {text!r}; it accepts {', '.join(allowed_values)}",
        )
    return text, ""


def _accepted_categories(value: Any) -> tuple[tuple[str, ...], str]:
    valid = {str(choice["id"]) for choice in setup_profile_choices()}
    if not isinstance(value, list) or not value:
        return (), "the pack carries no selected_categories"
    accepted = tuple(str(item) for item in value if str(item) in valid)
    rejected = tuple(str(item) for item in value if str(item) not in valid)
    if rejected:
        return (
            accepted,
            f"this OMJ does not accept setup profile category {', '.join(repr(item) for item in rejected)}",
        )
    return accepted, ""


def _accepted_families(policy: Any) -> tuple[tuple[str, ...], str]:
    if not isinstance(policy, dict):
        return (), "the pack carries no capability policy"
    declared = policy.get("disabled_families")
    if not isinstance(declared, list):
        return (), "the pack's capability policy declares no disabled_families list"
    accepted: list[str] = []
    rejected: list[str] = []
    for item in declared:
        text = str(item).strip()
        if not text or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", text):
            rejected.append(str(item))
        else:
            accepted.append(text)
    if rejected:
        return (
            tuple(sorted(set(accepted))),
            f"this OMJ does not accept capability family {', '.join(repr(item) for item in rejected)}",
        )
    return tuple(sorted(set(accepted))), ""


def configured_field_summary(
    profile: dict[str, Any] | None, *, capability_policy: Any = None
) -> dict[str, Any]:
    source = profile if isinstance(profile, dict) else {}
    policy = (
        capability_policy
        if isinstance(capability_policy, dict)
        else source.get("capability_policy")
    )
    disabled = policy.get("disabled_families") if isinstance(policy, dict) else []
    return {
        "default_executor": str(source.get("default_executor", "")),
        "operating_model_id": str(source.get("operating_model_id", "")),
        "memory_mode": str(source.get("memory_mode", "")),
        "selected_categories": _string_list(source.get("selected_categories")),
        "disabled_families": _string_list(disabled),
    }


def _field_row(field: str, value: Any, reason: str, *, status: str) -> dict[str, Any]:
    return {
        "field": field,
        "status": "not_applied" if reason else status,
        "value": value,
        "reason": reason,
    }


def _external_field_row(field: str, value: Any, reason: str) -> dict[str, Any]:
    return {"field": field, "status": "not_applied", "value": value, "reason": reason}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes, dict)):
        return []
    return [str(item) for item in value]


def _assert_safe_export_target(target: Path) -> None:
    if target.is_symlink():
        raise SetupProfilePackError(
            f"refusing to write through symlinked export path: {target}"
        )
    absolute_parent = target.parent.absolute()
    resolved_parent = target.parent.resolve()
    if resolved_parent != absolute_parent and not _is_macos_system_alias(
        absolute_parent, resolved_parent
    ):
        raise SetupProfilePackError(
            f"refusing symlinked export directory: {target.parent}"
        )
    if target.exists():
        raise SetupProfilePackError(
            f"refusing to overwrite existing export path: {target}"
        )


def _is_macos_system_alias(absolute: Path, resolved: Path) -> bool:
    """Allow /var and /tmp's documented macOS private aliases only."""
    parts = absolute.parts
    resolved_parts = resolved.parts
    return (
        len(parts) > 2
        and len(resolved_parts) > 3
        and parts[0] == resolved_parts[0] == "/"
        and parts[1] in {"var", "tmp"}
        and resolved_parts[1:3] == ("private", parts[1])
    )


def _assert_owned_profile_path(target: Path, root: Path) -> None:
    # Resolve the destination to detect a symlink escape, while allowing
    # ordinary system aliases such as macOS /var -> /private/var.
    if root.expanduser().is_symlink():
        raise SetupProfilePackError(f"refusing symlinked OMJ home: {root}")
    if target.parent.is_symlink():
        raise SetupProfilePackError(
            f"refusing symlinked setup-profile directory: {target.parent}"
        )
    try:
        target.parent.resolve().relative_to(root.resolve())
    except ValueError as error:
        raise SetupProfilePackError(
            f"refusing profile write outside owned OMJ home: {target}"
        ) from error
    if target.is_symlink():
        raise SetupProfilePackError(
            f"refusing to overwrite symlinked setup profile: {target}"
        )
    if target.exists() and target.is_dir():
        raise SetupProfilePackError(f"setup profile path is a directory: {target}")
