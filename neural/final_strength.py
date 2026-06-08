"""Clean high-N final strength eval for Q10: final trained net vs uniform-random
and vs the frozen gen-0 (untrained) net, both via MCTS, with Wilson 95% CIs.
Quantifies the rise that the per-gen (noisy, N=32) curve only hinted at."""
from __future__ import annotations
import json, math, sys
import torch
from net import A3GoNet
from batched_az import BatchedMCTS, match_vs_random_batched, match_net_vs_net_batched


def wilson(wins, total, z=1.96):
    if total == 0:
        return (0.0, 0.0, 0.0)
    p = wins / total
    d = 1 + z*z/total
    c = (p + z*z/(2*total)) / d
    h = z*math.sqrt(p*(1-p)/total + z*z/(4*total*total)) / d
    return (round(p, 3), round(max(0, c-h), 3), round(min(1, c+h), 3))


def main():
    n = 4
    games = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    sims = int(sys.argv[2]) if len(sys.argv) > 2 else 48
    device = "cuda" if torch.cuda.is_available() else "cpu"

    final = A3GoNet(n).to(device)
    final.load_state_dict(torch.load("best_batched_4cubed.pt", map_location=device))
    final.eval()
    torch.manual_seed(0)  # match the training run's gen-0 init
    gen0 = A3GoNet(n).to(device); gen0.eval()

    mf = BatchedMCTS(final, device, sims=sims, seed=0)
    m0 = BatchedMCTS(gen0, device, sims=sims, seed=0)

    # vs random (decided games)
    wr_final = match_vs_random_batched(mf, n, games, seed=4242)
    wr_gen0 = match_vs_random_batched(m0, n, games, seed=4242)
    # final vs gen0 head-to-head (low-temp sampling), color-balanced
    wr_h2h = match_net_vs_net_batched(mf, m0, n, games, temp=0.3, seed=77)

    # convert win-rates to approx counts for CI (decided≈games; use games as n)
    res = {
        "experiment": "Q10 final strength (4^3)",
        "ckpt": "best_batched_4cubed.pt", "games_per_match": games, "sims": sims,
        "final_vs_random_winrate": wr_final,
        "gen0_vs_random_winrate": wr_gen0,
        "final_vs_gen0_winrate": wr_h2h,
        "final_vs_random_ci95": list(wilson(round(wr_final*games), games)),
        "final_vs_gen0_ci95": list(wilson(round(wr_h2h*games), games)),
        "beats_random_decisively": wilson(round(wr_final*games), games)[1] > 0.5,
        "beats_gen0_decisively": wilson(round(wr_h2h*games), games)[1] > 0.5,
    }
    print(json.dumps(res, indent=2))
    with open("experiments_q10_final.json", "w") as f:
        json.dump(res, f, indent=2)


if __name__ == "__main__":
    main()
