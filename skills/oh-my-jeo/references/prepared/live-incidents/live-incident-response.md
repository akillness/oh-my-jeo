# Prepared guidance: live-incident-response

Family: `live-incidents`<br>
Category: `reliability`<br>
Phase: `live-incident-command`<br>
Role: `operator`

## Contract
[omh] Production is down or an incident is open: command an incident that is still open -- severity as declared live state, commander and roles, an append-only timeline, a recorded temporary mitigation, verified recovery, and the customer notice. Use when the user says: live-incident-response, live incident response, incident response, active incident, ongoing incident, open incident, incident open, incident commander.

This is a source-pinned, prepared-only contract. It is routing and handoff guidance, not provider, executor, dispatch, verification, review, CI, merge-readiness, or merge evidence.

## Triggers
- live-incident-response
- live incident response
- incident response
- active incident
- ongoing incident
- open incident
- incident open
- incident commander

## Required inputs
- what is broken right now, and the user-visible behavior that shows it
- blast radius: which customers, tenants, or regions, and since when
- who is available for commander, operations, communications, and scribe
- the signal that decides recovery, and the value that counts as healthy
- mitigation state so far: nothing tried, tried and failed, or in place

## Expected outputs
- live_incident_record/v1
- declared severity: the level, the observation that set it, and when it last changed
- role assignment naming a person per role, or recording the role unfilled
- append-only timeline: one entry per observation, action, or decision, each timestamped and attributed
- mitigation entries marked temporary or permanent, each with what removes it
- recovery verification: the signal, its healthy value, the observed value, and who observed it
- customer notice draft plus the prepared paging and status-page requests, kept apart from observed sends

## Artifact expectations
- live_incident_record/v1 with severity, roles, timeline, mitigations, recovery verification, and a communication ledger
- every communication entry reads prepared or observed and never both; a correction appends an entry and never edits one

## Acceptance criteria
- Severity is declared, carries the observation that set it, and every change appended rather than overwrote the previous level.
- One commander is named; operations, communications, and scribe each name a person or read unfilled.
- Every timeline entry is timestamped, attributed, and typed, and no earlier entry was edited.
- Each mitigation reads temporary or permanent, and a temporary one names what removes it.
- Recovery cites the named signal, its healthy value, the observed value, and the observer, never the mitigation alone.
- Paging, status-page, and customer-send entries read prepared unless a connector result was observed.

## Handoff policy
Keep severity, role assignment, the timeline, mitigation records, and recovery verification in Hermes. Paging, status-page updates, and customer sends are `connector-operator` requests recorded as observed only when the connector returns a result; rollbacks, code changes, and infrastructure operations are executor or operator work and reach the timeline as observations, never as claims.

## Catalog rules
- Route only on the source-defined description and triggers; do not treat nearest local contracts as aliases.
- Source routing exclusion: The incident is over and the request is the postmortem, the SLO or error-budget consequence, or remediation follow-up; use `reliability-review`.
- Source routing exclusion: The request is one customer's support case needing a reply, a severity opinion, and an escalation path, with no incident declared; use `support-operations`.
- Source routing exclusion: The request is a release being rolled out and watched -- deploy checklist, health signals, rollback criteria -- and nothing has been declared broken; use `deploy-and-monitor`.
- Source routing exclusion: The request is to send the page, publish the status-page update, or deliver the customer notice; use `connector-operator`, which records a send as observed only on a returned result.
- Source routing exclusion: The request asks whether a release is ready across rollout, rollback, and observability, before anything broke; use `production-audit`.
- Keep this canonical ID as prepared guidance because the local catalog marks it preparedGuidanceMissing.
- Do not claim provider, executor, runtime, mutation, or observed-result capability from this metadata alone.

## Pinned source
- Repository: `rlaope/oh-my-hermes`
- Commit: `117f67a2347b82ea527ca1d7f8c0e8d609ec8c4c`
- Source path: `skills/omh-live-incident-response/SKILL.md`
- SHA256: `0a912c1377e1897560692f79fc771e0ea61ce70a8928b2573a48c71c4187e1c9`

## Method references
- `omh-live-incident-response/references/incident-command-method.md` (pinned `skills/omh-live-incident-response/references/incident-command-method.md`)

## Source gaps
- None declared

## Blocked prerequisites
- The local catalog member live-incident-response is absent; nearest local contracts are explicitly non-equivalent.
- An explicit accepted handoff and matching observed provider, executor, or host evidence are required before execution claims.
- Native, provider, connector, or command surfaces remain upstream-only/not_observed until a selected executor or wrapper supplies observed evidence; this record does not provide OMJ execution.

## Evidence boundary
prepared_not_observed: this record is Hermes-facing prepared guidance only. Keep scope, routing, and preparation in Hermes; selected executor/runtime or provider actions require an explicit accepted handoff and observed evidence. No executor/provider/runtime execution, observed result, review, CI, deploy, or merge evidence is implied.
