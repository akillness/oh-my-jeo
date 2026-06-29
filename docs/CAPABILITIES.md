# OMJ Capability Manifests

OMJ capability manifests are runtime-readable maps for Hermes, plugin tools, and
wrapper backends. They answer one bounded question:

What can this installed OMJ surface prepare, explain, or observe, and what is
still not evidence?

The manifests are not a new source of truth. They are deterministic projections
over existing OMJ catalogs and contracts:

- skill metadata from `src/skills/catalog.py`
- situation playbooks from `src/catalogs/playbooks.py`
- role descriptors from `src/catalogs/roles.py`
- routing and locale policy from `src/routing/*`
- wrapper action ids from `src/wrapper/contract.py`
- runtime observation events from `src/runtime/records.py`
- plugin hook/tool metadata from `src/plugin_bundle/omj/*`
- optional MCP bridge metadata from `omj mcp manifest` and host recipes from
  `omj mcp config-recipe`

Use:

```sh
omj capabilities export --json
omj capabilities export --section keywords --json
omj capabilities summary --json
omj capabilities list
omj capabilities inspect ultragoal --json
omj capabilities inspect handoff-guide --section roles --json
omj capabilities inspect request-to-handoff --section playbooks --json
omj context brief "make an image card for this PR" --json
```

The Hermes plugin exposes the same contract through the metadata-only
`omj_capabilities` tool, exposes `omj_context` when Hermes needs the compact
OMJ mental model, generic-tool checkpoint, and optional message route hint in
one payload, exposes `omj_interact` when Hermes needs a renderable
`chat_interaction/v1` plus a metadata-only wrapper session record, exposes
`omj_recommend` when Hermes only needs route hints, and exposes `omj_probe`
when Hermes needs local setup/runtime status or a capability roadmap without
asking the user to approve a shell command.
Use `action=summary` when Hermes needs to answer "what can OMJ do?" or render a
small workflow picker/card without asking the user to approve a shell catalog
command.
Friendly section aliases such as `roles`, `agents`, `patterns`, `tools`, and
`evidence` are accepted as input; JSON responses keep the canonical section
names shown below.

The summary also includes `capability_families`, the user-facing front door for
normal chat surfaces:

| Family | What Hermes should show first |
| --- | --- |
| Plan and decide | Clarify goals, prepare plans, and make loop or decision paths explicit. |
| Learn and gather | Find sources, explain papers, triage signals, and prepare source-backed briefs. |
| Create materials and visuals | Shape files, reports, packages, and image-card prompts before generation is claimed. |
| Delegate coding and ship | Prepare scoped handoffs for Codex, Claude Code, Hermes, or another runtime after scope is clear. |
| Operate and observe | Show setup health, automation, workflow learning, memory review, status, and repair next steps. |

Capability families are the public, user-facing front door. The older lanes and
groups remain in the manifest as compatibility context for wrappers, tests, and
existing plugin surfaces; they should not be introduced to normal users before
the family layer.

## Sections

| Section | Purpose |
| --- | --- |
| `agent_roles` | Responsibility roles such as research, planning, review, and coding handoff. They are descriptors, not runtime agents. |
| `skills` | Skill capabilities, triggers, harnesses, quality bars, handoff policy, and orchestration eligibility derived from the generated skill catalog. |
| `hooks` | Plugin tools/hooks plus wrapper event contracts and whether each surface is only supported or actually observed. |
| `keywords` | Explicit invocation prefixes, natural-language routing rules, locale aliases, conflict policy, and guard rules. |
| `orchestration_patterns` | Safe workflow patterns such as clarify-then-plan, plan-execute-verify, team pipeline, worktree isolation, loop tick, and executor session handoff. |
| `playbooks` | Situation-level workflow maps such as request-to-handoff, feedback triage, research department, materials processing, and idea-to-deploy, including owner/action hints for the first wrapper card. |
| `tool_requirements` | Tool/MCP requirements when derivable, plus setup guidance for the optional allowlisted OMJ MCP bridge. |
| `evidence_boundaries` | The shared prepared-vs-observed claim rule. |

## Claim Boundary

Capability presence means OMJ can prepare guidance, status, or a handoff. It
does not mean Hermes loaded a plugin, a worker ran, code changed, review passed,
CI passed, or a PR was merged.

Those claims require matching local wrapper or runtime artifacts such as
`runtime_observation/v1`.

Workspace-isolation guidance uses `worktree_session_isolation/v1`. It can tell a
wrapper to keep the same workspace, recommend a worktree, or require a worktree
before opening a coding agent. It is still prepared guidance until a wrapper or
operator invokes or observes the workspace action. `omj worktree prepare` is the
explicit opt-in backend that can create a local Git worktree and record
`omj_worktree_observation/v1`. `omj worktree bind` can then return
`worktree_executor_binding/v1` so a wrapper can show open/attach/record actions
for the selected coding agent. Those records prove workspace isolation and
session-start guidance only, not executor dispatch, implementation, review, CI,
or merge.

The optional MCP bridge uses `omj mcp serve` and exposes only `omj_status`,
`omj_recommend`, and `omj_probe`. `omj_probe` can include the parity matrix and
capability roadmap when the host asks for them. `omj mcp config-recipe --host
claude-code|codex|opencode|cursor|generic` can print copy-paste snippets for
common MCP-capable hosts, but bridge availability and host config text are not
host-load evidence. A host or wrapper that actually observes bridge load or use
can record `omj_mcp_host_session/v1` with `omj mcp observe-host`; that remains
session evidence only.

The managed plugin bridge has the same split. Local install/import/register
smoke proves the bundle is present and importable, including tools such as
`omj_interact`, `omj_context`, `omj_recommend`, `omj_capabilities`,
`omj_probe`, `omj_hud`, and `omj_status`.
`omj_probe` can return the same capability roadmap shape as `omj probe
--roadmap`; in standalone plugin-bundle mode it returns a degraded roadmap that
only uses local files and metadata. Host or wrapper evidence that Hermes
actually loaded or used the plugin is recorded separately with
`omj plugin observe-host`, or self-recorded by an invoked plugin tool/hook when
the host passes bounded `observation` metadata, as
`omj_plugin_host_observation/v1`. Active readiness requires the latest observed
event to be `plugin_load`, `tool_call`, `hook_call`, or `status_query`;
`blocked`, `session_end`, and `plugin_unload` do not make the native bridge
active.

## Why This Exists

Hermes and wrapper surfaces should not need to scrape README prose to know which
skills exist, which actions are safe, or why a route was selected. The capability
manifest gives them a compact local contract while preserving OMJ's direction:
Hermes remains the chat surface, selected executors own implementation, and OMJ
keeps the evidence boundary visible.
