"""ALGO-1 A/B — Gumbel AlphaZero vs PUCT at matched and varying sim budgets.

Question: does Gumbel root selection give more strength-per-sim than PUCT? Key
comparisons on 4^3 (fast): Gumbel@N vs PUCT@N (matched), and Gumbel@low vs
PUCT@high (does Gumbel@16 match PUCT@32/64?). Per-game CPU sharding, net on GPU.

Usage: uv run python ab_gumbel.py [n] [games] [out.json]
"""
from __future__ import annotations
import os, sys, json, time, math
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import torch
torch.set_num_threads(1)

from a3go_engine import Board
from az import action_to_move
from arch_util import load_net

CKPT = {4: "best_distill_big_4cubed.pt", 5: "best_distill5strong_5cubed.pt",
        7: "best_distill7_7cubed.pt"}


class GumbelAgent:
    kind = "cpu"
    def __init__(self, ckpt, n, sims, device, seed=0):
        from gumbel_az import GumbelMCTS
        self.net, _, _ = load_net(ckpt, n, device)
        # Gumbel needs sims >> max_considered for sequential halving to have rounds;
        # tune the considered set to the budget (paper uses 16 with sims~50-200).
        mc = max(2, min(16, sims // 4))
        self.m = GumbelMCTS(self.net, device, sims=sims, max_considered=mc, seed=seed)
    def move(self, board, passes):
        return action_to_move(self.m.select(board, passes), board.w)


class PUCTAgent:
    kind = "cpu"
    def __init__(self, ckpt, n, sims, device, seed=0, temp_moves=6):
        from batched_az import BatchedMCTS
        self.net, _, _ = load_net(ckpt, n, device)
        self.m = BatchedMCTS(self.net, device, sims=sims, seed=seed)
        self.temp_moves = temp_moves; self.n = n; self.ply = 0
        import random; self.rng = random.Random(seed * 7 + 1)
    def move(self, board, passes):
        # opening-temperature sampling for variety (else PUCT argmax is deterministic)
        self.ply += 1
        if self.ply <= self.temp_moves:
            pi = self.m.run_policies([board], [passes], [1.0], root_noise=0.25)[0]
            return action_to_move(self.rng.choices(range(len(pi)), weights=pi)[0], board.w)
        pi = self.m.run_policies([board], [passes], [1e-3])[0]
        return action_to_move(int(pi.argmax()), board.w)


def play_game(agentA, agentB, n, a_black, seed):
    b = Board(n)
    passes = 0; ply = 0
    while ply < n * n * n * 2:
        agent = agentA if ((b.player == 1) == a_black) else agentB
        mv = agent.move(b, passes)
        if mv == "pass":
            b.pass_move(); passes += 1
            if passes >= 2: break
        else:
            b.play(*mv); passes = 0
        ply += 1
    s = b.score_tromp_taylor()
    if s["winner"] == "draw": return None
    return (s["winner"] == "black") == a_black  # True => A won


SPECS = None  # set in main, passed via task


def _one(task):
    (label, specA, specB, n, gi) = task
    import torch as _t; _t.set_num_threads(1)
    dev = "cuda" if _t.cuda.is_available() else "cpu"
    ck = CKPT[n]
    A = _mk(specA, n, ck, dev, seed=100 + gi)
    B = _mk(specB, n, ck, dev, seed=200 + gi)
    r = play_game(A, B, n, a_black=(gi % 2 == 0), seed=gi)
    return (label, r)


def _mk(spec, n, ck, dev, seed):
    kind, sims = spec
    if kind == "gumbel": return GumbelAgent(ck, n, sims, dev, seed=seed)
    return PUCTAgent(ck, n, sims, dev, seed=seed)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    G = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    out = sys.argv[3] if len(sys.argv) > 3 else f"ab_gumbel_{n}cubed.json"
    # matchups: (label, A=gumbel, B=puct)
    matchups = [
        ("gumbel8_vs_puct8",    ("gumbel", 8),  ("puct", 8)),
        ("gumbel16_vs_puct16",  ("gumbel", 16), ("puct", 16)),
        ("gumbel32_vs_puct32",  ("gumbel", 32), ("puct", 32)),
        ("gumbel64_vs_puct64",  ("gumbel", 64), ("puct", 64)),
        ("gumbel16_vs_puct32",  ("gumbel", 16), ("puct", 32)),
    ]
    tasks = []
    for (lab, sa, sb) in matchups:
        for gi in range(G):
            tasks.append((lab, sa, sb, n, gi))
    print(f"# ALGO-1 Gumbel A/B n={n}^3 G={G}, {len(matchups)} matchups", flush=True)
    agg = {lab: [0, 0] for (lab, _, _) in matchups}  # [A_wins, decided]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=min(14, len(tasks)),
                             mp_context=mp.get_context("spawn")) as ex:
        for (lab, r) in ex.map(_one, tasks, chunksize=1):
            if r is None: continue
            agg[lab][1] += 1
            if r: agg[lab][0] += 1
    res = []
    print(f"\n=== Gumbel A/B (win-rate of Gumbel side), n={n}^3, {time.time()-t0:.0f}s ===", flush=True)
    for (lab, _, _) in matchups:
        w, d = agg[lab]
        wr = w / d if d else 0.0
        z = 1.96; lo = hi = wr
        if d:
            den = 1 + z*z/d; c = wr + z*z/(2*d)
            half = z*math.sqrt(wr*(1-wr)/d + z*z/(4*d*d))
            lo, hi = (c-half)/den, (c+half)/den
        res.append({"matchup": lab, "gumbel_winrate": round(wr, 3), "decided": d,
                    "ci95": [round(lo, 3), round(hi, 3)]})
        print(f"  {lab:24s}: {wr:.3f} [{lo:.3f},{hi:.3f}]  ({w}/{d})", flush=True)
    json.dump({"n": n, "games": G, "results": res, "secs": round(time.time()-t0, 1)},
              open(out, "w"), indent=2)
    print(f"\nwrote {out}", flush=True)


if __name__ == "__main__":
    main()
