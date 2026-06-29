from __future__ import annotations

import json
import unittest

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()

from omj.catalogs.provider_auth import (
    AUTH_KINDS,
    PROVIDER_AUTH_CONTRACT_VERSION,
    STATUS_CONFIGURED,
    STATUS_HOST_MANAGED,
    STATUS_LOCAL_DEFAULT,
    STATUS_LOCAL_OVERRIDE,
    STATUS_MISSING,
    _validate_catalog,
    diagnose_provider_auth,
    get_provider_auth,
    list_provider_auth,
)
from omj.coding.executors import EXECUTOR_PROFILES


class ProviderAuthCatalogTests(unittest.TestCase):
    def test_catalog_integrity_and_owner_neutrality(self) -> None:
        _validate_catalog()  # raises on duplicate id / unknown owner / shape errors
        payload = list_provider_auth()
        self.assertEqual(payload["schema_version"], PROVIDER_AUTH_CONTRACT_VERSION)
        providers = payload["providers"]
        ids = [p["id"] for p in providers]
        self.assertEqual(len(ids), len(set(ids)), "provider ids must be unique")
        kinds = {p["auth_kind"] for p in providers}
        self.assertEqual(kinds, set(AUTH_KINDS), "all three auth kinds must be represented")
        for provider in providers:
            self.assertTrue(provider["consumed_by"], f"{provider['id']} needs an owner")
            for owner in provider["consumed_by"]:
                self.assertIn(owner, EXECUTOR_PROFILES)
            self.assertEqual(provider["runtime_claim"], "descriptor_not_runtime_router")

    def test_taxonomy_borrowed_from_coding_runtime(self) -> None:
        by_id = {p["id"]: p for p in list_provider_auth()["providers"]}
        # OAuth surfaces the user named explicitly.
        self.assertEqual(by_id["anthropic"]["auth_kind"], "oauth")
        self.assertEqual(by_id["antigravity"]["auth_kind"], "oauth")
        self.assertIn("claude-code", by_id["anthropic"]["consumed_by"])
        # Local keyless endpoints with their default URLs.
        self.assertEqual(by_id["lmstudio"]["auth_kind"], "local_endpoint")
        self.assertFalse(by_id["lmstudio"]["requires_secret"])
        self.assertEqual(by_id["lmstudio"]["default_endpoint"], "http://localhost:1234/v1")
        self.assertEqual(by_id["ollama"]["default_endpoint"], "http://localhost:11434")
        self.assertIn("OLLAMA_HOST", by_id["ollama"]["endpoint_env"])
        # OpenAI-compatible cloud APIs ("그외의 api").
        self.assertEqual(by_id["groq"]["auth_kind"], "api_key")
        self.assertEqual(by_id["groq"]["api_key_env"], ["GROQ_API_KEY"])

    def test_openai_compatible_set_is_broad_with_distinct_credentials(self) -> None:
        providers = list_provider_auth()["providers"]
        api = [p for p in providers if p["auth_kind"] == "api_key"]
        # The "그외의 api" catalog should cover the major OpenAI-compatible hosts.
        self.assertGreaterEqual(len(api), 20)
        for expected in ("perplexity", "cohere", "sambanova", "dashscope", "zhipu", "minimax"):
            self.assertIn(expected, {p["id"] for p in api}, f"missing provider {expected}")
        # Each api provider must carry a distinct primary credential env var and
        # endpoint so a copy-paste row does not shadow another provider.
        primary_envs = [p["api_key_env"][0] for p in api]
        self.assertEqual(len(primary_envs), len(set(primary_envs)))
        endpoints = [p["default_endpoint"] for p in api]
        self.assertEqual(len(endpoints), len(set(endpoints)))
        self.assertTrue(all(endpoints))


    def test_get_provider_auth_unknown_raises(self) -> None:
        with self.assertRaises(KeyError):
            get_provider_auth("does-not-exist")

    def test_list_and_diagnose_are_deterministic(self) -> None:
        self.assertEqual(list_provider_auth(), list_provider_auth())
        env = {"GROQ_API_KEY": "x"}
        self.assertEqual(diagnose_provider_auth(env), diagnose_provider_auth(env))


class ProviderAuthDiagnosticTests(unittest.TestCase):
    def _by_id(self, env: dict[str, str]) -> dict[str, dict]:
        return {p["id"]: p for p in diagnose_provider_auth(env)["providers"]}

    def test_api_key_present_is_configured_absent_is_missing(self) -> None:
        rows = self._by_id({"GROQ_API_KEY": "secret-value"})
        self.assertEqual(rows["groq"]["status"], STATUS_CONFIGURED)
        self.assertTrue(rows["groq"]["configured"])
        self.assertEqual(rows["groq"]["api_key_env_present"], ["GROQ_API_KEY"])
        self.assertEqual(rows["deepseek"]["status"], STATUS_MISSING)
        self.assertFalse(rows["deepseek"]["configured"])

    def test_blank_env_value_counts_as_missing(self) -> None:
        rows = self._by_id({"GROQ_API_KEY": "   "})
        self.assertEqual(rows["groq"]["status"], STATUS_MISSING)
        self.assertEqual(rows["groq"]["api_key_env_present"], [])

    def test_oauth_is_host_managed_unless_api_key_override(self) -> None:
        rows = self._by_id({})
        self.assertEqual(rows["antigravity"]["status"], STATUS_HOST_MANAGED)
        self.assertEqual(rows["anthropic"]["status"], STATUS_HOST_MANAGED)
        self.assertFalse(rows["anthropic"]["configured"])
        # API-key override is the only host-detectable signal; status stays
        # host_managed but configured flips True.
        rows_override = self._by_id({"ANTHROPIC_API_KEY": "sk-ant-override"})
        self.assertEqual(rows_override["anthropic"]["status"], STATUS_HOST_MANAGED)
        self.assertTrue(rows_override["anthropic"]["configured"])

    def test_local_endpoint_default_vs_override(self) -> None:
        rows = self._by_id({})
        self.assertEqual(rows["lmstudio"]["status"], STATUS_LOCAL_DEFAULT)
        self.assertTrue(rows["lmstudio"]["configured"])  # keyless
        rows_override = self._by_id({"OLLAMA_HOST": "http://10.0.0.5:11434"})
        self.assertEqual(rows_override["ollama"]["status"], STATUS_LOCAL_OVERRIDE)
        self.assertEqual(rows_override["ollama"]["endpoint_env_present"], ["OLLAMA_HOST"])

    def test_diagnostic_never_echoes_secret_or_endpoint_values(self) -> None:
        secret = "sk-DO-NOT-LEAK-1234567890"
        endpoint = "http://hidden-host.internal:9999"
        blob = json.dumps(
            diagnose_provider_auth(
                {"GROQ_API_KEY": secret, "ANTHROPIC_API_KEY": secret, "OLLAMA_HOST": endpoint}
            )
        )
        self.assertNotIn(secret, blob)
        self.assertNotIn("hidden-host.internal", blob)

    def test_summary_counts_match_rows(self) -> None:
        diag = diagnose_provider_auth({"GROQ_API_KEY": "x"})
        summary = diag["summary"]
        self.assertEqual(summary["total"], len(diag["providers"]))
        self.assertEqual(
            summary["configured"],
            sum(1 for p in diag["providers"] if p["configured"]),
        )
        self.assertIn("groq", summary["configured_ids"])


class ProviderAuthCliTests(unittest.TestCase):
    def test_cli_list_inspect_doctor(self) -> None:
        code, out, _ = run_cli(["providers", "list"], output_json=True)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["schema_version"], PROVIDER_AUTH_CONTRACT_VERSION)

        code, out, _ = run_cli(["providers", "inspect", "anthropic"], output_json=True)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["provider"]["id"], "anthropic")

        code, out, _ = run_cli(["providers", "doctor"], output_json=True)
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertIn("summary", payload)
        self.assertIn("boundary", payload)

    def test_cli_inspect_unknown_provider_errors(self) -> None:
        code, _, err = run_cli(["providers", "inspect", "nope"], output_json=True)
        self.assertEqual(code, 2)
        self.assertIn("unknown provider", err)


if __name__ == "__main__":
    unittest.main()
