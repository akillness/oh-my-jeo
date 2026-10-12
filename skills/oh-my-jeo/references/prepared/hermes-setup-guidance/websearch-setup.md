# Prepared guidance: websearch-setup

Family: `hermes-setup-guidance`<br>
Category: `hermes-setup`<br>
Phase: `setup`<br>
Role: `guide`

## Contract
[omh] Expensive or unconfigured web search: diagnose scraper and auxiliary extract-model configuration, guide account setup, and apply each change as its own diff approval. Use when the user says: websearch-setup, web search setup, make web search cheaper, set up web search, configure web search, reduce web search cost, connect scraper api key, set up auxiliary web-extract model.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- websearch-setup
- web search setup
- make web search cheaper
- set up web search
- configure web search
- reduce web search cost
- connect scraper api key
- set up auxiliary web-extract model

## Required inputs
- scraper API key availability; value through secure entry or user-side setup only
- target auxiliary web-extract model role slot

## Expected outputs
- read-only diagnosis of the current scraper `.env` key and auxiliary web-extract model routing state
- a diff-approved `.env` write adding the scraper API key, approved on its own
- a diff-approved routing block change assigning the auxiliary web-extract model, approved separately from the key write
- verification checklist confirming both writes were applied

## Artifact expectations
- setup verification note when the wrapper captures it

## Acceptance criteria
- If a prerequisite is unmet, mark that item "not applicable" and continue with the rest of the guide instead of blocking or guessing.
- Success is applicable-only: verification passes when every applicable item is confirmed complete, not when every possible item exists.
- The scraper API key write and the auxiliary web-extract model write were verified as two separate, independently-approved changes.

## Handoff policy
Run diagnosis and guidance directly in Hermes for web search setup. Diagnosis reads non-secret metadata only; no writes. Show redacted placeholders in the config or `.env` diff; apply only after the user explicitly approves. Never ask the user to paste secrets into chat. Use Hermes-native secure entry or user-side OAuth/token setup; if unavailable, stop credential application and guide user-side setup. Use only a user-authorized credential store or local configuration; disclose destination and scope first. Keep secrets out of chat, previews, logs and evidence. Do not promise chat or platform non-retention. Delegate to a selected coding executor only if the user needs a change outside chat-driven config or `.env` edits.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: hermes-setup-gated
- source owner: skills/omh-websearch-setup/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-websearch-setup/SKILL.md`
- SHA256: `5429a81ae3d8e62d5974095ae845cdc892f2b2eb10641c87463565e0ba8c5877`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- blocked until supplied or observed: scraper API key availability; value through secure entry or user-side setup only
- blocked until supplied or observed: target auxiliary web-extract model role slot
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
