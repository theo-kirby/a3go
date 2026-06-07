/*
 * Color-balanced head-to-head match driver. Plays `games` games between two
 * agent factories, swapping who is Black each game so first-move advantage does
 * not bias the comparison. Returns win stats with a 95% CI on agent A.
 */
import { BoardState3D } from "../engine/BoardState3D";
import { Agent } from "./agents";
import { playGame } from "./playGame";

export type AgentFactory = (seed: number, name: string) => Agent;

export interface MatchOptions {
    n: number; // board size N (N^3)
    games: number;
    komi?: number;
    seedBase?: number;
}

export interface MatchResult {
    n: number;
    games: number;
    komi: number;
    aWins: number;
    bWins: number;
    draws: number;
    aWinRate: number;
    ci95: number;
    aAsBlackWins: number;
    aAsBlackGames: number;
    aAsWhiteWins: number;
    aAsWhiteGames: number;
    avgMoves: number;
    avgMargin: number;
    secs: number;
}

export function playMatch(
    makeA: AgentFactory,
    makeB: AgentFactory,
    opts: MatchOptions,
): MatchResult {
    const komi = opts.komi ?? 0;
    const seedBase = opts.seedBase ?? 1;
    let aWins = 0;
    let bWins = 0;
    let draws = 0;
    let aAsBlackWins = 0;
    let aAsBlackGames = 0;
    let aAsWhiteWins = 0;
    let aAsWhiteGames = 0;
    let sumMoves = 0;
    let sumMargin = 0;
    const t0 = Date.now();

    for (let i = 0; i < opts.games; i++) {
        const aIsBlack = i % 2 === 0;
        const state = new BoardState3D({ width: opts.n, height: opts.n, depth: opts.n });
        const a = makeA(seedBase + i, "A");
        const b = makeB(seedBase + 500000 + i, "B");
        const black = aIsBlack ? a : b;
        const white = aIsBlack ? b : a;
        const r = playGame(state, black, white, { komi });

        let aWon = false;
        if (r.winner === "draw") {
            draws++;
        } else if ((r.winner === "black") === aIsBlack) {
            aWins++;
            aWon = true;
        } else {
            bWins++;
        }
        if (aIsBlack) {
            aAsBlackGames++;
            if (aWon) aAsBlackWins++;
        } else {
            aAsWhiteGames++;
            if (aWon) aAsWhiteWins++;
        }
        sumMoves += r.moveCount;
        sumMargin += r.margin;
    }

    const secs = (Date.now() - t0) / 1000;
    const p = aWins / opts.games;
    return {
        n: opts.n,
        games: opts.games,
        komi,
        aWins,
        bWins,
        draws,
        aWinRate: p,
        ci95: 1.96 * Math.sqrt((p * (1 - p)) / opts.games),
        aAsBlackWins,
        aAsBlackGames,
        aAsWhiteWins,
        aAsWhiteGames,
        avgMoves: sumMoves / opts.games,
        avgMargin: sumMargin / opts.games,
        secs,
    };
}
