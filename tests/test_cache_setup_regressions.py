from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import warnings
from types import SimpleNamespace
from unittest.mock import patch

from _local_package import load_local_package

load_local_package()

import omj.commands.setup as setup_commands
import omj.workflows.paper_learning as paper_learning

GOAL_ROOT = Path(__file__).resolve().parents[1]


class CacheAndSetupRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        for module in (setup_commands, paper_learning):
            self.assertTrue(str(Path(module.__file__).resolve()).startswith(str(GOAL_ROOT)))

    def _record_fixture(self, root: Path) -> tuple[SimpleNamespace, dict[str, object]]:
        source = root / "paper.pdf"
        source.write_bytes(b"paper bytes")
        paths = SimpleNamespace(omj_home=root / ".omj")
        record = paper_learning.build_paper_learning_record(
            title="Durable Paper",
            source_ref=str(source),
            authors=("Author",),
            level="expert",
            source_state="metadata_only",
            sections=("Abstract", "Method"),
            paper_id="paper-001",
            created_at="2026-10-12T00:00:00Z",
            created_at_ns=1,
        )
        return paths, record

    @staticmethod
    def _runtime_warnings(caught: list[warnings.WarningMessage]) -> list[warnings.WarningMessage]:
        return [item for item in caught if issubclass(item.category, RuntimeWarning)]

    def test_create_persists_authoritative_card_when_index_cache_raises_oserror(self) -> None:
        with TemporaryDirectory() as tmp:
            paths, record = self._record_fixture(Path(tmp))
            with patch.object(paper_learning, "_write_index_cache", side_effect=OSError("cache unavailable")) as cache:
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    written = paper_learning.write_paper_learning_record(paths, record)

            self.assertEqual(written["paper_id"], "paper-001")
            self.assertEqual(cache.call_count, 1)
            runtime_warnings = self._runtime_warnings(caught)
            self.assertEqual(len(runtime_warnings), 1)
            self.assertIn("authoritative paper record remains committed", str(runtime_warnings[0].message))
            card_path = paper_learning.paper_learning_card_path(paths, "paper-001")
            self.assertEqual(json.loads(card_path.read_text(encoding="utf-8"))["paper_id"], "paper-001")

    def test_progress_persists_ledger_and_card_when_index_cache_raises_oserror(self) -> None:
        with TemporaryDirectory() as tmp:
            paths, record = self._record_fixture(Path(tmp))
            with patch.object(paper_learning, "_write_index_cache"):
                paper_learning.write_paper_learning_record(paths, record)

            with patch.object(paper_learning, "_write_index_cache", side_effect=OSError("cache unavailable")) as cache:
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    updated, entry = paper_learning.record_paper_progress(
                        paths,
                        "paper-001",
                        covered=("Abstract",),
                        next_section="Method",
                        note="covered abstract",
                        recorded_at="2026-10-12T00:01:00Z",
                    )

            self.assertEqual(updated["paper_id"], "paper-001")
            self.assertEqual(updated["progress_count"], 1)
            self.assertEqual(entry["paper_id"], "paper-001")
            self.assertEqual(cache.call_count, 1)
            self.assertEqual(len(self._runtime_warnings(caught)), 1)
            ledger_path = paper_learning.paper_learning_ledger_path(paths, "paper-001")
            ledger_rows = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(ledger_rows), 1)
            self.assertEqual(ledger_rows[0]["part_index"], 1)
            card = json.loads(paper_learning.paper_learning_card_path(paths, "paper-001").read_text(encoding="utf-8"))
            self.assertEqual(card["progress_count"], 1)

    def test_unexpected_cache_runtime_error_propagates(self) -> None:
        with TemporaryDirectory() as tmp:
            paths, record = self._record_fixture(Path(tmp))
            with patch.object(paper_learning, "_write_index_cache", side_effect=RuntimeError("unexpected cache failure")):
                with self.assertRaisesRegex(RuntimeError, "unexpected cache failure"):
                    paper_learning.write_paper_learning_record(paths, record)

    def test_apply_reports_external_dir_and_omj_binding_and_keeps_both(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = Namespace(
                omj_home=str(root / ".omj"),
                hermes_home=str(root / ".hermes"),
                scope=None,
                dry_run=False,
            )
            result = setup_commands._apply_result(args)
            config_path = Path(result["config"])
            config_text = config_path.read_text(encoding="utf-8")

            self.assertTrue(result["changed"])
            self.assertEqual(result["message"], "recorded plugins.entries.omj.settings.omj_home")
            self.assertEqual(
                result["messages"],
                ["created skills.external_dirs", "recorded plugins.entries.omj.settings.omj_home"],
            )
            self.assertIn(str(Path(result["skills_dir"]).resolve()), config_text)
            self.assertIn(f"omj_home: '{str(Path(result['omj_home']).resolve())}'", config_text)
            self.assertEqual(result["omj_home"], str(Path(args.omj_home).resolve()))


if __name__ == "__main__":
    unittest.main()
