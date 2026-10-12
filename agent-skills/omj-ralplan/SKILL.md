---
name: omj-ralplan
description: [omj] Compare source-backed options, architecture, risks, and validation through reviewed consensus planning before acceptance.
metadata:
  omj:
    portability: portable
    category: planning
    phase: reviewed-plan
---

# Ralplan

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`ralplan` makes this workflow explicit: Compare source-backed options, architecture, risks, and validation through reviewed consensus planning before acceptance.

## Do Not Use When

- The request is still too ambiguous to name requirements, non-goals, or acceptance criteria; use `deep-interview` first.
- The user asks for one full research-plan-implementation-review-PR cycle; use `ultraprocess` and keep ralplan as the planning stage.
- The user wants a pure source lookup, citation check, or paper explanation with no implementation plan.

## Examples

Good example:

- Prompt: $ralplan turn this risky refactor into a reviewable plan with acceptance criteria and verification commands.
- Expected behavior: Produce repo/source facts, alternatives, risk review, acceptance criteria, exact verification commands, and handoff readiness without editing code.
- Why: The request is clear enough to plan but risky enough to require consensus-style review before execution.

Bad example:

- Prompt: $ralplan implement the refactor now and open the PR.
- Expected behavior: Stop at the reviewed plan or route the full delivery cycle to `ultraprocess` after plan acceptance.
- Why: Ralplan is a planning gate, not implementation, review, CI, or PR evidence.

## Completion Checklist

- Observed repo facts and source/web evidence gaps are named.
- At least two options or one chosen option plus rejected alternatives are recorded.
- Risks, acceptance criteria, and verification commands are testable or explicitly blocked.
- Record consumer current state and target state; map Success criteria Criterion | Task | Verification scenario and sizing bands. Target-state coverage includes each behavior unless the user excluded it; record gaps.
- name each consumer of the result, their current workflow on this surface, and the state in which that workflow keeps working with no new friction or loss.
- For every difference between current and target, each with why it matters; use an evidence-gap record below instead when unobserved.
- Never shrink scope on your own; plan an MVP or a first phase only when the user requested one.
- Size each task as one band, never as hours or days: `XS` (one small edit), `S` (one file and its test), `M` (several files in one module), `L` (several modules or one contract change), `XL` (crosses subsystems; split it into smaller tasks).
- Review Focus has at most five unmapped failure cases with an owning test or task, or explicitly states none.
- The plan stays unaccepted and awaiting with no handoff until an actual user answer accepts it. After acceptance, mark any prepared implementation handoff prepared_not_observed until selected-owner execution evidence is observed.

## Recovery Notes

- If requirements are still fuzzy, route back to deep-interview before planning.
- If current-source evidence is missing, route a web-research step before accepting the plan.
- If the user asks for implementation, hand off through ultraprocess, ultragoal, or the selected executor path after the plan is accepted.
- If the acceptance prompt times out (timeout), is dismissed, or receives no answer, keep status awaiting rather than accepted or refused; do not hand off or start implementation.
- If target-state coverage, a sizing band, or a Criterion | Task | Verification scenario row is missing, keep the plan blocked and name the gap.

## Use When

Compare source-backed options, architecture, risks, and validation through reviewed consensus planning before acceptance.

Strong routing signals: `ralplan`, `$ralplan`, `consensus plan`, `reviewed plan`, `issue to PR`, `acceptance criteria`, `verification command`, `reviewable PR`, `risky planning`, `dangerous`, `dangerous planning`, `unsafe`, `refactor safety`, `PR로 만들`, `PR로 만들 수 있게`, `위험한 리팩터링`, `리팩터링 위험`, `리스크 있는 리팩터링`, `검증 command`, `리뷰 가능한 단위`, `코드베이스 조사`, `웹리서치 계획`, `대안 비교`, `리스크 검토`

## Catalog Metadata

Category: `planning`
Phase: `reviewed-plan`
Host-owned workflow responsibility
Quality tier: `reviewed-plan-gated`

Quality bar:

- Start from observed repo facts and source/web evidence when freshness or external behavior matters.
- Include planner view, critic/risk review, alternative paths, rejected options, and a testability check before handoff.
- Produce testable acceptance criteria and exact verification commands or explain why they are not yet knowable.
- Record unresolved tradeoffs and evidence gaps instead of flattening uncertainty.
- End with a selected executor/runtime handoff shape only after the plan is accepted.
- Do not implement directly from consensus planning.
- Take plan acceptance only from the answer the user gave — the response status and value the question tool returns, or the user's own reply — never from the wording of the question you asked: when the acceptance question times out, is dismissed, or returns with no answer, the plan stays unaccepted, so record no acceptance, prepare no handoff, and start nothing; a missing answer is not a refusal either, so ask again later or report the plan as awaiting acceptance.

Handoff policy:

Compare source-backed options, architecture, risks, and validation through reviewed consensus planning before acceptance. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- requirements
- codebase facts
- source or web evidence when needed
- options
- tradeoffs
- test shape

Expected outputs:

- reviewed plan
- acceptance criteria
- risk register
- verification commands
- handoff guidance

Artifact expectations:

- plan and review artifacts when a wrapper supports file-backed planning

Safety rules:

- Do not implement directly from the planning lane.
- Do not invent codebase or web evidence; label missing evidence and source gaps.
- Make acceptance criteria testable.
- Record unresolved tradeoffs explicitly.
- Keep rejected options and handoff readiness separate from accepted execution evidence.
- Only an actual user answer accepts the plan; track consumer/target state via Success-criteria rows with XS–XL sizing and a capped Review Focus.

## Execution and Handoff Discipline

1. State the target, constraints, acceptance criteria, authority, and stop condition before work.
2. Planning and coordination do not take ownership of code implicitly. Keep the selected first-class coding owner explicit, including the current host when selected.
3. Read supporting references only when needed using available host file tools; loading guidance is not dispatch or plan acceptance.
4. Take acceptance only from the user's actual answer. A timeout, dismissal, or missing answer leaves the plan unaccepted; prepare no handoff and start nothing.
5. A selected owner, task card, plan, or prepared handoff stays `prepared_not_observed` until observed execution evidence exists. Preserve failures and unresolved criteria.
6. Verify behavior with the smallest relevant observed check. Current loader admission is not evidence of a live session; local fresh files do not prove host discovery, execution, review, CI, or merge.
7. Network operations, configuration or memory writes, external publishing, and new authority remain separately approval-gated. Do not activate unsupported services.

## Supporting Context

[Native and historical provenance](../omj/references/native-provenance.md)
