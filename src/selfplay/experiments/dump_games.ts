/*
 * Cross-validation fixture generator: play K seeded uniform-random self-play
 * games on an N³ board, recording the exact move list and the Tromp-Taylor score
 * breakdown (komi 0) for each. The Python engine port (neural/a3go_engine.py)
 * replays these move lists and must reproduce the identical final score — a
 * strong equivalence check between the TS reference engine and the port.
 *
 *   npx tsx src/selfplay/experiments/dump_games.ts [n] [games] [seed] > fixture.json
 *   (writes JSON to stdout; progress to stderr)
 */
import { BoardState3D } from "../../engine/BoardState3D";
import { JGOFNumericPlayerColor } from "../../engine/formats/JGOF";
import { scoreTrompTaylor } from "../../engine/Scorer3D";
import { RandomAgent, Move } from "../agents";

const N = Number(process.argv[2] ?? 4);
const GAMES = Number(process.argv[3] ?? 50);
const SEED = Number(process.argv[4] ?? 12345);

interface DumpedGame {
    n: number;
    moves: Array<[number, number, number] | "pass">;
    blackStones: number;
    whiteStones: number;
    blackTerritory: number;
    whiteTerritory: number;
    neutral: number;
    diff: number;
    winner: string;
}

const games: DumpedGame[] = [];
for (let g = 0; g < GAMES; g++) {
    const state = new BoardState3D({ width: N, height: N, depth: N });
    const black = new RandomAgent(SEED + g, "B");
    const white = new RandomAgent(SEED + 100000 + g, "W");
    const moves: Array<[number, number, number] | "pass"> = [];
    let consecutivePasses = 0;
    const maxMoves = state.topology.numPoints * 8;
    let count = 0;
    while (consecutivePasses < 2 && count < maxMoves) {
        const agent = state.player === JGOFNumericPlayerColor.BLACK ? black : white;
        const m: Move = agent.selectMove(state);
        if (m === "pass") {
            state.pass();
            moves.push("pass");
            consecutivePasses++;
        } else {
            state.play(m.x, m.y, m.z);
            moves.push([m.x, m.y, m.z]);
            consecutivePasses = 0;
        }
        count++;
    }
    const s = scoreTrompTaylor(state, { komi: 0 });
    games.push({
        n: N,
        moves,
        blackStones: s.black.stones,
        whiteStones: s.white.stones,
        blackTerritory: s.blackTerritory.length,
        whiteTerritory: s.whiteTerritory.length,
        neutral: s.neutral.length,
        diff: s.diff,
        winner: s.winner,
    });
    if ((g + 1) % 10 === 0) process.stderr.write(`\r  dumped ${g + 1}/${GAMES}`);
}
process.stderr.write("\n");
process.stdout.write(JSON.stringify({ n: N, games: GAMES, seed: SEED, data: games }, null, 0));
