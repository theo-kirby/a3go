"""Minimal AlphaZero training loop for 3D Go: self-play -> train -> evaluate,
for a few generations on a small board. Proves the pipeline end-to-end and emits
a JSON result (win-rate vs random + generation-over-generation strength) for the
Flywheel graph.

    uv run python train.py [n] [iters] [games_per_iter] [sims]
"""

from __future__ import annotations

import copy
import json
import random
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F

from net import A3GoNet
from az import MCTS, self_play_game, play_match_vs_random, play_match_net_vs_net


def train_on(net, examples, device, epochs=4, batch=128, lr=1e-3):
    net.train()
    opt = torch.optim.Adam(net.parameters(), lr=lr, weight_decay=1e-4)
    X = torch.from_numpy(np.stack([e[0] for e in examples])).to(device)
    P = torch.from_numpy(np.stack([e[1] for e in examples])).to(device)
    Z = torch.from_numpy(np.stack([e[2] for e in examples])).to(device)
    n = X.shape[0]
    last = 0.0
    for _ in range(epochs):
        perm = torch.randperm(n, device=device)
        for i in range(0, n, batch):
            idx = perm[i : i + batch]
            logits, v = net(X[idx])
            logp = F.log_softmax(logits, dim=1)
            loss_p = -(P[idx] * logp).sum(dim=1).mean()
            loss_v = F.mse_loss(v, Z[idx])
            loss = loss_p + loss_v
            opt.zero_grad()
            loss.backward()
            opt.step()
            last = float(loss.item())
    return last


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    games_per_iter = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    sims = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    eval_games = int(sys.argv[6]) if len(sys.argv) > 6 else 40

    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(0)
    random.seed(0)
    net = A3GoNet(n).to(device)
    print(f"# Neural AZ training — {n}^3, {iters} iters × {games_per_iter} games, "
          f"sims={sims}, device={device}")

    # Baseline: untrained net vs random.
    gen0 = copy.deepcopy(net)
    history = []
    t_start = time.time()
    for it in range(1, iters + 1):
        t0 = time.time()
        mcts = MCTS(net, device, sims=sims, seed=1000 + it)
        examples = []
        wins = {0: 0, 1: 0, 2: 0}
        for g in range(games_per_iter):
            data, winner = self_play_game(mcts, n, rng=random.Random(1000 * it + g))
            examples.extend(data)
            wins[winner] += 1
        loss = train_on(net, examples, device)
        # Evaluate current net vs uniform-random.
        eval_mcts = MCTS(net, device, sims=sims)
        wr_random = play_match_vs_random(eval_mcts, n, eval_games, seed=it)
        # Strength vs the untrained gen-0 net.
        wr_vs_gen0 = play_match_net_vs_net(eval_mcts, MCTS(gen0, device, sims=sims), n, eval_games)
        secs = time.time() - t0
        row = {
            "iter": it,
            "examples": len(examples),
            "selfplay_blackwins": wins[1],
            "selfplay_whitewins": wins[2],
            "selfplay_draws": wins[0],
            "loss": round(loss, 4),
            "winrate_vs_random": round(wr_random, 4),
            "winrate_vs_gen0": round(wr_vs_gen0, 4),
            "secs": round(secs, 1),
        }
        history.append(row)
        print(f"  iter {it}: loss={row['loss']} vs_random={row['winrate_vs_random']:.2f} "
              f"vs_gen0={row['winrate_vs_gen0']:.2f} ({row['secs']:.0f}s)")

    result = {
        "boardSize": n,
        "iters": iters,
        "gamesPerIter": games_per_iter,
        "sims": sims,
        "evalGames": eval_games,
        "device": device,
        "totalSecs": round(time.time() - t_start, 1),
        "history": history,
    }
    out = sys.argv[5] if len(sys.argv) > 5 else "train_result.json"
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    torch.save(net.state_dict(), f"net_{n}cubed_gen{iters}.pt")
    print(f"Wrote -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
