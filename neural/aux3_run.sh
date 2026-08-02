#!/usr/bin/env bash
# AUX-3 A/B: hard (argmax, 1x) vs soft (T=4, W=8, prune=0.02) policy target.
# Same raw-visit 5^3 data, 3 seeds, plain A3GoNet 64x6. Eval matches AUX-1:
# net_sims=512 vs classical@48 cap50, n=128.
set -e
cd /home/theo/a3go/neural
export A3GO_CH=64 A3GO_BLK=6
NPZ=distill_softpol_5cubed.npz
for s in 0 1 2; do
  echo "=== seed $s HARD train ==="
  A3GO_SP_MODE=hard A3GO_SEED=$s uv run python train_softpolicy.py $NPZ 40 best_sp5_hard_s$s.pt 256 1e-3
  echo "=== seed $s SOFT train (T=4 W=8) ==="
  A3GO_SP_MODE=soft A3GO_SP_T=4 A3GO_SP_W=8 A3GO_SP_PRUNE=0.02 A3GO_SEED=$s uv run python train_softpolicy.py $NPZ 40 best_sp5_soft_s$s.pt 256 1e-3
done
for s in 0 1 2; do
  echo "=== seed $s HARD eval ==="
  uv run python net_vs_classical_mp.py best_sp5_hard_s$s.pt 5 128 512 48 50 experiments_aux3_hard_s$s.json
  echo "=== seed $s SOFT eval ==="
  uv run python net_vs_classical_mp.py best_sp5_soft_s$s.pt 5 128 512 48 50 experiments_aux3_soft_s$s.json
done
echo ALL_AUX3_DONE
