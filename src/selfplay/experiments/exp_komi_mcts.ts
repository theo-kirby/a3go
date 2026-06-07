/*
 * Experiment: estimate fair komi using MCTS as a close-game reference. Both
 * sides are equal-strength MCTS playing under the komi being tested; we measure
 * Black's win-rate vs komi and the 50% crossing. Also reports avg margin, which
 * indicates whether games are close enough for the win-rate crossing to be a
 * meaningful komi estimate.
 *
 *   npx tsx src/selfplay/experiments/exp_komi_mcts.ts [size] [games] [playouts]
 */
import * as fs from "fs";
import { BoardState3D } from "../../engine/BoardState3D";
import { MCTSAgent } from "../mcts";
import { playGame } from "../playGame";

const N = Number(process.argv[2] ?? 3);
const GAMES = Number(process.argv[3] ?? 30);
const PLAYOUTS = Number(process.argv[4] ?? 96);
const KOMI_GRID = [-1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 7.5];

interface Row {
    komi: number;
    games: number;
    blackWins: number;
    blackWinRate: number;
    ci95: number;
    avgMargin: number;
    avgMoves: number;
}

const t0 = Date.now();
const rows: Row[] = [];
console.log(`# Komi re-estimate via MCTS(${PLAYOUTS}) self-play — ${N}^3, ${GAMES} games/komi\n`);
console.log("komi  | blackWin% (±95%) | avgMargin | avgMoves");
console.log("------|------------------|-----------|---------");

for (const komi of KOMI_GRID) {
    let blackWins = 0;
    let sumMargin = 0;
    let sumMoves = 0;
    for (let i = 0; i < GAMES; i++) {
        const state = new BoardState3D({ width: N, height: N, depth: N });
        const black = new MCTSAgent({ playouts: PLAYOUTS, seed: 7000 + i, komi, name: "B" });
        const white = new MCTSAgent({ playouts: PLAYOUTS, seed: 8000 + i, komi, name: "W" });
        const r = playGame(state, black, white, { komi });
        if (r.winner === "black") blackWins++;
        sumMargin += r.margin;
        sumMoves += r.moveCount;
    }
    const p = blackWins / GAMES;
    const row: Row = {
        komi,
        games: GAMES,
        blackWins,
        blackWinRate: p,
        ci95: 1.96 * Math.sqrt((p * (1 - p)) / GAMES),
        avgMargin: sumMargin / GAMES,
        avgMoves: sumMoves / GAMES,
    };
    rows.push(row);
    console.log(
        `${komi.toFixed(1).padStart(5)} | ${(100 * p).toFixed(1)}% (±${(100 * row.ci95).toFixed(1)}) | ` +
            `${row.avgMargin.toFixed(1).padStart(9)} | ${row.avgMoves.toFixed(1).padStart(8)}`,
    );
}

let crossing: number | null = null;
for (let i = 1; i < rows.length; i++) {
    const a = rows[i - 1];
    const b = rows[i];
    if (a.blackWinRate >= 0.5 && b.blackWinRate < 0.5) {
        const t = (a.blackWinRate - 0.5) / (a.blackWinRate - b.blackWinRate);
        crossing = a.komi + t * (b.komi - a.komi);
        break;
    }
}
console.log(
    crossing === null
        ? `\n≈ fair komi: not bracketed in [${KOMI_GRID[0]}, ${KOMI_GRID[KOMI_GRID.length - 1]}]`
        : `\n≈ MCTS fair komi (50% crossing): ${crossing.toFixed(2)}`,
);
console.log(`(elapsed ${((Date.now() - t0) / 1000).toFixed(0)}s)`);

const out = process.env.OUT;
if (out) {
    fs.writeFileSync(
        out,
        JSON.stringify({ n: N, playouts: PLAYOUTS, games: GAMES, rows, crossing }, null, 2),
    );
    console.log(`Wrote → ${out}`);
}
