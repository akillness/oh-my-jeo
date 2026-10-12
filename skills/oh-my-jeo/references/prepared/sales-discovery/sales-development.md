# Prepared guidance: sales-development

Family: `sales-discovery`  
Category: `strategy`  
Phase: `sales-development`  
Role: `operator`

## Contract
[omh] Prospect or account worth pursuing: turn an account or market opportunity into a focused discovery, qualification, and next-step brief. Use when the user says: sales discovery, account plan, outbound messaging, 영업 발굴, 고객사 계획, 아웃바운드 메시지.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- sales discovery
- account plan
- outbound messaging
- 영업 발굴
- 고객사 계획
- 아웃바운드 메시지

## Required inputs
- account or segment
- available evidence
- buyer hypothesis
- sales objective

## Expected outputs
- sales_opportunity_evidence_record/v1
- sales_qualification_state/v1
- sales_draft_sequence/v1
- sales_handoff_disposition/v1

## Artifact expectations
- prepared sales development brief when a wrapper captures it

## Acceptance criteria
- The decision, options, tradeoffs, assumptions, and rejected alternatives are named.
- Observed signals are separated from strategic inference.
- Accepted decisions and implementation follow-ups are not conflated.

## Handoff policy
Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. Hermes prepares research, discovery, and message guidance; it does not research unobserved facts as facts, contact prospects, create opportunities, change CRM data, book meetings, or claim revenue or progress.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: decision-gated
- source owner: skills/omh-sales-development/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-sales-development/SKILL.md`
- SHA256: `7f6c72f1d9e7b5e4ecefb0aca6899c7439f0929994af734dfda9d2c149157f96`

## Method references
- `omh-sales-development/references/procedure.md` (pinned `skills/omh-sales-development/references/procedure.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: account or segment
- blocked until supplied or observed: available evidence
- blocked until supplied or observed: buyer hypothesis
- blocked until supplied or observed: sales objective
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
