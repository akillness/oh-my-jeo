from __future__ import annotations

import json
from typing import Any

from ..host_observation import OBSERVATION_SCHEMA, attach_public_observation, observe_plugin_tool_call
from ..runtime_paths import resolve_handler_homes
from ..runtime_reader import read_omj_hud, read_omj_status

OMJ_HUD_SCHEMA = {
    "name": "omj_hud",
    "description": (
        "Read the compact OMJ metadata-only HUD payload for Hermes TUI/status surfaces. "
        "Token fields are shown only when supplied by the host metadata."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "omj_home": {
                "type": "string",
                "description": "Optional OMJ_HOME override. Defaults to $OMJ_HOME or ~/.omj.",
            },
            "hermes_home": {
                "type": "string",
                "description": "Optional HERMES_HOME override. Defaults to $HERMES_HOME or ~/.hermes.",
            },
            "preset": {
                "type": "string",
                "enum": ["minimal", "focused", "full"],
                "description": "HUD display density.",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum recent runtime runs to summarize.",
            },
            "tokens_remaining": {
                "type": "number",
                "description": "Optional host-provided token count.",
            },
            "token_budget": {
                "type": "number",
                "description": "Optional host-provided token budget.",
            },
            "input_tokens": {
                "type": "number",
                "description": "Optional host-provided input token count.",
            },
            "output_tokens": {
                "type": "number",
                "description": "Optional host-provided output token count.",
            },
            "context_remaining_percent": {
                "type": "number",
                "description": "Optional host-provided context remaining percentage.",
            },
            "observation": OBSERVATION_SCHEMA,
        },
    },
}


def omj_hud_handler(args: dict[str, Any], **kwargs) -> str:
    homes = resolve_handler_homes(args, kwargs)
    bound_kwargs = dict(kwargs)
    bound_kwargs.update({"omj_home": str(homes.omj_home), "hermes_home": str(homes.hermes_home)})
    observation = observe_plugin_tool_call("omj_hud", args, bound_kwargs)
    token_metadata = {
        key: args.get(key)
        for key in (
            "tokens_remaining",
            "token_budget",
            "input_tokens",
            "output_tokens",
            "context_remaining_percent",
        )
        if args.get(key) is not None
    }
    payload = read_omj_hud(
        omj_home=homes.omj_home,
        hermes_home=homes.hermes_home,
        preset=str(args.get("preset", "focused") or "focused"),
        limit=args.get("limit") or 3,
        token_metadata=token_metadata,
    )
    runtime = payload.get("runtime")
    if isinstance(runtime, dict) and not runtime.get("latest_run_id"):
        selected_status = read_omj_status(omj_home=homes.omj_home, limit=1)
        latest_run_id = str(selected_status.get("latest_run_id", "") or "")
        if latest_run_id:
            runtime["latest_run_id"] = latest_run_id
    return json.dumps(attach_public_observation(payload, observation), sort_keys=True)
