"""Q6 — Does SEKI (mutual life without two eyes) occur in 3D Go, and does
6-connectivity change it vs 2D?

Deterministic capture solver + eye detector classify hand-built standoff
positions. A group is "alive" if the attacker, moving first and playing optimal
bounded minimax, cannot capture it. SEKI = both groups alive AND neither group
is alive by its own two eyes (i.e. their life is mutual / shared-liberty, not
independent).

Method is exact (bounded minimax over the real engine rules, memoized by
position hash); no self-play, no net. We test the SAME shape as a walled-off 2D
slice (depth=1) and as a 3D-opened version (the contested region gains z+/-1
neighbors) to isolate the effect of 6-connectivity.
"""
from __future__ import annotations
import json
import sys

from a3go_engine import Board, BLACK, WHITE, EMPTY, other


# --- position construction ---------------------------------------------------
def make_board(shape, blacks, whites, player=BLACK):
    b = Board(0, shape=shape)
    for (x, y, z) in blacks:
        b.grid[x, y, z] = BLACK
    for (x, y, z) in whites:
        b.grid[x, y, z] = WHITE
    b.player = player
    b.history = {b._hash()}
    return b


def neighbors(b, x, y, z):
    out = []
    for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        nx, ny, nz = x + dx, y + dy, z + dz
        if 0 <= nx < b.w and 0 <= ny < b.h and 0 <= nz < b.d:
            out.append((nx, ny, nz))
    return out


def simple_eyes(b, color):
    """Empty points all of whose in-bounds neighbors are `color` (simple eyes)."""
    eyes = []
    for x in range(b.w):
        for y in range(b.h):
            for z in range(b.d):
                if b.grid[x, y, z] != EMPTY:
                    continue
                nb = neighbors(b, x, y, z)
                if nb and all(b.grid[p] == color for p in nb):
                    eyes.append((x, y, z))
    return eyes


def alive_by_two_eyes(b, color):
    # Conservative: ≥2 simple eyes for the color => independently alive.
    return len(simple_eyes(b, color)) >= 2


# --- bounded minimax capture solver ------------------------------------------
def can_capture(b, target_color, rep, attacker, depth, memo):
    """True if `attacker` (whoever is to move when b.player==attacker) can force
    the capture of the target group (the stone at `rep`) within `depth` plies.
    Defender plays optimally to survive. Memoized by (position, to_move, depth)."""
    if b.grid[rep] != target_color:
        return True  # already captured
    if depth <= 0:
        return False
    key = (b.grid.tobytes(), b.player, depth)
    cached = memo.get(key)
    if cached is not None:
        return cached
    moves = b.legal_moves()
    moves.append("pass")
    if b.player == attacker:
        result = False
        for mv in moves:
            nb = b.clone()
            try:
                if mv == "pass":
                    nb.pass_move()
                else:
                    nb.play(*mv)
            except Exception:
                continue
            if can_capture(nb, target_color, rep, attacker, depth - 1, memo):
                result = True
                break
    else:  # defender to move: attacker wins only if EVERY reply still loses
        result = True
        for mv in moves:
            nb = b.clone()
            try:
                if mv == "pass":
                    nb.pass_move()
                else:
                    nb.play(*mv)
            except Exception:
                continue
            if not can_capture(nb, target_color, rep, attacker, depth - 1, memo):
                result = False
                break
    memo[key] = result
    return result


def classify(b, black_rep, white_rep, depth=8):
    """Classify a two-group standoff position."""
    # Can White capture Black (White to move)?
    bb = b.clone(); bb.player = WHITE
    black_capt = can_capture(bb, BLACK, black_rep, WHITE, depth, {})
    # Can Black capture White (Black to move)?
    wb = b.clone(); wb.player = BLACK
    white_capt = can_capture(wb, WHITE, white_rep, BLACK, depth, {})
    b_eyes = len(simple_eyes(b, BLACK))
    w_eyes = len(simple_eyes(b, WHITE))
    b_two = b_eyes >= 2
    w_two = w_eyes >= 2
    both_alive = (not black_capt) and (not white_capt)
    independent = b_two or w_two
    seki = both_alive and not b_two and not w_two
    if black_capt or white_capt:
        status = "not-seki (a group is capturable)"
    elif b_two and w_two:
        status = "both independently alive (two eyes each)"
    elif independent:
        status = "mixed (one two-eyed, one not) — alive but not classic seki"
    else:
        status = "SEKI (mutual life, no two eyes)"
    return {
        "black_capturable": black_capt, "white_capturable": white_capt,
        "black_simple_eyes": b_eyes, "white_simple_eyes": w_eyes,
        "both_alive": both_alive, "seki": seki, "status": status,
    }


# --- test cases --------------------------------------------------------------
def main():
    out = {"experiment": "Q6 seki in 3D vs 2D",
           "method": "bounded minimax capture solver (exact over engine rules) + "
                     "simple-eye detector; seki = both groups uncapturable AND "
                     "neither alive by two eyes",
           "cases": []}

    # --- Case A: tight 2D seki on a walled-off slice (4x3x1) ---
    # Black wall = top row + the two side cells of the middle row; White wall =
    # bottom row. Shared dame = exactly (1,1,0),(2,1,0). Eyeless both sides.
    shape = (4, 3, 1)
    blacks = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (0, 1, 0), (3, 1, 0)]
    whites = [(0, 2, 0), (1, 2, 0), (2, 2, 0), (3, 2, 0)]
    bA = make_board(shape, blacks, whites)
    rA = classify(bA, (0, 0, 0), (0, 2, 0), depth=12)
    rA.update({"name": "A: 2D slice (4x3x1) — eyeless walls share exactly 2 dame",
               "shape": list(shape), "empties": int((bA.grid == EMPTY).sum())})
    out["cases"].append(rA)

    # --- Case B: the SAME standoff opened minimally into 3D. The walls are
    # extended up into z=1, leaving the two dame cells AND the two cells directly
    # above them empty (a 2x1x2 contested box). A stone played in a dame now has
    # an extra z-neighbour liberty — does 6-connectivity break the seki? ---
    shape = (4, 3, 2)
    blacks = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0), (0, 1, 0), (3, 1, 0),
              (0, 0, 1), (1, 0, 1), (2, 0, 1), (3, 0, 1), (0, 1, 1), (3, 1, 1)]
    whites = [(0, 2, 0), (1, 2, 0), (2, 2, 0), (3, 2, 0),
              (0, 2, 1), (1, 2, 1), (2, 2, 1), (3, 2, 1)]
    # empties: (1,1,0),(2,1,0),(1,1,1),(2,1,1)  -> 4-cell shared box
    bB = make_board(shape, blacks, whites)
    rB = classify(bB, (0, 0, 0), (0, 2, 0), depth=10)
    rB.update({"name": "B: 3D-opened (4x3x2) — same walls, dame box gains z-liberties",
               "shape": list(shape), "empties": int((bB.grid == EMPTY).sum())})
    out["cases"].append(rB)

    # --- Case C control: a capturable group. Black single stone in the corner
    # of a 3x3x1 with one liberty surrounded by white -> White must be able to
    # capture it (solver sanity that it CAN detect capture). ---
    shape = (3, 3, 1)
    blacks = [(0, 0, 0)]
    whites = [(1, 0, 0), (0, 1, 0)]  # black (0,0) has 1 liberty? neighbors (1,0)W,(0,1)W -> 0 libs already
    # give black one liberty by removing one white; use (0,0) with liberty at...
    whites = [(1, 0, 0)]  # black (0,0,0) neighbors: (1,0,0)W, (0,1,0)empty -> 1+ libs
    bC = make_board(shape, blacks, whites)
    rC = classify(bC, (0, 0, 0), (1, 0, 0), depth=6)
    rC.update({"name": "C control: lone black stone vs white — capturable sanity",
               "shape": list(shape), "empties": int((bC.grid == EMPTY).sum())})
    out["cases"].append(rC)

    # --- Case D control: two-eye life detector sanity on a 2D slice (4x4x1).
    # One black group enclosing two separate simple eyes -> alive_by_two_eyes. ---
    shape = (4, 4, 1)
    blacks = [(0, 0, 0), (1, 0, 0), (2, 0, 0),
              (0, 1, 0), (2, 1, 0),
              (0, 2, 0), (1, 2, 0), (2, 2, 0)]
    # eyes at (1,1,0) [nbrs (1,0)B,(0,1)B,(2,1)B,(1,2)B -> all black] and the
    # outside is open; add a second eye by enclosing (3,?) — instead enclose a
    # second eye at top: extend group to wrap (3,0),(3,1),(3,2) leaving (3,?)...
    # simplest: a 3x3 black ring with center eye + a tail forming a 2nd eye:
    # eyes at (0,0,0) and (0,2,0), separated by black (0,1,0); group connected
    # via the x=1 column.
    blacks = [(1, 0, 0), (1, 1, 0), (0, 1, 0), (1, 2, 0), (1, 3, 0), (0, 3, 0)]
    bD = make_board(shape, blacks, whites=[])
    eyesD = simple_eyes(bD, BLACK)
    out["cases"].append({
        "name": "D control: two-eye detector sanity (4x4x1)",
        "shape": list(shape), "black_simple_eyes": len(eyesD), "eyes": eyesD,
        "alive_by_two_eyes": alive_by_two_eyes(bD, BLACK),
    })

    print(json.dumps(out, indent=2))
    outpath = sys.argv[1] if len(sys.argv) > 1 else None
    if outpath:
        with open(outpath, "w") as f:
            json.dump(out, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
