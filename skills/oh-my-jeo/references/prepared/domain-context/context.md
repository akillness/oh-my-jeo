# Prepared guidance: context

Family: `domain-context`<br>
Category: `clarification`<br>
Phase: `terminology-alignment`<br>
Role: `planner`

## Contract
[omh] Repository vocabulary unclear or inconsistent: project terminology alignment workflow: look up, capture, correct, and align the words a repository uses before planning or handoff. Use when the user says: ulw-context, project terminology alignment, review project terms, align project terminology, terminology this project uses.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- context
- ulw-context
- project terminology alignment
- review project terms
- align project terminology
- terminology this project uses

## Required inputs
- the terminology question or alignment goal
- repository evidence and optional root PROJECT_TERMS.md source status
- active reviewed project terminology profile when one exists
- unresolved decisions and their dependency relationships when an interview is needed

## Expected outputs
- direct source-labeled terminology answer or proposed terminology alignment
- dependency-ready frontier with concise recommendations when decisions remain
- explicit pending-candidate staging choice when machine mappings should be reviewed
- confirmed shared-understanding summary and separately prepared planning or coding-owner handoff

## Artifact expectations
- optional human-reviewed PROJECT_TERMS.md patch proposal that OMH does not write automatically
- pending domain-intelligence candidates only after explicit staging confirmation
- prepared `ulw-plan` or selected coding-owner handoff only after separate confirmation

## Acceptance criteria
- Source status and reviewed-profile status are named without treating either as model-use evidence.
- Safe lookups were answered directly and unresolved decisions were asked only when the user confirmed interview entry.
- Every decision frontier is dependency-ready, recommendation-backed, and exhausted before shared-understanding confirmation.
- Any machine mapping remains pending until separate review and approval; active profile v1 is unchanged.
- Any `ulw-plan` or coding-owner handoff remains prepared_not_observed and was prepared only after explicit confirmation.

## Handoff policy
Keep terminology lookup, source inspection, and decision-frontier facilitation in Hermes. Stage project candidates only after explicit confirmation, activate them only through the existing separate review lifecycle, and prepare `ulw-plan` or a selected executor-neutral coding handoff only after the user confirms shared understanding and the next path.

## Catalog rules
- Source routing exclusion: A safe one-term definition or source lookup can be answered directly; use the read-only lookup mode and do not enter the full context interview.
- Source routing exclusion: The request is broad ambiguity with no project-language conflict; use `deep-interview`.
- Source routing exclusion: The unresolved decision is empirical and a cheap isolated experiment can answer it; use `decision-prototype` and keep the frontier for the rest.
- Source routing exclusion: The terminology is already agreed and the request is to produce an implementation plan; use `ralplan`.
- Source routing exclusion: The user wants to capture or curate general retained memory rather than repository terminology; use `memory-new` or `memory-sync`.
- Source routing exclusion: The user asks for workflow discovery, help, status, file lookup, direct answer, or dispatch; preserve `oh-my-hermes` and ordinary protected-route behavior.
- Route only on the source-defined description and triggers; do not treat nearest local contracts deep-interview as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/ulw-context/SKILL.md`
- SHA256: `372aa8e9d50db2e0f7e60988e1b9ee0bfd13a0a4e64dbd24d8e0d40067b3d80b`

## Method references
- `context/ulw-context/references/decision-frontier.md` (pinned `skills/ulw-context/references/decision-frontier.md`)
- `context/ulw-context/references/project-terms.md` (pinned `skills/ulw-context/references/project-terms.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member context is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep terminology lookup, source inspection, and decision-frontier facilitation in Hermes. Stage project candidates only after explicit confirmation, activate them only through the existing separate review lifecycle, and prepare `ulw-plan` or a selected executor-neutral coding handoff only after the user confirms shared understanding and the next path. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
