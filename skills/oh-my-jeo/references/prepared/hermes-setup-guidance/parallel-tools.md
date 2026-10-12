# Prepared guidance: parallel-tools

Family: `hermes-setup-guidance`<br>
Category: `hermes-setup`<br>
Phase: `setup`<br>
Role: `guide`

## Contract
[omh] Parallel tool-call capability in doubt: check version currency and parallel-tool capability status, then apply an update only after diff approval. Use when the user says: parallel-tools, parallel tools, hermes parallel tools setup, update hermes for parallel tools, check parallel tool support, enable parallel tool calls, verify parallel tools capability, check hermes version for parallel tools.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- parallel-tools
- parallel tools
- hermes parallel tools setup
- update hermes for parallel tools
- check parallel tool support
- enable parallel tool calls
- verify parallel tools capability
- check hermes version for parallel tools

## Required inputs
- installed Hermes version
- current parallel-tool capability status

## Expected outputs
- read-only diagnosis of the installed version and parallel-tool capability status
- a user-runnable update command to check or restore version currency
- a capability status report naming which parallel-tool features are active

## Artifact expectations
- capability status note when the wrapper captures it

## Acceptance criteria
- If a prerequisite is unmet, mark that item "not applicable" and continue with the rest of the guide instead of blocking or guessing.
- Success is applicable-only: verification passes when every applicable item is confirmed complete, not when every possible item exists.
- The reported capability status matches an observed read, not an assumed default.

## Handoff policy
Run diagnosis and reporting directly in Hermes for parallel-tool capability. Diagnosis reads non-secret metadata only; no writes. Show redacted placeholders in the config or `.env` diff; apply only after the user explicitly approves. Never ask the user to paste secrets into chat. Use Hermes-native secure entry or user-side OAuth/token setup; if unavailable, stop credential application and guide user-side setup. Use only a user-authorized credential store or local configuration; disclose destination and scope first. Keep secrets out of chat, previews, logs and evidence. Do not promise chat or platform non-retention. Delegate to a selected coding executor only if the user needs a change outside a local version/config check.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: hermes-setup-gated
- source owner: skills/omh-parallel-tools/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-parallel-tools/SKILL.md`
- SHA256: `aec5623baa178ca98657617c42a83d2fdbc2da32b22323fce7f59e5c164a398e`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- blocked until supplied or observed: installed Hermes version
- blocked until supplied or observed: current parallel-tool capability status
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
