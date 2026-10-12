"""Bounded, offline static risk audit for one local Hermes plugin tree."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
from typing import Any, Final, Literal, TypeAlias

from .plugin_hook_contract import (
    CANONICAL_HOOK_FIELD,
    HOST_VERSION_HOLD_STATUSES,
    MANIFEST_FILENAME,
    NO_HOST_VERSION_OBSERVED,
    PLUGIN_HOOK_CONTRACT_HOST,
    PLUGIN_HOOK_CONTRACT_RANGE,
    PLUGIN_HOOK_CONTRACT_SOURCE,
    SECONDARY_HOOK_FIELD,
    HostVersionObservation,
    PluginHookDeclarationError,
    PluginManifestFormatError,
    read_hook_declaration,
)

PLUGIN_RISK_AUDIT_SCHEMA_VERSION: Final = "plugin_risk_audit/v1"
MAX_PLUGIN_AUDIT_DEPTH: Final = 8
MAX_PLUGIN_AUDIT_DIRECTORIES: Final = 128
MAX_PLUGIN_AUDIT_FILES: Final = 128
MAX_PLUGIN_AUDIT_DIRECTORY_ENTRIES: Final = 128
MAX_PLUGIN_AUDIT_FILE_BYTES: Final = 131_072
_IGNORED_DIRECTORIES: Final = frozenset({".git", ".venv", "__pycache__", "node_modules"})
_AUDITED_FILENAMES: Final = frozenset({".env", "plugin.json", "plugin.yaml", "pyproject.toml", "requirements.txt", "setup.cfg", "setup.py"})
_AUDITED_SUFFIXES: Final = frozenset({".cjs", ".cts", ".js", ".json", ".mjs", ".mts", ".py", ".toml", ".ts", ".txt", ".yaml", ".yml"})

_HOOK_CAPABILITY = re.compile(r"\b(?:on_session_end|pre_llm_call|pre_tool_call)\b")
_PROCESS_EXECUTION = re.compile(
    r"\b(?:os\.system|subprocess\.(?:call|check_call|check_output|Popen|run)|child_process\.(?:exec|execFile|fork|spawn))\s*\("
)
_DYNAMIC_EXECUTION = re.compile(r"(?<!\.)\b(?:compile|eval|exec)\s*\(|\bnew\s+Function\s*\(")
_NETWORK_REQUEST = re.compile(
    r"\b(?:axios|httpx|requests|urllib(?:\.request|3)?|https?|http)\.(?:get|post|put|request|urlopen)\s*\(|\bfetch\s*\("
)
_SECRET_ASSIGNMENT = re.compile(
    r"\b(?:api[_-]?key|password|private[_-]?key|secret|token)\b\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
    re.IGNORECASE,
)
_DEPENDENCY_DECLARATION = re.compile(r"(?:^\s*dependencies\s*=|^\s*[A-Za-z0-9_.-]+\s*(?:[<>=!~]|$))", re.MULTILINE)
_PACKAGE_DEPENDENCY_FIELDS: Final = frozenset({"dependencies", "optionalDependencies", "peerDependencies"})
_REPLACEMENT_WRITE_CALL = re.compile(
    r"\b(?:os\.(?:rename|replace)|shutil\.(?:copy|copy2|copyfile|copytree|move)"
    r"|fs\.(?:promises\.)?(?:copyFile|cp|rename|writeFile)(?:Sync)?)\s*\("
    r"|\.write_(?:bytes|text)\s*\("
    r"|\bopen\s*\([^\n)]{0,200},\s*['\"][rbt+]*[wax][rwaxbt+]*['\"]"
)
_REPLACEMENT_TARGET = re.compile(
    r"['\"][^'\"\n]{0,200}\.(?:cjs|cts|dll|dylib|exe|js|mjs|mts|node|py|pyc|pyz|so|ts)['\"]"
    r"|['\"](?:package\.json|plugin\.json|plugin\.ya?ml|pyproject\.toml|requirements\.txt)['\"]"
)
_ARCHIVE_EXTRACTION = re.compile(r"\bshutil\.unpack_archive\s*\(|\.extractall\s*\(")
_SELF_UPDATE_COMMAND = re.compile(
    r"\bpip[0-9.]*\b[^\n]{0,60}\binstall\b[^\n]{0,60}(?:--upgrade|--force-reinstall)\b"
    r"|\bnpm\b[^\n]{0,60}\b(?:install|update)\b[^\n]{0,60}(?:--global|-g)\b"
    r"|\bgit\b[^\n]{0,20}\bpull\b"
    r"|\bhermes\b[^\n]{0,30}\bplugins?\b[^\n]{0,30}\b(?:install|update|upgrade)\b"
)
_INTEGRITY_VERIFICATION = re.compile(
    r"\bhashlib\.(?:blake2b|sha256|sha384|sha512)\s*\(|\bhmac\.compare_digest\s*\("
    r"|\bcrypto\.create(?:Hash|Verify)\s*\(|\b(?:cosign|gpg|gpgv|minisign)\b[^\n]{0,40}--verify\b"
)

JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
ManifestStatus: TypeAlias = Literal["invalid_json", "missing", "present"]
RiskCategory: TypeAlias = Literal[
    "declared_dependency",
    "dynamic_code_execution",
    "hermes_hook_capability",
    "network_request",
    "potential_committed_secret",
    "process_execution",
    "self_update_or_code_replacement",
    "undetermined_hook_contract",
    "undetermined_self_update_path",
]
SelfUpdateSignal: TypeAlias = Literal[
    "archive_extraction",
    "code_replacement_write",
    "host_update_command",
    "integrity_verification",
    "remote_retrieval",
]
SelfUpdateClassification: TypeAlias = Literal["detected", "needs_review", "not_detected"]
MITIGATING_SELF_UPDATE_SIGNALS: Final[frozenset[str]] = frozenset({"integrity_verification"})
SELF_UPDATE_COMPOSITIONS: Final[tuple[tuple[str, frozenset[str]], ...]] = (
    ("remote_retrieval_and_code_replacement", frozenset({"remote_retrieval", "code_replacement_write"})),
    ("remote_retrieval_and_archive_extraction", frozenset({"remote_retrieval", "archive_extraction"})),
    ("host_managed_update_bypass", frozenset({"host_update_command"})),
)


@dataclass(frozen=True, slots=True)
class _Source:
    name: str
    content: bytes
    is_root_file: bool
    manifest_status: ManifestStatus | None
    risk_categories: frozenset[str]
    self_update_signals: frozenset[str]


@dataclass(frozen=True, slots=True)
class _Undecodable:
    pass


_UNDECODABLE = _Undecodable()


def audit_plugin_risk(
    plugin_root: Path, *, host_version: HostVersionObservation = NO_HOST_VERSION_OBSERVED
) -> JsonObject:
    root = _resolve_root(plugin_root)
    raw_sources = _read_sources(root)
    sources = tuple(_audit_source(source) for source in raw_sources)
    manifest_text = _root_manifest_text(raw_sources)
    manifest_status, declared_hooks = _declared_hook_report(manifest_text, host_version)
    self_update = _self_update_report(sources)
    categories = sorted(
        {category for source in sources for category in source.risk_categories}
        | _hook_categories(declared_hooks)
        | _self_update_categories(str(self_update["classification"]))
    )
    return {
        "schema_version": PLUGIN_RISK_AUDIT_SCHEMA_VERSION,
        "source": {
            "explicit_root": True,
            "manifest_status": _manifest_status(sources),
            "manifest_yaml_status": manifest_status,
            "scanned_file_count": len(sources),
            "scanned_byte_count": sum(len(source.content) for source in sources),
            "dropped_file_count": 0,
            "unknown_file_count": 0,
        },
        "summary": {
            "scanned_file_count": len(sources),
            "scanned_byte_count": sum(len(source.content) for source in sources),
            "risk_categories": categories,
            "risk_category_count": len(categories),
        },
        "declared_hooks": declared_hooks,
        "self_update": self_update,
        "not_observed": {
            key: {"status": "not_observed"}
            for key in (
                "plugin_import", "plugin_registration", "plugin_execution", "plugin_hook_registration",
                "plugin_hook_execution", "plugin_hook_timeout_enforcement", "plugin_hook_failure_handling",
                "plugin_code_replacement", "plugin_self_update_execution", "hermes_host_execution",
                "hermes_plugin_admission", "dependency_installation", "network_access", "ci_annotation_publication",
            )
        },
        "claim_boundary": (
            "The audit statically reads bounded text from one explicitly named local plugin directory and returns "
            "aggregate risk categories plus declared hook semantics. A declared hook is static metadata, not evidence "
            "that it registered, ran, stayed within budget, or handled failures. An absent declaration is not evidence "
            "that the plugin has no hooks, and a declared hook is not evidence that the hook registered or executed. "
            "The audit does not import or execute plugin code, register a plugin, install dependencies, access a network, "
            "or prove the plugin safe. Self-update is a composition of static signals, never evidence that retrieval or "
            "replacement happened; integrity checks are mitigation only and not evidence that any checksum or signature "
            "was valid. A compatible host mapping is not host admission or execution evidence."
        ),
    }


def scanned_text_risk_categories(name: str, text: str) -> tuple[RiskCategory, ...]:
    categories = _risk_categories(name, text)
    signals = _self_update_signals(text, categories) - MITIGATING_SELF_UPDATE_SIGNALS
    classification = _self_update_classification(_matched_composition(signals), signals, "dynamic_code_execution" in categories)
    return tuple(sorted(categories | _self_update_categories(classification)))


def _resolve_root(plugin_root: Path) -> Path:
    provided = Path(os.path.abspath(Path(plugin_root).expanduser()))
    if provided == Path(provided.anchor):
        raise ValueError("plugin audit root must not be the filesystem root")
    for parent in provided.parents:
        if parent in {Path("/var"), Path("/tmp")}:
            continue
        if parent.is_symlink():
            raise ValueError("plugin audit root must not traverse a symlink")
    if provided.is_symlink():
        raise ValueError("plugin audit root must not traverse a symlink")
    if not provided.is_dir():
        raise ValueError("plugin audit root must be a real directory")
    return provided.resolve(strict=True)


def _read_sources(root: Path) -> tuple[_Source, ...]:
    files: list[tuple[Path, bool]] = []
    directories = 0
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        depth = len(current_path.relative_to(root).parts)
        if depth > MAX_PLUGIN_AUDIT_DEPTH:
            raise ValueError("plugin audit tree exceeds maximum depth")
        directories += 1
        if directories > MAX_PLUGIN_AUDIT_DIRECTORIES:
            raise ValueError("plugin audit tree exceeds directory bound")
        entries = list(current_path.iterdir())
        if len(entries) > MAX_PLUGIN_AUDIT_DIRECTORY_ENTRIES:
            raise ValueError("plugin audit directory must contain at most 128 entries")
        for entry in entries:
            if entry.is_symlink():
                raise ValueError("plugin audit refuses symlink entries")
        dirnames[:] = sorted(name for name in dirnames if name not in _IGNORED_DIRECTORIES)
        for filename in sorted(filenames):
            candidate = current_path / filename
            if _is_audited_file(filename):
                files.append((candidate, depth == 0))
                if len(files) > MAX_PLUGIN_AUDIT_FILES:
                    raise ValueError("plugin audit tree exceeds file bound")
    sources: list[_Source] = []
    for path, is_root_file in files:
        try:
            if not path.is_file():
                raise ValueError(f"plugin audit file {path.name} is not a regular file")
            size = path.stat().st_size
            if size > MAX_PLUGIN_AUDIT_FILE_BYTES:
                raise ValueError(f"plugin audit file {path.name} exceeds bounded size")
            content = path.read_bytes()
        except OSError as exc:
            raise ValueError(f"plugin audit could not read {path.name}") from exc
        sources.append(_Source(path.name, content, is_root_file, None, frozenset(), frozenset()))
    return tuple(sources)


def _is_audited_file(name: str) -> bool:
    return name in _AUDITED_FILENAMES or Path(name).suffix.lower() in _AUDITED_SUFFIXES


def _audit_source(source: _Source) -> _Source:
    text = source.content.decode("utf-8", errors="replace")
    categories = _risk_categories(source.name, text)
    return _Source(
        source.name,
        source.content,
        source.is_root_file,
        _source_manifest_status(source.name, source.is_root_file, text),
        categories,
        _self_update_signals(text, categories),
    )


def _risk_categories(name: str, text: str) -> frozenset[str]:
    categories: set[str] = set()
    if _declares_dependencies(name, text):
        categories.add("declared_dependency")
    if _HOOK_CAPABILITY.search(text):
        categories.add("hermes_hook_capability")
    if _PROCESS_EXECUTION.search(text):
        categories.add("process_execution")
    if _DYNAMIC_EXECUTION.search(text):
        categories.add("dynamic_code_execution")
    if _NETWORK_REQUEST.search(text):
        categories.add("network_request")
    if _SECRET_ASSIGNMENT.search(text):
        categories.add("potential_committed_secret")
    return frozenset(categories)


def _declares_dependencies(name: str, text: str) -> bool:
    if name in {"pyproject.toml", "requirements.txt", "setup.cfg", "setup.py"}:
        return _DEPENDENCY_DECLARATION.search(text) is not None
    if name != "package.json":
        return False
    try:
        package = json.loads(text)
    except json.JSONDecodeError:
        return False
    return isinstance(package, dict) and any(isinstance(package.get(field), dict) and package[field] for field in _PACKAGE_DEPENDENCY_FIELDS)


def _source_manifest_status(name: str, is_root_file: bool, text: str) -> ManifestStatus | None:
    if name != "plugin.json" or not is_root_file:
        return None
    try:
        json.loads(text)
    except json.JSONDecodeError:
        return "invalid_json"
    return "present"


def _manifest_status(sources: tuple[_Source, ...]) -> ManifestStatus:
    statuses = {source.manifest_status for source in sources if source.manifest_status is not None}
    if "invalid_json" in statuses:
        return "invalid_json"
    if "present" in statuses:
        return "present"
    return "missing"


def _root_manifest_text(sources: tuple[_Source, ...]) -> str | None | _Undecodable:
    for source in sources:
        if source.is_root_file and source.name == MANIFEST_FILENAME:
            try:
                return source.content.decode("utf-8")
            except UnicodeDecodeError:
                return _UNDECODABLE
    return None


def _declared_hook_report(manifest_text: str | None | _Undecodable, host_version: HostVersionObservation) -> tuple[str, JsonObject]:
    if manifest_text is None:
        return "absent", _hook_report("absent", None, (), host_version, manifest_present=False)
    if isinstance(manifest_text, _Undecodable):
        return "unreadable", _hook_report("invalid", None, ("plugin manifest is not valid UTF-8",), host_version)
    try:
        declaration = read_hook_declaration(manifest_text)
    except PluginManifestFormatError as exc:
        return "unreadable", _hook_report("invalid", None, (str(exc)[:200],), host_version)
    except PluginHookDeclarationError as exc:
        return "present", _hook_report("invalid", None, (str(exc)[:200],), host_version)
    return "present", _hook_report("declared" if declaration.hooks else "absent", declaration, (), host_version)


def _hook_report(status: str, declaration: Any, diagnostics: tuple[str, ...], host_version: HostVersionObservation, *, manifest_present: bool = True) -> JsonObject:
    hooks = declaration.hooks if declaration is not None else ()
    unknown = sum(1 for hook in hooks if hook.contract.effect == "unknown")
    range_state = declaration.range_status if declaration is not None else "undeclared"
    findings = list(diagnostics)
    if declaration is not None:
        if range_state == "unsupported":
            findings.append(f"manifest requires a {PLUGIN_HOOK_CONTRACT_HOST} version outside {PLUGIN_HOOK_CONTRACT_RANGE}; declared hook semantics are unknown")
        elif range_state == "unparsable":
            findings.append("manifest declares an unreadable Hermes version range; declared hook semantics are unknown")
        elif range_state == "undeclared" and hooks:
            findings.append(f"manifest declares no Hermes version range; hooks are classified against {PLUGIN_HOOK_CONTRACT_RANGE}")
        if unknown:
            findings.append(f"{unknown} declared hook name(s) are not in the supported host contract and cannot be classified")
        if any(hook.field == SECONDARY_HOOK_FIELD for hook in hooks):
            findings.append(f"hook(s) declared under `{SECONDARY_HOOK_FIELD}`, which the Hermes manifest parser does not read into `{CANONICAL_HOOK_FIELD}`")
    findings.extend(_host_diagnostics(host_version, len(hooks)))
    if not manifest_present:
        findings.append("no root plugin.yaml was scanned, so the plugin's declared hook contract was never established")
    classified = manifest_present and status != "invalid" and not unknown and range_state in ("supported", "undeclared") and host_version.status not in HOST_VERSION_HOLD_STATUSES
    return {
        "declaration_status": status,
        "classification_status": "classified" if classified else "unknown",
        "host_contract": {
            "host": PLUGIN_HOOK_CONTRACT_HOST,
            "supported_range": PLUGIN_HOOK_CONTRACT_RANGE,
            "contract_source": PLUGIN_HOOK_CONTRACT_SOURCE,
            "declared_range": _declared_range_value(declaration),
            "declared_range_status": range_state,
            "inspected_host": _inspected_host(host_version),
        },
        "hook_count": len(hooks),
        "unknown_hook_count": unknown,
        "effects": sorted({hook.contract.effect for hook in hooks}),
        "hooks": [
            {
                "hook": hook.name,
                "declared_in": hook.field,
                "effect": hook.contract.effect,
                "host_contract": hook.contract.host_contract,
                "timeout_semantics": hook.contract.timeout_semantics,
            }
            for hook in hooks
        ],
        "diagnostics": findings,
    }


def _inspected_host(observation: HostVersionObservation) -> JsonObject:
    if observation.version is not None:
        version = observation.version
    elif observation.status == "not_observed":
        version = "<absent>"
    else:
        version = "<invalid>"
    return {"version": version, "observation_method": observation.method, "compatibility": observation.status}


def _declared_range_value(declaration: Any) -> str:
    if declaration is None or declaration.declared_range is None:
        return "<absent>"
    if declaration.range_status == "unparsable":
        return "<invalid>"
    return declaration.declared_range


def _host_diagnostics(observation: HostVersionObservation, hook_count: int) -> list[str]:
    if observation.status == "incompatible":
        return [
            f"the inspected {PLUGIN_HOOK_CONTRACT_HOST} version is outside the supported host contract "
            f"{PLUGIN_HOOK_CONTRACT_RANGE}; the hook mapping was never established for it, so the declared "
            "hook semantics are held unknown"
        ]
    if observation.status == "unreadable":
        return [f"the inspected {PLUGIN_HOOK_CONTRACT_HOST} version was not readable; declared hook semantics are held unknown"]
    if observation.status == "not_observed" and hook_count:
        return [f"no {PLUGIN_HOOK_CONTRACT_HOST} version was inspected, so hook semantics are not bound to the host this plugin would be enabled on"]
    return []


def _hook_categories(declared_hooks: JsonObject) -> set[str]:
    categories: set[str] = set()
    if declared_hooks["hook_count"]:
        categories.add("hermes_hook_capability")
    if declared_hooks["classification_status"] != "classified":
        categories.add("undetermined_hook_contract")
    return categories


def _self_update_signals(text: str, categories: frozenset[str]) -> frozenset[str]:
    signals: set[str] = set()
    if "network_request" in categories:
        signals.add("remote_retrieval")
    if _REPLACEMENT_WRITE_CALL.search(text) and _REPLACEMENT_TARGET.search(text):
        signals.add("code_replacement_write")
    if _ARCHIVE_EXTRACTION.search(text):
        signals.add("archive_extraction")
    if _SELF_UPDATE_COMMAND.search(text) and _PROCESS_EXECUTION.search(text):
        signals.add("host_update_command")
    if _INTEGRITY_VERIFICATION.search(text):
        signals.add("integrity_verification")
    return frozenset(signals)


def _self_update_report(sources: tuple[_Source, ...]) -> JsonObject:
    counts: dict[str, int] = {}
    for source in sources:
        for signal in source.self_update_signals:
            counts[signal] = counts.get(signal, 0) + 1
    observed = frozenset(counts)
    composing = observed - MITIGATING_SELF_UPDATE_SIGNALS
    mitigating = observed & MITIGATING_SELF_UPDATE_SIGNALS
    dynamic = any("dynamic_code_execution" in source.risk_categories for source in sources)
    composition = _matched_composition(composing)
    classification = _self_update_classification(composition, composing, dynamic)
    diagnostics = [_SELF_UPDATE_DIAGNOSTICS[classification]]
    if mitigating:
        diagnostics.append("integrity verification appears as a mitigating signal only; it is not evidence any checksum or signature was computed, compared, or valid")
    return {
        "classification": classification,
        "composition": composition,
        "signals": sorted(composing),
        "mitigating_signals": sorted(mitigating),
        "signal_file_counts": {name: counts[name] for name in sorted(counts)},
        "diagnostics": diagnostics,
    }


def _matched_composition(signals: frozenset[str]) -> str | None:
    for name, members in SELF_UPDATE_COMPOSITIONS:
        if members <= signals:
            return name
    return None


def _self_update_classification(composition: str | None, signals: frozenset[str], dynamic_execution: bool) -> SelfUpdateClassification:
    if composition is not None:
        return "detected"
    if dynamic_execution and "remote_retrieval" in signals:
        return "needs_review"
    return "not_detected"


def _self_update_categories(classification: str) -> set[str]:
    if classification == "detected":
        return {"self_update_or_code_replacement"}
    if classification == "needs_review":
        return {"undetermined_self_update_path"}
    return set()


_SELF_UPDATE_DIAGNOSTICS: Final[dict[str, str]] = {
    "detected": "the scanned text composes a plausible path to replace installed plugin code; this is not evidence the plugin retrieved or replaced anything",
    "needs_review": "the scanned text can retrieve remote bytes and execute dynamic code, so a code-replacement path is neither established nor ruled out",
    "not_detected": "no self-update composition matched; this is not evidence that the plugin cannot replace its own code outside this bounded static read",
}
