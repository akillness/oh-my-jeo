# Prepared guidance: award-bar-score

Family: `design-direction`<br>
Category: `materials`<br>
Phase: `award-bar-score`<br>
Role: `operator`

## Contract
[omh] Aiming for design-award quality: score a web surface against published design-award judging axes and name the binding constraint. Use when the user says: award-bar-score, award bar score, award winning, award-winning, award winning website, award-winning website, award winning design, award ready.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- award-bar-score
- award bar score
- award winning
- award-winning
- award winning website
- award-winning website
- award winning design
- award ready
- make it award winning
- design award
- design awards
- css design awards
- cssda
- awwwards
- site of the day
- website of the day
- wotd
- score my site
- 어워드
- 디자인 어워드
- 어워드 수준
- 수상작 수준
- 수상 가능한 디자인
- 어워드 받을만한
- 올해의 사이트

## Required inputs
- the target URL, route, or rendered capture being judged
- the award model and its published axes, weights, and threshold
- the surface's own accessibility and performance budgets
- audience and primary user task

## Expected outputs
- award_bar_score/v1
- per-axis scores with named evidence for UI, UX, and innovation
- the weighted total and its distance from the published threshold
- the binding constraint: the axis whose gain moves the total most
- tradeoff_ledger/v1 when an innovation move costs accessibility or performance budget
- downstream route: frontend, accessibility-audit, visual-qa, or design-quality-gate

## Artifact expectations
- award_bar_score/v1 with prepared_not_observed status
- every axis score cites the rendered evidence it was read from, or stays not_observed
- the weighted total is arithmetic over the stated weights, never an impression
- no claim that a submission would win, place, or be selected

## Acceptance criteria
- Each of UI, UX, and innovation carries its own score and the rendered evidence it was read from.
- The weighted total is computed from the stated weights and compared against the published threshold.
- The binding constraint names one axis and what moving it requires.
- Any innovation move that costs accessibility or performance budget is recorded as a tradeoff the user chooses.
- No award, jury, placement, or selection outcome is claimed.

## Handoff policy
Keep axis scoring, the weighted total, the binding-constraint call, and the tradeoff ledger in Hermes. Route implementation to frontend, WCAG evidence to accessibility-audit, and rendered captures to visual-qa; never score an axis from a description of a page instead of the page.

## Catalog rules
- quality_tier: design-orchestration-gated
- contract_source: skills/omh-award-bar-score/SKILL.md:68
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Load `references/award-judging-model.md` for the published axes, weights, and thresholds, the measured per-axis score table, and the stack table that separates entry-fee craft (fluid type, real typography) from optional spend (WebGL).
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-award-bar-score/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-award-bar-score/SKILL.md`
- SHA256: `b8d1ad604145a81d879ffc32b671f0df1f12f8fb58852932cffb44f350da54e6`

## Method references
- `omh-award-bar-score/references/award-judging-model.md` (pinned `skills/omh-award-bar-score/references/award-judging-model.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: the target URL, route, or rendered capture being judged
- Required source input: the award model and its published axes, weights, and threshold
- Required source input: the surface's own accessibility and performance budgets

## Evidence boundary
prepared_not_observed for award-bar-score: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
