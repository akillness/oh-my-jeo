# Prepared guidance: relational-db

Family: `backend-and-relational-db`<br>
Category: `planning`<br>
Phase: `relational-db`<br>
Role: `planner`

## Contract
[omh] Database work on a relational store -- a slow query, an index to size, a migration on a big table, a lock taken during deploy, N+1 queries: plan it with the checks that prove it safe, and never call a migration ready without its lock behaviour and rollback. Use when the user says: relational-db, relational database, online migration, migration for a large table, lock-safe ddl, alter table, took a lock, table lock.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- relational-db
- relational database
- online migration
- migration for a large table
- lock-safe ddl
- alter table
- took a lock
- table lock

## Required inputs
- engine and version, and whether it is managed or self-hosted
- the table sizes involved, in rows and bytes, and the write rate
- the query, its observed plan (`EXPLAIN (ANALYZE, BUFFERS)` or the engine's equivalent), and its latency
- for a migration: the statements, the deploy mechanism, and the longest lock the service tolerates
- observed evidence for any readiness or completion claim

## Expected outputs
- db_problem_statement/v1
- query_plan_evidence/v1 when a query is involved
- index_proposal/v1 when an index is proposed
- online_migration_plan/v1 when a table changes shape
- n_plus_one_finding/v1 when an endpoint issues per-row queries
- capacity_projection/v1 when partitioning or sharding is asked
- migration_readiness_verdict/v1

## Artifact expectations
- db_problem_statement/v1 names the engine, the version, the table sizes, and the observed symptom separately from the suspected cause
- index_proposal/v1 gives the columns in order, the index type, the estimated size, the write cost, and the non-blocking build method
- online_migration_plan/v1 gives every step its statement, the lock mode it takes and for how long, the `lock_timeout` guarding it, the backfill batch size, and its rollback
- migration_readiness_verdict/v1 reads ready only when every step states lock behaviour and a rollback; otherwise it names the steps that do not
- capacity_projection/v1 projects rows, bytes, and write rate against the single-node limit before recommending a partition or a shard

## Acceptance criteria
- Engine, version, and table sizes are stated.
- Every proposed index cites an observed plan or is marked unverified.
- Every migration step states its lock mode, its duration bound, and its rollback.
- The readiness verdict is ready only when no step lacks lock behaviour or rollback.
- Nothing was connected to, run, or applied by OMH.

## Handoff policy
Keep the problem statement, the index proposal, the migration plan with its lock behaviour and rollback, and the readiness verdict in Hermes. Query plans, row counts, lock waits, and every applied statement are recorded only from executor, operator, or wrapper observed output; OMH never connects to a database.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: db-lock-and-rollback-gated
- source owner: skills/omh-relational-db/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-relational-db/SKILL.md`
- SHA256: `02be09b6e1cc793de7008e7d4e68f635db9f6a654e2bb9f0849b2d957ea44bfe`

## Method references
- `omh-relational-db/references/engine-lock-tables.md` (pinned `skills/omh-relational-db/references/engine-lock-tables.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: engine and version, and whether it is managed or self-hosted
- blocked until supplied or observed: the table sizes involved, in rows and bytes, and the write rate
- blocked until supplied or observed: the query, its observed plan (`EXPLAIN (ANALYZE, BUFFERS)` or the engine's equivalent), and its latency
- blocked until supplied or observed: for a migration: the statements, the deploy mechanism, and the longest lock the service tolerates
- blocked until supplied or observed: observed evidence for any readiness or completion claim
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
