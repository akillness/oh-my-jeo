# oh-my-jeo

<p align="center">
  <img src="assets/oh-my-jeo-architecture.svg" alt="oh-my-jeo architecture and workflow map" width="920">
</p>

<p align="center">
  <strong>Install once. Keep your agent chat. Let oh-my-jeo make the next step safe.</strong>
  <br>
  <em>Chat-first workflow skills, deterministic contracts, status cards, and delegated coding handoffs for Hermes-style agents.</em>
</p>

<p align="center">
  <a href="https://github.com/akillness/oh-my-jeo"><img alt="GitHub" src="https://img.shields.io/badge/github-akillness%2Foh--my--jeo-181717?logo=github"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-blue">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

oh-my-jeo is a **spec-first workflow pack** for chat agents. The product is not
"more CLI commands" — the `omj` command (with the `omh` alias kept for backward
compatibility) is setup, repair, doctor, verifier,
and the wrapper/backend surface that turns a plain chat request into a
deterministic, reviewable contract. For normal users the experience stays in
chat; the command layer is a first-class backend for wrappers and routers,
without replacing your existing setup.

text
user says a plain request in chat
  -> oh-my-jeo routes it to the right skill / playbook / profile
  -> the agent explains the next action and the evidence boundary
  -> coding is handed off to the selected runtime only when accepted


oh-my-jeo adds a thin layer of ready-to-use workflows such as `web-research`, `doctor`, `idea-to-deploy`, `ultragoal`, `loop`, and `ultraprocess` so the agent feels easier to start, easier to trust, and more natural to apply in real work.

<p align="center">
  <img src="assets/hermes-agent-hero.png" alt="Hermes agent hero" width="720">
</p>

## Quick Start

```sh
curl -fsSL https://raw.githubusercontent.com/akillness/oh-my-jeo/main/install.sh | sh
omj setup
omj doctor
```

Hermes skill tap path:

```sh
hermes skills tap add rlaope/oh-my-hermes
hermes skills install rlaope/oh-my-hermes/skills/oh-my-hermes --yes
```

Then, from chat:

```text
Use OMJ request-to-handoff for: I want to safely add a feature to this repo.
```


> **Origin & attribution.** oh-my-jeo is an MIT-licensed derivative of
> [oh-my-hermes](https://github.com/rlaope/oh-my-hermes) by `@rlaope`. The
> engine and skill catalog are inherited verbatim. The `curl … | sh` installer
> and its source archive now resolve through the oh-my-jeo distribution
> (`akillness/oh-my-jeo`), so the canonical install path installs the `omj`
> command directly, while the Hermes skill tap and license attribution still
> point upstream
> ([website](https://rlaope.github.io/oh-my-hermes/)); see `NOTICE` for the full
> attribution. oh-my-jeo layers its own brand, documentation, visualization, and
> agent spec on top.

> **Why you still see `omh`.** `omj` (oh-my-jeo) is the canonical implementation
> namespace and Hermes plugin ABI. The Python import namespace still exposes both
> `omj` and `omh` (same objects), and chat accepts either "OMJ"/"oh-my-jeo" or
> "OMH"/"oh-my-hermes". The engine ships its ABI under the `omj` token — the
> bridge installs to `~/.hermes/plugins/omj`, advertises `omj_*` tools, and emits
> `omj_*` schema versions — so it stays loadable by an unmodified Hermes host;
> renaming the canonical `omj` ABI would break host interoperability, so it is
> kept stable on purpose. `omh` survives only as a thin backward-compatibility
> alias so legacy `import omh` call sites and host references keep resolving (see
> `.ouroboros/seeds/full-rename-seed.yaml`).


[Documentation](docs/README.md) -
[Installation](docs/INSTALLATION.md) -
[Capabilities](docs/CAPABILITIES.md) -
[Agent Install](INSTALL_FOR_AGENTS.md) -
[Roles](docs/ROLES.md) -
[Application Cases](docs/APPLICATION_CASES.md) -
[GitHub Pages site](site/index.html)

<br>

## Core Workflows

<p align="center">
  <img src="assets/omj-core-workflows.png" alt="Core workflows illustration" width="920">
</p>

The full skill catalog is larger; these representative modes are the ones to
understand first. The rest live in [Workflow Reference](docs/WORKFLOWS.md) and
[Capabilities](docs/CAPABILITIES.md). Workflows group into five surface lanes —
**Plan and decide**, **Learn and gather**, **Create materials and visuals**,
**Delegate coding and ship**, and **Operate and observe**.

- **Deep Interview** (`deep-interview`) — clarify the one missing decision
  before planning, when the request is still fuzzy.
- **Ralplan** (`ralplan`) — turn repo facts, sources, risks, acceptance
  criteria, and verification commands into a reviewed plan.
- **Ultragoal** (`ultragoal`) — keep an ambitious goal tied to checkpoints and
  completion gates instead of a one-shot answer.
- **Ultra Process** (`ultraprocess`) — run one delivery cycle: research →
  ralplan → implementation path → code review → docs/status sync.
- **Loop** (`loop`) — iterate through research, plan, handoff, and feedback when
  the right implementation must be discovered.
- **Web Research** (`web-research`) — gather current, source-backed evidence.
- **Paper Learning** (`paper-learning`) — explain a paper at easy, moderate, or
  expert level without dropping section coverage.
- **Source Finder** (`source-finder`) — prepare typed source candidates.
- **Idea To Deploy** (`idea-to-deploy`) — scope coding work for Codex, Claude
  Code, Hermes, or another runtime without claiming execution.
- **Workflow Learning** (`workflow-learning`) — turn missed routes into traces,
  evals, review queues, regression cases, and patch proposals.

<br>

## Project Structure

text
src/
  routing/      intent, policy, recommend, route_plan, chat        # what runs next
  workflows/    materials, paper_learning, research, visual, memory # value modes
  coding/       coding_delegation, executors, isolation, worktree   # delegated coding
  wrapper/      contract, lifecycle, sessions, route_hints          # chat envelopes
  runtime/      artifacts, records                                  # prepared vs observed
  system/       paths, ingress, local_store, targets                # platform-neutral I/O
  install/      installer, manifest, plugin_pack, config_adapter    # reversible bootstrap
  quality/      harness_quality, grounded_score, parity             # contracts & gates
  surfaces/     hud, menubar, demo, quickstart, context             # operator views
  plugin_bundle/omj/   plugin.yaml, hooks/, tools/                  # Hermes plugin payload
skills/         <skill>/SKILL.md                                    # tap-installable skill pack
docs/           architecture, workflows, roles, playbooks, parity   # contracts & guides
site/           static GitHub Pages marketing + docs                # no build step
tests/          50+ deterministic contract test modules             # the content gate


The package keeps a thin `omj.*` import shim over readable `src/<domain>/`
folders, so wheels install `omj.routing` while a source checkout reads
`src/routing/`. Domain command handlers live under `src/commands/`.

The jeo brand is a real import surface, not just a rename: `src/omj/`
installs an import hook so `import omj`, `from omj.routing import
recommend_skills`, and `from omj.commands.main import main` resolve to the
**same module objects** as their `omj.*` counterparts (object identity, no
forked runtime state). Both `omj` and `omj` console scripts target
`omj.cli:main`. This is the first stage of a deliberate, test-guarded
`omj` → `omj` migration; the `omj` namespace and the Hermes plugin contract
(`plugin_bundle/omj/`, `omj_*` tools) stay in place for compatibility until
later stages retire them behind shims. See `tests/test_omj_namespace.py`
for the executable identity proofs.

<br>

## Request Flow

oh-my-jeo keeps the flow simple and visible. The agent chooses the smallest role
path that fits the request instead of locking setup to one team model.

text
plain request
  -> choose workflow lane
  -> prepare plan, source brief, or handoff
  -> observe execution / review / CI only when evidence exists
  -> report the next action in chat


| Request shape | Typical flow |
| --- | --- |
| Quick answer or setup repair | Agent explains, oh-my-jeo checks local state, suggests the next command. |
| Research or product signal | Source finder / research / brief workflow before implementation. |
| Coding task | Scoped handoff to Codex, Claude Code, Hermes, or another chosen runtime. |
| Release or review question | Separate prepared claims from observed tests, review, CI, and merge evidence. |

<br>

## Evidence Boundaries

The defining contract: **prepared ≠ observed**. Plans, handoffs, dispatch,
results, verification, review, CI, and merge readiness stay visibly separate.
oh-my-jeo never turns a prepared handoff into execution proof — observed
evidence only exists once a separate runtime record is written under
`runtime/`. Project memory under `.omj/memory` is reviewed prepared context, not
execution evidence.

<br>

## Documentation

| Need | Read |
| --- | --- |
| Full docs map | [Documentation](docs/README.md) |
| Install, update, reapply, uninstall | [Installation](docs/INSTALLATION.md) |
| AI-agent pasteable install protocol | [Agent Install](INSTALL_FOR_AGENTS.md) |
| Product direction and boundaries | [Direction](docs/DIRECTION.md) |
| Architecture and module ownership | [Architecture](docs/ARCHITECTURE.md) |
| Capability manifests | [Capabilities](docs/CAPABILITIES.md) |
| Orchestration pattern contracts | [Orchestration Patterns](docs/ORCHESTRATION_PATTERNS.md) |
| Situation playbooks | [Playbooks](docs/PLAYBOOKS.md) |
| Role surfaces and profile packs | [Roles](docs/ROLES.md) |
| Representative workflows | [Application Cases](docs/APPLICATION_CASES.md) |
| oh-my-jeo agent spec (spec-stack) | [Agent Spec](docs/OH_MY_JEO_AGENT_SPEC.md) |

<br>

## Development

sh
python3 -m unittest discover -s tests
python3 -m compileall src
python3 -m omj.cli docs workflows --check


oh-my-jeo inherits oh-my-hermes 1.0.1, a quality-gated stable baseline, and is
distributed under the MIT License (see `LICENSE` and `NOTICE`).
