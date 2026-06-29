from __future__ import annotations

PROVIDED_TOOLS = (
    "omj_capabilities",
    "omj_context",
    "omj_gather_evidence",
    "omj_hud",
    "omj_interact",
    "omj_probe",
    "omj_recommend",
    "omj_role",
    "omj_status",
)
PROVIDED_HOOKS = ("on_session_end", "pre_llm_call", "pre_tool_call")

TOOL_FILE_STEMS = {
    "omj_capabilities": "capability_tool",
    "omj_context": "context_tool",
    "omj_gather_evidence": "evidence_tool",
    "omj_hud": "hud_tool",
    "omj_interact": "chat_tool",
    "omj_probe": "probe_tool",
    "omj_recommend": "recommend_tool",
    "omj_role": "role_tool",
    "omj_status": "status_tool",
}

TOOLS_REQUIRING_ROLE_CATALOG = frozenset({"omj_role"})
