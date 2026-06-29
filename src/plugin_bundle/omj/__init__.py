from __future__ import annotations

_TOOLSET = "omj"


def register(ctx):
    """Register the OMJ thin native bridge with Hermes."""
    from .hooks.llm_hooks import pre_llm_call
    from .hooks.session_hooks import on_session_end
    from .hooks.tool_hooks import pre_tool_call
    from .tools.capability_tool import OMJ_CAPABILITIES_SCHEMA, omj_capabilities_handler
    from .tools.chat_tool import OMJ_INTERACT_SCHEMA, omj_interact_handler
    from .tools.context_tool import OMJ_CONTEXT_SCHEMA, omj_context_handler
    from .tools.evidence_tool import OMJ_EVIDENCE_SCHEMA, omj_evidence_handler
    from .tools.hud_tool import OMJ_HUD_SCHEMA, omj_hud_handler
    from .tools.probe_tool import OMJ_PROBE_SCHEMA, omj_probe_handler
    from .tools.recommend_tool import OMJ_RECOMMEND_SCHEMA, omj_recommend_handler
    from .tools.role_tool import OMJ_ROLE_SCHEMA, omj_role_handler
    from .tools.status_tool import OMJ_STATUS_SCHEMA, omj_status_handler

    ctx.register_tool(
        "omj_capabilities",
        _TOOLSET,
        OMJ_CAPABILITIES_SCHEMA,
        omj_capabilities_handler,
        description=OMJ_CAPABILITIES_SCHEMA["description"],
    )
    ctx.register_tool(
        "omj_context",
        _TOOLSET,
        OMJ_CONTEXT_SCHEMA,
        omj_context_handler,
        description=OMJ_CONTEXT_SCHEMA["description"],
    )
    ctx.register_tool(
        "omj_gather_evidence",
        _TOOLSET,
        OMJ_EVIDENCE_SCHEMA,
        omj_evidence_handler,
        description=OMJ_EVIDENCE_SCHEMA["description"],
    )
    ctx.register_tool(
        "omj_hud",
        _TOOLSET,
        OMJ_HUD_SCHEMA,
        omj_hud_handler,
        description=OMJ_HUD_SCHEMA["description"],
    )
    ctx.register_tool(
        "omj_interact",
        _TOOLSET,
        OMJ_INTERACT_SCHEMA,
        omj_interact_handler,
        description=OMJ_INTERACT_SCHEMA["description"],
    )
    ctx.register_tool(
        "omj_probe",
        _TOOLSET,
        OMJ_PROBE_SCHEMA,
        omj_probe_handler,
        description=OMJ_PROBE_SCHEMA["description"],
    )
    ctx.register_tool(
        "omj_recommend",
        _TOOLSET,
        OMJ_RECOMMEND_SCHEMA,
        omj_recommend_handler,
        description=OMJ_RECOMMEND_SCHEMA["description"],
    )
    ctx.register_tool(
        "omj_role",
        _TOOLSET,
        OMJ_ROLE_SCHEMA,
        omj_role_handler,
        description=OMJ_ROLE_SCHEMA["description"],
    )
    ctx.register_tool(
        "omj_status",
        _TOOLSET,
        OMJ_STATUS_SCHEMA,
        omj_status_handler,
        description=OMJ_STATUS_SCHEMA["description"],
    )
    ctx.register_hook("on_session_end", on_session_end)
    ctx.register_hook("pre_llm_call", pre_llm_call)
    ctx.register_hook("pre_tool_call", pre_tool_call)
