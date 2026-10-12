# Prepared guidance: morning-brief

Family: `hermes-setup-guidance`<br>
Category: `hermes-setup`<br>
Phase: `setup`<br>
Role: `guide`

## Contract
[omh] Mail and calendar brief configuration: morning brief SETUP (one-time) - connects mail and calendar MCP with read-and-draft-only scope and diff approval; produces the configuration, not the daily brief itself. Use when the user says: morning-brief, morning brief, connect my email for a morning brief, set up morning brief, configure morning brief, connect mail for morning brief, connect calendar for morning brief, set up my morning brief.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- morning-brief
- morning brief
- connect my email for a morning brief
- set up morning brief
- configure morning brief
- connect mail for morning brief
- connect calendar for morning brief
- set up my morning brief

## Required inputs
- mail and calendar MCP connection status
- OAuth/app-password availability; value through secure entry or user-side setup only

## Expected outputs
- read-only diagnosis of the current mail/calendar MCP connection state
- diff-approved MCP config write scoped to read and draft-only access
- an on-demand morning brief once connection is verified

## Artifact expectations
- connection verification note when the wrapper captures it

## Acceptance criteria
- If a prerequisite is unmet, mark that item "not applicable" and continue with the rest of the guide instead of blocking or guessing.
- Success is applicable-only: verification passes when every applicable item is confirmed complete, not when every possible item exists.
- The connection is confirmed read and draft-only, with Send permission never enabled, before the brief is reported ready.

## Handoff policy
Run diagnosis and guidance directly in Hermes for the mail/calendar connection. Diagnosis reads non-secret metadata only; no writes. Show redacted placeholders in the config or `.env` diff; apply only after the user explicitly approves. Never ask the user to paste secrets into chat. Use Hermes-native secure entry or user-side OAuth/token setup; if unavailable, stop credential application and guide user-side setup. Use only a user-authorized credential store or local configuration; disclose destination and scope first. Keep secrets out of chat, previews, logs and evidence. Do not promise chat or platform non-retention. Delegate to a selected coding executor only if the user needs a change outside chat-driven MCP config edits.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: hermes-setup-gated
- source owner: skills/omh-morning-brief/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-morning-brief/SKILL.md`
- SHA256: `6f1b4f5ae68e7e6514749f9d8bf83d3d94be78e5ead056a68809de2ab0e9e603`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- blocked until supplied or observed: mail and calendar MCP connection status
- blocked until supplied or observed: OAuth/app-password availability; value through secure entry or user-side setup only
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
