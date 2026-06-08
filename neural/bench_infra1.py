"""INFRA-1 throughput benchmark: locate the true wall in GPU-batched MCTS.

For each board size we time BatchedMCTS.run_policies (one full move-search for a
batch of B independent games at S sims) and separately time the isolated batched
GPU forward (_eval_batch). The gap between (total move time) and (S * forward
time) is the per-node PYTHON ENGINE cost (clone + legal_moves floodfill + select),
which is NOT batched and is the suspected residual wall on big boards.

Outputs JSON: per (n, B, sims) -> ms/move/game, sims/s aggregate, GPU-forward
fraction. Establishes whether INFRA-1's remaining lever is GPU (no) or the engine
(INFRA-2: incremental legal moves / avoid full clone).
"""
from __future__ import annotations
import sys, json, time
import numpy as np
import torch

from a3go_engine import Board
from net import encode
from batched_az import BatchedMCTS
from arch_util import load_net


def time_forward(net, device, boards, reps=5):
    X = torch.from_numpy(np.stack([encode(b) for b in boards])).to(device)
    with torch.no_grad():  # warmup
        net(X)
    if device == "cuda":
        torch.cuda.synchronize()
    t0 = time.time()
    for _ in range(reps):
        with torch.no_grad():
            logits, v = net(X)
        if device == "cuda":
            torch.cuda.synchronize()
    return (time.time() - t0) / reps


def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    cfg = [
        ("4", "best_distill_big_4cubed.pt", [64, 256], [64, 256]),
        ("5", "best_distill5strong_5cubed.pt", [64, 256], [64, 256]),
        ("7", "best_distill7_7cubed.pt", [32, 128], [128, 512]),
    ]
    out = {"device": device, "results": []}
    for n_s, ckpt, batches, sims_list in cfg:
        n = int(n_s)
        try:
            net, ch, bl = load_net(ckpt, n, device)
        except Exception as e:
            out["results"].append({"n": n, "ckpt": ckpt, "error": str(e)[:200]})
            print(f"n={n} load FAIL: {e}", flush=True)
            continue
        for B in batches:
            boards = [Board(n) for _ in range(B)]
            fwd = time_forward(net, device, boards)
            for S in sims_list:
                mcts = BatchedMCTS(net, device, sims=S, c_puct=1.5, seed=0)
                # fresh empty boards (worst case = most legal moves)
                bb = [Board(n) for _ in range(B)]
                t0 = time.time()
                mcts.run_policies(bb, [0] * B, [1e-3] * B)
                dt = time.time() - t0
                per_move_game_ms = dt / B * 1000.0
                sims_per_s = S * B / dt
                gpu_frac = (S * fwd) / dt if dt > 0 else 0.0
                rec = {"n": n, "ckpt": ckpt, "arch": f"{ch}x{bl}", "B": B, "sims": S,
                       "move_total_s": round(dt, 3), "ms_per_move_per_game": round(per_move_game_ms, 2),
                       "sims_per_s_agg": round(sims_per_s, 1), "fwd_ms_batch": round(fwd * 1000, 2),
                       "gpu_forward_frac": round(gpu_frac, 3)}
                out["results"].append(rec)
                print(f"n={n} {ch}x{bl} B={B:4d} S={S:4d} | {per_move_game_ms:7.1f} ms/move/game | "
                      f"{sims_per_s:8.0f} sims/s | fwd={fwd*1000:5.1f}ms | GPU%={gpu_frac*100:4.1f}",
                      flush=True)
    with open("bench_infra1.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote bench_infra1.json", flush=True)


if __name__ == "__main__":
    main()
