# Prepared guidance: native-debugging

Family: `application-and-native-debug`  
Category: `verification`  
Phase: `native-debugging`  
Role: `reviewer`

## Contract
[omh] Native program crashes or corrupts memory: prepare hypothesis-driven debugging of native binaries and instruct the executor to drive a DAP debugger instead of printf. Use when the user says: native-debugging, native debugging, native binary, segfault, segmentation fault, core dump, stack corruption, memory corruption.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- native-debugging
- native debugging
- native binary
- segfault
- segmentation fault
- core dump
- stack corruption
- memory corruption

## Required inputs
- the binary, crash signature, or fault symptom
- whether source and debug symbols are available
- platform, architecture, and the reproduction command
- how reliably the fault reproduces
- existing crash logs, core dumps, or sanitizer output
- observed debugger evidence for any resolution claim

## Expected outputs
- native_fault_statement/v1
- hypothesis_set/v1 with at least three competing hypotheses
- distinguishing_observation_plan/v1
- debugger_session_plan/v1
- native_debug_handoff/v1
- observed_debugger_evidence/v1 when observed

## Artifact expectations
- native_fault_statement/v1 separates the observed symptom from the assumed cause and names the reproduction command
- hypothesis_set/v1 spans distinct axes — caller-side misuse, callee invariant, memory lifetime, concurrency, build/runtime mismatch — not three phrasings of one guess
- distinguishing_observation_plan/v1 pairs each hypothesis with the one observation that refutes it, and where to read it
- debugger_session_plan/v1 names the adapter (lldb or gdb via DAP), the breakpoints and watchpoints, the frames and threads to inspect, and the values to read at each stop
- native_debug_handoff/v1 states that the executor drives the debugger and OMH executes nothing
- breakpoint hits, memory and register reads, backtraces, and confirmed reproductions only when observed

## Acceptance criteria
- The fault is stated as an observed symptom with a reproduction command, separate from any assumed cause.
- At least three hypotheses span distinct axes and each carries its refuting observation.
- The debugger session plan names the DAP adapter, breakpoints, watchpoints, threads, frames, and values to read.
- The handoff says the executor drives the debugger and OMH executes nothing.
- Reproduction, debugger output, root cause, and fix are reported as separate observed or not_observed states.

## Handoff policy
Keep the fault statement, hypothesis set, distinguishing observations, and the debugger plan in Hermes. Record every breakpoint hit, register or memory read, backtrace, and reproduction only from executor or wrapper observed evidence.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The failure is a build or CI failure rather than a runtime fault in a binary; use `build-failure-triage`.
- Source routing exclusion: The subject is an agent or workflow misbehaving rather than a native binary; use `agent-debug`.
- Source routing exclusion: The wrong result, flaky test, or lost update is in application code such as a Python or TypeScript service and needs its root cause reproduced; use `app-debugging`.
- Source routing exclusion: The change is Rust source work whose risk is `unsafe` or UB discipline; use `rust`.
- Source routing exclusion: The request is to judge whether a fix is verified rather than to find the fault; use `verification-gate`.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-native-debugging/SKILL.md`
- SHA256: `ff35522cac4f4b3f11cbbcfe15cdb4a7d8c7c644dac43b506e3c278621152cba`

## Method references
- `omh-native-debugging/references/native-debug-loop.md` (pinned `skills/omh-native-debugging/references/native-debug-loop.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member native-debugging is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
