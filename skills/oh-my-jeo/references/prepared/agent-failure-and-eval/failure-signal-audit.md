# Prepared guidance: failure-signal-audit

Family: `agent-failure-and-eval`  
Category: `review`  
Phase: `failure-signal-audit`  
Role: `reviewer`

## Contract
[omh] Hidden or swallowed errors suspected: find swallowed errors, unsafe fallbacks, hidden UI/runtime failures, and missing propagation before they become false green status. Use when the user says: failure-signal-audit, failure signal audit, silent failure, silent failures, silent failure hunter, swallowed error, swallowed errors, empty catch.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- failure-signal-audit
- failure signal audit
- silent failure
- silent failures
- silent failure hunter
- swallowed error
- swallowed errors
- empty catch

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- failure_signal_audit_plan/v1
- silent_failure_finding/v1 when observed
- fallback_risk_matrix/v1
- propagation_gap_map/v1
- false_green_status_review/v1
- remediation_handoff/v1 when needed

## Artifact expectations
- failure_signal_audit_plan/v1 with source boundary, surfaces, evidence types, and stop condition
- silent_failure_finding/v1 only from observed code, trace, console, network, test, or runtime evidence
- fallback_risk_matrix/v1 separating safe fallback, user-visible degraded mode, masked failure, and destructive fallback
- propagation_gap_map/v1 for missing context, lost stack, ignored async rejection, empty catch, null/empty default, or log-only handling
- false_green_status_review/v1 comparing PASS/green claims against observed checks and missing signals
- remediation_handoff/v1 only after findings are accepted and the selected owner is explicit
- contract_id: `failure_signal_audit_plan/v1`; enforcement_level: `guidance_only`; consumer_id: `none`

## Acceptance criteria
- Audit scope, source surfaces, and evidence types are named.
- Swallowed errors, dangerous fallbacks, propagation gaps, and false-green claims are reported as separate finding types.
- Each finding names location or evidence ref, severity, user/operator impact, and a smallest safe remediation route.
- No remediation, runtime repair, verification, CI, merge, or future reliability claim is made without observed follow-up evidence.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: workflow-surface-gated
- source owner: skills/omh-failure-signal-audit/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-failure-signal-audit/SKILL.md`
- SHA256: `445b56b47ba41f6f9eb027461bdf476aea8eaa48807b8fb1d5e73e33541b4d65`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- blocked until supplied or observed: user request
- blocked until supplied or observed: target context
- blocked until supplied or observed: delivery or status expectation
- blocked until supplied or observed: known missing evidence
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
