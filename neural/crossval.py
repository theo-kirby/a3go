"""Cross-validate the Python engine port against the TS reference engine.

Reads a fixture JSON produced by `dump_games.ts` (move lists + Tromp-Taylor score
per seeded random game), replays each game's moves in a3go_engine.Board, and
asserts that (a) every recorded move is legal in the port and (b) the final
Tromp-Taylor breakdown matches the TS engine exactly.

    uv run python crossval.py fixture.json
"""

import json
import sys

from a3go_engine import Board, IllegalMove


def replay(game) -> dict:
    b = Board(game["n"], komi=0.0)
    for i, mv in enumerate(game["moves"]):
        if mv == "pass":
            b.pass_move()
        else:
            x, y, z = mv
            try:
                b.play(x, y, z)
            except IllegalMove as e:
                raise AssertionError(f"move {i} {mv} rejected by port: {e}")
    return b.score_tromp_taylor()


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "fixture.json"
    fixture = json.load(open(path))
    data = fixture["data"]
    mism = 0
    fields = [
        ("black_stones", "blackStones"),
        ("white_stones", "whiteStones"),
        ("black_territory", "blackTerritory"),
        ("white_territory", "whiteTerritory"),
        ("neutral", "neutral"),
        ("diff", "diff"),
        ("winner", "winner"),
    ]
    for g, game in enumerate(data):
        got = replay(game)
        for pk, tk in fields:
            if got[pk] != game[tk]:
                mism += 1
                print(f"  MISMATCH game {g} {pk}: port={got[pk]} ts={game[tk]}")
                break
    n = len(data)
    print(f"\nCross-validation: {n - mism}/{n} games match the TS engine exactly "
          f"(n={fixture['n']}^3, seed={fixture['seed']}).")
    result = {
        "boardSize": fixture["n"],
        "games": n,
        "matched": n - mism,
        "mismatched": mism,
        "seed": fixture["seed"],
        "pass": mism == 0,
    }
    with open("crossval_result.json", "w") as f:
        json.dump(result, f, indent=2)
    return 0 if mism == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
