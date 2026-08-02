#!/usr/bin/env bash
# ARCH-3 pipeline: richer input planes vs the 3-plane baseline, holding the target
# (AUX-3 soft policy T=4/W=8/prune) + trunk (A3GoNet 64x6) + data-gen FIXED so the
# ONLY variable is the input representation. Idempotent (skip-if-exists) so it can
# resume after interruption. Protocol matches AUX-3/ARCH-2: 5^3, net@512 vs cls@48
# cap50, n=128, seeds {0,1,2} pooled.
cd /home/theo/a3go/neural
export A3GO_CH=64 A3GO_BLK=6 A3GO_SP_T=4 A3GO_SP_W=8 A3GO_SP_PRUNE=0.02
NPZ=distill_arch3_5cubed.npz
CONFIGS="base all koban libs capture history"

echo "=== PHASE 1: COLLECT $(date) ==="
if [ ! -f "$NPZ" ]; then
  uv run python collect_arch3.py 5 384 128 64 $NPZ
else
  echo "  $NPZ exists, skipping collect"
fi

echo "=== PHASE 2: TRAIN (6 cfg x 3 seeds) $(date) ==="
for cfg in $CONFIGS; do
  for s in 0 1 2; do
    ck=best_arch3_${cfg}_s${s}.pt
    if [ -f "$ck" ]; then echo "  $ck exists, skip"; continue; fi
    echo "  -- train cfg=$cfg seed=$s $(date +%H:%M:%S) --"
    A3GO_CFG=$cfg A3GO_SEED=$s uv run python train_arch3.py $NPZ 40 $ck 256 1e-3 2>&1 | tail -1
  done
done

echo "=== PHASE 3: EVAL base + all (3 seeds, net@512 vs cls@48, n=128) $(date) ==="
for cfg in base all; do
  for s in 0 1 2; do
    out=experiments_arch3_${cfg}_s${s}.json
    if [ -f "$out" ]; then echo "  $out exists, skip"; continue; fi
    echo "  -- eval cfg=$cfg seed=$s $(date +%H:%M:%S) --"
    A3GO_CFG=$cfg uv run python eval_arch3.py best_arch3_${cfg}_s${s}.pt 5 128 512 48 50 $out 2>&1 | tail -3
  done
done
echo "ARCH3_HEADLINE_DONE $(date)"
