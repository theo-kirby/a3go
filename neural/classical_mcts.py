"""Classical (non-neural) UCT MCTS with eye-avoiding random rollouts over the
Python engine — the fixed-strength baseline the success bar names (mirrors the
TS MCTSAgent). Used to test whether the trained neural net beats classical MCTS
(2nd leg of the baseline bar), apples-to-apples in one engine/process.
"""
from __future__ import annotations
import math
import random

from a3go_engine import Board, EMPTY, other
from az import action_to_move  # noqa: F401 (kept for parity of move encoding)


def _simple_eye(board: Board, x, y, z, color) -> bool:
    nb = []
    for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        nx, ny, nz = x + dx, y + dy, z + dz
        if 0 <= nx < board.w and 0 <= ny < board.h and 0 <= nz < board.d:
            nb.append(board.grid[nx, ny, nz])
    return bool(nb) and all(v == color for v in nb)


def _rollout_moves(board: Board, rng: random.Random):
    """Legal moves minus the player's own simple eyes (don't fill own eyes)."""
    color = board.player
    mv = [m for m in board.legal_moves() if not _simple_eye(board, m[0], m[1], m[2], color)]
    return mv


class _CNode:
    __slots__ = ("board", "passes", "untried", "children", "N", "Q", "move", "parent")

    def __init__(self, board, passes, move=None, parent=None):
        self.board = board
        self.passes = passes
        self.move = move
        self.parent = parent
        self.children = []
        self.N = 0
        self.Q = 0.0
        self.untried = None  # lazy


class ClassicalMCTS:
    def __init__(self, playouts=128, c=1.4, seed=0, max_rollout=None):
        self.playouts = playouts
        self.c = c
        self.rng = random.Random(seed)
        self.max_rollout = max_rollout

    def _expand_moves(self, node):
        if node.untried is None:
            mv = _rollout_moves(node.board, self.rng)
            mv.append("pass")
            self.rng.shuffle(mv)
            node.untried = mv
        return node.untried

    def _step(self, board, passes, mv):
        b = board.clone()
        if mv == "pass":
            b.pass_move()
            return b, passes + 1
        b.play(*mv)
        return b, 0

    def _rollout(self, board, passes):
        """Fast Monte-Carlo playout: instead of enumerating ALL legal moves each
        step (O(cells) clone+apply per step), pick random empty points and try
        play_fast (capture+suicide, no superko) until one succeeds — O(1-2) ops
        per step since most random empties are legal. Skips own simple eyes."""
        import numpy as np
        b = board.clone()
        p = passes
        cap = self.max_rollout or (b.w * b.h * b.d * 2)
        rr = self.rng
        for _ in range(cap):
            if p >= 2:
                break
            empties = np.argwhere(b.grid == EMPTY)
            if len(empties) == 0:
                b.pass_move(); p += 1; continue
            order = list(range(len(empties)))
            rr.shuffle(order)
            played = False
            color = b.player
            for i in order:
                x, y, z = int(empties[i][0]), int(empties[i][1]), int(empties[i][2])
                if _simple_eye(b, x, y, z, color):
                    continue  # don't fill own eye
                if b.play_fast(x, y, z):
                    played = True; p = 0; break
            if not played:
                b.pass_move(); p += 1
        return b.score_tromp_taylor()

    def _search(self, board: Board, passes: int):
        root = _CNode(board.clone(), passes)
        root_player = board.player
        for _ in range(self.playouts):
            node = root
            # selection
            while True:
                untried = self._expand_moves(node)
                if untried:
                    break
                if not node.children:
                    break
                # UCB1
                logN = math.log(node.N + 1)
                best, bestv = None, -1e18
                for ch in node.children:
                    val = ch.Q / max(ch.N, 1) + self.c * math.sqrt(logN / max(ch.N, 1))
                    if val > bestv:
                        bestv, best = val, ch
                node = best
            # expansion
            untried = self._expand_moves(node)
            if untried:
                mv = untried.pop()
                cb, cp = self._step(node.board, node.passes, mv)
                child = _CNode(cb, cp, move=mv, parent=node)
                node.children.append(child)
                node = child
            # simulation
            s = self._rollout(node.board, node.passes)
            # backprop: reward from root_player's perspective
            if s["winner"] == "draw":
                reward = 0.5
            else:
                reward = 1.0 if (s["winner"] == "black") == (root_player == 1) else 0.0
            while node is not None:
                node.N += 1
                node.Q += reward
                node = node.parent
        return root, root_player

    def select_move(self, board: Board, passes: int):
        root, _ = self._search(board, passes)
        if not root.children:
            return "pass"
        return max(root.children, key=lambda ch: ch.N).move  # most-visited

    def move_and_policy(self, board: Board, passes: int, temp: float = 1.0):
        """Return (sampled_or_argmax_move, visit-count policy vector over n^3+1
        actions) — the distillation target. temp<=1e-3 => argmax."""
        import numpy as np
        from az import move_to_action, action_to_move
        n = board.w
        root, _ = self._search(board, passes)
        pi = np.zeros(n * n * n + 1, dtype=np.float32)
        if not root.children:
            pi[n * n * n] = 1.0
            return "pass", pi
        for ch in root.children:
            pi[move_to_action(ch.move, n)] = ch.N
        if temp <= 1e-3:
            a = int(pi.argmax())
            out = np.zeros_like(pi); out[a] = 1.0
            return action_to_move(a, n), out
        p = pi ** (1.0 / temp)
        s = p.sum()
        pi = p / s if s > 0 else pi
        import random as _r
        a = _r.choices(range(len(pi)), weights=pi)[0]
        return action_to_move(a, n), pi
