# Prepared guidance: security-event-response

Family: `application-security`  
Category: `review`  
Phase: `security-event-response`  
Role: `reviewer`

## Contract
[omh] Security event on the code already shipped -- a CVE in a dependency, a secret committed to the repo, a license question, an advisory: triage reachability and severity, contain in order, and never close a leaked secret before its rotation is observed. Use when the user says: security-event-response, security event response, cve, triage this cve, cve in our dependency, cve in a dependency, security advisory, dependabot alert.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- security-event-response
- security event response
- cve
- triage this cve
- cve in our dependency
- cve in a dependency
- security advisory
- dependabot alert
- dependabot security
- vulnerable dependency
- vulnerability in our dependency
- reachability analysis
- npm audit
- committed a secret
- committed an api key
- leaked secret
- leaked a secret
- leaked credential
- leaked api key
- leaked an api key
- leaked aws key
- leaked an aws key
- secret in git history
- secret in the history
- dependency license
- dependency's license
- license ok
- license compatibility
- license compatible
- gpl dependency
- agpl dependency

## Required inputs
- the event kind: CVE or advisory, leaked secret, license question, or an advisory that forces a major version
- for a CVE: the advisory id, the affected package and version range, and the installed version from the lockfile
- for a leaked secret: the credential type and scope, where it was pushed, whether the repository is public, and when
- for a license: the package, its declared license, and how the product is distributed
- observed evidence for any containment or closure claim

## Expected outputs
- security_event_record/v1
- reachability_analysis/v1 when a vulnerable dependency is involved
- containment_plan/v1
- license_fit_verdict/v1 when a license is asked
- event_closure_verdict/v1

## Artifact expectations
- security_event_record/v1 names the event kind, the source, the affected package or credential class, and the exposure window, separately from the suspected impact
- reachability_analysis/v1 names the vulnerable function or path, the repository call sites that reach it or the observed absence of any, and a severity call from the advisory score adjusted by that reachability
- containment_plan/v1 orders every step; for a leaked secret the rotation and the observed rejection of the old credential come before any history rewrite, because a rewrite does not un-publish a secret already cloned
- license_fit_verdict/v1 gives the SPDX id, the obligation it triggers for this distribution model, and fits, conflicts, or needs counsel
- event_closure_verdict/v1 reads closed only when the rotation or the fixed version is recorded observed; a prepared step keeps the event open and is named

## Acceptance criteria
- The event kind, source, and exposure window are stated.
- Every severity call cites the reachable path or its observed absence.
- A leaked secret's rotation precedes any history rewrite in the plan.
- The closure verdict is closed only when the rotation or fixed version is observed.
- No secret value appears anywhere, and OMH scanned, contacted, or rotated nothing.

## Handoff policy
Keep the event record, the reachability call, the ordered containment plan, and the closure verdict in Hermes. Scanner output, advisory text, registry metadata, rotations, revocations, and history rewrites are recorded only from executor, operator, or wrapper observed output; OMH never scans, contacts a registry, or rotates a credential.

## Catalog rules
- quality_tier: event-closure-gated
- contract_source: skills/omh-security-event-response/SKILL.md:73
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Load `references/event-containment-order.md` for the per-event containment order, the severity adjustment, and the license obligation table instead of recalling them.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-security-event-response/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-security-event-response/SKILL.md`
- SHA256: `3364c8da9f0f3267d95d0d171479ada6efbd8dc9d13f90f4c21d4e651852d1a6`

## Method references
- `omh-security-event-response/references/event-containment-order.md` (pinned `skills/omh-security-event-response/references/event-containment-order.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: the event kind: CVE or advisory, leaked secret, license question, or an advisory that forces a major version
- Required source input: for a CVE: the advisory id, the affected package and version range, and the installed version from the lockfile
- Required source input: for a leaked secret: the credential type and scope, where it was pushed, whether the repository is public, and when
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for security-event-response: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
