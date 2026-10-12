---
name: omj
description: [omj] Conservatively route explicit requests to reviewed workflows; ask when intent conflicts.
metadata:
  omj:
    portability: portable
    category: router
    phase: routing
---

# Oh My Jeo

Portability: `portable`. This is host-neutral guidance, not a native plugin, persona replacement, or runtime hook.

## Host and Dependency Boundary

This workflow uses the selected host's existing tools; the OMJ CLI is not required to follow its guidance. Optional OMJ metadata persistence is a separately configured operation, never an implicit dependency.

The host owns tools, skill discovery, permissions, project trust, duplicate resolution, and delegation. Use only capabilities the host actually exposes. Missing tools require an explicit fallback or unresolved prerequisite, never hidden execution or permission bypass.

## Why This Exists

`oh-my-jeo` makes this workflow explicit: Conservatively route explicit requests to reviewed workflows; ask when intent conflicts.

## Do Not Use When

- The user already invoked a more specific installed skill and its routing signals are unambiguous.
- The message is ordinary chat, status acknowledgement, or a question that does not need workflow routing.
- The wrapper wants to claim execution, review, CI, or merge evidence that no observed artifact provides.

## Examples

Good example:

- Prompt: Use OMJ request-to-handoff for: safely add a feature to this repo.
- Expected behavior: Classify the request, name the selected workflow or prepared coding handoff, and expose the observed/prepared evidence boundary.
- Why: The user asks for OMJ-shaped routing without naming a narrow workflow, so the router should choose the safest next surface.

Bad example:

- Prompt: omj
- Expected behavior: Show the workflow picker or ask what the user wants to do next; do not infer a coding workflow.
- Why: A bare product name is a picker or clarification signal, not implementation evidence.

## Completion Checklist

- The selected workflow, confidence reason, evidence boundary, and user-facing next action are named.
- Low-confidence or conflicting signals return a picker or clarification instead of forced routing.
- Catalog answers are rendered without shell approval when wrapper metadata is sufficient.

## Recovery Notes

- If routing signals conflict, show the compact picker or ask one clarifying question.
- If wrapper metadata is unavailable, keep the recommendation advisory and avoid runtime claims.

## Use When

Conservatively route explicit requests to reviewed workflows; ask when intent conflicts.

Strong routing signals: `oh-my-jeo`, `oh my jeo`, `omj`, `./`, `/`, `./o`, `/o`, `./om`, `/om`, `./omj`, `/omj`, `./skills`, `/skills`, `skill picker`, `workflow picker`, `native command`, `command preview`, `route hint`, `route-hint`, `route hint card`, `fallback card`, `discord command`, `slack command`, `telegram command`, `skill routing`, `workflow routing`, `chat routing`, `request-to-handoff`, `plain request`, `role-owned next action`, `wrapper contract`, `prepared observed`, `evidence boundary`, `상태 기록`, `증거 경계`

## Catalog Metadata

Category: `router`
Phase: `routing`
Host-owned workflow responsibility
Quality tier: `routing-gated`

Quality bar:

- Route only from explicit invocation, strong catalog evidence, or a clear workflow-shaped request.
- Return a clarification or fallback path instead of forcing low-confidence messages into a workflow.
- Keep users command-agnostic by naming the next UX step rather than shell commands.
- Expose direct workflow selection without renaming skills or adding an `omj-` prefix to every skill name.
- Use request-to-handoff as the first path when a plain request needs role, plan, handoff, or status UX.

Handoff policy:

Conservatively route explicit requests to reviewed workflows; ask when intent conflicts. Keep planning, coordination, and implementation ownership explicit. Prepare a selected coding-owner handoff only for accepted code work. External effects and memory/configuration writes require their own approval; prepared artifacts are not execution evidence.

Required inputs:

- user request
- installed skill descriptions
- host-provided installed skill descriptions

Expected outputs:

- selected workflow guidance
- chat_route_hint/v1 when a wrapper needs a lightweight preview
- clarification question when routing is ambiguous

Artifact expectations:

- runtime run record when a wrapper can observe request handling

Safety rules:

- Prefer explicit skill invocation over weak keyword inference.
- Treat partial `./`, `/`, `./o`, or `/om` input as command preview; show one top-level `omj` entry before opening the workflow picker.
- Use `omj chat route-hint` when a wrapper needs a metadata-only workflow preview without plugin load or shell catalog approval.
- Host command/menu registration and rendering remain host-owned; selecting guidance does not prove registration or execution.
- Treat bare `./omj`, `/omj`, `./skills`, or `/skills` as a workflow picker request, not as implementation intent.
- Ask one concise question when routing signals conflict.
- Do not override the host's routing or trust policy.

## Execution and Handoff Discipline

1. State the target, constraints, acceptance criteria, authority, and stop condition before work.
2. Planning and coordination do not take ownership of code implicitly. Keep the selected first-class coding owner explicit, including the current host when selected.
3. Read supporting references only when needed using available host file tools; loading guidance is not dispatch or plan acceptance.
4. Take acceptance only from the user's actual answer. A timeout, dismissal, or missing answer leaves the plan unaccepted; prepare no handoff and start nothing.
5. A selected owner, task card, plan, or prepared handoff stays `prepared_not_observed` until observed execution evidence exists. Preserve failures and unresolved criteria.
6. Verify behavior with the smallest relevant observed check. Current loader admission is not evidence of a live session; local fresh files do not prove host discovery, execution, review, CI, or merge.
7. Network operations, configuration or memory writes, external publishing, and new authority remain separately approval-gated. Do not activate unsupported services.

## Supporting Context

[Reviewed workflow inventory](references/portable-workflows.md)
[Native and historical provenance](references/native-provenance.md)
