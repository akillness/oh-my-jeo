from __future__ import annotations

import json
import unittest

from _local_package import load_local_package

load_local_package()

from _cli_harness import run_cli

from omj.hermes_bootstrap import (
    APPLY_PROOF_BOUNDARY,
    DEFAULT_INSTALL_METHOD,
    HERMES_BOOTSTRAP_SCHEMA,
    HERMES_INSTALL_PS_URL,
    HERMES_INSTALL_SCRIPT_URL,
    HERMES_PYPI_PACKAGE,
    PLAN_PROOF_BOUNDARY,
    build_hermes_install_plan,
    detect_hermes,
    run_hermes_install,
)
from omj.release_smoke_core import CommandResult


def _absent_which(_name: str) -> None:
    return None


def _present_which(path: str = "/usr/local/bin/hermes"):
    def which(_name: str) -> str:
        return path

    return which


class DetectHermesTests(unittest.TestCase):
    def test_absent_runtime_reports_not_found_without_running_version_probe(self) -> None:
        calls: list[list[str]] = []

        def runner(command, _timeout, _env):
            calls.append(list(command))
            return CommandResult(command, 0, "", "")

        result = detect_hermes(which=_absent_which, runner=runner)

        self.assertFalse(result["found"])
        self.assertIsNone(result["path"])
        self.assertEqual(result["version"], "")
        self.assertFalse(result["version_probe_ok"])
        self.assertTrue(result["observed"])
        self.assertEqual(result["schema_version"], HERMES_BOOTSTRAP_SCHEMA)
        self.assertEqual(result["pypi_package"], HERMES_PYPI_PACKAGE)
        self.assertEqual(calls, [], "version probe must not run when the CLI is absent")

    def test_present_runtime_captures_first_version_line(self) -> None:
        seen: list[list[str]] = []

        def runner(command, _timeout, _env):
            seen.append(list(command))
            return CommandResult(command, 0, "hermes 0.17.0\nextra noise\n", "")

        result = detect_hermes(which=_present_which(), runner=runner)

        self.assertTrue(result["found"])
        self.assertEqual(result["path"], "/usr/local/bin/hermes")
        self.assertEqual(result["version"], "hermes 0.17.0")
        self.assertTrue(result["version_probe_ok"])
        self.assertEqual(seen, [["hermes", "--version"]])

    def test_present_runtime_with_failing_probe_reports_no_version(self) -> None:
        def runner(command, _timeout, _env):
            return CommandResult(command, 1, "", "boom")

        result = detect_hermes(which=_present_which(), runner=runner)

        self.assertTrue(result["found"])
        self.assertFalse(result["version_probe_ok"])
        self.assertEqual(result["version"], "")


class InstallPlanTests(unittest.TestCase):
    def test_posix_script_plan_is_non_executing_and_uses_official_installer(self) -> None:
        plan = build_hermes_install_plan("script", platform="linux", which=_absent_which)

        self.assertEqual(plan["mode"], "plan")
        self.assertFalse(plan["executed"])
        self.assertFalse(plan["observed"])
        self.assertFalse(plan["already_present"])
        self.assertEqual(plan["command"], ["bash", "-c", f"curl -fsSL {HERMES_INSTALL_SCRIPT_URL} | bash"])
        self.assertEqual(plan["source_ref"], HERMES_INSTALL_SCRIPT_URL)
        self.assertEqual(plan["proof_boundary"], PLAN_PROOF_BOUNDARY)

    def test_windows_script_plan_uses_powershell_installer(self) -> None:
        plan = build_hermes_install_plan("script", platform="win32", which=_absent_which)

        self.assertIn("powershell", plan["command"])
        self.assertEqual(plan["command_display"], f"iex (irm {HERMES_INSTALL_PS_URL})")
        self.assertEqual(plan["source_ref"], HERMES_INSTALL_PS_URL)

    def test_pip_plan_targets_pypi_package(self) -> None:
        plan = build_hermes_install_plan("pip", platform="linux", which=_absent_which)

        self.assertIn("-m", plan["command"])
        self.assertIn("pip", plan["command"])
        self.assertIn(HERMES_PYPI_PACKAGE, plan["command"])
        self.assertEqual(plan["source_ref"], HERMES_PYPI_PACKAGE)

    def test_plan_reports_already_present_when_runtime_detected(self) -> None:
        plan = build_hermes_install_plan("script", platform="linux", which=_present_which())
        self.assertTrue(plan["already_present"])

    def test_unknown_method_raises(self) -> None:
        with self.assertRaises(ValueError):
            build_hermes_install_plan("brew", platform="linux", which=_absent_which)


class RunInstallTests(unittest.TestCase):
    def test_already_present_is_a_no_op_without_executing_installer(self) -> None:
        calls: list[list[str]] = []

        def runner(command, _timeout, _env):
            calls.append(list(command))
            return CommandResult(command, 0, "", "")

        result = run_hermes_install("script", platform="linux", which=_present_which(), runner=runner)

        self.assertTrue(result["ok"])
        self.assertTrue(result["already_present"])
        self.assertFalse(result["executed"])
        # Only the version probe in detect ran; the installer command did not.
        self.assertNotIn(["bash", "-c", f"curl -fsSL {HERMES_INSTALL_SCRIPT_URL} | bash"], calls)

    def test_successful_install_executes_installer_and_observes_runtime(self) -> None:
        states = {"installed": False}
        seen: list[list[str]] = []

        def which(_name: str):
            return "/usr/local/bin/hermes" if states["installed"] else None

        def runner(command, _timeout, _env):
            cmd = list(command)
            seen.append(cmd)
            if cmd[0] == "bash":
                states["installed"] = True
                return CommandResult(command, 0, "installed hermes", "")
            return CommandResult(command, 0, "hermes 0.17.0", "")

        result = run_hermes_install("script", platform="linux", which=which, runner=runner)

        self.assertTrue(result["executed"])
        self.assertTrue(result["observed"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["returncode"], 0)
        self.assertTrue(result["detected"]["found"])
        self.assertEqual(result["proof_boundary"], APPLY_PROOF_BOUNDARY)
        self.assertIn(["bash", "-c", f"curl -fsSL {HERMES_INSTALL_SCRIPT_URL} | bash"], seen)

    def test_failed_install_is_not_ok_even_with_zero_returncode_when_runtime_absent(self) -> None:
        def which(_name: str):
            return None  # installer "succeeds" but runtime never appears.

        def runner(command, _timeout, _env):
            return CommandResult(command, 0, "noop", "")

        result = run_hermes_install("script", platform="linux", which=which, runner=runner)

        self.assertTrue(result["executed"])
        self.assertFalse(result["ok"])

    def test_failed_installer_returncode_is_not_ok(self) -> None:
        def runner(command, _timeout, _env):
            return CommandResult(command, 1, "", "network error")

        result = run_hermes_install("script", platform="linux", which=_absent_which, runner=runner)

        self.assertTrue(result["executed"])
        self.assertEqual(result["returncode"], 1)
        self.assertFalse(result["ok"])


class HermesCliTests(unittest.TestCase):
    def test_hermes_status_emits_detection_payload(self) -> None:
        status, out, _ = run_cli(["hermes", "status"])
        self.assertEqual(status, 0)
        payload = json.loads(out)
        self.assertEqual(payload["schema_version"], HERMES_BOOTSTRAP_SCHEMA)
        self.assertIn("found", payload)
        self.assertIn("Presence of the CLI is not", payload["proof_boundary"])

    def test_hermes_install_defaults_to_plan_only(self) -> None:
        status, out, _ = run_cli(["hermes", "install"])
        self.assertEqual(status, 0)
        payload = json.loads(out)
        self.assertEqual(payload["mode"], "plan")
        self.assertFalse(payload["executed"])
        self.assertEqual(payload["method"], DEFAULT_INSTALL_METHOD)
        self.assertIn("No installer was executed", payload["proof_boundary"])

    def test_hermes_install_plan_pip_method(self) -> None:
        status, out, _ = run_cli(["hermes", "install", "--method", "pip"])
        self.assertEqual(status, 0)
        payload = json.loads(out)
        self.assertEqual(payload["method"], "pip")
        self.assertIn(HERMES_PYPI_PACKAGE, payload["command"])


class DoctorHermesCheckTests(unittest.TestCase):
    def test_doctor_warns_when_hermes_runtime_absent(self) -> None:
        from unittest.mock import patch

        from omj.maintenance import doctor as doctor_module
        from omj.paths import resolve_paths

        absent = {
            "schema_version": HERMES_BOOTSTRAP_SCHEMA,
            "found": False,
            "path": None,
            "version": "",
            "observed": True,
        }
        with patch.object(doctor_module, "detect_hermes", return_value=absent):
            checks = doctor_module.run_doctor(resolve_paths(None, None))
        check = next(c for c in checks if c.name == "hermes_runtime")
        self.assertTrue(check.ok)
        self.assertEqual(check.severity, "warning")
        self.assertIn("omj hermes install", check.message)
        self.assertIn("omj hermes install --apply", check.next_action)

    def test_doctor_reports_ok_when_hermes_runtime_present(self) -> None:
        from unittest.mock import patch

        from omj.maintenance import doctor as doctor_module
        from omj.paths import resolve_paths

        present = {
            "schema_version": HERMES_BOOTSTRAP_SCHEMA,
            "found": True,
            "path": "/usr/local/bin/hermes",
            "version": "hermes 0.17.0",
            "observed": True,
        }
        with patch.object(doctor_module, "detect_hermes", return_value=present):
            checks = doctor_module.run_doctor(resolve_paths(None, None))
        check = next(c for c in checks if c.name == "hermes_runtime")
        self.assertEqual(check.severity, "ok")
        self.assertIn("/usr/local/bin/hermes", check.message)
        self.assertIn("0.17.0", check.message)
        self.assertEqual(check.next_action, "")


class SetupWithHermesTests(unittest.TestCase):
    def _args(self, **overrides):
        import argparse

        namespace = argparse.Namespace(
            with_hermes=False,
            hermes_method=DEFAULT_INSTALL_METHOD,
            dry_run=False,
        )
        for key, value in overrides.items():
            setattr(namespace, key, value)
        return namespace

    def test_setup_without_flag_only_detects_runtime(self) -> None:
        from omj.commands.setup import _hermes_runtime_setup_result

        result = _hermes_runtime_setup_result(self._args())
        self.assertEqual(result["status"], "not_requested")
        self.assertFalse(result["requested"])
        self.assertFalse(result["executed"])
        self.assertIn("detected", result)
        self.assertIn("--with-hermes", result["proof_boundary"])

    def test_setup_with_flag_in_dry_run_only_plans(self) -> None:
        from omj.commands.setup import _hermes_runtime_setup_result

        result = _hermes_runtime_setup_result(self._args(with_hermes=True, dry_run=True))
        self.assertEqual(result["status"], "would_install")
        self.assertTrue(result["requested"])
        self.assertFalse(result["executed"])
        self.assertEqual(result["mode"], "plan")


if __name__ == "__main__":
    unittest.main()
