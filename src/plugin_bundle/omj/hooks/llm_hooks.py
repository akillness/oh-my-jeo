from __future__ import annotations

from ..awareness import awareness_context_matches_message, awareness_primer_context, awareness_route_hint, awareness_route_hint_context
from ..context_brief import build_context_brief
from ..host_observation import observe_plugin_hook_call
from ..omj_roles import extract_role_marker, role_context_payload
from ..runtime_reader import read_omj_hud, read_omj_status
from .session_hooks import host_reported_child


_ORCHESTRATION_WORKFLOWS = frozenset(
    {
        "loop",
        "maestro",
        "ralph",
        "ralplan",
        "team",
        "ultragoal",
        "ultraprocess",
        "ultrawork",
    }
)


def _token_metadata_from_kwargs(kwargs: dict) -> dict[str, object]:
    keys = (
        "tokens_remaining",
        "token_budget",
        "input_tokens",
        "output_tokens",
        "context_remaining_percent",
    )
    return {key: kwargs[key] for key in keys if kwargs.get(key) is not None}


def _filter_route_hint_payload(payload: dict[str, object]) -> dict[str, object]:
    """Keep task hints while removing only orchestrating route hints/cards."""
    raw_hints = payload.get("hints", [])
    kept: list[object] = []
    changed = False
    for raw_hint in raw_hints if isinstance(raw_hints, list) else []:
        if not isinstance(raw_hint, dict):
            kept.append(raw_hint)
            continue
        if str(raw_hint.get("workflow", "")) in _ORCHESTRATION_WORKFLOWS:
            changed = True
            continue
        adjacent = [str(item) for item in raw_hint.get("adjacent_workflows", [])]
        loadable = [item for item in adjacent if item not in _ORCHESTRATION_WORKFLOWS]
        hint = raw_hint
        if len(loadable) != len(adjacent):
            changed = True
            hint = {**raw_hint, "adjacent_workflows": loadable}
        kept.append(hint)
    if not changed:
        return payload
    hints = [hint for hint in kept if isinstance(hint, dict)]
    primary = hints[0] if hints else {}
    filtered = dict(payload)
    filtered["status"] = "hinted" if hints else "no_hint"
    filtered["hints"] = kept
    filtered["selected_workflow"] = str(primary.get("workflow", ""))
    filtered["primary_workflow"] = str(primary.get("workflow", ""))
    filtered["primary_next_action"] = str(primary.get("next_action", ""))
    filtered["adjacent_workflows"] = _unique_route_workflows(hints)
    return filtered


def _unique_route_workflows(hints: list[dict[str, object]]) -> list[str]:
    seen: list[str] = []
    for hint in hints:
        for value in hint.get("adjacent_workflows", []):
            text = str(value)
            if text not in seen:
                seen.append(text)
    return seen


def _subagent_route_hint_context(message: str) -> str:
    payload = _filter_route_hint_payload(awareness_route_hint(message, max_hints=2))
    if payload.get("status") != "hinted" or not payload.get("hints"):
        return ""
    adjacent_summary = ", ".join(str(item) for item in payload.get("adjacent_workflows", []))
    mentioned_summary = ", ".join(str(item) for item in payload.get("mentioned_workflows", []))
    not_executed_summary = ", ".join(str(item) for item in payload.get("not_executed", []))
    lines = [
        "[OMJ Route Hint]",
        "Use this message-specific OMJ hint before generic chat/tools when it fits the user intent.",
        f"intent={payload.get('intent_class')}; selected={payload.get('selected_workflow')}; confidence=medium",
    ]
    if mentioned_summary:
        lines.append(f"mentioned_workflows={mentioned_summary}.")
    if adjacent_summary:
        lines.append(f"adjacent_workflows={adjacent_summary}.")
    if not_executed_summary:
        lines.append(f"not_executed={not_executed_summary}.")
    for hint in payload["hints"]:
        adjacent = ", ".join(str(item) for item in hint.get("adjacent_workflows", []))
        lines.append(
            f"- selected={hint.get('workflow')}; lane={hint.get('lane')}; "
            f"next_action={hint.get('next_action')}; reason={hint.get('reason')}"
        )
        context_card = hint.get("workflow_context_card")
        if isinstance(context_card, dict):
            first_response_shape = str(context_card.get("first_response_shape") or "").strip()
            if first_response_shape:
                lines.append(f"  first_response_shape={first_response_shape}")
        fallback_action = str(hint.get("fallback_action") or "").strip()
        if fallback_action:
            lines.append(f"  fallback_action={fallback_action}.")
        if adjacent:
            lines.append(f"  adjacent_workflows={adjacent}.")
        not_evidence = ", ".join(str(item) for item in hint.get("not_evidence_yet", [])[:4])
        if not_evidence:
            lines.append(f"  not_evidence_yet={not_evidence}.")
    lines.append("Boundary: " + str(payload["claim_boundary"]))
    return "\n".join(lines)



def pre_llm_call(**kwargs) -> dict[str, object] | None:
    """Inject bounded OMJ role/status context without storing prompts."""
    observe_plugin_hook_call("pre_llm_call", kwargs)
    context_parts: list[str] = []
    payload: dict[str, object] = {}
    user_message = str(kwargs.get("user_message", "") or "")
    is_first_turn = bool(kwargs.get("is_first_turn", False))
    omj_home = str(kwargs.get("omj_home", "") or "") or None
    session_id = str(kwargs.get("session_id", "") or "").strip()
    is_host_child = bool(session_id and host_reported_child(omj_home=omj_home, session_id=session_id))
    route_hint_context = (
        _subagent_route_hint_context(user_message)
        if is_host_child
        else awareness_route_hint_context(user_message)
    )
    should_include_awareness = is_first_turn or bool(route_hint_context) or awareness_context_matches_message(user_message)
    if kwargs.get("include_omj_awareness", True) is not False and should_include_awareness:
        context_parts.append(awareness_primer_context())
        context_brief = build_context_brief(
            user_message,
            source=str(kwargs.get("source") or kwargs.get("host") or "pre_llm_call"),
            max_hints=2,
            include_prompt_context=False,
        )
        payload["omj_context_brief"] = context_brief
        if route_hint_context:
            context_parts.append(route_hint_context)

    marker = extract_role_marker(user_message)
    if marker:
        role_payload = role_context_payload(marker)
        if role_payload["status"] == "available":
            context_parts.append(
                "\n".join(
                    [
                        f"[OMJ Role: {role_payload['role']} ]".replace(" ]", "]"),
                        str(role_payload["context"]),
                        str(role_payload["claim_boundary"]),
                    ]
                )
            )
        else:
            context_parts.append(
                "[OMJ Role Warning] "
                f"Unknown role '{marker}'. Available roles: {', '.join(role_payload['available_roles']) or '(none)'}.'"
            )

    try:
        hermes_home = str(kwargs.get("hermes_home", "") or "") or None
        status = read_omj_status(omj_home=omj_home, limit=3)
        hud = read_omj_hud(
            omj_home=omj_home,
            hermes_home=hermes_home,
            preset="focused",
            limit=3,
            token_metadata=_token_metadata_from_kwargs(kwargs),
        )
    except Exception:
        status = {}
        hud = {}

    if not context_parts and not status.get("runtime_state_present") and not status.get("runs"):
        return None

    if status.get("runtime_state_present") or status.get("runs"):
        lines = [
            str(hud.get("display", {}).get("line", "[omj] status unavailable")),
            "[OMJ] Native bridge status context.",
            "Evidence boundary: prepared handoffs are not execution, review, CI, merge-readiness, or merge evidence.",
        ]
        latest_run_id = status.get("latest_run_id")
        if latest_run_id:
            lines.append(f"Latest runtime run: {latest_run_id}.")
        for run in status.get("runs", [])[:3]:
            run_id = run.get("run_id", "unknown")
            workflow = run.get("workflow", "unknown")
            phase = run.get("phase", "unknown")
            observation = run.get("observation_status", "unknown")
            execution = run.get("execution_observed", False)
            review = run.get("review_observed", False)
            ci = run.get("ci_observed", False)
            merge = run.get("merge_observed", False)
            lines.append(
                f"- {run_id}: workflow={workflow}, phase={phase}, observation={observation}, "
                f"execution_observed={execution}, review_observed={review}, ci_observed={ci}, merge_observed={merge}."
            )
        lines.append("Use omj_hud for the compact status line, omj_role for role context, or omj_status for full metadata-only status.")
        context_parts.append("\n".join(lines))
    payload["context"] = "\n\n".join(context_parts)
    return payload
