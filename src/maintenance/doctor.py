from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..command_path import inspect_omj_command_path
from ..config_adapter import external_dirs, read_config
from ..hermes_bootstrap import detect_hermes
from ..hashutil import sha256_file, sha256_text
from ..install.installer import content_freshness, skill_install_relative_dir, skill_profile_state
from ..manifest import local_modifications, manifest_owned_files, read_manifest
from ..paths import OmjPaths
from ..plugin_observations import (
    PLUGIN_HOST_ACTIVE_OBSERVATION_EVENTS,
    latest_plugin_host_observation,
    plugin_host_runtime_readiness,
)
from ..plugin_pack import inspect_plugin_bundle
from ..plugin_bundle.omj.runtime_paths import binding_diagnostic
from ..runtime.artifacts import read_state, read_state_error
from ..skill_pack import builtin_skill_reference_templates, builtin_skill_templates
from ..skills.catalog import CORE_PROFILE_SKILLS, CORE_SKILLS
from ..targets import read_target_registry_result, summarize_target_registry
from ..workflow_state import list_workflow_states
from .advisory import AdvisoryReport, run_config_advisories

def run_doctor_advisories(paths: OmjPaths) -> AdvisoryReport:
    """Run read-only configuration advice separately from health checks."""
    return run_config_advisories(
        paths.hermes_home,
        omj_home=paths.omj_home,
        discovery_home=paths.hermes_home.parent,
    )

WARNING_NEXT_ACTION_PRIORITY = {
    # These warnings often block first-run usability even when the local OMJ
    # health checks are otherwise OK. Lower-priority warnings stay visible in
    # the check list without replacing the beginner next action.
    "command_path": 100,
    "target_topology": 80,
}
DEFAULT_DOCTOR_NEXT_ACTION = "Open Hermes Agent and try: Use OMJ request-to-handoff for: I want to safely add a feature to this repo."


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    message: str
    severity: str = "auto"
    remediation: str = ""
    next_action: str = ""
    observed: bool = True

    def __post_init__(self) -> None:
        if self.severity == "auto":
            object.__setattr__(self, "severity", "ok" if self.ok else "blocking")
        if not self.ok and not self.remediation:
            object.__setattr__(self, "remediation", _default_remediation(self.name))
        if not self.ok and not self.next_action:
            object.__setattr__(self, "next_action", _default_next_action(self.name))


def run_doctor(paths: OmjPaths) -> list[Check]:
    checks: list[Check] = []
    command_path = inspect_omj_command_path()
    checks.append(
        Check(
            "command_path",
            True,
            str(command_path["message"]),
            severity="ok" if command_path["found"] else "warning",
            next_action=str(command_path["next_action"]),
            observed=bool(command_path["observed"]),
        )
    )
    manifest_error = ""
    try:
        manifest = read_manifest(paths.manifest_path)
    except (OSError, ValueError) as error:
        manifest = None
        manifest_error = f": {error}"
    state_error = read_state_error(paths)
    state = None if state_error else read_state(paths)
    checks.append(Check("manifest", manifest is not None, f"{paths.manifest_path}{manifest_error}"))
    if manifest:
        manifest_skills_dir = manifest.get("skills_dir")
        checks.append(
            Check(
                "manifest_skills_dir",
                manifest_skills_dir == str(paths.skills_dir),
                f"manifest skills_dir={manifest_skills_dir!r}; expected {paths.skills_dir}",
            )
        )
        modified = local_modifications(manifest, paths.skills_dir)
        checks.append(Check("local_modifications", not modified, "managed files match manifest" if not modified else f"changed managed files: {', '.join(modified)}"))
        owned_files = manifest_owned_files(manifest)
        missing_owned = [relative for relative in owned_files if not (paths.skills_dir / relative).is_file()]
        checks.append(Check("manifest_owned_files", not missing_owned, f"{len(owned_files)} manifest-owned file(s) present" if not missing_owned else f"missing manifest-owned files: {', '.join(missing_owned)}"))
        checks.append(Check("manifest_freshness", not modified, "manifest-owned files match recorded digests" if not modified else f"stale manifest-owned files: {', '.join(modified)}"))
    checks.extend(_runtime_checks(paths, manifest, state, state_error))
    checks.extend(_skill_health_checks(paths, manifest))
    checks.append(_content_freshness_check(paths, manifest))
    checks.append(Check("skills_dir", paths.skills_dir.is_dir(), f"{paths.skills_dir}"))
    config_text = read_config(paths.hermes_config_path)
    dirs = external_dirs(config_text)
    checks.append(Check("hermes_config", paths.hermes_config_path.exists(), f"{paths.hermes_config_path}"))
    external_registered = any(_same_resolved_path(paths.skills_dir, Path(value)) for value in dirs)
    checks.append(Check("external_dir", external_registered, f"{paths.skills_dir} in skills.external_dirs (realpath-aware)"))
    checks.append(Check("runtime_context", external_registered, (
        f"Hermes config {paths.hermes_config_path} points at {paths.skills_dir}; for a bot or hosted runtime, run doctor with the same --hermes-home used by that process"
        if external_registered else f"{paths.skills_dir} is not registered in {paths.hermes_config_path}; run `omj apply`, or pass --hermes-home matching the Hermes or bot runtime"
    )))
    _append_model_checks(checks, paths.hermes_home)
    hermes_runtime = detect_hermes()
    checks.append(
        Check(
            "hermes_runtime",
            True,
            (
                f"hermes runtime found at {hermes_runtime['path']}"
                + (f" (version {hermes_runtime['version']})" if hermes_runtime["version"] else "")
                if hermes_runtime["found"]
                else (
                    "hermes runtime CLI not found on PATH; OMJ wraps Hermes but the runtime is not installed. "
                    "Run `omj hermes install` to see the upstream installer, or `omj hermes install --apply` to install it."
                )
            ),
            severity="ok" if hermes_runtime["found"] else "warning",
            next_action=(
                ""
                if hermes_runtime["found"]
                else "Run `omj hermes install --apply` to install the Hermes runtime OMJ wraps, then rerun `omj doctor`."
            ),
            observed=bool(hermes_runtime["observed"]),
        )
    )
    target_registry, target_registry_error = read_target_registry_result(paths)
    target_topology = summarize_target_registry(paths)
    if target_registry_error:
        checks.append(Check("target_registry", False, f"target registry unreadable: {target_registry_error}"))
    else:
        known_count = int(target_topology.get("known_target_count") or 0)
        active_count = int(target_topology.get("active_agent_count") or 0)
        mode = str(target_topology.get("mode", "unknown"))
        if target_registry:
            checks.append(
                Check(
                    "target_registry",
                    True,
                    f"{known_count} known Hermes target(s); active_agent_count={active_count}; mode={mode}",
                )
            )
        else:
            checks.append(
                Check(
                    "target_registry",
                    True,
                    "no target registry yet; `omj setup` or wrapper target metadata will create it when needed",
                    observed=False,
                )
            )
    checks.append(
        Check(
            "target_topology",
            target_topology.get("status") != "unreadable",
            (
                f"mode={target_topology.get('mode')}; transition={target_topology.get('transition')}; "
                f"skill_scope_awareness={target_topology.get('requires_skill_scope_awareness')}"
            ),
            severity="warning" if target_topology.get("requires_skill_scope_awareness") else "auto",
            observed=target_topology.get("status") == "available",
        )
    )
    plugin = inspect_plugin_bundle(paths)
    latest_plugin_observation, plugin_observation_errors = latest_plugin_host_observation(paths)
    latest_plugin_readiness = ""
    if latest_plugin_observation:
        latest_plugin_readiness = str(
            latest_plugin_observation.get("runtime_readiness")
            or plugin_host_runtime_readiness(
                event=str(latest_plugin_observation.get("event", "")),
                status=str(latest_plugin_observation.get("status", "")),
            )
        )
    latest_plugin_active = latest_plugin_readiness == "active_runtime_observed"
    plugin_expected = bool(plugin["plugin_dir_installed"]) or bool(state and state.get("last_plugin_distribution"))
    if plugin_expected:
        binding_ok, binding_message = binding_diagnostic(
            paths.omj_home,
            paths.hermes_home,
            config_text,
        )
        checks.append(
            Check(
                "plugin_binding",
                binding_ok,
                binding_message,
                severity="ok" if binding_ok else "warning",
                remediation="Run `omj setup` to record the selected OMJ home, or preserve the profile-owned binding and rerun doctor.",
                next_action="Run `omj setup` with the Hermes profile home selected, then rerun `omj doctor`.",
            )
        )
    if not plugin_expected:
        checks.append(Check("plugin_bundle", True, f"managed OMJ plugin bridge is not installed yet at {paths.hermes_plugin_dir}"))
    else:
        checks.extend(
            [
                Check("plugin_bundle", bool(plugin["plugin_dir_installed"]), f"{paths.hermes_plugin_dir}"),
                Check("plugin_manifest", bool(plugin["plugin_manifest_valid"]), str(plugin["plugin_manifest_path"])),
                Check(
                    "plugin_bundle_current",
                    bool(plugin["plugin_manifest_current"]),
                    (
                        "installed plugin bundle matches the current OMJ package"
                        if plugin["plugin_manifest_current"]
                        else _plugin_bridge_message(plugin)
                    ),
                    remediation="" if plugin["plugin_manifest_current"] else _plugin_bridge_remediation(plugin),
                    next_action="" if plugin["plugin_manifest_current"] else _plugin_bridge_next_action(plugin),
                ),
                Check(
                    "plugin_import_smoke",
                    bool(plugin["plugin_import_smoke"]),
                    "installed plugin imports without side effects" if plugin["plugin_import_smoke"] else "; ".join(plugin["errors"]),
                    remediation="" if plugin["plugin_import_smoke"] else _plugin_bridge_remediation(plugin),
                    next_action="" if plugin["plugin_import_smoke"] else _plugin_bridge_next_action(plugin),
                ),
                Check(
                    "plugin_register_smoke",
                    bool(plugin["plugin_register_smoke"]),
                    (f"registered tools={plugin['registered_tools']} hooks={plugin['registered_hooks']}" if plugin["plugin_register_smoke"] else _plugin_bridge_message(plugin)),
                    remediation="" if plugin["plugin_register_smoke"] else _plugin_bridge_remediation(plugin),
                    next_action="" if plugin["plugin_register_smoke"] else _plugin_bridge_next_action(plugin),
                ),
                Check(
                    "plugin_descriptor_admission",
                    bool(plugin.get("descriptor_admission", {}).get("ok")),
                    _plugin_admission_message(plugin.get("descriptor_admission", {})),
                    remediation="Run `omj setup` to install a plugin descriptor admitted by the local Hermes hook contract.",
                    next_action="Run `omj setup`, then `omj doctor` again.",
                ),
                Check(
                    "plugin_bundle_import_scan",
                    bool(plugin.get("bundle_import_scan", {}).get("ok")) and bool(plugin.get("bundle_import_scan", {}).get("scanned")),
                    _plugin_import_scan_message(plugin.get("bundle_import_scan", {})),
                    remediation="Run `omj setup` after repairing the managed plugin bundle import boundary.",
                    next_action="Run `omj setup`, then `omj doctor` again.",
                ),
                Check(
                    "plugin_runtime_observed",
                    True,
                    (
                        f"{latest_plugin_readiness} by {latest_plugin_observation.get('host', 'unknown')} "
                        f"({latest_plugin_observation.get('event', 'unknown')}, "
                        f"session={latest_plugin_observation.get('session_id', 'unknown')})"
                        if latest_plugin_observation and latest_plugin_observation.get("observed")
                        else (
                            f"plugin observation ledger unreadable: {'; '.join(plugin_observation_errors[:3])}"
                            if plugin_observation_errors
                            else (
                                f"latest plugin host observation is {latest_plugin_observation.get('status', 'unknown')}; "
                                "Hermes runtime load/use is not currently observed"
                                if latest_plugin_observation
                                else "not required for doctor; Hermes runtime load/use must be observed separately before claiming native runtime readiness"
                            )
                        )
                    ),
                    severity="ok" if latest_plugin_active else "warning",
                    next_action=(
                        ""
                        if latest_plugin_active
                        else (
                            "Record an active Hermes plugin event "
                            f"({', '.join(PLUGIN_HOST_ACTIVE_OBSERVATION_EVENTS)}) before claiming native runtime readiness. "
                            "Watch it flip live with `omj hud --watch` once Hermes actually uses OMJ."
                        )
                    ),
                    observed=bool(latest_plugin_observation and latest_plugin_observation.get("observed")),
                ),
            ]
        )
    profile_installs = state.get("last_team_profile_install") if isinstance(state, dict) else None
    if not profile_installs:
        checks.append(Check("team_profile_packs", True, f"optional OMJ team profile packs are not installed at {paths.hermes_agents_dir}"))
    else:
        expected_files: list[str] = []
        if isinstance(profile_installs, list):
            for install in profile_installs:
                if isinstance(install, dict) and isinstance(install.get("files"), list):
                    expected_files.extend(str(item) for item in install["files"])
        missing = [path for path in expected_files if not Path(path).exists()]
        checks.append(
            Check(
                "team_profile_packs",
                not missing,
                (
                    f"{len(expected_files)} optional team profile file(s) installed under {paths.hermes_agents_dir}"
                    if not missing
                    else f"missing optional team profile files: {', '.join(missing)}"
                ),
            )
        )
    return checks


def _runtime_checks(
    paths: OmjPaths,
    manifest: dict | None,
    state: dict | None,
    state_error: str | None,
) -> list[Check]:
    runtime = paths.runtime_dir
    runtime_ok = not runtime.exists() or runtime.is_dir()
    if runtime_ok and runtime.is_dir():
        runs = paths.runtime_runs_dir
        runtime_ok = not runs.exists() or runs.is_dir()
    runtime_message = (
        f"{runtime} is a directory with readable runtime paths"
        if runtime_ok and runtime.exists()
        else f"{runtime} is not a directory"
        if runtime.exists()
        else f"{runtime} has not been created yet"
    )
    checks = [
        Check("runtime_artifacts", runtime_ok, runtime_message, observed=runtime.exists()),
    ]
    if state_error:
        checks.append(Check("runtime_state", False, f"runtime state unreadable: {state_error}"))
    elif state is None:
        checks.append(Check("runtime_state", True, f"{paths.runtime_state_path} not recorded yet", observed=False))
    else:
        expected_hash = sha256_file(paths.manifest_path) if manifest and paths.manifest_path.is_file() else None
        actual_hash = state.get("manifest_sha256")
        hash_ok = actual_hash in {None, expected_hash}
        checks.append(
            Check(
                "runtime_state",
                hash_ok,
                "runtime state matches manifest hash" if hash_ok else "runtime state manifest hash is stale",
            )
        )
    workflow_dir = paths.workflow_state_dir
    if not workflow_dir.exists():
        checks.append(Check("workflow_state", True, f"{workflow_dir} not recorded yet", observed=False))
    elif not workflow_dir.is_dir():
        checks.append(Check("workflow_state", False, f"{workflow_dir} is not a directory"))
    else:
        states, errors = list_workflow_states(paths)
        checks.append(
            Check(
                "workflow_state",
                not errors,
                f"{workflow_dir} contains {len(states)} readable workflow state file(s)"
                if not errors
                else f"{workflow_dir} has unreadable state: {errors}",
            )
        )
    return checks


def _skill_health_checks(paths: OmjPaths, manifest: dict | None) -> list[Check]:
    profile = str((manifest or {}).get("requested_profile") or (manifest or {}).get("profile") or "full")
    profile_state = skill_profile_state(paths.skills_dir, manifest)
    catalog_names = [template.name for template in builtin_skill_templates()]
    selected = list(CORE_PROFILE_SKILLS) if profile == "core" else catalog_names
    baseline = list(CORE_SKILLS)
    names = list(dict.fromkeys([*baseline, *selected]))
    checks = [
        Check(
            "skill_profile",
            profile in {"core", "full"} and profile_state.get("effective_profile") != "none",
            f"requested={profile}; effective={profile_state.get('effective_profile')}; installed={profile_state.get('installed_skill_count')}",
            observed=bool(manifest),
        )
    ]
    for name in names:
        path = paths.skills_dir / skill_install_relative_dir(name) / "SKILL.md"
        checks.append(Check(f"skill:{name}", path.is_file(), str(path), observed=path.exists()))
    return checks


def _content_freshness_check(paths: OmjPaths, manifest: dict | None) -> Check:
    try:
        freshness = content_freshness(paths)
    except (OSError, ValueError) as error:
        return Check("content_freshness", False, f"producer content unreadable: {error}", observed=manifest is not None)
    missing = {str(item) for item in freshness.get("missing_files", [])}
    modified = {str(item) for item in freshness.get("modified_files", [])}
    ownership_mismatch: set[str] = set()
    producer_mismatch: set[str] = set()
    if manifest and str(manifest.get("source") or "builtin") == "builtin":
        profile = str(manifest.get("requested_profile") or manifest.get("profile") or "full")
        selected = set(CORE_PROFILE_SKILLS) if profile == "core" else {template.name for template in builtin_skill_templates()}
        expected: dict[str, str] = {}
        for template in builtin_skill_templates():
            if template.name in selected:
                expected[(skill_install_relative_dir(template.name) / "SKILL.md").as_posix()] = sha256_text(template.content)
        for reference in builtin_skill_reference_templates():
            if reference.skill_name in selected:
                relative = skill_install_relative_dir(reference.skill_name) / reference.relative_path
                expected[relative.as_posix()] = sha256_text(reference.content)
        owned = manifest_owned_files(manifest)
        ownership_mismatch = set(expected).symmetric_difference(owned)
        for relative, expected_sha in expected.items():
            path = paths.skills_dir / relative
            if not path.is_file():
                producer_mismatch.add(relative)
            else:
                try:
                    if sha256_file(path) != expected_sha:
                        producer_mismatch.add(relative)
                except OSError:
                    producer_mismatch.add(relative)
    problems = sorted(missing | modified | ownership_mismatch | producer_mismatch)
    ok = bool(manifest) and not problems and bool(freshness.get("content_fresh"))
    message = (
        f"producer-owned content is fresh ({freshness.get('owned_file_count', 0)} file(s))"
        if ok
        else f"stale or incomplete producer content: {', '.join(problems[:8]) or 'manifest/content unavailable'}"
    )
    return Check("content_freshness", ok, message, observed=manifest is not None)

def doctor_ok(checks: list[Check]) -> bool:
    return all(check.ok for check in checks)


def recommended_next_action(checks: list[Check]) -> str:
    for check in checks:
        if not check.ok and check.severity == "blocking":
            return check.next_action or check.remediation
    prioritized_warnings = sorted(
        (
            check
            for check in checks
            if check.severity == "warning" and check.next_action and WARNING_NEXT_ACTION_PRIORITY.get(check.name, 0) > 0
        ),
        key=lambda check: WARNING_NEXT_ACTION_PRIORITY[check.name],
        reverse=True,
    )
    if prioritized_warnings:
        return prioritized_warnings[0].next_action
    return DEFAULT_DOCTOR_NEXT_ACTION


def _plugin_admission_message(admission: dict) -> str:
    if admission.get("ok"):
        return "installed plugin descriptor is admitted by the Hermes hook contract"
    invalid = admission.get("invalid_fields") or []
    detail = str(admission.get("detail") or admission.get("reason") or "descriptor rejected")
    return f"plugin descriptor admission failed: {detail}" + (f"; invalid fields={invalid}" if invalid else "")


def _plugin_import_scan_message(scan: dict) -> str:
    if scan.get("ok") and scan.get("scanned"):
        return f"plugin bundle import scan passed ({scan.get('module_count', 0)} module(s))"
    findings = scan.get("findings") or []
    detail = str(scan.get("reason") or "plugin bundle import scan failed")
    if findings:
        detail += f"; findings={findings[:3]}"
    return detail

def _plugin_bridge_message(plugin: dict) -> str:
    errors = [str(item) for item in plugin.get("errors", []) if str(item)]
    if errors:
        return "; ".join(errors)
    missing_tools = [str(item) for item in plugin.get("missing_registered_tools", [])]
    missing_hooks = [str(item) for item in plugin.get("missing_registered_hooks", [])]
    if missing_tools or missing_hooks:
        details: list[str] = []
        if missing_tools:
            details.append(f"missing tools={missing_tools}")
        if missing_hooks:
            details.append(f"missing hooks={missing_hooks}")
        return "plugin register smoke is incomplete: " + "; ".join(details)
    return "managed plugin bridge is installed but did not pass local import/register smoke"


def _plugin_bridge_remediation(plugin: dict) -> str:
    if plugin.get("plugin_bundle_stale"):
        return "Run `omj setup` to refresh the managed plugin bridge from the current OMJ package."
    return "Run `omj setup`; use `omj setup --force` only if replacing local plugin edits is intended."


def _plugin_bridge_next_action(plugin: dict) -> str:
    if plugin.get("plugin_bundle_stale"):
        return "Run `omj setup`, then `omj doctor` again."
    return "Run `omj setup --force`, then `omj doctor` again."


def _same_resolved_path(expected: Path, candidate: Path) -> bool:
    try:
        return expected.expanduser().resolve() == candidate.expanduser().resolve()
    except (OSError, RuntimeError, ValueError):
        return False


def _append_model_checks(checks: list[Check], hermes_home: Path) -> None:
    """Report selected Hermes model metadata as advisory, never native readiness."""
    try:
        from ..commands.providers import build_model_status
        payload = build_model_status(hermes_home)
    except (OSError, ValueError, TypeError, KeyError, ImportError):
        payload = {}
    source = payload.get("source_state", {}).get("config", {}) if isinstance(payload, dict) else {}
    config = payload.get("config", {}) if isinstance(payload, dict) else {}
    default_row = payload.get("default_model", {}) if isinstance(payload, dict) else {}
    provider_row = payload.get("provider", {}) if isinstance(payload, dict) else {}
    base_row = payload.get("base_url", {}) if isinstance(payload, dict) else {}
    default_model = str(default_row.get("value", "") if isinstance(default_row, dict) else default_row or "")
    provider = str(provider_row.get("value", "") if isinstance(provider_row, dict) else provider_row or "")
    base_url = str(base_row.get("host", "") if isinstance(base_row, dict) else base_row or "")
    found = bool(source.get("found") or config.get("found"))
    checks.append(Check("model_selected_home", True, f"selected Hermes home={hermes_home}", severity="ok", observed=True))
    checks.append(Check("model_default", True, f"default model={default_model or 'unset'}", severity="warning" if not default_model else "ok", observed=found))
    checks.append(Check("model_provider", True, f"provider={provider or 'unset'}", severity="warning" if not provider else "ok", observed=found))
    checks.append(Check("model_base_url", True, f"base URL={base_url or 'unset'}", severity="warning" if not base_url else "ok", observed=found))


def _default_remediation(name: str) -> str:
    if name == "external_dir" or name == "runtime_context":
        return "Run `omj setup` or `omj apply` with the same --hermes-home used by the Hermes or wrapper runtime."
    if name.startswith("skill:") or name in {"manifest", "manifest_skills_dir", "skills_dir"}:
        return "Run `omj setup` to install the managed skill pack, or reinstall with `omj install --force` if managed files drifted."
    if name == "local_modifications":
        return "Review local edits under the managed skill directory, then run `omj install --force` only if replacing managed files is intended."
    if name in {"runtime_artifacts", "workflow_state", "runtime_state"}:
        return "Repair the unreadable or invalid OMJ runtime artifact/state shape, then rerun `omj doctor`."
    if name.startswith("plugin_"):
        return "Run `omj setup` to reinstall the managed plugin bridge, or `omj setup --force` if replacing local plugin edits is intended."
    if name.startswith("target_"):
        return "Repair the OMJ target registry or rerun `omj setup` with the Hermes home used by the wrapper runtime."
    if name == "hermes_config":
        return "Run `omj setup` to create or update the Hermes configuration for managed skill discovery."
    return "Run `omj doctor` after repairing the reported path or configuration."


def _default_next_action(name: str) -> str:
    if name == "external_dir" or name == "runtime_context":
        return "Run `omj setup`, then restart or refresh Hermes Agent so it can reload the registered skill directory."
    if name == "local_modifications":
        return "Inspect changed managed skill files; use `omj install --force` only when replacing those edits is acceptable."
    if name.startswith("skill:") or name in {"manifest", "manifest_skills_dir", "skills_dir", "hermes_config"}:
        return "Run `omj setup`, then `omj doctor` again."
    if name.startswith("plugin_"):
        return "Run `omj setup --force`, then `omj doctor` again."
    if name.startswith("target_"):
        return "Run `omj setup` for the current Hermes target, then rerun `omj doctor`."
    if name in {"runtime_artifacts", "workflow_state", "runtime_state"}:
        return "Repair the OMJ runtime path or malformed state artifact, then rerun `omj doctor`."
    return "Fix the reported check and rerun `omj doctor`."
