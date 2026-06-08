"""AlphaZero training with the two stability fixes the naive loop was missing:
a multi-generation REPLAY BUFFER (no catastrophic forgetting) and BEST-NET
GATING (a new net only becomes the self-play net if it actually beats the
current best). Self-play uses Dirichlet root noise (in az.self_play_game).

    uv run python train_gated.py [n] [iters] [games] [sims] [out] [eval_games]
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
from az import MCTS, self_play_game, play_match_vs_random, play_match_net_vs_net


def train_copy(best, examples, device, epochs=6, batch=128, lr=1e-3):
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
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    games = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    sims = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    out = sys.argv[5] if len(sys.argv) > 5 else "train_gated_result.json"
    eval_games = int(sys.argv[6]) if len(sys.argv) > 6 else 30

    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(0)
    random.seed(0)
    best = A3GoNet(n).to(device)
    best.eval()
    base = copy.deepcopy(best)  # frozen gen-0 reference
    buffer: deque = deque(maxlen=12000)
    print(f"# AZ + replay buffer + gating — {n}^3, {iters} iters x {games} games, sims={sims}, {device}")

    history = []
    t_start = time.time()
    for it in range(1, iters + 1):
        t0 = time.time()
        # 1) Self-play with the current BEST net (+ Dirichlet noise inside).
        sp = MCTS(best, device, sims=sims, seed=1000 + it)
        draws = bw = ww = 0
        for g in range(games):
            data, winner = self_play_game(sp, n, rng=random.Random(7000 * it + g))
            buffer.extend(data)
            draws += winner == 0
            bw += winner == 1
            ww += winner == 2
        # 2) Train a candidate from best on the whole replay buffer.
        cand, loss = train_copy(best, list(buffer), device)
        # 3) Gate: promote only if candidate beats best.
        wr_cand_vs_best = play_match_net_vs_net(
            MCTS(cand, device, sims=sims), MCTS(best, device, sims=sims), n, eval_games, seed=it
        )
        promoted = wr_cand_vs_best >= 0.55
        if promoted:
            best = cand
        # 4) Track best vs random and vs frozen gen-0.
        wr_random = play_match_vs_random(MCTS(best, device, sims=sims), n, eval_games, seed=100 + it)
        wr_vs_base = play_match_net_vs_net(
            MCTS(best, device, sims=sims), MCTS(base, device, sims=sims), n, eval_games, seed=200 + it
        )
        row = {
            "iter": it,
            "buffer": len(buffer),
            "loss": round(loss, 4),
            "cand_vs_best": round(wr_cand_vs_best, 3),
            "promoted": promoted,
            "best_vs_random": round(wr_random, 3),
            "best_vs_gen0": round(wr_vs_base, 3),
            "selfplay_bwd": [bw, ww, draws],
            "secs": round(time.time() - t0, 1),
        }
        history.append(row)
        print(f"  it {it}: loss={row['loss']} cand_vs_best={row['cand_vs_best']} "
              f"{'PROMOTED' if promoted else 'kept'} best_vs_random={row['best_vs_random']} "
              f"best_vs_gen0={row['best_vs_gen0']} ({row['secs']:.0f}s)")

    result = {
        "boardSize": n, "iters": iters, "gamesPerIter": games, "sims": sims,
        "evalGames": eval_games, "device": device, "replayBuffer": True, "gating": True,
        "totalSecs": round(time.time() - t_start, 1), "history": history,
    }
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    torch.save(best.state_dict(), f"best_{n}cubed.pt")
    print(f"Wrote -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
