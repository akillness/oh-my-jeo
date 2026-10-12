# Prepared guidance: tech-debt-audit

Family: `behavior-preserving-refactor`  
Category: `maintenance`  
Phase: `tech-debt-audit`  
Role: `reviewer`

## Contract
[omh] Accumulated tech debt to rank: build the severity-by-effort debt ledger from observed repo evidence - orient, audit the named dimensions with file:line citations, rank fixes and quick wins - and reconcile RESOLVED/NEW/CARRIED against the previous ledger on rerun. Use when the user says: tech-debt-audit, tech debt, tech debt audit, technical debt, technical debt audit, tech debt ledger, debt ledger, audit our tech debt.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- tech-debt-audit
- tech debt
- tech debt audit
- technical debt
- technical debt audit
- tech debt ledger
- debt ledger
- audit our tech debt

## Required inputs
- the repo root or the scoped path list the audit is confined to
- the stack truth from manifests (package/build files), not from memory of the tree
- the previous ledger when one exists, so the rerun can reconcile instead of restart

## Expected outputs
- orientation summary: manifests read, churn ranking, largest files, test and CI entry points
- findings table per `tech_debt_ledger/v1`: id, category, file:line, severity, effort, recommendation
- top fixes ranked by severity and the quick wins ranked by payoff-per-effort
- the looks-bad-but-is-actually-fine list, and the RESOLVED/NEW/CARRIED reconciliation on rerun

## Artifact expectations
- debt ledger per `omh-tech-debt-audit/references/debt-dimensions.md`
- prepared detection commands named per stack, marked observed only after their output is seen

## Acceptance criteria
- Orientation evidence is observed: manifests, churn ranking, and largest files are named, not assumed.
- Every finding has id, dimension, file:line, severity, effort, and a bounded recommendation.
- Quick wins and top fixes are ranked, and the looks-bad-but-is-actually-fine section is present.
- On rerun, every prior finding is reconciled RESOLVED, CARRIED, or superseded - none silently dropped.

## Handoff policy
Hermes owns the orientation, the dimension audit, and the ledger; detection commands run through the operator's terminal and stay prepared_not_observed until their output is seen, and every fix the ledger recommends is coding work for the selected executor lane, never part of the audit.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The target is one diff, PR, or claim rather than the codebase's accumulated state; use `code-review`.
- Source routing exclusion: The user wants the debt removed now, behavior preserved; use `ai-slop-cleaner` for deletion-first cleanup.
- Source routing exclusion: A boundary-changing fix from the ledger needs its execution shaped into phases; use `refactor-plan`.
- Source routing exclusion: The question is release risk for a specific deploy rather than source quality; use `production-audit`.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-tech-debt-audit/SKILL.md`
- SHA256: `e8c5ce7eda593b4a824f67e3391e09dfc81ef52ab963c5e5d74c3574d9f47469`

## Method references
- `omh-tech-debt-audit/references/debt-dimensions.md` (pinned `skills/omh-tech-debt-audit/references/debt-dimensions.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member tech-debt-audit is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
