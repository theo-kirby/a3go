"""INFRA-3 — AlphaZero self-play to beat the classical teacher (Success-bar S5).

Distillation caps the net at the teacher's quality. This runs a real AZ loop —
net-guided MCTS self-play (M5 batched, GPU) -> train a candidate -> gate -> repeat
— seeded from the distilled champion, to push PAST the teacher ceiling.

The gate is EXTERNALLY ANCHORED (the Pass-5 scar: unanchored net-vs-net self-play
DRIFTS off the truth — it improved every self-referential metric while dropping
strength vs classical). So we promote a candidate only if it (a) does NOT regress
against classical MCTS@matched vs the current best, AND (b) beats the current best
head-to-head. Best's classical win-rate is cached and only re-measured on promotion.

Usage: uv run python az_selfplay.py [n] [iters] [games] [sims] [out_ckpt] [seed_ckpt]
"""
from __future__ import annotations
import os, sys, json, time, copy, random
os.environ.setdefault("OMP_NUM_THREADS", "1")
from collections import deque
import numpy as np
import torch
import torch.nn.functional as F

from a3go_engine import Board
from net import A3GoNet
from az import action_to_move
from batched_az import BatchedMCTS, self_play_batch, match_net_vs_net_batched
from classical_mcts import ClassicalMCTS
from arch_util import infer_arch


def clone_net(net, n, device):
    ch = net.stem[0].weight.shape[0]
    bl = len([k for k in net.state_dict() if k.startswith("tower.") and k.endswith(".c1.weight")])
    c = A3GoNet(n, channels=ch, blocks=bl).to(device)
    c.load_state_dict(copy.deepcopy(net.state_dict()))
    return c


def train_candidate(net, buffer, device, epochs=4, batch=256, lr=5e-4):
    X = torch.from_numpy(np.stack([e[0] for e in buffer])).to(device)
    P = torch.from_numpy(np.stack([e[1] for e in buffer])).to(device)
    Z = torch.from_numpy(np.stack([np.float32(e[2]) for e in buffer])).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=lr, weight_decay=1e-4)
    m = X.shape[0]
    net.train()
    for ep in range(epochs):
        perm = torch.randperm(m, device=device)
        for i in range(0, m, batch):
            idx = perm[i:i + batch]
            logits, v = net(X[idx])
            loss = -(P[idx] * F.log_softmax(logits, 1)).sum(1).mean() + F.mse_loss(v, Z[idx])
            opt.zero_grad(); loss.backward(); opt.step()
    net.eval()


def match_net_vs_classical(net_mcts, cls_playouts, n, games, seed=0):
    """Net (GPU-batched MCTS, argmax) vs classical UCT (CPU, sequential per board),
    color-balanced, lockstep so net moves batch. Returns net win-rate over decided."""
    boards = [Board(n) for _ in range(games)]
    passes = [0] * games
    done = [False] * games
    net_black = [g % 2 == 0 for g in range(games)]
    cls = [ClassicalMCTS(playouts=cls_playouts, seed=seed * 100 + g) for g in range(games)]
    maxm = n * n * n * 2
    for _ in range(maxm):
        net_turn = [i for i in range(games) if not done[i] and ((boards[i].player == 1) == net_black[i])]
        cls_turn = [i for i in range(games) if not done[i] and ((boards[i].player == 1) != net_black[i])]
        if not net_turn and not cls_turn:
            break
        if net_turn:
            pis = net_mcts.run_policies([boards[i] for i in net_turn], [passes[i] for i in net_turn],
                                        [1e-3] * len(net_turn))
            for k, i in enumerate(net_turn):
                a = int(pis[k].argmax()); mv = action_to_move(a, n)
                _apply(boards[i], mv, passes, done, i)
        for i in cls_turn:
            mv = cls[i].select_move(boards[i], passes[i])
            _apply(boards[i], mv, passes, done, i)
    w = d = 0
    for i, b in enumerate(boards):
        s = b.score_tromp_taylor()
        if s["winner"] == "draw":
            continue
        d += 1
        if (s["winner"] == "black") == net_black[i]:
            w += 1
    return w / max(1, d)


def _apply(b, mv, passes, done, i):
    if mv == "pass":
        b.pass_move(); passes[i] += 1
        if passes[i] >= 2: done[i] = True
    else:
        b.play(*mv); passes[i] = 0


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    games = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    sims = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    out = sys.argv[5] if len(sys.argv) > 5 else f"az_selfplay_{n}cubed.pt"
    seed_ckpt = sys.argv[6] if len(sys.argv) > 6 else {
        4: "best_distill_big_4cubed.pt", 5: "best_distill5strong_5cubed.pt"}[n]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.set_num_threads(1)

    state = torch.load(seed_ckpt, map_location=device)
    ch, bl = infer_arch(state)
    best = A3GoNet(n, channels=ch, blocks=bl).to(device); best.load_state_dict(state); best.eval()
    print(f"# INFRA-3 AZ self-play n={n}^3 seed={seed_ckpt} ({ch}x{bl}) iters={iters} games={games} sims={sims} {device}", flush=True)

    ANCHOR_PLAYOUTS = sims      # classical anchor matched to self-play sims
    ANCHOR_GAMES = 24
    best_mcts = BatchedMCTS(best, device, sims=sims, seed=1)
    best_wr_cls = match_net_vs_classical(best_mcts, ANCHOR_PLAYOUTS, n, ANCHOR_GAMES, seed=0)
    print(f"  seed champion vs classical@{ANCHOR_PLAYOUTS}: {best_wr_cls:.3f} (anchor)", flush=True)

    buffer = deque(maxlen=games * 5)
    history = [{"iter": 0, "best_wr_vs_classical": round(best_wr_cls, 3), "event": "seed"}]
    t0 = time.time()
    for it in range(1, iters + 1):
        ti = time.time()
        # 1. self-play with the current best (Dirichlet root noise on)
        examples, _ = self_play_batch(best_mcts, n, games, seed=1000 + it, root_noise=0.25)
        buffer.extend(examples)
        # 2. train candidate warm-started from best
        cand = clone_net(best, n, device)
        train_candidate(cand, list(buffer), device, epochs=4)
        cand_mcts = BatchedMCTS(cand, device, sims=sims, seed=2)
        # 3. gate: cand vs best (net-vs-net) + cand vs classical (external anchor)
        cand_vs_best = match_net_vs_net_batched(cand_mcts, best_mcts, n, 60, temp=0.4, seed=it)
        cand_wr_cls = match_net_vs_classical(cand_mcts, ANCHOR_PLAYOUTS, n, ANCHOR_GAMES, seed=it)
        promote = (cand_vs_best >= 0.55) and (cand_wr_cls >= best_wr_cls - 1.0 / ANCHOR_GAMES)
        ev = {"iter": it, "cand_vs_best": round(cand_vs_best, 3),
              "cand_wr_vs_classical": round(cand_wr_cls, 3),
              "best_wr_vs_classical": round(best_wr_cls, 3),
              "buffer": len(buffer), "promoted": bool(promote), "secs": round(time.time() - ti, 1)}
        history.append(ev)
        print(f"  it{it}: cand_vs_best={cand_vs_best:.3f} cand_vs_cls={cand_wr_cls:.3f} "
              f"best_vs_cls={best_wr_cls:.3f} -> {'PROMOTE' if promote else 'keep'} ({ev['secs']}s)", flush=True)
        if promote:
            best = cand; best.eval()
            best_mcts = BatchedMCTS(best, device, sims=sims, seed=1)
            best_wr_cls = cand_wr_cls
            torch.save(best.state_dict(), out)
        json.dump({"n": n, "sims": sims, "games": games, "anchor_playouts": ANCHOR_PLAYOUTS,
                   "history": history, "secs": round(time.time() - t0, 1)},
                  open(f"az_selfplay_{n}cubed.json", "w"), indent=2)
    torch.save(best.state_dict(), out)
    print(f"\nfinal best vs classical@{ANCHOR_PLAYOUTS}: {best_wr_cls:.3f}  -> {out}", flush=True)
    print(f"wrote az_selfplay_{n}cubed.json ({round(time.time()-t0,1)}s)", flush=True)


if __name__ == "__main__":
    main()
