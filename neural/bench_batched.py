"""Benchmark batched self-play games/sec vs the batch-1 baseline (~0.05 g/s on
4^3, sims=32 — train_gated_4.json: 192 games / 3867 s)."""
from __future__ import annotations
import sys, time, json
import torch
from net import A3GoNet
from batched_az import BatchedMCTS, self_play_batch


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    games = int(sys.argv[2]) if len(sys.argv) > 2 else 64
    sims = int(sys.argv[3]) if len(sys.argv) > 3 else 32
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(0)
    net = A3GoNet(n).to(device).eval()
    mcts = BatchedMCTS(net, device, sims=sims, seed=1)

    t0 = time.time()
    examples, winners = self_play_batch(mcts, n, games, komi=0.0, seed=7)
    dt = time.time() - t0
    bw = sum(w == 1 for w in winners); ww = sum(w == 2 for w in winners); dr = sum(w == 0 for w in winners)
    gps = games / dt
    baseline = 0.05
    out = {
        "n": n, "games": games, "sims": sims, "device": device,
        "secs": round(dt, 1), "games_per_sec": round(gps, 3),
        "examples": len(examples), "B_W_draw": [bw, ww, dr],
        "baseline_gps": baseline, "speedup_x": round(gps / baseline, 1),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
