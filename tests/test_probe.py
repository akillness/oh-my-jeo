from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()

from omj.catalogs.provider_auth import (
    PROVIDER_AUTH_CONTRACT_VERSION,
    PROVIDER_AUTH_DIAGNOSTIC_BOUNDARY,
)


class ProbeCliTests(unittest.TestCase):
    def test_probe_reports_unknown_and_missing_without_install(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            status, stdout, stderr = run_cli(["--omj-home", str(root / ".omj"), "--hermes-home", str(root / ".hermes"), "probe"])

            self.assertEqual(stderr, "")
            self.assertEqual(status, 0)
            payload = json.loads(stdout)
            caps = {capability["name"]: capability for capability in payload["capabilities"]}
            self.assertEqual(caps["external_skill_dirs"]["status"], "unknown")
            self.assertEqual(caps["managed_skills"]["status"], "missing")
            self.assertEqual(caps["native_hooks"]["status"], "unknown")
            self.assertEqual(caps["mcp_preference"]["status"], "unknown")
            self.assertEqual(caps["mcp_host_session"]["status"], "unverified")
            self.assertEqual(caps["mcp_host_config"]["status"], "unknown")
            self.assertEqual(caps["omj_plugin_bundle"]["status"], "missing")
            self.assertEqual(caps["plugin_import_smoke"]["status"], "unknown")
            self.assertEqual(caps["target_registry"]["status"], "missing")
            self.assertEqual(payload["target_topology"]["mode"], "unknown")
            self.assertFalse(payload["plugin_distribution_ready"])
            self.assertFalse(payload["native_integration_claim_ready"])

    def test_probe_roadmap_separates_product_setup_from_runtime_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = ["--omj-home", str(root / ".omj"), "--hermes-home", str(root / ".hermes")]

            status, stdout, stderr = run_cli(base + ["probe", "--roadmap", "--json"])

            self.assertEqual(stderr, "")
            self.assertEqual(status, 0)
            roadmap = json.loads(stdout)["capability_gap_roadmap"]
            self.assertEqual(roadmap["schema_version"], "omj_capability_gap_roadmap/v1")
            self.assertGreaterEqual(roadmap["summary"]["baseline_product_gaps"], 2)
            self.assertFalse(roadmap["summary"]["baseline_ready"])
            self.assertEqual(roadmap["next_actions"][0]["id"], "run_setup")
            self.assertIn("omj_plugin_bundle", roadmap["next_actions"][0]["capabilities"])
            self.assertIn("not workflow execution evidence", roadmap["next_actions"][0]["boundary"])

            self.assertEqual(run_cli(base + ["setup", "--with-plugin"])[0], 0)
            status, stdout, stderr = run_cli(base + ["probe", "--parity", "--json"])

            self.assertEqual(stderr, "")
            self.assertEqual(status, 0)
            payload = json.loads(stdout)
            roadmap = payload["capability_gap_roadmap"]
            self.assertTrue(roadmap["summary"]["baseline_ready"])
            self.assertEqual(roadmap["summary"]["baseline_product_gaps"], 0)
            self.assertGreaterEqual(roadmap["summary"]["evidence_gaps"], 1)
            self.assertIn("parity_matrix", payload)
            actions = {action["id"]: action for action in roadmap["next_actions"]}
            self.assertIn("observe_plugin_runtime", actions)
            self.assertIn("record_wrapper_usage", actions)
            self.assertIn("not coding execution", actions["observe_plugin_runtime"]["boundary"])
            self.assertNotIn("command", actions["record_wrapper_usage"])
            self.assertIn("operator_instruction", actions["record_wrapper_usage"])

    def test_probe_reports_available_local_evidence_after_install_and_wrapper_record(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            omj_home = root / ".omj"
            hermes_home = root / ".hermes"

            self.assertEqual(run_cli(["--omj-home", str(omj_home), "--hermes-home", str(hermes_home), "install"])[0], 0)
            self.assertEqual(run_cli(["--omj-home", str(omj_home), "--hermes-home", str(hermes_home), "apply"])[0], 0)
            status, stdout, _ = run_cli(
                [
                    "--omj-home",
                    str(omj_home),
                    "runtime",
                    "record",
                    "--skill",
                    "oh-my-jeo",
                    "--harness",
                    "coding-handling",
                ]
            )
            self.assertEqual(status, 0)
            run_id = json.loads(stdout)["run"]["run_id"]
            self.assertEqual(run_cli(["--omj-home", str(omj_home), "runtime", "wrapper", "--run", run_id, "--prompt-dispatched"])[0], 0)

            status, stdout, stderr = run_cli(["--omj-home", str(omj_home), "--hermes-home", str(hermes_home), "probe"])

            self.assertEqual(stderr, "")
            self.assertEqual(status, 0)
            caps = {capability["name"]: capability for capability in json.loads(stdout)["capabilities"]}
            self.assertEqual(caps["external_skill_dirs"]["status"], "available")
            self.assertEqual(caps["managed_skills"]["status"], "available")
            self.assertEqual(caps["wrapper_metadata"]["status"], "available")
            self.assertEqual(caps["omj_plugin_bundle"]["status"], "missing")
            self.assertEqual(caps["target_registry"]["status"], "missing")
            self.assertFalse(json.loads(stdout)["plugin_distribution_ready"])

            self.assertEqual(run_cli(["--omj-home", str(omj_home), "--hermes-home", str(hermes_home), "setup"])[0], 0)
            status, stdout, stderr = run_cli(["--omj-home", str(omj_home), "--hermes-home", str(hermes_home), "probe"])
            self.assertEqual(stderr, "")
            self.assertEqual(status, 0)
            payload = json.loads(stdout)
            caps = {capability["name"]: capability for capability in payload["capabilities"]}
            self.assertEqual(caps["target_registry"]["status"], "available")
            self.assertEqual(payload["target_topology"]["mode"], "single_agent_target")

    def test_probe_counts_wrapper_sessions_as_wrapper_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            omj_home = root / ".omj"
            hermes_home = root / ".hermes"
            base = ["--omj-home", str(omj_home), "--hermes-home", str(hermes_home)]

            self.assertEqual(run_cli(base + ["setup"])[0], 0)
            status, stdout, stderr = run_cli(
                base + ["chat", "session", "start", "--source", "discord", "I want to safely add a feature"]
            )

            self.assertEqual(stderr, "")
            self.assertEqual(status, 0)
            session = json.loads(stdout)["session"]
            self.assertTrue((omj_home / "runtime" / "wrapper_sessions" / session["session_id"] / "session.json").exists())

            status, stdout, stderr = run_cli(base + ["probe", "--roadmap", "--json"])

            self.assertEqual(stderr, "")
            self.assertEqual(status, 0)
            payload = json.loads(stdout)
            caps = {capability["name"]: capability for capability in payload["capabilities"]}
            self.assertEqual(caps["wrapper_metadata"]["status"], "available")
            actions = {action["id"] for action in payload["capability_gap_roadmap"]["next_actions"]}
            self.assertNotIn("record_wrapper_usage", actions)

    def test_probe_separates_mcp_preference_from_host_config(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            omj_home = root / ".omj"
            hermes_home = root / ".hermes"

            self.assertEqual(run_cli(["--omj-home", str(omj_home), "--hermes-home", str(hermes_home), "setup", "--with-mcp"])[0], 0)

            status, stdout, stderr = run_cli(["--omj-home", str(omj_home), "--hermes-home", str(hermes_home), "probe"])

            self.assertEqual(stderr, "")
            self.assertEqual(status, 0)
            payload = json.loads(stdout)
            caps = {capability["name"]: capability for capability in payload["capabilities"]}
            self.assertEqual(caps["mcp_preference"]["status"], "unverified")
            self.assertIn("bridge preference was requested", caps["mcp_preference"]["message"])
            self.assertIn("runtime/state.json", caps["mcp_preference"]["evidence"])
            self.assertEqual(caps["mcp_bridge_server"]["status"], "available")
            self.assertIn("omj_status", caps["mcp_bridge_server"]["message"])
            self.assertEqual(caps["mcp_bridge_runtime"]["status"], "unverified")
            self.assertEqual(caps["mcp_host_session"]["status"], "unverified")
            self.assertEqual(caps["mcp_host_config"]["status"], "unknown")
            self.assertIn("No Hermes MCP host config", caps["mcp_host_config"]["message"])
            self.assertFalse(payload["native_integration_claim_ready"])

            (hermes_home / ".mcp.json").write_text("{}", encoding="utf-8")
            status, stdout, stderr = run_cli(["--omj-home", str(omj_home), "--hermes-home", str(hermes_home), "probe"])

            self.assertEqual(stderr, "")
            self.assertEqual(status, 0)
            caps = {capability["name"]: capability for capability in json.loads(stdout)["capabilities"]}
            self.assertEqual(caps["mcp_preference"]["status"], "unverified")
            self.assertEqual(caps["mcp_host_config"]["status"], "unverified")
            self.assertIn("MCP host config exists", caps["mcp_host_config"]["message"])
            self.assertNotIn("mcp", {capability["name"] for capability in json.loads(stdout)["capabilities"]})

    def test_probe_reports_plugin_distribution_without_native_runtime_claim(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            omj_home = root / ".omj"
            hermes_home = root / ".hermes"

            self.assertEqual(run_cli(["--omj-home", str(omj_home), "--hermes-home", str(hermes_home), "setup", "--with-plugin"])[0], 0)

            status, stdout, stderr = run_cli(["--omj-home", str(omj_home), "--hermes-home", str(hermes_home), "probe"])

            self.assertEqual(stderr, "")
            self.assertEqual(status, 0)
            payload = json.loads(stdout)
            caps = {capability["name"]: capability for capability in payload["capabilities"]}
            self.assertIn("dedicated plugin capabilities", caps["plugin_bundles"]["message"])
            self.assertNotIn("no stable Hermes plugin bundle contract", caps["plugin_bundles"]["message"])
            self.assertEqual(caps["omj_plugin_bundle"]["status"], "available")
            self.assertEqual(caps["plugin_import_smoke"]["status"], "available")
            self.assertEqual(caps["plugin_register_smoke"]["status"], "available")
            self.assertEqual(caps["plugin_runtime_observed"]["status"], "unverified")
            self.assertTrue(payload["plugin_distribution_ready"])
            self.assertFalse(payload["native_integration_claim_ready"])

    def test_probe_roadmap_points_to_repair_for_broken_plugin_bridge(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            omj_home = root / ".omj"
            hermes_home = root / ".hermes"
            base = ["--omj-home", str(omj_home), "--hermes-home", str(hermes_home)]

            self.assertEqual(run_cli(base + ["setup", "--with-plugin"])[0], 0)
            (hermes_home / "plugins" / "omj" / "__init__.py").write_text("definitely not python: nope\n", encoding="utf-8")

            status, stdout, stderr = run_cli(base + ["probe", "--roadmap", "--json"])

            self.assertEqual(stderr, "")
            self.assertEqual(status, 0)
            payload = json.loads(stdout)
            caps = {capability["name"]: capability for capability in payload["capabilities"]}
            self.assertEqual(caps["omj_plugin_bundle"]["status"], "available")
            self.assertEqual(caps["plugin_import_smoke"]["status"], "missing")
            self.assertEqual(caps["plugin_register_smoke"]["status"], "missing")
            self.assertFalse(payload["plugin_distribution_ready"])
            roadmap = payload["capability_gap_roadmap"]
            self.assertEqual(roadmap["summary"]["baseline_product_gaps"], 2)
            actions = {action["id"]: action for action in roadmap["next_actions"]}
            self.assertIn("repair_plugin_bridge", actions)
            self.assertEqual(actions["repair_plugin_bridge"]["command"], "omj setup")
            self.assertEqual(actions["repair_plugin_bridge"]["fallback_command"], "omj setup --force")
            self.assertIn("not proof that Hermes loaded", actions["repair_plugin_bridge"]["boundary"])


class ProbeProviderAuthTests(unittest.TestCase):
    _MANAGED_ENV_KEYS = (
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GROQ_API_KEY",
        "OLLAMA_HOST",
        "LMSTUDIO_BASE_URL",
    )

    def _probe(self, env_overrides):
        saved = {key: os.environ.get(key) for key in self._MANAGED_ENV_KEYS}
        try:
            for key in self._MANAGED_ENV_KEYS:
                os.environ.pop(key, None)
            for key, value in env_overrides.items():
                os.environ[key] = value
            with TemporaryDirectory() as tmp:
                base = ["--omj-home", str(Path(tmp) / ".omj"), "--hermes-home", str(Path(tmp) / ".hermes")]
                status, stdout, stderr = run_cli(base + ["probe"])
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
        self.assertEqual(stderr, "")
        self.assertEqual(status, 0)
        return stdout, json.loads(stdout)

    def test_probe_surfaces_provider_auth_readiness_capability(self):
        stdout, payload = self._probe({})
        caps = {capability["name"]: capability for capability in payload["capabilities"]}
        self.assertIn("provider_auth_readiness", caps)
        cap = caps["provider_auth_readiness"]
        self.assertEqual(cap["status"], "available")
        self.assertEqual(cap["evidence"], "omj providers doctor")
        self.assertIn("env-presence metadata only", cap["message"])

        provider_auth = payload["provider_auth"]
        self.assertEqual(provider_auth["schema_version"], PROVIDER_AUTH_CONTRACT_VERSION)
        self.assertEqual(provider_auth["boundary"], PROVIDER_AUTH_DIAGNOSTIC_BOUNDARY)
        summary = provider_auth["summary"]
        # The catalog size is fixed regardless of host env.
        self.assertEqual(summary["total"], 30)
        # With no provider env set, only the two keyless local endpoints are configured.
        self.assertEqual(sorted(summary["configured_ids"]), ["lmstudio", "ollama"])
        self.assertEqual(summary["host_managed"], 4)

    def test_probe_provider_auth_reflects_host_env_without_leaking_secret(self):
        secret = "sk-PROBE-DO-NOT-LEAK-0987654321"
        stdout, payload = self._probe({"GROQ_API_KEY": secret})
        summary = payload["provider_auth"]["summary"]
        self.assertIn("groq", summary["configured_ids"])
        self.assertNotIn("groq", summary["missing_required_ids"])
        # The diagnostic reports env-var presence only, never the secret value.
        self.assertNotIn(secret, stdout)


if __name__ == "__main__":
    unittest.main()
