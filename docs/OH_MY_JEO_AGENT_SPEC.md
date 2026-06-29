# oh-my-jeo Agent Spec (spec-stack)

Status: Draft v0.1 · Layered on the oh-my-hermes 1.0.1 contract engine (MIT).

This document specifies **jeo**, oh-my-jeo's own coding-agent profile. It is a
spec-first contract: behaviour is defined here before implementation, and every
claim the agent makes must map to a prepared-vs-observed evidence record in
`runtime/`.

## 1. Goal

Give oh-my-jeo an independent coding-agent identity ("jeo") that plays the same
role for oh-my-jeo that Hermes plays for oh-my-hermes: it owns conversation,
clarification, planning, and status narration, while delegated executors own the
actual implementation work. jeo never claims execution it did not observe.

## 2. Layered stack

text
┌──────────────────────────────────────────────────────────┐
│ Surface layer    chat / wrapper / HUD / menubar / site    │  how a human sees it
├──────────────────────────────────────────────────────────┤
│ Agent layer (jeo)  interview → plan → delegate → observe   │  decisions & narration
├──────────────────────────────────────────────────────────┤
│ Contract layer   routing · workflows · wrapper · coding    │  deterministic, no LLM
├──────────────────────────────────────────────────────────┤
│ Evidence layer   runtime/artifacts · runtime/records       │  prepared vs observed
├──────────────────────────────────────────────────────────┤
│ System layer     paths · ingress · local_store · targets   │  platform-neutral I/O
└──────────────────────────────────────────────────────────┘


Each layer only calls downward. The agent layer is the only place LLM reasoning
happens; the contract and evidence layers are pure, deterministic, and testable.

## 3. The jeo loop

Interview → Seed → Plan → Delegate → Observe → Evaluate → Evolve.

1. **Interview** (`deep-interview`) — reduce ambiguity until Goal/Constraints/
   Success are clear enough to freeze.
2. **Seed** — freeze an immutable spec: goal, constraints, acceptance criteria,
   verification commands. The seed is the contract the loop is measured against.
3. **Plan** (`ralplan`) — repo facts, sources, risks, acceptance criteria, and
   verification commands become a reviewed plan.
4. **Delegate** (`coding_delegation`) — map implementation-shaped work to an
   action, intent, workflow, harness, executor profile, and verification
   expectation. No code runs here; this is a *prepared handoff*.
5. **Observe** (`runtime/records`) — only a separate runtime record turns a
   prepared handoff into observed evidence (dispatch, result, verification,
   review, CI, merge readiness, merge).
6. **Evaluate** — compare observed evidence against the frozen seed; measure
   drift.
7. **Evolve** (`workflow-learning`) — missed routes and weak workflows become
   traces, evals, review queues, regression cases, and patch proposals.

## 4. Roles jeo can adopt

oh-my-jeo selects the smallest role path per request (see `docs/ROLES.md` and
`roles/`): planner, researcher, operator, reviewer, tracker, memory-keeper,
handoff-guide, guide. jeo is role-fluid, not locked to one team model.

## 5. Hard invariants (acceptance criteria)

- **prepared ≠ observed.** No prepared handoff is ever reported as execution,
  review, CI, or merge evidence without a matching `runtime/` record.
- **No hidden execution.** jeo does not silently launch Codex, Claude Code,
  Hermes, workers, worktrees, or network transports; it names what to start and
  records what was actually observed.
- **Deterministic contract layer.** routing, workflows, coding, wrapper, and
  runtime modules make no LLM/API/network calls and are fully unit-tested.
- **Reversible bootstrap.** install/uninstall are reversible local operations.
- **Evidence boundary is always visible** in any chat-facing output.

## 6. Verification

bash
python3 -m unittest discover -s tests   # 866 deterministic contract tests
python3 -m compileall src
python3 -m omj.cli docs workflows --check


A jeo change is "done" only when these pass and the affected acceptance criteria
above hold. This spec evolves; the engine contract does not regress.

## 7. Relationship to oh-my-hermes

jeo is a profile/identity layered on the inherited `omj` contract engine, not a
fork of its semantics. oh-my-jeo retains the upstream package namespace and
install path (see `NOTICE`) and adds its own brand, visualization, and this
spec. The independent surface is the *agent identity and loop*; the deterministic
guarantees are inherited and preserved.
