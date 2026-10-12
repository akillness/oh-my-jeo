# Prepared guidance: todo-checklist

Family: `todo-checklist`  
Category: `operator`  
Phase: `observability`  
Role: `tracker`

## Contract
[omh] Resume or finish the work we agreed on: continue or finish the accepted work from conversation context, preserve rejected ideas, and report evidence-bounded completion. Also declare and advance the metadata-only plan checklist without starting a delivery engine. Use when the user says: todo-checklist, plan checklist, todo checklist, phase checklist, declare a plan checklist, declare the plan todo, show the plan todo, clear the plan todo.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- todo-checklist
- plan checklist
- todo checklist
- phase checklist
- declare a plan checklist
- declare the plan todo
- show the plan todo
- clear the plan todo

## Required inputs
- the work to be tracked

## Expected outputs
- a declared checklist with exactly one active item
- explicit states as work completes

## Artifact expectations
- metadata-only `omh_todo/v1` plan todo owned by the declaring session

## Acceptance criteria
- Exactly one item is active, or the list is complete and every item is done.
- Use `action=advance` or a complete `action=set` list; never drop an item by omission.
- Item states are described as declarations; observed results are cited separately or named as missing.
- Name whether work is blocked or human-deferred.

## Handoff policy
Declare and update the checklist directly with `omh_todo`; a checklist item is a plan declaration and never dispatches, executes, or verifies anything.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: evidence-gated
- source owner: skills/omh-todo-checklist/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-todo-checklist/SKILL.md`
- SHA256: `a20344d5082437113e8e84cc63262d7e9d08a882dbeb3e50fb79fd0e09afd458`

## Method references
- `omh-todo-checklist/references/checklist-discipline.md` (pinned `skills/omh-todo-checklist/references/checklist-discipline.md`)
- `omh-todo-checklist/references/closing-a-story.md` (pinned `skills/omh-todo-checklist/references/closing-a-story.md`)
- `omh-todo-checklist/references/requirements-quality-checklist.md` (pinned `skills/omh-todo-checklist/references/requirements-quality-checklist.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: the work to be tracked
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
