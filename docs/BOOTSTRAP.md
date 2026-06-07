# Bootstrap — first-agent startup sequence

You are the first autonomous agent on a fresh `a3go` repo. This document is your
startup runbook. It is **self-contained**: follow it top to bottom without
needing any prior conversation. Your job is to stand up a Flywheel research graph
and then run an autonomous, **$0 / local-only** research campaign on the 3D-Go
thesis until the frontier is exhausted.

Read first, in this order: [BOOTSTRAP.md](./BOOTSTRAP.md) (this) →
[THESIS.md](./THESIS.md) → [CODEBASE.md](./CODEBASE.md) →
[FLYWHEEL.md](./FLYWHEEL.md).

> **This is a blank slate.** The repo ships no prior findings on purpose. The
> thesis poses the questions *without* answers. Do not assume an outcome for any
> question (komi values, whether tactics survive, what the binding constraint is)
> — **derive every conclusion by running code** and record it in the graph.

## Step 1 — Validate the vendored slice

```bash
npm install
npm test                 # expect: 48/48 checks pass
npm run selfplay -- 6 30 # smoke: MCTS vs random, a few games — expect a summary table, no errors
```

Use **`tsx` / `npm run` only — never bare `node`** (the engine's TS enums +
extensionless imports require it; see CODEBASE.md). A clean `npm test` (48/48)
and a completed self-play summary on a small board (e.g. 3³) prove the engine
slice and tooling are wired correctly. If anything fails here, fix it before
proceeding — everything downstream rests on this.

Also confirm a clean tree before you start committing findings:

```bash
npm run checks           # eslint + prettier:check must pass
```

## Step 2 — Confirm Flywheel auth and set budget posture

```bash
flywheel auth:status
```

Establish the **budget posture explicitly and hold it for the whole run**:

- **Local-only, $0 managed compute.**
- **Do NOT** request compute grants, acquire compute leases, or create campaign
  budgets (no `compute:acquire`, `compute-grants:*`, `campaign-budgets:create`).
- If a question seems to *need* **managed/cloud** compute, that is a finding to
  report to the human, not a reason to spend.

### You have strong local compute — use it

"$0 / local-only" is about **not provisioning metered managed/cloud compute** —
it is **not** an instruction to ration this machine. The local box is powerful
and every cycle on it is free. Confirm it yourself, then exploit it:

```bash
nvidia-smi --query-gpu=name,memory.total --format=csv   # GPU
nproc; lscpu | grep "Model name"                        # CPU
free -h                                                  # RAM
```

At time of writing this box is an **NVIDIA RTX 5090 (32 GB VRAM, CUDA-capable)**,
an **AMD Ryzen 9 9950X (16 cores / 32 threads)**, and **~60 GB RAM**. Practical
consequences for the campaign:

- **Parallelize self-play.** The current runners are single-threaded (a property
  of the code, not the hardware). You have 32 threads — fan self-play games out
  across them (Node `worker_threads`, or just run several `tsx` processes with
  different seeds and aggregate). This can buy ~an order of magnitude in
  throughput before any algorithmic change, directly loosening the board-size /
  komi-precision questions (THESIS.md Q1, Q2).
- **The GPU is free and available** for the neural phase — local GPU training is
  $0, so that phase is *not* gated on a managed-compute budget (see
  `neural/README.md`). The NVIDIA driver is present; PyTorch isn't installed yet.

**Language/toolchain rule:** the TypeScript engine + self-play run on `tsx` and
are **CPU-only — they never touch the GPU**. Anything that needs the GPU (i.e.
the neural phase) is **Python, managed with [`uv`](https://docs.astral.sh/uv/)** —
`uv init` / `uv add` / `uv run`, not raw `pip`/`venv`/`conda`. Keep that Python
work in its own project under `neural/` (see `neural/README.md`).

So: be ambitious with local CPU (`tsx`, parallelized) and the GPU (`uv` + Python);
be disciplined about never reaching for managed/cloud compute.

## Step 3 — Build the campaign graph skeleton

Create the durable graph (see FLYWHEEL.md for the exact commands and payload
shapes). At minimum:

1. **Campaign root** — an *insight* node holding the thesis (from THESIS.md):
   the claim, the success bar, and the open questions Q1–Q5. This is the root of
   the whole campaign.
2. **Control node** — an *insight* node holding the **run contract** for the
   autonomous run. Capture, concretely:
   - **objective** — make progress on the 3D-Go thesis (Q1–Q5).
   - **decision criterion** — per-probe, how a question is considered resolved
     (e.g. a CI that excludes the null, a komi crossing pinned to ±0.5).
   - **start node** — where the frontier begins (the campaign root).
   - **budget** — **$0 / local-only** (from Step 2).
   - **lookahead `n`** — how many hops ahead to plan.
   - **frontier width `k`** — how many candidate branches to consider per hop.
   - **terminal condition** — stop when the frontier is exhausted (no positive-
     value probe remains within budget), then report to the human.
3. Optionally seed one child *question* node per open question (Q1–Q5) so the
   frontier has explicit branches to expand. You may also let `flywheel-auto`
   create these as it plans.

Record real `node_id`s as you go; later steps and replanning depend on them.

## Step 4 — Run the design gate, then go autonomous

1. Pick the first probe (a cheap, high-information question is a good opener —
   e.g. a baseline-strength or board-characterization probe on the smallest
   tractable board). Write its **design brief** as an insight node and run it
   through the **design gate** (FLYWHEEL.md): the brief must be coherent, the
   decision criterion decidable from the planned metrics, and the budget
   respected ($0/local) — *before* launching.

2. Launch the **autonomous run** with the **`flywheel-auto`** skill, under the
   control node from Step 3 and the **$0 / local-only** budget. It should:
   - expand the frontier (breadth `k`, lookahead `n`);
   - for each probe, run the relevant experiment via `tsx`
     (`src/selfplay/experiments/exp_*.ts`, writing data to `experiments/` via
     `OUT=`);
   - commit an **empirical node** per resolved probe with its **artifact(s)**
     attached (the result JSON, and a short text/table summary);
   - link results to every question they bear on (multi-parent);
   - **replan after each resolution** (new findings open or close branches);
   - record a `stop_reason` when it halts.

3. When the frontier is exhausted (terminal condition met), **stop and report to
   the human**: a summary of what was learned per question (Q1–Q5), the graph
   shape, the `stop_reason`, and the recommended next step — including whether
   anything is now blocked on something outside the $0/local budget (e.g. the
   deferred neural phase; see `neural/README.md`).

## Guardrails

- **Blank slate:** never paste a conclusion you didn't just derive from a run.
- **Budget:** $0 / local-only. No compute grants/leases. If you think you need
  them, report instead of spending.
- **Reproducibility:** every empirical node must be re-runnable — record the
  exact command, seeds, and the `OUT=` artifact path.
- **Vendored engine:** you own `src/engine` and may rewrite it (optimizing the
  hot path is fair game); log any divergence in `src/engine/VENDORED.md`.
- **Finish clean:** `npm run checks` and `npm test` green before you commit code
  changes.
