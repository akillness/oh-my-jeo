# Prepared guidance: adversarial-consensus

Family: `adversarial-decision`<br>
Category: `planning`<br>
Phase: `adversarial-consensus`<br>
Role: `planner`

## Contract
[omh] Technical proposal facing adversarial scrutiny: independent perspectives attack a proposal, then distill into a bundle a separate planner consumes. Use when the user says: adversarial-consensus, adversarial planning, adversarial plan review, red team this plan, red-team this plan, red team the proposal, multi-perspective review, multiple perspectives.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- adversarial-consensus
- adversarial planning
- adversarial plan review
- red team this plan
- red-team this plan
- red team the proposal
- multi-perspective review
- multiple perspectives

## Required inputs
- the proposal, plan draft, or direction under review
- the decision the review must inform
- known constraints and non-negotiables
- the perspective roster and why each angle is distinct

## Expected outputs
- per-perspective independent findings
- cross-attack objections attributed to their author
- defend, refine, or concede verdict per objection
- distilled bundle in the fixed buckets Hard Constraints, Decisions, Risks, Open Questions
- mandatory planner handoff naming the follow-on planning workflow

## Artifact expectations
- record the distilled bundle with `omh hermes plan --record`, which writes `<repo>/.omh/plans/<slug>.md` inside a repository and the user-scope OMH store outside one, so the planner pass consumes a file rather than scrollback

## Acceptance criteria
- The roster is named with 3-5 distinct angles, and no two seats argue the same one.
- Round-one findings were produced blind, and any perspective that could not be kept blind is named as a broken-independence caveat instead of being presented as independent.
- Every cross-attack objection targets another perspective's finding, and no perspective defended itself in that round.
- Every objection carries exactly one verdict — defended, refined, or conceded — and conceded findings are struck, not softened.
- The bundle contains only Hard Constraints, Decisions, Risks, Open Questions, every line traces to a surviving finding, and nothing new was added at distillation.
- The closing message states that the bundle is input, names the follow-on planning workflow, and claims no plan, acceptance, implementation, or verification evidence.

## Handoff policy
Keep every round in Hermes as prepared prompt contracts. The distilled bundle is planning input: hand it to `ralplan` or `plan` for the plan itself, and prepare a selected executor/runtime handoff only after that separate planning pass produces an accepted plan.

## Catalog rules
- Source routing exclusion: The user wants the plan itself, with options, acceptance criteria, and verification commands; use `ralplan`, which this workflow feeds.
- Source routing exclusion: The request is still too ambiguous to state the proposal being attacked; use `deep-interview` first.
- Source routing exclusion: The user wants completed code reviewed for defects rather than a proposal attacked before it is built; use `code-review`.
- Source routing exclusion: The user wants hostile runtime scenarios against a built change; use `ultraqa`.
- Source routing exclusion: One perspective would do: a small local change with no contested decision does not earn three rounds.
- Route only on the source-defined description and triggers; do not treat nearest local contracts ralplan as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-adversarial-consensus/SKILL.md`
- SHA256: `c531e927bf354b3c1f16dacd4124879162a592b2b4827c27fbc3fb3b2884fb8c`

## Method references
- `adversarial-consensus/omh-adversarial-consensus/references/consensus-protocol.md` (pinned `skills/omh-adversarial-consensus/references/consensus-protocol.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member adversarial-consensus is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep every round in Hermes as prepared prompt contracts. The distilled bundle is planning input: hand it to `ralplan` or `plan` for the plan itself, and prepare a selected executor/runtime handoff only after that separate planning pass produces an accepted plan. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
