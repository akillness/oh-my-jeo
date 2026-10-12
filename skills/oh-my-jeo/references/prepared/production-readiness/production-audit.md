# Prepared guidance: production-audit

Family: `production-readiness`  
Category: `review`  
Phase: `production-readiness`  
Role: `reviewer`

## Contract
[omh] Imminent production launch or release: evaluate release, deploy, security, observability, rollback, docs, and support readiness without claiming production access. Use when the user says: production-audit, production audit, production readiness, prod audit, prod readiness, ready for production, ready to ship, ship readiness.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- production-audit
- production audit
- production readiness
- prod audit
- prod readiness
- ready for production
- ready to ship
- ship readiness

## Required inputs
- product, service, release, or artifact scope
- target environment and release channel
- known test, CI, deploy, observability, security, and support evidence
- rollback owner and acceptable risk threshold

## Expected outputs
- production_audit_plan/v1
- readiness_matrix/v1
- release_gate_verdict/v1
- rollback_and_monitoring_plan/v1
- risk_register/v1
- not-evidence boundary

## Artifact expectations
- readiness_matrix/v1 covering build, tests, CI, security/privacy, performance, observability, rollback, docs/support, and release communication
- release_gate_verdict/v1 with GO, HOLD, or BLOCK plus missing evidence
- rollback_and_monitoring_plan/v1 with health signals, owner, threshold, and recovery path
- Artifact contracts:
- This label denotes the machine-enforcement level, not a skill quality score and not an observed evidence state.
- contract_id: `readiness_matrix/v1`; enforcement_level: `executable_validated`; consumer_id: `parse_readiness_matrix`

## Acceptance criteria
- Findings or no-issue results are grounded in concrete file, artifact, command, or source evidence.
- Open questions, residual risk, and missing verification are named.
- Fixes or follow-up work are separate handoffs unless the user explicitly asked to implement them.

## Handoff policy
Keep readiness synthesis in Hermes. Code fixes, deploys, infrastructure changes, security scans, and platform actions require selected executor/runtime or operator evidence.

## Catalog rules
- Source routing exclusion: The user wants to implement a feature or fix; prepare a coding handoff first.
- Source routing exclusion: The user wants incident/SLO analysis after production behavior; use `reliability-review`.
- Source routing exclusion: The user wants a narrow code diff review; use `code-review`.
- Route only on the source-defined description and triggers; do not treat nearest local contracts deploy-and-monitor, ops-review as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-production-audit/SKILL.md`
- SHA256: `be28c1c10dd2a8fdca2e0782fdfbdec209f64375fa589f93d4308ab295964e6f`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member production-audit is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep readiness synthesis in Hermes. Code fixes, deploys, infrastructure changes, security scans, and platform actions require selected executor/runtime or operator evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
