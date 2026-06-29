from __future__ import annotations

from ..awareness import awareness_context_matches_message, awareness_primer_context, awareness_route_hint_context
from ..context_brief import build_context_brief
from ..host_observation import observe_plugin_hook_call
from ..omj_roles import extract_role_marker, role_context_payload
from ..runtime_reader import read_omj_hud, read_omj_status


def _token_metadata_from_kwargs(kwargs: dict) -> dict[str, object]:
    keys = (
        "tokens_remaining",
        "token_budget",
        "input_tokens",
        "output_tokens",
        "context_remaining_percent",
    )
    return {key: kwargs[key] for key in keys if kwargs.get(key) is not None}


def pre_llm_call(**kwargs) -> dict[str, object] | None:
    """Inject bounded OMJ role/status context without storing prompts."""
    observe_plugin_hook_call("pre_llm_call", kwargs)
    context_parts: list[str] = []
    payload: dict[str, object] = {}
    user_message = str(kwargs.get("user_message", "") or "")
    is_first_turn = bool(kwargs.get("is_first_turn", False))
    route_hint_context = awareness_route_hint_context(user_message)
    should_include_awareness = is_first_turn or bool(route_hint_context) or awareness_context_matches_message(user_message)
    if kwargs.get("include_omj_awareness", True) is not False and should_include_awareness:
        context_parts.append(awareness_primer_context())
        payload["omj_context_brief"] = build_context_brief(
            user_message,
            source=str(kwargs.get("source") or kwargs.get("host") or "pre_llm_call"),
            max_hints=2,
            include_prompt_context=False,
        )
        if route_hint_context:
            context_parts.append(route_hint_context)

    marker = extract_role_marker(user_message)
    if marker:
        role_payload = role_context_payload(marker)
        if role_payload["status"] == "available":
            context_parts.append(
                "\n".join(
                    [
                        f"[OMJ Role: {role_payload['role']}]",
                        str(role_payload["context"]),
                        str(role_payload["claim_boundary"]),
                    ]
                )
            )
        else:
            context_parts.append(
                "[OMJ Role Warning] "
                f"Unknown role '{marker}'. Available roles: {', '.join(role_payload['available_roles']) or '(none)'}."
            )

    try:
        omj_home = str(kwargs.get("omj_home", "") or "") or None
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
