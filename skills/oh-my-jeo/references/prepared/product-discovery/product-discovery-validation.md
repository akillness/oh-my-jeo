# Prepared guidance: product-discovery-validation

Family: `product-discovery`<br>
Category: `planning`<br>
Phase: `product-discovery-validation`<br>
Role: `planner`

## Contract
[omh] Unvalidated early product idea: test whether a customer problem, segment, and business hypothesis deserve product investment, ending in kill, pivot, persevere, or inconclusive before any PRD. Use when the user says: product-discovery-validation, product discovery validation, product discovery, customer discovery, customer discovery plan, zero to one validation, validate the problem before building, problem solution interview.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- product-discovery-validation
- product discovery validation
- product discovery
- customer discovery
- customer discovery plan
- zero to one validation
- validate the problem before building
- problem solution interview

## Required inputs
- problem hypothesis
- target segment
- known evidence and current alternatives
- decision owner
- learning budget and deadline
- success, failure, and stop criteria

## Expected outputs
- discovery_decision_frame/v1
- discovery_evidence_ledger/v1
- customer_discovery_plan/v1
- assumption_test_portfolio/v1
- discovery_decision_receipt/v1
- initial_gtm_hypothesis/v1

## Artifact expectations
- prepared discovery decision frame, evidence ledger, customer discovery plan, assumption test portfolio, decision receipt, and GTM hypothesis when a wrapper captures them

## Acceptance criteria
- Preserve workflow intent and stop conditions; load the full contract before claiming completion.
- Reply in the user's own words and the host's own voice: its SOUL.md persona owns reply language, tone, speech level, and sentence endings, progress updates included (where it sets no language, use the one the user wrote in), and OMH shapes structure and content only; OMH's record terms (surface, lane, wrapper, handoff, evidence boundary, not_observed) stay in records and tool calls, never in the sentence the user reads unless they ask about one; and when a stop condition or a decision the user owns ends the turn, offer the next action as a question rather than declaring what will not be done.
- Record observed delegation results; otherwise return `not_available` or `not_observed`.
- Use Hermes-native subagent/delegation features when available: native subagents -> Hermes delegation when available, otherwise sequential lanes.

## Handoff policy
Keep decision framing, evidence classification, assumption ranking, test precommitment, and the discovery decision in Hermes. A prepared plan, ledger, portfolio, or receipt is not participant recruitment, an interview, a survey, a payment, a prototype, a PRD, code, or a launch. Prepare a `product-brief` handoff only from a `persevere` receipt the decision owner accepted; route a single empirical prototype question to `decision-prototype`; reach `idea-to-deploy` only after the resulting product brief and plan are accepted.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-product-discovery-validation/SKILL.md`
- SHA256: `1ab833ce4b011d8dbdb17941fe1fc0b4e7c56d39e5aac399142e0bc000cf8ab1`

## Method references
- `omh-product-discovery-validation/references/full-contract.md` (pinned `skills/omh-product-discovery-validation/references/full-contract.md`)
- `omh-product-discovery-validation/references/procedure.md` (pinned `skills/omh-product-discovery-validation/references/procedure.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member product-discovery-validation is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
