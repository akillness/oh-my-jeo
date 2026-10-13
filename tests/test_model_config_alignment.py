from __future__ import annotations

import json
import hashlib
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()


# Frozen from the pinned upstream model_contracts.py. These are exact contract
# ids, not a claim that a provider account or host currently serves them.
UPSTREAM_EXACT_CONTRACTS = (
    "gpt-6-astra",
    "gpt-6-sol",
    "gpt-6.1-sol",
    "gpt-6-luna",
    "claude-opus-5-5",
    "claude-sonnet-5-5",
    "deepseek-v4.1-flash",
    "jev-1.13.0",
)

UPSTREAM_DECLARED_PROJECTIONS = {
    "gpt-6-astra-fast": ("gpt-6-astra", "standard", "fast"),
    "gpt-6-astra-flex": ("gpt-6-astra", "standard", "flex"),
    "gpt-6-astra-pro": ("gpt-6-astra", "pro", "standard"),
    "gpt-6-astra-pro-fast": ("gpt-6-astra", "pro", "fast"),
    "gpt-6-astra-pro-flex": ("gpt-6-astra", "pro", "flex"),
    "gpt-6.1-sol-pro": ("gpt-6.1-sol", "pro", "standard"),
    "deepseek-flash": ("deepseek-v4.1-flash", "thinking", "standard"),
    "anthropic.claude-opus-5-5": ("claude-opus-5-5", "thinking", "standard"),
    "claude-opus-5.5": ("claude-opus-5-5", "thinking", "standard"),
    "anthropic.claude-sonnet-5-5": ("claude-sonnet-5-5", "thinking", "standard"),
    "claude-sonnet-5.5": ("claude-sonnet-5-5", "thinking", "standard"),
    "jev-latest": ("jev-1.13.0", "none", "standard"),
    "jev-preview": ("jev-1.13.0", "none", "standard"),
}


def _coverage_inventory(*model_ids: str, status: str = "observed") -> dict[str, object]:
    return {
        "source": "test-local-inventory",
        "inventory_status": status,
        "models": [
            {"provider": model_id.split("/", 1)[0], "model_id": model_id.split("/", 1)[-1], "status": "observed"}
            for model_id in model_ids
        ],
    }


def _rows(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    comparison = payload["comparison"]
    assert isinstance(comparison, dict)
    rows = comparison["models"]
    assert isinstance(rows, list)
    return {str(row["requested_model"]): row for row in rows if isinstance(row, dict)}


class ModelCoverageAlignmentTests(unittest.TestCase):
    def test_cli_covers_every_pinned_exact_contract_and_declared_projection(self) -> None:
        inventory_models = (*UPSTREAM_EXACT_CONTRACTS, *UPSTREAM_DECLARED_PROJECTIONS)
        args = [
            "providers",
            "model-coverage",
            "--inventory",
            json.dumps(_coverage_inventory(*inventory_models)),
            "--json",
        ]
        for model_id in UPSTREAM_EXACT_CONTRACTS:
            args.extend(("--required-model", model_id))
        for model_id in UPSTREAM_DECLARED_PROJECTIONS:
            args.extend(("--recommended-model", model_id))

        with patch("socket.socket", side_effect=AssertionError("model coverage must never use the network")):
            code, output, error = run_cli(args, output_json=True)

        self.assertEqual((code, error), (0, ""))
        payload = json.loads(output)
        rows = _rows(payload)
        self.assertEqual(set(rows), set(inventory_models))
        for model_id in UPSTREAM_EXACT_CONTRACTS:
            self.assertEqual(rows[model_id]["status"], "exact")
            self.assertEqual(rows[model_id]["contract_model_id"], model_id)
            self.assertEqual(rows[model_id]["actionability"], "covered")
        for model_id, (contract_id, _reasoning_mode, service_tier) in UPSTREAM_DECLARED_PROJECTIONS.items():
            row = rows[model_id]
            self.assertEqual(row["status"], "declared_inheritance")
            self.assertEqual(row["contract_model_id"], contract_id)
            self.assertEqual(row["actionability"], "covered")
            self.assertEqual(row["dimensions"]["contract"]["provenance"], "declared_inheritance")
            self.assertIn(service_tier, {"standard", "fast", "flex"})
            self.assertNotIn("availability", row)

    def test_unknown_and_unmeasured_inventory_is_not_qualified(self) -> None:
        unknown = "unlisted-provider/future-model"
        inventory = _coverage_inventory("gpt-6-sol", unknown, status="unavailable")
        code, output, error = run_cli(
            [
                "providers",
                "model-coverage",
                "--inventory",
                json.dumps(inventory),
                "--required-model",
                unknown,
                "--recommended-model",
                "gpt-6-sol",
                "--json",
            ],
            output_json=True,
        )

        self.assertEqual((code, error), (1, ""))
        payload = json.loads(output)
        rows = _rows(payload)
        self.assertEqual(rows[unknown]["status"], "missing")
        self.assertEqual(rows[unknown]["actionability"], "required_missing")
        self.assertIsNone(rows[unknown]["contract_model_id"])
        self.assertEqual(rows["gpt-6-sol"]["status"], "exact")
        self.assertEqual(payload["comparison"]["inventory"]["status"], "unavailable")
        self.assertTrue(payload["blocking"])


    def test_secret_shaped_provider_and_model_refs_are_rejected_without_echo(self) -> None:
        secret = "ghp_1234567890abcdef1234567890abcdef"
        cases = (
            {"models": [{"model_id": secret}]},
            {"models": [{"provider": secret, "model_id": "safe-model"}]},
        )
        for inventory in cases:
            with self.subTest(inventory=inventory):
                code, output, error = run_cli(
                    ["providers", "model-coverage", "--inventory", json.dumps(inventory), "--json"],
                    output_json=True,
                )
                self.assertEqual(code, 2)
                self.assertNotIn(secret, output)
                self.assertNotIn(secret, error)

    def test_request_verdicts_public_contract_exports_remain_importable(self) -> None:
        from omj.coding import request_verdicts

        self.assertTrue(request_verdicts.MODEL_CONTRACTS)
        self.assertTrue(request_verdicts.DECLARED_MODEL_CONTRACT_PROJECTIONS)
        self.assertEqual(request_verdicts.MODEL_CONTRACT_COVERAGE_SCHEMA_VERSION, "model_contract_coverage/v1")


class HermesModelConfigCliAlignmentTests(unittest.TestCase):
    def _hermes_home(self, root: Path, body: str) -> Path:
        home = root / ".hermes"
        home.mkdir()
        (home / "config.yaml").write_text(body, encoding="utf-8")
        return home

    def test_dotted_model_provider_and_base_url_are_readable(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            home = self._hermes_home(
                Path(raw_root),
                "model:\n"
                "  default: anthropic.claude-opus-5-5\n"
                "  provider: anthropic.gateway\n"
                "  base_url: https://api.example.invalid/v1\n",
            )
            code, output, error = run_cli(
                ["--hermes-home", str(home), "providers", "model-status", "--json"], output_json=True
            )
            self.assertEqual((code, error), (0, ""))
            payload = json.loads(output)
            self.assertTrue(payload["config"]["readable"])
            self.assertEqual(payload["default_model"]["value"], "anthropic.claude-opus-5-5")
            self.assertEqual(payload["provider"]["value"], "anthropic.gateway")
            self.assertEqual(payload["base_url"]["host"], "api.example.invalid")
    def test_absent_model_section_value_is_readable_not_false_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            home = self._hermes_home(
                Path(raw_root),
                "model:\n  provider: anthropic\n  base_url: https://api.example.invalid/v1\n",
            )
            code, output, error = run_cli(
                ["--hermes-home", str(home), "providers", "model-status", "--json"], output_json=True
            )
            self.assertEqual((code, error), (0, ""))
            payload = json.loads(output)
            self.assertTrue(payload["config"]["readable"])
            self.assertEqual(payload["default_model"], {"value": "", "family": ""})

    def test_secret_shaped_aliases_are_rejected_without_echo(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            home = self._hermes_home(
                Path(raw_root),
                "model:\n  default: anthropic/claude-opus-5-5\n  provider: anthropic\n",
            )
            digest = hashlib.sha256((home / "config.yaml").read_bytes()).hexdigest()
            for alias in (
                "ghp_1234567890abcdef1234567890abcdef",
                "Bearer sk-secret-value-1234567890",
                "Auth sk-secret-value-1234567890",
            ):
                with self.subTest(alias=alias):
                    code, output, error = run_cli(
                        [
                            "--hermes-home",
                            str(home),
                            "providers",
                            "model-setup-preview",
                            "--model-alias",
                            f"{alias}=anthropic/claude-opus-5-5",
                            "--model-config-digest",
                            digest,
                            "--json",
                        ],
                        output_json=True,
                    )
                    self.assertEqual(code, 2)
                    self.assertNotIn(alias, output)
                    self.assertNotIn(alias, error)



    def test_provider_model_inspection_status_and_preview_are_public_read_only_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            home = self._hermes_home(
                root,
                "model:\n"
                "  default: anthropic/claude-opus-5-5\n"
                "  provider: anthropic\n"
                "  base_url: https://config-user:super-secret-token@example.invalid/v1\n"
                "  aliases:\n"
                "    main: anthropic/claude-opus-5-5\n",
            )
            config_digest = hashlib.sha256((home / "config.yaml").read_bytes()).hexdigest()
            base = ["--hermes-home", str(home), "--scope", "project", "providers"]
            with patch("socket.socket", side_effect=AssertionError("model inspection must never use the network")):
                inventory_code, inventory_out, inventory_err = run_cli(
                    [*base, "model-inventory", "--json"], output_json=True
                )
                status_code, status_out, status_err = run_cli(
                    [*base, "model-status", "--json"], output_json=True
                )
                preview_code, preview_out, preview_err = run_cli(
                    [
                        *base,
                        "model-setup-preview",
                        "--confirm-model",
                        "anthropic/claude-opus-5-5",
                        "--model-alias",
                        "main=anthropic/claude-opus-5-5",
                        "--model-config-digest",
                        config_digest,
                        "--json",
                    ],
                    output_json=True,
                )

            self.assertEqual((inventory_code, inventory_err), (0, ""))
            self.assertEqual((status_code, status_err), (0, ""))
            self.assertEqual((preview_code, preview_err), (0, ""))
            inventory = json.loads(inventory_out)
            status = json.loads(status_out)
            preview = json.loads(preview_out)
            for payload in (inventory, status, preview):
                rendered = json.dumps(payload, sort_keys=True)
                self.assertNotIn("super-secret-token", rendered)
                self.assertNotIn("config-user", rendered)
            self.assertEqual(status["config"]["path"], str(home / "config.yaml"))
            self.assertTrue(status["config"]["found"])
            self.assertTrue(status["config"]["readable"])
            self.assertEqual(len(status["config"]["digest"]), 64)
            self.assertEqual(status["default_model"]["value"], "anthropic/claude-opus-5-5")
            self.assertEqual(status["default_model"]["family"], "anthropic")
            self.assertEqual(status["provider"]["value"], "anthropic")
            self.assertTrue(status["provider"]["pinned"])
            self.assertTrue(status["base_url"]["set"])
            self.assertEqual(status["base_url"]["host"], "example.invalid")
            self.assertEqual(inventory["source_state"]["config"]["path"], str(home / "config.yaml"))
            self.assertEqual(len(inventory["source_state"]["config"]["sha256"]), 64)
            self.assertTrue(inventory["source_state"]["config"]["readable"])
            self.assertEqual(preview["source_state"]["config"]["path"], str(home / "config.yaml"))
            self.assertEqual(len(preview["source_state"]["config"]["sha256"]), 64)
            self.assertEqual(inventory["models"][0]["model_id"], "anthropic/claude-opus-5-5")
            self.assertIn(inventory["models"][0]["provenance"], {"config", "alias", "local"})
            self.assertIn(inventory["models"][0]["status"], {"known", "discovered", "explicitly_confirmed"})
            self.assertEqual(preview["confirmed_models"], ["anthropic/claude-opus-5-5"])
            self.assertEqual(preview["changes"], {"main": "anthropic/claude-opus-5-5"})
            self.assertEqual(preview["proposed_aliases"], {"main": "anthropic/claude-opus-5-5"})
            self.assertEqual(preview["collisions"], {})
            self.assertEqual(preview["drift"]["expected_digest"], config_digest)
            self.assertEqual(preview["drift"]["current_digest"], config_digest)
            self.assertTrue(preview["drift"]["match"])
            self.assertEqual((home / "config.yaml").read_text(encoding="utf-8"), "model:\n  default: anthropic/claude-opus-5-5\n  provider: anthropic\n  base_url: https://config-user:super-secret-token@example.invalid/v1\n  aliases:\n    main: anthropic/claude-opus-5-5\n")

    def test_status_reports_provider_default_base_url_mismatch_without_network_or_nonzero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            home = self._hermes_home(
                root,
                "model:\n"
                "  default: openai/gpt-6-sol\n"
                "  provider: auto\n"
                "  base_url: https://gateway.invalid/v1\n",
            )
            with patch("socket.socket", side_effect=AssertionError("status must never probe a gateway")):
                code, output, error = run_cli(
                    ["--hermes-home", str(home), "providers", "model-status", "--json"], output_json=True
                )
            self.assertEqual((code, error), (0, ""))
            payload = json.loads(output)
            self.assertEqual(payload["default_model"]["value"], "openai/gpt-6-sol")
            self.assertEqual(payload["default_model"]["family"], "openai")
            self.assertEqual(payload["provider"], {"value": "auto", "pinned": False})
            self.assertTrue(payload["disagreements"])
            self.assertIn("model.default", payload["disagreements"][0])
            self.assertIn("model.base_url", payload["disagreements"][0])

    def test_status_negative_controls_do_not_claim_provider_activation(self) -> None:
        cases = (
            (
                "gateway",
                "model:\n  default: openai/gpt-6-sol\n  provider: auto\n  base_url: https://gateway.invalid/v1\n",
                "gateway.invalid",
                True,
            ),
            (
                "custom",
                "model:\n  default: custom/tenant-model\n  provider: custom\n",
                "",
                False,
            ),
            (
                "no-url",
                "model:\n  default: anthropic/claude-opus-5-5\n  provider: auto\n",
                "",
                False,
            ),
            (
                "non-family",
                "model:\n  default: anthropic/claude-opus-5-5\n  provider: auto\n  base_url: https://api.openai.com/v1\n",
                "api.openai.com",
                True,
            ),
            (
                "pinned-mismatch",
                "model:\n  default: openai/gpt-6-sol\n  provider: anthropic\n  base_url: https://api.anthropic.com/v1\n",
                "api.anthropic.com",
                False,
            ),
        )
        for name, body, expected_host, has_disagreement in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as raw_root:
                home = self._hermes_home(Path(raw_root), body)
                with patch("socket.socket", side_effect=AssertionError("status must never probe a gateway")):
                    code, output, error = run_cli(
                        ["--hermes-home", str(home), "providers", "model-status", "--json"],
                        output_json=True,
                    )
                self.assertEqual((code, error), (0, ""))
                payload = json.loads(output)
                self.assertEqual(payload["base_url"]["host"], expected_host)
                self.assertEqual(bool(payload["disagreements"]), has_disagreement)
                self.assertNotIn("active_model", payload)
                self.assertNotIn("selected_model", payload)

    def test_unknown_confirmed_model_row_preserves_contract_gap_and_source(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            home = self._hermes_home(
                Path(raw_root),
                "model:\n"
                "  default: anthropic/claude-opus-5-5\n"
                "  provider: anthropic\n",
            )
            unknown = "anthropic/unknown-model"
            digest = hashlib.sha256((home / "config.yaml").read_bytes()).hexdigest()
            code, output, error = run_cli(
                [
                    "--hermes-home",
                    str(home),
                    "providers",
                    "model-setup-preview",
                    "--confirm-model",
                    unknown,
                    "--model-alias",
                    f"unknown={unknown}",
                    "--model-config-digest",
                    digest,
                    "--json",
                ],
                output_json=True,
            )
            self.assertEqual((code, error), (0, ""))
            payload = json.loads(output)
            row = next(item for item in payload["models"] if item["model_id"] == unknown)
            self.assertEqual(row["status"], "explicitly_confirmed")
            self.assertIn("contract_model_id", row)
            self.assertIsNone(row["contract_model_id"])
            self.assertTrue(row["source"])

    def test_model_setup_preview_refuses_alias_collision_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            home = self._hermes_home(
                root,
                "model:\n"
                "  default: anthropic/claude-opus-5-5\n"
                "  provider: anthropic\n"
                "  aliases:\n"
                "    main: anthropic/claude-opus-5-5\n",
            )
            before = (home / "config.yaml").read_bytes()
            digest = hashlib.sha256(before).hexdigest()
            code, _output, error = run_cli(
                [
                    "--hermes-home",
                    str(home),
                    "providers",
                    "model-setup-preview",
                    "--confirm-model",
                    "anthropic/claude-sonnet-5-5",
                    "--model-alias",
                    "main=anthropic/claude-sonnet-5-5",
                    "--model-config-digest",
                    digest,
                    "--json",
                ],
                output_json=True,
            )
            self.assertEqual(code, 2)
            self.assertIn("collision", error.casefold())
            self.assertEqual((home / "config.yaml").read_bytes(), before)


    def test_setup_model_flags_preview_alias_collision_and_digest_are_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            home = self._hermes_home(
                root,
                "model:\n"
                "  default: anthropic/claude-opus-5-5\n"
                "  provider: anthropic\n"
                "  aliases:\n"
                "    main: anthropic/claude-opus-5-5\n",
            )
            before = (home / "config.yaml").read_bytes()
            code, output, error = run_cli(
                [
                    "--hermes-home",
                    str(home),
                    "setup",
                    "--no-interactive",
                    "--dry-run",
                    "--model-setup",
                    "--confirm-model",
                    "anthropic/claude-opus-5-5",
                    "--model-alias",
                    "main=anthropic/claude-sonnet-5-5",
                    "--json",
                ],
                output_json=True,
            )
            self.assertEqual((code, error), (0, ""))
            payload = json.loads(output)
            activation = payload["steps"]["model_activation"]
            self.assertEqual(activation["status"], "preview_ready")
            self.assertEqual(activation["preview"]["changes"], {"main": "anthropic/claude-sonnet-5-5"})
            self.assertEqual(activation["apply"]["status"], "not_requested")
            self.assertEqual((home / "config.yaml").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
