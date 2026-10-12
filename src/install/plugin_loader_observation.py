from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
from typing import Any

from ..plugin_bundle.omj.metadata import PROVIDED_HOOKS, PROVIDED_TOOLS
from .release_smoke_core import CommandResult, Runner, subprocess_runner_exact_env

OBSERVATION_SCHEMA_VERSION = "plugin_loader_observation/v1"
_OBSERVATION_PREFIX = "OMJ_PLUGIN_LOADER_OBSERVATION="
# `hermes_cli.__version__` is the real, stable, public version attribute
# shipped on hermes_cli itself; it is read directly rather than guessing at
# an unverified submodule, so this probe never falsely claims "unresolved"
# for a host it could not actually inspect correctly.
_PROBE_SCRIPT = r'''
import json

import hermes_cli
from hermes_cli.plugins import PluginManager

hermes_version = str(getattr(hermes_cli, "__version__", "") or "unknown")
manager = PluginManager()
manager.discover_and_load(force=True)
loaded = manager._plugins.get("omj")
payload = {
    "enabled": bool(loaded and loaded.enabled),
    "error": None if loaded is None else loaded.error,
    "tools": [] if loaded is None else sorted(loaded.tools_registered),
    "hooks": [] if loaded is None else sorted(loaded.hooks_registered),
    "hermes_version": hermes_version,
}
print("OMJ_PLUGIN_LOADER_OBSERVATION=" + json.dumps(payload, sort_keys=True))
'''


def observe_real_loader_registration(
    plugin_dir: Path,
    *,
    python_executable: Path | None = None,
    hermes_code_root: Path | None = None,
    runner: Runner | None = None,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    """Observe Hermes' real plugin manager in an isolated temporary home.

    This probe executes no tool or hook. It only asks the host manager which
    registrations it recorded for the copied, locally-owned plugin bundle.
    """
    hermes_python = python_executable or _find_hermes_python()
    if hermes_python is None or not hermes_python.is_file():
        return _not_observed("hermes_not_installed")
    if not plugin_dir.is_dir():
        return _not_observed("plugin_bundle_not_installed")
    if hermes_code_root is not None and not (hermes_code_root / "hermes_cli").is_dir():
        return _not_observed("hermes_code_tree_absent")

    execute = runner or subprocess_runner_exact_env
    with TemporaryDirectory(prefix="omj-hermes-loader-") as tmp:
        probe_root = Path(tmp)
        hermes_home = probe_root / "hermes-home"
        disposable_home = probe_root / "home"
        isolated_plugin = hermes_home / "plugins" / "omj"
        isolated_plugin.parent.mkdir(parents=True)
        disposable_home.mkdir(parents=True)
        shutil.copytree(plugin_dir, isolated_plugin)
        (hermes_home / "config.yaml").write_text(
            "plugins:\n  enabled:\n    - omj\n  disabled: []\n",
            encoding="utf-8",
        )
        env: dict[str, str] = {
            "HOME": str(disposable_home),
            "HERMES_HOME": str(hermes_home),
            "PATH": os.environ.get("PATH", ""),
        }
        if hermes_code_root is not None:
            env["PYTHONPATH"] = str(hermes_code_root)
        command = [str(hermes_python), "-c", _PROBE_SCRIPT]
        try:
            result = execute(command, timeout_seconds, env)
        except (OSError, subprocess.TimeoutExpired, TimeoutError) as exc:
            return _not_observed("loader_probe_failed", detail=type(exc).__name__)
        env_identity = {"HOME": env["HOME"], "HERMES_HOME": env["HERMES_HOME"], "PYTHONPATH": env.get("PYTHONPATH", "")}

    if result.returncode != 0:
        return _not_observed("loader_probe_failed", detail=_bounded_detail(result.stderr or result.stdout), env=env_identity)
    payload = _parse_observation(result)
    if payload is None:
        return _not_observed("loader_probe_failed", detail="invalid_probe_output", env=env_identity)
    hermes_version = payload.get("hermes_version")
    if not isinstance(hermes_version, str) or not hermes_version or hermes_version == "unknown":
        return _not_observed("hermes_version_unresolved", env=env_identity)

    tools = _string_list(payload.get("tools"))
    hooks = _string_list(payload.get("hooks"))
    enabled = payload.get("enabled") is True
    error = payload.get("error")
    expected_tools = sorted(PROVIDED_TOOLS)
    expected_hooks = sorted(PROVIDED_HOOKS)
    ok = enabled and tools == expected_tools and hooks == expected_hooks
    return {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "observed": True,
        "ok": ok,
        "reason": "registration_matches_manifest" if ok else "registration_mismatch",
        "enabled": enabled,
        "error": "" if error is None else _bounded_detail(str(error)),
        "hermes_version": hermes_version,
        "registered_tools": tools,
        "registered_hooks": hooks,
        "expected_tools": expected_tools,
        "expected_hooks": expected_hooks,
        "environment": env_identity,
    }


def resolve_hermes_code_root(hermes_home: Path | None = None) -> Path:
    """Resolve the selected Hermes code tree, with profile-to-root fallback."""
    override = _hermes_python_override()
    if override is not None and len(override.parents) >= 3:
        tree = override.parents[2]
        if (tree / "hermes_cli").is_dir():
            return tree
    selected = hermes_home or _selected_hermes_home()
    if (selected / "hermes_cli").is_dir():
        return selected
    if selected.parent.name == "profiles" and (selected.parent.parent / "hermes_cli").is_dir():
        return selected.parent.parent
    return selected


def _selected_hermes_home() -> Path:
    value = " ".join(os.environ.get("HERMES_HOME", "").split())
    return Path(value).expanduser() if value else Path.home() / ".hermes"


def _hermes_python_override() -> Path | None:
    value = " ".join(os.environ.get("HERMES_PYTHON", "").split())
    return Path(value).expanduser() if value else None


def _find_hermes_python() -> Path | None:
    override = _hermes_python_override()
    if override is not None:
        return override if override.is_file() else None
    candidate = Path.home() / ".hermes" / "hermes-agent" / "venv" / "bin" / "python"
    if candidate.is_file():
        return candidate
    executable = shutil.which("hermes")
    if not executable:
        return None
    try:
        first_line = Path(executable).read_text(encoding="utf-8").splitlines()[0]
    except (OSError, UnicodeError, IndexError):
        return None
    if first_line.startswith("#!") and "python" in first_line.lower():
        candidate = Path(first_line[2:].strip())
        return candidate if candidate.is_file() else None
    return None


def _parse_observation(result: CommandResult) -> dict[str, Any] | None:
    for line in reversed(result.stdout.splitlines()):
        if not line.startswith(_OBSERVATION_PREFIX):
            continue
        try:
            payload = json.loads(line.removeprefix(_OBSERVATION_PREFIX))
        except json.JSONDecodeError:
            return None
        return payload if isinstance(payload, dict) else None
    return None


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted(str(item) for item in value if isinstance(item, str))


def _bounded_detail(value: str) -> str:
    return " ".join(value.split())[:300]


def _not_observed(reason: str, *, detail: str = "", env: dict[str, str] | None = None) -> dict[str, Any]:
    return {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "observed": False,
        "ok": False,
        "reason": reason,
        "detail": detail,
        "registered_tools": [],
        "registered_hooks": [],
        "expected_tools": sorted(PROVIDED_TOOLS),
        "expected_hooks": sorted(PROVIDED_HOOKS),
        "environment": env or {},
    }


__all__ = ["OBSERVATION_SCHEMA_VERSION", "observe_real_loader_registration", "resolve_hermes_code_root"]
