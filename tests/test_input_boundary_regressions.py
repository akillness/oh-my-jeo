from __future__ import annotations

import json
import io
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()

import omj.commands.context as context_commands
import omj.commands.memory as memory_commands
import omj.commands.providers as provider_commands
import omj.profiles.transport as transport
from omj.commands.context import _read_project_terms_source
from omj.commands.memory import _read_required_json
from omj.commands.providers import _read_json_object
from omj.profiles.transport import SetupProfilePackError, read_setup_profile_pack
from omj.plugin_bundle.omj import runtime_paths

GOAL_ROOT = Path(__file__).resolve().parents[1]
TERMS_TEXT = (
    "# Project Terms\n\n"
    "Project terminology only. This file is not agent instructions, routing rules, approval, execution, or evidence. Changes affect OMJ only after explicit review.\n\n"
    "<!-- omj-project-terms/v1 -->\n\n"
    "## domain: core\n"
    "- term: `foo` = `bar`\n"
)


class InputBoundaryRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        for module in (context_commands, provider_commands, memory_commands, transport, runtime_paths):
            self.assertTrue(str(Path(module.__file__).resolve()).startswith(str(GOAL_ROOT)))

    def _fifo_refusal(self, expression_factory, expected: str) -> None:
        with TemporaryDirectory() as tmp:
            fifo = Path(tmp) / "input.fifo"
            os.mkfifo(fifo)
            expression = expression_factory(fifo)
            code = (
                "from _local_package import load_local_package; load_local_package(); "
                "import omj.commands.context, omj.commands.providers, omj.commands.memory, omj.profiles.transport; "
                "from pathlib import Path; "
                f"assert all(str(Path(m.__file__).resolve()).startswith({str(GOAL_ROOT)!r}) for m in (omj.commands.context, omj.commands.providers, omj.commands.memory, omj.profiles.transport)); "
                "\ntry:\n"
                f"    {expression}\n"
                "except Exception as exc:\n"
                "    print(type(exc).__name__ + ':' + str(exc))\n"
            )
            env = dict(os.environ)
            env["PYTHONPATH"] = str(GOAL_ROOT / "tests")
            completed = subprocess.run(
                [sys.executable, "-c", code],
                cwd=str(GOAL_ROOT),
                env=env,
                capture_output=True,
                text=True,
                timeout=2,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn(expected, completed.stdout)

    def test_fifo_inputs_refuse_without_blocking(self) -> None:
        self._fifo_refusal(
            lambda path: f"omj.commands.context._read_project_terms_source({str(path)!r})",
            "project_terms_source_not_regular_file",
        )
        self._fifo_refusal(
            lambda path: f"omj.commands.providers._read_json_object({str(path)!r}, 'chain config')",
            "chain config path must be a regular file",
        )
        self._fifo_refusal(
            lambda path: f"omj.commands.memory._read_required_json({str(path)!r})",
            "memory JSON input must be a regular file",
        )
        self._fifo_refusal(
            lambda path: f"omj.profiles.transport.read_setup_profile_pack({str(path)!r})",
            "setup profile pack must be a regular file",
        )

    def test_valid_and_just_over_bound_regular_files(self) -> None:
        cases = (
            ("terms", context_commands.MAX_PROJECT_TERMS_SOURCE_BYTES, _read_project_terms_source, "project_terms_source_too_large"),
            ("provider", provider_commands._MAX_JSON_INPUT_BYTES, lambda path: _read_json_object(str(path), "chain config"), "chain config exceeds maximum size"),
            ("memory", memory_commands._MAX_MEMORY_JSON_BYTES, _read_required_json, "memory JSON input exceeds"),
            ("pack", transport._MAX_PACK_BYTES, read_setup_profile_pack, "setup profile pack exceeds"),
        )
        for name, limit, reader, error_text in cases:
            with self.subTest(reader=name), TemporaryDirectory() as tmp:
                path = Path(tmp) / "input.json"
                valid = b"{}"
                path.write_bytes(valid)
                result = reader(path)
                self.assertEqual(result, b"{}" if name == "terms" else {})
                path.write_bytes(b"{" + b"x" * (limit + 1) + b"}")
                with self.assertRaises(ValueError) as raised:
                    reader(path)
                self.assertIn(error_text, str(raised.exception))

    def test_terms_provider_and_memory_production_clis_accept_valid_files(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            terms = root / "PROJECT_TERMS.md"
            terms.write_text(TERMS_TEXT, encoding="utf-8")
            status, stdout, stderr = run_cli(["context", "terms", "inspect", "--source", str(terms)])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(json.loads(stdout)["schema_version"], "omj_project_terms_inspect/v1")

            chain = root / "chain.json"
            chain.write_text(json.dumps({"fast": [["openai", "low"]]}), encoding="utf-8")
            status, stdout, stderr = run_cli(["providers", "complexity", "hello", "--chain-json", str(chain)])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(json.loads(stdout)["schema_version"], "request_complexity/v1")

            fixture = root / "fixture.json"
            fixture.write_text(json.dumps({"cases": []}), encoding="utf-8")
            status, stdout, stderr = run_cli(["memory", "evaluate", "--fixture", str(fixture)])
            self.assertEqual((status, stderr), (0, ""))
            self.assertEqual(json.loads(stdout)["schema_version"], "omj_memory_retrieval_evaluation/v1")
    def test_provider_literal_and_memory_stdin_inputs_are_bounded(self) -> None:
        self.assertEqual(_read_json_object('{"fast": []}', "chain config"), {"fast": []})
        with self.assertRaisesRegex(ValueError, "chain config exceeds maximum size"):
            _read_json_object("{" + "x" * provider_commands._MAX_JSON_INPUT_BYTES + "}", "chain config")

        with patch.object(memory_commands.sys, "stdin", io.BytesIO(b'{"cases": []}')):
            self.assertEqual(_read_required_json("-"), {"cases": []})
        with patch.object(memory_commands.sys, "stdin", io.BytesIO(b"x" * (memory_commands._MAX_MEMORY_JSON_BYTES + 1))):
            with self.assertRaisesRegex(ValueError, "memory JSON input exceeds"):
                _read_required_json("-")


    def test_read_growth_is_rejected_after_regular_file_stat(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "input"
            path.write_bytes(b"{}")
            with patch.object(context_commands.os, "read", return_value=b"x" * (context_commands.MAX_PROJECT_TERMS_SOURCE_BYTES + 1)):
                with self.assertRaisesRegex(ValueError, "project_terms_source_too_large"):
                    _read_project_terms_source(path)
            with patch.object(provider_commands.os, "read", return_value=b"{}" + b"x" * provider_commands._MAX_JSON_INPUT_BYTES):
                with self.assertRaisesRegex(ValueError, "chain config exceeds maximum size"):
                    _read_json_object(str(path), "chain config")
            with patch.object(memory_commands.os, "read", return_value=b"{}" + b"x" * memory_commands._MAX_MEMORY_JSON_BYTES):
                with self.assertRaisesRegex(ValueError, "memory JSON input exceeds"):
                    _read_required_json(str(path))
            with patch.object(transport.os, "read", return_value=b"{}" + b"x" * transport._MAX_PACK_BYTES):
                with self.assertRaisesRegex(SetupProfilePackError, "setup profile pack exceeds"):
                    read_setup_profile_pack(path)

    def test_profile_pack_symlink_and_config_fifo_are_refused(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "link.json"
            link.symlink_to(target)
            with self.assertRaisesRegex(SetupProfilePackError, "must not be a symlink"):
                read_setup_profile_pack(link)

            hermes = root / "hermes"
            hermes.mkdir()
            os.mkfifo(hermes / "config.yaml")
            self.assertIs(runtime_paths._configured_home(hermes), runtime_paths._MISSING)

    def test_configured_home_preserves_valid_binding_and_refuses_growth(self) -> None:
        with TemporaryDirectory() as tmp:
            hermes = Path(tmp) / "hermes"
            hermes.mkdir()
            config = hermes / "config.yaml"
            config.write_text("plugins:\n  entries:\n    omj:\n      settings:\n        omj_home: '/tmp/omj-bound'\n", encoding="utf-8")
            self.assertEqual(runtime_paths._configured_home(hermes), Path("/tmp/omj-bound").resolve())
            with patch.object(runtime_paths.os, "read", return_value=b"x" * (runtime_paths._MAX_CONFIG_FILE_BYTES + 1)):
                self.assertIs(runtime_paths._configured_home(hermes), runtime_paths._MISSING)


if __name__ == "__main__":
    unittest.main()
