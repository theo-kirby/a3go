/*
 * Q7 — ko / superko frequency & dynamics in 3D. Plays seeded uniform-random
 * self-play and instruments every move for capture events and ko bans:
 *  - capture-size distribution (single-stone captures are the ones that create
 *    ko shapes; bigger captures cannot be immediately recaptured into a repeat);
 *  - ko bans: after a single-stone capture, is the opponent's immediate recapture
 *    at the vacated point ILLEGAL (positional-superko forbidden)? That is a ko in
 *    action.
 * All public-API only (no engine changes); deterministic from the seed.
 *
 *   npx tsx src/selfplay/experiments/exp_ko.ts [gamesPerSize] [sizesCSV] [seed]
 */
import * as fs from "fs";
import { BoardState3D } from "../../engine/BoardState3D";
import { JGOFNumericPlayerColor } from "../../engine/formats/JGOF";
import { RandomAgent, isLegalMove } from "../agents";

const GAMES = Number(process.argv[2] ?? 200);
const SIZES = (process.argv[3] ?? "3,4,5").split(",").map(Number);
const SEED = Number(process.argv[4] ?? 4242);

const other = (c: JGOFNumericPlayerColor) =>
    c === JGOFNumericPlayerColor.BLACK
        ? JGOFNumericPlayerColor.WHITE
        : JGOFNumericPlayerColor.BLACK;

function stonesOf(s: BoardState3D, color: JGOFNumericPlayerColor): Set<string> {
    const out = new Set<string>();
    s.topology.forEachPoint((x, y, z) => {
        if (s.getStone(x, y, z) === color) {
            out.add(`${x},${y},${z}`);
        }
    });
    return out;
}

interface Row {
    n: number;
    games: number;
    moves: number;
    captureMoves: number;
    singleCaptures: number;
    multiCaptures: number;
    koBans: number; // single-capture whose immediate recapture is superko-illegal
    capturesPerGame: number;
    singleCapturesPerGame: number;
    koBansPerGame: number;
}

const rows: Row[] = [];
for (const n of SIZES) {
    let moves = 0;
    let captureMoves = 0;
    let singleCaptures = 0;
    let multiCaptures = 0;
    let koBans = 0;
    for (let g = 0; g < GAMES; g++) {
        const state = new BoardState3D({ width: n, height: n, depth: n });
        const black = new RandomAgent(SEED + g, "B");
        const white = new RandomAgent(SEED + 100000 + g, "W");
        let consecutivePasses = 0;
        const maxMoves = state.topology.numPoints * 8;
        let count = 0;
        while (consecutivePasses < 2 && count < maxMoves) {
            const mover = state.player;
            const opp = other(mover);
            const agent = mover === JGOFNumericPlayerColor.BLACK ? black : white;
            const m = agent.selectMove(state);
            if (m === "pass") {
                state.pass();
                consecutivePasses++;
                count++;
                continue;
            }
            const oppBefore = stonesOf(state, opp);
            state.play(m.x, m.y, m.z);
            consecutivePasses = 0;
            count++;
            moves++;
            const oppAfter = stonesOf(state, opp);
            if (oppAfter.size < oppBefore.size) {
                captureMoves++;
                const removed: string[] = [];
                for (const p of oppBefore) {
                    if (!oppAfter.has(p)) {
                        removed.push(p);
                    }
                }
                if (removed.length === 1) {
                    singleCaptures++;
                    // It is now `opp` to move. Can opp immediately recapture at the
                    // vacated point? If illegal, that is a ko/superko ban.
                    const [x, y, z] = removed[0].split(",").map(Number);
                    if (!isLegalMove(state, x, y, z)) {
                        koBans++;
                    }
                } else {
                    multiCaptures++;
                }
            }
        }
    }
    rows.push({
        n,
        games: GAMES,
        moves,
        captureMoves,
        singleCaptures,
        multiCaptures,
        koBans,
        capturesPerGame: captureMoves / GAMES,
        singleCapturesPerGame: singleCaptures / GAMES,
        koBansPerGame: koBans / GAMES,
    });
}

console.log("# Q7 — ko / superko frequency in random 3D self-play\n");
console.log("size | games | captures/game | single/game | koBans/game | single | multi | koBans");
console.log("-----|-------|---------------|-------------|-------------|--------|-------|-------");
for (const r of rows) {
    console.log(
        `${r.n}^3  | ${String(r.games).padStart(5)} | ${r.capturesPerGame.toFixed(2).padStart(13)} | ` +
            `${r.singleCapturesPerGame.toFixed(2).padStart(11)} | ${r.koBansPerGame.toFixed(3).padStart(11)} | ` +
            `${String(r.singleCaptures).padStart(6)} | ${String(r.multiCaptures).padStart(5)} | ${String(r.koBans).padStart(6)}`,
    );
}
console.log(
    "\nReading: single-stone captures create ko shapes; koBans count how often the\n" +
        "immediate recapture is positional-superko-illegal. Compare across sizes to see\n" +
        "whether ko fights are rarer/more common as 6-connectivity grows.",
);

const out = process.env.OUT;
if (out) {
    fs.writeFileSync(out, JSON.stringify({ rows }, null, 2));
    console.log(`\nWrote → ${out}`);
}
