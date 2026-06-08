"""PROOF-1 — anchored rating ladder (Bradley-Terry / Elo) across a fixed cast of
agents {random, classical@playouts, net@sims}. Turns scattered pairwise win-rates
into one comparable strength scale with bootstrap CIs (Success-bar-v2 criterion S2).

Agents:
  - RandomAgent           : uniform-legal (the Elo anchor, pinned to 0)
  - ClassicalAgent(p)     : classical UCT MCTS, p playouts (CPU)
  - NetAgent(ckpt, sims)  : the net via GPU-batched PUCT MCTS, argmax

The match loop batches NET moves across all games where it is the net's turn
(one GPU forward per sim round) while classical/random move per-board. Net-vs-net
pairs run on GPU in the main process; pairs with NO net are farmed across CPU
cores (classical is the slow part). Ratings fit by the standard Bradley-Terry
minorization-maximization; CIs by bootstrap over games.

Usage:
  uv run python ladder.py <n> <games_per_pair> [out.json]
"""
from __future__ import annotations
import os, sys, json, time, math, random
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

# Pin BLAS/OMP to 1 thread BEFORE importing numpy/torch: we parallelize across
# games with a process pool, so each worker must be single-threaded or 14 workers
# x 32 intra-op threads oversubscribe the 32-thread CPU and everything crawls.
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np
import torch
torch.set_num_threads(1)

from a3go_engine import Board
from az import action_to_move, move_to_action
from batched_az import BatchedMCTS
from classical_mcts import ClassicalMCTS
from arch_util import load_net


# ---------------------------------------------------------------- agents
class RandomAgent:
    kind = "cpu"
    def __init__(self, seed=0): self.rng = random.Random(seed)
    def move(self, board, passes):
        mv = board.legal_moves()
        return self.rng.choice(mv) if mv else "pass"


class ClassicalAgent:
    kind = "cpu"
    def __init__(self, playouts, seed=0):
        self.playouts = playouts; self.seed = seed
        self.mcts = ClassicalMCTS(playouts=playouts, seed=seed)
    def move(self, board, passes):
        return self.mcts.select_move(board, passes)


class NetAgent:
    kind = "net"
    def __init__(self, ckpt, n, sims, device, seed=0, temp_moves=6):
        self.net, self.ch, self.bl = load_net(ckpt, n, device)
        self.mcts = BatchedMCTS(self.net, device, sims=sims, seed=seed)
        self.sims = sims; self.ckpt = ckpt; self.temp_moves = temp_moves
        self.rng = random.Random(seed * 1000 + 7)
    def moves_batch(self, boards, passes_list, ply):
        # Sample (temp=1) for the opening plies so games VARY, then play argmax —
        # pure argmax made net-vs-net games deterministic per color (degenerate
        # 40/40 ladder results). Opening variety + late-game strength.
        if ply < self.temp_moves:
            pis = self.mcts.run_policies(boards, passes_list, [1.0] * len(boards),
                                         root_noise=0.25)
            return [action_to_move(self.rng.choices(range(len(p)), weights=p)[0],
                                    boards[0].w) for p in pis]
        pis = self.mcts.run_policies(boards, passes_list, [1e-3] * len(boards))
        return [action_to_move(int(p.argmax()), boards[0].w) for p in pis]


def _apply(board, mv, passes, i, done):
    if mv == "pass":
        board.pass_move(); passes[i] += 1
        if passes[i] >= 2: done[i] = True
    else:
        board.play(*mv); passes[i] = 0


def play_match(agentA, agentB, n, games, komi=0.0, seed=0, max_moves=None):
    """A vs B, color-balanced, lockstep so NET turns batch. Returns (A_wins, decided)."""
    max_moves = max_moves or n * n * n * 2
    boards = [Board(n, komi=komi) for _ in range(games)]
    passes = [0] * games
    done = [False] * games
    a_black = [g % 2 == 0 for g in range(games)]
    for ply in range(max_moves):
        for agent, is_a in ((agentA, True), (agentB, False)):
            turn = [i for i in range(games) if not done[i]
                    and ((boards[i].player == 1) == (a_black[i] == is_a))]
            if not turn:
                continue
            if agent.kind == "net":
                mvs = agent.moves_batch([boards[i] for i in turn],
                                        [passes[i] for i in turn], ply)
                for k, i in enumerate(turn):
                    _apply(boards[i], mvs[k], passes, i, done)
            else:
                for i in turn:
                    _apply(boards[i], agent.move(boards[i], passes[i]), passes, i, done)
        if all(done):
            break
    aw = dec = 0
    for i, b in enumerate(boards):
        s = b.score_tromp_taylor()
        if s["winner"] == "draw":
            continue
        dec += 1
        if (s["winner"] == "black") == a_black[i]:
            aw += 1
    return aw, dec


def _build(spec, n, device="cpu", seed=0):
    kind = spec[0]
    if kind == "random": return RandomAgent(seed=seed)
    if kind == "classical": return ClassicalAgent(spec[1], seed=seed)
    if kind == "net":
        # Net runs on GPU when available (workers are spawned, so a fresh CUDA
        # context per worker is safe). On small boards CPU is fine; on 7^3 the
        # net needs the GPU. Classical stays on CPU (rollouts).
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        return NetAgent(spec[1], n, spec[2], dev, seed=seed)
    raise ValueError(spec)


# ---------------------------------------------- per-game worker (CPU, multiproc)
# On small boards (4^3/5^3) the net is tiny and everything is cheap on CPU, so we
# shard the whole tournament into single-game tasks across all cores rather than
# batching on the GPU — maximal parallelism, no fork-after-CUDA hazard. Agents are
# cached per worker so each net checkpoint loads once per process, not per game.
_WORKER_CACHE: dict = {}


def _agent_cached(spec, n, seed):
    key = (spec, seed)
    a = _WORKER_CACHE.get(key)
    if a is None:
        a = _build(spec, n, device="cpu", seed=seed)
        _WORKER_CACHE[key] = a
    return a


def _one_game(task):
    (ia, ib, specA, specB, n, gseed) = task
    a = _agent_cached(specA, n, 7 + ia)
    b = _agent_cached(specB, n, 9 + ib)
    aw, dec = play_match(a, b, n, 1, seed=gseed)  # one game
    return ia, ib, aw, dec


# ------------------------------------------------- Bradley-Terry / Elo fit
def fit_bt(wins, games, anchor_idx=0, iters=5000, reg=1.0):
    """wins[i][j]=A-wins of i over j; games[i][j]=decided games. Returns Elo (anchor=0).

    Regularized: add `reg` virtual wins each direction between every pair (a weak
    symmetric prior) so a player who won 0 or 100% of real games gets a finite
    rating instead of +/-inf — the perfect-separation problem that pinned the
    unregularized fit at the clamp."""
    m = len(wins)
    p = np.ones(m)
    W = np.array(wins, float)
    N = np.array(games, float)
    if reg > 0:
        for i in range(m):
            for j in range(m):
                if i != j:
                    W[i][j] += reg          # reg virtual wins of i over j
                    N[i][j] += reg          # ... over reg virtual games
    wtot = W.sum(axis=1)
    for _ in range(iters):
        newp = p.copy()
        for i in range(m):
            denom = 0.0
            for j in range(m):
                nij = N[i][j] + N[j][i]
                if nij > 0:
                    denom += nij / (p[i] + p[j])
            if denom > 0 and wtot[i] > 0:
                newp[i] = wtot[i] / denom
        newp /= newp.sum()
        if np.max(np.abs(newp - p)) < 1e-12:
            p = newp; break
        p = newp
    elo = 400.0 * np.log10(np.maximum(p, 1e-12))
    elo -= elo[anchor_idx]
    return elo


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    G = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    out = sys.argv[3] if len(sys.argv) > 3 else f"ladder_{n}cubed.json"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Fixed cast. Net checkpoint chosen per board size (the strongest distilled net).
    net_ckpt = {4: "best_distill_big_4cubed.pt", 5: "best_distill5strong_5cubed.pt",
                7: "best_distill7_7cubed.pt"}[n]
    cast = [
        ("random",), ("classical", 16), ("classical", 48), ("classical", 128),
        ("net", net_ckpt, 48), ("net", net_ckpt, 128), ("net", net_ckpt, 256),
    ]
    labels = ["random", "cls@16", "cls@48", "cls@128",
              "net@48", "net@128", "net@256"]
    m = len(cast)
    print(f"# ladder n={n}^3 G={G} cast={labels} (per-game CPU sharding)", flush=True)

    wins = [[0] * m for _ in range(m)]
    games = [[0] * m for _ in range(m)]

    # flat list of single-game tasks over all pairs (color alternates by game seed)
    tasks = []
    for i in range(m):
        for j in range(i + 1, m):
            for g in range(G):
                tasks.append((i, j, cast[i], cast[j], n, 1000 + i * 131 + j * 17 + g))

    t0 = time.time()
    pair_done = {}
    nworkers = min(14, len(tasks))
    with ProcessPoolExecutor(max_workers=nworkers,
                             mp_context=mp.get_context("spawn")) as ex:
        for ia, ib, aw, dec in ex.map(_one_game, tasks, chunksize=1):
            wins[ia][ib] += aw; wins[ib][ia] += (dec - aw)
            games[ia][ib] += dec; games[ib][ia] += dec
            k = (ia, ib); pair_done[k] = pair_done.get(k, 0) + 1
            if pair_done[k] == G:
                w = wins[ia][ib]; d = games[ia][ib]
                print(f"  {labels[ia]:8s} vs {labels[ib]:8s}: {w}/{d}  ({time.time()-t0:.0f}s)", flush=True)

    elo = fit_bt(wins, games, anchor_idx=0)
    # bootstrap CIs over games (resample each pair's outcomes)
    rng = np.random.default_rng(0)
    boot = []
    flat = []
    for i in range(m):
        for j in range(i + 1, m):
            flat.append((i, j, wins[i][j], games[i][j]))
    for _ in range(300):
        bw = [[0] * m for _ in range(m)]; bg = [[0] * m for _ in range(m)]
        for (i, j, w, g) in flat:
            if g == 0: continue
            bwij = rng.binomial(g, w / g)
            bw[i][j] = bwij; bw[j][i] = g - bwij; bg[i][j] = g; bg[j][i] = g
        boot.append(fit_bt(bw, bg, anchor_idx=0))
    boot = np.array(boot)
    lo = np.percentile(boot, 2.5, axis=0); hi = np.percentile(boot, 97.5, axis=0)

    order = np.argsort(-elo)
    table = []
    print(f"\n=== Elo ladder (n={n}^3, anchor random=0), {time.time()-t0:.0f}s ===", flush=True)
    for r in order:
        table.append({"agent": labels[r], "elo": round(float(elo[r]), 1),
                      "ci95": [round(float(lo[r]), 1), round(float(hi[r]), 1)]})
        print(f"  {labels[r]:8s}  {elo[r]:7.1f}  [{lo[r]:7.1f}, {hi[r]:7.1f}]", flush=True)

    result = {"n": n, "games_per_pair": G, "labels": labels, "cast": [list(c) for c in cast],
              "wins": wins, "games": games, "elo": [round(float(x), 2) for x in elo],
              "ci95_lo": [round(float(x), 2) for x in lo], "ci95_hi": [round(float(x), 2) for x in hi],
              "ranking": table, "secs": round(time.time() - t0, 1)}
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nwrote {out}", flush=True)


if __name__ == "__main__":
    main()
