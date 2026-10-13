# Prepared guidance: product-brief

Family: `product-brief`<br>
Category: `planning`<br>
Phase: `product-brief`<br>
Role: `planner`

## Contract
[omh] PRD or roadmap priorities to decide: turn product evidence into a decision-ready PRD, prioritization frame, and roadmap brief. Use when the user says: product requirements document, PRD, roadmap prioritization, 제품 요구사항 문서, 제품 기획서, 로드맵 우선순위.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- product requirements document
- PRD
- roadmap prioritization
- 제품 요구사항 문서
- 제품 기획서
- 로드맵 우선순위

## Required inputs
- product evidence
- problem and user
- goal and non-goals
- decision owner

## Expected outputs
- problem, user, evidence, metric, goal, and non-goal brief
- PRD with requirements, open questions, risks, dependencies, and acceptance shape
- prioritization/roadmap options with tradeoffs and decision owner
- explicit downstream route to ralplan, strategy-brief, or ultrawork only when its prerequisite is satisfied

## Artifact expectations
- prepared product brief or PRD when a wrapper captures it

## Acceptance criteria
- The plan names goals, non-goals, assumptions, acceptance criteria, and verification shape.
- Draft recommendations, accepted decisions, and executor handoffs are separate states.
- Rejected options or unresolved tradeoffs are recorded before handoff.

## Handoff policy
Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. A PRD or roadmap is prepared planning, not stakeholder acceptance, Jira or Linear mutation, implementation, test evidence, delivery, or a market commitment.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: planning-gated
- source owner: skills/omh-product-brief/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-product-brief/SKILL.md`
- SHA256: `91e9fb7689d6ce6de64df6d1423a70b98ca3a536c059176543b9be65d7ed8436`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- blocked until supplied or observed: product evidence
- blocked until supplied or observed: problem and user
- blocked until supplied or observed: goal and non-goals
- blocked until supplied or observed: decision owner
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
