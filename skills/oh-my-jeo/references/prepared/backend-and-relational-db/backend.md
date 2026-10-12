# Prepared guidance: backend

Family: `backend-and-relational-db`  
Category: `planning`  
Phase: `backend-design`  
Role: `planner`

## Contract
[omh] Designing an API, server, or data-layer change: prepare server, API, and data-layer contracts — auth boundary, error paths, response shape, and schema/migration discipline — before implementation. Use when the user says: backend, back-end, back end, backend skill, server side, server-side, api design, api contract.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- backend
- back-end
- back end
- backend skill
- server side
- server-side
- api design
- api contract

## Required inputs
- the service, endpoint, or data surface being changed
- callers and their trust level (public, partner, internal, machine)
- language, framework, and datastore when known
- authentication and authorization model in force
- existing schema and migration tooling
- backward-compatibility and rollout constraints
- observed integration or load evidence for completion claims

## Expected outputs
- backend_service_contract/v1
- auth_boundary_map/v1
- error_path_table/v1
- response_shape_contract/v1
- schema_migration_plan/v1 when the change touches storage
- consumer_impact_and_sunset/v1 when an existing contract changes
- backend_implementation_handoff/v1
- observed_integration_evidence/v1 when observed

## Artifact expectations
- backend_service_contract/v1 names each endpoint or job, its caller class, request and response shapes, and its idempotency and pagination rules
- auth_boundary_map/v1 states where an untrusted caller becomes a trusted one, and which check runs on each path
- error_path_table/v1 pairs every failure mode with its status/code, body shape, retryability, and log/redaction rule
- response_shape_contract/v1 keeps success and error envelopes consistent across the surface instead of per-endpoint improvisation
- schema_migration_plan/v1 orders expand, backfill, switch, and contract steps with the rollback point for each
- consumer_impact_and_sunset/v1 lists each identified consumer with what breaks for it, then the compatibility window, the migration path, and the sunset date; a consumer set that could not be enumerated is reported as `consumers_not_enumerable` with the reason, never as zero breakage
- integration runs, applied migrations, load numbers, and deployment only when observed

## Acceptance criteria
- The surface, its callers, and each caller's trust level are named.
- The auth_boundary_map/v1 states where trust changes and which check enforces it on every path.
- The error_path_table/v1 covers each failure mode with status, body shape, retryability, and redaction rule.
- The response_shape_contract/v1 is consistent across endpoints rather than per-endpoint improvisation.
- Storage changes carry an expand/backfill/switch/contract order with a rollback point per step.
- A change to an existing contract carries its consumer list or an explicit `consumers_not_enumerable`, plus the compatibility window, migration path, and sunset date.
- The handoff names the executor, the stack, and the per-stack reference to load first.
- Implementation, migrations, integration runs, and deployment stay observed-only.

## Handoff policy
Keep the service contract, auth boundary, error-path table, and migration plan in Hermes. Record code changes, running servers, applied migrations, integration runs, and load results only from executor or wrapper observed evidence.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: backend-contract-gated
- source owner: skills/omh-backend/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-backend/SKILL.md`
- SHA256: `1579e0f0651b81b79bfac370ebdf9be910cddfa5460431244f144a767c191a42`

## Method references
- `omh-backend/references/consumer-impact.md` (pinned `skills/omh-backend/references/consumer-impact.md`)
- `omh-backend/references/schema-migration.md` (pinned `skills/omh-backend/references/schema-migration.md`)
- `omh-backend/references/service-contract.md` (pinned `skills/omh-backend/references/service-contract.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: the service, endpoint, or data surface being changed
- blocked until supplied or observed: callers and their trust level (public, partner, internal, machine)
- blocked until supplied or observed: language, framework, and datastore when known
- blocked until supplied or observed: authentication and authorization model in force
- blocked until supplied or observed: existing schema and migration tooling
- blocked until supplied or observed: backward-compatibility and rollout constraints
- blocked until supplied or observed: observed integration or load evidence for completion claims
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
