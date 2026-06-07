# Flywheel primer

[Flywheel](https://docs.flywheel.paradigma.inc) is "infrastructure for
autonomous research workflows": a durable graph of research **nodes** that is the
system of record for a campaign. This repo's research is recorded as a Flywheel
graph. This is a distilled, working primer — enough to author and grow the graph
without re-reading the full docs. When in doubt, `flywheel help <command>` and
the `flywheel-*` skills are authoritative.

## Node model

A node is intentionally minimal:

- `title` — short label.
- `content` — markdown body (the substance).
- `summary` — optional one-paragraph abstract used in tree/summary renders.
- `repo_context` — optional pointer to repo/commit/paths the node is about.
  **It must be present in every commit payload even if all its fields are null.**

There are **no typed `kind`/`hypothesis` fields**. *Insight vs. empirical is a
usage convention, not a schema field:*

- **Insight nodes** hold design, rationale, plans, decisions, conclusions.
- **Empirical nodes** hold an experiment run + its **artifacts** (the data).

Nodes form a **DAG**: edges are parent→child; a node may have **multiple
parents** (e.g. a komi result that is a child of both the "komi" question node
and the "board size" question node). Each node has a stable `node_id` (UUID) and
a human-friendly `slug` (e.g. `lively-bush-4140`); `nodes:resolve-slug` maps one
to the other.

## CLI essentials

API-key/CLI mode. Global flags: `--format=json|tsv|csv|table`, `--out=<path|->`,
`--env=<profile>`. Payloads can be inline JSON or `@path/to/file.json` — prefer
`@file` for anything non-trivial.

### Create a node (one shot)

```bash
flywheel nodes:commit-new --payload_json=@node.json
```

`nodes:commit-new` creates **and** commits in one request. The payload carries
`title`, `content`, optional `summary`, `repo_context` (present even if null),
and the parent edge(s). Use `flywheel help nodes:commit-new` / `--schema` for the
exact shape. (`nodes:create` makes a title-only stub if you want to fill it in
later.)

### Edit an existing node (optimistic locking)

Editing is a lease + commit cycle:

```bash
flywheel nodes:get --node_id <id>                  # read current state + revision
flywheel nodes:stage:lease:acquire \
    --node_id <id> \
    --stage_session_id <your-session-id> \
    --base_committed_revision <rev>                 # acquire edit lease
flywheel nodes:commit --node_id <id> --payload_json=@edit.json   # commit (carries expected_revision)
flywheel nodes:stage:lease:release --node_id <id> --stage_session_id <your-session-id>
```

Concurrent edits are guarded by **optimistic locking** on the revision number —
if someone else committed since you read, your commit is rejected and you re-read
and retry. `nodes:stage:lease:heartbeat` keeps a long edit alive.

### Attach artifacts (the data behind an empirical node)

```bash
flywheel artifacts:upload \
    --node_id <id> \
    --expected_revision <rev> \
    --items='[{"local_path":"experiments/komi3.json","artifact_type":"json","title":"komi sweep 3^3"}]'
```

One-shot upload = prepare + PUT + finalize. Each item needs `local_path` and an
`artifact_type`, one of: **`text`, `table`, `json`, `image`, `banner`, `html`,
`plotly_html`, `vega`, `checkpoint`, `binary`, `diff_carousel`**. Optional per
item: `media_type`, `title`, `execution_id`, `note`, `metadata`. (Lower-level
`artifacts:upload:prepare` / `:finalize` exist if you need them.)

### Multi-parent edges

```bash
flywheel nodes:add-parent --node_id <child> --parent_id <parent> \
    --expected_revision <childRev> --expected_parent_revision <parentRev>
```

`nodes:remove-parent` detaches. Use multi-parent when a result answers more than
one question.

### Inspect the graph

```bash
flywheel nodes:render:tree --node_id <root> [--projection topology] [--max_depth N]
flywheel graph:get                     # graph projection for navigation/topology
flywheel nodes:children --node_id <id> # page direct children
flywheel nodes:parents  --node_id <id> # page direct parents
flywheel export:summary --node_id <root>   # markdown summary export
```

The `flywheel-tree` skill renders DAGs as readable terminal trees.

## Rate limits

- **120 node creates / minute**, **2000 / day**.
- **120 graph writes / minute** (commits, edges, etc.).

On HTTP 429, honor the `Retry-After` header and back off. Batch where you can.

## The design brief + design gate

Before launching a non-trivial probe, write a **design brief** as an insight
node and run it through the **design gate** — a checkpoint that forces the
experiment to be well-posed before any compute is spent. A complete brief
answers ~10 fields:

1. **Objective** — the question this probe answers (tie to a THESIS.md Q).
2. **Hypothesis** — what you expect and why (you may be wrong; that's fine).
3. **Method** — exactly what will run (script, board size, agents, games).
4. **Decision criterion** — the threshold/observation that resolves it
   (e.g. "win-rate CI excludes 50%", "crossing within ±0.5").
5. **Metrics** — what you measure (win-rate, margin, draw rate, games/sec…).
6. **Baselines / controls** — what you compare against.
7. **Budget** — compute posture and cost ceiling (for this campaign: **$0 /
   local-only**, see BOOTSTRAP.md).
8. **Reproducibility** — seeds, `OUT=` artifact path, exact command.
9. **Risks / confounds** — what could make the result misleading.
10. **Outcome & next step** — filled in after the run: what happened, what it
    implies, what to do next.

The **design gate** is the go/no-go on that brief: it must be coherent and
runnable, the decision criterion must actually be decidable from the planned
metrics, and the budget must be respected — *before* you launch. Only then
expand the frontier and execute.

## The specialized `flywheel-*` skills

Invoke these as skills (not shell commands) for graph-native workflows:

- **`flywheel`** — general guidance: experiment design, MCP/tool-contract
  questions, setup/troubleshooting.
- **`flywheel-auto`** — advance a frontier **autonomously** under an explicit
  budget: persist control state, execute branches, replan after each resolution.
  This is the engine of the autonomous run (see BOOTSTRAP.md step 4).
- **`flywheel-lookahead`** — planning-only `n`/`k` lookahead: author option
  nodes at each hop and select one continuation chain, no execution.
- **`flywheel-reproduce`** — graphify claim-bearing source and validate it
  empirically within a hard budget.
- **`flywheel-to-graph`** — port source material into nodes/artifacts/edges, no
  execution.
- **`flywheel-tree`** — render DAGs as terminal trees.
- **`flywheel-prove`** / **`flywheel-llm-proof-paper`** — Lean proving / paper
  reference sanity-checking (not used by this campaign).

## Auth note

This environment runs the CLI in **API-key mode** (`flywheel auth:status` to
confirm). Some `account:*` / `account:merge` / email / billing commands require
a **browser session** and are unavailable with an API key — that's expected; the
node/graph/artifact/compute commands you need for research all work in CLI mode.
