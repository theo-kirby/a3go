"""M5-powered AlphaZero training at VOLUME — the lever M4 identified as the wall.

Same stability machinery as train_gated.py (multi-generation replay buffer +
best-net gating + Dirichlet root noise) but self-play and ALL evaluation matches
run through batched_az (game-parallel, single batched GPU forward per sim round),
so we can afford ~5x the self-play volume of M4 in less wall-clock.

    uv run python train_batched.py [n] [iters] [games] [sims] [out] [eval_games] [buffer]

Logs one line per generation (flushed) so progress can be monitored live.
"""
from __future__ import annotations

import copy
import json
import random
import sys
import time
from collections import deque

import numpy as np
import torch
import torch.nn.functional as F

from net import A3GoNet
from batched_az import (
    BatchedMCTS, self_play_batch,
    match_vs_random_batched, match_net_vs_net_batched,
)


def train_copy(best, examples, device, epochs=6, batch=256, lr=1e-3):
    net = copy.deepcopy(best)
    net.train()
    opt = torch.optim.Adam(net.parameters(), lr=lr, weight_decay=1e-4)
    X = torch.from_numpy(np.stack([e[0] for e in examples])).to(device)
    P = torch.from_numpy(np.stack([e[1] for e in examples])).to(device)
    Z = torch.from_numpy(np.stack([e[2] for e in examples])).to(device)
    m = X.shape[0]
    last = 0.0
    for _ in range(epochs):
        perm = torch.randperm(m, device=device)
        for i in range(0, m, batch):
            idx = perm[i : i + batch]
            logits, v = net(X[idx])
            loss = -(P[idx] * F.log_softmax(logits, dim=1)).sum(1).mean() + F.mse_loss(v, Z[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
            last = float(loss.item())
    net.eval()
    return net, last


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    games = int(sys.argv[3]) if len(sys.argv) > 3 else 96
    sims = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    out = sys.argv[5] if len(sys.argv) > 5 else "train_batched_4.json"
    eval_games = int(sys.argv[6]) if len(sys.argv) > 6 else 40
    buffer_max = int(sys.argv[7]) if len(sys.argv) > 7 else 40000
    gate = float(sys.argv[8]) if len(sys.argv) > 8 else 0.55  # promotion threshold
    init = sys.argv[9] if len(sys.argv) > 9 else ""  # warm-start checkpoint (autogo: distill->selfplay)
    ckpt_out = sys.argv[10] if len(sys.argv) > 10 else f"best_batched_{int(sys.argv[1]) if len(sys.argv)>1 else 4}cubed.pt"

    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(0)
    random.seed(0)
    np.random.seed(0)
    best = A3GoNet(n).to(device)
    if init:
        best.load_state_dict(torch.load(init, map_location=device))
        print(f"# warm-started from {init}", flush=True)
    best.eval()
    base = copy.deepcopy(best)  # frozen gen-0/init reference
    buffer: deque = deque(maxlen=buffer_max)
    print(f"# M5 batched AZ — {n}^3, {iters} iters x {games} games, sims={sims}, "
          f"buffer={buffer_max}, eval={eval_games}, {device}", flush=True)

    history = []
    promotions = 0
    t_start = time.time()
    for it in range(1, iters + 1):
        t0 = time.time()
        # 1) Self-play with current BEST (batched, Dirichlet noise inside).
        sp = BatchedMCTS(best, device, sims=sims, seed=1000 + it)
        # autogo: fixed Dirichlet noise compounds badly across iterations -> anneal
        # from 0.25 down to 0.05 so late generations get cleaner per-game targets.
        noise = 0.25 - 0.20 * (it - 1) / max(1, iters - 1)
        data, winners = self_play_batch(sp, n, games, seed=7000 * it, root_noise=noise)
        buffer.extend(data)
        bw = sum(w == 1 for w in winners)
        ww = sum(w == 2 for w in winners)
        dr = sum(w == 0 for w in winners)
        t_sp = time.time() - t0
        # 2) Train candidate from best on the whole replay buffer.
        t1 = time.time()
        cand, loss = train_copy(best, list(buffer), device)
        t_tr = time.time() - t1
        # 3) Gate: promote only if candidate beats best.
        t2 = time.time()
        wr_cand = match_net_vs_net_batched(
            BatchedMCTS(cand, device, sims=sims), BatchedMCTS(best, device, sims=sims),
            n, eval_games, seed=it)
        promoted = wr_cand >= gate
        if promoted:
            best = cand
            promotions += 1
        # 4) Strength tracking: vs random and vs frozen gen-0.
        wr_random = match_vs_random_batched(
            BatchedMCTS(best, device, sims=sims), n, eval_games, seed=100 + it)
        wr_base = match_net_vs_net_batched(
            BatchedMCTS(best, device, sims=sims), BatchedMCTS(base, device, sims=sims),
            n, eval_games, seed=200 + it)
        t_ev = time.time() - t2
        row = {
            "iter": it, "buffer": len(buffer), "loss": round(loss, 4),
            "cand_vs_best": round(wr_cand, 3), "promoted": promoted,
            "promotions": promotions,
            "best_vs_random": round(wr_random, 3), "best_vs_gen0": round(wr_base, 3),
            "selfplay_bwd": [bw, ww, dr],
            "secs": round(time.time() - t0, 1),
            "t_selfplay": round(t_sp, 1), "t_train": round(t_tr, 1), "t_eval": round(t_ev, 1),
            "games_per_sec": round(games / t_sp, 2),
        }
        history.append(row)
        print(f"  it {it}: loss={row['loss']} cand_vs_best={row['cand_vs_best']} "
              f"{'PROMOTED' if promoted else 'kept'}(#{promotions}) "
              f"vs_random={row['best_vs_random']} vs_gen0={row['best_vs_gen0']} "
              f"sp={row['games_per_sec']}g/s ({row['secs']:.0f}s)", flush=True)
        # checkpoint each iter so a kill is recoverable
        result = {
            "boardSize": n, "iters": iters, "gamesPerIter": games, "sims": sims,
            "evalGames": eval_games, "device": device, "bufferMax": buffer_max,
            "replayBuffer": True, "gating": True, "batchedSelfPlay": True,
            "promotions": promotions,
            "totalSecs": round(time.time() - t_start, 1), "history": history,
        }
        with open(out, "w") as f:
            json.dump(result, f, indent=2)
        torch.save(best.state_dict(), ckpt_out)

    print(f"Wrote -> {out}  (promotions={promotions}/{iters})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
