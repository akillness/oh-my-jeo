# Prepared guidance: inference-serving

Family: `inference-serving`<br>
Category: `operations`<br>
Phase: `inference-serving`<br>
Role: `operator`

## Contract
[omh] Self-hosted LLM serving on GPUs: choose the serving engine and quantization from decision tables, prepare deployment as an idempotent runbook with observed-only verification, and measure the endpoint with the standard TTFT/TPOT/goodput protocol. Use when the user says: inference-serving, inference serving, serve this model, serve the model, model serving, serving endpoint, vllm, llama.cpp.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- inference-serving
- inference serving
- serve this model
- serve the model
- model serving
- serving endpoint
- vllm
- llama.cpp

## Required inputs
- the model id(s) and where the weights live (HF id, local path, gated or not)
- the hardware truth: GPUs and VRAM, or CPU/Apple Silicon, and single- vs multi-user load
- the delivery surface: docker, Kubernetes, or bare process, and the port/ingress constraints
- for benchmarks: the SLO (TTFT/TPOT bounds) and the load shape the number must represent

## Expected outputs
- engine and quantization verdict from the decision tables, with the rejected options named
- deployment runbook with its gates (secret, existing-deployment), verification commands, and the four-places port invariant
- benchmark plan naming metrics, load shape, dataset, and metadata to save
- observed-only status: what ran, what was verified, what stays prepared

## Artifact expectations
- serving decision and runbook per `omh-inference-serving/references/serving-runbooks.md`
- benchmark protocol per `omh-inference-serving/references/serving-bench.md`
- result files with metadata only after observed runs

## Acceptance criteria
- The engine/quantization verdict names the situation-table row it came from and the rejected options.
- Every runbook step's status is prepared or observed, never assumed, and the port invariant was honored.
- Benchmark numbers carry metrics, load shape, dataset, SLO, and saved metadata, or are not reported.
- Anything the workflow started for measurement was stopped, and credentials never appear in artifacts.

## Handoff policy
Keep engine/quantization decisions, runbook preparation, and benchmark design in Hermes; the commands run through the operator's terminal with observed evidence, and repository changes (deploy manifests, benchmark harnesses) are coding work for the selected executor lane. A runbook or benchmark plan is prepared_not_observed until its commands' results are seen.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: A new model generation needs recognition, calibration, routing, and pricing onboarding; use `model-optimization`.
- Source routing exclusion: The user wants their own machine's model routing or providers configured; use `model-setup`.
- Source routing exclusion: The question is whether a coding runtime/executor can run at all; use `executor-runtime-readiness`.
- Source routing exclusion: The goal is application or system performance rather than the serving endpoint itself; use `ultraperf`.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-inference-serving/SKILL.md`
- SHA256: `40846949cfeefef13cd6029c61fb41c92e5a53c13f199a25e65609b22ec2286f`

## Method references
- `omh-inference-serving/references/serving-bench.md` (pinned `skills/omh-inference-serving/references/serving-bench.md`)
- `omh-inference-serving/references/serving-runbooks.md` (pinned `skills/omh-inference-serving/references/serving-runbooks.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member inference-serving is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
