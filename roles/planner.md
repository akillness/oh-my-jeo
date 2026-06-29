# Planner

This OMJ role is a responsibility descriptor, not a runtime agent.

Own clarification, non-goals, acceptance criteria, tradeoffs, loopability, and verification strategy; freeze an immutable requirements seed once ambiguity is low (about 0.2 or less) so planning reads a frozen contract.

## OMJ Role Context

Use this role as OMJ workflow-layer responsibility context: route the user's request to the nearest skill, name adjacent OMJ workflows when the work crosses lanes, and keep status/evidence boundaries visible.

Normal users talk to Hermes; role names help Hermes explain ownership and next action without making the user learn backend OMJ commands.

Role selection is prepared guidance only. It is not worker dispatch, tool execution, file generation, delivery, review, CI, merge-readiness, or merge evidence.

## Legacy Aliases

- `planning-lead`

## Owns

- One-question clarification when scope is ambiguous
- Plan artifact with goals, non-goals, risks, and verification
- Decision gate before handoff or execution
- Contested decisions kept explicit with competing options and a human judgment-call flag instead of one forced verdict

## Primary Skills

- `deep-interview`
- `plan`
- `ralplan`
- `loop`

## Primary Harnesses

- `deep-interview`
- `planning`
- `strategy-synthesis`
- `goal-loop`

## Wrapper Actions

- `ask_followup`
- `accept_plan`
- `revise_plan`
- `show_status`

## Evidence Boundary

A planner role can make work reviewable; it is not proof that the work was accepted or executed.
