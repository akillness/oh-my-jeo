from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOSTS = ("claude", "codex", "cursor", "openclaw", "opencode", "pi")


def _run_cli(workspace: Path, *args: str, env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "tests"), str(ROOT / "src")))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["OMJ_OUTPUT"] = "json"
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "-m", "omj.cli", *args],
        cwd=workspace,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _payload(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    if result.returncode != 0:
        raise AssertionError(f"CLI failed ({result.returncode}): {result.stderr}")
    return json.loads(result.stdout)


class HostAdapterContractTests(unittest.TestCase):
    def test_each_host_install_uses_its_declared_local_layout_and_receipt(self) -> None:
        with TemporaryDirectory() as tmp:
            for host in HOSTS:
                with self.subTest(host=host):
                    workspace = Path(tmp) / host
                    workspace.mkdir()
                    result = _run_cli(
                        workspace,
                        "install",
                        "--target",
                        "agents",
                        "--host",
                        host,
                        "--scope",
                        "project",
                        "--json",
                    )
                    payload = _payload(result)
                    expected_root = workspace / (".claude" if host == "claude" else ".agents") / "skills"
                    self.assertEqual(payload["projection"], "fresh")
                    self.assertEqual(Path(payload["target_dirs"][0]).resolve(), expected_root.resolve())
                    receipt = expected_root / ".omj-agent-skills-manifest.json"
                    self.assertTrue(receipt.is_file())
                    manifest = json.loads(receipt.read_text(encoding="utf-8"))
                    self.assertEqual(manifest["schema_version"], "omj_agent_skills_projection/v1")
                    self.assertTrue(manifest["files"])
                    self.assertEqual(payload["host_adapter"]["host"], host)
                    self.assertEqual(payload["host_adapter"]["transform"], "copy-only")
                    self.assertEqual(payload["host_adapter"]["schema_version"], "omj_host_adapter/v1")
                    self.assertEqual(payload["host_adapter"]["source"], "agent-skills")
                    self.assertEqual(payload["host_adapter"]["digest_format"], "sha256(sorted '<file-sha256>  <relative-posix-path>\\n' UTF-8 inventory)")
                    self.assertEqual(payload["host_adapter"]["evidence"], "docs/AGENT-SKILLS.md#host-support-matrix")
                    caveat = str(payload["host_adapter"].get("caveat", ""))
                    if host == "claude":
                        self.assertIn("Historical upstream OMH repo discovery", caveat)
                        self.assertIn("OMJ repo discovery not_observed", caveat)
                        self.assertIn("not workflow execution", caveat)
                    self.assertTrue(payload["host_adapter"]["source_digest"])
                    self.assertEqual(payload["host_adapter"]["files"], manifest["files"])
                    self.assertEqual(payload["host_adapter"]["targets"]["repo"], ".claude/skills" if host == "claude" else ".agents/skills")
                    self.assertEqual(payload["host_observation"], "not_observed")
                    self.assertIn("not prove host discovery", payload["claim_boundary"])
                    installed_files = [path for path in workspace.rglob("*") if path.is_file()]
                    self.assertTrue(installed_files)
                    self.assertTrue(all(path.is_relative_to(expected_root) for path in installed_files))
                    self.assertFalse((workspace / ".omj").exists())
                    self.assertFalse((workspace / ".hermes").exists())

    def test_each_host_user_install_writes_only_isolated_home_and_status_is_fresh(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for host in HOSTS:
                with self.subTest(host=host):
                    workspace = root / f"workspace-{host}"
                    home = root / f"home-{host}"
                    workspace.mkdir()
                    home.mkdir()
                    env = {"HOME": str(home), "USERPROFILE": str(home)}
                    result = _run_cli(
                        workspace,
                        "install",
                        "--target",
                        "agents",
                        "--host",
                        host,
                        "--scope",
                        "user",
                        "--json",
                        env_overrides=env,
                    )
                    payload = _payload(result)
                    expected_root = home / (".claude" if host == "claude" else ".agents") / "skills"
                    self.assertEqual(payload["projection"], "fresh")
                    self.assertEqual(Path(payload["target_dirs"][0]).resolve(), expected_root.resolve())
                    receipt = expected_root / ".omj-agent-skills-manifest.json"
                    self.assertTrue(receipt.is_file())
                    manifest = json.loads(receipt.read_text(encoding="utf-8"))
                    self.assertEqual(manifest["target_dirs"], [str(expected_root.resolve())])
                    self.assertEqual(manifest["files"], payload["host_adapter"]["files"])
                    self.assertEqual(payload["host_observation"], "not_observed")
                    self.assertEqual(list(workspace.rglob("*")), [])
                    status = _run_cli(
                        workspace,
                        "install",
                        "--target",
                        "agents",
                        "--host",
                        host,
                        "--scope",
                        "user",
                        "--status",
                        "--json",
                        env_overrides=env,
                    )
                    status_payload = _payload(status)
                    self.assertEqual(status_payload["projection"], "fresh")
                    self.assertEqual(status_payload["drift"], "clean")

    def test_dry_run_and_status_are_read_only_for_every_host(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            for host in HOSTS:
                with self.subTest(host=host):
                    dry_run = _run_cli(
                        workspace,
                        "install",
                        "--target",
                        "agents",
                        "--host",
                        host,
                        "--scope",
                        "project",
                        "--dry-run",
                        "--json",
                    )
                    self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
                    self.assertEqual(list(workspace.rglob("*")), [])
                    status = _run_cli(
                        workspace,
                        "install",
                        "--target",
                        "agents",
                        "--host",
                        host,
                        "--scope",
                        "project",
                        "--status",
                        "--json",
                    )
                    self.assertEqual(status.returncode, 0, status.stderr)
                    self.assertEqual(list(workspace.rglob("*")), [])
                    self.assertEqual(_payload(status)["projection"], "missing")

    def test_reinstall_is_byte_idempotent_and_preserves_foreign_skills(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            foreign = workspace / ".agents" / "skills" / "foreign-skill" / "SKILL.md"
            foreign.parent.mkdir(parents=True)
            foreign.write_text("foreign host-owned skill\n", encoding="utf-8")
            first = _payload(
                _run_cli(workspace, "install", "--target", "agents", "--host", "codex", "--scope", "project", "--json")
            )
            root = workspace / ".agents" / "skills"
            before = {
                path.relative_to(workspace).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in workspace.rglob("*")
                if path.is_file()
            }
            second = _payload(
                _run_cli(workspace, "install", "--target", "agents", "--host", "codex", "--scope", "project", "--json")
            )
            after = {
                path.relative_to(workspace).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in workspace.rglob("*")
                if path.is_file()
            }
            self.assertEqual(first["catalog_revision"], second["catalog_revision"])
            self.assertEqual(before, after)
            self.assertEqual(foreign.read_text(encoding="utf-8"), "foreign host-owned skill\n")
            self.assertEqual(second["drift"], "clean")
            self.assertEqual(second["projection"], "fresh")
            self.assertTrue((root / ".omj-agent-skills-manifest.json").is_file())

    def test_edited_owned_file_refuses_without_partial_write(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            _payload(_run_cli(workspace, "install", "--target", "agents", "--host", "cursor", "--scope", "project", "--json"))
            root = workspace / ".agents" / "skills"
            manifest_path = root / ".omj-agent-skills-manifest.json"
            manifest_before = manifest_path.read_bytes()
            relative = next(iter(json.loads(manifest_path.read_text(encoding="utf-8"))["files"]))
            edited = root / relative
            edited.write_text("locally edited and must not be replaced\n", encoding="utf-8")
            result = _run_cli(workspace, "install", "--target", "agents", "--host", "cursor", "--scope", "project", "--json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("modified", result.stderr.lower())
            self.assertEqual(edited.read_text(encoding="utf-8"), "locally edited and must not be replaced\n")
            self.assertEqual(manifest_path.read_bytes(), manifest_before)

    def test_unknown_collision_symlink_and_path_escape_refuse_before_writing(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            # An unowned collision at a generated destination must preflight before any write.
            projection = workspace / "projection"
            docs = _run_cli(workspace, "docs", "agent-skills", "--output", str(projection))
            self.assertEqual(docs.returncode, 0, docs.stderr)
            relative = next(path.relative_to(projection) for path in projection.rglob("SKILL.md"))
            collision = workspace / ".agents" / "skills" / relative
            collision.parent.mkdir(parents=True)
            collision.write_text("unowned\n", encoding="utf-8")
            snapshot = {path.relative_to(workspace).as_posix(): path.read_bytes() for path in workspace.rglob("*") if path.is_file()}
            result = _run_cli(workspace, "install", "--target", "agents", "--host", "openclaw", "--scope", "project", "--json")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(snapshot, {path.relative_to(workspace).as_posix(): path.read_bytes() for path in workspace.rglob("*") if path.is_file()})

            # A symlinked host root cannot redirect an authorized install.
            symlink_workspace = workspace / "symlink-case"
            symlink_workspace.mkdir()
            outside = workspace / "outside"
            outside.mkdir()
            (symlink_workspace / ".agents").symlink_to(outside, target_is_directory=True)
            result = _run_cli(symlink_workspace, "install", "--target", "agents", "--host", "pi", "--scope", "project", "--dry-run", "--json")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(outside.rglob("*")), [])

            # A path escape introduced into the owned receipt is rejected before writes.
            clean_workspace = workspace / "escape-case"
            clean_workspace.mkdir()
            _payload(_run_cli(clean_workspace, "install", "--target", "agents", "--host", "opencode", "--scope", "project", "--json"))
            receipt = clean_workspace / ".agents" / "skills" / ".omj-agent-skills-manifest.json"
            manifest = json.loads(receipt.read_text(encoding="utf-8"))
            manifest["files"]["../escaped.md"] = "0" * 64
            receipt.write_text(json.dumps(manifest), encoding="utf-8")
            result = _run_cli(clean_workspace, "install", "--target", "agents", "--host", "opencode", "--scope", "project", "--status", "--json")
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((clean_workspace / "escaped.md").exists())


if __name__ == "__main__":
    unittest.main()
