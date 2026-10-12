# Prepared guidance: codebase-onboarding

Family: `code-intelligence`<br>
Category: `planning`<br>
Phase: `codebase-onboarding`<br>
Role: `planner`

## Contract
[omh] Unfamiliar repository needing a guided tour: create a repo map, reading path, glossary, risk map, and first-task runway for unfamiliar codebases. Use when the user says: codebase-onboarding, codebase onboarding, repo onboarding, repository onboarding, codebase tour, code tour, new repo orientation, understand this repo.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- codebase-onboarding
- codebase onboarding
- repo onboarding
- repository onboarding
- codebase tour
- code tour
- new repo orientation
- understand this repo

## Required inputs
- repo root or supplied source context
- target audience: operator, new contributor, maintainer, or executor
- desired depth: quick map, architecture tour, first issue, or handoff pack
- known constraints such as no network, no secrets, or read-only mode

## Expected outputs
- codebase_onboarding_plan/v1
- repo_map/v1
- reading_path/v1
- domain_glossary/v1
- risk_and_unknowns_map/v1
- first_task_runway/v1
- not-evidence boundary

## Artifact expectations
- repo_map/v1 with observed directories, entrypoints, generated surfaces, tests, docs, scripts, and runtime artifacts
- reading_path/v1 ordered from product direction to architecture, core modules, tests, and operational docs
- domain_glossary/v1 with repo-specific terms, owners, artifacts, and evidence references
- first_task_runway/v1 with low-risk starter tasks, verification commands, and handoff readiness

## Acceptance criteria
- The plan names goals, non-goals, assumptions, acceptance criteria, and verification shape.
- Draft recommendations, accepted decisions, and executor handoffs are separate states.
- Rejected options or unresolved tradeoffs are recorded before handoff.

## Handoff policy
Keep codebase orientation in Hermes as prepared local context. File reads, generated maps, and first-task recommendations need observed repo evidence; code edits and executor handoffs happen only after onboarding identifies a concrete task.

## Catalog rules
- Source routing exclusion: The user already named a concrete implementation task and acceptance criteria; use `ultrawork` or `idea-to-deploy`.
- Source routing exclusion: The user needs a whole-workspace capability inventory; use `workspace-audit`.
- Source routing exclusion: The user wants a code diff review; use `code-review`.
- Route only on the source-defined description and triggers; do not treat nearest local contracts plan as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-codebase-onboarding/SKILL.md`
- SHA256: `c604623f641ae38026951712bbe2e6ed62ba26fc5413ed066dfeb66c181598e3`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member codebase-onboarding is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep codebase orientation in Hermes as prepared local context. File reads, generated maps, and first-task recommendations need observed repo evidence; code edits and executor handoffs happen only after onboarding identifies a concrete task. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
