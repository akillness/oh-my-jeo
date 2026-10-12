from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOSTS = ("claude", "codex", "cursor", "openclaw", "opencode", "pi")
EXPECTED_PORTABILITY = {
    "cancel": "hermes-only",
    "skill": "hermes-only",
    "research-department": "hermes-only",
    "workflow-learning": "hermes-only",
    "doctor": "requires-omj-cli",
    "ultragoal": "requires-omj-cli",
    "loop": "requires-omj-cli",
    "automation-blueprint": "requires-omj-cli",
    "memory-curation-review": "requires-omj-cli",
    "agent-ops-review": "requires-omj-cli",
    "ultrawork": "requires-omj-cli",
}



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


def _files(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file()
    }


class AgentSkillsProjectionContractTests(unittest.TestCase):
    def test_docs_agent_skills_generates_namespaced_resources_and_all_host_assets(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            output = workspace / "portable"
            result = _run_cli(workspace, "docs", "agent-skills", "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            portable = _files(output)
            self.assertEqual(payload["file_count"], len(portable))
            self.assertGreater(payload["file_count"], 0)
            self.assertEqual(payload["adapter_file_count"], 18)
            self.assertTrue(any(path.endswith("/SKILL.md") for path in portable))
            self.assertTrue(any("/references/" in path for path in portable))
            for relative in portable:
                parts = Path(relative).parts
                self.assertGreaterEqual(len(parts), 2)
                self.assertIn(parts[1], {"SKILL.md", "references"})

            expected_adapters = {
                f".{host}/{suffix}"
                for host in HOSTS
                for suffix in ("install.sh", "install.ps1", "manifest.json")
            }
            actual_adapters = {
                path.relative_to(workspace).as_posix()
                for path in workspace.rglob("*")
                if path.is_file() and path.relative_to(workspace).as_posix().split("/", 1)[0] in {f".{host}" for host in HOSTS}
            }
            self.assertEqual(actual_adapters, expected_adapters)
            for host in HOSTS:
                manifest_path = workspace / f".{host}" / "manifest.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertEqual(manifest["host"], host)
                self.assertEqual(manifest["source"], "agent-skills")
                self.assertEqual(manifest["transform"], "copy-only")
                self.assertEqual(manifest["digest_format"], "sha256(sorted '<file-sha256>  <relative-posix-path>\\n' UTF-8 inventory)")
                self.assertEqual(manifest["files"], portable)

            check = _run_cli(workspace, "docs", "agent-skills", "--output", str(output), "--check")
            self.assertEqual(check.returncode, 0, check.stderr)
            self.assertTrue(json.loads(check.stdout)["ok"])

    def test_generated_posix_wrapper_executes_from_source_and_rejects_tamper(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            output = workspace / "agent-skills"
            generated = _run_cli(workspace, "docs", "agent-skills", "--output", str(output))
            self.assertEqual(generated.returncode, 0, generated.stderr)
            wrapper = workspace / ".codex" / "install.sh"
            first = subprocess.run(
                ["/bin/sh", str(wrapper)],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            target = workspace / ".agents" / "skills"
            receipt = target / ".omj-agent-skills-manifest.json"
            self.assertTrue(receipt.is_file())
            victim = next(path for path in target.rglob("SKILL.md") if path.is_file())
            victim_bytes = victim.read_bytes()
            receipt_bytes = receipt.read_bytes()
            before_reinstall = _files(target)
            reinstall = subprocess.run(
                ["/bin/sh", str(wrapper)],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(reinstall.returncode, 0, reinstall.stderr)
            self.assertEqual(before_reinstall, _files(target))
            outside = workspace / "outside.txt"
            outside.write_bytes(b"outside\n")
            victim.unlink()
            victim.symlink_to(outside)
            leaf_guard = subprocess.run(
                ["/bin/sh", str(wrapper)],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(leaf_guard.returncode, 0)
            self.assertTrue(victim.is_symlink())
            self.assertEqual(outside.read_bytes(), b"outside\n")
            victim.unlink()
            victim.write_bytes(victim_bytes)

            receipt.unlink()
            receipt.symlink_to(outside)
            receipt_guard = subprocess.run(
                ["/bin/sh", str(wrapper)],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(receipt_guard.returncode, 0)
            self.assertTrue(receipt.is_symlink())
            self.assertEqual(outside.read_bytes(), b"outside\n")
            receipt.unlink()
            receipt.write_bytes(receipt_bytes)
            before = _files(target)

            tampered = next(path for path in output.rglob("SKILL.md") if path.is_file())
            tampered.write_text(tampered.read_text(encoding="utf-8") + "\ntampered\n", encoding="utf-8")
            second = subprocess.run(
                ["/bin/sh", str(wrapper)],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(before, _files(target))
            self.assertTrue(receipt.is_file())
 
    def test_nondefault_output_wrapper_consumes_source_and_status_tracks_receipt(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            output = workspace / "portable bundle"
            generated = _run_cli(workspace, "docs", "agent-skills", "--output", str(output))
            self.assertEqual(generated.returncode, 0, generated.stderr)

            posix = workspace / ".codex" / "install.sh"
            powershell = workspace / ".codex" / "install.ps1"
            self.assertIn("source=$(dirname -- \"$0\")/../'portable bundle'", posix.read_text(encoding="utf-8"))
            self.assertIn("$source = Join-Path (Split-Path -Parent $PSScriptRoot) 'portable bundle'", powershell.read_text(encoding="utf-8"))

            installed = subprocess.run(
                ["/bin/sh", str(posix)],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)
            target = workspace / ".agents" / "skills"
            receipt = target / ".omj-agent-skills-manifest.json"
            self.assertTrue(receipt.is_file())
            source_bytes = {
                path.relative_to(output).as_posix(): path.read_bytes()
                for path in output.rglob("*")
                if path.is_file()
            }
            target_bytes = {
                path.relative_to(target).as_posix(): path.read_bytes()
                for path in target.rglob("*")
                if path.is_file() and path != receipt
            }
            self.assertEqual(target_bytes, source_bytes)
            manifest = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(
                manifest["files"],
                {relative: hashlib.sha256(content).hexdigest() for relative, content in source_bytes.items()},
            )

            fresh = _run_cli(
                workspace,
                "install",
                "--target",
                "agents",
                "--host",
                "codex",
                "--scope",
                "project",
                "--status",
                "--json",
            )
            self.assertEqual(fresh.returncode, 0, fresh.stderr)
            fresh_payload = json.loads(fresh.stdout)
            self.assertEqual(fresh_payload["projection"], "fresh")
            self.assertEqual(fresh_payload["drift"], "clean")

            victim = next(path for path in target.rglob("SKILL.md") if path.is_file())
            victim.write_bytes(victim.read_bytes() + b"tampered\n")
            stale = _run_cli(
                workspace,
                "install",
                "--target",
                "agents",
                "--host",
                "codex",
                "--scope",
                "project",
                "--status",
                "--json",
            )
            self.assertEqual(stale.returncode, 0, stale.stderr)
            stale_payload = json.loads(stale.stdout)
            self.assertEqual(stale_payload["projection"], "stale")
            self.assertEqual(stale_payload["drift"], "locally_modified")
            self.assertIn(victim.relative_to(target).as_posix(), stale_payload["locally_modified"])

    def test_generated_wrapper_receipt_is_fresh_to_cli_status_and_tamper_is_stale(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            output = workspace / "agent-skills"
            generated = _run_cli(workspace, "docs", "agent-skills", "--output", str(output))
            self.assertEqual(generated.returncode, 0, generated.stderr)
            wrapper = workspace / ".codex" / "install.sh"
            installed = subprocess.run(
                ["/bin/sh", str(wrapper)],
                cwd=workspace,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)

            status = _run_cli(
                workspace,
                "install",
                "--target",
                "agents",
                "--host",
                "codex",
                "--scope",
                "project",
                "--status",
                "--json",
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            payload = json.loads(status.stdout)
            self.assertEqual(payload["projection"], "fresh")
            self.assertEqual(payload["drift"], "clean")

            victim = next(path for path in (workspace / ".agents" / "skills").rglob("SKILL.md") if path.is_file())
            victim.write_bytes(victim.read_bytes() + b"tampered\n")
            stale = _run_cli(
                workspace,
                "install",
                "--target",
                "agents",
                "--host",
                "codex",
                "--scope",
                "project",
                "--status",
                "--json",
            )
            self.assertEqual(stale.returncode, 0, stale.stderr)
            stale_payload = json.loads(stale.stdout)
            self.assertEqual(stale_payload["projection"], "stale")
            self.assertEqual(stale_payload["drift"], "locally_modified")
            self.assertIn(victim.relative_to(workspace / ".agents" / "skills").as_posix(), stale_payload["locally_modified"])

    def test_portable_projection_classifies_inventory_and_neutralizes_included_content(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            output = workspace / "portable"
            generated = _run_cli(workspace, "docs", "agent-skills", "--output", str(output))
            self.assertEqual(generated.returncode, 0, generated.stderr)
            manifest = json.loads((workspace / ".codex" / "manifest.json").read_text(encoding="utf-8"))
            portability = manifest["portability"]
            self.assertEqual(set(portability.values()), {"portable", "requires-omj-cli", "hermes-only"})
            for name, classification in EXPECTED_PORTABILITY.items():
                self.assertEqual(portability[name], classification)
            self.assertEqual(
                {
                    name: classification
                    for name, classification in portability.items()
                    if classification == "hermes-only"
                },
                {name: "hermes-only" for name, classification in EXPECTED_PORTABILITY.items() if classification == "hermes-only"},
            )

            included = {
                path.parent.name.removeprefix("omj-"): path
                for path in output.glob("*/SKILL.md")
            }
            self.assertNotIn("cancel", included)
            self.assertNotIn("skill", included)
            self.assertNotIn("research-department", included)
            self.assertNotIn("workflow-learning", included)
            for canonical, classification in portability.items():
                folder = "omj" if canonical == "oh-my-jeo" else f"omj-{canonical}"
                if classification == "hermes-only":
                    self.assertFalse((output / folder).exists())
                    continue
                skill = output / folder / "SKILL.md"
                self.assertTrue(skill.is_file(), canonical)
                text = skill.read_text(encoding="utf-8")
                frontmatter, body = text.split("---", 2)[1:]
                self.assertIn(f"portability: {classification}", frontmatter)
                self.assertNotIn("metadata.hermes", frontmatter)
                for forbidden in (
                    "hermes skills tap",
                    "hermes skills install",
                    "skills.external_dirs",
                    "pre_llm_call",
                    "pre_tool_call",
                    "on_session_end",
                ):
                    self.assertNotIn(forbidden, body)

            provenance = output / "omj" / "references" / "native-provenance.md"
            provenance_text = provenance.read_text(encoding="utf-8")
            self.assertIn("# Native and Historical Provenance", provenance_text)
            self.assertIn(
                "These native contracts and historical source methods are non-operative provenance, not executable portable instructions.",
                provenance_text,
            )
            for reference in output.rglob("references/*.md"):
                skill_root = output / reference.relative_to(output).parts[0]
                self.assertTrue((skill_root / "SKILL.md").is_file(), reference)
                for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", reference.read_text(encoding="utf-8")):
                    target = link.split("#", 1)[0]
                    if not target or target.startswith(("http://", "https://", "mailto:", "/")):
                        continue
                    self.assertTrue((reference.parent / target).resolve().is_file(), f"{reference}: {link}")

            for wrapper in output.rglob("install.sh"):
                wrapper_text = wrapper.read_text(encoding="utf-8")
                for forbidden in ("pip install", "npm install", "brew install", "curl -fsSL"):
                    self.assertNotIn(forbidden, wrapper_text)

            from omj.skills.catalog import portable_skill_names, portability_for_skill

            self.assertEqual(
                set(portable_skill_names()),
                {name for name, classification in portability.items() if classification != "hermes-only"},
            )
            with self.assertRaises(ValueError):
                portability_for_skill("not-a-catalog-skill")
            procedural_clauses = {
                "ultrawork": ("disjoint lane ownership", "prepared_not_observed"),
                "loop": ("machine-decidable finish line", "per-item retry cap"),
                "ultraqa": ("adversarial scenarios", "fix-or-retry routing"),
                "agent-ops-review": ("agent ops review card", "prepared_not_observed"),
            }
            for name, clauses in procedural_clauses.items():
                body = (output / f"omj-{name}" / "SKILL.md").read_text(encoding="utf-8").lower()
                for clause in clauses:
                    self.assertIn(clause.lower(), body, name)
            for name in ("ultrawork", "loop", "ultraqa", "agent-ops-review"):
                body_path = output / f"omj-{name}" / "SKILL.md"
                reference_path = output / f"omj-{name}" / "references" / "procedures" / f"{name}.md"
                body = body_path.read_text(encoding="utf-8").lower()
                reference = reference_path.read_text(encoding="utf-8").lower()
                self.assertIn(f"references/procedures/{name}.md", body)
                for clause in ("source-owned", "conditional", "host-owned", "read-only"):
                    self.assertIn(clause, reference, name)
                self.assertNotIn("hermes skills install", reference)
                self.assertNotIn("skills.external_dirs", reference)

    def test_projection_is_byte_idempotent_and_check_detects_drift(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)

            output = workspace / "portable"
            first = _run_cli(workspace, "docs", "agent-skills", "--output", str(output))
            self.assertEqual(first.returncode, 0, first.stderr)
            before = _files(workspace)
            second = _run_cli(workspace, "docs", "agent-skills", "--output", str(output))
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(before, _files(workspace))

            edited = next(path for path in output.rglob("SKILL.md") if path.is_file())
            edited.write_text(edited.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
            stale = _run_cli(workspace, "docs", "agent-skills", "--output", str(output), "--check")
            self.assertNotEqual(stale.returncode, 0)
            self.assertEqual(edited.read_text(encoding="utf-8").splitlines()[-1], "local edit")

    def test_check_rejects_extra_and_symlinked_projection_files(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            output = workspace / "portable"
            result = _run_cli(workspace, "docs", "agent-skills", "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stderr)
            extra = output / "extra" / "SKILL.md"
            extra.parent.mkdir(parents=True)
            extra.write_text("unowned\n", encoding="utf-8")
            check = _run_cli(workspace, "docs", "agent-skills", "--output", str(output), "--check")
            self.assertNotEqual(check.returncode, 0)
            extra.unlink()

            source = output / "source.txt"
            source.write_text("outside\n", encoding="utf-8")
            linked = output / "linked" / "SKILL.md"
            linked.parent.mkdir(parents=True)
            linked.symlink_to(source)
            check = _run_cli(workspace, "docs", "agent-skills", "--output", str(output), "--check")
            self.assertNotEqual(check.returncode, 0)
            self.assertTrue(linked.is_symlink())


if __name__ == "__main__":
    unittest.main()
