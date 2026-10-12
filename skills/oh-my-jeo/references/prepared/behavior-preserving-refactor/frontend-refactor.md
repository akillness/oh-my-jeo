# Prepared guidance: frontend-refactor

Family: `behavior-preserving-refactor`<br>
Category: `maintenance`<br>
Phase: `frontend-refactor`<br>
Role: `handoff-guide`

## Contract
[omh] Oversized or tangled UI component: behavior-preserving refactor of UI code - preview the full change plan first, apply as a second explicit step, and work impact-ordered from state architecture down to naming polish. Use when the user says: frontend-refactor, front-refactor, frontend refactor, refactor this component, refactor the component, refactor my component, component refactor, react refactor.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- frontend-refactor
- front-refactor
- frontend refactor
- refactor this component
- refactor the component
- refactor my component
- component refactor
- react refactor

## Required inputs
- the target files or component, and the framework in use
- current behavior evidence: tests, or the characterization checks to write first
- the diff budget: micro pass only, one macro tier, or full ladder

## Expected outputs
- preview change plan with per-change line refs, before/after, safety reason, and category counts
- impact-ordered pass selection naming what is deferred and why
- characterization-test gate verdict before any macro change
- apply-step handoff with the unsafe-in-isolation changes listed under notes, never half-applied

## Artifact expectations
- metadata-only runtime record when a wrapper or shell is available

## Acceptance criteria
- The preview plan was emitted before any file changed, and the apply step was an explicit second decision.
- Behavior evidence exists on both sides of apply, and unsafe-in-isolation changes are listed as notes, not half-applied.
- Pass order was impact-first and each finding names its category and safety reason.
- Out-of-scope smells were routed: generic slop to `ai-slop-cleaner`, new UI to `frontend`, verdict-only review to `code-review`.

## Handoff policy
Hermes prepares the preview plan, pass order, and characterization-test gate; the apply step is coding work for the selected executor lane, and behavior preservation is claimed only from observed test runs before and after apply.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The target is not UI code, or the smell is generic slop, duplication, or dead code outside a component tree; use `ai-slop-cleaner`.
- Source routing exclusion: The user wants new UI built or redesigned rather than restructured; use `frontend`.
- Source routing exclusion: The user wants findings and a verdict without changing the code; use `code-review`.
- Source routing exclusion: The restructuring crosses module boundaries or changes architecture beyond the component tree; use `refactor-plan` for the phased execution shape, or `ralplan` first when the direction itself is still contested.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-frontend-refactor/SKILL.md`
- SHA256: `b2a22786194fe49410a1ab0b6183b89d0f70711c6a5ad9bac243505cec047ed0`

## Method references
- `omh-frontend-refactor/references/refactor-passes.md` (pinned `skills/omh-frontend-refactor/references/refactor-passes.md`)
- `omh-frontend-refactor/references/state-discipline.md` (pinned `skills/omh-frontend-refactor/references/state-discipline.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member frontend-refactor is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
