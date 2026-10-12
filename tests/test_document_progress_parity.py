from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from _cli_harness import run_cli
from _local_package import load_local_package

load_local_package()

from omj.document_chunk_plan import (  # noqa: E402
    DocumentPlanError,
    DocumentPlanMissing,
    DOCUMENT_CHUNK_PLAN_SCHEMA_VERSION,
    build_document_plan,
    fingerprint_source,
    mark_document_plan_chunk,
    normalize_plan_request,
    read_document_plan,
    validate_document_plan,
    write_document_plan,
)
from omj.long_document import (  # noqa: E402
    build_chunk_ledger,
    build_long_document_card,
    format_page_range,
    pages_per_range_for_budget,
    plan_page_ranges,
    validate_long_document_card,
)
from omj.paper_learning import (  # noqa: E402
    PAPER_LEARNING_INDEX_SCHEMA_VERSION,
    PAPER_LEARNING_PROGRESS_SCHEMA_VERSION,
    PAPER_LEARNING_RECORD_SCHEMA_VERSION,
    PaperLearningStoreError,
    build_paper_learning_record,
    list_paper_learning_records,
    paper_learning_record_exists,
    read_paper_progress_ledger,
    record_paper_progress,
    scan_paper_learning_store,
    show_paper_learning_record,
    validate_paper_learning_store,
    write_paper_learning_record,
)
from omj.paths import resolve_paths  # noqa: E402


class LongDocumentParityTests(unittest.TestCase):
    def test_page_ranges_cover_each_page_once_and_preserve_progress_anchors(self) -> None:
        ledger = build_chunk_ledger(
            125,
            pages_per_range=60,
            chars_per_page=1600,
            covered_ranges=("1-60",),
            scanned_ranges=("61-70",),
        )

        covered_pages = [page for item in ledger for page in range(item["page_start"], item["page_end"] + 1)]
        self.assertEqual(covered_pages, list(range(1, 126)))
        self.assertEqual([item["pages"] for item in ledger], ["1-60", "61-120", "121-125"])
        self.assertEqual([item["state"] for item in ledger], ["covered", "next", "missing"])
        self.assertTrue(ledger[1]["scanned"])
        self.assertEqual(format_page_range(7, 7), "7")
        self.assertEqual(plan_page_ranges(125, 60), [(1, 60), (61, 120), (121, 125)])

    def test_page_budget_rejects_non_positive_values_and_inconsistent_full_read_claims(self) -> None:
        for bad_budget, bad_density in ((0, 1600), (100000, 0), (-1, 1600)):
            with self.subTest(budget=bad_budget, density=bad_density):
                with self.assertRaises(ValueError):
                    pages_per_range_for_budget(bad_budget, bad_density)

        for bad_page_count in (True, 0, -1):
            with self.assertRaises(ValueError):
                build_long_document_card(page_count=bad_page_count)


        card = build_long_document_card(
            title="Contract",
            page_count=120,
            source_state="metadata_only",
            covered_ranges=("1-60",),
        )
        card["source_state"] = {
            "state": "full_text_observed",
            "page_count": 120,
            "covered_ranges": ["1-60"],
            "evidence_ref": "host:partial",
        }
        errors = validate_long_document_card(card)
        self.assertTrue(any("full_text_observed requires every ledger range" in error for error in errors))

    def test_three_hundred_pages_use_five_budgeted_ranges_and_delegate_only_above_threshold(self) -> None:
        card = build_long_document_card(
            title="A long paper",
            page_count=300,
            char_budget=100000,
            chars_per_page=1600,
        )

        self.assertEqual(card["read_budget"]["pages_per_range"], 60)
        self.assertEqual(card["read_budget"]["single_read_fits"], False)
        self.assertEqual(card["read_budget"]["estimated_read_calls"], 5)
        self.assertEqual(card["delegation_policy"]["mode"], "delegate_ranges")
        self.assertEqual([entry["pages"] for entry in card["chunk_ledger"]], ["1-60", "61-120", "121-180", "181-240", "241-300"])
        self.assertTrue(all(entry["chars"] <= 100000 for entry in card["chunk_ledger"]))

    def test_long_document_plan_discloses_prepared_boundary_without_extraction_claim(self) -> None:
        card = build_long_document_card(title="Prepared only", page_count=2, source_state="metadata_only")

        self.assertEqual(validate_long_document_card(card), [])
        self.assertIn("text_extraction", card["not_observed"])
        self.assertIn("scanned_page_ocr", card["not_observed"])
        self.assertIn("range_delegation", card["not_observed"])
        self.assertIn("page_anchored_coverage", card["coverage_policy"])
        self.assertFalse(card["source_state"]["state"] == "full_text_observed")

class DocumentChunkPlanParityTests(unittest.TestCase):
    def _plan(self, root: Path) -> tuple[Path, dict[str, object]]:
        source = root / "paper.txt"
        source.write_bytes(b"document identity bytes")
        request = normalize_plan_request(
            {
                "source": str(source),
                "pages": 10,
                "chars": 16000,
                "lines": 200,
                "budget_chars": 4000,
                "chars_per_page": 1600,
                "outline": [
                    {"title": "Introduction", "page": 1},
                    {"title": "Method", "page": 4},
                    {"title": "Results", "page": 8},
                ],
            }
        )
        return source, build_document_plan(
            request,
            fingerprint_source("paper.txt", source),
            now="2026-10-12T00:00:00Z",
        )

    def test_plan_preserves_offset_limit_and_outline_anchors_within_budget(self) -> None:
        with TemporaryDirectory() as tmp:
            source, plan = self._plan(Path(tmp))
            self.assertEqual(plan["schema_version"], DOCUMENT_CHUNK_PLAN_SCHEMA_VERSION)
            self.assertEqual(plan["source"]["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(plan["source"]["identity_basis"], "sha256")
            self.assertGreater(plan["range_count"], 1)
            for entry in plan["ranges"]:
                self.assertLessEqual(entry["estimated_chars"], 4000)
                self.assertGreaterEqual(entry["read_window"]["offset"], 1)
                self.assertGreaterEqual(entry["read_window"]["limit"], 1)
                self.assertLessEqual(entry["read_window"]["limit"], 2000)
            spans = [entry["chars"] for entry in plan["ranges"]]
            self.assertEqual(spans[0]["start"], 0)
            self.assertEqual(spans[-1]["end"], 16000)
            self.assertTrue(all(left["end"] == right["start"] for left, right in zip(spans, spans[1:])))

            sections = [section for entry in plan["ranges"] for section in entry["sections"]]
            self.assertEqual(list(dict.fromkeys(sections)), ["Introduction", "Method", "Results"])
            self.assertEqual(validate_document_plan(plan), plan)

    def test_plan_validation_rejects_boolean_zero_negative_and_under_budget_inputs(self) -> None:
        invalid = (
            {"pages": True},
            {"pages": 0},
            {"pages": -1},
            {"pages": 3, "budget_chars": 999},
            {"pages": 3, "chars_per_page": 49},
            {"pages": 3, "outline": [{"title": "Past end", "page": 4}]},
        )
        for overrides in invalid:
            with self.subTest(overrides=overrides):
                args = {"source": "paper.pdf", "pages": 3}
                args.update(overrides)
                with self.assertRaises(DocumentPlanError):
                    normalize_plan_request(args)

    def test_plan_discloses_prepared_not_observed_delegation_and_fingerprint_only_boundary(self) -> None:
        with TemporaryDirectory() as tmp:
            _source, plan = self._plan(Path(tmp))
            claim_boundary = plan["claim_boundary"]
            self.assertIn("OMJ performs no parsing, extraction, or OCR", claim_boundary)
            self.assertIn("may read source bytes only to fingerprint source identity", claim_boundary)
            self.assertEqual(plan["delegation_hint"]["status"], "prepared_not_observed")
            self.assertIn("not a dispatch", plan["delegation_hint"]["claim_boundary"])
            self.assertIn("caller_supplied", plan["provenance"].values())
    def test_mark_is_idempotent_for_same_chunk_state_and_refuses_bad_paths_or_notes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _source, plan = self._plan(root)
            write_document_plan(root / ".omj", plan)
            first = mark_document_plan_chunk(root / ".omj", plan["plan_id"], 1, "covered", "read once", now="2026-10-12T00:01:00Z")
            second = mark_document_plan_chunk(root / ".omj", plan["plan_id"], 1, "covered", "read once", now="2026-10-12T00:01:00Z")
            self.assertEqual(first["ledger"], second["ledger"])
            self.assertEqual(second["ledger"]["1"]["state"], "covered")
            self.assertEqual(second["ledger"]["2"]["state"], "next")
            with self.assertRaises(DocumentPlanMissing):
                read_document_plan(root / ".omj", "000000000000")
            with self.assertRaises(DocumentPlanError):
                mark_document_plan_chunk(root / ".omj", plan["plan_id"], 1, "covered", "x" * 501)
            with self.assertRaises(DocumentPlanError):
                read_document_plan(root / ".omj", "../escape")

    def test_sensitive_source_digest_is_refused_without_refusing_the_plan_label(self) -> None:
        with TemporaryDirectory() as tmp:
            secret = Path(tmp) / ".env"
            secret.write_text("TOKEN=private\n", encoding="utf-8")
            fingerprint = fingerprint_source(".env", secret)
            self.assertEqual(fingerprint["fingerprint_basis"], "refused_sensitive_name")
            self.assertEqual(fingerprint["sha256"], "")
            self.assertEqual(fingerprint["identity_basis"], "size_and_mtime")


class PaperDocumentProgressParityTests(unittest.TestCase):
    def _paths_and_record(self, root: Path):
        source = root / "paper.pdf"
        source.write_bytes(b"paper bytes, identity only")
        paths = resolve_paths(root / ".omj", root / ".hermes")
        record = build_paper_learning_record(
            title="Durable Paper",
            source_ref=str(source),
            authors=("Author",),
            level="expert",
            source_state="metadata_only",
            sections=("Abstract", "Introduction", "Method", "Results"),
            paper_id="paper-001",
            created_at="2026-10-12T00:00:00Z",
            created_at_ns=1,
        )
        return paths, source, record

    def test_record_progress_revision_and_store_index_survive_a_new_session_without_read_claims(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths, source, record = self._paths_and_record(root)
            written = write_paper_learning_record(paths, record)
            self.assertEqual(written["schema_version"], PAPER_LEARNING_RECORD_SCHEMA_VERSION)
            self.assertEqual(written["source"]["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(written["card"]["source_state"]["state"], "metadata_only")
            self.assertIn("full_pdf_extraction", written["card"]["not_observed"])

            with self.assertRaises(ValueError):
                record_paper_progress(paths, "paper-001", observed=("Method",))


            revised, first_entry = record_paper_progress(
                paths,
                "paper-001",
                covered=("Abstract",),
                observed=("Abstract",),
                next_section="Introduction",
                note="Resume at introduction.",
                source_state="file_text_extraction_observed",
                evidence_ref="host:abstract-1",
                recorded_at="2026-10-12T00:01:00Z",
            )
            revised, second_entry = record_paper_progress(
                paths,
                "paper-001",
                covered=("Introduction",),
                missing=("Results",),
                next_section="Method",
                note="Results were not present in the observed text.",
                recorded_at="2026-10-12T00:02:00Z",
            )

            self.assertEqual(revised["progress_count"], 2)
            self.assertEqual(revised["updated_at"], "2026-10-12T00:02:00Z")
            self.assertEqual(revised["reading"]["covered"], ["Abstract", "Introduction"])
            self.assertEqual(revised["reading"]["next"], "Method")
            self.assertEqual(revised["reading"]["missing"], ["Results"])
            self.assertEqual(first_entry["schema_version"], PAPER_LEARNING_PROGRESS_SCHEMA_VERSION)
            self.assertEqual(second_entry["missing"], ["Results"])

            resumed_paths = resolve_paths(root / ".omj", root / ".hermes")
            resumed = show_paper_learning_record(resumed_paths, "paper-001")
            entries, errors = read_paper_progress_ledger(resumed_paths, "paper-001")
            listed = list_paper_learning_records(resumed_paths)
            store = validate_paper_learning_store(resumed_paths)
            index = json.loads((resumed_paths.omj_home / "paper-learning" / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(resumed["progress_count"], 2)
            self.assertEqual(len(entries), 2)
            self.assertEqual(errors, [])
            self.assertEqual(listed[0]["paper_id"], "paper-001")
            self.assertTrue(store["ok"])
            self.assertEqual(index["schema_version"], PAPER_LEARNING_INDEX_SCHEMA_VERSION)
            self.assertEqual(index["papers"][0]["next"], "Method")

            with self.assertRaises(ValueError):
                record_paper_progress(resumed_paths, "paper-001", note="x" * 501)

    def test_store_scan_reports_corrupt_record_instead_of_dropping_it_and_refuses_unknown_ids(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths, _source, record = self._paths_and_record(root)
            write_paper_learning_record(paths, record)
            broken_dir = paths.omj_home / "paper-learning" / "paper-broken"
            broken_dir.mkdir(parents=True)
            (broken_dir / "card.json").write_text("{not json", encoding="utf-8")

            readable, unreadable = scan_paper_learning_store(paths)
            self.assertEqual([item["paper_id"] for item in readable], ["paper-001"])
            self.assertEqual(unreadable[0]["paper_id"], "paper-broken")
            self.assertEqual(unreadable[0]["reason_code"], "record_corrupt")
            report = validate_paper_learning_store(paths)
            self.assertFalse(report["ok"])
            self.assertTrue(any("paper-broken" in error for error in report["errors"]))
            self.assertTrue(paper_learning_record_exists(paths, "paper-001"))
            self.assertFalse(paper_learning_record_exists(paths, "../paper-001"))
            with self.assertRaises(PaperLearningStoreError) as exc_info:
                show_paper_learning_record(paths, "missing-paper")
            self.assertEqual(exc_info.exception.reason_code, "record_not_found")


class PaperLearningCliParityTests(unittest.TestCase):
    def test_cli_plan_list_show_progress_round_trip_when_wired(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "paper.txt"
            source.write_text("metadata source", encoding="utf-8")
            common = ["--omj-home", str(root / ".omj"), "--hermes-home", str(root / ".hermes")]

            status, stdout, stderr = run_cli(
                common + ["paper", "plan", "--title", "CLI Paper", "--source", str(source), "--section", "Abstract", "--section", "Method"],
            )
            self.assertEqual(status, 0)
            self.assertEqual(stderr, "")
            planned = json.loads(stdout)
            paper_id = planned["record"]["paper_id"]
            self.assertIn("full_pdf_extraction", planned["record"]["card"]["not_observed"])

            status, stdout, stderr = run_cli(common + ["paper", "list"])
            self.assertEqual(status, 0)
            self.assertEqual(stderr, "")
            listed = json.loads(stdout)
            self.assertEqual(listed["count"], 1)
            self.assertEqual(listed["papers"][0]["paper_id"], paper_id)

            status, stdout, stderr = run_cli(common + ["paper", "progress", paper_id, "--covered", "Abstract", "--next", "Method"])
            self.assertEqual(status, 0)
            self.assertEqual(stderr, "")
            progressed = json.loads(stdout)
            self.assertEqual(progressed["entry"]["covered"], ["Abstract"])
            self.assertEqual(progressed["record"]["reading"]["next"], "Method")

            status, stdout, stderr = run_cli(common + ["paper", "show", paper_id])
            self.assertEqual(status, 0)
            self.assertEqual(stderr, "")
            shown = json.loads(stdout)
            self.assertEqual(shown["record"]["progress_count"], 1)
            self.assertEqual(shown["ledger"][0]["next"], "Method")
            self.assertTrue(shown["boundary"]["prepared_is_not_observed"])


if __name__ == "__main__":
    unittest.main()
