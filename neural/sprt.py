"""WS1 / EVAL-1 (`259c2ebe`) — SPRT-bounded net-vs-classical anchor.

The net-vs-net screen (screen_nvn.py) orders the lever family fast, but it is a
*relative* signal — it can't say "beats classical". For that we still need the
expensive net-vs-classical match (eval_arch3.py), which ran a FIXED 128 games/seed
(~3h/seed) regardless of how early the result was obvious. This wraps the same
per-game match in a Sequential Probability Ratio Test (Wald): we accumulate decided
games and stop the moment the evidence crosses a decision boundary, so a clear
winner (or clear non-winner) resolves in a fraction of the fixed-n cost while a
genuine near-parity result still runs out to the cap.

Hypotheses on the net's win-rate p against classical at equal budget:
  H0: p = p0  (<= parity, default 0.50)   vs   H1: p = p1  (> parity, default 0.55)
Decision boundaries from (alpha, beta) error rates (default 0.05 each):
  accept H1 (beats classical) when LLR >= log((1-beta)/alpha)
  accept H0 (not a winner)     when LLR <= log(beta/(1-alpha))
Each decided game contributes log(p1/p0) on a win, log((1-p1)/(1-p0)) on a loss;
draws are excluded (same convention as eval_arch3 win-rate). Capped at n_max
decided games — reaching the cap is itself the "re-power" audit the PASS-15
small-sample scar demands (we record the n the result actually rests on).

Reuses eval_arch3._play_one verbatim for the game (net on CPU MCTS vs classical
random-rollout MCTS at equal budget), so the protocol is byte-identical to the
fixed-n anchor; only the stopping rule changes.

Usage:
  A3GO_CFG=libs A3GO_CH=64 A3GO_BLK=6 uv run python sprt.py \
      best_arch3_libs_s0.pt 5 512 48 50 [n_max] [p0] [p1] [out.json]
"""
from __future__ import annotations
import os, sys, json, math, time
import multiprocessing as mp

from eval_arch3 import _play_one, wilson


def main() -> int:
    ckpt = sys.argv[1] if len(sys.argv) > 1 else "best_arch3_libs_s0.pt"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    net_sims = int(sys.argv[3]) if len(sys.argv) > 3 else 512
    cls_playouts = int(sys.argv[4]) if len(sys.argv) > 4 else 48
    cls_cap = int(sys.argv[5]) if len(sys.argv) > 5 else 50
    n_max = int(sys.argv[6]) if len(sys.argv) > 6 else 256
    p0 = float(sys.argv[7]) if len(sys.argv) > 7 else 0.50
    p1 = float(sys.argv[8]) if len(sys.argv) > 8 else 0.55
    out = sys.argv[9] if len(sys.argv) > 9 else "sprt_anchor.json"
    cfg = os.environ.get("A3GO_CFG", "libs")
    ch = int(os.environ.get("A3GO_CH", "64")); blk = int(os.environ.get("A3GO_BLK", "6"))
    alpha = beta = 0.05
    workers = min(14, os.cpu_count() or 8)

    upper = math.log((1 - beta) / alpha)      # accept H1 (beats classical)
    lower = math.log(beta / (1 - alpha))       # accept H0 (not a winner)
    w_win = math.log(p1 / p0)
    w_loss = math.log((1 - p1) / (1 - p0))
    print(f"# SPRT {ckpt} cfg={cfg} ch={ch} blk={blk} | H0 p={p0} vs H1 p={p1} "
          f"| boundaries [{lower:.2f}, {upper:.2f}] n_max={n_max}", flush=True)

    t0 = time.time()
    wins = decided = draws = played = 0
    llr = 0.0
    decision = "inconclusive"
    chunk = workers  # one wave of games per pool dispatch; check SPRT between waves
    g = 0
    with mp.Pool(workers) as pool:
        while decided < n_max:
            args = [(g + k, ckpt, n, net_sims, cls_playouts, cls_cap, ch, blk, cfg)
                    for k in range(chunk)]
            g += chunk
            for net_is_black, winner, diff in pool.map(_play_one, args):
                played += 1
                if winner == "draw":
                    draws += 1
                    continue
                decided += 1
                net_won = (winner == "black") == net_is_black
                if net_won:
                    wins += 1; llr += w_win
                else:
                    llr += w_loss
            p, lo, hi = wilson(wins, decided)
            print(f"  decided={decided:3d} wins={wins:3d} wr={p:.3f} "
                  f"llr={llr:+.2f}  ({time.time()-t0:.0f}s)", flush=True)
            if llr >= upper:
                decision = "beats_classical"; break
            if llr <= lower:
                decision = "not_a_winner"; break

    p, lo, hi = wilson(wins, decided)
    res = {"experiment": "EVAL-1 SPRT-bounded net-vs-classical anchor",
           "ckpt": ckpt, "cfg": cfg, "channels": ch, "blocks": blk, "boardSize": n,
           "net_sims": net_sims, "classical_playouts": cls_playouts, "classical_rollout_cap": cls_cap,
           "sprt": {"p0": p0, "p1": p1, "alpha": alpha, "beta": beta,
                    "boundary_lo": round(lower, 3), "boundary_hi": round(upper, 3),
                    "llr": round(llr, 3), "n_max": n_max},
           "decision": decision, "played": played, "decided": decided, "draws": draws,
           "net_wins": wins, "net_winrate": p, "winrate_ci95": [lo, hi],
           "beats_classical_decisively": decision == "beats_classical",
           "eval_secs": round(time.time() - t0, 1),
           "games_per_sec": round(played / max(1e-9, time.time() - t0), 3)}
    print(json.dumps(res, indent=2), flush=True)
    json.dump(res, open(out, "w"), indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
