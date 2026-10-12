# Prepared guidance: internal-audit

Family: `internal-controls`<br>
Category: `review`<br>
Phase: `internal-audit`<br>
Role: `reviewer`

## Contract
[omh] Testing an internal control -- SOX, ICFR or ITGC: define the population and the sample, name the evidence that proves each item, re-perform the control, and grade any deficiency from stated likelihood, magnitude and compensating-control criteria, never by assertion. Use when the user says: internal-audit, internal audit, internal control, internal controls, internal control audit, control testing, test of controls, tests of controls.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- internal-audit
- internal audit
- internal control
- internal controls
- internal control audit
- control testing
- test of controls
- tests of controls

## Required inputs
- the control: its objective, owner, frequency, and the risk or assertion it addresses
- the population it operates over: the period, the source system, and how completeness was checked
- the firm's or team's sampling guidance, or the confidence and tolerable deviation rate to use
- the materiality threshold and the compensating controls that exist
- the evidence each sample item actually produced, as observed documents, logs, or approvals

## Expected outputs
- control_under_test/v1
- sample_design/v1
- evidence_request/v1
- reperformance_record/v1
- deficiency_severity_grade/v1

## Artifact expectations
- control_under_test/v1 names the control's objective, owner, frequency, and risk, and the population with its period, source, and completeness check
- sample_design/v1 states the sampling method and derives the sample size from the control's frequency and the stated confidence and tolerable deviation rate, with a selection record that lets someone draw the same items again
- evidence_request/v1 names, per sample item, the document, log, or approval that proves the control operated and who provides it, and separates evidence obtained from evidence described
- reperformance_record/v1 records, per sample item, the independent re-performance of the control and its result -- operated, deviation, or not testable -- with the evidence reference
- deficiency_severity_grade/v1 derives control deficiency, significant deficiency, or material weakness from stated likelihood, magnitude against stated materiality, and compensating controls, shows each criterion's value and source, and withholds the grade when a criterion is missing

## Acceptance criteria
- The control, its population, and the completeness check are stated.
- The sample size is derived from stated frequency, confidence, and tolerable rate, and the selection can be redrawn.
- Each sample item names the evidence obtained, not described.
- Each item's re-performance result cites its evidence.
- The severity grade shows every criterion, or is withheld with the missing one named, and OMH signed off nothing.

## Handoff policy
Keep the control definition, sample design, evidence requests, re-performance record, and severity grade in Hermes. Populations, sample items, evidence, and re-performance results are recorded only from auditor, control owner, or operator observed output; OMH never queries a ledger or system of record and never signs off a control.

## Catalog rules
- classification: preparedGuidanceMissing
- quality_tier: criteria-derived-severity
- source owner: skills/omh-internal-audit/SKILL.md
- Original upstream commands and authority remain upstream-only/not_observed; OMJ must not invent command substitutions or provider/execution claims.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-internal-audit/SKILL.md`
- SHA256: `7964b9b5c72d96eafef71e148d7cbac97b7b47a358a019ddd09abc4296cc3fe2`

## Method references
- `internal-audit/omh-internal-audit/references/control-audit-method.md` (pinned `skills/omh-internal-audit/references/control-audit-method.md`)

## Source gaps
- None declared

## Blocked prerequisites
- blocked until supplied or observed: the control: its objective, owner, frequency, and the risk or assertion it addresses
- blocked until supplied or observed: the population it operates over: the period, the source system, and how completeness was checked
- blocked until supplied or observed: the firm's or team's sampling guidance, or the confidence and tolerable deviation rate to use
- blocked until supplied or observed: the materiality threshold and the compensating controls that exist
- blocked until supplied or observed: the evidence each sample item actually produced, as observed documents, logs, or approvals
- blocked for OMJ: upstream commands, connectors, providers, writes, and execution remain upstream-only/not_observed

## Evidence boundary
prepared_not_observed: this is deterministic Hermes guidance metadata only; no OMJ execution, network/API/LLM/native runtime, connector, provider, database, write, review, CI, merge, or observed-result claim is implied.
