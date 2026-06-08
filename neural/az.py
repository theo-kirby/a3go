"""AlphaZero-style PUCT MCTS guided by the policy/value net, plus self-play game
generation and evaluation helpers, over the Python 3D-Go engine."""

from __future__ import annotations

import math
import random

import numpy as np
import torch

from a3go_engine import Board, other
from net import encode


def n_actions(n: int) -> int:
    return n * n * n + 1


def action_to_move(a: int, n: int):
    if a == n * n * n:
        return "pass"
    x = a // (n * n)
    r = a % (n * n)
    return (x, r // n, r % n)


def move_to_action(mv, n: int) -> int:
    if mv == "pass":
        return n * n * n
    x, y, z = mv
    return x * n * n + y * n + z


def legal_action_mask(board: Board) -> np.ndarray:
    # INFRA-2: take the engine's native (n,n,n) legal mask and flatten it (C-order
    # index x*n*n + y*n + z) instead of rebuilding it cell-by-cell from a tuple
    # list — this was the dominant MCTS cost on 7^3 (bench_infra1).
    n = board.w
    mask = np.zeros(n_actions(n), dtype=bool)
    mask[: n * n * n] = board.legal_move_mask().reshape(-1)
    mask[n * n * n] = True  # pass always legal
    return mask


class _Node:
    __slots__ = ("board", "passes", "to_move", "P", "N", "W", "children", "mask", "is_terminal")

    def __init__(self, board: Board, passes: int):
        self.board = board
        self.passes = passes
        self.to_move = board.player
        self.is_terminal = passes >= 2
        self.P = None  # priors (after expansion)
        self.N = None  # visit counts per action
        self.W = None  # total value per action
        self.children: dict[int, _Node] = {}
        self.mask = None


class MCTS:
    def __init__(self, net, device, sims: int = 48, c_puct: float = 1.5, seed: int = 0):
        self.net = net
        self.device = device
        self.sims = sims
        self.c_puct = c_puct
        self.nprng = np.random.default_rng(seed)

    def _eval(self, board: Board):
        x = torch.from_numpy(encode(board)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits, v = self.net(x)
        return logits[0].float().cpu().numpy(), float(v.item())

    def _terminal_value(self, board: Board) -> float:
        """Value for the side to move at a 2-pass terminal node."""
        s = board.score_tromp_taylor()
        if s["winner"] == "draw":
            return 0.0
        winner = 1 if s["winner"] == "black" else 2
        return 1.0 if winner == board.player else -1.0

    def _expand(self, node: _Node) -> float:
        """Expand node with net priors; return value (for node.to_move)."""
        if node.is_terminal:
            return self._terminal_value(node.board)
        logits, v = self._eval(node.board)
        mask = legal_action_mask(node.board)
        node.mask = mask
        logits = np.where(mask, logits, -1e9)
        logits -= logits.max()
        p = np.exp(logits)
        p *= mask
        s = p.sum()
        node.P = p / s if s > 0 else mask / mask.sum()
        node.N = np.zeros_like(node.P)
        node.W = np.zeros_like(node.P)
        return v

    def _select(self, node: _Node) -> int:
        total = node.N.sum()
        sq = math.sqrt(total + 1e-8)
        q = np.where(node.N > 0, node.W / np.maximum(node.N, 1), 0.0)
        u = self.c_puct * node.P * sq / (1 + node.N)
        scores = np.where(node.mask, q + u, -1e18)
        return int(scores.argmax())

    def _child_board(self, node: _Node, a: int):
        n = node.board.w
        b = node.board.clone()
        mv = action_to_move(a, n)
        if mv == "pass":
            b.pass_move()
            return b, node.passes + 1
        b.play(*mv)
        return b, 0

    def _simulate(self, node: _Node) -> float:
        if node.is_terminal:
            return self._terminal_value(node.board)
        if node.P is None:
            return self._expand(node)
        a = self._select(node)
        child = node.children.get(a)
        if child is None:
            cb, cp = self._child_board(node, a)
            child = _Node(cb, cp)
            node.children[a] = child
            v_child = self._expand(child)
        else:
            v_child = self._simulate(child)
        # child value is from child.to_move's perspective = opponent of node.to_move
        v = -v_child
        node.N[a] += 1
        node.W[a] += v
        return v

    def policy(self, board: Board, passes: int, temp: float = 1.0,
               root_noise: float = 0.0, dir_alpha: float = 0.5) -> np.ndarray:
        root = _Node(board.clone(), passes)
        self._expand(root)
        if root_noise > 0.0 and root.P is not None:
            legal = root.mask
            k = int(legal.sum())
            if k > 0:
                noise = np.zeros_like(root.P)
                noise[legal] = self.nprng.dirichlet([dir_alpha] * k)
                root.P = (1.0 - root_noise) * root.P + root_noise * noise
        for _ in range(self.sims):
            self._simulate(root)
        counts = root.N
        if temp <= 1e-3:
            pi = np.zeros_like(counts)
            pi[int(counts.argmax())] = 1.0
            return pi
        c = counts ** (1.0 / temp)
        s = c.sum()
        return c / s if s > 0 else legal_action_mask(board) / legal_action_mask(board).sum()


def self_play_game(mcts: MCTS, n: int, komi: float = 0.0, max_moves: int | None = None,
                   temp_moves: int = 8, rng: random.Random | None = None):
    """Return (examples, winner). examples = list of (encoded_state, pi, to_move)."""
    rng = rng or random.Random()
    board = Board(n, komi=komi)
    passes = 0
    examples = []
    max_moves = max_moves or n * n * n * 2
    for t in range(max_moves):
        temp = 1.0 if t < temp_moves else 1e-3
        pi = mcts.policy(board, passes, temp=temp, root_noise=0.25)
        examples.append((encode(board), pi.astype(np.float32), board.player))
        a = rng.choices(range(len(pi)), weights=pi)[0] if temp > 1e-3 else int(pi.argmax())
        mv = action_to_move(a, n)
        if mv == "pass":
            board.pass_move()
            passes += 1
            if passes >= 2:
                break
        else:
            board.play(*mv)
            passes = 0
    s = board.score_tromp_taylor()
    winner = 0 if s["winner"] == "draw" else (1 if s["winner"] == "black" else 2)
    data = []
    for enc, pi, player in examples:
        if winner == 0:
            z = 0.0
        else:
            z = 1.0 if winner == player else -1.0
        data.append((enc, pi, np.float32(z)))
    return data, winner


def _random_move(board: Board, passes: int, rng: random.Random):
    moves = board.legal_moves()
    if not moves:
        return "pass"
    return rng.choice(moves)


def play_match_vs_random(mcts: MCTS, n: int, games: int, komi: float = 0.0,
                         seed: int = 0) -> float:
    """Net (MCTS, temp~0) vs uniform-random, color-balanced. Returns net win-rate."""
    rng = random.Random(seed)
    net_wins = 0
    decided = 0
    for g in range(games):
        net_is_black = g % 2 == 0
        board = Board(n, komi=komi)
        passes = 0
        for _ in range(n * n * n * 2):
            net_turn = (board.player == 1) == net_is_black
            if net_turn:
                pi = mcts.policy(board, passes, temp=1e-3)
                a = int(pi.argmax())
                mv = action_to_move(a, n)
            else:
                mv = _random_move(board, passes, rng)
            if mv == "pass":
                board.pass_move()
                passes += 1
                if passes >= 2:
                    break
            else:
                board.play(*mv)
                passes = 0
        s = board.score_tromp_taylor()
        if s["winner"] == "draw":
            continue
        decided += 1
        net_won = (s["winner"] == "black") == net_is_black
        if net_won:
            net_wins += 1
    return net_wins / max(1, decided)


def play_match_net_vs_net(a: MCTS, b: MCTS, n: int, games: int, komi: float = 0.0,
                          temp: float = 0.3, seed: int = 0) -> float:
    """A vs B, color-balanced. Low-temp *sampling* (not argmax) so color-balanced
    games are not degenerate-deterministic. Returns A win-rate over decided games."""
    rng = random.Random(seed)
    a_wins = 0
    decided = 0
    for g in range(games):
        a_is_black = g % 2 == 0
        board = Board(n, komi=komi)
        passes = 0
        for _ in range(n * n * n * 2):
            mcts = a if ((board.player == 1) == a_is_black) else b
            pi = mcts.policy(board, passes, temp=temp)
            mv = action_to_move(rng.choices(range(len(pi)), weights=pi)[0], n)
            if mv == "pass":
                board.pass_move()
                passes += 1
                if passes >= 2:
                    break
            else:
                board.play(*mv)
                passes = 0
        s = board.score_tromp_taylor()
        if s["winner"] == "draw":
            continue
        decided += 1
        if (s["winner"] == "black") == a_is_black:
            a_wins += 1
    return a_wins / max(1, decided)
