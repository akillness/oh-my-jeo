# Prepared guidance: refactor-plan

Family: `behavior-preserving-refactor`  
Category: `planning`  
Phase: `refactor-plan`  
Role: `planner`

## Contract
[omh] Decided cross-module refactor to phase: refactor planning - turn a decided boundary-changing refactor into a phased plan - reconnaissance, contracts-first phase order, per-phase verification and rollback, a files table, and an explicit approval gate before any edit. Use when the user says: refactor-plan, refactor plan, plan this refactor, plan the refactor, refactor planning, refactor phases, phased refactor, refactor in phases.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- refactor-plan
- refactor plan
- plan this refactor
- plan the refactor
- refactor planning
- refactor phases
- phased refactor
- refactor in phases

## Required inputs
- the decided target shape (what moves where), or a pointer to the accepted plan that decided it
- the affected-file evidence: import graph, codegraph handoff, or an observed file inventory
- the regression gates that exist today (test suite, typecheck, generated-artifact checks)

## Expected outputs
- reconnaissance: affected files, ownership boundaries, hidden coupling, blast radius — and for an upgrade, the advisory, licence, migration-guide, and lockfile intake
- phase plan in the fixed order - types/interfaces, implementations, callers, tests, cleanup - each with verification and rollback
- files table: path, action, phase, blocks/blocked-by
- for an upgrade, the call-site readiness gate: every breaking change between the two versions against this repository's call sites or an observed empty search, and every stage's rollback
- the approval gate: the plan stops and waits for the user's go

## Artifact expectations
- metadata-only runtime record when a wrapper or shell is available

## Acceptance criteria
- Reconnaissance names affected files, boundaries, coupling, and blast radius from observed evidence.
- Every phase carries its verification command and its rollback point, and ends at a shippable commit.
- The files table covers every touched file with action, phase, and dependencies.
- For an upgrade, every breaking change row names its call sites or an observed empty search, and every stage names its rollback.
- The plan stopped at the approval gate; no implementation began without the user's go.

## Handoff policy
Hermes owns reconnaissance and the phased plan; implementation of any approved phase is coding work for the selected executor lane under its own evidence rules. An approved plan is approval of the order, not evidence any phase ran.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The refactor's direction is still contested or the goal itself needs consensus planning; use `ralplan`.
- Source routing exclusion: The work is deletion-first cleanup with no boundary changes; use `ai-slop-cleaner`.
- Source routing exclusion: The plan is done and the claim is that work is complete; use `verification-gate` for the evidence close.
- Source routing exclusion: The version bump carries a security advisory, a CVE, or a leaked secret; use `security-event-response`, which owns containment and closure.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-refactor-plan/SKILL.md`
- SHA256: `205d3ecac0b4101b105d69ba0b33e80c2ee5fa120de7982ba98b6f58686014b7`

## Method references
- `omh-refactor-plan/references/dependency-upgrade.md` (pinned `skills/omh-refactor-plan/references/dependency-upgrade.md`)
- `omh-refactor-plan/references/refactor-phases.md` (pinned `skills/omh-refactor-plan/references/refactor-phases.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member refactor-plan is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
