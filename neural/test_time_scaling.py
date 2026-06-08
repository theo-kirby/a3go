"""PROOF-2 — test-time search scaling of the distilled nets, across board sizes.

Question: does giving the SAME net more MCTS sims at play time make it stronger,
and does the effect grow on bigger boards where the value head is better
calibrated (cross-board law: value MSE 0.044/0.019/0.006 for 4^3/5^3/7^3)?

Each (board, sims) point is an independent net@S-vs-net@baseline match; INFRA-1
showed these matches are CPU-bound (the GPU forward is tiny), so we run the points
across a process pool (one core each, GPU shared and free) rather than serially.
All net-vs-net, color-balanced, low-temp sampling for variety.

Usage: uv run python test_time_scaling.py [out.json]
"""
from __future__ import annotations
import os, sys, json, time, math
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import torch
torch.set_num_threads(1)


def wilson(p, n, z=1.96):
    if n == 0:
        return (0.0, 1.0)
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - half) / d, (c + half) / d)


CFGS = [
    (4, "best_distill_big_4cubed.pt", 48, [48, 96, 192, 384, 768]),
    (5, "best_distill5strong_5cubed.pt", 48, [48, 96, 192, 384, 768]),
    (7, "best_distill7_7cubed.pt", 64, [64, 128, 256, 512, 1024]),
]
GAMES = 60


def run_point(task):
    (n, ckpt, S, base, seed) = task
    import torch as _t
    _t.set_num_threads(1)
    from batched_az import BatchedMCTS, match_net_vs_net_batched
    from arch_util import load_net
    device = "cuda" if _t.cuda.is_available() else "cpu"
    net, ch, bl = load_net(ckpt, n, device)
    a = BatchedMCTS(net, device, sims=S, seed=11)
    b = BatchedMCTS(net, device, sims=base, seed=777)
    t0 = time.time()
    wr = match_net_vs_net_batched(a, b, n, GAMES, temp=0.4, seed=S)
    return (n, S, base, f"{ch}x{bl}", round(wr, 3), round(time.time() - t0, 1))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "test_time_scaling.json"
    tasks = []
    for n, ckpt, base, sweep in CFGS:
        for S in sweep:
            tasks.append((n, ckpt, S, base, S))
    print(f"# test-time scaling: {len(tasks)} (board,sims) points across a pool, {GAMES} games each", flush=True)
    t0 = time.time()
    raw = {}
    with ProcessPoolExecutor(max_workers=min(14, len(tasks)),
                             mp_context=mp.get_context("spawn")) as ex:
        for (n, S, base, arch, wr, secs) in ex.map(run_point, tasks):
            lo, hi = wilson(wr, GAMES)
            raw.setdefault(n, {"arch": arch, "baseline_sims": base, "curve": []})
            raw[n]["curve"].append({"sims": S, "winrate": wr, "ci95": [round(lo, 3), round(hi, 3)], "secs": secs})
            print(f"  n={n}^3 net@{S:5d} vs net@{base}: {wr:.3f} [{lo:.3f},{hi:.3f}]  ({secs}s)", flush=True)
    boards = []
    for n in sorted(raw):
        raw[n]["curve"].sort(key=lambda c: c["sims"])
        boards.append({"n": n, **raw[n]})
    result = {"games_per_point": GAMES, "boards": boards, "secs": round(time.time() - t0, 1)}
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n=== scaling curves (win-rate of net@S vs fixed baseline) ===", flush=True)
    for bd in boards:
        pts = "  ".join(f"{c['sims']}:{c['winrate']:.2f}" for c in bd["curve"])
        print(f"  {bd['n']}^3 (base@{bd['baseline_sims']}): {pts}", flush=True)
    print(f"\nwrote {out} ({result['secs']}s)", flush=True)


if __name__ == "__main__":
    main()
