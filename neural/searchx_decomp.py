"""SEARCHX-1 — net-vs-search decomposition: how much of the agent's strength is
the NET vs the SEARCH? Degenerate-search regimes on the trained 5^3 libs net:

  - policy-only   : play the raw net policy argmax, NO tree (sims=0)
  - value-only-1ply: expand all legal root children, evaluate each child's value
                     in one batched forward, play the move minimizing the
                     opponent's value (greedy 1-ply, no recursion)
  - full MCTS     : sims sweep {1,4,16,64}

Each regime's strength is anchored by win-rate vs uniform-random (absolute), and
policy-only is also played head-to-head vs full(sims=64) to read off how much
search adds on top of the raw net. 5^3 only (the trained libs checkpoints are 5^3);
the per-board-size sweep needs cheap 4^3/7^3 libs nets (stage REP/ARCH-1 retrain).

    uv run python searchx_decomp.py [n] [games] [out.json]
"""
from __future__ import annotations
import os, sys, json, time, random
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np
import torch
torch.set_num_threads(1)

from a3go_engine import Board
from batched_az import BatchedMCTS, _apply_action, _apply_move, _winrate, _legal_random_move
from net_arch3 import A3GoNetIn
from input_planes import config_planes, n_planes
from az import legal_action_mask, action_to_move, n_actions

CFG = "libs"
SEEDS = [0, 1, 2]


class RichMCTS(BatchedMCTS):
    def __init__(self, net, device, cfg, sims, seed=0):
        super().__init__(net, device, sims=sims, seed=seed)
        self.cfg = cfg

    def _eval_batch(self, boards):
        if not boards:
            return None, None
        X = torch.from_numpy(np.stack([config_planes(b, self.cfg) for b in boards])).to(self.device)
        with torch.no_grad():
            logits, v = self.net(X)
        return logits.float().cpu().numpy(), v.float().cpu().numpy()


class PolicyOnly(RichMCTS):
    """Raw net policy, no tree."""
    def run_policies(self, boards, passes_list, temps, root_noise=0.0, dir_alpha=0.5):
        lg, _ = self._eval_batch(boards)
        out = []
        for k, b in enumerate(boards):
            mask = legal_action_mask(b)
            x = np.where(mask, lg[k], -1e9)
            x = x - x.max()
            p = np.exp(x) * mask
            s = p.sum()
            out.append((p / s if s > 0 else mask / mask.sum()).astype(np.float32))
        return out


class ValueOnly1Ply(RichMCTS):
    """Greedy 1-ply on value: pick the move minimizing the opponent's value."""
    def run_policies(self, boards, passes_list, temps, root_noise=0.0, dir_alpha=0.5):
        # Build child boards per game; one batched value forward over all children.
        all_children = []
        spans = []
        for b in boards:
            n = b.w
            mask = legal_action_mask(b)
            acts = [a for a in range(n_actions(n)) if mask[a]]
            kids = []
            for a in acts:
                mv = action_to_move(a, n)
                cb = b.clone()
                if mv == "pass":
                    cb.pass_move()
                else:
                    cb.play(*mv)
                kids.append((a, cb))
            spans.append((len(all_children), len(kids)))
            all_children.extend(cb for _, cb in kids)
            spans[-1] = (spans[-1][0], spans[-1][1], acts)
        vals = None
        if all_children:
            _, v = self._eval_batch(all_children)
            vals = v
        out = []
        for gi, b in enumerate(boards):
            n = b.w
            start, k, acts = spans[gi]
            pi = np.zeros(n_actions(n), dtype=np.float32)
            if k == 0:
                pi[n_actions(n) - 1] = 1.0
            else:
                # child value is from the CHILD's side-to-move (opponent) POV; we
                # want to MINIMIZE opponent value -> argmin.
                cv = vals[start:start + k]
                best = acts[int(np.argmin(cv))]
                pi[best] = 1.0
            out.append(pi)
        return out


def load_net(n, seed, device):
    net = A3GoNetIn(n, in_planes=n_planes(CFG), channels=64, blocks=6)
    net.load_state_dict(torch.load(f"best_arch3_{CFG}_s{seed}.pt", map_location=device))
    return net.to(device).eval()


def match_vs_random(agent, n, games, seed):
    rng = random.Random(seed)
    boards = [Board(n) for _ in range(games)]
    passes = [0] * games; done = [False] * games
    net_black = [g % 2 == 0 for g in range(games)]
    for _ in range(n * n * n * 2):
        nt = [i for i in range(games) if not done[i] and ((boards[i].player == 1) == net_black[i])]
        rt = [i for i in range(games) if not done[i] and ((boards[i].player == 1) != net_black[i])]
        if not nt and not rt:
            break
        if nt:
            pis = agent.run_policies([boards[i] for i in nt], [passes[i] for i in nt], [1e-3] * len(nt))
            for k, i in enumerate(nt):
                _apply_action(boards[i], int(pis[k].argmax()), n, passes, done, i)
        for i in rt:
            _apply_move(boards[i], _legal_random_move(boards[i], rng), passes, done, i)
    return _winrate(boards, net_black)


def match_aa(a, b, n, games, seed, temp=0.3):
    rng = random.Random(seed)
    boards = [Board(n) for _ in range(games)]
    passes = [0] * games; done = [False] * games
    a_black = [g % 2 == 0 for g in range(games)]
    for _ in range(n * n * n * 2):
        for agent, isa in ((a, True), (b, False)):
            turn = [i for i in range(games) if not done[i]
                    and ((boards[i].player == 1) == (a_black[i] == isa))]
            if not turn:
                continue
            pis = agent.run_policies([boards[i] for i in turn], [passes[i] for i in turn], [temp] * len(turn))
            for k, i in enumerate(turn):
                _apply_action(boards[i], rng.choices(range(len(pis[k])), weights=pis[k])[0], n, passes, done, i)
        if all(done):
            break
    return _winrate(boards, a_black)


def wr_ci(wr, ndec):
    se = (wr * (1 - wr) / max(1, ndec)) ** 0.5
    return [round(wr - 1.96 * se, 4), round(wr + 1.96 * se, 4)]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    games = int(sys.argv[2]) if len(sys.argv) > 2 else 64
    out = sys.argv[3] if len(sys.argv) > 3 else "searchx1_decomp.json"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sims_sweep = [1, 4, 16, 64]
    t0 = time.time()
    print(f"# SEARCHX-1 decomposition n={n}^3 games={games} device={device}", flush=True)

    def make(seed, kind, sims=0):
        net = load_net(n, seed, device)
        if kind == "policy":
            return PolicyOnly(net, device, CFG, sims=0, seed=300 + seed)
        if kind == "value1ply":
            return ValueOnly1Ply(net, device, CFG, sims=0, seed=400 + seed)
        return RichMCTS(net, device, CFG, sims=sims, seed=500 + seed)

    regimes = [("policy_only", "policy", 0), ("value_only_1ply", "value1ply", 0)]
    regimes += [(f"mcts_sims{s}", "mcts", s) for s in sims_sweep]

    vs_random = {}
    for label, kind, sims in regimes:
        wtot = 0.0
        for s in SEEDS:
            ag = make(s, kind, sims)
            wtot += match_vs_random(ag, n, games, seed=7000 + s)
        wr = wtot / len(SEEDS)
        vs_random[label] = {"winrate_vs_random": round(wr, 4), "ci95": wr_ci(wr, games * len(SEEDS))}
        print(f"  {label:16s} vs random: {wr:.4f} {vs_random[label]['ci95']} ({time.time()-t0:.0f}s)", flush=True)

    # head-to-head: policy-only vs full(sims=64) -> how much search adds
    h2h = 0.0
    for s in SEEDS:
        po = make(s, "policy"); full = make(s, "mcts", 64)
        h2h += match_aa(po, full, n, games, seed=8000 + s)
    h2h /= len(SEEDS)
    print(f"  policy_only vs mcts_sims64 (A=policy): {h2h:.4f} {wr_ci(h2h, games*len(SEEDS))}", flush=True)

    result = {"experiment": "SEARCHX-1 net-vs-search decomposition (libs 5^3)",
              "n": n, "games_per_seed": games, "seeds": SEEDS, "sims_sweep": sims_sweep,
              "vs_random": vs_random,
              "policy_only_vs_mcts64": {"policy_winrate": round(h2h, 4), "ci95": wr_ci(h2h, games * len(SEEDS))},
              "secs": round(time.time() - t0, 1)}
    json.dump(result, open(out, "w"), indent=2)
    print(f"wrote {out} ({result['secs']}s)", flush=True)


if __name__ == "__main__":
    main()
