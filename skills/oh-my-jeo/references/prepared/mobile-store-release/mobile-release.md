# Prepared guidance: mobile-release

Family: `mobile-store-release`  
Category: `planning`  
Phase: `mobile-release`  
Role: `planner`

## Contract
[omh] Releasing an iOS or Android app through the stores -- signing, the privacy manifest, a TestFlight or Play beta, a staged rollout, a hotfix: prepare each gate the store enforces, and plan the halt and the next build before the rollout starts, because a store release cannot be rolled back. Use when the user says: mobile-release, mobile release, mobile app release, ios release, android release, app store release, app store submission, submit to the app store.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- mobile-release
- mobile release
- mobile app release
- ios release
- android release
- app store release
- app store submission
- submit to the app store
- app store review
- app store connect
- testflight
- play store
- play store release
- google play
- play console
- internal testing track
- closed testing track
- phased release
- code signing
- provisioning profile
- signing certificate
- distribution certificate
- android keystore
- upload keystore
- upload key
- play app signing
- privacy manifest
- privacyinfo.xcprivacy
- required reason api
- data safety form
- expedited review
- fastlane

## Required inputs
- the platforms, the app's bundle or package id, and the version and build number going out
- how signing is set up today: certificates, provisioning profiles, the keystore or upload key, and who holds them
- the SDKs the build ships, for the privacy manifest and the data safety form
- the beta channel and testers, and what they must verify before the rollout
- the crash-free and ANR figures the rollout will be judged on, observed from the consoles or crash reporting

## Expected outputs
- signing_plan/v1
- privacy_declaration_check/v1
- beta_channel_plan/v1
- staged_rollout_plan/v1
- hotfix_plan/v1

## Artifact expectations
- signing_plan/v1 names each certificate, provisioning profile, keystore, and upload key with its expiry and where it is held, and never contains the secret itself
- privacy_declaration_check/v1 compares the iOS privacy manifest's required-reason APIs and the Play data safety form against every SDK the build ships, and names each mismatch
- beta_channel_plan/v1 names the TestFlight group or Play testing track, whether it needs beta review, the testers, and the checks that must pass before the rollout
- staged_rollout_plan/v1 lists the rollout steps (App Store phased release or Play staged percentages) with the crash-free and ANR thresholds that halt each step
- hotfix_plan/v1 halts the bad rollout, names the higher build number that replaces it, whether to request an expedited review, and any server-side flag that contains the damage first

## Acceptance criteria
- Every signing asset is named with its expiry and holder, and no secret is in the plan.
- The privacy declarations match the shipped SDKs, or each mismatch is named.
- The beta channel, its testers, and its exit checks are stated.
- Every rollout step names the threshold that halts it.
- The hotfix build number and the halt are planned, and OMH submitted nothing.

## Handoff policy
Keep the signing plan, privacy declaration check, beta plan, staged rollout, and hotfix plan in Hermes. Build numbers, review outcomes, crash-free rates and rollout percentages are recorded only from store console, crash reporting, executor, or operator observed output; OMH never builds, signs, uploads, or submits a build.

## Catalog rules
- quality_tier: store-gate-halt-planned
- contract_source: skills/omh-mobile-release/SKILL.md:72
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Load `references/mobile-release-method.md` for the per-platform signing, privacy, beta, rollout and hotfix table instead of recalling store rules.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-mobile-release/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-mobile-release/SKILL.md`
- SHA256: `3aefffa78ef41fb8d0047a34ac8c372bd37814356f9b74efa9091e01e15819b7`

## Method references
- `omh-mobile-release/references/mobile-release-method.md` (pinned `skills/omh-mobile-release/references/mobile-release-method.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: the platforms, the app's bundle or package id, and the version and build number going out
- Required source input: how signing is set up today: certificates, provisioning profiles, the keystore or upload key, and who holds them
- Required source input: the SDKs the build ships, for the privacy manifest and the data safety form
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for mobile-release: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
