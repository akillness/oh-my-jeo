# Prepared guidance: buzz

Family: `hermes-setup-guidance`<br>
Category: `operator`<br>
Phase: `messaging-integration`<br>
Role: `tracker`

## Contract
[omh] Buzz community agent setup or relay trouble: connect and operate Hermes as a native Buzz community agent, deliver local media with verified relay receipts, or diagnose a self-hosted Buzz relay without inventing transport evidence. Aliases: omh-buzz. Use when the user says: connect Hermes to Buzz, Buzz community agent, Buzz gateway setup, Buzz media attachment, Buzz relay self-hosting, Buzz connection diagnostics, 버즈 커뮤니티 연결, Buzz 메시지 첨부.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- connect Hermes to Buzz
- Buzz community agent
- Buzz gateway setup
- Buzz media attachment
- Buzz relay self-hosting
- Buzz connection diagnostics
- 버즈 커뮤니티 연결
- Buzz 메시지 첨부

## Required inputs
- Buzz task: gateway setup, media delivery, or self-host diagnosis
- target Hermes home or active Buzz conversation
- observable stop condition

## Expected outputs
- selected Buzz workflow lane
- bounded setup or diagnostic evidence
- observed delivery stage or explicit unobserved boundary

## Artifact expectations
- redacted Buzz readiness summary when setup is inspected
- delivery receipt with accepted event id when media is sent
- self-host failure-tree evidence when relay health is diagnosed

## Acceptance criteria
- Exactly one of setup, media, or self-host is selected from request meaning; no internal lane is public.
- Secrets remain out of argv, logs, rendered output, and workflow artifacts.
- Configuration, process, relay, event acceptance, subscription, and client rendering are separate claims.
- Any state-changing self-host command remains user-driven and has an explicit rollback or backup boundary.
- The final answer names what was observed, what remains unobserved, and the next smallest proof action.

## Handoff policy
Operate through Hermes' native Buzz adapter and official Buzz surfaces. Keep state-changing self-host commands user-driven and delegate repository code changes only when the user explicitly asks for them.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: evidence-gated
- source owner: skills/omh-buzz/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-buzz/SKILL.md`
- SHA256: `fffc268347d6af81912b08f9c27561a63fb96217a804086b705a0b33952b8c77`

## Method references
- `buzz/omh-buzz/references/media.md` (pinned `skills/omh-buzz/references/media.md`)
- `buzz/omh-buzz/references/self-host.md` (pinned `skills/omh-buzz/references/self-host.md`)
- `buzz/omh-buzz/references/setup.md` (pinned `skills/omh-buzz/references/setup.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: Buzz task: gateway setup, media delivery, or self-host diagnosis
- blocked until supplied or observed: target Hermes home or active Buzz conversation
- blocked until supplied or observed: observable stop condition
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
