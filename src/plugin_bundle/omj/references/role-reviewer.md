# Reviewer

This OMJ role is a responsibility descriptor, not a runtime agent.

Own claim checking, severity-rated review findings, QA framing, release/readiness review, evidence requirements, and a structured terminal verdict.

## OMJ Role Context

Use this role as OMJ workflow-layer responsibility context: route the user's request to the nearest skill, name adjacent OMJ workflows when the work crosses lanes, and keep status/evidence boundaries visible.

Normal users talk to Hermes; role names help Hermes explain ownership and next action without making the user learn backend OMJ commands.

Role selection is prepared guidance only. It is not worker dispatch, tool execution, file generation, delivery, review, CI, merge-readiness, or merge evidence.

## Legacy Aliases

- `review-gate`
- `hybrid-review`
- `hybrid-verification`

## Owns

- Severity-rated findings (CRITICAL/HIGH/MEDIUM/LOW) and risks, naming the files actually inspected because a clean report still has to show that inspection happened
- A structured terminal verdict: CLEAR/WATCH/BLOCK for readiness and APPROVE/COMMENT/REQUEST-CHANGES for review, where APPROVE means review-approved (not merged) and any open CRITICAL or HIGH forces BLOCK or REQUEST-CHANGES
- Verification, CI, and release-readiness status
- Follow-up handoff only when fixes are accepted

## Primary Skills

- `code-review`
- `ultraqa`
- `ask`

## Primary Harnesses

- `code-review`
- `qa`
- `ops-review`

## Wrapper Actions

- `show_findings`
- `show_verdict`
- `prepare_fix_handoff`
- `refresh_status`

## Evidence Boundary

Review findings are not fix evidence; a CLEAR or APPROVE verdict is review-approved, not merged.
