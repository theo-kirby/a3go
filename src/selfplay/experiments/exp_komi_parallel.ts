/*
 * Q1 — fair komi, parallel high-throughput version. Equal-strength MCTS vs MCTS
 * under a swept komi grid; Black win-rate vs komi with 95% CI and the 50%
 * crossing. Games are sharded across CPU cores via ./parallel.ts so we can run
 * hundreds of games per komi instead of dozens.
 *
 *   npx tsx src/selfplay/experiments/exp_komi_parallel.ts [size] [gamesPerKomi] [playouts] [shardsPerKomi]
 */
import * as fs from "fs";
import { runShards, defaultConcurrency, ShardJob } from "../parallel";
import type { ShardAggregate } from "../worker_selfplay";

const N = Number(process.argv[2] ?? 3);
const GAMES = Number(process.argv[3] ?? 200);
const PLAYOUTS = Number(process.argv[4] ?? 96);
const SHARDS = Number(process.argv[5] ?? defaultConcurrency());
const KOMI_GRID = [-1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 7.5];

/** Split `total` games into `shards` near-equal positive counts. */
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
    komi: number;
    games: number;
    blackWins: number;
    whiteWins: number;
    draws: number;
    blackWinRate: number;
    ci95: number;
    avgMargin: number;
    avgMoves: number;
    drawRate: number;
}

async function main(): Promise<void> {
    // Build every (komi, shard) job up front, then run the whole grid as one pool.
    const jobs: ShardJob[] = [];
    const jobKomi: number[] = [];
    KOMI_GRID.forEach((komi, ki) => {
        splitGames(GAMES, SHARDS).forEach((g, si) => {
            jobs.push({
                mode: "selfplay",
                n: N,
                komi,
                playouts: PLAYOUTS,
                games: g,
                seedBase: 1_000_000 * (ki + 1) + 10_000 * si,
            });
            jobKomi.push(komi);
        });
    });

    process.stderr.write(
        `# Komi(parallel) ${N}^3 — ${GAMES} games/komi × ${KOMI_GRID.length} komi, ` +
            `MCTS(${PLAYOUTS}), ${jobs.length} shards, concurrency ${defaultConcurrency()}\n`,
    );
    const wall0 = Date.now();
    const aggs = await runShards(jobs);
    const wallSecs = (Date.now() - wall0) / 1000;

    // Merge shards back per komi.
    const byKomi = new Map<number, ShardAggregate[]>();
    aggs.forEach((a, i) => {
        const k = jobKomi[i];
        if (!byKomi.has(k)) byKomi.set(k, []);
        byKomi.get(k)!.push(a);
    });

    let totalGames = 0;
    let sumShardSecs = 0;
    const rows: Row[] = [];
    for (const komi of KOMI_GRID) {
        const list = byKomi.get(komi)!;
        const games = list.reduce((s, a) => s + a.games, 0);
        const blackWins = list.reduce((s, a) => s + a.refWins, 0);
        const whiteWins = list.reduce((s, a) => s + a.oppWins, 0);
        const draws = list.reduce((s, a) => s + a.draws, 0);
        const sumMargin = list.reduce((s, a) => s + a.sumMargin, 0);
        const sumMoves = list.reduce((s, a) => s + a.sumMoves, 0);
        totalGames += games;
        sumShardSecs += list.reduce((s, a) => s + a.secs, 0);
        const p = blackWins / games;
        rows.push({
            komi,
            games,
            blackWins,
            whiteWins,
            draws,
            blackWinRate: p,
            ci95: 1.96 * Math.sqrt((p * (1 - p)) / games),
            avgMargin: sumMargin / games,
            avgMoves: sumMoves / games,
            drawRate: draws / games,
        });
    }

    console.log(`# Komi re-estimate (parallel) — ${N}^3, MCTS(${PLAYOUTS}), ${GAMES} games/komi\n`);
    console.log("komi  | blackWin% (±95%) | draw% | avgMargin | avgMoves");
    console.log("------|------------------|-------|-----------|---------");
    for (const r of rows) {
        console.log(
            `${r.komi.toFixed(1).padStart(5)} | ${(100 * r.blackWinRate).toFixed(1)}% ` +
                `(±${(100 * r.ci95).toFixed(1)}) | ${(100 * r.drawRate).toFixed(1).padStart(4)}% | ` +
                `${r.avgMargin.toFixed(2).padStart(9)} | ${r.avgMoves.toFixed(1).padStart(8)}`,
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
    // Mean-margin-fair komi: the komi at which mean (black−white) score is zero.
    // avgMargin here already folds komi in; recover komi0 mean diff from the
    // komi=−0.5/0.5 rows is messy, so report the win-rate crossing as primary.
    console.log(
        crossing === null
            ? `\n≈ fair komi (win-rate 50% crossing): not bracketed in grid`
            : `\n≈ fair komi (win-rate 50% crossing): ${crossing.toFixed(2)}`,
    );
    const coreRate = totalGames / sumShardSecs;
    const parRate = totalGames / wallSecs;
    console.log(
        `throughput: ${coreRate.toFixed(1)} games/s/core × ~${(parRate / coreRate).toFixed(1)} ` +
            `effective = ${parRate.toFixed(1)} games/s wall (${totalGames} games in ${wallSecs.toFixed(0)}s)`,
    );

    const out = process.env.OUT;
    if (out) {
        fs.writeFileSync(
            out,
            JSON.stringify(
                {
                    n: N,
                    playouts: PLAYOUTS,
                    gamesPerKomi: GAMES,
                    shardsPerKomi: SHARDS,
                    rows,
                    crossing,
                    throughput: { coreRate, parRate, wallSecs, totalGames },
                },
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
