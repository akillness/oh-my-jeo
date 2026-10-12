# Prepared guidance: meta-router

Family: `explicit-meta-routing`<br>
Category: `router`<br>
Phase: `meta-routing`<br>
Role: `guide`

## Contract
[omh] Message opens with /omh and a task: meta-routing guidance for a leading /omh command: reason over the imperative task, consult the live workflow catalog, and select or chain the right workflow(s).

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- /omh
- ./omh
- meta-router
- leading /omh command

## Required inputs
- leading /omh or ./omh command with an imperative remainder
- live OMH catalog via bounded `omh recommend --json` queries
- available shell/CLI or plugin tool surface

## Expected outputs
- selected workflow or chain with rationale
- consulted catalog evidence from the bounded recommend output
- observed-vs-prepared evidence boundary for the routing decision

## Artifact expectations
- runtime run record when a wrapper can observe the meta-routing decision

## Acceptance criteria
- The selected workflow, confidence reason, evidence boundary, and user-facing next action are named.
- Low-confidence or conflicting signals return a picker or clarification instead of forced routing.
- Catalog answers are rendered without shell approval when wrapper metadata is sufficient.

## Handoff policy
Reason over the /omh remainder, select or chain concrete workflows from the live catalog, and prepare a selected executor/runtime handoff only when the chosen chain requires code edits; do not execute code.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: routing-gated
- source owner: skills/omh-meta-router/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-meta-router/SKILL.md`
- SHA256: `3515feecbfffca34258790c3834298936a7c232a665a504f6144d0863beeec4e`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.
- Pinned source references `references/catalog-index.md`, but the upstream file is absent; preserve this as an unavailable conditional reference and do not synthesize catalog content.

## Blocked prerequisites
- blocked until supplied or observed: leading /omh or ./omh command with an imperative remainder
- blocked until supplied or observed: live OMH catalog via bounded `omh recommend --json` queries
- blocked until supplied or observed: available shell/CLI or plugin tool surface
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
