from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from _local_package import load_local_package

load_local_package()

from omj.quality.agent_debug import (  # noqa: E402
    AgentDebugIncidentError,
    AgentDebugReportError,
    agent_debug_export_leaks,
    agent_debug_incident_errors,
    agent_debug_reference_errors,
    build_agent_debug_export,
    build_agent_debug_incident,
    build_agent_debug_report,
    format_agent_debug_report,
)
from omj.quality.session_file_activity import (  # noqa: E402
    SessionFileActivityError,
    build_session_file_activity,
    format_session_file_activity_summary,
)


SESSION = "20261012_101500_a1b2c3"
SIBLING = "20261012_101500_deadbe"
SECRET = "RAW-USER-PROMPT-AND-TOOL-SECRET"


def _call(call_id: str, name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": call_id,
        "call_id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments, sort_keys=True)},
    }


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> Path:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    return path


def _incident_rows(root: Path) -> list[dict[str, object]]:
    return [
        {
            "session_id": SESSION,
            "role": "user",
            "content": SECRET,
            "timestamp": 1_000.0,
            "_compressed_summary": 0,
        },
        {
            "session_id": SESSION,
            "role": "assistant",
            "content": "",
            "timestamp": 1_001.0,
            "tool_calls": [_call("c1", "terminal", {"command": "pytest tests/example.py", "timeout": 30})],
            "_compressed_summary": 0,
        },
        {
            "session_id": SESSION,
            "role": "tool",
            "content": json.dumps({"exit_code": 1, "error": SECRET, "output": SECRET}),
            "tool_call_id": "c1",
            "tool_name": "terminal",
            "timestamp": 1_002.0,
            "_compressed_summary": 0,
        },
        {
            "session_id": SESSION,
            "role": "assistant",
            "content": "",
            "timestamp": 1_003.0,
            "tool_calls": [_call("c2", "terminal", {"timeout": 30, "command": "pytest tests/example.py"})],
            "_compressed_summary": 0,
        },
        {
            "session_id": SESSION,
            "role": "tool",
            "content": json.dumps({"exit_code": 1, "error": SECRET}),
            "tool_call_id": "c2",
            "tool_name": "terminal",
            "timestamp": 1_004.0,
            "_compressed_summary": 0,
        },
        {
            "session_id": SESSION,
            "role": "assistant",
            "content": "",
            "timestamp": 1_005.0,
            "tool_calls": [_call("c3", "terminal", {"command": "pytest -x"})],
            "_compressed_summary": 0,
        },
        {
            "session_id": SESSION,
            "role": "tool",
            "content": json.dumps({"exit_code": 0, "output": "ok"}),
            "tool_call_id": "c3",
            "tool_name": "terminal",
            "timestamp": 1_006.0,
            "_compressed_summary": 0,
        },
        {
            "session_id": SESSION,
            "role": "user",
            "content": "compacted summary",
            "timestamp": 1_007.0,
            "_compressed_summary": 1,
        },
        {
            "session_id": SESSION,
            "role": "assistant",
            "content": "",
            "timestamp": 1_008.0,
            "tool_calls": [
                _call("f1", "read_file", {"path": str(root / "src" / "app.py")}),
                _call("f2", "write_file", {"path": "src/../src/app.py", "content": SECRET}),
                _call("f3", "patch", {"path": "../outside.txt", "old_string": "a", "new_string": "b"}),
            ],
            "_compressed_summary": 0,
        },
        {
            "session_id": SESSION,
            "role": "tool",
            "content": json.dumps({"content": "safe", "total_lines": 1}),
            "tool_call_id": "f1",
            "tool_name": "read_file",
            "timestamp": 1_009.0,
            "_compressed_summary": 0,
        },
        {
            "session_id": SESSION,
            "role": "tool",
            "content": json.dumps({"bytes_written": 4}),
            "tool_call_id": "f2",
            "tool_name": "write_file",
            "timestamp": 1_010.0,
            "_compressed_summary": 0,
        },
        {
            "session_id": SESSION,
            "role": "tool",
            "content": json.dumps({"success": False, "error": "outside"}),
            "tool_call_id": "f3",
            "tool_name": "patch",
            "timestamp": 1_011.0,
            "_compressed_summary": 0,
        },
        {
            "session_id": SIBLING,
            "role": "user",
            "content": "foreign session should not appear",
            "timestamp": 900.0,
            "_compressed_summary": 0,
        },
    ]


class IncidentEvidenceParityTests(unittest.TestCase):
    def test_jsonl_report_deduplicates_calls_and_cites_exact_rows_without_text(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            record = _write_jsonl(Path(tmp) / "session.jsonl", _incident_rows(root))
            report = build_agent_debug_report(None, SESSION, session_record=record)
            self.assertEqual(report["schema_version"], "agent_debug_report/v1")
            self.assertEqual(report["source"]["locator"], "record_line")
            self.assertEqual(report["source"]["label"], record.name)
            self.assertEqual(report["source"]["snapshot"]["bytes"], record.stat().st_size)
            self.assertEqual(
                [finding["finding_id"] for finding in report["findings"]],
                ["tool_error:3", "identical_retry_after_error:3", "tool_error:5", "compaction_boundary:8", "tool_error:12"],
            )
            retry = report["findings"][1]["citation"]
            self.assertEqual(retry["message_ids"], [3, 5])
            self.assertEqual(retry["tool_call_ids"], ["c1", "c2"])
            self.assertEqual(retry["tool_name"], "terminal")
            self.assertEqual(len(retry["arguments_sha256"]), 16)
            self.assertEqual(agent_debug_reference_errors(report, session_record=record), [])
            rendered = json.dumps(report) + format_agent_debug_report(report)
            self.assertNotIn(SECRET, rendered)
            self.assertNotIn(str(record), rendered)

    def test_jsonl_turn_window_limits_findings_and_preserves_turn_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            rows = _incident_rows(root)
            rows.insert(7, {"session_id": SESSION, "role": "user", "content": "second turn", "timestamp": 1_007.5})
            record = _write_jsonl(Path(tmp) / "turns.jsonl", rows)
            report = build_agent_debug_report(None, SESSION, session_record=record, turns=(1, 1))
            self.assertEqual(report["turns"], {"start": 1, "end": 1, "turn_count": 2})
            self.assertEqual(
                [finding["finding_id"] for finding in report["findings"]],
                ["tool_error:3", "identical_retry_after_error:3", "tool_error:5"],
            )

    def test_ambiguous_prefix_and_budget_are_explicit_errors_or_unknown(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            rows = _incident_rows(root)
            rows.append({"session_id": SIBLING, "role": "user", "content": "sibling", "timestamp": 1_020.0})
            record = _write_jsonl(Path(tmp) / "sessions.jsonl", rows)
            with self.assertRaisesRegex(AgentDebugReportError, "ambiguous"):
                build_agent_debug_report(None, "20261012_101500_", session_record=record)
            oversized = dict(rows[2], content=json.dumps({"exit_code": 1, "output": "x" * 50_000}))
            capped = _write_jsonl(Path(tmp) / "capped.jsonl", rows[:2] + [oversized] + rows[3:])
            report = build_agent_debug_report(None, SESSION, session_record=capped, max_row_bytes=256)
            self.assertFalse(report["budget"]["complete"])
            self.assertGreaterEqual(report["budget"]["oversized_rows"], 1)
            self.assertNotIn("tool_error:3", [finding["finding_id"] for finding in report["findings"]])
            self.assertTrue(report["unavailable"])
            with self.assertRaisesRegex(AgentDebugReportError, "at least 1"):
                build_agent_debug_report(None, SESSION, session_record=record, max_rows=0)

    def test_incident_keeps_competing_hypotheses_unobserved_and_export_redacted(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            record = _write_jsonl(Path(tmp) / "session.jsonl", _incident_rows(root))
            report = build_agent_debug_report(None, SESSION, session_record=record)
            incident = build_agent_debug_incident(report, observable="looping")
            hypotheses = incident["agent_failure_pattern_hypothesis"]["hypotheses"]
            self.assertGreaterEqual(len(hypotheses), 2)
            self.assertEqual(len({item["hypothesis_id"] for item in hypotheses}), len(hypotheses))
            self.assertTrue(all(item["observed"] is False for item in hypotheses))
            self.assertTrue(all(isinstance(item["evidence_for"], list) for item in hypotheses))
            self.assertTrue(all(isinstance(item["evidence_against"], list) for item in hypotheses))
            self.assertIn("finding:identical_retry_after_error:3", hypotheses[0]["evidence_for"])
            recovery = incident["contained_recovery_action"]
            self.assertFalse(recovery["executed"])
            self.assertTrue(recovery["requires_approval"])
            self.assertTrue(recovery["reversible"])
            self.assertEqual(agent_debug_incident_errors(report, incident), [])
            package = build_agent_debug_export({"report": report, "incident": incident}, session_record=record)
            self.assertEqual(agent_debug_export_leaks(package), [])
            self.assertNotIn(SECRET, json.dumps(package))

    def test_invalid_incident_and_missing_source_fail_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(AgentDebugReportError, "record"):
                build_agent_debug_report(None, SESSION, session_record=Path(tmp) / "missing.jsonl")
            forged = {"agent_failure_capture": {}, "agent_failure_pattern_hypothesis": {}, "contained_recovery_action": {}}
            with self.assertRaises(AgentDebugIncidentError):
                build_agent_debug_incident(forged, observable="looping")  # type: ignore[arg-type]


class SessionFileActivityParityTests(unittest.TestCase):
    def test_jsonl_file_lineage_normalizes_root_and_excludes_foreign_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            record = _write_jsonl(Path(tmp) / "session.jsonl", _incident_rows(root))
            payload = build_session_file_activity(None, SESSION, session_record=record, workspace=str(root), max_files=2)
            entries = {entry["path"]: entry for entry in payload["files"]}
            self.assertEqual(set(entries), {"src/app.py"})
            self.assertEqual(entries["src/app.py"]["extension"], ".py")
            self.assertEqual(len(entries["src/app.py"]["path_sha256"]), 16)
            self.assertEqual(payload["digests"]["paths"]["src/app.py"], entries["src/app.py"]["path_sha256"])
            self.assertEqual(
                [(item["operation"], item["outcome"]) for item in entries["src/app.py"]["activity"]],
                [("read", "succeeded"), ("write", "succeeded")],
            )
            self.assertEqual(payload["calls"]["by_tool"], {"read_file": 1, "write_file": 1, "patch": 1})
            self.assertEqual(payload["omitted_paths"]["by_reason"]["outside_workspace"], 1)
            rendered = json.dumps(payload) + format_session_file_activity_summary(payload)
            self.assertNotIn(str(root), rendered)
            self.assertNotIn("outside.txt", rendered)
            self.assertNotIn(SECRET, rendered)


    def test_focus_is_workspace_relative_and_unknown_extensions_are_omitted(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            rows = _incident_rows(root)
            rows.extend(
                [
                    {
                        "session_id": SESSION,
                        "role": "assistant",
                        "content": "",
                        "timestamp": 1_012.0,
                        "tool_calls": [_call("u1", "read_file", {"path": "docs/notes.bin"})],
                        "_compressed_summary": 0,
                    },
                    {
                        "session_id": SESSION,
                        "role": "tool",
                        "content": json.dumps({"content": "binary"}),
                        "tool_call_id": "u1",
                        "tool_name": "read_file",
                        "timestamp": 1_013.0,
                        "_compressed_summary": 0,
                    },
                    {
                        "session_id": SESSION,
                        "role": "assistant",
                        "content": "",
                        "timestamp": 1_014.0,
                        "tool_calls": [_call("u2", "read_file", {"path": "docs/readme.md"})],
                        "_compressed_summary": 0,
                    },
                ]
            )
            record = _write_jsonl(Path(tmp) / "focused.jsonl", rows)
            payload = build_session_file_activity(
                None,
                SESSION,
                session_record=record,
                workspace=str(root),
                focus="src",
            )
            self.assertEqual(payload["focus"], ["src"])
            self.assertEqual({entry["path"] for entry in payload["files"]}, {"src/app.py"})
            self.assertGreaterEqual(payload["omitted_paths"]["by_reason"]["focus"], 1)
            unfiltered = build_session_file_activity(None, SESSION, session_record=record, workspace=str(root))
            self.assertGreaterEqual(unfiltered["omitted_paths"]["by_reason"]["extension_guard"], 1)
            with self.assertRaisesRegex(SessionFileActivityError, "focus"):
                build_session_file_activity(None, SESSION, session_record=record, workspace=str(root), focus="/tmp")

    def test_file_lineage_is_bounded_and_escape_arguments_fail_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            rows = _incident_rows(root)
            for index in range(3):
                rows.insert(
                    8,
                    {
                        "session_id": SESSION,
                        "role": "assistant",
                        "content": "",
                        "timestamp": 2_000.0 + index,
                        "tool_calls": [_call(f"r{index}", "read_file", {"path": f"src/{index}.py"})],
                        "_compressed_summary": 0,
                    },
                )
            record = _write_jsonl(Path(tmp) / "session.jsonl", rows)
            payload = build_session_file_activity(None, SESSION, session_record=record, workspace=str(root), max_files=2)
            self.assertEqual(payload["max_files"], 2)
            self.assertTrue(payload["truncated"])
            self.assertEqual(payload["shown_file_count"], 2)
            self.assertGreater(payload["omitted_file_count"], 0)
            with self.assertRaisesRegex(SessionFileActivityError, "at least 1"):
                build_session_file_activity(None, SESSION, session_record=record, workspace=str(root), max_files=0)
            with self.assertRaisesRegex(SessionFileActivityError, "no Hermes session"):
                build_session_file_activity(None, "missing", session_record=record, workspace=str(root))


if __name__ == "__main__":
    unittest.main()
