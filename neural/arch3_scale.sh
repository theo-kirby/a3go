#!/usr/bin/env bash
# PASS-19 SCALE-libs: capacity scale-up on the winning liberty input (cfg=libs).
# Only CAPACITY varies vs ARCH-3's libs@64x6 (0.449); same data + soft-target +
# protocol (5^3, net@512 vs cls@48 cap50, n=128, seeds 0/1/2). Train 96x8 + 128x10;
# eval 96x8 vs classical now (128x10 eval deferred — big-net CPU eval ~5h/seed).
# Idempotent.
cd /home/theo/a3go/neural
export A3GO_CFG=libs A3GO_SP_T=4 A3GO_SP_W=8 A3GO_SP_PRUNE=0.02
NPZ=distill_arch3_5cubed.npz

echo "=== TRAIN libs 96x8 + 128x10 (x3 seeds) $(date) ==="
for cb in "96 8" "128 10"; do
  set -- $cb; CH=$1; BLK=$2
  for s in 0 1 2; do
    ck=best_libs_${CH}x${BLK}_s${s}.pt
    if [ -f "$ck" ]; then echo "  $ck exists, skip"; continue; fi
    echo "  -- train libs ${CH}x${BLK} seed=$s $(date +%H:%M:%S) --"
    A3GO_CH=$CH A3GO_BLK=$BLK A3GO_SEED=$s uv run python train_arch3.py $NPZ 40 $ck 256 1e-3 2>&1 | tail -1
  done
done

echo "=== EVAL libs 96x8 x3 vs classical@48 n=128 net@512 $(date) ==="
for s in 0 1 2; do
  out=experiments_libs_96x8_s${s}.json
  if [ -f "$out" ]; then echo "  $out exists, skip"; continue; fi
  echo "  -- eval libs 96x8 seed=$s $(date +%H:%M:%S) --"
  A3GO_CH=96 A3GO_BLK=8 uv run python eval_arch3.py best_libs_96x8_s${s}.pt 5 128 512 48 50 $out 2>&1 | tail -3
done
echo "ARCH3_SCALE_96_DONE $(date)"
