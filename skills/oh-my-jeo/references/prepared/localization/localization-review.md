# Prepared guidance: localization-review

Family: `localization`<br>
Category: `review`<br>
Phase: `localization-review`<br>
Role: `reviewer`

## Contract
[omh] Translated product or content release: make a product or content release locale-ready with terminology, cultural-fit, and quality-review guidance. Use when the user says: localization review, translation QA, locale glossary, 현지화 검토, 번역 QA, 용어집.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- localization-review
- localization review
- translation QA
- locale glossary
- 현지화 검토
- 번역 QA
- 용어집

## Required inputs
- locale
- audience
- source version
- product or content context

## Expected outputs
- locale/audience/context and source-version brief
- approved-term glossary and transcreation/localization choices
- string/content issue matrix with context, severity, and review owner
- locale QA acceptance criteria and handoff/observed-evidence gaps

## Artifact expectations
- prepared localization review when a wrapper captures it

## Acceptance criteria
- Findings or no-issue results are grounded in concrete file, artifact, command, or source evidence.
- Open questions, residual risk, and missing verification are named.
- Fixes or follow-up work are separate handoffs unless the user explicitly asked to implement them.

## Handoff policy
Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. Hermes may draft and review language guidance; it does not alter locale files, upload strings, publish translations, validate a rendered build, or claim market approval.

## Catalog rules
- Source routing exclusion: The request is a short sentence or word translation or rewrite with no product or locale QA context; answer directly or use `content-operator`.
- Source routing exclusion: The user needs fresh rendered UI evidence, clipping checks, or a visual PASS/REVISE/BLOCK verdict; use `visual-qa`.
- Source routing exclusion: The user asks to edit locale files, push a translation-management-system job, publish strings, or configure localization settings; use `workspace-file-operator` or `connector-operator` with explicit target and authority.
- Source routing exclusion: The request asks for a regulatory or contractual conclusion about translated legal text; use `legal-compliance-review`.
- Route only on the source-defined description and triggers; do not treat nearest local contracts materials-package as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-localization-review/SKILL.md`
- SHA256: `16a8c9bf1b5716695c37dc66effffd0fddaee853e1296e44badcb0dcdb4f8bdf`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member localization-review is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. Hermes may draft and review language guidance; it does not alter locale files, upload strings, publish translations, validate a rendered build, or claim market approval. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
