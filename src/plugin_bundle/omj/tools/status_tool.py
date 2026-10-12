from __future__ import annotations

import json

from ..host_observation import OBSERVATION_SCHEMA, attach_public_observation, observe_plugin_tool_call
from ..runtime_paths import resolve_handler_homes
from ..runtime_reader import read_omj_status

OMJ_STATUS_SCHEMA = {
    "name": "omj_status",
    "description": (
        "Read OMJ metadata-only runtime status. Prepared handoffs are kept separate "
        "from observed execution, review, CI, and merge evidence."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "omj_home": {
                "type": "string",
                "description": "Optional OMJ_HOME override. Defaults to the host/profile binding, then $OMJ_HOME or ~/.omj.",
            },
            "hermes_home": {
                "type": "string",
                "description": "Optional HERMES_HOME override. Defaults to the host/profile binding, then $HERMES_HOME or ~/.hermes.",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum recent runtime runs to summarize.",
            },
            "observation": OBSERVATION_SCHEMA,
        },
    },
}


def omj_status_handler(args: dict, **kwargs) -> str:
    homes = resolve_handler_homes(args, kwargs)
    bound_kwargs = dict(kwargs)
    bound_kwargs.update({"omj_home": str(homes.omj_home), "hermes_home": str(homes.hermes_home)})
    observation = observe_plugin_tool_call("omj_status", args, bound_kwargs)
    payload = read_omj_status(
        omj_home=homes.omj_home,
        limit=int(args.get("limit") or 5),
    )
    return json.dumps(attach_public_observation(payload, observation), sort_keys=True)
