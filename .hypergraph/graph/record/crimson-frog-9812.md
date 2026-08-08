---
node_id: c67f9da4-2149-5c1e-9d8f-91768caa6cfb
slug: crimson-frog-9812
title: Phase 2 — Neural self-play (AlphaZero-style) [DESIGN BRIEF + IN PROGRESS]
created_at: '2026-06-07T12:52:31.634886+00:00'
parents:
- purple-fog-6345
summary: 'The major next thrust: a PyTorch policy/value net trained from self-play on the local RTX 5090 ($0). The only path to komi precision and the ''rising self-play strength'' half of the success bar. Contains the design brief; empirical children track milestones.'
origin:
  backend: flywheel
  node_id: c67f9da4-2149-5c1e-9d8f-91768caa6cfb
  slug: crimson-frog-9812
  revision: 0
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: 70186fe1-a9e6-5641-a99d-4ccdd46eb636
  slug: young-star-7683
  revision: 0
  pushed_at: '2026-08-08T10:01:24+00:00'
  content_sha256: f8febf83e5b46fe2e01ba2e36c7b6369060d2099286344f10d87ef59e7007fec
---
# Phase 2 — Neural self-play (AlphaZero-style)

## Why now (start gate — both hold)
1. Self-play throughput is characterized (pass 1: parallel harness, games/s per size measured). ✓
2. Toolchain readiness + human go-ahead. ✓ (`uv` present, RTX 5090 driver 580.159; human confirmed).

## Design brief (run through the design gate before scaling)
- **Objective:** train a policy/value network via self-play that (a) beats the classical MCTS reference and (b) produces a monotone rising-strength curve, and use its lower-variance evaluations to pin komi.
- **Hypothesis:** a small 3D-conv net + MCTS-with-net (PUCT) will exceed classical MCTS at equal or lower playout budget, and its sharper value estimates will make komi identifiable on 4³ where win-rate could not.
- **Method:** (1) port a minimal 3D-Go engine to Python (NumPy) for fast batched self-play, **cross-validated against the TS engine**; (2) define a policy+value CNN (PyTorch); (3) AlphaZero loop: self-play → train → evaluate vs previous best → promote; start on 3³/4³.
- **Decision criterion:** new net beats classical MCTS with win-rate CI excluding 50%; successive generations beat predecessors (within noise); komi estimate SE shrinks vs the classical mean-margin estimate.
- **Metrics:** head-to-head win-rate (±CI), generation-over-generation win-rate, value-head komi estimate + SE, self-play games/sec on GPU.
- **Baselines:** classical MCTS (`silent-dew-2840`), uniform-random.
- **Budget:** $0 / local GPU (RTX 5090). No managed compute. Reproducibility: pin `pyproject.toml` + `uv.lock`; seed self-play.
- **Risks/confounds:** Blackwell (sm_120) needs a recent CUDA wheel (cu128 / torch ≥2.7); engine-port bugs would silently corrupt training — mitigated by cross-validation against the 48/48-tested TS engine; small boards are near-2D so test 4³+ too.
- **Outcome & next step:** _(filled as milestones land in the empirical children below)_

## Milestones (each becomes an empirical child)
1. Toolchain up + `torch.cuda.is_available()` True on the 5090.
2. Python 3D-Go engine ported + cross-validated vs TS engine.
3. Net defined + GPU forward pass; minimal self-play→train→eval loop end-to-end on 3³.
4. First neural-vs-MCTS evaluation; first rising-strength data point.