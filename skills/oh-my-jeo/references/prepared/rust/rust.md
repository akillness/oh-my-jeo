# Prepared guidance: rust

Family: `rust`<br>
Category: `planning`<br>
Phase: `rust-development`<br>
Role: `planner`

## Contract
[omh] Rust ownership, lifetime, or unsafe trouble: prepare Rust changes with ownership, error, and API discipline, and escalate any unsafe, FFI, or lock-free change to the UB checklist. Use when the user says: rust, rust code, rust skill, rustlang, borrow checker, lifetime error, ownership error, trait bound.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- rust
- rust code
- rust skill
- rustlang
- borrow checker
- lifetime error
- ownership error
- trait bound

## Required inputs
- the crate, module, or function being changed
- whether the change touches `unsafe`, raw pointers, FFI, `MaybeUninit`, or a lock-free primitive
- the crate's edition, MSRV, and async runtime when relevant
- existing error type and public API stability constraints
- the gate commands the repository already runs
- observed compiler, clippy, test, and Miri/sanitizer evidence for completion claims

## Expected outputs
- rust_change_contract/v1
- ownership_shape/v1
- error_and_api_contract/v1
- rust_gate_list/v1
- ub_escalation_verdict/v1
- ub_discipline_checklist/v1 when the escalation triggers
- observed_rust_gate_evidence/v1 when observed

## Artifact expectations
- rust_change_contract/v1 names the crate, the change, and the escalation verdict on its first line
- ownership_shape/v1 states who owns each value, which borrows cross a function or await boundary, and where a clone is deliberate rather than a borrow-checker surrender
- error_and_api_contract/v1 names the error type, its conversion boundary, and every `unwrap`, `expect`, or `panic!` that survives with its justification
- rust_gate_list/v1 lists the exact commands the executor must run and pass
- ub_escalation_verdict/v1 is `escalated` or `not_escalated` with the trigger that decided it
- ub_discipline_checklist/v1 adds the Miri, sanitizer, and loom-style concurrency requirements when escalated
- compiler, clippy, test, Miri, sanitizer, and loom results only when observed

## Acceptance criteria
- The escalation verdict is stated with the trigger that decided it.
- The ownership shape names owners, borrows across boundaries, and every deliberate clone.
- The error type, its conversion boundary, and every surviving `unwrap`/`expect`/`panic!` are named.
- The gate list names the exact commands the executor must run and pass.
- An escalated change carries the Miri, sanitizer, and concurrency-testing requirements as blocking items.
- Compiler, clippy, test, Miri, sanitizer, and loom results stay observed-only.

## Handoff policy
Keep the ownership shape, error-type choice, API surface, gate list, and the UB escalation verdict in Hermes. Record compilation, clippy output, test results, Miri runs, sanitizer runs, and loom runs only from executor or wrapper observed evidence.

## Catalog rules
- Source routing exclusion: The request is a server, API, or schema design that happens to mention a Rust stack; use `backend` for the contract and name Rust as the stack.
- Source routing exclusion: The request is debugging a stripped or source-less native binary; use `native-debugging`.
- Source routing exclusion: The request is a general code review of finished Rust; use `code-review`.
- Source routing exclusion: The request is a Rust vocabulary or concept question with no change to prepare; answer it directly.
- Route only on the source-defined description and triggers; do not treat nearest local contracts plan, code-review as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-rust/SKILL.md`
- SHA256: `8810fd2a8d52e2d4bf36b86c1921b84722fa3f01e6875562987679dcab7e86c2`

## Method references
- `omh-rust/references/rust-discipline.md` (pinned `skills/omh-rust/references/rust-discipline.md`)
- `omh-rust/references/ub-escalation.md` (pinned `skills/omh-rust/references/ub-escalation.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member rust is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep the ownership shape, error-type choice, API surface, gate list, and the UB escalation verdict in Hermes. Record compilation, clippy output, test results, Miri runs, sanitizer runs, and loom runs only from executor or wrapper observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
