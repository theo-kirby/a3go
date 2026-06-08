/*
 * Self-play shard worker. Plays one shard of games for a single (size, komi,
 * playouts) cell and prints a JSON aggregate to stdout — nothing else goes to
 * stdout so the parent can parse it cleanly (diagnostics go to stderr).
 *
 * This is the unit of parallelism: the orchestrator in ./parallel.ts spawns many
 * of these as independent OS processes (one per core), each with a distinct
 * seedBase, then merges their aggregates. Single-threaded by itself; throughput
 * comes from running many shards at once.
 *
 * Job spec (argv[2], JSON):
 *   { mode: "selfplay" | "vsrandom", n, komi, playouts, games, seedBase }
 * - selfplay: equal-strength MCTS (Black) vs MCTS (White), both at `komi`,
 *   Black always first. Used for komi sweeps and board characterization.
 * - vsrandom: MCTS vs uniform-random, color-balanced (A is MCTS), at `komi`.
 *   Used for the strength baseline on larger boards.
 */
import { BoardState3D } from "../engine/BoardState3D";
import { MCTSAgent } from "./mcts";
import { RandomAgent } from "./agents";
import { playGame } from "./playGame";

interface Job {
    mode: "selfplay" | "vsrandom";
    n: number;
    komi: number;
    playouts: number;
    games: number;
    seedBase: number;
}

export interface ShardAggregate {
    mode: string;
    n: number;
    komi: number;
    playouts: number;
    games: number;
    /** Wins for the reference side: Black in selfplay, the MCTS agent in vsrandom. */
    refWins: number;
    oppWins: number;
    draws: number;
    sumMargin: number;
    sumMoves: number;
    /** Sum and sum-of-squares of signed (blackArea − whiteArea) at the played komi. */
    sumDiff: number;
    sumDiff2: number;
    hitMoveCap: number;
    secs: number;
}

function runSelfplay(job: Job): ShardAggregate {
    let refWins = 0;
    let oppWins = 0;
    let draws = 0;
    let sumMargin = 0;
    let sumMoves = 0;
    let sumDiff = 0;
    let sumDiff2 = 0;
    let hitMoveCap = 0;
    const t0 = Date.now();

    for (let i = 0; i < job.games; i++) {
        const state = new BoardState3D({ width: job.n, height: job.n, depth: job.n });
        const black = new MCTSAgent({
            playouts: job.playouts,
            seed: job.seedBase + i,
            komi: job.komi,
            name: "B",
        });
        const white = new MCTSAgent({
            playouts: job.playouts,
            seed: job.seedBase + 500000 + i,
            komi: job.komi,
            name: "W",
        });
        const r = playGame(state, black, white, { komi: job.komi });
        if (r.winner === "black") refWins++;
        else if (r.winner === "white") oppWins++;
        else draws++;
        sumMargin += r.margin;
        sumMoves += r.moveCount;
        sumDiff += r.diff;
        sumDiff2 += r.diff * r.diff;
        if (r.hitMoveCap) hitMoveCap++;
    }

    return {
        mode: job.mode,
        n: job.n,
        komi: job.komi,
        playouts: job.playouts,
        games: job.games,
        refWins,
        oppWins,
        draws,
        sumMargin,
        sumMoves,
        sumDiff,
        sumDiff2,
        hitMoveCap,
        secs: (Date.now() - t0) / 1000,
    };
}

function runVsRandom(job: Job): ShardAggregate {
    let refWins = 0; // MCTS wins
    let oppWins = 0; // random wins
    let draws = 0;
    let sumMargin = 0;
    let sumMoves = 0;
    let sumDiff = 0;
    let sumDiff2 = 0;
    let hitMoveCap = 0;
    const t0 = Date.now();

    for (let i = 0; i < job.games; i++) {
        const mctsIsBlack = i % 2 === 0;
        const state = new BoardState3D({ width: job.n, height: job.n, depth: job.n });
        const mcts = new MCTSAgent({
            playouts: job.playouts,
            seed: job.seedBase + i,
            komi: job.komi,
            name: "MCTS",
        });
        const rand = new RandomAgent(job.seedBase + 500000 + i, "random");
        const black = mctsIsBlack ? mcts : rand;
        const white = mctsIsBlack ? rand : mcts;
        const r = playGame(state, black, white, { komi: job.komi });
        const mctsWon = (r.winner === "black") === mctsIsBlack && r.winner !== "draw";
        if (r.winner === "draw") draws++;
        else if (mctsWon) refWins++;
        else oppWins++;
        sumMargin += r.margin;
        sumMoves += r.moveCount;
        sumDiff += r.diff;
        sumDiff2 += r.diff * r.diff;
        if (r.hitMoveCap) hitMoveCap++;
    }

    return {
        mode: job.mode,
        n: job.n,
        komi: job.komi,
        playouts: job.playouts,
        games: job.games,
        refWins,
        oppWins,
        draws,
        sumMargin,
        sumMoves,
        sumDiff,
        sumDiff2,
        hitMoveCap,
        secs: (Date.now() - t0) / 1000,
    };
}

function main(): void {
    const raw = process.argv[2];
    if (!raw) {
        process.stderr.write("worker_selfplay: missing job JSON arg\n");
        process.exit(2);
    }
    const job = JSON.parse(raw) as Job;
    const agg = job.mode === "vsrandom" ? runVsRandom(job) : runSelfplay(job);
    process.stdout.write(JSON.stringify(agg));
}

main();
