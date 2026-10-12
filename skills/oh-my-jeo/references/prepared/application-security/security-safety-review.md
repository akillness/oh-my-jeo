# Prepared guidance: security-safety-review

Family: `application-security`<br>
Category: `review`<br>
Phase: `security-safety-review`<br>
Role: `reviewer`

## Contract
[omh] Agent or automation safety risks: review prompt, tool, secret, dependency, destructive-action, and explicit local plugin risks before agent or code execution. Use when the user says: security-safety-review, security safety review, ai coding safety, agent safety review, prompt injection review, tool permission review, secret exposure review, destructive action review.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- security-safety-review
- security safety review
- ai coding safety
- agent safety review
- prompt injection review
- tool permission review
- secret exposure review
- destructive action review
- supply chain safety
- sandbox safety
- plugin risk audit
- Hermes plugin audit
- local plugin guard
- key rotation
- secret rotation
- credential rotation
- certificate rotation
- rotate the api key
- rotate this api key
- rotate the credentials
- revoke the old key
- 보안 안전 검토
- 에이전트 안전
- 프롬프트 인젝션
- 시크릿 노출
- 파괴적 명령

## Required inputs
- target workflow, code change, prompt, tool, dependency, or release surface
- available evidence: diff, config, package metadata, command plan, or runtime permissions
- risk tolerance and allowed actions
- known secrets, credentials, external services, or destructive operations to avoid

## Expected outputs
- security_safety_review_plan/v1
- threat_surface_map/v1
- permission_and_secret_risk_matrix/v1
- prompt_injection_risk_review/v1
- safe_action_policy/v1
- plugin_risk_audit/v1 for one explicitly named local plugin directory
- remediation_handoff/v1 when needed
- credential_rotation_sequence/v1 when a live credential must be replaced
- not-evidence boundary

## Artifact expectations
- threat_surface_map/v1 with prompts, tools, files, dependencies, credentials, network, destructive actions, and external services
- permission_and_secret_risk_matrix/v1 with redacted findings, allowed actions, missing evidence, and escalation gates
- prompt_injection_risk_review/v1 with untrusted input boundaries and tool-use constraints
- safe_action_policy/v1 with allowed, confirmation-gated, blocked, and observed-only actions
- plugin_risk_audit/v1 with bounded aggregate local risk categories and no source disclosure
- credential_rotation_sequence/v1 attached to remediation_handoff/v1, ordering issue-new, deploy-new, verify-new, revoke-old, verify-revoked, with the overlap window and the operator who runs each step
- Artifact contracts:
- This label denotes the machine-enforcement level, not a skill quality score and not an observed evidence state.
- contract_id: `security_safety_review_plan/v1`; enforcement_level: `guidance_only`; consumer_id: `none`

## Acceptance criteria
- Findings or no-issue results are grounded in concrete file, artifact, command, or source evidence.
- Open questions, residual risk, and missing verification are named.
- Fixes or follow-up work are separate handoffs unless the user explicitly asked to implement them.

## Handoff policy
Keep safety review in Hermes. Scans, dependency updates, sandbox changes, credential checks, external security tools, and code fixes require explicit observed executor or operator evidence.

## Catalog rules
- quality_tier: security-safety-gated
- contract_source: skills/omh-security-safety-review/SKILL.md:66
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Order a credential replacement issue-new, deploy-new, verify-new, revoke-old, verify-revoked, and name what breaks if the order changes; revocation is proven by a call that fails with the old credential, never by the revoke command's exit status, which reports that the request was accepted. Load `references/credential-rotation.md` for the overlap window and the per-credential-type steps.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-security-safety-review/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-security-safety-review/SKILL.md`
- SHA256: `30a68dafe7cafd75bd9032dd065a46da88944d6b611b7e75c2db3b66f31c2b1a`

## Method references
- `omh-security-safety-review/references/credential-rotation.md` (pinned `skills/omh-security-safety-review/references/credential-rotation.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: target workflow, code change, prompt, tool, dependency, or release surface
- Required source input: available evidence: diff, config, package metadata, command plan, or runtime permissions
- Required source input: risk tolerance and allowed actions
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for security-safety-review: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
