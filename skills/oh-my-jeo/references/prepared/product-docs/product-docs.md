# Prepared guidance: product-docs

Family: `product-docs`<br>
Category: `research`<br>
Phase: `product-documentation`<br>
Role: `researcher`

## Contract
[omh] Explaining OMH itself: current-source-first documentation for OMH itself: product identity, public capability catalog, model routing, local state, and long-term memory. Use when the user says: product-docs, OMH documentation, oh-my-hermes documentation, what is OMH, what is oh-my-hermes, how does OMH work, OMH capability catalog, OMH skill catalog.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- product-docs
- product-docs

## Required inputs
- A bounded product-docs documentation request and its disclosed source scope

## Expected outputs
- Prepared product-docs source-backed answer with explicit not_observed gaps

## Artifact expectations
- Metadata-only prepared product-docs record; no mutation or execution evidence

## Acceptance criteria
- Answer only from disclosed current sources or bounded local observations.
- Treat wrapper metadata-only memory comparisons as advisory local context,
- not proof of Hermes-memory mutation or raw-entry exposure.
- Record observed delegation results; otherwise return `not_available` or
- `not_observed`.
- Prepared OMH routing is not execution, review, CI, or merge evidence.
- Preserve workflow intent and stop conditions; verify before claiming
- completion.
- Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply language, tone, speech level, and sentence endings, progress updates included (where it sets no language, use the one the user wrote in), and OMH shapes structure and content only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Use Hermes-native subagent/delegation features when available:
- native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Handoff policy
Answer read-only OMH documentation questions directly from official current sources or bounded local metadata. Route requested setup, update, settings, or code mutations to the appropriate specialized workflow and stop before mutation unless the user separately authorizes it.

## Catalog rules
- quality_tier: source-gated
- contract_source: skills/omh-docs/SKILL.md:1
- Source Route: `references/product-and-sources.md` for the full official-source hierarchy,
- Source Route: `references/capability-map.md`. It covers the six public capability families,
- Source Route: `references/model-routing-and-local-state.md`. It separates published routing
- Source Route: `references/long-term-memory.md`. It distinguishes reviewed OMH project memory
- Workflow Lane: `omh-routing/references/skill-common-rail.md`.
- source_reference_text_source: skills/omh-docs/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-docs/SKILL.md`
- SHA256: `5a2b13a24e3898b8b34153cea07eb1cfa2b6f74343c58a727fdc9bbeabbafd4a`

## Method references
- `product-docs/omh-docs/references/capability-map.md` (pinned `skills/omh-docs/references/capability-map.md`)
- `product-docs/omh-docs/references/long-term-memory.md` (pinned `skills/omh-docs/references/long-term-memory.md`)
- `product-docs/omh-docs/references/model-routing-and-local-state.md` (pinned `skills/omh-docs/references/model-routing-and-local-state.md`)
- `product-docs/omh-docs/references/product-and-sources.md` (pinned `skills/omh-docs/references/product-and-sources.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: A bounded product-docs documentation request and its disclosed source scope

## Evidence boundary
prepared_not_observed for product-docs: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
