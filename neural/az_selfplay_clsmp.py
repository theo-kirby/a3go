"""INFRA-3 (run 3) — AZ self-play on 5^3 with a PARALLEL CLASSICAL anchor.

PASS-14 (frozen-net anchor) showed a 0.735 net-vs-net gain over the seed did NOT
translate to beating classical (still 0.50@512 parity). Hypothesis: the gate was
optimizing the wrong proxy. This run anchors the promotion gate on the OOD objective
the absolute metric actually measures — cand-vs-CLASSICAL — but keeps it tractable
on 5^3 by running the classical eval through the parallel multiprocessing harness
(net on CPU, games fanned across 14 cores; ~4 min/eval) instead of the sequential
in-loop path (which stalled >40 min/eval on 5^3 — the reason run-2 used a frozen net).

Gate: promote iff cand_vs_best >= 0.55 (net-vs-net, cheap GPU) AND
cand_wr_cls >= best_wr_cls - 1/ANCHOR_GAMES (no regression vs classical).
best_wr_cls is cached, re-measured only on promotion.

Usage: uv run python az_selfplay_clsmp.py [n] [iters] [games] [sims] [out] [seed_ckpt]
"""
from __future__ import annotations
import os, sys, json, time, subprocess
os.environ.setdefault("OMP_NUM_THREADS", "1")
from collections import deque
import torch

from net import A3GoNet
from batched_az import BatchedMCTS, self_play_batch, match_net_vs_net_batched
from arch_util import infer_arch
from az_selfplay import clone_net, train_candidate

ANCHOR_GAMES = 32
ANCHOR_CAP = 50


def classical_winrate(net, n, sims, ch, bl, tag):
    """Win-rate of `net` vs classical@sims via the parallel mp harness (net on CPU)."""
    ckpt = f"_anchor_{tag}.pt"
    out = f"_anchor_{tag}.json"
    torch.save(net.state_dict(), ckpt)
    env = dict(os.environ, A3GO_CH=str(ch), A3GO_BLK=str(bl))
    subprocess.run(
        ["uv", "run", "python", "net_vs_classical_mp.py", ckpt, str(n),
         str(ANCHOR_GAMES), str(sims), str(sims), str(ANCHOR_CAP), out],
        check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wr = json.load(open(out))["net_winrate"]
    os.remove(ckpt); os.remove(out)
    return float(wr)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    games = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    sims = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    out = sys.argv[5] if len(sys.argv) > 5 else f"best_az_cls5_{n}cubed.pt"
    seed_ckpt = sys.argv[6] if len(sys.argv) > 6 else "best_distill5strong_5cubed.pt"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.set_num_threads(1)

    state = torch.load(seed_ckpt, map_location=device)
    ch, bl = infer_arch(state)
    best = A3GoNet(n, channels=ch, blocks=bl).to(device); best.load_state_dict(state); best.eval()
    best_mcts = BatchedMCTS(best, device, sims=sims, seed=1)
    print(f"# INFRA-3(cls-mp) n={n}^3 seed={seed_ckpt} ({ch}x{bl}) iters={iters} games={games} sims={sims} {device}", flush=True)

    best_wr_cls = classical_winrate(best, n, sims, ch, bl, "seed")
    print(f"  seed champion vs classical@{sims}: {best_wr_cls:.3f} (anchor, {ANCHOR_GAMES} games)", flush=True)

    buffer = deque(maxlen=games * 5)
    history = [{"iter": 0, "best_wr_vs_classical": round(best_wr_cls, 3), "event": "seed"}]
    t0 = time.time(); promotions = 0
    for it in range(1, iters + 1):
        ti = time.time()
        examples, _ = self_play_batch(best_mcts, n, games, seed=3000 + it, root_noise=0.25)
        buffer.extend(examples)
        cand = clone_net(best, n, device)
        train_candidate(cand, list(buffer), device, epochs=4)
        cand_mcts = BatchedMCTS(cand, device, sims=sims, seed=2)
        cand_vs_best = match_net_vs_net_batched(cand_mcts, best_mcts, n, 60, temp=0.4, seed=it)
        # only pay for the (expensive) classical anchor if the cheap net-vs-net gate passes
        if cand_vs_best >= 0.55:
            cand_wr_cls = classical_winrate(cand, n, sims, ch, bl, f"it{it}")
        else:
            cand_wr_cls = -1.0
        promote = (cand_vs_best >= 0.55) and (cand_wr_cls >= best_wr_cls - 1.0 / ANCHOR_GAMES)
        ev = {"iter": it, "cand_vs_best": round(cand_vs_best, 3),
              "cand_wr_vs_classical": round(cand_wr_cls, 3),
              "best_wr_vs_classical": round(best_wr_cls, 3),
              "buffer": len(buffer), "promoted": bool(promote), "secs": round(time.time() - ti, 1)}
        history.append(ev)
        print(f"  it{it}: cand_vs_best={cand_vs_best:.3f} cand_vs_cls={cand_wr_cls:.3f} "
              f"best_vs_cls={best_wr_cls:.3f} -> {'PROMOTE' if promote else 'keep'} ({ev['secs']}s)", flush=True)
        if promote:
            best = cand; best.eval(); best_mcts = BatchedMCTS(best, device, sims=sims, seed=1)
            best_wr_cls = cand_wr_cls; promotions += 1
            torch.save(best.state_dict(), out)
        json.dump({"n": n, "sims": sims, "games": games, "anchor_games": ANCHOR_GAMES,
                   "seed_ckpt": seed_ckpt, "promotions": promotions, "history": history,
                   "secs": round(time.time() - t0, 1)},
                  open(f"az_cls5_{n}cubed.json", "w"), indent=2)
    torch.save(best.state_dict(), out)
    print(f"\nfinal best vs classical@{sims}: {best_wr_cls:.3f} ({promotions} promotions) -> {out}", flush=True)
    print(f"wrote az_cls5_{n}cubed.json ({round(time.time()-t0,1)}s)", flush=True)


if __name__ == "__main__":
    main()
