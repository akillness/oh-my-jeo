# Prepared guidance: ultraperf

Family: `performance-procedure`<br>
Category: `optimization`<br>
Phase: `measured-optimization-loop`<br>
Role: `tracker`

## Contract
[omh] Software slowness, memory leaks, or cost spikes: find where a system is actually slow, leaking, or expensive across runtime, memory, token cost, storage, rendering, inference, CI, and query domains, then fix one measured hot path at a time behind a regression budget. Use when the user says: ultraperf, ulw-perf, performance audit, performance bottleneck, find the bottleneck, profile the hot path, memory leak investigation, token cost hotspot.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- ultraperf
- $ultraperf
- ulw-perf
- performance audit
- performance bottleneck
- find the bottleneck
- profile the hot path
- memory leak investigation
- token cost hotspot
- storage footprint audit
- rendering jank
- model inference hotspot
- slow ci pipeline
- query performance audit
- performance-goal
- performance goal
- latency
- throughput
- benchmark
- 성능 병목
- 메모리 누수
- 느려진 원인
- 성능 전반 점검

## Required inputs
- symptom or suspected slow surface
- workload or reproduction
- runnable evaluator or measurement command
- acceptable tolerance

## Expected outputs
- baseline record
- ranked hot-path hypotheses
- smallest reversible fix handoff
- re-measured delta
- regression budget and gate

## Artifact expectations
- baseline measurement record
- final profile or benchmark evidence
- budget delta with tolerance

## Acceptance criteria
- Baseline, workload, environment, and evaluator command are recorded before any edit is proposed.
- Each accepted fix names the measured hot path, the reversible change, and its owner.
- Re-measured deltas cite observed evidence; unmeasured steps stay not_observed.
- The regression budget and the gate that enforces it are stated with the tolerance.

## Handoff policy
Hermes owns the audit, baseline, hypothesis, budget, and status; every optimization code edit becomes a selected executor/runtime handoff and returns as observed re-measurement.

## Catalog rules
- quality_tier: measurement-gated
- contract_source: skills/ulw-perf/SKILL.md:67
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/ulw-perf/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/ulw-perf/SKILL.md`
- SHA256: `fbff5ed34135d088446e31b02f4ab6638a35c607355111cfff38c587bdda1abf`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- Required source input: symptom or suspected slow surface
- Required source input: workload or reproduction
- Required source input: runnable evaluator or measurement command
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for ultraperf: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
