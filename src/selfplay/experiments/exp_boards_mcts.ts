/*
 * Experiment: characterize board sizes under MCTS self-play (komi 0).
 * Reports candidate "best board size" metrics: decisiveness (avg |margin|,
 * draw rate), game length, and tractability (games/sec). Triviality is probed
 * separately by the komi experiment (how komi-sensitive a board's win-rate is).
 *
 *   npx tsx src/selfplay/experiments/exp_boards_mcts.ts [games] [playouts] [sizesCSV]
 */
import * as fs from "fs";
import { BoardState3D } from "../../engine/BoardState3D";
import { MCTSAgent } from "../mcts";
import { playGame } from "../playGame";

const GAMES = Number(process.argv[2] ?? 24);
const PLAYOUTS = Number(process.argv[3] ?? 96);
const SIZES = (process.argv[4] ?? "3,4").split(",").map(Number);

interface Row {
    n: number;
    games: number;
    blackWinRate: number;
    avgMoves: number;
    avgMargin: number;
    /** mean signed (blackArea − whiteArea) at komi 0 = fair-komi point estimate. */
    fairKomiEstimate: number;
    fairKomiStdErr: number;
    drawRate: number;
    gamesPerSec: number;
}

console.log(
    `# Board characterization + komi point-estimate — MCTS(${PLAYOUTS}) self-play, komi 0, ${GAMES} games/size\n`,
);
console.log("size | blackWin% | avgMoves | avgMargin | fairKomi≈ (±SE) | draw% | games/s");
console.log("-----|-----------|----------|-----------|-----------------|-------|--------");

const rows: Row[] = [];
for (const n of SIZES) {
    let blackWins = 0;
    let draws = 0;
    let sumMoves = 0;
    let sumMargin = 0;
    const diffs: number[] = []; // signed black−white at komi 0
    const t0 = Date.now();
    for (let i = 0; i < GAMES; i++) {
        const state = new BoardState3D({ width: n, height: n, depth: n });
        const black = new MCTSAgent({ playouts: PLAYOUTS, seed: 3100 + i, komi: 0, name: "B" });
        const white = new MCTSAgent({ playouts: PLAYOUTS, seed: 4100 + i, komi: 0, name: "W" });
        const r = playGame(state, black, white, { komi: 0 });
        if (r.winner === "black") blackWins++;
        else if (r.winner === "draw") draws++;
        sumMoves += r.moveCount;
        sumMargin += r.margin;
        diffs.push(r.diff);
    }
    const secs = (Date.now() - t0) / 1000;
    const meanDiff = diffs.reduce((a, b) => a + b, 0) / GAMES;
    const variance = diffs.reduce((a, b) => a + (b - meanDiff) ** 2, 0) / Math.max(1, GAMES - 1);
    const stdErr = Math.sqrt(variance / GAMES);
    const row: Row = {
        n,
        games: GAMES,
        blackWinRate: blackWins / GAMES,
        avgMoves: sumMoves / GAMES,
        avgMargin: sumMargin / GAMES,
        fairKomiEstimate: meanDiff,
        fairKomiStdErr: stdErr,
        drawRate: draws / GAMES,
        gamesPerSec: GAMES / secs,
    };
    rows.push(row);
    console.log(
        `${n}^3  | ${(100 * row.blackWinRate).toFixed(1)}%   | ${row.avgMoves.toFixed(1).padStart(8)} | ` +
            `${row.avgMargin.toFixed(1).padStart(9)} | ${meanDiff.toFixed(2).padStart(7)} (±${stdErr.toFixed(2)}) | ` +
            `${(100 * row.drawRate).toFixed(1).padStart(4)}% | ${row.gamesPerSec.toFixed(1).padStart(6)}`,
    );
}

const out = process.env.OUT;
if (out) {
    fs.writeFileSync(out, JSON.stringify({ playouts: PLAYOUTS, games: GAMES, rows }, null, 2));
    console.log(`\nWrote → ${out}`);
}
