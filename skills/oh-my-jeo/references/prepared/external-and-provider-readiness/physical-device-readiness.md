# Prepared guidance: physical-device-readiness

Family: `external-and-provider-readiness`  
Category: `operations`  
Phase: `device-readiness`  
Role: `operator`

## Contract
[omh] Agent control of a robot, 3D printer, or IoT relay: gate robots, 3D printers, IoT relays, sensors, and lab hardware before trials; use external-connector-readiness for provider or connector adoption and toolbelt-readiness for missing control tools. Use when the user says: physical-device-readiness, physical device readiness, device safety readiness, physical device safety, hardware safety gate, 3d printer readiness, 3D printer safety, snapmaker printer safety.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- physical-device-readiness
- physical device readiness
- device safety readiness
- physical device safety
- hardware safety gate
- 3d printer readiness
- 3D printer safety
- snapmaker printer safety

## Required inputs
- user request
- target context
- delivery or status expectation
- known missing evidence

## Expected outputs
- physical_device_readiness_card/v1
- device_safety_envelope/v1
- hazard_and_actuator_inventory/v1
- sensor_camera_gate_policy/v1
- operator_approval_policy/v1
- dry_run_and_simulation_policy/v1
- emergency_stop_and_rollback_plan/v1
- device_trial_manifest/v1 when observed
- next action
- prepared-vs-observed boundary

## Artifact expectations
- physical_device_readiness_card/v1 metadata-only wrapper card when prepared
- device_safety_envelope/v1 with device, workspace, hazards, actuator classes, human/property risk, owner, authority, and stop condition
- hazard_and_actuator_inventory/v1 separating motion, heat, pressure, electrical, relay, network, credential, and environmental risks
- sensor_camera_gate_policy/v1 for camera/OCR, sensor telemetry, stale readings, manual inspection, and blocked/no-camera fallback
- operator_approval_policy/v1 with explicit human authority, confirmation moment, disallowed autonomous actions, and emergency contact or stop owner
- dry_run_and_simulation_policy/v1 for slicer/G-code dry-runs, command previews, mock relays, simulated robot paths, and no-hardware trial mode
- emergency_stop_and_rollback_plan/v1 with stop command, power/network isolation, recovery boundary, and abort condition
- device_trial_manifest/v1 only when real telemetry, camera capture id, dry-run output, command transcript, operator confirmation, or hardware observation is recorded

## Acceptance criteria
- Device scope, actuator and hazard classes, sensor/camera gates, operator approval, dry-run policy, emergency stop, and stop condition are explicit.
- Physical actions, heat commands, relay toggles, robot movement, print starts, camera inspections, and telemetry readings are marked observed, missing, risky, or not_observed.
- Route external APIs or provider setup to external-connector-readiness, terminal commands to command-operator, safety concerns to security-safety-review, visual/camera checks to visual-qa, and missing tools to toolbelt-readiness.
- Do not claim device movement, heat, print, relay, robot, camera, sensor, or emergency-stop success without observed device-trial evidence.

## Handoff policy
Keep this as Hermes-facing orchestration guidance first. Prepare executor, connector, gateway, or host-runtime handoff only when the user accepts that next step and observed evidence can be recorded.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The request is already handled by a narrower explicit skill with stronger evidence.
- Source routing exclusion: The user asks OMH to secretly run external platforms, connectors, schedulers, file exports, or runtime agents.
- Source routing exclusion: The only safe answer is to ask for missing authority, credentials, target, or observed evidence first.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-physical-device-readiness/SKILL.md`
- SHA256: `44c42487019fb1b0a86cd29e4dbad485d8e29af603780bf0a9f3622a8be99dc0`

## Method references
- No source-specific method reference is declared; do not invent one.

## Source gaps
- The pinned upstream member declares no physical method reference; its SKILL.md source contract remains authoritative.

## Blocked prerequisites
- The local catalog member physical-device-readiness is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
