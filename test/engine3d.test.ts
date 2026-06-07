/*
 * Correctness tests for the 3D Go engine (BoardState3D, Topology3D, Scorer3D).
 *
 * Standalone, dependency-free harness (no Jest). Run with:
 *   npm test            (= tsx test/engine3d.test.ts)
 *   npx tsx test/engine3d.test.ts
 * Exits non-zero on failure. Validates the engine before any self-play
 * conclusions rest on it.
 */
import { BoardState3D } from "../src/engine/BoardState3D";
import { Topology3D } from "../src/engine/Topology";
import { scoreTrompTaylor } from "../src/engine/Scorer3D";
import { JGOFNumericPlayerColor as C } from "../src/engine/formats/JGOF";

// --- tiny assertion harness -------------------------------------------------
let pass = 0;
const fails: string[] = [];
function check(name: string, cond: boolean, detail = ""): void {
    if (cond) {
        pass++;
    } else {
        fails.push(`${name}${detail ? " :: " + detail : ""}`);
    }
}
function eq<T>(name: string, got: T, want: T): void {
    check(name, got === want, `got ${String(got)}, expected ${String(want)}`);
}
function throwsWith(name: string, fn: () => void, match?: string): void {
    try {
        fn();
        check(name, false, "expected throw, got none");
    } catch (e) {
        const m = (e as Error).message;
        check(name, !match || m.includes(match), `message="${m}" (wanted "${match}")`);
    }
}
function group(title: string): void {
    console.log(`\n# ${title}`);
}

// --- helpers ----------------------------------------------------------------
const libsAt = (b: BoardState3D, x: number, y: number, z: number): number =>
    b.countLiberties(b.getRawStoneString(x, y, z));

// ===========================================================================
group("Topology3D — neighbor / liberty counts (the 3D-specific invariant)");
{
    const t = new Topology3D(3, 3, 3);
    eq("numPoints 3x3x3 = 27", t.numPoints, 27);
    const countNeighbors = (x: number, y: number, z: number): number => {
        let n = 0;
        t.forEachNeighbor(x, y, z, () => n++);
        return n;
    };
    // On a 3^3 cube: corner=3, edge=4, face-center=5, body-center=6.
    eq("corner (0,0,0) has 3 neighbors", countNeighbors(0, 0, 0), 3);
    eq("edge   (1,0,0) has 4 neighbors", countNeighbors(1, 0, 0), 4);
    eq("face   (1,1,0) has 5 neighbors", countNeighbors(1, 1, 0), 5);
    eq("center (1,1,1) has 6 neighbors", countNeighbors(1, 1, 1), 6);

    // idx is a bijection over all points.
    const seen = new Set<number>();
    let dup = false;
    t.forEachPoint((x, y, z) => {
        const i = t.idx(x, y, z);
        if (seen.has(i) || i < 0 || i >= t.numPoints) {
            dup = true;
        }
        seen.add(i);
    });
    check("idx is a bijection over all 27 points", !dup && seen.size === 27);
}

group("BoardState3D — placement, turn order, basic liberties");
{
    const b = new BoardState3D({ width: 3, height: 3, depth: 3 });
    eq("first player is BLACK", b.player, C.BLACK);
    b.play(0, 0, 0); // black corner
    eq("after one move it's WHITE's turn", b.player, C.WHITE);
    eq("move_number incremented to 1", b.move_number, 1);
    eq("corner stone has 3 liberties", libsAt(b, 0, 0, 0), 3);
    b.play(1, 1, 1); // white center
    eq("center stone has 6 liberties", libsAt(b, 1, 1, 1), 6);

    throwsWith("playing on an occupied point throws", () => b.play(0, 0, 0), "not empty");
    throwsWith("playing out of bounds throws", () => b.play(3, 0, 0), "Out of bounds");
}

group("BoardState3D — capture (single stone & group) and prisoner accounting");
{
    // Single-stone capture: black corner stone, two of its 3 liberties pre-set
    // white; white plays the third to capture. (setStone = sandbox place-mode.)
    const b = new BoardState3D({ width: 3, height: 3, depth: 3, player: C.WHITE });
    b.setStone(0, 0, 0, C.BLACK); // corner, liberties (1,0,0),(0,1,0),(0,0,1)
    b.setStone(1, 0, 0, C.WHITE);
    b.setStone(0, 1, 0, C.WHITE);
    eq("black corner present before last liberty filled", b.getStone(0, 0, 0), C.BLACK);
    b.play(0, 0, 1); // W fills the last liberty -> captures B(0,0,0)
    eq("black corner captured (now empty)", b.getStone(0, 0, 0), C.EMPTY);
    eq("white_prisoners counts the 1 stone white captured", b.white_prisoners, 1);

    // Group capture: a 2-stone black group on a 3x3x1 plane, all liberties but
    // one pre-set white; white plays the last to capture both.
    const g = new BoardState3D({ width: 3, height: 3, depth: 1, player: C.WHITE });
    g.setStone(1, 0, 0, C.BLACK); // group {(1,0),(1,1)}
    g.setStone(1, 1, 0, C.BLACK);
    g.setStone(0, 0, 0, C.WHITE);
    g.setStone(2, 0, 0, C.WHITE);
    g.setStone(0, 1, 0, C.WHITE);
    g.setStone(2, 1, 0, C.WHITE); // remaining black liberty: (1,2)
    eq("black pair alive before atari filled", g.getStone(1, 0, 0), C.BLACK);
    g.play(1, 2, 0); // W fills (1,2) -> black group has 0 liberties -> captured
    eq("group stone (1,0) captured", g.getStone(1, 0, 0), C.EMPTY);
    eq("group stone (1,1) captured", g.getStone(1, 1, 0), C.EMPTY);
    eq("white_prisoners == 2 (captured the pair)", g.white_prisoners, 2);
}

group("BoardState3D — suicide rejection, and capture-takes-priority exception");
{
    // Suicide: black plays the corner (0,0); both its neighbors are white and it
    // captures nothing -> zero liberties -> illegal.
    const s = new BoardState3D({ width: 3, height: 3, depth: 1, player: C.BLACK });
    s.setStone(1, 0, 0, C.WHITE);
    s.setStone(0, 1, 0, C.WHITE);
    throwsWith(
        "filling own last liberty (no capture) is suicide",
        () => s.play(0, 0, 0),
        "Suicide",
    );

    // Capture-takes-priority: the same shape becomes legal if the move captures.
    // Line of 3: B at center, W at left; white plays right -> would have 0 libs
    // for the black center, capturing it, so white's move is legal.
    const c = new BoardState3D({ width: 3, height: 1, depth: 1, player: C.WHITE });
    c.setStone(1, 0, 0, C.BLACK); // center, libs x=0,x=2
    c.setStone(0, 0, 0, C.WHITE); // left wall
    c.play(2, 0, 0); // W right -> captures B(1,0,0)
    eq("center black captured by enclosing line", c.getStone(1, 0, 0), C.EMPTY);
    eq("white_prisoners==1 from the enclosure", c.white_prisoners, 1);
}

group("BoardState3D — positional superko (minimal 2x1x1 repetitive capture)");
{
    // Minimal ko: two-point line. B@0, W captures by playing @1 (B has only nbr @1),
    // then B replaying @0 would recreate the post-B position from the FIRST move,
    // i.e. recreate a previously-seen whole-board position -> must be rejected.
    const b = new BoardState3D({ width: 2, height: 1, depth: 1 });
    b.play(0, 0, 0); // B -> board [B,.]   (this position recorded in history)
    eq("after B: [B,.]", b.getStone(0, 0, 0), C.BLACK);
    b.play(1, 0, 0); // W -> captures B(0) -> board [.,W]
    eq("after W: black captured", b.getStone(0, 0, 0), C.EMPTY);
    eq("after W: white at x=1", b.getStone(1, 0, 0), C.WHITE);
    // Black plays (0,0,0): would capture W(1), board returns to [B,.] (a prior position).
    throwsWith(
        "recapture recreating a prior position is rejected (superko)",
        () => b.play(0, 0, 0),
        "superko",
    );
    // State must be intact after the rejected move (rollback).
    eq("after rejected ko: white still at x=1", b.getStone(1, 0, 0), C.WHITE);
    eq("after rejected ko: x=0 still empty", b.getStone(0, 0, 0), C.EMPTY);
    // The rejected move was Black's recapture, so it is still Black to move.
    eq("after rejected ko: still black's move (recapture forbidden)", b.player, C.BLACK);
}

group("BoardState3D — hashPosition excludes player-to-move (PSK, not SSK)");
{
    const a = new BoardState3D({ width: 3, height: 3, depth: 1 });
    a.play(1, 1, 0); // identical board, but...
    const h1 = a.hashPosition();
    // Build a board with the same stones but the OTHER player to move.
    const a2 = new BoardState3D({ width: 3, height: 3, depth: 1, player: C.WHITE });
    a2.setStone(1, 1, 0, C.BLACK);
    eq("same stones hash equal regardless of side to move", a2.hashPosition(), h1);
}

group("Scorer3D — Tromp-Taylor area scoring & komi");
{
    // One black stone on 3x3x1: 1 stone + 8 territory = area 9, white 0.
    const b = new BoardState3D({ width: 3, height: 3, depth: 1 });
    b.setStone(1, 1, 0, C.BLACK);
    const s0 = scoreTrompTaylor(b, { komi: 0 });
    eq("black area = 9 (1 stone + 8 territory)", s0.black.area, 9);
    eq("white area = 0", s0.white.area, 0);
    eq("diff = +9 (black ahead)", s0.diff, 9);
    eq("winner black", s0.winner, "black");

    const s9 = scoreTrompTaylor(b, { komi: 9 });
    eq("komi 9 -> white area 9", s9.white.area, 9);
    eq("komi 9 -> draw", s9.winner, "draw");

    const s95 = scoreTrompTaylor(b, { komi: 9.5 });
    eq("komi 9.5 -> white wins by 0.5", s95.winner, "white");
    eq("komi 9.5 -> margin 0.5", s95.margin, 0.5);

    // A neutral (dame) region bordered by both colors counts for neither.
    const d = new BoardState3D({ width: 3, height: 1, depth: 1 });
    d.setStone(0, 0, 0, C.BLACK);
    d.setStone(2, 0, 0, C.WHITE);
    const sd = scoreTrompTaylor(d, { komi: 0 });
    eq("contested middle point is neutral (black area=1)", sd.black.area, 1);
    eq("contested middle point is neutral (white area=1)", sd.white.area, 1);
    eq("1 neutral point", sd.neutral.length, 1);
}

group("BoardState3D — clone() is a faithful deep copy (history + counters)");
{
    const b = new BoardState3D({ width: 2, height: 1, depth: 1 });
    b.play(0, 0, 0); // B  -> [B,.]
    b.play(1, 0, 0); // W captures -> [.,W]; history holds [B,.] and [.,W]
    const c = b.clone();
    eq("clone copies board (x=1 white)", c.getStone(1, 0, 0), C.WHITE);
    eq("clone copies side-to-move (black)", c.player, b.player);
    eq("clone copies move_number", c.move_number, b.move_number);
    eq("clone copies white_prisoners", c.white_prisoners, b.white_prisoners);
    // Superko history must carry over: the ko forbidden on the original is also
    // forbidden on the clone. (Regression test for the clone-history fix.)
    throwsWith(
        "clone preserves superko history (forbidden ko stays forbidden)",
        () => c.play(0, 0, 0),
        "superko",
    );
    // Mutating the clone must not corrupt the original's history/board (isolation).
    eq("original board unchanged after clone mutated", b.getStone(1, 0, 0), C.WHITE);
}

// --- report -----------------------------------------------------------------
console.log(`\n${"=".repeat(60)}`);
if (fails.length === 0) {
    console.log(`PASS — ${pass}/${pass} checks passed.`);
    process.exit(0);
} else {
    console.log(`FAIL — ${pass}/${pass + fails.length} passed, ${fails.length} failed:`);
    for (const f of fails) {
        console.log(`  ✗ ${f}`);
    }
    process.exit(1);
}
