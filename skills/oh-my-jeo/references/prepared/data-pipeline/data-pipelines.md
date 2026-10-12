# Prepared guidance: data-pipelines

Family: `data-pipeline`<br>
Category: `planning`<br>
Phase: `data-pipelines`<br>
Role: `planner`

## Contract
[omh] Data pipeline work -- an ETL or streaming job, a backfill or replay, duplicate events, a schema change downstream, a lineage question, a data-quality regression: make every rerun idempotent, bound every replay, and gate each load on observed checks. Use when the user says: data-pipelines, data pipeline, data pipelines, etl, elt, etl pipeline, etl job, etl backfill.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- data-pipelines
- data pipeline
- data pipelines
- etl
- elt
- etl pipeline
- etl job
- etl backfill

## Required inputs
- the pipeline: its orchestrator, its sources, its sinks, and its schedule or trigger
- the unit of the problem: the table, topic, or model, and the time window affected
- what makes a row unique at the sink: the natural key, the event id, or the partition
- the downstream readers already known: models, dashboards, exports, services
- observed counts, job logs, or check results for any claim about what was loaded

## Expected outputs
- lineage_map/v1
- schema_change_impact/v1
- idempotency_contract/v1
- replay_backfill_plan/v1
- data_quality_gate/v1

## Artifact expectations
- lineage_map/v1 names each upstream source and each downstream reader of the affected table, topic, or model, from the orchestrator's graph or a lineage record, and marks readers found by search rather than by the graph
- schema_change_impact/v1 classifies the change as additive, widening, or breaking for each downstream reader, and names the reader that breaks and the order that avoids it
- idempotency_contract/v1 names the key that makes a rerun safe -- a natural key upsert, an event-id dedupe window, or a partition overwrite -- and what happens to a row written twice
- replay_backfill_plan/v1 bounds the window, names the target partitions or offsets, pauses or isolates downstream readers, and writes through the idempotency contract so a second run changes nothing
- data_quality_gate/v1 names the observed checks each load must pass before readers see it -- row count against the prior window, key uniqueness, null rate, freshness -- and the value that stops the load

## Acceptance criteria
- The sink's unique key and the idempotency contract are stated.
- Every replay or backfill is bounded by window and target.
- Every downstream reader of a schema change is named with its impact.
- Every load names its data-quality gate and the value that stops it.
- OMH ran nothing, and every count cites observed output or is marked unverified.

## Handoff policy
Keep the lineage map, schema impact, idempotency contract, replay or backfill plan, and quality gates in Hermes. Row counts, job runs, query results and check outcomes are recorded only from executor, operator, or wrapper observed output; OMH never runs a pipeline, triggers a backfill, or queries a warehouse.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: idempotent-replay-gated
- source owner: skills/omh-data-pipelines/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-data-pipelines/SKILL.md`
- SHA256: `085ff980578de449585a9b2e8b9751c681d1c24513060b35c47fa1d1a23d9238`

## Method references
- `omh-data-pipelines/references/pipeline-method.md` (pinned `skills/omh-data-pipelines/references/pipeline-method.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: the pipeline: its orchestrator, its sources, its sinks, and its schedule or trigger
- blocked until supplied or observed: the unit of the problem: the table, topic, or model, and the time window affected
- blocked until supplied or observed: what makes a row unique at the sink: the natural key, the event id, or the partition
- blocked until supplied or observed: the downstream readers already known: models, dashboards, exports, services
- blocked until supplied or observed: observed counts, job logs, or check results for any claim about what was loaded
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
