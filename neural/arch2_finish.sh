#!/usr/bin/env bash
# ARCH-2 finisher: 3 consistent seeds (40ep, lr2e-3) of the BN-free nested-bottleneck
# net on the SAME data+soft-target as AUX-3's BN-soft baseline; eval each vs classical
# (5^3, net@512 vs cls@48, n=128); then an UNCONTENDED games/sec comparison vs BN-soft.
set -e
cd /home/theo/a3go/neural
export A3GO_BR_CH=64 A3GO_BR_BLK=8 A3GO_BR_CB=48
NPZ=distill_softpol_5cubed.npz
for s in 0 1 2; do
  echo "=== ARCH2 train seed $s ==="
  A3GO_SEED=$s uv run python train_arch2.py $NPZ 40 best_arch2_s$s.pt 256 2e-3
done
for s in 0 1 2; do
  echo "=== ARCH2 eval seed $s ==="
  uv run python eval_arch2.py best_arch2_s$s.pt 5 128 512 48 50 experiments_arch2_s$s.json
done
echo "=== CLEAN SPEED (sequential, 24 games each) ==="
A3GO_BR_CH=64 A3GO_BR_BLK=8 A3GO_BR_CB=48 uv run python eval_arch2.py best_arch2_s0.pt 5 24 512 48 50 /tmp/arch2_speed.json
A3GO_CH=64 A3GO_BLK=6 uv run python -c "
import time, multiprocessing as mp, json
import net_vs_classical_mp as M
args=[(g,'best_sp5_soft_s0.pt',5,512,48,50) for g in range(24)]
t0=time.time()
with mp.Pool(14) as p: p.map(M._play_one,args)
secs=time.time()-t0
json.dump({'net':'BN-soft-64x6','params':1413603,'games':24,'games_per_sec':round(24/secs,4)}, open('/tmp/bnsoft_speed.json','w'))
print('BN-soft games/sec =', round(24/secs,4))
"
echo ALL_ARCH2_DONE
