from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from omj.plugin_bundle.omj.host_observation import (
    _reset_runtime_observation_throttle,
    observe_plugin_hook_call,
    observe_plugin_tool_call,
)
from omj.plugin_bundle.omj.runtime_reader import read_omj_hud


def _state(omj_home: Path) -> dict:
    path = omj_home / "runtime" / "state.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _observation_count(omj_home: Path) -> int:
    path = omj_home / "runtime" / "plugin_host_observations.jsonl"
    if not path.exists():
        return 0
    return len([line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()])


class PluginRuntimeAutoObserveTests(unittest.TestCase):
    def setUp(self) -> None:
        import os

        _reset_runtime_observation_throttle()
        # Snapshot and restore the process environment so host-signal env vars set
        # by one test never leak into another (or into the developer environment).
        saved = dict(os.environ)

        def _restore() -> None:
            os.environ.clear()
            os.environ.update(saved)

        self.addCleanup(_restore)
        self.addCleanup(_reset_runtime_observation_throttle)

    def _scrub_env(self) -> None:
        import os

        for key in (
            "OMJ_HOME",
            "OMJ_PLUGIN_SESSION_ID",
            "OMJ_PLUGIN_HOST",
            "HERMES_SESSION_ID",
            "HERMES_THREAD_ID",
            "HERMES_CONVERSATION_ID",
            "HERMES_HOST",
            "HERMES_AGENT",
        ):
            os.environ.pop(key, None)

    def test_bare_hook_call_without_host_signal_records_nothing(self) -> None:
        self._scrub_env()
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / ".omj"
            record = observe_plugin_hook_call("pre_tool_call", {"omj_home": str(home)})
            self.assertIsNone(record)
            self.assertFalse((home / "runtime" / "state.json").exists())
            self.assertEqual(_observation_count(home), 0)

    def test_session_alias_kwarg_records_live_runtime_observation(self) -> None:
        self._scrub_env()
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / ".omj"
            record = observe_plugin_hook_call(
                "pre_tool_call", {"thread_id": "th-9", "omj_home": str(home)}
            )
            self.assertIsNotNone(record)
            assert record is not None
            self.assertEqual(record["event"], "hook_call")
            self.assertEqual(record["session_id"], "th-9")
            self.assertEqual(record["host"], "host")
            self.assertEqual(record["runtime_readiness"], "active_runtime_observed")
            self.assertTrue(record["native_integration_active"])

            state = _state(home)
            self.assertEqual(state["last_plugin_runtime_readiness"], "active_runtime_observed")
            self.assertIsNotNone(state["last_plugin_runtime_observed"])
            self.assertEqual(state["last_plugin_host_observation"]["session_id"], "th-9")

            hud = read_omj_hud(omj_home=home, preset="full")
            self.assertTrue(hud["plugin"]["runtime_observed"])
            self.assertTrue(hud["plugin"]["runtime_active"])
            self.assertEqual(hud["plugin"]["runtime_readiness"], "active_runtime_observed")
            self.assertIn("plugin-runtime:live", hud["display"]["line"])

    def test_tool_observation_uses_conversation_alias_and_explicit_host(self) -> None:
        self._scrub_env()
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / ".omj"
            record = observe_plugin_tool_call(
                "omj_status",
                {},
                {"conversation_id": "conv-7", "host": "hermes-agent", "omj_home": str(home)},
            )
            self.assertIsNotNone(record)
            assert record is not None
            self.assertEqual(record["event"], "tool_call")
            self.assertEqual(record["tool"], "omj_status")
            self.assertEqual(record["host"], "hermes-agent")
            self.assertEqual(record["session_id"], "conv-7")
            self.assertEqual(record["runtime_readiness"], "active_runtime_observed")

    def test_environment_session_signal_defaults_host_to_hermes(self) -> None:
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / ".omj"
            with mock.patch.dict(
                "os.environ",
                {"OMJ_HOME": str(home), "HERMES_SESSION_ID": "hsess-1"},
                clear=False,
            ):
                self._scrub_env_except({"OMJ_HOME", "HERMES_SESSION_ID"})
                record = observe_plugin_hook_call("pre_llm_call", {})
            self.assertIsNotNone(record)
            assert record is not None
            self.assertEqual(record["host"], "hermes")
            self.assertEqual(record["session_id"], "hsess-1")
            self.assertEqual(record["runtime_readiness"], "active_runtime_observed")
            self.assertEqual(_state(home)["last_plugin_runtime_readiness"], "active_runtime_observed")

    def test_repeated_hook_calls_in_one_process_record_once(self) -> None:
        self._scrub_env()
        with TemporaryDirectory() as tmp:
            home = Path(tmp) / ".omj"
            first = observe_plugin_hook_call(
                "pre_tool_call", {"session_id": "sess-dup", "host": "hermes-agent", "omj_home": str(home)}
            )
            second = observe_plugin_hook_call(
                "pre_tool_call", {"session_id": "sess-dup", "host": "hermes-agent", "omj_home": str(home)}
            )
            self.assertIsNotNone(first)
            self.assertIsNone(second)
            self.assertEqual(_observation_count(home), 1)

            # A distinct session in the same process records its own observation.
            third = observe_plugin_hook_call(
                "pre_tool_call", {"session_id": "sess-other", "host": "hermes-agent", "omj_home": str(home)}
            )
            self.assertIsNotNone(third)
            self.assertEqual(_observation_count(home), 2)

    def _scrub_env_except(self, keep: set[str]) -> None:
        import os

        for key in (
            "OMJ_PLUGIN_SESSION_ID",
            "OMJ_PLUGIN_HOST",
            "HERMES_THREAD_ID",
            "HERMES_CONVERSATION_ID",
            "HERMES_HOST",
            "HERMES_AGENT",
        ):
            if key not in keep:
                os.environ.pop(key, None)


if __name__ == "__main__":
    unittest.main()
