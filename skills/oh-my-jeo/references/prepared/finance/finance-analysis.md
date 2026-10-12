# Prepared guidance: finance-analysis

Family: `finance`  
Category: `operations`  
Phase: `finance-analysis`  
Role: `operator`

## Contract
[omh] Company budget overrun, cash risk, or close issue: turn finance and accounting inputs into a decision-ready variance, cash, and close-risk brief. Use when the user says: finance analysis, budget variance, budget vs actual, month-end close, 재무 분석, 예산 대비 실적, 월마감.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- finance-analysis
- finance analysis
- budget variance
- budget vs actual
- month-end close
- 재무 분석
- 예산 대비 실적
- 월마감

## Required inputs
- period
- supplied finance source
- decision question
- calculation assumptions

## Expected outputs
- finance_scope_source_record/v1
- finance_reconciliation_analysis_schedule/v1
- finance_risk_register/v1
- finance_decision_brief/v1

## Artifact expectations
- prepared finance analysis brief when a wrapper captures it

## Acceptance criteria
- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Handoff policy
Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. Calculations are only as authoritative as supplied or observed sources and methods; no ERP, bank, ledger, tax, payment, or filing action is implied.

## Catalog rules
- Source routing exclusion: The request is for a current quote, exchange rate, crypto price, or other live market lookup; use `live-info-operator`.
- Source routing exclusion: The user wants generic exploration of a supplied CSV or table without accounting periods, controls, or finance decision framing; use `data-analysis`.
- Source routing exclusion: The user asks to post journal entries, reconcile accounts, approve payments, submit tax filings, or configure an accounting system; use `connector-operator` for an explicit observed action path.
- Source routing exclusion: The user wants pipeline coverage, deal health, or a seller forecast scenario rather than authoritative revenue or close reporting; use `sales-pipeline-review`.
- Source routing exclusion: The user needs an enterprise or product direction decision after analysis; route that decision to `strategy-brief`.
- Source routing exclusion: The ask is testing whether an internal control operated -- a SOX or ICFR sample, re-performance, or a deficiency's severity; use `internal-audit`.
- Route only on the source-defined description and triggers; do not treat nearest local contracts ops-review, report-package as aliases.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-finance-analysis/SKILL.md`
- SHA256: `a0263ea7e99e71e903e4c7997497854d02cadad3060f826bed1e4eb95cba89d9`

## Method references
- `omh-finance-analysis/references/procedure.md` (pinned `skills/omh-finance-analysis/references/procedure.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member finance-analysis is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep domain framing, clarification, source/evidence synthesis, draft outputs, and next-work routing in Hermes. A prepared brief, review, reply, or plan is not an external action, approval, filing, send, publish, data mutation, implementation, review, CI, or merge claim. Prepare a connector, file, coding, or human-review handoff only when the user explicitly accepts that next step; report it only from observed evidence. Calculations are only as authoritative as supplied or observed sources and methods; no ERP, bank, ledger, tax, payment, or filing action is implied. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
