"""ALGO-1 — Gumbel AlphaZero root action selection (Danihelka et al. 2022).

Standard PUCT needs many sims for a good move; Gumbel AlphaZero guarantees a
policy-IMPROVEMENT action with very few sims via Gumbel-top-k sampling without
replacement + Sequential Halving at the root (PUCT inside the tree). Since sims
are the binding currency on big boards, this multiplies strength-per-sim and
removes the hand-tuned Dirichlet noise.

This is a single-tree implementation (batch-1 net forwards) reusing the engine +
node machinery from az.py; on small boards at the LOW sim budgets where Gumbel
matters, batch-1 on GPU is cheap. The A/B vs PUCT is in ab_gumbel.py.
"""
from __future__ import annotations
import math
import numpy as np
import torch

from a3go_engine import Board
from net import encode
from az import _Node, action_to_move, legal_action_mask, n_actions

C_VISIT = 50.0
C_SCALE = 1.0


class GumbelMCTS:
    def __init__(self, net, device, sims=16, max_considered=16, c_puct=1.5, seed=0):
        self.net = net
        self.device = device
        self.sims = sims
        self.max_considered = max_considered
        self.c_puct = c_puct
        self.rng = np.random.default_rng(seed)

    def _eval(self, board):
        X = torch.from_numpy(encode(board)[None]).to(self.device)
        with torch.no_grad():
            logits, v = self.net(X)
        return logits[0].float().cpu().numpy(), float(v[0])

    def _set_priors(self, node, logits):
        mask = legal_action_mask(node.board)
        node.mask = mask
        lg = np.where(mask, logits, -1e9)
        lg = lg - lg.max()
        p = np.exp(lg) * mask
        s = p.sum()
        node.P = p / s if s > 0 else mask / mask.sum()
        node.N = np.zeros_like(node.P)
        node.W = np.zeros_like(node.P)

    def _child_board(self, node, a):
        n = node.board.w
        b = node.board.clone()
        mv = action_to_move(a, n)
        if mv == "pass":
            b.pass_move(); return b, node.passes + 1
        b.play(*mv); return b, 0

    # PUCT simulation within a subtree rooted at `node`; returns leaf value from
    # `node`'s side-to-move perspective.
    def _simulate(self, node):
        if node.is_terminal:
            return self._terminal_value(node.board)
        if node.P is None:
            logits, v = self._eval(node.board)
            self._set_priors(node, logits)
            return v
        total = node.N.sum()
        sq = math.sqrt(total + 1e-8)
        q = np.where(node.N > 0, node.W / np.maximum(node.N, 1), 0.0)
        u = self.c_puct * node.P * sq / (1 + node.N)
        scores = np.where(node.mask, q + u, -1e18)
        a = int(scores.argmax())
        child = node.children.get(a)
        if child is None:
            cb, cp = self._child_board(node, a)
            child = _Node(cb, cp); node.children[a] = child
        v_child = self._simulate(child)
        v = -v_child
        node.N[a] += 1
        node.W[a] += v
        return v

    @staticmethod
    def _terminal_value(board):
        s = board.score_tromp_taylor()
        if s["winner"] == "draw":
            return 0.0
        winner = 1 if s["winner"] == "black" else 2
        return 1.0 if winner == board.player else -1.0

    def select(self, board, passes, return_policy=False):
        """Run Gumbel + Sequential Halving at the root; return the chosen action
        (and, optionally, the improved policy over actions)."""
        root = _Node(board.clone(), passes)
        if root.is_terminal:
            a = n_actions(board.w) - 1
            return (a, None) if return_policy else a
        logits, _ = self._eval(root.board)
        self._set_priors(root, logits)
        legal = np.where(root.mask)[0]
        if len(legal) == 1:
            a = int(legal[0])
            return (a, None) if return_policy else a

        # raw policy logits (pre-softmax) restricted to legal actions
        raw = logits.copy()
        g = self.rng.gumbel(size=raw.shape)
        score0 = raw + g
        m = int(min(self.max_considered, len(legal)))
        # initial top-m legal actions by logit+gumbel
        cand = legal[np.argsort(-score0[legal])[:m]]

        # per-candidate child + value accumulator
        child = {}
        qsum = {a: 0.0 for a in cand}
        qn = {a: 0 for a in cand}
        for a in cand:
            cb, cp = self._child_board(root, int(a))
            child[a] = _Node(cb, cp)

        phases = max(1, int(math.ceil(math.log2(m))))
        budget = self.sims
        cur = list(cand)
        used = 0
        while len(cur) > 1 and used < budget:
            per = max(1, (budget - used) // (phases * max(1, len(cur))))
            for a in cur:
                for _ in range(per):
                    if used >= budget:
                        break
                    ch = child[a]
                    if ch.is_terminal:
                        vc = self._terminal_value(ch.board)
                    else:
                        vc = self._simulate(ch)
                    # value of action a for the ROOT player = -value(child to move)
                    qsum[a] += -vc; qn[a] += 1; used += 1
            # rank by logit + gumbel + sigma(qhat); keep top half
            maxn = max(qn.values()) if qn else 0
            def rank(a):
                qhat = qsum[a] / qn[a] if qn[a] > 0 else 0.0
                return raw[a] + g[a] + (C_VISIT + maxn) * C_SCALE * qhat
            cur = sorted(cur, key=rank, reverse=True)[:max(1, len(cur) // 2)]
            phases -= 1
            if phases <= 0:
                phases = 1
        maxn = max(qn.values()) if qn else 0
        def final_rank(a):
            qhat = qsum[a] / qn[a] if qn[a] > 0 else 0.0
            return raw[a] + g[a] + (C_VISIT + maxn) * C_SCALE * qhat
        best = max(cur, key=final_rank)
        best = int(best)
        if not return_policy:
            return best
        # improved policy = softmax over completed Q for all considered actions
        pol = np.zeros(n_actions(board.w), dtype=np.float32)
        for a in cand:
            qhat = qsum[a] / qn[a] if qn[a] > 0 else 0.0
            pol[a] = raw[a] + (C_VISIT + maxn) * C_SCALE * qhat
        mask = root.mask
        lg = np.where(mask, pol, -1e9); lg -= lg.max()
        p = np.exp(lg) * mask; p /= p.sum()
        return best, p
