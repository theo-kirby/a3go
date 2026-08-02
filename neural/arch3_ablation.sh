#!/usr/bin/env bash
# ARCH-3 attribution: the full 10-plane stack beat the 3-plane baseline decisively
# (+0.106, CI-separated). Now eval each single plane-GROUP arm (base+one group) vs
# classical at the SAME protocol to attribute the gain. Nets already trained by
# arch3_pipeline.sh. Idempotent.
cd /home/theo/a3go/neural
export A3GO_CH=64 A3GO_BLK=6
for cfg in koban libs capture history; do
  for s in 0 1 2; do
    out=experiments_arch3_${cfg}_s${s}.json
    if [ -f "$out" ]; then echo "  $out exists, skip"; continue; fi
    echo "  -- eval cfg=$cfg seed=$s $(date +%H:%M:%S) --"
    A3GO_CFG=$cfg uv run python eval_arch3.py best_arch3_${cfg}_s${s}.pt 5 128 512 48 50 $out 2>&1 | tail -3
  done
done
echo "ARCH3_ABLATION_DONE $(date)"
