# Neural phase (deferred)

This directory is a **placeholder** for a future neural self-play training phase
(AlphaZero-style: a policy/value network trained from self-play, replacing the
hand-written rollouts of the classical MCTS agent). It ships **no dependencies
and no toolchain** — only this note. The classical, dependency-light TypeScript
stack in `src/` is the whole campaign for now.

## What this phase would be

- A PyTorch (Python) training loop: self-play game generation → train a
  policy/value net → evaluate the new net against the previous best → repeat.
- A bridge between the TypeScript engine and Python (or a port of the engine),
  fast enough to generate self-play data at the volume neural training needs.
- Stronger agents measured against the same success bar as the classical phase
  (beats baselines; rising self-play strength — see
  [../docs/THESIS.md](../docs/THESIS.md)).

## Compute is local and free

Training runs on the **local GPU** — an **NVIDIA RTX 5090 (32 GB VRAM)** on this
box (see [../docs/BOOTSTRAP.md](../docs/BOOTSTRAP.md) → "You have strong local
compute"). That means neural training is **$0 / local** and is **not** gated on a
managed-compute budget. The NVIDIA driver is already present; what's missing is
the Python toolchain (no PyTorch, no Python project here yet).

## Toolchain: Python via `uv`

**Anything that needs the GPU is Python, and Python here is managed with
[`uv`](https://docs.astral.sh/uv/).** The TypeScript engine/self-play stack stays
on `tsx` and never touches the GPU; this neural phase is a *separate Python
project* living under `neural/`. Do not reach for raw `pip`/`venv`/`conda` — use
`uv` so the environment is reproducible and pinned.

When this phase opens, scaffold roughly:

```bash
cd neural
uv init                     # create the Python project (pyproject.toml)
uv add torch                # CUDA-enabled PyTorch wheel (see note below)
uv run python -c "import torch; print(torch.cuda.is_available())"   # expect True
uv run <train-script>.py    # always run GPU code through `uv run`
```

Commit `pyproject.toml` **and** `uv.lock` so the env is reproducible; `.venv/` is
gitignored. Note on CUDA: PyTorch's wheels bundle their own CUDA runtime, so the
present GPU driver is sufficient — you do **not** need to install the system CUDA
toolkit (`nvcc`) for standard training. `nvcc` is only required if you later
compile custom CUDA kernels. Pick the wheel index matching the installed driver
(e.g. a recent `cu12x` build) if the default resolve doesn't land a CUDA build.

## Start gate

**Open this phase only after both of these hold:**

1. **Local self-play throughput has been characterized** — i.e. the campaign has
   actually measured how many self-play games/sec the engine produces per board
   size (ideally *after* parallelizing across the CPU's 32 threads), and what
   bounds it. Neural training needs self-play data at volume, so know the data
   rate first. (See CODEBASE.md's performance note and THESIS.md Q2.)
2. **The `uv` + PyTorch toolchain is stood up and GPU-verified**
   (`uv run python -c "import torch; print(torch.cuda.is_available())"` → `True`
   on the RTX 5090), **and** the human has confirmed it's time to start the
   neural phase. No *managed* compute budget is required — the GPU is local and
   free — so this is a readiness/sequencing gate, not a spending gate.

Until then the budget posture is **$0 / local-only** (no managed/cloud compute);
neural training is out of scope and this directory stays a stub. When the gate
opens, design the phase as a Flywheel design brief and run it through the design
gate before standing up the toolchain.
