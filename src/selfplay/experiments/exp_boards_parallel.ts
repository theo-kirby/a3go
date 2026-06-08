/*
 * Q2 — board characterization, parallel version. MCTS self-play at komi 0 across
 * board sizes; reports decisiveness (avg |margin|, draw rate), game length,
 * fair-komi point estimate (mean signed black−white diff ± SE), and throughput.
 * Sharded across cores via ./parallel.ts so larger boards (5^3+) become testable.
 *
 *   npx tsx src/selfplay/experiments/exp_boards_parallel.ts [gamesPerSize] [playouts] [sizesCSV] [shardsPerSize]
 */
import * as fs from "fs";
import { runShards, defaultConcurrency, ShardJob } from "../parallel";
import type { ShardAggregate } from "../worker_selfplay";

const GAMES = Number(process.argv[2] ?? 120);
const PLAYOUTS = Number(process.argv[3] ?? 96);
const SIZES = (process.argv[4] ?? "3,4,5").split(",").map(Number);
const SHARDS = Number(process.argv[5] ?? defaultConcurrency());

function splitGames(total: number, shards: number): number[] {
    const base = Math.floor(total / shards);
    const rem = total % shards;
    const out: number[] = [];
    for (let i = 0; i < shards; i++) {
        const g = base + (i < rem ? 1 : 0);
        if (g > 0) out.push(g);
    }
    return out;
}

interface Row {
    n: number;
    games: number;
    blackWinRate: number;
    drawRate: number;
    avgMoves: number;
    avgMargin: number;
    fairKomiEstimate: number;
    fairKomiStdErr: number;
    coreGamesPerSec: number;
    parGamesPerSec: number;
}

async function main(): Promise<void> {
    const jobs: ShardJob[] = [];
    const jobN: number[] = [];
    SIZES.forEach((n, ni) => {
        splitGames(GAMES, SHARDS).forEach((g, si) => {
            jobs.push({
                mode: "selfplay",
                n,
                komi: 0,
                playouts: PLAYOUTS,
                games: g,
                seedBase: 3_000_000 * (ni + 1) + 10_000 * si,
            });
            jobN.push(n);
        });
    });

    process.stderr.write(
        `# Boards(parallel) sizes ${SIZES.join(",")} — ${GAMES} games/size, ` +
            `MCTS(${PLAYOUTS}), ${jobs.length} shards, concurrency ${defaultConcurrency()}\n`,
    );
    const wall0 = Date.now();
    const aggs = await runShards(jobs);
    const wallSecs = (Date.now() - wall0) / 1000;

    const byN = new Map<number, ShardAggregate[]>();
    aggs.forEach((a, i) => {
        const n = jobN[i];
        if (!byN.has(n)) byN.set(n, []);
        byN.get(n)!.push(a);
    });

    const rows: Row[] = [];
    for (const n of SIZES) {
        const list = byN.get(n)!;
        const games = list.reduce((s, a) => s + a.games, 0);
        const blackWins = list.reduce((s, a) => s + a.refWins, 0);
        const draws = list.reduce((s, a) => s + a.draws, 0);
        const sumMoves = list.reduce((s, a) => s + a.sumMoves, 0);
        const sumMargin = list.reduce((s, a) => s + a.sumMargin, 0);
        const sumDiff = list.reduce((s, a) => s + a.sumDiff, 0);
        const sumDiff2 = list.reduce((s, a) => s + a.sumDiff2, 0);
        const shardSecs = list.reduce((s, a) => s + a.secs, 0);
        const meanDiff = sumDiff / games;
        const variance =
            Math.max(0, sumDiff2 / games - meanDiff * meanDiff) * (games / (games - 1));
        const stdErr = Math.sqrt(variance / games);
        rows.push({
            n,
            games,
            blackWinRate: blackWins / games,
            drawRate: draws / games,
            avgMoves: sumMoves / games,
            avgMargin: sumMargin / games,
            fairKomiEstimate: meanDiff,
            fairKomiStdErr: stdErr,
            coreGamesPerSec: games / shardSecs,
            parGamesPerSec: games / wallSecs,
        });
    }

    console.log(`# Board characterization (parallel) — MCTS(${PLAYOUTS}) self-play, komi 0\n`);
    console.log("size | blackWin% | draw% | avgMoves | avgMargin | fairKomi≈ (±SE) | games/s/core");
    console.log("-----|-----------|-------|----------|-----------|-----------------|-------------");
    for (const r of rows) {
        console.log(
            `${r.n}^3  | ${(100 * r.blackWinRate).toFixed(1).padStart(5)}%   | ` +
                `${(100 * r.drawRate).toFixed(1).padStart(4)}% | ${r.avgMoves.toFixed(1).padStart(8)} | ` +
                `${r.avgMargin.toFixed(1).padStart(9)} | ${r.fairKomiEstimate.toFixed(2).padStart(6)} ` +
                `(±${r.fairKomiStdErr.toFixed(2)}) | ${r.coreGamesPerSec.toFixed(2).padStart(11)}`,
        );
    }
    console.log(`\n(total wall ${wallSecs.toFixed(0)}s, concurrency ${defaultConcurrency()})`);

    const out = process.env.OUT;
    if (out) {
        fs.writeFileSync(
            out,
            JSON.stringify(
                { playouts: PLAYOUTS, gamesPerSize: GAMES, shardsPerSize: SHARDS, rows },
                null,
                2,
            ),
        );
        console.log(`Wrote → ${out}`);
    }
}

main().catch((e) => {
    process.stderr.write(String(e) + "\n");
    process.exit(1);
});
