"""INFRA-3 (run 2) — AZ self-play with a FROZEN-reference anchor, for 5^3.

Run 1 (4^3) validated the externally-anchored gate but per-iter classical eval is
too slow on 5^3 (~15-25 min/eval). Here the gate anchors to the FROZEN distilled
champion the run was seeded from (net-vs-net, GPU-cheap, drift-free because the
reference never moves — the Pass-5 drift came from anchoring to the MOVING best).
"Does self-play beat the net it started from?" is a meaningful beyond-distillation
claim (the distilled 5^3 net is at parity with classical [e7c35c64]). A classical
translation check on the final best is left to a separate parallel eval.

Gate: promote candidate iff (a) beats current best head-to-head >= 0.55 AND
(b) does not regress vs the frozen reference (cand_vs_ref >= best_vs_ref - tol).

Usage: uv run python az_selfplay_frozen.py [n] [iters] [games] [sims] [out] [seed_ckpt]
"""
from __future__ import annotations
import os, sys, json, time
os.environ.setdefault("OMP_NUM_THREADS", "1")
from collections import deque
import torch

from net import A3GoNet
from batched_az import BatchedMCTS, self_play_batch, match_net_vs_net_batched
from arch_util import infer_arch
from az_selfplay import clone_net, train_candidate


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    games = int(sys.argv[3]) if len(sys.argv) > 3 else 80
    sims = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    out = sys.argv[5] if len(sys.argv) > 5 else f"best_az_frozen_{n}cubed.pt"
    seed_ckpt = sys.argv[6] if len(sys.argv) > 6 else {
        4: "best_distill_big_4cubed.pt", 5: "best_distill5strong_5cubed.pt",
        7: "best_distill7_7cubed.pt"}[n]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.set_num_threads(1)

    state = torch.load(seed_ckpt, map_location=device)
    ch, bl = infer_arch(state)
    def fresh():
        m = A3GoNet(n, channels=ch, blocks=bl).to(device); m.load_state_dict(state); m.eval(); return m
    ref = fresh()                  # FROZEN reference (the distilled champion)
    best = fresh()                 # current best (starts == ref)
    ref_mcts = BatchedMCTS(ref, device, sims=sims, seed=9)
    best_mcts = BatchedMCTS(best, device, sims=sims, seed=1)
    print(f"# INFRA-3(frozen) n={n}^3 seed={seed_ckpt} ({ch}x{bl}) iters={iters} games={games} sims={sims} {device}", flush=True)

    EVAL = 80
    best_vs_ref = 0.5              # best starts identical to ref
    buffer = deque(maxlen=games * 5)
    history = [{"iter": 0, "best_vs_ref": 0.5, "event": "seed"}]
    t0 = time.time()
    promotions = 0
    for it in range(1, iters + 1):
        ti = time.time()
        examples, _ = self_play_batch(best_mcts, n, games, seed=2000 + it, root_noise=0.25)
        buffer.extend(examples)
        cand = clone_net(best, n, device)
        train_candidate(cand, list(buffer), device, epochs=4)
        cand_mcts = BatchedMCTS(cand, device, sims=sims, seed=2)
        cand_vs_best = match_net_vs_net_batched(cand_mcts, best_mcts, n, EVAL, temp=0.4, seed=it)
        cand_vs_ref = match_net_vs_net_batched(cand_mcts, ref_mcts, n, EVAL, temp=0.4, seed=100 + it)
        promote = (cand_vs_best >= 0.55) and (cand_vs_ref >= best_vs_ref - 1.0 / EVAL)
        ev = {"iter": it, "cand_vs_best": round(cand_vs_best, 3), "cand_vs_ref": round(cand_vs_ref, 3),
              "best_vs_ref": round(best_vs_ref, 3), "buffer": len(buffer),
              "promoted": bool(promote), "secs": round(time.time() - ti, 1)}
        history.append(ev)
        print(f"  it{it}: cand_vs_best={cand_vs_best:.3f} cand_vs_ref={cand_vs_ref:.3f} "
              f"best_vs_ref={best_vs_ref:.3f} -> {'PROMOTE' if promote else 'keep'} ({ev['secs']}s)", flush=True)
        if promote:
            best = cand; best.eval(); best_mcts = BatchedMCTS(best, device, sims=sims, seed=1)
            best_vs_ref = cand_vs_ref; promotions += 1
            torch.save(best.state_dict(), out)
        json.dump({"n": n, "sims": sims, "games": games, "seed_ckpt": seed_ckpt,
                   "promotions": promotions, "history": history, "secs": round(time.time() - t0, 1)},
                  open(f"az_frozen_{n}cubed.json", "w"), indent=2)
    torch.save(best.state_dict(), out)
    print(f"\nfinal best vs frozen distilled champion: {best_vs_ref:.3f} ({promotions} promotions) -> {out}", flush=True)
    print(f"wrote az_frozen_{n}cubed.json ({round(time.time()-t0,1)}s)", flush=True)


if __name__ == "__main__":
    main()
