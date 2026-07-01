# Project Memory

OMJ project memory is a local, reviewed long-term context layer for a single
project. It stores typed summaries under `.omj/memory/` and can attach compact
recall packs to coding handoffs.

It is not Hermes global memory. OMJ does not read, patch, or mutate opaque
Hermes internal memory.

## What It Stores

Project memory uses deterministic JSON files:

- `.omj/memory/candidates/*.json` for captured candidates awaiting review.
- `.omj/memory/records/*.json` for approved reviewed records.
- `.omj/memory/reviews/*.json` for approve/reject decisions.
- `.omj/memory/index.json` for local file inventory.

Generated `.omj/` files are local-only and ignored by default.

Approved records can be typed as:

- `fact`
- `decision`
- `lesson`
- `procedure`
- `episode`
- `failed_attempt`

Records include TTL and staleness metadata. `episode` records default to a
short TTL. Other records default to staleness review metadata so recall can
skip stale context unless an operator explicitly includes it.

## Failure-First Recall

OMJ project memory prioritizes what did **not** work. A `failed_attempt` record
captures one dead end — the exact approach that stalled or failed plus its
cause — so a later task avoids repeating it. When a recall query actually
matches a `failed_attempt`, that record is surfaced **ahead of every other
record**, even ones with a higher raw keyword-overlap score. The intent is to
close capability gaps rather than only reinforce known strengths: resurfacing a
relevant dead end is higher-leverage than restating what already works.

The failure boost is gated on a genuine query hit (real token/tag overlap). An
empty query or a query that does not match the dead end never lets an unrelated
`failed_attempt` crowd out relevant context, and each recall item carries a
`failure_first` boolean so a handoff can see why it was ordered first.

Capture a dead end deterministically (no LLM) as a bounded, review-gated
summary:

```sh
omj memory record-failure "ran the router regex over the whole file with finditer" \
  --cause "the scanner matches line-by-line so the whole-file scan missed the hit"
```

`record-failure` still honors the memory policy: under `review-first` the dead
end waits for approval before it can be recalled; under `auto-safe` a bounded,
non-sensitive summary is auto-approved. It never persists raw logs or
transcripts — only a redacted, metadata-only summary.

## Policy

`omj setup` records a `project_memory_policy/v1` object in
`.omj/setup-profile.json`.

Modes:

- `review-first`: default. Capture candidates, require review before recall.
- `auto-safe`: auto-approve candidates that pass local safety checks; keep
  risky items in review.
- `off`: disable automatic capture and recall.

Example:

```sh
omj setup --memory-mode review-first
omj setup --memory-mode auto-safe
omj setup --memory-mode off
```

Setup only records OMJ-local policy. It does not mutate Hermes memory.

## CLI Flow

Capture a candidate:

```sh
omj memory capture --type procedure --tag tests "Run unittest discovery after workflow contract changes"
```

Review pending candidates:

```sh
omj memory review
```

Approve or reject:

```sh
omj memory approve cand_1234 --approved-by user
omj memory reject cand_1234 --reason "temporary task progress"
```

Recall reviewed memory for a task:

```sh
omj memory recall --executor codex "workflow docs verification"
```

Status:

```sh
omj memory status
```

Every review and recall payload says it is prepared memory context only. It is
not execution, review, CI, merge, or Hermes internal-memory evidence.

## Safety Rules

Capture never persists raw `--content` or stdin text. It stores hashes, lengths,
typed summaries, and review metadata.

The local safety classifier blocks or requires review for:

- credential-like text
- raw logs and tracebacks
- full transcripts
- short-lived PR or commit identifiers
- temporary task progress
- unusually long raw content

Blocked candidates cannot be approved directly. Recapture them as a safe,
bounded summary or reject them.

## Handoff Behavior

When memory recall is enabled and reviewed records match a coding task, OMJ
adds `memory_recall_pack/v1` to prepared coding handoffs. This applies to:

- `omj coding delegate`
- `omj coding lifecycle start`
- `omj chat interact --mode delegate`
- wrapper-session handoff preparation

Persisted lifecycle records keep only a compact recall summary. They do not
persist raw recalled summaries in status cards.

Recall packs are prepared context. They can help the selected coding owner —
Codex, Claude Code, Hermes runtime/handoff paths, or a generic executor — start
with known project facts, decisions, lessons, or procedures, but they do not
prove that any executor ran or that review/CI/merge happened.

## Future Backends

The v1 policy names `local_json` as the current backend and leaves an extension
seam for optional backends. Mem0, Graphiti, Cognee, Letta, or another memory
system could be added later as optional adapters only if dependency, privacy,
and packaging boundaries are explicit.
