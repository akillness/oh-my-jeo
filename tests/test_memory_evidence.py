"""Black-box contract tests for the OMJ-local memory evidence report.

The tests invoke a fresh ``omj memory evidence`` process. Fixtures contain
only OMJ-owned record/candidate files and an explicitly supplied JSONL session
record; Hermes state databases and native memory files are never evidence.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest import mock
from _local_package import load_local_package

load_local_package()

from omj.paths import OmjPaths  # noqa: E402
from omj.quality.memory_evidence import build_memory_evidence  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
DAY = 86_400
NOW = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc).timestamp()
SINCE = NOW - 7 * DAY
IN_WINDOW = NOW - 2 * DAY
OUTSIDE = SINCE - 1
CANARY = "RAW-MEMORY-CANARY-DO-NOT-REPORT"
SECRET = "credential=super-secret-value"


def _iso(value: float) -> str:
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _call(call_id: str, name: str, arguments: object) -> dict[str, object]:
    return {
        "id": call_id,
        "call_id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments, sort_keys=True)},
    }


def _deep_json(depth: int) -> str:
    return '{"next":' * depth + '"leaf"' + ("}" * depth)


def _deep_call(depth: int) -> dict[str, object]:
    return {
        "id": "deep",
        "call_id": "deep",
        "type": "function",
        "function": {"name": "omj_memory", "arguments": _deep_json(depth)},
    }


def _deep_wrapper_call(depth: int) -> dict[str, object]:
    return {
        "id": "deep",
        "call_id": "deep",
        "type": "function",
        "function": {
            "name": "tool_call",
            "arguments": json.dumps({"name": "omj_memory", "arguments": _deep_json(depth)}),
        },
    }


def _lifecycle_record(record_id: str, deadline_key: str, deadline: str) -> dict[str, object]:
    record = _record(record_id, IN_WINDOW)
    record.update(
        {
            "revision": 1,
            "admission": {"state": "approved_manual"},
            "staleness": {"resolution": "resolved", deadline_key: deadline},
        }
    )
    return record



def _write_jsonl(path: Path, rows: list[object], *, trailing: str | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows) + (trailing or ""), encoding="utf-8")
    return path


def _record(record_id: str, created_at: float, *, status: str = "approved", source: str = "operator") -> dict[str, object]:
    return {
        "schema_version": "project_memory_record/v1",
        "record_id": record_id,
        "record_type": "fact",
        "summary": CANARY,
        "scope": {"kind": "project", "ref": "default"},
        "source": source,
        "source_ref": "fixture",
        "review_status": status,
        "approved_by": "fixture-reviewer",
        "approved_at": _iso(created_at),
        "created_at": _iso(created_at),
        "updated_at": _iso(created_at),
        "claim_boundary": "prepared context only",
    }


def _candidate(candidate_id: str, created_at: float, *, status: str) -> dict[str, object]:
    return {
        "schema_version": "project_memory_candidate/v1",
        "candidate_id": candidate_id,
        "record_type": "fact",
        "summary": CANARY,
        "scope": {"kind": "project", "ref": "default"},
        "source": "cli",
        "status": status,
        "created_at": _iso(created_at),
    }


def _write_store(root: Path) -> None:
    records = root / ".omj" / "memory" / "records"
    candidates = root / ".omj" / "memory" / "candidates"
    records.mkdir(parents=True)
    candidates.mkdir(parents=True)
    for record in (_record("r-in", IN_WINDOW), _record("r-boundary", SINCE), _record("r-old", OUTSIDE)):
        (records / f"{record['record_id']}.json").write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
    for candidate in (
        _candidate("c-pending", IN_WINDOW, status="pending_review"),
        _candidate("c-private", IN_WINDOW, status="sk-private-abc"),
        _candidate("c-unsafe", IN_WINDOW, status="private status with secret"),
        _candidate("c-rejected-old", OUTSIDE, status="rejected"),
    ):
        (candidates / f"{candidate['candidate_id']}.json").write_text(json.dumps(candidate, sort_keys=True), encoding="utf-8")


def _session_rows() -> list[dict[str, object]]:
    return [
        # c1 is repeated by compaction in the same session; it counts once.
        {"session_id": "s-one", "role": "assistant", "timestamp": IN_WINDOW, "tool_calls": [_call("c1", "omj_memory", {"action": "capture", "summary": CANARY})], "content": SECRET},
        {"session_id": "s-one", "role": "tool", "timestamp": IN_WINDOW + 1, "tool_call_id": "c1", "tool_name": "omj_memory", "content": json.dumps({"action": "capture", "status": "remembered", "display_line": CANARY})},
        {"session_id": "s-one", "role": "assistant", "timestamp": IN_WINDOW + 2, "tool_calls": [_call("c1", "omj_memory", {"action": "sta"})], "content": "compacted"},
        {"session_id": "s-one", "role": "tool", "timestamp": IN_WINDOW + 3, "tool_call_id": "c1", "tool_name": "omj_memory", "content": "[omj_memory] result truncated"},
        # Direct call without a result and non-object result preserve partial states.
        {"session_id": "s-one", "role": "assistant", "timestamp": IN_WINDOW + 4, "tool_calls": [_call("c2", "omj_memory", {"action": "capture"})], "content": ""},
        {"session_id": "s-one", "role": "assistant", "timestamp": IN_WINDOW + 5, "tool_calls": [_call("c3", "omj_memory", {"action": "status"})], "content": ""},
        {"session_id": "s-one", "role": "tool", "timestamp": IN_WINDOW + 6, "tool_call_id": "c3", "tool_name": "omj_memory", "content": "[]"},
        # One-entry generic wrapper is accepted and attributed to its wrapped tool.
        {"session_id": "s-one", "role": "assistant", "timestamp": IN_WINDOW + 7, "tool_calls": [_call("c4", "tool_call", {"name": "omj_memory", "arguments": {"action": "capture"}})], "content": ""},
        {"session_id": "s-one", "role": "tool", "timestamp": IN_WINDOW + 8, "tool_call_id": "c4", "tool_name": "omj_memory", "content": json.dumps({"action": "capture", "status": "pending_review"})},
        # More than one wrapped call is refused, not an observed memory call.
        {"session_id": "s-one", "role": "assistant", "timestamp": IN_WINDOW + 9, "tool_calls": [_call("c5", "tool_call", {"calls": [{"name": "omj_memory", "arguments": {"action": "capture"}}, {"name": "omj_memory", "arguments": {"action": "status"}}]})], "content": ""},
        {"session_id": "s-one", "role": "tool", "timestamp": IN_WINDOW + 10, "tool_call_id": "c5", "tool_name": "tool_call", "content": json.dumps({"error": "tool_call refused"})},
        # Result-only rows are disclosed separately, not turned into a call.
        {"session_id": "s-one", "role": "tool", "timestamp": IN_WINDOW + 11, "tool_call_id": "c6", "tool_name": "omj_memory", "content": json.dumps({"action": "capture", "status": "remembered"})},
        # A confirmed status is an operator receipt, not an observed native write.
        {"session_id": "s-one", "role": "assistant", "timestamp": IN_WINDOW + 12, "tool_calls": [_call("c7", "omj_memory", {"action": "confirm"})], "content": ""},
        {"session_id": "s-one", "role": "tool", "timestamp": IN_WINDOW + 13, "tool_call_id": "c7", "tool_name": "omj_memory", "content": json.dumps({"action": "confirm", "status": "confirmed"})},
        # Same call id in a different session is a distinct call.
        {"session_id": "s-two", "role": "assistant", "timestamp": SINCE, "tool_calls": [_call("c1", "omj_memory", {"action": "demote"})], "content": ""},
        {"session_id": "s-two", "role": "tool", "timestamp": SINCE, "tool_call_id": "c1", "tool_name": "omj_memory", "content": json.dumps({"action": "demote", "status": "demoted"})},
        # Unrelated traffic must remain unknown, never silently zero.
        {"session_id": "s-two", "role": "assistant", "timestamp": SINCE, "tool_calls": [_call("u1", "terminal", {"command": "echo " + CANARY})], "content": ""},
        {"session_id": "s-two", "role": "tool", "timestamp": SINCE, "tool_call_id": "u1", "tool_name": "terminal", "content": json.dumps({"output": CANARY})},
        # Structured timestamp is outside; message text must not affect the window.
        {"session_id": "s-two", "role": "assistant", "timestamp": OUTSIDE, "tool_calls": [_call("old", "omj_memory", {"action": "capture", "summary": "old"})], "content": "inside-window words"},
        {"session_id": "s-two", "role": "tool", "timestamp": OUTSIDE, "tool_call_id": "old", "tool_name": "omj_memory", "content": json.dumps({"action": "capture", "status": "remembered"})},
    ]


def _snapshot(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


def _run(root: Path, *args: str, json_output: bool = True, clock: float | None = None) -> tuple[int, str, str, dict[str, object] | None]:
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "tests"), str(ROOT / "src")))
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if json_output:
        env["OMJ_OUTPUT"] = "json"
    else:
        env.pop("OMJ_OUTPUT", None)
    cli_args = ["--omj-home", str(root / ".omj"), "--hermes-home", str(root / ".hermes"), *args]
    if clock is None:
        command = [sys.executable, "-B", "-m", "omj.cli", *cli_args]
    else:
        frozen_code = (
            "class FrozenDateTime:\n"
            "    @classmethod\n"
            "    def now(cls, tz=None):\n"
            f"        return RealDateTime.fromtimestamp({float(clock)!r}, tz)\n"
            "    @classmethod\n"
            "    def fromtimestamp(cls, *args, **kwargs):\n"
            "        return RealDateTime.fromtimestamp(*args, **kwargs)\n"
            "    @classmethod\n"
            "    def fromisoformat(cls, *args, **kwargs):\n"
            "        return RealDateTime.fromisoformat(*args, **kwargs)\n"
        )
        launcher = (
            "import datetime,runpy; RealDateTime=datetime.datetime; "
            f"exec({frozen_code!r}); "
            "import omj.quality.memory_evidence as evidence; evidence.datetime=FrozenDateTime; "
            "runpy.run_module('omj.cli', run_name='__main__')"
        )
        command = [sys.executable, "-B", "-c", launcher, *cli_args]
    completed = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True, check=False)
    payload = None
    if completed.stdout.strip() and json_output:
        try:
            value = json.loads(completed.stdout)
        except json.JSONDecodeError:
            value = None
        if isinstance(value, dict):
            payload = value
    return completed.returncode, completed.stdout, completed.stderr, payload


class MemoryEvidenceSourcePrivacyTests(unittest.TestCase):
    def test_real_scanner_allowlists_private_and_credential_statuses(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            candidates = root / ".omj" / "memory" / "candidates"
            for candidate_id, status in (
                ("c-ghp", "ghp_secret_token"),
                ("c-akia", "AKIAIOSFODNN7EXAMPLE"),
                ("c-xox", "xoxb-1234567890-secret"),
            ):
                candidate = _candidate(candidate_id, IN_WINDOW, status=status)
                (candidates / f"{candidate_id}.json").write_text(json.dumps(candidate, sort_keys=True), encoding="utf-8")
            payload = build_memory_evidence(OmjPaths(root / ".omj", root / ".hermes"), days=7, now=NOW)

        store = payload["omj_store"]
        self.assertEqual(store["read_state"], "read")
        self.assertEqual(store["candidates"]["total"], 7)
        self.assertEqual(store["candidates"]["created_in_window"], 6)
        self.assertEqual(store["candidates"]["by_status"], {"(other)": 5, "pending_review": 1})
        serialized = json.dumps(payload, ensure_ascii=False)
        for secret in ("sk-private-abc", "private status with secret", "ghp_secret_token", "AKIAIOSFODNN7EXAMPLE", "xoxb-1234567890-secret"):
            self.assertNotIn(secret, serialized)
        for prefix in ("sk-private-", "ghp_", "AKIA", "xox"):
            self.assertNotIn(prefix, serialized)
    def test_malformed_scanner_source_state_is_incomplete_not_a_consumer_crash(self) -> None:
        scanned = {
            "read_state": "complete",
            "complete": True,
            "limit_reached": False,
            "errors": [],
            "records": [],
            "candidates": [],
            "budget": {"complete": True},
            "sources": {
                "records": {"read_state": [], "complete": True},
                "candidates": {"read_state": "read", "complete": True},
            },
        }
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with mock.patch("omj.workflows.memory.scan_governed_memory", return_value=scanned):
                payload = build_memory_evidence(OmjPaths(root / ".omj", root / ".hermes"), days=7, now=NOW)
        self.assertFalse(payload["ok"])
        store = payload["omj_store"]
        self.assertEqual(store["read_state"], "partial")
        self.assertFalse(store["complete"])
        self.assertEqual(store["sources"]["records"]["read_state"], "partial")
        self.assertIsNone(store["records"]["total"])

    def test_explicit_empty_admission_state_does_not_fall_back_to_approved_review_status(self) -> None:
        for admission_state in (None, ""):
            with self.subTest(admission_state=admission_state), TemporaryDirectory() as tmp:
                root = Path(tmp)
                _write_store(root)
                record = _record("r-explicit-admission", IN_WINDOW)
                record["admission"] = {"state": admission_state}
                records = root / ".omj" / "memory" / "records"
                (records / "r-explicit-admission.json").write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
                status, _stdout, stderr, payload = _run(root, "memory", "evidence", clock=NOW)
            self.assertEqual((status, stderr), (0, ""))
            assert payload is not None
            section = payload["omj_store"]["records"]
            self.assertEqual(section["total"], 3)
            self.assertEqual(section["not_admitted"], 1)
            self.assertEqual(section["pending_active"], 0)
            self.assertEqual(section["by_unadmitted_state"], {"other": 1})


    def test_pending_active_record_is_excluded_from_admitted_snapshot(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            pending = _record("r-pending", IN_WINDOW, status="pending_review")
            records = root / ".omj" / "memory" / "records"
            (records / "r-pending.json").write_text(json.dumps(pending, sort_keys=True), encoding="utf-8")
            status, _stdout, stderr, payload = _run(root, "memory", "evidence", clock=NOW)
        self.assertEqual((status, stderr), (0, ""))
        assert payload is not None
        records_section = payload["omj_store"]["records"]
        self.assertEqual(records_section["total"], 3)
        self.assertEqual(records_section["created_in_window"], 2)
        self.assertEqual(records_section["by_admission_state"], {"approved_manual": 3})
        self.assertEqual(records_section["pending_active"], 1)
        self.assertNotIn("r-pending", json.dumps(payload, ensure_ascii=False))

    def test_store_refusals_and_skipped_links_are_incomplete_not_healthy_zero(self) -> None:
        cases = ("linked_directory", "linked_leaf", "corrupt", "unsupported", "directory_leaf")
        for case in cases:
            with self.subTest(case=case), TemporaryDirectory() as tmp:
                root = Path(tmp)
                _write_store(root)
                records = root / ".omj" / "memory" / "records"
                if case == "linked_directory":
                    replacement = root / "foreign-records"
                    replacement.mkdir()
                    (replacement / "foreign.json").write_text("{}", encoding="utf-8")
                    for child in records.iterdir():
                        child.unlink()
                    records.rmdir()
                    records.symlink_to(replacement, target_is_directory=True)
                elif case == "linked_leaf":
                    linked = root / "foreign.json"
                    linked.write_text("{}", encoding="utf-8")
                    (records / "linked.json").symlink_to(linked)
                elif case == "corrupt":
                    (records / "corrupt.json").write_text("{not-json", encoding="utf-8")
                elif case == "unsupported":
                    (records / "unsupported.json").write_text(json.dumps({"schema_version": "unknown/v9"}), encoding="utf-8")
                else:
                    (records / "directory.json").mkdir()
                status, _stdout, stderr, payload = _run(root, "memory", "evidence", clock=NOW)
                self.assertEqual((status, stderr), (3, ""))
                assert payload is not None
                self.assertFalse(payload["ok"])
                self.assertNotEqual(payload["omj_store"]["read_state"], "read")
                record_headline = next(row for row in payload["headline"] if row["derived_from"] == "omj_store.records.total")
                self.assertFalse(record_headline["observed"])
                self.assertIsNone(record_headline["count"])

    def test_legacy_status_lineage_and_incident_redact_each_metadata_axis(self) -> None:
        status_values = (
            "ghp_12345678901234567890",
            "AKIAIOSFODNN7EXAMPLE",
            "xoxb-1234567890-abcdefghijkl",
            "sk-live-12345678901234567890",
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            candidates = root / ".omj" / "memory" / "candidates"
            for index, value in enumerate(status_values):
                candidate = _candidate(f"c-credential-{index}", IN_WINDOW, status=value)
                (candidates / f"c-credential-{index}.json").write_text(json.dumps(candidate, sort_keys=True), encoding="utf-8")
            plain = _candidate("c-plain", IN_WINDOW, status="pending_review")
            (candidates / "c-plain.json").write_text(json.dumps(plain, sort_keys=True), encoding="utf-8")
            for field, token in (
                ("source", "ghp_abcdefghijklmnopqrstuv"),
                ("source_ref", "AKIA1234567890ABCDEF"),
                ("source_class", "xoxb-1234567890-abcdefghijkl"),
            ):
                record = _record(f"r-{field}", IN_WINDOW, source="plain-source")
                record["source_ref"] = "plain-ref"
                record["source_class"] = "plain-class"
                record["derived_from"] = ["plain-provenance"]
                record[field] = token
                record_path = root / ".omj" / "memory" / "records" / f"r-{field}.json"
                record_path.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
            before = _snapshot(root)
            status, _stdout, stderr, status_payload = _run(root, "memory", "status")
            self.assertEqual((status, stderr), (0, ""))
            assert status_payload is not None
            statuses = status_payload["counts"]["candidate_statuses"]
            self.assertEqual(statuses, {"(other)": 6, "pending_review": 2, "rejected": 1})
            serialized_status = json.dumps(status_payload, ensure_ascii=False)
            for value in status_values:
                self.assertNotIn(value, serialized_status)
            for field, token in (
                ("source", "ghp_abcdefghijklmnopqrstuv"),
                ("source_ref", "AKIA1234567890ABCDEF"),
                ("source_class", "xoxb-1234567890-abcdefghijkl"),
            ):
                for command in (("memory", "lineage", f"r-{field}"), ("memory", "recall-incident", "--record-id", f"r-{field}")):
                    with self.subTest(field=field, command=command[1]):
                        result_status, _result_stdout, result_stderr, result_payload = _run(root, *command)
                        self.assertEqual((result_status, result_stderr), (0, ""))
                        assert result_payload is not None
                        serialized = json.dumps(result_payload, ensure_ascii=False)
                        self.assertNotIn(token, serialized)
                        if field != "source":
                            self.assertIn("plain-source", serialized)
                        if field != "source_ref":
                            self.assertIn("plain-ref", serialized)
                        if field != "source_class":
                            self.assertIn("plain-class", serialized)
                        self.assertIn("plain-provenance", serialized)
            self.assertEqual(before, _snapshot(root))
    def test_recall_incident_redacts_nested_shared_metadata_axes(self) -> None:
        tokens = {
            "scope_ref": "ghp_abcdefghijklmnopqrstuv",
            "retention_origin": "xoxb-1234567890-abcdefghijkl",
            "staleness_query": "AKIA1234567890ABCDEF",
        }
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            record = _record("r-nested", IN_WINDOW)
            record["scope"] = {"kind": "project", "ref": tokens["scope_ref"]}
            record["retention"] = {"origin": tokens["retention_origin"]}
            record["staleness"] = {"query": tokens["staleness_query"]}
            record_path = root / ".omj" / "memory" / "records" / "r-nested.json"
            record_path.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
            status, _stdout, stderr, payload = _run(root, "memory", "recall-incident", "--record-id", "r-nested")
        self.assertEqual((status, stderr), (0, ""))
        assert payload is not None
        serialized = json.dumps(payload, ensure_ascii=False)
        for token in tokens.values():
            self.assertNotIn(token, serialized)
        self.assertIn("project", serialized)
    def test_oversized_record_is_rejected_before_parse(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            oversized = _record("r-oversized", IN_WINDOW)
            oversized["summary"] = "x" * (1_048_576 + 10_000)
            (root / ".omj" / "memory" / "records" / "r-oversized.json").write_text(
                json.dumps(oversized, sort_keys=True), encoding="utf-8"
            )
            status, _stdout, stderr, payload = _run(root, "memory", "evidence", clock=NOW)
        self.assertEqual((status, stderr), (3, ""))
        assert payload is not None
        self.assertFalse(payload["ok"])
        self.assertNotEqual(payload["omj_store"]["read_state"], "read")
        record_headline = next(row for row in payload["headline"] if row["derived_from"] == "omj_store.records.total")
        self.assertFalse(record_headline["observed"])
        self.assertNotIn("r-oversized", json.dumps(payload, ensure_ascii=False))
    def test_deeply_nested_record_is_refused_as_incomplete_not_a_consumer_crash(self) -> None:
        nested_open = "".join('{"next":' for _ in range(1_500))
        nested_raw = nested_open + json.dumps("leaf") + ("}" * 1_500)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            record = _record("r-deep", IN_WINDOW)
            record_json = json.dumps(record, sort_keys=True)
            record_path = root / ".omj" / "memory" / "records" / "r-deep.json"
            record_path.write_text(record_json[:-1] + ',"extra":' + nested_raw + "}", encoding="utf-8")
            status, _stdout, stderr, payload = _run(root, "memory", "evidence", clock=NOW)
        self.assertEqual((status, stderr), (3, ""))
        assert payload is not None
        self.assertFalse(payload["ok"])
        self.assertNotEqual(payload["omj_store"]["read_state"], "read")
        self.assertIsNone(payload["omj_store"]["records"]["total"])

    def test_scan_inventory_is_bounded_before_sorting_all_entries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            records = root / ".omj" / "memory" / "records"
            for index in range(4_097):
                record = {
                    "schema_version": "project_memory_record/v1",
                    "record_id": f"r-bound-{index:05d}",
                    "record_type": "fact",
                    "summary": "bounded scan fixture",
                    "scope": {"kind": "project", "ref": "default"},
                    "source": "operator",
                    "review_status": "approved",
                    "created_at": _iso(IN_WINDOW),
                }
                (records / f"r-bound-{index:05d}.json").write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
            payload = build_memory_evidence(OmjPaths(root / ".omj", root / ".hermes"), days=7, now=NOW)
        self.assertFalse(payload["ok"])
        self.assertNotEqual(payload["omj_store"]["read_state"], "read")

    def test_ambiguous_memory_timestamps_are_unknown_and_status_three(self) -> None:
        rows = [
            {"session_id": "s-ambiguous", "role": "assistant", "tool_calls": [_call("amb", "omj_memory", {"action": "capture"})], "content": ""},
            {"session_id": "s-ambiguous", "role": "tool", "tool_call_id": "amb", "tool_name": "omj_memory", "content": json.dumps({"status": "remembered"})},
            {"session_id": "s-wrapper", "role": "assistant", "timestamp": IN_WINDOW, "tool_calls": [_call("wrap", "tool_call", {"name": "omj_memory", "arguments": {"action": "capture"}})], "content": ""},
            {"session_id": "s-wrapper", "role": "tool", "tool_call_id": "wrap", "tool_name": "tool_call", "content": json.dumps({"action": "capture", "status": "remembered"})},
            {"session_id": "s-result", "role": "tool", "tool_call_id": "result-only", "tool_name": "omj_memory", "content": json.dumps({"status": "remembered"})},
        ]
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            session = _write_jsonl(root / "ambiguous.jsonl", rows)
            status, _stdout, stderr, payload = _run(root, "memory", "evidence", "--session-jsonl", str(session), clock=NOW)
        self.assertEqual((status, stderr), (3, ""))
        assert payload is not None
        self.assertFalse(payload["ok"])
        traffic = payload["session_records"]
        self.assertNotEqual(traffic["read_state"], "read")
        self.assertFalse(traffic["budget"]["complete"])
        self.assertIsNone(traffic["calls"]["total"])
        self.assertGreaterEqual(traffic["window"]["ambiguous_timestamps"], 1)
    def test_missing_wrapper_result_timestamp_is_unknown_and_status_three(self) -> None:
        rows = [
            {"session_id": "s-wrapper", "role": "assistant", "timestamp": IN_WINDOW, "tool_calls": [_call("wrap", "tool_call", {"name": "omj_memory", "arguments": {"action": "capture"}})], "content": ""},
            {"session_id": "s-wrapper", "role": "tool", "tool_call_id": "wrap", "tool_name": "tool_call", "content": json.dumps({"action": "capture", "status": "remembered"})},
        ]
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            session = _write_jsonl(root / "wrapper-result-missing-time.jsonl", rows)
            status, _stdout, stderr, payload = _run(root, "memory", "evidence", "--session-jsonl", str(session), clock=NOW)
        self.assertEqual((status, stderr), (3, ""))
        assert payload is not None
        traffic = payload["session_records"]
        self.assertFalse(payload["ok"])
        self.assertNotEqual(traffic["read_state"], "read")
        self.assertFalse(traffic["budget"]["complete"])
        self.assertIsNone(traffic["calls"]["total"])
        self.assertGreaterEqual(traffic["window"]["ambiguous_timestamps"], 1)
    def test_max_rows_probe_reads_one_byte_and_reports_actual_stream_bytes(self) -> None:
        first = {"session_id": "s-first", "role": "assistant", "timestamp": IN_WINDOW, "tool_calls": []}
        second = json.dumps({"session_id": "s-second", "role": "assistant", "timestamp": IN_WINDOW, "tool_calls": []}) + "x" * 100_000
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            session = _write_jsonl(root / "max-rows.jsonl", [first], trailing=second + "\n")
            original_open = Path.open
            session_size = session.stat().st_size
            observed_reads: list[int] = []

            class TrackingReader:
                def __init__(self, handle: object) -> None:
                    self._handle = handle

                def __enter__(self) -> "TrackingReader":
                    return self

                def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
                    self._handle.close()  # type: ignore[attr-defined]

                def readline(self, size: int = -1) -> bytes:
                    value = self._handle.readline(size)  # type: ignore[attr-defined]
                    observed_reads.append(len(value))
                    return value

                def read(self, size: int = -1) -> bytes:
                    value = self._handle.read(size)  # type: ignore[attr-defined]
                    observed_reads.append(len(value))
                    return value

                def __getattr__(self, name: str) -> object:
                    return getattr(self._handle, name)

            def open_spy(path: Path, *args: object, **kwargs: object) -> object:
                handle = original_open(path, *args, **kwargs)
                return TrackingReader(handle) if path == session else handle

            with mock.patch.object(Path, "open", new=open_spy):
                payload = build_memory_evidence(OmjPaths(root / ".omj", root / ".hermes"), days=7, now=NOW, session_jsonl=session, max_rows=1)
        assert payload is not None
        budget = payload["session_records"]["budget"]
        self.assertTrue(budget["row_limit_reached"], f"session={payload['session_records']!r} observed_reads={observed_reads!r}")
        self.assertEqual(budget["bytes_read"], sum(observed_reads))
        self.assertEqual(observed_reads[-1], 1)
        self.assertLess(budget["bytes_read"], session_size)

    def test_encoded_nested_session_values_are_bounded_unknown_and_traceback_free(self) -> None:
        cases = (
            ("control", None, 0),
            ("tool_calls", "tool_calls", 1_500),
            ("tool_calls", "tool_calls", 20_000),
            ("wrapper", "wrapper", 1_500),
            ("wrapper", "wrapper", 20_000),
            ("content", "content", 1_500),
            ("content", "content", 20_000),
        )
        for label, location, depth in cases:
            with self.subTest(label=label, depth=depth):
                with TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    _write_store(root)
                    call = _deep_wrapper_call(depth) if location == "wrapper" else _deep_call(depth)
                    if location in {"tool_calls", "wrapper"}:
                        rows = [
                            {"session_id": "s-deep", "role": "assistant", "timestamp": IN_WINDOW, "tool_calls": json.dumps([call]), "content": ""},
                        ]
                    elif location == "content":
                        rows = [
                            {"session_id": "s-deep", "role": "assistant", "timestamp": IN_WINDOW, "tool_calls": [_call("deep", "omj_memory", {"action": "capture"})], "content": ""},
                            {"session_id": "s-deep", "role": "tool", "timestamp": IN_WINDOW + 1, "tool_call_id": "deep", "tool_name": "omj_memory", "content": _deep_json(depth)},
                        ]
                    else:
                        rows = [
                            {"session_id": "s-control", "role": "assistant", "timestamp": IN_WINDOW, "tool_calls": json.dumps([_call("control", "omj_memory", {"action": "capture"})]), "content": ""},
                            {"session_id": "s-control", "role": "tool", "timestamp": IN_WINDOW + 1, "tool_call_id": "control", "tool_name": "omj_memory", "content": json.dumps({"action": "capture", "status": "remembered"})},
                        ]
                    if location is not None:
                        rows.insert(
                            0,
                            {"session_id": "s-unknown", "role": "assistant", "timestamp": IN_WINDOW, "tool_calls": [_call("unknown", "terminal", {"command": "echo bounded"})], "content": ""},
                        )
                    session = _write_jsonl(root / f"{label}-{depth}.jsonl", rows)
                    session_size = session.stat().st_size
                    self.assertLess(session_size, 1_048_576)
                    status, _stdout, stderr, payload = _run(root, "memory", "evidence", "--session-jsonl", str(session), clock=NOW)
                self.assertEqual(stderr, "")
                self.assertNotIn("Traceback", stderr)
                assert payload is not None
                traffic = payload["session_records"]
                budget = traffic["budget"]
                self.assertGreater(budget["bytes_read"], 0)
                self.assertEqual(budget["bytes_read"], session_size)
                self.assertLessEqual(budget["bytes_read"], 1_048_576)
                if location is None:
                    self.assertEqual(status, 0)
                    self.assertEqual(traffic["read_state"], "read")
                    self.assertEqual(traffic["calls"]["total"], 1)
                    self.assertTrue(budget["complete"])
                else:
                    self.assertEqual(status, 3)
                    self.assertFalse(payload["ok"])
                    self.assertEqual(traffic["read_state"], "partial")
                    self.assertFalse(budget["complete"])
                    self.assertIsNone(traffic["calls"]["total"])
                    self.assertGreaterEqual(traffic["unknown_traffic"], 1)

    def test_recall_incident_deadlines_are_normalized_and_invalid_values_close_replay(self) -> None:
        cases = (
            ("review_due_at", "2999-01-02T03:04:05+02:00", "2999-01-02T01:04:05Z", True, "eligible", False),
            ("open_expires_at", "2999-01-02T03:04:05+02:00", "2999-01-02T01:04:05Z", True, "eligible", False),
            ("review_due_at", "ghp_" + "A" * 24, "invalid", False, "unreadable_staleness", True),
            ("open_expires_at", "xoxb-" + "B" * 24, "invalid", False, "unreadable_expiry", True),
            ("review_due_at", "not-a-date", "invalid", False, "unreadable_staleness", False),
            ("open_expires_at", "not-a-date", "invalid", False, "unreadable_expiry", False),
        )
        for deadline_key, value, expected_deadline, eligible, expected_reason, sensitive in cases:
            with self.subTest(deadline_key=deadline_key, value=value):
                with TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    _write_store(root)
                    record = _lifecycle_record(f"r-deadline-{deadline_key}", deadline_key, value)
                    record_path = root / ".omj" / "memory" / "records" / f"{record['record_id']}.json"
                    record_path.write_text(json.dumps(record, sort_keys=True), encoding="utf-8")
                    status, _stdout, stderr, payload = _run(root, "memory", "recall-incident", "--record-id", str(record["record_id"]))
                self.assertEqual((status, stderr), (0, ""))
                assert payload is not None
                serialized = json.dumps(payload, ensure_ascii=False)
                if sensitive:
                    self.assertNotIn(value, serialized)
                replay = payload["replay"]
                self.assertEqual(replay["review_deadline"], expected_deadline)
                self.assertIs(replay["replay_eligible"], eligible)
                self.assertEqual(replay["reason_code"], expected_reason)

    def test_oversized_jsonl_is_bounded_and_consumed_bytes_are_accounted(self) -> None:
        oversized_line = json.dumps({"session_id": "s-big", "role": "assistant", "timestamp": IN_WINDOW, "tool_calls": []})
        oversized_line += "x" * (1_048_576 + 10_000 - len(oversized_line))
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            session = root / "oversized.jsonl"
            session.write_text(oversized_line + "\n", encoding="utf-8")
            status, _stdout, stderr, payload = _run(root, "memory", "evidence", "--session-jsonl", str(session), "--max-rows", "1", clock=NOW)
        self.assertEqual((status, stderr), (3, ""))
        assert payload is not None
        traffic = payload["session_records"]
        self.assertFalse(traffic["budget"]["complete"])
        self.assertTrue(traffic["budget"]["byte_limit_reached"])
        self.assertEqual(traffic["budget"]["oversized_rows"], 1)
        self.assertGreater(traffic["budget"]["bytes_read"], 0)
        self.assertLessEqual(traffic["budget"]["bytes_read"], 1_048_576)

class MemoryEvidenceCliTests(unittest.TestCase):
    def test_report_counts_current_records_and_candidates_by_admission_window(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            session = _write_jsonl(root / "session.jsonl", _session_rows())
            status, _stdout, stderr, payload = _run(root, "memory", "evidence", "--days", "7", "--session-jsonl", str(session), clock=NOW)
        self.assertEqual((status, stderr), (0, ""))
        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual(payload["schema_version"], "memory_evidence/v1")
        self.assertEqual(payload["window"]["days"], 7)
        store = payload["omj_store"]
        self.assertEqual(store["read_state"], "read")
        self.assertEqual(store["records"]["total"], 3)
        self.assertEqual(store["records"]["created_in_window"], 2)
        self.assertEqual(store["records"]["by_admission_state"], {"approved_manual": 3})
        self.assertEqual(store["records"]["by_source"], {"operator": 3})
        self.assertEqual(store["candidates"]["total"], 4)
        self.assertEqual(store["candidates"]["created_in_window"], 3)
        self.assertEqual(store["candidates"]["by_status"], {"(other)": 2, "pending_review": 1})
        serialized = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn(CANARY, serialized)
        self.assertNotIn("sk-private-abc", serialized)
        self.assertNotIn("private status with secret", serialized)

    def test_session_fixture_classifies_wrappers_deduplicates_session_call_ids_and_uses_timestamps(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            session = _write_jsonl(root / "session.jsonl", _session_rows())
            status, _stdout, stderr, payload = _run(root, "memory", "evidence", "--since", _iso(SINCE), "--session-jsonl", str(session), clock=NOW)
        self.assertEqual((status, stderr), (0, ""))
        assert payload is not None
        traffic = payload["session_records"]
        self.assertEqual(traffic["read_state"], "read")
        self.assertEqual(traffic["calls"]["total"], 6)
        self.assertEqual(traffic["calls"]["by_action_status"], {
            "capture": {"remembered": 1, "pending_review": 1, "(no_result)": 1},
            "confirm": {"confirmed": 1},
            "demote": {"demoted": 1},
            "status": {"(unparsed)": 1},
        })
        self.assertEqual(traffic["writes"]["observed"], 3)
        self.assertEqual(traffic["writes"]["confirmed_status_only"], 1)
        self.assertEqual(traffic["results_without_call"], 1)
        self.assertGreater(traffic["unknown_traffic"], 0)
        self.assertEqual(traffic["window"]["included_at_boundary"], 1)
        self.assertEqual(traffic["window"]["excluded_before_since"], 1)
        serialized = json.dumps(payload, ensure_ascii=False).lower()
        self.assertNotIn(CANARY.lower(), serialized)
        self.assertNotIn(SECRET.lower(), serialized)
        self.assertNotIn('"arguments"', serialized)
        self.assertNotIn('"content"', serialized)

    def test_window_validation_is_exclusive_and_fails_before_any_source_read(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "does-not-exist.jsonl"
            cases = (
                (("--days", "0"), "--days"),
                (("--days", "-1"), "--days"),
                (("--since", "nan"), "--since"),
                (("--since", "inf"), "--since"),
                (("--since", "2030-01-01T00:00:00Z"), "--since"),
                (("--days", "7", "--since", _iso(SINCE)), "exclusive"),
            )
            for args, marker in cases:
                with self.subTest(args=args):
                    status, stdout, stderr, payload = _run(root, "memory", "evidence", *args, "--session-jsonl", str(missing))
                    self.assertEqual(status, 2)
                    self.assertEqual(stdout, "")
                    self.assertIsNone(payload)
                    self.assertIn(marker, stderr.lower())
                    self.assertNotIn("no such file", stderr.lower())

    def test_missing_unreadable_and_partial_sources_are_not_reported_as_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            missing = root / "missing.jsonl"
            status, stdout, stderr, missing_payload = _run(root, "memory", "evidence", "--session-jsonl", str(missing))
            self.assertEqual((status, stderr), (3, ""))
            self.assertEqual(stdout.strip()[:1], "{")
            assert missing_payload is not None
            self.assertEqual(missing_payload["session_records"]["read_state"], "missing")
            self.assertIsNone(missing_payload["session_records"]["calls"]["total"])
            self.assertFalse(missing_payload["ok"])

            unreadable = root / "unreadable.jsonl"
            unreadable.mkdir()
            status, _stdout, stderr, unreadable_payload = _run(root, "memory", "evidence", "--session-jsonl", str(unreadable))
            self.assertEqual((status, stderr), (3, ""))
            assert unreadable_payload is not None
            self.assertEqual(unreadable_payload["session_records"]["read_state"], "unreadable")

            malformed = root / "malformed.jsonl"
            _write_jsonl(malformed, _session_rows(), trailing="not-json\n")
            status, _stdout, stderr, partial_payload = _run(root, "memory", "evidence", "--session-jsonl", str(malformed))
            self.assertEqual((status, stderr), (3, ""))
            assert partial_payload is not None
            self.assertEqual(partial_payload["session_records"]["read_state"], "partial")
            self.assertEqual(partial_payload["session_records"]["budget"]["malformed_rows"], 1)

    def test_budget_limits_are_explicit_and_absent_readable_store_is_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = _write_jsonl(root / "session.jsonl", _session_rows())
            status, _stdout, stderr, payload = _run(root, "memory", "evidence", "--session-jsonl", str(session), "--max-rows", "2")
            self.assertEqual((status, stderr), (3, ""))
            assert payload is not None
            self.assertFalse(payload["session_records"]["budget"]["complete"])
            self.assertTrue(payload["session_records"]["budget"]["row_limit_reached"])

            empty_root = root / "empty"
            (empty_root / ".omj" / "memory").mkdir(parents=True)
            status, _stdout, stderr, empty = _run(empty_root, "memory", "evidence")
            self.assertEqual((status, stderr), (0, ""))
            assert empty is not None
            self.assertTrue(empty["ok"])
            self.assertEqual(empty["omj_store"]["records"]["total"], 0)
            self.assertEqual(empty["omj_store"]["candidates"]["total"], 0)

    def test_text_and_json_derive_the_same_claims_without_writes_or_native_memory_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_store(root)
            native = root / ".hermes" / "memories"
            native.mkdir(parents=True)
            (native / "MEMORY.md").write_text(f"{SECRET}\n{CANARY}\n", encoding="utf-8")
            session = _write_jsonl(root / "session.jsonl", _session_rows())
            before = _snapshot(root)
            json_status, json_stdout, json_stderr, payload = _run(root, "memory", "evidence", "--session-jsonl", str(session), clock=NOW)
            text_status, text_stdout, text_stderr, _ = _run(root, "memory", "evidence", "--session-jsonl", str(session), json_output=False, clock=NOW)
            after = _snapshot(root)
        self.assertEqual((json_status, json_stderr), (0, ""))
        self.assertEqual((text_status, text_stderr), (0, ""))
        assert payload is not None
        self.assertIn("OMJ records", text_stdout)
        self.assertIn(str(payload["omj_store"]["records"]["total"]), text_stdout)
        self.assertIn(str(payload["omj_store"]["candidates"]["total"]), text_stdout)
        self.assertNotIn(CANARY, json_stdout + text_stdout)
        self.assertNotIn(SECRET, json_stdout + text_stdout)
        self.assertEqual(before, after)
        self.assertEqual(payload["redaction_policy"], "metadata_only")
        native_section = payload["native_memory"]
        self.assertEqual(native_section["read_state"], "unsupported")
        self.assertFalse(native_section["observed"])
        self.assertIsNone(native_section["headroom"])
        self.assertIsNone(native_section["freed_entries"])
        self.assertEqual(native_section["claim_boundary"], "Native Hermes memory/provider state is outside OMJ evidence scope.")
        prepared = payload["prepared_attachments"]
        self.assertEqual(prepared["read_state"], "unsupported")
        self.assertFalse(prepared["observed"])
        self.assertIsNot(prepared.get("served"), True)
        self.assertIsNot(prepared.get("used"), True)
        self.assertIsNot(prepared.get("confirmed_status_observed"), True)
        self.assertEqual(prepared["claim_boundary"], "Prepared attachments are not served/use evidence.")
        headline_by_source = {row["derived_from"]: row for row in payload["headline"]}
        self.assertEqual(headline_by_source["omj_store.records.total"]["count"], 3)
        self.assertIn("current admitted OMJ-local record snapshot", headline_by_source["omj_store.records.total"]["claim"])
        self.assertNotIn("last 7 days", headline_by_source["omj_store.records.total"]["claim"])
        self.assertIn("current OMJ-local candidate snapshot", headline_by_source["omj_store.candidates.total"]["claim"])
        self.assertNotIn("last 7 days", headline_by_source["omj_store.candidates.total"]["claim"])
        self.assertIn("last 7 days", headline_by_source["omj_store.candidates.created_in_window"]["claim"])
        self.assertEqual(headline_by_source["omj_store.candidates.total"]["count"], 4)
        self.assertEqual(headline_by_source["omj_store.candidates.created_in_window"]["count"], 3)

if __name__ == "__main__":
    unittest.main()
