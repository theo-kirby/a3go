"""M5 — batched / game-parallel MCTS self-play and evaluation.

The batch-1 bottleneck (az.MCTS): one GPU forward per tree-node expansion, so the
RTX 5090 idle-waits on Python (measured ~0.05 self-play games/s on 4^3). Here we
run many independent game-trees in lockstep: every simulation round each live tree
descends to exactly one leaf, and ALL leaves needing evaluation across all trees
are evaluated in a SINGLE batched forward pass. Microbench: batch=256 is ~210x
cheaper per position than batch=1, so the GPU is no longer the wall.

Trees are independent (one per game), so within a round each tree contributes at
most one leaf and there is no in-tree leaf collision — no virtual loss needed.

Reuses the engine + helpers from az.py; same PUCT, same priors, same backup sign
convention (value backed up alternates sign each ply).
"""
from __future__ import annotations

import random
import numpy as np
import torch

from a3go_engine import Board
from net import encode
from az import _Node, action_to_move, legal_action_mask, n_actions


class BatchedMCTS:
    def __init__(self, net, device, sims: int = 48, c_puct: float = 1.5, seed: int = 0):
        self.net = net
        self.device = device
        self.sims = sims
        self.c_puct = c_puct
        self.nprng = np.random.default_rng(seed)

    # ---- batched network eval ------------------------------------------------
    def _eval_batch(self, boards):
        if not boards:
            return None, None
        X = torch.from_numpy(np.stack([encode(b) for b in boards])).to(self.device)
        with torch.no_grad():
            logits, v = self.net(X)
        return logits.float().cpu().numpy(), v.float().cpu().numpy()

    # ---- node helpers --------------------------------------------------------
    @staticmethod
    def _terminal_value(board: Board) -> float:
        s = board.score_tromp_taylor()
        if s["winner"] == "draw":
            return 0.0
        winner = 1 if s["winner"] == "black" else 2
        return 1.0 if winner == board.player else -1.0

    @staticmethod
    def _set_priors(node: _Node, logits: np.ndarray):
        mask = legal_action_mask(node.board)
        node.mask = mask
        lg = np.where(mask, logits, -1e9)
        lg = lg - lg.max()
        p = np.exp(lg) * mask
        s = p.sum()
        node.P = p / s if s > 0 else mask / mask.sum()
        node.N = np.zeros_like(node.P)
        node.W = np.zeros_like(node.P)

    def _select(self, node: _Node) -> int:
        total = node.N.sum()
        sq = np.sqrt(total + 1e-8)
        q = np.where(node.N > 0, node.W / np.maximum(node.N, 1), 0.0)
        u = self.c_puct * node.P * sq / (1 + node.N)
        scores = np.where(node.mask, q + u, -1e18)
        return int(scores.argmax())

    @staticmethod
    def _child_board(node: _Node, a: int):
        n = node.board.w
        b = node.board.clone()
        mv = action_to_move(a, n)
        if mv == "pass":
            b.pass_move()
            return b, node.passes + 1
        b.play(*mv)
        return b, 0

    def _descend(self, root: _Node):
        """Descend by PUCT to a leaf. Returns (path, leaf, needs_eval).
        path = list of (node, action). needs_eval True if leaf is unexpanded
        non-terminal (must batch-eval then expand)."""
        node = root
        path = []
        while True:
            if node.is_terminal:
                return path, node, False
            if node.P is None:
                return path, node, True
            a = self._select(node)
            path.append((node, a))
            child = node.children.get(a)
            if child is None:
                cb, cp = self._child_board(node, a)
                child = _Node(cb, cp)
                node.children[a] = child
                if child.is_terminal:
                    return path, child, False
                return path, child, True
            node = child

    @staticmethod
    def _backup(path, leaf_value: float):
        v = leaf_value
        for node, a in reversed(path):
            v = -v
            node.N[a] += 1
            node.W[a] += v

    # ---- the core: run sims for a batch of roots, return visit policies ------
    def run_policies(self, boards, passes_list, temps, root_noise: float = 0.0,
                     dir_alpha: float = 0.5):
        """boards/passes_list: parallel lists for B live games. temps: per-game
        temperature. Returns list of pi (visit-count policies)."""
        B = len(boards)
        roots = [_Node(b.clone(), p) for b, p in zip(boards, passes_list)]
        # Expand all roots in one batched eval (skip terminals).
        idx = [i for i, r in enumerate(roots) if not r.is_terminal]
        lg, _ = self._eval_batch([roots[i].board for i in idx])
        for k, i in enumerate(idx):
            self._set_priors(roots[i], lg[k])
        if root_noise > 0.0:
            for i in idx:
                r = roots[i]
                legal = r.mask
                kk = int(legal.sum())
                if kk > 0:
                    noise = np.zeros_like(r.P)
                    noise[legal] = self.nprng.dirichlet([dir_alpha] * kk)
                    r.P = (1.0 - root_noise) * r.P + root_noise * noise

        for _ in range(self.sims):
            pending = []  # (game_index, path, leaf)
            eval_boards = []
            for gi, root in enumerate(roots):
                if root.is_terminal:
                    continue
                path, leaf, needs = self._descend(root)
                if needs:
                    pending.append((gi, path, leaf))
                    eval_boards.append(leaf.board)
                else:
                    self._backup(path, self._terminal_value(leaf.board))
            if eval_boards:
                lg, v = self._eval_batch(eval_boards)
                for k, (gi, path, leaf) in enumerate(pending):
                    self._set_priors(leaf, lg[k])
                    self._backup(path, float(v[k]))

        pis = []
        for gi, root in enumerate(roots):
            if root.is_terminal or root.N is None:
                a = n_actions(boards[gi].w) - 1  # pass
                pi = np.zeros(n_actions(boards[gi].w), dtype=np.float32)
                pi[a] = 1.0
                pis.append(pi)
                continue
            counts = root.N
            t = temps[gi]
            if t <= 1e-3:
                pi = np.zeros_like(counts)
                pi[int(counts.argmax())] = 1.0
            else:
                c = counts ** (1.0 / t)
                s = c.sum()
                pi = c / s if s > 0 else root.mask / root.mask.sum()
            pis.append(pi.astype(np.float32))
        return pis


def self_play_batch(mcts: BatchedMCTS, n: int, num_games: int, komi: float = 0.0,
                    temp_moves: int = 8, max_moves: int | None = None,
                    seed: int = 0, root_noise: float = 0.25):
    """Run num_games self-play games in lockstep (single batched eval per sim
    round across all live games). Returns (examples, winners).
    examples = list of (encoded_state, pi float32, z float32)."""
    max_moves = max_moves or n * n * n * 2
    rng = random.Random(seed)
    boards = [Board(n, komi=komi) for _ in range(num_games)]
    passes = [0] * num_games
    done = [False] * num_games
    # per-game list of (encoded, pi, player)
    game_examples = [[] for _ in range(num_games)]

    for t in range(max_moves):
        live = [i for i in range(num_games) if not done[i]]
        if not live:
            break
        temp = 1.0 if t < temp_moves else 1e-3
        pis = mcts.run_policies([boards[i] for i in live], [passes[i] for i in live],
                                [temp] * len(live), root_noise=root_noise)
        for k, i in enumerate(live):
            pi = pis[k]
            game_examples[i].append((encode(boards[i]), pi, boards[i].player))
            if temp > 1e-3:
                a = rng.choices(range(len(pi)), weights=pi)[0]
            else:
                a = int(pi.argmax())
            mv = action_to_move(a, n)
            if mv == "pass":
                boards[i].pass_move()
                passes[i] += 1
                if passes[i] >= 2:
                    done[i] = True
            else:
                boards[i].play(*mv)
                passes[i] = 0

    examples = []
    winners = []
    for i in range(num_games):
        s = boards[i].score_tromp_taylor()
        winner = 0 if s["winner"] == "draw" else (1 if s["winner"] == "black" else 2)
        winners.append(winner)
        for enc, pi, player in game_examples[i]:
            z = 0.0 if winner == 0 else (1.0 if winner == player else -1.0)
            examples.append((enc, pi, np.float32(z)))
    return examples, winners


def _legal_random_move(board: Board, rng: random.Random):
    moves = board.legal_moves()
    return rng.choice(moves) if moves else "pass"


def match_vs_random_batched(mcts: BatchedMCTS, n: int, games: int, komi: float = 0.0,
                            seed: int = 0, temp: float = 1e-3) -> float:
    """Net (batched MCTS, argmax) vs uniform-random, color-balanced, in lockstep.
    Returns net win-rate over decided games."""
    rng = random.Random(seed)
    boards = [Board(n, komi=komi) for _ in range(games)]
    passes = [0] * games
    done = [False] * games
    net_is_black = [g % 2 == 0 for g in range(games)]
    max_moves = n * n * n * 2
    for _ in range(max_moves):
        # games where it's the NET's turn and not done
        net_turn = [i for i in range(games) if not done[i]
                    and ((boards[i].player == 1) == net_is_black[i])]
        rnd_turn = [i for i in range(games) if not done[i]
                    and ((boards[i].player == 1) != net_is_black[i])]
        if not net_turn and not rnd_turn:
            break
        if net_turn:
            pis = mcts.run_policies([boards[i] for i in net_turn],
                                    [passes[i] for i in net_turn],
                                    [temp] * len(net_turn))
            for k, i in enumerate(net_turn):
                a = int(pis[k].argmax())
                _apply_action(boards[i], a, n, passes, done, i)
        for i in rnd_turn:
            mv = _legal_random_move(boards[i], rng)
            _apply_move(boards[i], mv, passes, done, i)
    return _winrate(boards, net_is_black)


def match_net_vs_net_batched(a: BatchedMCTS, b: BatchedMCTS, n: int, games: int,
                             komi: float = 0.0, temp: float = 0.3, seed: int = 0) -> float:
    """A vs B color-balanced, lockstep, low-temp sampling. Returns A win-rate."""
    rng = random.Random(seed)
    boards = [Board(n, komi=komi) for _ in range(games)]
    passes = [0] * games
    done = [False] * games
    a_is_black = [g % 2 == 0 for g in range(games)]
    max_moves = n * n * n * 2
    for _ in range(max_moves):
        a_turn = [i for i in range(games) if not done[i]
                  and ((boards[i].player == 1) == a_is_black[i])]
        b_turn = [i for i in range(games) if not done[i]
                  and ((boards[i].player == 1) != a_is_black[i])]
        if not a_turn and not b_turn:
            break
        for player, turn in ((a, a_turn), (b, b_turn)):
            if not turn:
                continue
            pis = player.run_policies([boards[i] for i in turn],
                                      [passes[i] for i in turn], [temp] * len(turn))
            for k, i in enumerate(turn):
                act = rng.choices(range(len(pis[k])), weights=pis[k])[0]
                _apply_action(boards[i], act, n, passes, done, i)
    return _winrate(boards, a_is_black)


def _apply_action(board, a, n, passes, done, i):
    _apply_move(board, action_to_move(a, n), passes, done, i)


def _apply_move(board, mv, passes, done, i):
    if mv == "pass":
        board.pass_move()
        passes[i] += 1
        if passes[i] >= 2:
            done[i] = True
    else:
        board.play(*mv)
        passes[i] = 0


def _winrate(boards, focal_is_black):
    wins = decided = 0
    for i, b in enumerate(boards):
        s = b.score_tromp_taylor()
        if s["winner"] == "draw":
            continue
        decided += 1
        if (s["winner"] == "black") == focal_is_black[i]:
            wins += 1
    return wins / max(1, decided)
