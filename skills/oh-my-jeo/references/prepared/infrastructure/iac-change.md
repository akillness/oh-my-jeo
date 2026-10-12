# Prepared guidance: iac-change

Family: `infrastructure`<br>
Category: `planning`<br>
Phase: `iac-change`<br>
Role: `planner`

## Contract
[omh] Infrastructure-as-code change -- Terraform, OpenTofu, Pulumi, a Kubernetes manifest, a Helm chart: read the drift, the blast radius and the cost delta from the saved plan, then stage the apply behind a health gate with a rollback per stage. Use when the user says: iac-change, iac change, infrastructure as code, infrastructure-as-code, terraform plan, terraform apply, terraform state, terraform drift.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- iac-change
- iac change
- infrastructure as code
- infrastructure-as-code
- terraform plan
- terraform apply
- terraform state
- terraform drift
- terraform module
- terraform change
- opentofu
- tofu plan
- pulumi
- pulumi preview
- pulumi up
- cloudformation
- cloudformation change set
- helm upgrade
- helm diff
- helm chart
- helm chart change
- kubectl apply
- kubectl diff
- kustomize
- kubernetes manifest
- kubernetes manifests
- k8s manifest
- k8s manifests
- infracost
- drift detection
- cost delta
- staged apply
- stage the apply

## Required inputs
- the tool and the unit of change: the Terraform workspace or stack, the cluster and namespace, or the Helm release
- the environments the change reaches, in promotion order
- the observed plan or diff output for the change, saved to a file where the tool allows it
- the health signal each environment already exposes: rollout status, probes, error rate, or a smoke check
- observed output for any drift, apply, health, or rollback claim

## Expected outputs
- drift_assessment/v1
- blast_radius/v1
- cost_delta/v1
- staged_apply_plan/v1
- health_gate/v1
- rollback_plan/v1

## Artifact expectations
- drift_assessment/v1 separates drift already present between state and the running infrastructure from the change being proposed, from a refresh-only plan or a live diff, and names who resolves each drifted resource before the apply
- blast_radius/v1 lists every resource the saved plan creates, updates in place, replaces, or destroys, calls out each replacement or destroy of a stateful resource, and names what depends on it
- cost_delta/v1 gives the monthly delta from an observed estimate for the saved plan, or marks the delta unestimated and names the resources that drive it
- staged_apply_plan/v1 orders the stages from the least to the most exposed environment and applies the reviewed saved plan, never a fresh one
- health_gate/v1 names, per stage, the observed signal that promotes it -- rollout status, a follow-up plan with no changes, an error rate -- and the value that stops it
- rollback_plan/v1 names, per stage, the command or revert that undoes it and what cannot be undone, such as a destroyed volume or a rotated resource id

## Acceptance criteria
- Existing drift is separated from the proposed change.
- Every replacement or destroy is listed, and each stateful one waits for explicit approval.
- The cost delta is observed or marked unestimated.
- Every stage names its health gate and its rollback.
- OMH ran nothing, and every fact cites observed output or is marked unverified.

## Handoff policy
Keep the drift assessment, blast radius, cost delta, staged apply plan, health gates and rollbacks in Hermes. Plan output, diffs, apply results, rollout status and cost estimates are recorded only from executor, operator, or wrapper observed output; OMH never runs terraform, tofu, pulumi, kubectl or helm, and any apply is the operator's.

## Catalog rules
- quality_tier: staged-apply-gated
- contract_source: skills/omh-iac-change/SKILL.md:72
- Workflow Lane: - Shared product, routing, compatibility, and evidence rules: `omh-routing/references/skill-common-rail.md`.
- Catalog Metadata: - Load `references/iac-change-method.md` for the per-tool drift, plan, health and rollback commands and the replacement markers instead of recalling them.
- Runtime Evidence: Shared product, compatibility, topology, memory, harness, and execution rules: `omh-routing/references/skill-common-rail.md`. Load it when applicable; otherwise name an unavailable capability.
- source_reference_text_source: skills/omh-iac-change/SKILL.md

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-iac-change/SKILL.md`
- SHA256: `19e48fac2583ed8131bc1eb3ebe77bd225846583038379380a46b57e31d4a057`

## Method references
- `omh-iac-change/references/iac-change-method.md` (pinned `skills/omh-iac-change/references/iac-change-method.md`)

## Source gaps
- None declared

## Blocked prerequisites
- Required source input: the tool and the unit of change: the Terraform workspace or stack, the cluster and namespace, or the Helm release
- Required source input: the environments the change reaches, in promotion order
- Required source input: the observed plan or diff output for the change, saved to a file where the tool allows it
- Explicit owner selection and fresh observed evidence are required before any external, executor, connector, or runtime handoff.

## Evidence boundary
prepared_not_observed for iac-change: Hermes may prepare the source-backed contract, but implementation, provider/connector/runtime execution, verification, review, CI, deployment, and merge evidence remain not_observed; no network, dependency, or native execution engine is invoked.
