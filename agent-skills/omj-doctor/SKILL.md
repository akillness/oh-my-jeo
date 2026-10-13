---
name: omj-doctor
description: [omj] Inspect OMJ command, managed files, explicitly selected native registration, and runtime readiness as separate evidence boundaries.
metadata:
  omj:
    portability: requires-omj-cli
    category: operator
    phase: diagnostics
---

# Doctor

Portability: `requires-omj-cli`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow requires an explicitly configured local `omj` CLI for its OMJ-specific ledger or inspection operations. Check command availability before using those operations; if unavailable, report the missing prerequisite, do not install anything, and keep that operation unsupported. CLI records prove only the observations they contain, not host execution.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`doctor` makes this workflow explicit: Inspect OMJ command, managed files, explicitly selected native registration, and runtime readiness as separate evidence boundaries.

## Do Not Use When

- The user is asking for a general product explanation rather than local health diagnostics.
- The requested change is a repository bug fix, not an installed-environment check.
- The wrapper wants to claim host reload, skill execution, or plugin behavior that was not observed.

## Examples

Good example:

- Prompt: doctor after omj update says setup is next but managed skills still look stale.
- Expected behavior: Inspect managed files, explicitly selected native registration, runtime readiness, and the next authorized repair with explicit proof boundaries.
- Why: The issue is local installation health and needs grouped diagnostic evidence.

Bad example:

- Prompt: doctor implement a new uninstall command UX.
- Expected behavior: Route to planning or implementation instead of health diagnostics.
- Why: That is product development work, not a local health check.

## Completion Checklist

- Command availability, managed files, explicitly selected native registration, runtime state, and optional surfaces are grouped separately.
- Blocking issues and warnings are separated, with one next repair action named for each blocking area.
- Plugin installation, import/register smoke, current loader admission, and live session loading are separate claims.
- The final status says whether setup/update/doctor repaired anything or only observed health.

## Recovery Notes

- If managed skills are stale, recommend omj update or omj setup depending on whether registration also needs repair.
- If explicitly selected native registration is missing, report it and request authorized setup repair; never edit hidden runtime state.
- If plugin register smoke fails, reinstall the plugin bundle with setup --with-plugin --force before claiming plugin readiness.
- If omj is missing from PATH, use the installer-reported absolute command path and then re-run doctor.

## Use When

Inspect OMJ command, managed files, explicitly selected native registration, and runtime readiness as separate evidence boundaries.

Strong routing signals: `doctor`, `$doctor`, `diagnose omj`, `installation health`

## Catalog Metadata

Category: `operator`
Phase: `diagnostics`
Host-owned workflow responsibility
Quality tier: `evidence-gated`

Quality bar:

- Name the workflow target, constraints, validation evidence, and stop condition.
- Separate workflow guidance from executor or wrapper behavior unless evidence proves the step happened.

Handoff policy:

Run directly as local health inspection; propose executor work only when a repo fix is required.

Required inputs:

- omj home
- explicitly selected native source home, only when its inspection is requested
- observed issue

Expected outputs:

- health checks
- fix guidance
- known proof boundary

Artifact expectations:

- doctor state summary when runtime artifacts are writable

Safety rules:

- Do not imply hidden host or executor runtime behavior.
- Use the smallest verification that can prove the claim.

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
