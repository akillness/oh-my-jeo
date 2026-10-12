# Prepared guidance: model-optimization

Family: `model-onboarding`  
Category: `optimization`  
Phase: `model-onboarding`  
Role: `tracker`

## Contract
[omh] Onboarding a newly released model generation: when a model family ships a new generation or changes its serving contract, walk the recognition, research, calibration, routing, and measurement process that keeps model handling honest and current. Use when the user says: model-optimization, model optimization, optimize for model, onboard new model, calibrate new model, new model calibration, model calibration.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- model-optimization
- model optimization
- optimize for model
- onboard new model
- calibrate new model
- new model calibration
- model calibration

## Required inputs
- the model id(s) as served, and the provider or gateway serving them
- recognition probe output for each id
- official release/contract documentation, with community harness findings labeled separately

## Expected outputs
- recognition and calibration coverage verdict for the family
- trait-to-counter calibration draft (or a no-change verdict with reasons)
- routing/pricing placement plan naming config surfaces vs repo changes
- measurement plan naming the benchmark pair or the reason none can run yet

## Artifact expectations
- metadata-only runtime record when a wrapper or shell is available

## Acceptance criteria
- Recognition probe output exists for every new id, and the family label is the expected one.
- Every research finding is labeled official, official-client, observed, or community with its source kept.
- The calibration draft counters named traits and marks version-specific rules as such.
- Routing and pricing changes name their surface (operator config vs repo change) and their approval state.
- The measurement plan names the benchmark pair, or the recorded reason none can run, and the worse-measured-calibration rule is stated.

## Handoff policy
Keep recognition probes, research synthesis, calibration drafting, and the process checklist in Hermes. Machine-local routing placement is a config edit the operator approves; repository changes (prefix table rows, calibration text, shipped chain defaults, docs) are coding work for the selected executor lane. A drafted calibration or prepared route is prepared_not_observed, never execution or benchmark evidence.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: evidence-gated
- source owner: skills/omh-model-optimization/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-model-optimization/SKILL.md`
- SHA256: `6936da423ff8a48ca072ef8d335f8ddaa68c661471cb7e3a2742549bba6be3f4`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- blocked until supplied or observed: the model id(s) as served, and the provider or gateway serving them
- blocked until supplied or observed: recognition probe output for each id
- blocked until supplied or observed: official release/contract documentation, with community harness findings labeled separately
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
