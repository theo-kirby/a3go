/*
 * GEO-1 precondition probe — the d=1 boundary of the dimensionality ladder.
 *
 * The GEO-1 design brief (record node still-recipe-4954) requires, before any
 * (n,n,d) ladder work: "verify (n,n,1) reproduces a 2D engine on a known 2D
 * position first". This script is that verification, in three parts:
 *
 *  A. STRUCTURAL — exhaustive equivalence of Topology3D(n,n,1) with the
 *     independently-written Topology2D(n,n): point iteration order, flat idx
 *     mapping, and per-point neighbor sets, for every point, over a range of n.
 *  B. RULES — known-answer 2D Go checks on BoardState3D(n,n,1): liberty counts
 *     (corner/edge/center = 2/3/4), corner capture + prisoner accounting,
 *     suicide rejection (incl. the 1x1 board), the classic 2D ko (immediate
 *     recapture superko-banned, legal again after an exchange elsewhere), and
 *     a hand-scored Tromp-Taylor position.
 *  C. MEASUREMENT — d=1 boundary datapoints on (3,3,1) at komi 0, where 2D Go
 *     is solved (perfect play: Black takes the whole board, +9, first move
 *     tengen). MCTS-vs-MCTS self-play, free and with the first move forced by
 *     cell type (center/edge/corner) — the 2D anchor for GEO-1's ladder and
 *     STRAT-1's cell-type question.
 *
 *   npx tsx src/selfplay/experiments/exp_2d_boundary.ts [games] [playouts] [seed]
 *   OUT=experiments/2d_boundary.json to write the result JSON.
 */
import * as fs from "fs";
import {
    BoardState3D,
    JGOFNumericPlayerColor,
    Topology2D,
    Topology3D,
    scoreTrompTaylor,
} from "../../engine";
import { MCTSAgent } from "../mcts";
import { playGame } from "../playGame";

const GAMES = Number(process.argv[2] ?? 40);
const PLAYOUTS = Number(process.argv[3] ?? 256);
const SEED = Number(process.argv[4] ?? 20260807);

const B = JGOFNumericPlayerColor.BLACK;
const W = JGOFNumericPlayerColor.WHITE;
const E = JGOFNumericPlayerColor.EMPTY;

let checksRun = 0;
let checksFailed = 0;
function check(name: string, ok: boolean, detail = "") {
    checksRun++;
    if (!ok) {
        checksFailed++;
    }
    console.log(`  [${ok ? "ok" : "FAIL"}] ${name}${detail ? ` — ${detail}` : ""}`);
}

/* ---------------------------------------------------------------- A ------ */

console.log("A. Topology3D(n,n,1) ≡ Topology2D(n,n), exhaustive per point");
const SIZES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 19];
let pointsCompared = 0;
for (const n of SIZES) {
    const t3 = new Topology3D(n, n, 1);
    const t2 = new Topology2D(n, n);
    let ok = t3.numPoints === t2.numPoints && t3.depth === 1;

    const order3: number[] = [];
    const order2: number[] = [];
    t3.forEachPoint((x, y, z) => order3.push(t3.idx(x, y, z)));
    t2.forEachPoint((x, y, z) => order2.push(t2.idx(x, y, z)));
    ok = ok && order3.length === order2.length && order3.every((v, i) => v === order2[i]);

    t3.forEachPoint((x, y, z) => {
        pointsCompared++;
        const nbr3: number[] = [];
        const nbr2: number[] = [];
        t3.forEachNeighbor(x, y, z, (a, b, c) => nbr3.push(t3.idx(a, b, c)));
        t2.forEachNeighbor(x, y, z, (a, b, c) => nbr2.push(t2.idx(a, b, c)));
        nbr3.sort((p, q) => p - q);
        nbr2.sort((p, q) => p - q);
        ok = ok && nbr3.length === nbr2.length && nbr3.every((v, i) => v === nbr2[i]);
        ok = ok && t3.idx(x, y, z) === t2.idx(x, y, z);
    });
    check(`n=${n}: points, order, idx, neighbor sets identical`, ok);
}
console.log(`  (${pointsCompared} points compared exhaustively)`);

/* ---------------------------------------------------------------- B ------ */

console.log("B. 2D rule semantics on BoardState3D(n,n,1)");

// B1: liberty counts corner/edge/center = 2/3/4 on (5,5,1).
{
    const s = new BoardState3D({ width: 5, height: 5, depth: 1 });
    s.setStone(0, 0, 0, B);
    s.setStone(2, 0, 0, B);
    s.setStone(2, 2, 0, B);
    const libs = (x: number, y: number) => s.countLiberties(s.getRawStoneString(x, y, 0));
    check(
        "liberties corner/edge/center = 2/3/4",
        libs(0, 0) === 2 && libs(2, 0) === 3 && libs(2, 2) === 4,
        `${libs(0, 0)}/${libs(2, 0)}/${libs(2, 2)}`,
    );
}

// B2: corner capture — W(1,0)+W(0,1) capture B(0,0); prisoner accounting.
{
    const s = new BoardState3D({ width: 5, height: 5, depth: 1 });
    s.setStone(0, 0, 0, B);
    s.setStone(1, 0, 0, W);
    s.player = W;
    const res = s.play(0, 1, 0);
    check(
        "corner stone captured by 2 stones (2D), prisoners counted",
        res.captured.length === 1 && s.getStone(0, 0, 0) === E && s.white_prisoners === 1,
        `captured=${res.captured.length}`,
    );
}

// B3: suicide rejected — the 1x1 board (0 liberties anywhere) and a 2D corner.
{
    const s1 = new BoardState3D({ width: 1, height: 1, depth: 1 });
    let threw1 = false;
    try {
        s1.play(0, 0, 0);
    } catch {
        threw1 = true;
    }
    const s2 = new BoardState3D({ width: 5, height: 5, depth: 1 });
    s2.setStone(1, 0, 0, B);
    s2.setStone(0, 1, 0, B);
    s2.player = W;
    let threw2 = false;
    try {
        s2.play(0, 0, 0);
    } catch {
        threw2 = true;
    }
    check("suicide rejected on (1,1,1) and in a (5,5,1) corner", threw1 && threw2);
}

// B4: classic 2D ko — immediate recapture is superko-banned, then legal after
// an exchange elsewhere. Board passed at construction so the ko shape is in
// the position history (as in a real game reaching it).
{
    const board = [
        [
            [E, B, W, E, E],
            [B, W, E, W, E],
            [E, B, W, E, E],
            [E, E, E, E, E],
            [E, E, E, E, E],
        ],
    ];
    const s = new BoardState3D({ width: 5, height: 5, depth: 1, board, player: B });
    const cap = s.play(2, 1, 0); // B takes the ko: captures W(1,1)
    const koTake = cap.captured.length === 1 && cap.captured[0].x === 1 && cap.captured[0].y === 1;
    let banned = false;
    try {
        s.play(1, 1, 0); // W immediate recapture would repeat the position
    } catch (e) {
        banned = e instanceof Error && /superko/i.test(e.message);
    }
    s.play(4, 4, 0); // W ko threat elsewhere
    s.play(4, 3, 0); // B answers elsewhere
    let retakeLegal = true;
    let retakeCaptures = 0;
    try {
        retakeCaptures = s.play(1, 1, 0).captured.length; // W retakes the ko
    } catch {
        retakeLegal = false;
    }
    check(
        "2D ko: take, immediate recapture superko-banned, legal after exchange",
        koTake && banned && retakeLegal && retakeCaptures === 1,
    );
}

// B5: Tromp-Taylor on a hand-scored 2D position: B column wall at x=2, one W
// stone at (4,2). Left region (10 empties) is Black territory; right region
// borders both colors -> neutral. B area 15, W area 1, diff +14.
{
    const s = new BoardState3D({ width: 5, height: 5, depth: 1 });
    for (let y = 0; y < 5; y++) {
        s.setStone(2, y, 0, B);
    }
    s.setStone(4, 2, 0, W);
    const sc = scoreTrompTaylor(s, { komi: 0 });
    check(
        "Tromp-Taylor hand-scored position: B 15 / W 1 / diff +14, 9 neutral",
        sc.black.area === 15 &&
            sc.white.area === 1 &&
            sc.diff === 14 &&
            sc.neutral.length === 9 &&
            sc.winner === "black",
        `B=${sc.black.area} W=${sc.white.area} diff=${sc.diff} neutral=${sc.neutral.length}`,
    );
}

// B6: empty board scores all-neutral, draw at komi 0.
{
    const s = new BoardState3D({ width: 5, height: 5, depth: 1 });
    const sc = scoreTrompTaylor(s, { komi: 0 });
    check(
        "empty board: 25 neutral, draw at komi 0",
        sc.neutral.length === 25 && sc.diff === 0 && sc.winner === "draw",
    );
}

/* ---------------------------------------------------------------- C ------ */

console.log(`C. (3,3,1) komi-0 measurement — ${GAMES} games/arm, MCTS(${PLAYOUTS}) both sides`);
console.log(
    "   2D anchor: 3x3 Go is solved — perfect play = Black takes all 9 (+9), tengen first.",
);

interface ArmResult {
    arm: string;
    forcedFirstMove: { x: number; y: number } | null;
    games: number;
    blackWins: number;
    blackWinRate: number;
    ci95: [number, number];
    meanDiff: number;
    fullBoardWins: number; // games Black scored the entire board (+9)
    meanMoves: number;
    seconds: number;
}

function wilson(w: number, n: number): [number, number] {
    if (n === 0) {
        return [0, 1];
    }
    const z = 1.96;
    const p = w / n;
    const den = 1 + (z * z) / n;
    const center = (p + (z * z) / (2 * n)) / den;
    const half = (z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n))) / den;
    return [Math.max(0, center - half), Math.min(1, center + half)];
}

function runArm(arm: string, forced: { x: number; y: number } | null): ArmResult {
    const t0 = Date.now();
    let blackWins = 0;
    let diffSum = 0;
    let fullBoard = 0;
    let movesSum = 0;
    for (let g = 0; g < GAMES; g++) {
        const initial = new BoardState3D({ width: 3, height: 3, depth: 1 });
        if (forced) {
            initial.play(forced.x, forced.y, 0); // Black's forced first move
        }
        const black = new MCTSAgent({
            playouts: PLAYOUTS,
            seed: SEED + g * 2,
            komi: 0,
            name: "mcts-B",
        });
        const white = new MCTSAgent({
            playouts: PLAYOUTS,
            seed: SEED + g * 2 + 1,
            komi: 0,
            name: "mcts-W",
        });
        const rec = playGame(initial, black, white, { komi: 0 });
        if (rec.winner === "black") {
            blackWins++;
        }
        diffSum += rec.diff;
        if (rec.diff === 9) {
            fullBoard++;
        }
        movesSum += rec.moveCount + (forced ? 1 : 0);
    }
    const seconds = (Date.now() - t0) / 1000;
    const r: ArmResult = {
        arm,
        forcedFirstMove: forced,
        games: GAMES,
        blackWins,
        blackWinRate: blackWins / GAMES,
        ci95: wilson(blackWins, GAMES),
        meanDiff: diffSum / GAMES,
        fullBoardWins: fullBoard,
        meanMoves: movesSum / GAMES,
        seconds,
    };
    console.log(
        `  ${arm.padEnd(14)} black ${blackWins}/${GAMES} (${(r.blackWinRate * 100).toFixed(0)}%` +
            ` [${(r.ci95[0] * 100).toFixed(0)},${(r.ci95[1] * 100).toFixed(0)}]),` +
            ` mean diff ${r.meanDiff.toFixed(2)}, +9 sweeps ${fullBoard}/${GAMES},` +
            ` ${seconds.toFixed(1)}s`,
    );
    return r;
}

const arms: ArmResult[] = [
    runArm("free", null),
    runArm("center(1,1)", { x: 1, y: 1 }),
    runArm("edge(1,0)", { x: 1, y: 0 }),
    runArm("corner(0,0)", { x: 0, y: 0 }),
];

/* ---------------------------------------------------------------- out ---- */

console.log(
    `\n${checksFailed === 0 ? "PASS" : "FAIL"}: ${checksRun - checksFailed}/${checksRun} boundary checks` +
        ` (${pointsCompared} topology points compared)`,
);

const out = process.env.OUT;
if (out) {
    fs.writeFileSync(
        out,
        JSON.stringify(
            {
                experiment: "2d_boundary (GEO-1 precondition, d=1 endpoint)",
                seed: SEED,
                games: GAMES,
                playouts: PLAYOUTS,
                topologySizes: SIZES,
                pointsCompared,
                checksRun,
                checksFailed,
                arms,
            },
            null,
            2,
        ) + "\n",
    );
    console.log(`wrote ${out}`);
}
process.exit(checksFailed === 0 ? 0 : 1);
