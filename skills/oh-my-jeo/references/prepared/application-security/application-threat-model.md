# Prepared guidance: application-threat-model

Family: `application-security`<br>
Category: `review`<br>
Phase: `application-threat-model`<br>
Role: `reviewer`

## Contract
[omh] Attack paths into an operated system: turn a system's components and data flows into assets, trust boundaries, attack scenarios, controls, and the security test that proves each control holds. Use when the user says: application-threat-model, application threat model, threat model, threat modeling, threat modelling, threat modeling session, threat modeling workshop, security threat model.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- application-threat-model
- application threat model
- threat model
- threat modeling
- threat modelling
- threat modeling session
- threat modeling workshop
- security threat model
- build a threat model
- model the threats
- threat scenarios
- stride analysis
- stride model
- trust boundary
- trust boundaries
- attack scenario
- attack scenarios
- attack tree
- attack trees
- abuse case
- abuse cases
- security design review
- security architecture review
- architecture security review
- how would an attacker
- how could an attacker
- what could an attacker do
- attacker perspective

## Required inputs
- the system under review: components, which component calls which, and where each is deployed
- data flows and data classes: what every store, queue, and message carries
- known trust boundaries: authentication points, network edges, tenant separation, third parties
- controls already deployed, and who owns each
- scope exclusions and the threat actors in scope

## Expected outputs
- application_threat_model/v1
- asset register: data class plus the one loss that makes each asset worth defending
- trust boundaries: what crosses, what authenticates the crossing, what the receiver assumes unchecked
- attack scenarios: entry point, path, precondition, impact
- one decision per scenario (mitigate, transfer, accept, eliminate) with an owner
- per-control security test naming the observable that fails without it, plus residual risk

## Artifact expectations
- application_threat_model/v1 with asset register, trust boundaries, attack scenarios, control decisions, and per-control tests
- every control marked deployed, planned, or unverified; a scenario with no boundary and no asset is dropped, never carried

## Acceptance criteria
- Every asset carries a data class and one named loss; every boundary names what crosses it and what authenticates the crossing.
- Every scenario resolves to mitigate, transfer, accept, or eliminate, with an owner.
- Every mitigating control carries a security test and the observable that fails without it.
- Controls read deployed, planned, or `unverified`; none is inferred from the architecture description.
- Residual risk is listed, and the model is not offered as a scan, a penetration test, or an attestation.

## Handoff policy
Keep the model in Hermes: assets, boundaries, scenarios, control decisions, and test definitions are analysis over architecture the user supplies. Writing the tests, running a scanner, changing an IAM policy, or patching a component is executor work and needs observed evidence before a control counts as deployed.

## Catalog rules
- quality_tier: security-safety-gated
- contract_source: skills/omh-application-threat-model/SKILL.md:70
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Run all six STRIDE prompts from `omh-application-threat-model/references/threat-model-method.md` per boundary; drop an unreachable scenario with its reason instead of carrying it.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-application-threat-model/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-application-threat-model/SKILL.md`
- SHA256: `8a83d2a32f275d5cc4919977bbe2affbc29b5e6df7bdde087799ff2b2f6bde29`

## Method references
- `omh-application-threat-model/references/threat-model-method.md` (pinned `skills/omh-application-threat-model/references/threat-model-method.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: the system under review: components, which component calls which, and where each is deployed
- Required source input: data flows and data classes: what every store, queue, and message carries
- Required source input: known trust boundaries: authentication points, network edges, tenant separation, third parties
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for application-threat-model: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
