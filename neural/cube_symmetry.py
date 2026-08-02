"""SYMM-1 — the order-48 symmetry group of the cube, acting on N^3 board tensors
and on the n^3+1 action vector. 3D Go's full symmetry group is the 48 signed axis
permutations (3! axis orderings x 2^3 sign flips); the 2D analogue (dihedral-8) is
the lever AlphaGo/KataGo use for data augmentation + test-time averaging.

A group element g = (perm, flips): perm is a permutation of axes (0,1,2), flips is
a 3-tuple of bools (reflect that axis after permuting). For cubic boards (n,n,n)
all 48 are board symmetries.

  transform_planes(X, g)  : (C,n,n,n) -> (C,n,n,n) in the g-frame
  inv_transform_grid(A, g): (n,n,n)   -> original frame (undo g)
  action_perm(g, n)       : index map so policy[action_perm] = policy in orig frame

Validated by `_selftest()` (run this file directly): geometry is an exact group
action (compose with inverse = identity) for all 48 elements.
"""
from __future__ import annotations
import itertools
import numpy as np

# All 48 elements as (perm, flips).
GROUP = [(perm, flips)
         for perm in itertools.permutations((0, 1, 2))
         for flips in itertools.product((False, True), repeat=3)]
assert len(GROUP) == 48


def transform_planes(X: np.ndarray, g) -> np.ndarray:
    """Apply g to a (C, n, n, n) plane stack (channel axis 0 untouched)."""
    perm, flips = g
    Y = np.transpose(X, (0,) + tuple(1 + p for p in perm))
    for ax, fl in enumerate(flips):
        if fl:
            Y = np.flip(Y, axis=1 + ax)
    return np.ascontiguousarray(Y)


def _transform_grid(A: np.ndarray, g) -> np.ndarray:
    """Apply g to a (n,n,n) scalar grid (same action as on planes, no channel)."""
    perm, flips = g
    Y = np.transpose(A, perm)
    for ax, fl in enumerate(flips):
        if fl:
            Y = np.flip(Y, axis=ax)
    return np.ascontiguousarray(Y)


def inv_element(g):
    """Inverse group element g^{-1} such that g∘g^{-1} = identity."""
    perm, flips = g
    # If g: y_perm[i] = x[perm[i]] then flip. Build inverse perm + flips.
    inv_perm = [0, 0, 0]
    for i, p in enumerate(perm):
        inv_perm[p] = i
    inv_perm = tuple(inv_perm)
    # flips applied AFTER permute in forward; for inverse, the flip on output axis i
    # corresponds to input axis perm[i]. The inverse first un-flips then un-permutes,
    # which is equivalent to (inv_perm, flips_permuted) where the flip for inverse
    # axis j is the forward flip on output axis inv_perm[j].
    inv_flips = tuple(flips[inv_perm[j]] for j in range(3))
    return (inv_perm, inv_flips)


def inv_transform_grid(A: np.ndarray, g) -> np.ndarray:
    """Undo g on a (n,n,n) grid: map a result in the g-frame back to the original."""
    return _transform_grid(A, inv_element(g))


def action_perm(g, n: int) -> np.ndarray:
    """Index array P (len n^3+1) s.t. for a policy `pol` computed in the g-frame,
    `pol[P]` is that policy expressed in the ORIGINAL frame (pass index invariant).
    Built by transforming an arange grid back through g^{-1}."""
    base = np.arange(n * n * n, dtype=np.int64).reshape(n, n, n)
    mapped = inv_transform_grid(base, g).reshape(-1)
    return np.concatenate([mapped, [n * n * n]])  # pass stays last


def _selftest():
    rng = np.random.default_rng(0)
    n = 5
    X = rng.standard_normal((4, n, n, n)).astype(np.float32)
    A = rng.standard_normal((n, n, n)).astype(np.float32)
    ok = True
    for g in GROUP:
        # plane transform then inverse = identity
        Y = transform_planes(X, g)
        Yb = _transform_grid  # alias check uses grid form on each channel
        back = np.stack([inv_transform_grid(Y[c], g) for c in range(X.shape[0])])
        if not np.allclose(back, X):
            ok = False; print("FAIL plane inverse", g); break
        # action_perm consistency: transforming a grid then reading via action_perm
        # recovers identity ordering.
        gA = _transform_grid(A, g)               # A in g-frame
        P = action_perm(g, n)
        recovered = gA.reshape(-1)[P[:-1]]       # express g-frame grid in orig frame
        if not np.allclose(recovered, A.reshape(-1)):
            ok = False; print("FAIL action_perm", g); break
    print("cube_symmetry selftest:", "PASS (48/48)" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _selftest() else 1)
