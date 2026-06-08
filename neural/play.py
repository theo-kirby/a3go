"""TOOL-2 — human-playable 3D-Go CLI vs any agent (net / classical / random).

Play in the terminal: the board prints as z-slice layers with coordinates, you
enter `x y z` (or `pass`), and the engine validates. Against a net you see its top
policy moves and value estimate each turn (what the agent is "thinking"). Optional
PNG render per move (via viz.py) and a move log for capturing games as artifacts.

    uv run python play.py --n 4 --vs net@256          # play Black vs the net
    uv run python play.py --n 4 --vs classical@128 --white
    uv run python play.py --n 4 --vs net@128 --auto 1  # agent-vs-agent showcase
    uv run python play.py --n 4 --vs net@256 --auto 1 --render   # + PNG per move
"""
from __future__ import annotations
import os, sys, argparse, json
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np
import torch

from a3go_engine import Board, BLACK, WHITE
from az import action_to_move, move_to_action, n_actions
from batched_az import BatchedMCTS
from classical_mcts import ClassicalMCTS

GLYPH = {0: ".", BLACK: "#", WHITE: "O"}


def text_board(grid):
    w, h, d = grid.shape
    lines = []
    header = "   ".join(f"z={z}" + " " * (2 * w - 2) for z in range(d))
    lines.append("    " + header)
    for y in range(h - 1, -1, -1):
        row = []
        for z in range(d):
            cells = " ".join(GLYPH[int(grid[x, y, z])] for x in range(w))
            row.append(cells)
        lines.append(f"y{y}  " + "   ".join(row))
    lines.append("     " + "   ".join(" ".join(str(x) for x in range(w)) + "    " for _ in range(d)))
    return "\n".join(lines)


class NetPlayer:
    def __init__(self, ckpt, n, sims, device):
        from arch_util import load_net
        self.net, _, _ = load_net(ckpt, n, device)
        self.mcts = BatchedMCTS(self.net, device, sims=sims, seed=0)
        self.device = device; self.n = n
    def readout(self, board):
        from net import encode
        X = torch.from_numpy(encode(board)[None]).to(self.device)
        with torch.no_grad():
            logits, v = self.net(X)
        p = torch.softmax(logits[0], 0).cpu().numpy()
        order = np.argsort(-p)[:5]
        tops = []
        for a in order:
            mv = action_to_move(int(a), self.n)
            tops.append((mv, float(p[a])))
        return float(v[0]), tops
    def move(self, board, passes):
        pi = self.mcts.run_policies([board], [passes], [1e-3])[0]
        return action_to_move(int(pi.argmax()), self.n)


class ClassicalPlayer:
    def __init__(self, playouts, seed=0):
        self.m = ClassicalMCTS(playouts=playouts, seed=seed)
    def readout(self, board):
        return None, []
    def move(self, board, passes):
        return self.m.select_move(board, passes)


def make_agent(spec, n, device):
    kind, _, arg = spec.partition("@")
    if kind == "net":
        ck = {4: "best_distill_big_4cubed.pt", 5: "best_distill5strong_5cubed.pt",
              7: "best_distill7_7cubed.pt"}[n]
        return NetPlayer(ck, n, int(arg or 128), device)
    if kind == "classical":
        return ClassicalPlayer(int(arg or 128))
    raise SystemExit(f"unknown agent {spec}")


def apply_move(board, mv, passes):
    if mv == "pass":
        board.pass_move(); return passes + 1
    board.play(*mv); return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--vs", default="net@128")
    ap.add_argument("--white", action="store_true", help="human plays White (agent moves first)")
    ap.add_argument("--auto", type=int, default=0, help="agent-vs-agent: run N showcase games, no human")
    ap.add_argument("--render", action="store_true", help="save a PNG per move (figures/play_*.png)")
    args = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.set_num_threads(1)
    n = args.n
    agent = make_agent(args.vs, n, device)

    if args.auto:
        opp = make_agent(args.vs, n, device)  # mirror agent
        for g in range(args.auto):
            b = Board(n); passes = 0; log = []
            players = {BLACK: agent, WHITE: opp}
            ply = 0
            while ply < n * n * n * 2 and passes < 2:
                cur = players[b.player]
                mv = cur.move(b, passes)
                log.append({"ply": ply, "player": int(b.player), "move": mv if mv == "pass" else list(mv)})
                passes = apply_move(b, mv, passes)
                ply += 1
                if args.render:
                    from viz import render_slices
                    render_slices(b.grid, f"figures/play_auto{g}_ply{ply:03d}.png",
                                  player=b.player, last_move=None if mv == "pass" else mv,
                                  title=f"auto game {g}, ply {ply}")
            s = b.score_tromp_taylor()
            print(f"auto game {g}: {s['winner']} (diff {s['diff']:+.0f}), {ply} plies", flush=True)
            json.dump({"n": n, "vs": args.vs, "winner": s["winner"], "diff": s["diff"], "moves": log},
                      open(f"play_auto_{n}cubed_g{g}.json", "w"), indent=2)
            if args.render:
                from viz import render_slices
                render_slices(b.grid, f"figures/play_auto{g}_final.png", player=b.player,
                              title=f"auto game {g} FINAL — {s['winner']} {s['diff']:+.0f}")
        return

    # interactive
    human = WHITE if args.white else BLACK
    b = Board(n); passes = 0
    print(f"You are {'White (O)' if human == WHITE else 'Black (#)'} vs {args.vs} on {n}^3. "
          f"Enter moves as 'x y z' or 'pass'.")
    while passes < 2:
        print("\n" + text_board(b.grid))
        if b.player == human:
            raw = input(f"{'White' if human==WHITE else 'Black'} move > ").strip()
            if raw == "pass":
                passes = apply_move(b, "pass", passes); continue
            try:
                x, y, z = map(int, raw.split())
                b.play(x, y, z); passes = 0
            except Exception as e:
                print("  illegal/again:", e); continue
        else:
            v, tops = agent.readout(b)
            if v is not None:
                print(f"  [agent value={v:+.2f}; top: " +
                      ", ".join(f"{m}:{p:.2f}" for m, p in tops) + "]")
            mv = agent.move(b, passes)
            print(f"  agent plays {mv}")
            passes = apply_move(b, mv, passes)
    s = b.score_tromp_taylor()
    print("\n" + text_board(b.grid))
    print(f"\nGAME OVER: {s['winner']} wins (area diff {s['diff']:+.0f})")


if __name__ == "__main__":
    main()
