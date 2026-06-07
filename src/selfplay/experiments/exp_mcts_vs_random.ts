/*
 * Experiment: does MCTS beat the uniform-random baseline, and by how much?
 * Plays color-balanced matches across board sizes and reports MCTS win-rate
 * (95% CI), the color split, game length, margin, and throughput. Whether MCTS
 * clears a chosen "stronger than random" bar is for the run to decide from the
 * numbers, not assumed here.
 *
 *   npx tsx src/selfplay/experiments/exp_mcts_vs_random.ts [games] [playouts]
 */
import * as fs from "fs";
import { RandomAgent } from "../agents";
import { MCTSAgent } from "../mcts";
import { playMatch, MatchResult } from "../match";

const GAMES = Number(process.argv[2] ?? 60);
const PLAYOUTS = Number(process.argv[3] ?? 150);
const SIZES = [3, 4];

const makeRandom = (seed: number, name: string) => new RandomAgent(seed, name);
const makeMcts = (komi: number) => (seed: number, name: string) =>
    new MCTSAgent({ playouts: PLAYOUTS, seed, komi, name });

console.log(`# MCTS(${PLAYOUTS}) vs random — ${GAMES} games/size, color-balanced\n`);
console.log("size | MCTS win% (±95%) | asBlack | asWhite | avgMoves | avgMargin | s/match");
console.log("-----|------------------|---------|---------|----------|-----------|--------");

const results: MatchResult[] = [];
for (const n of SIZES) {
    const r = playMatch(makeMcts(0), makeRandom, { n, games: GAMES, komi: 0, seedBase: 100 + n });
    results.push(r);
    const pct = (x: number) => (100 * x).toFixed(1) + "%";
    console.log(
        `${n}^3  | ${pct(r.aWinRate)} (±${(100 * r.ci95).toFixed(1)}) | ` +
            `${r.aAsBlackWins}/${r.aAsBlackGames}     | ${r.aAsWhiteWins}/${r.aAsWhiteGames}     | ` +
            `${r.avgMoves.toFixed(1).padStart(8)} | ${r.avgMargin.toFixed(1).padStart(9)} | ${r.secs.toFixed(1).padStart(6)}`,
    );
}

const out = process.env.OUT;
if (out) {
    fs.writeFileSync(out, JSON.stringify({ playouts: PLAYOUTS, games: GAMES, results }, null, 2));
    console.log(`\nWrote → ${out}`);
}
