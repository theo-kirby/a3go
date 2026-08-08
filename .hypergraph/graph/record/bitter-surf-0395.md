---
node_id: 08e469c3-18c7-5b06-8716-5a0431482749
slug: bitter-surf-0395
title: 'Neural toolchain up: torch 2.11+cu128, CUDA verified on RTX 5090 (sm_120 Blackwell)'
created_at: '2026-06-07T12:59:17.681756+00:00'
parents:
- crimson-frog-9812
summary: Milestone 1/4. uv project under neural/ with torch 2.11.0+cu128; torch.cuda.is_available()=True; device RTX 5090, capability (12,0); a 2048x2048 GPU matmul runs cleanly. Start gate (toolchain + GPU) satisfied.
origin:
  backend: flywheel
  node_id: 08e469c3-18c7-5b06-8716-5a0431482749
  slug: bitter-surf-0395
  revision: 1
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: e30e94a2-6da4-51ed-b4d0-e65974e569c3
  slug: wispy-shape-2944
  revision: 0
  pushed_at: '2026-08-08T10:01:49+00:00'
  content_sha256: 5d15092308b9e1595d630f267f1a121621d773765d5d94b9f0802fec613ca6da
---
# Phase 2 milestone 1 — toolchain stood up + GPU verified

## What was done
- `uv init neural` + `uv add numpy torch --index https://download.pytorch.org/whl/cu128` → **torch 2.11.0+cu128**, pinned in pyproject.toml + uv.lock (.venv gitignored).
- Verification: `torch.cuda.is_available()` → **True**; device **NVIDIA GeForce RTX 5090**; compute capability **(12, 0) = sm_120 (Blackwell)**; driver 580.159.03; 32 GB VRAM.
- Ran a 2048×2048 GPU matmul → finite result (confirms Blackwell kernels actually execute, not just that the capability string parses — the cu128 wheel is required for sm_120).

## Why it matters
The neural README start gate needs the uv+PyTorch toolchain GPU-verified before scaling. Blackwell (sm_120) is new enough that an older CUDA wheel would import but fail at kernel launch; cu128 / torch ≥2.7 is required. This is now confirmed. Budget honored: **/bin/bash / local GPU**, no managed compute.

## Reproduce
`uv run --directory neural python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_capability(0))"`. Artifact attached.