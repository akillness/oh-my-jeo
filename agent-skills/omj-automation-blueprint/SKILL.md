---
name: omj-automation-blueprint
description: [omj] Prepare recurring-operation blueprints with schedule, delivery, silence, context chain, and observed-only status; never activate scheduling implicitly.
metadata:
  omj:
    portability: requires-omj-cli
    category: operations
    phase: scheduled-ops-blueprint
---

# Automation Blueprint

Portability: `requires-omj-cli`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow requires an explicitly configured local `omj` CLI for its OMJ-specific ledger or inspection operations. Check command availability before using those operations; if unavailable, report the missing prerequisite, do not install anything, and keep that operation unsupported. CLI records prove only the observations they contain, not host execution.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`automation-blueprint` makes this workflow explicit: Prepare recurring-operation blueprints with schedule, delivery, silence, context chain, and observed-only status; never activate scheduling implicitly.

## Do Not Use When

- The user needs a one-off report or deck; use `report-package` or `materials-package`.
- The user asks to review incident metrics once; use `reliability-review`.
- The user needs actual code changes; prepare a selected executor/runtime handoff after the blueprint or plan is accepted.

## Examples

Good example:

- Prompt: automation-blueprint every weekday run an uptime check and send a Slack digest only if status changes.
- Expected behavior: Prepare an OMJ operations blueprint with schedule intent, delivery policy, silence, research/report guidance, missing evidence, and next confirmation.
- Why: The request is recurring, delivery-shaped, and must stay prepared until host automation and gateway delivery are observed.

Bad example:

- Prompt: automation-blueprint prove the Slack digest was delivered this morning.
- Expected behavior: Ask for observed delivery evidence or report delivery as not_observed.
- Why: A blueprint can prepare the scheduled operation, but it cannot prove runtime execution or delivery.

## Completion Checklist

- Confirm the workflow target, evidence boundary, and stop condition are named.
- Report which outputs are prepared, observed, blocked, or missing.
- Name the smallest next verification or handoff instead of claiming completion from narration.

## Recovery Notes

- If required context is missing, ask one blocking question or route back to the narrower workflow.
- If runtime or wrapper evidence is unavailable, keep the status as not_observed and expose the next observable action.

## Use When

Prepare recurring-operation blueprints with schedule, delivery, silence, context chain, and observed-only status; never activate scheduling implicitly.

Strong routing signals: `automation-blueprint`, `scheduled ops`, `scheduled operation`, `scheduled operations`, `automation blueprint`, `cron blueprint`, `cron-ready`, `recurring ops`, `recurring workflow`, `every morning`, `every day`, `daily digest`, `weekly digest`, `send to slack`, `send to discord`, `post to telegram`, `only if changed`, `silent if nothing changed`, `schedule this`, `매일`, `매주`, `정기`, `예약`, `반복`, `스케줄`, `슬랙`, `디스코드`, `텔레그램`, `보내`, `공유`, `변화 없으면`, `조용히`

## Catalog Metadata

Category: `operations`
Phase: `scheduled-ops-blueprint`
Host-owned workflow responsibility
Quality tier: `ops-blueprint-gated`

Quality bar:

- Name cadence/timezone uncertainty, delivery target, silence/no-change rule, selected skills, and context chain.
- Expose whether a no-agent watchdog is a candidate without claiming it exists or ran.
- List host automation, gateway delivery, source retrieval, and no-agent execution as not evidence until observed.

Handoff policy:

Prepare recurring-operation blueprints with schedule, delivery, silence, context chain, and observed-only status; never activate scheduling implicitly. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- recurring request
- schedule or cadence hint
- delivery target or current-thread default
- silence/no-change preference

Expected outputs:

- hermes_ops_blueprint/v1 projection
- schedule/delivery/silence confirmation needs
- status-card boundary
- not-evidence list

Artifact expectations:

- hermes_ops_blueprint/v1 under .omj/hermes-ops/blueprints when a wrapper or CLI records it

Safety rules:

- Do not claim scheduler activation, gateway delivery, retrieval, unattended execution, plugin loading, or connector work from a prepared blueprint.
- Keep scheduled operations as projection metadata until the host runtime supplies observed evidence.
- Route later coding, material generation, or report delivery into separate accepted handoffs when needed.

## Execution and Handoff Discipline

1. State the target, constraints, acceptance criteria, authority, and stop condition before work.
2. Planning and coordination do not take ownership of code implicitly. Keep the selected first-class coding owner explicit, including the current host when selected.
3. Read supporting references only when needed using available host file tools; loading guidance is not dispatch or plan acceptance.
4. Take acceptance only from the user's actual answer. A timeout, dismissal, or missing answer leaves the plan unaccepted; prepare no handoff and start nothing.
5. A selected owner, task card, plan, or prepared handoff stays `prepared_not_observed` until observed execution evidence exists. Preserve failures and unresolved criteria.
6. Verify behavior with the smallest relevant observed check. Current loader admission is not evidence of a live session; local fresh files do not prove host discovery, execution, review, CI, or merge.
7. Network operations, configuration or memory writes, external publishing, and new authority remain separately approval-gated. Do not activate unsupported services.

## Supporting Context

[Native and historical provenance](../omj/references/native-provenance.md)
