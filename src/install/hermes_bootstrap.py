"""Detect and optionally install the Hermes runtime that OMJ wraps.

OMJ is a Hermes-native wrapper orchestration layer. It does not patch Hermes
core, but it can run the official upstream Hermes installer on explicit opt-in so
a fresh machine can reach a working ``hermes`` runtime that OMJ then wraps.

This module preserves the prepared-vs-observed boundary:

* ``build_hermes_install_plan`` only prepares the upstream install command. It
  never executes anything and never mutates the system.
* ``run_hermes_install`` is the opt-in path that actually executes the upstream
  installer and records observed evidence of that execution.

Installing the Hermes runtime is not OMJ skill setup, plugin load, review, CI,
or merge evidence. Those remain separate, separately observed steps.
"""

from __future__ import annotations

import shutil
import sys
from typing import Callable

from .release_smoke_core import CommandResult, Runner, bounded_text, subprocess_runner

HERMES_BOOTSTRAP_SCHEMA = "hermes_bootstrap/v1"

# Upstream Hermes runtime that OMJ wraps (MIT, NousResearch/hermes-agent).
HERMES_UPSTREAM_REPO = "https://github.com/NousResearch/hermes-agent"
HERMES_PYPI_PACKAGE = "hermes-agent"
HERMES_INSTALL_SCRIPT_URL = "https://hermes-agent.nousresearch.com/install.sh"
HERMES_INSTALL_PS_URL = "https://hermes-agent.nousresearch.com/install.ps1"
HERMES_PYTHON_REQUIREMENT = ">=3.11,<3.14"

INSTALL_METHODS = ("script", "pip")
DEFAULT_INSTALL_METHOD = "script"

WhichFn = Callable[[str], str | None]

PLAN_PROOF_BOUNDARY = (
    "Prepared Hermes install command only. No installer was executed and no "
    "system state was changed; the Hermes runtime is not installed or observed "
    "by this output. Run `omj hermes install --apply` to execute the upstream "
    "installer."
)
APPLY_PROOF_BOUNDARY = (
    "Observed execution of the upstream Hermes installer. Installing the Hermes "
    "runtime is not OMJ skill setup, plugin load, review, CI, or merge evidence; "
    "those remain separate, separately observed steps."
)
DETECT_PROOF_BOUNDARY = (
    "Observed local detection of the `hermes` runtime only. Presence of the CLI "
    "is not OMJ skill setup, plugin load, review, CI, or merge evidence."
)


def _is_windows(platform: str) -> bool:
    return platform.startswith("win")


def detect_hermes(
    *,
    runner: Runner | None = None,
    which: WhichFn = shutil.which,
    timeout_seconds: int = 15,
) -> dict[str, object]:
    """Detect whether the ``hermes`` runtime CLI is installed locally.

    Presence is resolved via ``which``. When present, a read-only
    ``hermes --version`` is executed through ``runner`` to capture the version.
    """

    path = which("hermes")
    found = bool(path)
    version = ""
    version_ok = False
    if found:
        execute = runner or subprocess_runner
        result = execute(["hermes", "--version"], timeout_seconds, None)
        if result.returncode == 0:
            version_ok = True
            version = (result.stdout.strip() or result.stderr.strip()).splitlines()[0] if (result.stdout.strip() or result.stderr.strip()) else ""
    return {
        "schema_version": HERMES_BOOTSTRAP_SCHEMA,
        "found": found,
        "path": path,
        "version": version,
        "version_probe_ok": version_ok,
        "pypi_package": HERMES_PYPI_PACKAGE,
        "upstream_repo": HERMES_UPSTREAM_REPO,
        "python_requirement": HERMES_PYTHON_REQUIREMENT,
        "observed": True,
        "proof_boundary": DETECT_PROOF_BOUNDARY,
    }


def _install_command(method: str, *, platform: str) -> tuple[list[str], str, str]:
    """Return (command, display, source_ref) for an install method."""

    if method not in INSTALL_METHODS:
        raise ValueError(f"unknown Hermes install method: {method!r}; choose from {INSTALL_METHODS}")
    if method == "pip":
        command = [sys.executable, "-m", "pip", "install", "--upgrade", HERMES_PYPI_PACKAGE]
        display = " ".join(command)
        return command, display, HERMES_PYPI_PACKAGE
    # method == "script": run the official upstream installer.
    if _is_windows(platform):
        display = f"iex (irm {HERMES_INSTALL_PS_URL})"
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            f"iex (irm {HERMES_INSTALL_PS_URL})",
        ]
        return command, display, HERMES_INSTALL_PS_URL
    display = f"curl -fsSL {HERMES_INSTALL_SCRIPT_URL} | bash"
    command = ["bash", "-c", f"curl -fsSL {HERMES_INSTALL_SCRIPT_URL} | bash"]
    return command, display, HERMES_INSTALL_SCRIPT_URL


def build_hermes_install_plan(
    method: str = DEFAULT_INSTALL_METHOD,
    *,
    platform: str | None = None,
    which: WhichFn = shutil.which,
    runner: Runner | None = None,
) -> dict[str, object]:
    """Prepare the upstream Hermes install command without executing anything."""

    resolved_platform = platform if platform is not None else sys.platform
    command, display, source_ref = _install_command(method, platform=resolved_platform)
    presence = detect_hermes(which=which, runner=runner)
    return {
        "schema_version": HERMES_BOOTSTRAP_SCHEMA,
        "mode": "plan",
        "method": method,
        "platform": resolved_platform,
        "command": command,
        "command_display": display,
        "source_ref": source_ref,
        "upstream_repo": HERMES_UPSTREAM_REPO,
        "python_requirement": HERMES_PYTHON_REQUIREMENT,
        "already_present": bool(presence["found"]),
        "detected": presence,
        "executed": False,
        "observed": False,
        "proof_boundary": PLAN_PROOF_BOUNDARY,
    }


def run_hermes_install(
    method: str = DEFAULT_INSTALL_METHOD,
    *,
    platform: str | None = None,
    runner: Runner | None = None,
    which: WhichFn = shutil.which,
    timeout_seconds: int = 1200,
    force: bool = False,
) -> dict[str, object]:
    """Execute the upstream Hermes installer (opt-in, mutating, observed).

    When Hermes is already present and ``force`` is False, this is a no-op that
    reports the existing runtime without executing the installer.
    """

    resolved_platform = platform if platform is not None else sys.platform
    command, display, source_ref = _install_command(method, platform=resolved_platform)
    before = detect_hermes(which=which, runner=runner)
    base: dict[str, object] = {
        "schema_version": HERMES_BOOTSTRAP_SCHEMA,
        "mode": "apply",
        "method": method,
        "platform": resolved_platform,
        "command": command,
        "command_display": display,
        "source_ref": source_ref,
        "upstream_repo": HERMES_UPSTREAM_REPO,
        "python_requirement": HERMES_PYTHON_REQUIREMENT,
        "detected_before": before,
        "proof_boundary": APPLY_PROOF_BOUNDARY,
    }
    if before["found"] and not force:
        base.update(
            {
                "executed": False,
                "observed": False,
                "ok": True,
                "already_present": True,
                "detected": before,
            }
        )
        return base
    execute = runner or subprocess_runner
    result: CommandResult = execute(command, timeout_seconds, None)
    after = detect_hermes(which=which, runner=runner)
    base.update(
        {
            "executed": True,
            "observed": True,
            "already_present": bool(before["found"]),
            "returncode": result.returncode,
            "stdout": bounded_text(result.stdout),
            "stderr": bounded_text(result.stderr),
            "ok": result.returncode == 0 and bool(after["found"]),
            "detected": after,
        }
    )
    return base
