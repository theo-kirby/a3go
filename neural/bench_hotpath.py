"""Microbenchmark the self-play hot path to locate the throughput wall:
single-position GPU eval latency vs batched eval vs the pure-Python engine ops
(legal_moves, clone) per expansion. Guides whether M5 needs an engine optimization
alongside batched inference.
"""
from __future__ import annotations
import time
import numpy as np
import torch
from a3go_engine import Board
from net import A3GoNet, encode
import az


def timeit(fn, iters):
    t0 = time.perf_counter()
    for _ in range(iters):
        fn()
    return (time.perf_counter() - t0) / iters


def main():
    n = 4
    device = "cuda" if torch.cuda.is_available() else "cpu"
    net = A3GoNet(n).to(device).eval()

    # A mid-game-ish board: play ~20 random legal moves.
    rng = np.random.default_rng(0)
    b = Board(n)
    for _ in range(20):
        mv = b.legal_moves()
        if not mv:
            break
        x, y, z = mv[rng.integers(len(mv))]
        try:
            b.play(x, y, z)
        except Exception:
            pass

    # 1) engine ops
    t_legal = timeit(lambda: b.legal_moves(), 200)
    t_clone = timeit(lambda: b.clone(), 2000)
    t_encode = timeit(lambda: encode(b), 2000)

    # 2) single-position GPU eval (batch 1) incl host<->device + sync
    x1 = torch.from_numpy(encode(b)).unsqueeze(0).to(device)
    def eval1():
        with torch.no_grad():
            _ = net(x1)
        torch.cuda.synchronize() if device == "cuda" else None
    eval1()  # warmup
    t_eval1 = timeit(eval1, 200)

    # 3) batched GPU eval, various batch sizes (per-position cost)
    batch_rows = {}
    for B in (8, 32, 128, 256, 512):
        xb = torch.from_numpy(np.stack([encode(b)] * B)).to(device)
        def evalB():
            with torch.no_grad():
                _ = net(xb)
            torch.cuda.synchronize() if device == "cuda" else None
        evalB()  # warmup
        per = timeit(evalB, 50) / B
        batch_rows[B] = per

    print(f"# 4^3 hot-path microbench on {device}")
    print(f"legal_moves : {t_legal*1e3:8.3f} ms")
    print(f"clone       : {t_clone*1e3:8.3f} ms")
    print(f"encode      : {t_encode*1e3:8.3f} ms")
    print(f"eval batch=1: {t_eval1*1e3:8.3f} ms/pos")
    for B, per in batch_rows.items():
        print(f"eval batch={B:<4}: {per*1e3:8.4f} ms/pos  ({t_eval1/per:6.1f}x vs b=1)")

    # Where does a single expansion's time go? expansion = encode + eval + legal_moves
    print("\n# per-expansion cost model (batch-1 eval):")
    print(f"  encode+eval1+legal = {(t_encode+t_eval1+t_legal)*1e3:.3f} ms")
    print(f"  with batched eval(256): legal_moves alone = {t_legal*1e3:.3f} ms dominates")


if __name__ == "__main__":
    main()
