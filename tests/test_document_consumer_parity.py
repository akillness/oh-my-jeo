from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


class DocumentConsumerParityTests(unittest.TestCase):
    """Exercise the persisted document-plan contract through the real CLI."""

    @staticmethod
    def _run_argv(root: Path, *args: str) -> tuple[subprocess.CompletedProcess[str], dict | None]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(root / "src")
        env["OMJ_OUTPUT"] = "json"
        completed = subprocess.run(
            [sys.executable, "-m", "omj.cli", *args],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        if not completed.stdout.strip():
            return completed, None
        try:
            return completed, json.loads(completed.stdout)
        except json.JSONDecodeError:
            return completed, None

    @classmethod
    def _run(cls, root: Path, omj_home: Path, hermes_home: Path, *args: str) -> tuple[subprocess.CompletedProcess[str], dict | None]:
        return cls._run_argv(
            root,
            "--omj-home",
            str(omj_home),
            "--hermes-home",
            str(hermes_home),
            *args,
        )

    def test_document_plan_continuation_and_resume_persist_across_fresh_processes(self) -> None:
        """The plan's generated mark command must be real and progress must survive process boundaries."""
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            omj_home = workspace / ".omj"
            hermes_home = workspace / ".hermes"
            source = workspace / "fixture.bin"
            source_bytes = (bytes(range(256)) * 31) + bytes(range(64))
            self.assertEqual(len(source_bytes), 8000)
            source.write_bytes(source_bytes)

            completed, payload = self._run(
                root,
                omj_home,
                hermes_home,
                "document",
                "plan",
                "--source",
                str(source),
                "--pages",
                "5",
                "--chars",
                "8000",
                "--lines",
                "100",
                "--budget-chars",
                "4000",
                "--chars-per-page",
                "1600",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(payload)
            assert payload is not None
            plan = payload["plan"]
            plan_id = plan["plan_id"]
            self.assertEqual(Path(payload["store"]["omj_home"]), omj_home.resolve())
            self.assertEqual(
                Path(payload["store"]["plan_path"]),
                omj_home.resolve() / "documents" / plan_id / "plan.json",
            )
            source_sha256 = hashlib.sha256(source_bytes).hexdigest()
            created_at = plan["created_at"]
            completed, replayed = self._run(
                root,
                omj_home,
                hermes_home,
                "document",
                "plan",
                "--source",
                str(source),
                "--pages",
                "5",
                "--chars",
                "8000",
                "--lines",
                "100",
                "--budget-chars",
                "4000",
                "--chars-per-page",
                "1600",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(replayed)
            assert replayed is not None
            self.assertEqual(replayed["plan"]["plan_id"], plan_id)
            self.assertEqual(replayed["plan"]["created_at"], created_at)
            self.assertEqual(replayed["plan"]["updated_at"], created_at)
            self.assertEqual(replayed["plan"]["ledger_summary"], plan["ledger_summary"])
            self.assertEqual(plan["plan_schema_version"], "document_chunk_plan/v1")
            self.assertEqual(plan["source"]["sha256"], source_sha256)
            self.assertEqual(plan["inputs"], {
                "pages": 5,
                "chars": 8000,
                "lines": 100,
                "outline": [],
                "budget_chars": 4000,
                "chars_per_page": 1600,
            })
            self.assertEqual(plan["range_count"], 3)
            self.assertEqual(
                [item["chars"] for item in plan["ranges"]],
                [{"start": 0, "end": 3200}, {"start": 3200, "end": 6400}, {"start": 6400, "end": 8000}],
            )
            self.assertEqual(plan["ledger_summary"]["counts"], {"covered": 0, "next": 1, "missing": 2})
            self.assertTrue(payload["boundary"]["extraction_or_ocr_performed"] is False)
            self.assertTrue(payload["boundary"]["prepared_is_not_observed"] is True)
            self.assertTrue(payload["boundary"]["source_digest_is_identity_only"] is True)
            self.assertTrue(payload["boundary"]["covered_mark_is_caller_statement"] is True)

            continuation = plan["delegation_hint"]["after_each_range"]
            continuation_tokens = shlex.split(continuation)
            self.assertEqual(continuation_tokens[0], "omj")
            self.assertEqual(
                Path(continuation_tokens[continuation_tokens.index("--omj-home") + 1]),
                Path(payload["store"]["omj_home"]),
            )
            self.assertEqual(
                Path(continuation_tokens[continuation_tokens.index("--hermes-home") + 1]),
                hermes_home.resolve(),
            )
            document_index = continuation_tokens.index("document")
            self.assertEqual(continuation_tokens[document_index : document_index + 2], ["document", "mark"])
            self.assertIn(plan_id, continuation_tokens)
            self.assertIn("<n>", continuation_tokens)
            continuation_tokens = [
                str(plan["next_range"]["chunk"]) if token == "<n>" else token
                for token in continuation_tokens
            ]
            self.assertEqual(continuation_tokens[continuation_tokens.index("--state") + 1], "covered")

            # Execute the emitted command as-is; do not prepend a second home selection.
            completed, marked = self._run_argv(root, *continuation_tokens[1:])
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(marked)
            assert marked is not None
            self.assertEqual(marked["plan"]["plan_id"], plan_id)
            self.assertEqual(marked["plan"]["source"]["sha256"], source_sha256)
            self.assertEqual(marked["plan"]["ranges"][0]["state"], "covered")
            self.assertEqual(marked["store"]["omj_home"], payload["store"]["omj_home"])

            # Exercise all caller-visible ledger states and bounded metadata notes.
            for chunk, state, note in (("2", "next", "queued for review"), ("3", "missing", "source evidence gap")):
                completed, marked = self._run(
                    root,
                    omj_home,
                    hermes_home,
                    "document",
                    "mark",
                    "--plan-id",
                    plan_id,
                    "--range",
                    chunk,
                    "--state",
                    state,
                    "--note",
                    note,
                    "--source",
                    str(source),
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertIsNotNone(marked)
                assert marked is not None
                self.assertEqual(marked["plan"]["ranges"][int(chunk) - 1]["state"], state)

            completed, listed = self._run(root, omj_home, hermes_home, "document", "list", "--all")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(listed)
            assert listed is not None
            self.assertEqual(listed["count"], 1)
            summary = listed["plans"][0]
            self.assertEqual(summary["plan_id"], plan_id)
            self.assertEqual(summary["source"]["sha256"], source_sha256)
            self.assertEqual(summary["source_digest"], source_sha256)
            self.assertEqual(summary["created_at"], created_at)
            self.assertEqual(summary["range_count"], 3)
            self.assertEqual(summary["ledger_summary"]["counts"], {"covered": 1, "next": 1, "missing": 1})

            completed, shown = self._run(root, omj_home, hermes_home, "document", "show", plan_id)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(shown)
            assert shown is not None
            self.assertEqual(shown["plan"]["plan_id"], plan_id)
            self.assertEqual(shown["plan"]["source"]["sha256"], source_sha256)
            self.assertEqual(shown["plan"]["created_at"], created_at)
            self.assertEqual(shown["plan"]["updated_at"], marked["plan"]["updated_at"])
            self.assertEqual(shown["plan"]["ranges"][1]["state"], "next")
            self.assertEqual(shown["plan"]["ranges"][2]["state"], "missing")

            completed, resumed = self._run(root, omj_home, hermes_home, "document", "resume", plan_id)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(resumed)
            assert resumed is not None
            self.assertEqual(resumed["plan"]["plan_id"], plan_id)
            self.assertEqual(resumed["plan"]["source"]["sha256"], source_sha256)
            self.assertEqual(resumed["plan"]["created_at"], created_at)
            self.assertEqual(resumed["plan"]["next_range"]["chunk"], 2)
            self.assertEqual(resumed["plan"]["ledger_summary"]["counts"], {"covered": 1, "next": 1, "missing": 1})

            completed, validated = self._run(root, omj_home, hermes_home, "document", "validate")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(validated)
            assert validated is not None
            self.assertTrue(validated["ok"])
            self.assertEqual(validated["plan_count"], 1)
            self.assertEqual(validated["plans"][0]["plan_id"], plan_id)
            self.assertTrue(validated["plans"][0]["source"]["ok"])


    def test_document_plan_persists_missing_final_range_after_prior_ranges_are_covered(self) -> None:
        """A missing terminal range remains durable when no next range can be promoted."""
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            omj_home = workspace / ".omj"
            hermes_home = workspace / ".hermes"
            source = workspace / "terminal.txt"
            source.write_bytes(b"terminal identity source")

            completed, payload = self._run(
                root,
                omj_home,
                hermes_home,
                "document",
                "plan",
                "--source",
                str(source),
                "--pages",
                "3",
                "--chars",
                "4800",
                "--lines",
                "60",
                "--budget-chars",
                "1600",
                "--chars-per-page",
                "1600",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(payload)
            assert payload is not None
            plan_id = payload["plan"]["plan_id"]
            self.assertEqual(payload["plan"]["range_count"], 3)

            for chunk, state, note in (
                ("1", "covered", "first range read"),
                ("2", "covered", "second range read"),
                ("3", "missing", "terminal range unavailable"),
            ):
                completed, marked = self._run(
                    root,
                    omj_home,
                    hermes_home,
                    "document",
                    "mark",
                    "--plan-id",
                    plan_id,
                    "--range",
                    chunk,
                    "--state",
                    state,
                    "--note",
                    note,
                    "--source",
                    str(source),
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertIsNotNone(marked)

            completed, shown = self._run(root, omj_home, hermes_home, "document", "show", plan_id)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(shown)
            assert shown is not None
            self.assertIsNone(shown["plan"]["next_range"])
            self.assertEqual(shown["plan"]["ledger_summary"]["counts"], {"covered": 2, "next": 0, "missing": 1})
            self.assertEqual(shown["plan"]["ranges"][-1]["state"], "missing")

            persisted = json.loads(Path(payload["store"]["plan_path"]).read_text(encoding="utf-8"))
            self.assertEqual(persisted["ledger"]["3"]["state"], "missing")
            self.assertEqual(
                [(event["chunk"], event["state"], event["note"]) for event in persisted["progress_history"]],
                [
                    (1, "covered", "first range read"),
                    (2, "covered", "second range read"),
                    (3, "missing", "terminal range unavailable"),
                ],
            )
    def test_document_plan_rejects_invalid_identity_ranges_notes_and_changed_source_without_writes(self) -> None:
        """Invalid continuation inputs fail before mutating the persisted plan."""
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            omj_home = workspace / ".omj"
            hermes_home = workspace / ".hermes"
            source = workspace / "source.txt"
            other = workspace / "other.txt"
            source.write_text("authoritative source\n", encoding="utf-8")
            other.write_text("different source\n", encoding="utf-8")

            completed, payload = self._run(
                root,
                omj_home,
                hermes_home,
                "document",
                "plan",
                "--source",
                str(source),
                "--pages",
                "2",
                "--chars",
                "2400",
                "--budget-chars",
                "1200",
                "--chars-per-page",
                "1200",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            assert payload is not None
            plan_id = payload["plan"]["plan_id"]
            baseline_updated_at = payload["plan"]["updated_at"]
            baseline_ledger_summary = payload["plan"]["ledger_summary"]
            plan_path = Path(payload["store"]["plan_path"])
            baseline_plan_bytes = plan_path.read_bytes()
            completed, ignored = self._run(
                root,
                omj_home,
                hermes_home,
                "document",
                "validate",
                "--source",
                str(source),
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIsNone(ignored)
            self.assertIn("requires --plan-id", completed.stderr)
            self.assertEqual(plan_path.read_bytes(), baseline_plan_bytes)

            invalid_calls = (
                ("covered gap", ("document", "mark", "--plan-id", plan_id, "--range", "2", "--state", "covered")),
                ("unknown plan", ("document", "show", "deadbeefdead")),
                ("wrong range", ("document", "mark", "--plan-id", plan_id, "--range", "99", "--state", "covered")),
                ("wrong source identity", ("document", "mark", "--plan-id", plan_id, "--range", "1", "--state", "covered", "--source", str(other))),
                ("missing source evidence", ("document", "mark", "--plan-id", plan_id, "--range", "1", "--state", "covered", "--source", str(workspace / "missing.txt"))),
                ("bounded note", ("document", "mark", "--plan-id", plan_id, "--range", "1", "--state", "covered", "--note", "x" * 501, "--source", str(source))),
            )
            for label, args in invalid_calls:
                with self.subTest(case=label):
                    completed, ignored = self._run(root, omj_home, hermes_home, *args)
                    self.assertEqual(completed.returncode, 2)
                    self.assertIsNone(ignored)
                    self.assertIn("omj:", completed.stderr)

            source.write_text("changed source\n", encoding="utf-8")
            completed, ignored = self._run(
                root,
                omj_home,
                hermes_home,
                "document",
                "mark",
                "--plan-id",
                plan_id,
                "--range",
                "1",
                "--state",
                "covered",
                "--source",
                str(source),
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIsNone(ignored)
            self.assertIn("source", completed.stderr.lower())
            source.write_text("authoritative source\n", encoding="utf-8")

            completed, shown = self._run(root, omj_home, hermes_home, "document", "show", plan_id)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            assert shown is not None
            self.assertEqual(shown["plan"]["updated_at"], baseline_updated_at)
            self.assertEqual(shown["plan"]["ledger_summary"], baseline_ledger_summary)

            completed, validated = self._run(root, omj_home, hermes_home, "document", "validate")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            assert validated is not None
            self.assertTrue(validated["ok"])
            self.assertEqual(validated["plan_count"], 1)

    def test_document_plan_caps_long_read_window_at_two_thousand_lines(self) -> None:
        """A declared range wider than Hermes' read limit remains bounded and resumable."""
        root = Path(__file__).resolve().parents[1]
        with TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            source = workspace / "long.txt"
            source.write_text("metadata-only source\n", encoding="utf-8")
            completed, payload = self._run(
                root,
                workspace / ".omj",
                workspace / ".hermes",
                "document",
                "plan",
                "--source",
                str(source),
                "--pages",
                "5",
                "--lines",
                "4000",
                "--budget-chars",
                "500000",
                "--chars-per-page",
                "100000",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            assert payload is not None
            read_window = payload["plan"]["ranges"][0]["read_window"]
            self.assertEqual(read_window["offset"], 1)
            self.assertEqual(read_window["end_line"], 4000)
            self.assertEqual(read_window["limit"], 2000)
            self.assertEqual(read_window["read_calls_estimated"], 2)
            self.assertEqual(read_window["basis"], "caller_lines")


if __name__ == "__main__":
    unittest.main()
