from __future__ import annotations

import json
import os
from pathlib import Path
import select
import subprocess
import sys
import tempfile
import time
import unittest
from _local_package import load_local_package


ROOT = Path(__file__).resolve().parents[1]

load_local_package()

from omj.document_chunk_plan import read_document_plan  # noqa: E402


_CHILD_SCRIPT = r"""
import json
import os
import sys

ready_fd = int(sys.argv[1])
start_fd = int(sys.argv[2])
root = sys.argv[3]
args = json.loads(sys.argv[4])
os.write(ready_fd, b"r")
os.close(ready_fd)
if os.read(start_fd, 1) != b"s":
    os._exit(125)
os.close(start_fd)
env = os.environ.copy()
env["PYTHONPATH"] = os.path.join(root, "src")
env["OMJ_OUTPUT"] = "json"
os.execve(sys.executable, [sys.executable, "-m", "omj.cli", *args], env)
"""

_CREATE_RACE_CHILD_SCRIPT = r"""
import json
import os
import subprocess
import sys

ready_fd = int(sys.argv[1])
start_fd = int(sys.argv[2])
root = sys.argv[3]
plan_args = json.loads(sys.argv[4])
mark_args = json.loads(sys.argv[5])
os.write(ready_fd, b"r")
os.close(ready_fd)
if os.read(start_fd, 1) != b"s":
    os._exit(125)
os.close(start_fd)
env = os.environ.copy()
env["PYTHONPATH"] = os.path.join(root, "src")
env["OMJ_OUTPUT"] = "json"
plan = subprocess.run(
    [sys.executable, "-m", "omj.cli", *plan_args],
    cwd=root,
    env=env,
    text=True,
    capture_output=True,
    check=False,
)
if plan.returncode != 0:
    sys.stderr.write(plan.stderr)
    sys.exit(plan.returncode)
result = {"plan": json.loads(plan.stdout)}
if mark_args:
    mark = subprocess.run(
        [sys.executable, "-m", "omj.cli", *mark_args],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if mark.returncode != 0:
        sys.stderr.write(mark.stderr)
        sys.exit(mark.returncode)
    result["mark"] = json.loads(mark.stdout)
sys.stdout.write(json.dumps(result))
"""


class DocumentIntegrityRegressionTests(unittest.TestCase):
    @staticmethod
    def _run(
        omj_home: Path,
        hermes_home: Path,
        *args: str,
        timeout: float = 10,
    ) -> tuple[subprocess.CompletedProcess[str], dict | None]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env["OMJ_OUTPUT"] = "json"
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "omj.cli",
                "--omj-home",
                str(omj_home),
                "--hermes-home",
                str(hermes_home),
                *args,
            ],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        if not completed.stdout.strip():
            return completed, None
        try:
            return completed, json.loads(completed.stdout)
        except json.JSONDecodeError:
            return completed, None

    @staticmethod
    def _plan(
        workspace: Path,
        *,
        source: Path | None = None,
        pages: int = 3,
        budget_chars: int = 1_000,
        chars_per_page: int = 500,
    ) -> tuple[Path, Path, str, dict]:
        source = source or (workspace / "paper.txt")
        if not source.exists():
            source.write_text("metadata-only fixture\n", encoding="utf-8")
        omj_home = workspace / ".omj"
        hermes_home = workspace / ".hermes"
        completed, payload = DocumentIntegrityRegressionTests._run(
            omj_home,
            hermes_home,
            "document",
            "plan",
            "--source",
            str(source),
            "--pages",
            str(pages),
            "--budget-chars",
            str(budget_chars),
            "--chars-per-page",
            str(chars_per_page),
        )
        if completed.returncode != 0 or payload is None:
            raise AssertionError(f"document plan failed: {completed.stderr}")
        return source, omj_home, str(payload["plan"]["plan_id"]), payload

    @staticmethod
    def _persisted(omj_home: Path, plan_id: str) -> dict:
        return read_document_plan(omj_home, plan_id)

    def _run_competing_marks(
        self,
        omj_home: Path,
        hermes_home: Path,
        plan_id: str,
        source: Path,
    ) -> list[tuple[int, str, dict | None]]:
        mark_args = (
            (
                "document",
                "mark",
                "--plan-id",
                plan_id,
                "--range",
                "1",
                "--state",
                "covered",
                "--note",
                "concurrent-covered",
                "--source",
                str(source),
            ),
            (
                "document",
                "mark",
                "--plan-id",
                plan_id,
                "--range",
                "1",
                "--state",
                "next",
                "--note",
                "stale-next",
                "--source",
                str(source),
            ),
            (
                "document",
                "mark",
                "--plan-id",
                plan_id,
                "--range",
                "1",
                "--state",
                "missing",
                "--note",
                "stale-missing",
                "--source",
                str(source),
            ),
        )
        processes: list[subprocess.Popen[str]] = []
        ready_reads: list[int] = []
        start_writes: list[int] = []
        try:
            for args in mark_args:
                ready_read, ready_write = os.pipe()
                start_read, start_write = os.pipe()
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        _CHILD_SCRIPT,
                        str(ready_write),
                        str(start_read),
                        str(ROOT),
                        json.dumps(
                            [
                                "--omj-home",
                                str(omj_home),
                                "--hermes-home",
                                str(hermes_home),
                                *args,
                            ]
                        ),
                    ],
                    cwd=ROOT,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    pass_fds=(ready_write, start_read),
                )
                os.close(ready_write)
                os.close(start_read)
                ready_reads.append(ready_read)
                start_writes.append(start_write)
                processes.append(process)

            pending = set(ready_reads)
            deadline = time.monotonic() + 5
            while pending:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self.fail("competing mark children did not reach the pre-lock gate")
                readable, _, _ = select.select(list(pending), [], [], remaining)
                if not readable:
                    self.fail("competing mark children did not reach the pre-lock gate")
                for descriptor in readable:
                    if os.read(descriptor, 1) != b"r":
                        self.fail("competing mark child sent an invalid readiness signal")
                    os.close(descriptor)
                    pending.remove(descriptor)

            for descriptor in start_writes:
                os.write(descriptor, b"s")
                os.close(descriptor)
            start_writes.clear()

            results: list[tuple[int, str, dict | None]] = []
            for process in processes:
                try:
                    stdout, stderr = process.communicate(timeout=10)
                except subprocess.TimeoutExpired as exc:
                    process.kill()
                    process.communicate()
                    self.fail(f"competing mark child exceeded timeout: {exc}")
                payload = None
                if stdout.strip():
                    try:
                        payload = json.loads(stdout)
                    except json.JSONDecodeError:
                        self.fail(f"competing mark emitted non-JSON output: {stdout!r}")
                results.append((process.returncode, stderr, payload))
            return results
        finally:
            for descriptor in ready_reads:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            for descriptor in start_writes:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            for process in processes:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)

    def _run_creation_race(
        self,
        omj_home: Path,
        hermes_home: Path,
        plan_id: str,
        source: Path,
    ) -> list[tuple[int, str, dict]]:
        common = [
            "--omj-home",
            str(omj_home),
            "--hermes-home",
            str(hermes_home),
        ]
        plan_args = [
            *common,
            "document",
            "plan",
            "--source",
            str(source),
            "--pages",
            "3",
            "--budget-chars",
            "1000",
            "--chars-per-page",
            "500",
        ]
        mark_args = [
            *common,
            "document",
            "mark",
            "--plan-id",
            plan_id,
            "--range",
            "1",
            "--state",
            "covered",
            "--note",
            "created-race-accepted",
            "--source",
            str(source),
        ]
        roles = ((plan_args, []), (plan_args, mark_args))
        processes: list[subprocess.Popen[str]] = []
        ready_reads: list[int] = []
        start_writes: list[int] = []
        try:
            for child_plan_args, child_mark_args in roles:
                ready_read, ready_write = os.pipe()
                start_read, start_write = os.pipe()
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-c",
                        _CREATE_RACE_CHILD_SCRIPT,
                        str(ready_write),
                        str(start_read),
                        str(ROOT),
                        json.dumps(child_plan_args),
                        json.dumps(child_mark_args),
                    ],
                    cwd=ROOT,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    pass_fds=(ready_write, start_read),
                )
                os.close(ready_write)
                os.close(start_read)
                ready_reads.append(ready_read)
                start_writes.append(start_write)
                processes.append(process)

            pending = set(ready_reads)
            deadline = time.monotonic() + 5
            while pending:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    self.fail("creation-race children did not reach the pre-lock gate")
                readable, _, _ = select.select(list(pending), [], [], remaining)
                if not readable:
                    self.fail("creation-race children did not reach the pre-lock gate")
                for descriptor in readable:
                    if os.read(descriptor, 1) != b"r":
                        self.fail("creation-race child sent an invalid readiness signal")
                    os.close(descriptor)
                    pending.remove(descriptor)
            for descriptor in start_writes:
                os.write(descriptor, b"s")
                os.close(descriptor)
            start_writes.clear()

            results: list[tuple[int, str, dict]] = []
            for process in processes:
                try:
                    stdout, stderr = process.communicate(timeout=10)
                except subprocess.TimeoutExpired as exc:
                    process.kill()
                    process.communicate()
                    self.fail(f"creation-race child exceeded timeout: {exc}")
                if process.returncode != 0:
                    self.fail(f"creation-race child failed: {stderr}")
                try:
                    payload = json.loads(stdout)
                except json.JSONDecodeError as exc:
                    self.fail(f"creation-race emitted non-JSON output: {stdout!r}")
                results.append((process.returncode, stderr, payload))
            return results
        finally:
            for descriptor in ready_reads:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            for descriptor in start_writes:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
            for process in processes:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=5)

    def test_cli_freezes_300_page_ranges_and_resume_in_authoritative_store(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = workspace / "paper.txt"
            source.write_text("prepared metadata only\n", encoding="utf-8")
            omj_home = workspace / ".omj"
            hermes_home = workspace / ".hermes"
            completed, payload = self._run(
                omj_home,
                hermes_home,
                "document",
                "plan",
                "--source",
                str(source),
                "--pages",
                "300",
                "--budget-chars",
                "100000",
                "--chars-per-page",
                "1600",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(payload)
            assert payload is not None
            plan_id = payload["plan"]["plan_id"]
            plan = payload["plan"]
            self.assertEqual(plan["range_count"], 5)
            self.assertEqual(
                [(entry["pages"]["start"], entry["pages"]["end"]) for entry in plan["ranges"]],
                [(1, 60), (61, 120), (121, 180), (181, 240), (241, 300)],
            )
            self.assertEqual(plan["assumptions"]["budget_chars"], 100000)
            self.assertEqual(plan["assumptions"]["chars_per_page"]["value"], 1600.0)
            self.assertTrue(all(entry["estimated_chars"] <= 100000 for entry in plan["ranges"]))
            for entry in plan["ranges"]:
                window = entry["read_window"]
                span = window["end_line"] - window["offset"] + 1
                self.assertGreaterEqual(window["offset"], 1)
                self.assertGreaterEqual(window["end_line"], window["offset"])
                self.assertEqual(window["limit"], min(2000, span))
                self.assertGreaterEqual(window["read_calls_estimated"], 1)
            self.assertEqual(payload["boundary"]["prepared_is_not_observed"], True)
            self.assertEqual(payload["boundary"]["extraction_or_ocr_performed"], False)
            authoritative = self._persisted(omj_home, plan_id)
            self.assertEqual(authoritative["plan_id"], plan_id)
            self.assertEqual(authoritative["progress_history"], [])

            completed, replayed = self._run(
                omj_home,
                hermes_home,
                "document",
                "plan",
                "--source",
                str(source),
                "--pages",
                "300",
                "--budget-chars",
                "100000",
                "--chars-per-page",
                "1600",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(replayed)
            assert replayed is not None
            self.assertEqual(replayed["plan"]["plan_id"], plan_id)
            self.assertEqual(replayed["plan"]["created_at"], plan["created_at"])
            self.assertEqual(replayed["plan"]["ranges"], plan["ranges"])

            completed, marked = self._run(
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
                "--note",
                "first range read",
                "--source",
                str(source),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(marked)
            completed, resumed = self._run(
                omj_home,
                hermes_home,
                "document",
                "resume",
                "--plan-id",
                plan_id,
                "--source",
                str(source),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(resumed)
            assert resumed is not None
            self.assertEqual(resumed["plan"]["next_range"]["chunk"], 2)
            self.assertEqual(self._persisted(omj_home, plan_id)["ledger"]["1"]["state"], "covered")

    def test_concurrent_create_or_reuse_preserves_marked_progress(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source, omj_home, plan_id, _ = self._plan(workspace)
            plan_path = omj_home / "documents" / plan_id / "plan.json"
            plan_path.unlink()

            results = self._run_creation_race(
                omj_home,
                workspace / ".hermes",
                plan_id,
                source,
            )
            self.assertEqual([result[0] for result in results], [0, 0])
            marked = [result[2]["mark"]["plan"] for result in results if "mark" in result[2]]
            self.assertEqual(len(marked), 1)
            self.assertEqual(marked[0]["ledger_summary"]["counts"]["covered"], 1)

            authoritative = self._persisted(omj_home, plan_id)
            self.assertEqual(authoritative["ledger"]["1"]["state"], "covered")
            self.assertEqual(authoritative["ledger"]["1"]["note"], "created-race-accepted")
            self.assertEqual(
                [(event["chunk"], event["state"], event["note"]) for event in authoritative["progress_history"]],
                [(1, "covered", "created-race-accepted")],
            )

            completed, replayed = self._run(
                omj_home,
                workspace / ".hermes",
                "document",
                "plan",
                "--source",
                str(source),
                "--pages",
                "3",
                "--budget-chars",
                "1000",
                "--chars-per-page",
                "500",
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(replayed)
            assert replayed is not None
            self.assertEqual(replayed["plan"]["plan_id"], plan_id)
            self.assertEqual(replayed["plan"]["ledger_summary"]["counts"]["covered"], 1)

    def test_cli_progress_is_append_only_and_rejected_regressions_preserve_authoritative_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source, omj_home, plan_id, _ = self._plan(workspace)
            completed, _ = self._run(
                omj_home,
                workspace / ".hermes",
                "document",
                "mark",
                "--plan-id",
                plan_id,
                "--range",
                "1",
                "--state",
                "covered",
                "--note",
                "accepted",
                "--source",
                str(source),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            accepted = self._persisted(omj_home, plan_id)
            self.assertEqual(accepted["ledger"]["1"]["state"], "covered")
            self.assertEqual(accepted["progress_history"][0]["note"], "accepted")
            self.assertEqual(accepted["progress_history"][0]["state"], "covered")
            self.assertTrue(accepted["progress_history"][0]["marked_at"])
            accepted_timestamp = accepted["progress_history"][0]["marked_at"]
            accepted_bytes = (omj_home / "documents" / plan_id / "plan.json").read_bytes()

            for stale_state in ("next", "missing"):
                completed, payload = self._run(
                    omj_home,
                    workspace / ".hermes",
                    "document",
                    "mark",
                    "--plan-id",
                    plan_id,
                    "--range",
                    "1",
                    "--state",
                    stale_state,
                    "--note",
                    f"stale-{stale_state}",
                    "--source",
                    str(source),
                )
                self.assertEqual(completed.returncode, 2, completed.stderr)
                self.assertIsNone(payload)
                self.assertEqual(
                    (omj_home / "documents" / plan_id / "plan.json").read_bytes(),
                    accepted_bytes,
                )
                self.assertIn("covered range 1 cannot regress", completed.stderr)

            completed, _ = self._run(
                omj_home,
                workspace / ".hermes",
                "document",
                "mark",
                "--plan-id",
                plan_id,
                "--range",
                "2",
                "--state",
                "next",
                "--note",
                "queued",
                "--source",
                str(source),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            final = self._persisted(omj_home, plan_id)
            self.assertEqual(final["ledger"]["1"]["state"], "covered")
            self.assertEqual(final["ledger"]["2"]["state"], "next")
            self.assertEqual(
                [(event["chunk"], event["state"], event["note"]) for event in final["progress_history"]],
                [(1, "covered", "accepted"), (2, "next", "queued")],
            )
            self.assertEqual(final["progress_history"][0]["marked_at"], accepted_timestamp)
            self.assertTrue(all(event["marked_at"] for event in final["progress_history"]))

    def test_competing_process_marks_keep_covered_monotonic_and_retain_prior_events(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source, omj_home, plan_id, _ = self._plan(workspace)
            completed, _ = self._run(
                omj_home,
                workspace / ".hermes",
                "document",
                "mark",
                "--plan-id",
                plan_id,
                "--range",
                "1",
                "--state",
                "covered",
                "--note",
                "prior-accepted",
                "--source",
                str(source),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            prior_timestamp = self._persisted(omj_home, plan_id)["progress_history"][0]["marked_at"]
            results = self._run_competing_marks(omj_home, workspace / ".hermes", plan_id, source)
            self.assertEqual(results[0][0], 0)
            self.assertEqual([result[0] for result in results[1:]], [2, 2])
            self.assertTrue(all("cannot regress" in result[1] for result in results[1:]))
            final = self._persisted(omj_home, plan_id)
            self.assertEqual(final["ledger"]["1"]["state"], "covered")
            self.assertEqual(
                [(event["chunk"], event["state"], event["note"]) for event in final["progress_history"]],
                [(1, "covered", "prior-accepted"), (1, "covered", "concurrent-covered")],
            )
            self.assertEqual(final["progress_history"][0]["marked_at"], prior_timestamp)
            self.assertEqual(final["ledger"]["1"]["note"], "concurrent-covered")

    def test_sensitive_unhashed_identity_rejects_same_stat_wrong_path_without_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source = workspace / ".env"
            other = workspace / "otherfile"
            source_bytes = b"TOKEN=abc123\n"
            source.write_bytes(source_bytes)
            other.write_bytes(source_bytes)
            source_stat = source.stat()
            os.utime(other, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns))
            self.assertEqual(source.stat().st_size, other.stat().st_size)
            self.assertEqual(source.stat().st_mtime_ns, other.stat().st_mtime_ns)
            _source, omj_home, plan_id, payload = self._plan(workspace, source=source)
            self.assertEqual(payload["plan"]["source"]["fingerprint_basis"], "refused_sensitive_name")
            self.assertEqual(payload["plan"]["source"]["identity_basis"], "size_and_mtime")
            plan_path = omj_home / "documents" / plan_id / "plan.json"
            baseline = plan_path.read_bytes()

            completed, ignored = self._run(
                omj_home,
                workspace / ".hermes",
                "document",
                "mark",
                "--plan-id",
                plan_id,
                "--range",
                "1",
                "--state",
                "covered",
                "--note",
                "wrong-source",
                "--source",
                str(other),
            )
            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertIsNone(ignored)
            self.assertIn("source identity changed", completed.stderr)
            self.assertEqual(plan_path.read_bytes(), baseline)

            completed, marked = self._run(
                omj_home,
                workspace / ".hermes",
                "document",
                "mark",
                "--plan-id",
                plan_id,
                "--range",
                "1",
                "--state",
                "covered",
                "--note",
                "canonical-source",
                "--source",
                str(source),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIsNotNone(marked)
            final = self._persisted(omj_home, plan_id)
            self.assertEqual(final["ledger"]["1"]["state"], "covered")
            self.assertEqual(final["progress_history"][0]["note"], "canonical-source")
            self.assertEqual(final["source"]["path"], str(source.resolve()))


if __name__ == "__main__":
    unittest.main()
