from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import textwrap
import unittest
from typing import Mapping, Sequence

from _local_package import load_local_package

load_local_package()

from omj.release_smoke_core import CommandResult, subprocess_runner_exact_env


ROOT = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = ROOT / "install.sh"


class InstallScriptContractTests(unittest.TestCase):
    def test_default_installer_is_command_only(self) -> None:
        """The no-consent path installs the command without setup, Hermes, or network bootstrap."""
        with tempfile.TemporaryDirectory(prefix="omj-install-contract-") as temp:
            root = Path(temp)
            fixture = _InstallerFixture(root)
            before = _snapshot_roots(fixture.mutable_roots)
            result, commands = fixture.run()
            after = _snapshot_roots(fixture.mutable_roots)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(commands[0], ["sh", str(INSTALL_SCRIPT)])
            self.assertEqual(
                [command[1:] for command in fixture.python_commands()],
                [
                    ["-m", "venv", str(fixture.venv)],
                    ["-m", "pip", "install", "--disable-pip-version-check", "-q", "--force-reinstall", "--upgrade", str(fixture.package)],
                ],
            )
            self.assertEqual(before.get("home", {}), after.get("home", {}))
            self.assertNotIn("setup", fixture.omj_cli_subcommands())
            self.assertNotIn("doctor", fixture.omj_cli_subcommands())
            self.assertFalse((fixture.home / ".omj").exists())
            self.assertFalse((fixture.home / ".hermes").exists())
            self.assertNotIn("curl", fixture.all_command_text())
            self.assertNotIn("uv", fixture.all_command_text())

    def test_run_setup_does_not_imply_hermes_bootstrap(self) -> None:
        """Explicit OMJ_RUN_SETUP requests ordinary setup, not the autopilot/Hermes opt-in."""
        with tempfile.TemporaryDirectory(prefix="omj-install-contract-") as temp:
            fixture = _InstallerFixture(Path(temp))
            result, _commands = fixture.run({"OMJ_RUN_SETUP": "1"})

            self.assertEqual(result.returncode, 0, result.stderr)
            setup_commands = fixture.omj_cli_commands("setup")
            self.assertEqual(len(setup_commands), 1)
            self.assertNotIn("--autopilot", setup_commands[0])
            self.assertNotIn("--yes", setup_commands[0])
            self.assertEqual(len(fixture.omj_cli_commands("doctor")), 1)

    def test_autopilot_requires_explicit_environment_opt_in(self) -> None:
        """OMJ_AUTOPILOT=1 retains the deliberate one-shot setup flags."""
        with tempfile.TemporaryDirectory(prefix="omj-install-contract-") as temp:
            fixture = _InstallerFixture(Path(temp))
            result, _commands = fixture.run({"OMJ_AUTOPILOT": "1"})

            self.assertEqual(result.returncode, 0, result.stderr)
            setup_commands = fixture.omj_cli_commands("setup")
            self.assertEqual(len(setup_commands), 1)
            self.assertIn("--autopilot", setup_commands[0])
            self.assertIn("--yes", setup_commands[0])

    def test_python_floor_refused_before_venv(self) -> None:
        """An installed Python below 3.11 is rejected before the first filesystem write."""
        with tempfile.TemporaryDirectory(prefix="omj-install-contract-") as temp:
            fixture = _InstallerFixture(Path(temp), python_versions={"python3": "3.9"})
            before = _snapshot_roots(fixture.mutable_roots)
            result, _commands = fixture.run()
            after = _snapshot_roots(fixture.mutable_roots)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("3.9", result.stdout + result.stderr)
            self.assertEqual(before, after)
            self.assertEqual(fixture.python_commands(), [])

    def test_explicit_python_override_is_respected(self) -> None:
        """An explicitly named unsupported interpreter is refused, never replaced by another candidate."""
        with tempfile.TemporaryDirectory(prefix="omj-install-contract-") as temp:
            fixture = _InstallerFixture(
                Path(temp),
                python_versions={"python3": "3.12", "python-override": "3.9"},
            )
            override = fixture.python_bin / "python-override"
            result, commands = fixture.run({"OMJ_PYTHON": str(override)})

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("3.9", result.stdout + result.stderr)
            self.assertEqual(fixture.python_commands(), [])
            self.assertNotIn(str(fixture.python_bin / "python3"), fixture.all_command_text())

    def test_installed_supported_python_selected_without_provisioning(self) -> None:
        """When python3 is old, an installed versioned interpreter is selected without uv/download provisioning."""
        with tempfile.TemporaryDirectory(prefix="omj-install-contract-") as temp:
            fixture = _InstallerFixture(
                Path(temp),
                python_versions={"python3": "3.9", "python3.12": "3.12"},
                include_uv=True,
            )
            result, commands = fixture.run()

            self.assertEqual(result.returncode, 0, result.stderr)
            python_commands = fixture.python_commands()
            self.assertTrue(python_commands)
            self.assertEqual(python_commands[0][0], str(fixture.python_bin / "python3.12"))
            self.assertNotIn("uv", fixture.all_command_text())


class _InstallerFixture:
    def __init__(self, root: Path, *, python_versions: Mapping[str, str] | None = None, include_uv: bool = False) -> None:
        self.root = root
        self.home = root / "home"
        self.venv = root / "venv"
        self.bin = root / "bin"
        self.package = root / "local-package"
        self.python_bin = root / "fake-python"
        self.tool_bin = root / "host-tools"
        self.log = root / "python-calls.jsonl"
        self.mutable_roots = {"home": self.home, "venv": self.venv, "bin": self.bin}
        self._commands: list[list[str]] = []
        self.home.mkdir()
        self.package.mkdir()
        self.tool_bin.mkdir()
        for name in ("sh", "awk", "tr", "sed", "mkdir", "readlink", "ln", "dirname"):
            source = shutil.which(name)
            if source is None:
                raise RuntimeError(f"required host tool is unavailable: {name}")
            (self.tool_bin / name).symlink_to(source)
        versions = dict(python_versions or {"python3": "3.12"})
        for name, version in versions.items():
            _write_fake_python(self.python_bin / name, version, self.log)
        if include_uv:
            _write_fake_command(self.python_bin / "uv", self.log, "uv")

    def run(self, overrides: Mapping[str, str] | None = None) -> tuple[CommandResult, list[list[str]]]:
        env = {
            "HOME": str(self.home),
            "PATH": f"{self.python_bin}{os.pathsep}{self.tool_bin}",
            "PYTHONDONTWRITEBYTECODE": "1",
            "FAKE_PYTHON_LOG": str(self.log),
            "OMJ_CHANNEL": "local",
            "OMJ_PACKAGE_URL": str(self.package),
            "OMJ_SOURCE_REF": "local-contract-test",
            "OMJ_VENV_DIR": str(self.venv),
            "OMJ_BIN_DIR": str(self.bin),
            "OMJ_LINK_COMMAND": "1",
            "OMJ_FORCE_LINK": "1",
            "NO_COLOR": "1",
        }
        if overrides:
            env.update({key: str(value) for key, value in overrides.items()})

        def runner(command: Sequence[str], timeout: int, command_env: Mapping[str, str] | None) -> CommandResult:
            self._commands.append(list(command))
            return subprocess_runner_exact_env(command, timeout, command_env)

        result = runner(["sh", str(INSTALL_SCRIPT)], 30, env)
        return result, list(self._commands)

    def python_commands(self) -> list[list[str]]:
        records = self._read_log()
        return [
            [record["executable"], *record["argv"]]
            for record in records
            if record["argv"][:2] in (["-m", "venv"], ["-m", "pip"])
        ]

    def omj_cli_commands(self, subcommand: str) -> list[list[str]]:
        return [
            [record["executable"], *record["argv"]]
            for record in self._read_log()
            if record["argv"][:3] == ["-m", "omj.cli", subcommand]
        ]

    def omj_cli_subcommands(self) -> list[str]:
        return [record["argv"][2] for record in self._read_log() if record["argv"][:2] == ["-m", "omj.cli"] and len(record["argv"]) > 2]

    def all_command_text(self) -> str:
        records = self._read_log()
        return "\n".join(" ".join([record["executable"], *record["argv"]]) for record in records)

    def _read_log(self) -> list[dict[str, object]]:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]


def _write_fake_python(path: Path, version: str, log: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        textwrap.dedent(
            f"""\
            #!{sys.executable}
            import json
            import os
            from pathlib import Path
            import shutil
            import stat
            import sys

            version = {version!r}
            log = Path(os.environ["FAKE_PYTHON_LOG"])
            argv = sys.argv[1:]
            with log.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({{"executable": sys.argv[0], "argv": argv}}) + "\\n")

            if argv[:2] == ["-I", "-c"]:
                print(version)
                raise SystemExit(0)
            if argv[:2] == ["-m", "venv"]:
                venv = Path(argv[2])
                runtime = venv / "bin" / "python"
                runtime.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(Path(sys.argv[0]), runtime)
                runtime.chmod(runtime.stat().st_mode | stat.S_IXUSR)
                raise SystemExit(0)
            if argv[:2] == ["-m", "pip"]:
                command = Path(sys.argv[0]).parent / "omj"
                command.write_text("#!/bin/sh\\nexit 0\\n", encoding="utf-8")
                command.chmod(command.stat().st_mode | stat.S_IXUSR)
                raise SystemExit(0)
            if argv[:2] == ["-m", "omj.cli"]:
                raise SystemExit(0)
            raise SystemExit(0)
            """
        ),
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _write_fake_command(path: Path, log: Path, name: str) -> None:
    path.write_text(
        f"#!/bin/sh\nprintf '%s\\n' {name!r} >> {str(log)!r}\nexit 0\n",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _snapshot_roots(roots: Mapping[str, Path]) -> dict[str, dict[str, object]]:
    snapshots: dict[str, dict[str, object]] = {}
    for name, root in roots.items():
        entries: dict[str, object] = {}
        if root.exists():
            for path in sorted(root.rglob("*")):
                relative = str(path.relative_to(root))
                if path.is_symlink():
                    entries[relative] = ("symlink", os.readlink(path))
                elif path.is_file():
                    entries[relative] = ("file", path.read_bytes())
                else:
                    entries[relative] = ("dir",)
        snapshots[name] = entries
    return snapshots
