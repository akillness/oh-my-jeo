# Prepared guidance: capability-toggle

Family: `capability-policy`  
Category: `operator`  
Phase: `configuration`  
Role: `tracker`

## Contract
[omh] Tailoring enabled OMH families: turning one OMH capability family on or off so an install can be tailored instead of taken whole. Use when the user says: capability-toggle, capability policy, disable memory, enable memory, disable coding orchestration, disable a capability family, enable a capability family, 메모리 기능 꺼줘.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- capability-toggle
- capability policy
- disable memory
- enable memory
- disable coding orchestration
- disable a capability family
- enable a capability family
- 메모리 기능 꺼줘
- 메모리 기능 끄기
- 메모리 기능 켜줘
- 메모리 비활성화
- 메모리 관리 비활성화
- 코딩 오케스트레이션 비활성화
- 코딩 오케스트레이션 꺼줘
- 기능 비활성화
- 기능 활성화

## Required inputs
- capability family
- requested state

## Expected outputs
- policy change summary
- what was removed versus retained
- the exact command that reverses it

## Artifact expectations
- capability policy recorded in the local setup profile

## Acceptance criteria
- The affected family is named by its canonical id, not guessed from a partial word.
- Removed workflows and retained core skills are listed separately.
- The reversing command is stated so the change never reads as permanent.
- Locally modified skill files are reported as retained exceptions rather than deleted.

## Handoff policy
Read and write the local capability policy directly; propose executor work only when a repository fix is required.

## Catalog rules
- quality_tier: evidence-gated
- contract_source: skills/omh-capability-toggle/SKILL.md:66
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-capability-toggle/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-capability-toggle/SKILL.md`
- SHA256: `90f8a45a6ca1393f792eb0d2a2e39f0284077a3532d9922f99631b9f59f38d7a`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- Required source input: capability family
- Required source input: requested state
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for capability-toggle: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
