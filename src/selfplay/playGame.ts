/*
 * Headless game runner: play a full 3D-Go game between two agents and score it.
 * The core loop that drives the engine at speed and produces game records for
 * self-play experiments.
 */
import { BoardState3D } from "../engine/BoardState3D";
import { JGOFNumericPlayerColor } from "../engine/formats/JGOF";
import { scoreTrompTaylor } from "../engine/Scorer3D";
import { Agent, Move } from "./agents";

export interface PlayGameOptions {
    komi?: number;
    /** Hard cap on moves (incl. passes) to bound pathological games. Default
     *  8 × numPoints — random play fills the board long before this. */
    maxMoves?: number;
    /** If set, record the full move list (small games only; off for benches). */
    recordMoves?: boolean;
}

export interface GameRecord {
    width: number;
    height: number;
    depth: number;
    komi: number;
    blackAgent: string;
    whiteAgent: string;
    winner: "black" | "white" | "draw";
    /** black.area − white.area (komi already folded into white). */
    diff: number;
    margin: number;
    moveCount: number;
    passes: number;
    blackPrisoners: number;
    whitePrisoners: number;
    /** True if the game ended by two consecutive passes (normal termination). */
    terminatedByPasses: boolean;
    /** True if the move cap was hit (pathological — should be ~never). */
    hitMoveCap: boolean;
    moves?: Move[];
}

/**
 * Play one game to completion. The game ends on two consecutive passes (normal
 * Go termination) and is then scored by Tromp-Taylor area scoring + komi.
 * `black` plays first.
 */
export function playGame(
    initial: BoardState3D,
    black: Agent,
    white: Agent,
    opts: PlayGameOptions = {},
): GameRecord {
    const komi = opts.komi ?? 0;
    const numPoints = initial.topology.numPoints;
    const maxMoves = opts.maxMoves ?? numPoints * 8;
    const state = initial.clone();
    const moves: Move[] | undefined = opts.recordMoves ? [] : undefined;

    let consecutivePasses = 0;
    let totalPasses = 0;
    let moveCount = 0;
    let hitMoveCap = false;

    while (true) {
        if (moveCount >= maxMoves) {
            hitMoveCap = true;
            break;
        }
        const toMove = state.player;
        const agent = toMove === JGOFNumericPlayerColor.BLACK ? black : white;
        const move = agent.selectMove(state);

        if (move === "pass") {
            state.pass();
            consecutivePasses++;
            totalPasses++;
            moves?.push("pass");
            moveCount++;
            if (consecutivePasses >= 2) {
                break;
            }
            continue;
        }

        // A legal-move-only agent should never hand us an illegal move; if it
        // does, surface it loudly rather than silently mis-scoring.
        state.play(move.x, move.y, move.z);
        consecutivePasses = 0;
        moves?.push(move);
        moveCount++;
    }

    const score = scoreTrompTaylor(state, { komi });
    return {
        width: state.width,
        height: state.height,
        depth: state.depth,
        komi,
        blackAgent: black.name,
        whiteAgent: white.name,
        winner: score.winner,
        diff: score.diff,
        margin: score.margin,
        moveCount,
        passes: totalPasses,
        blackPrisoners: state.black_prisoners,
        whitePrisoners: state.white_prisoners,
        terminatedByPasses: consecutivePasses >= 2,
        hitMoveCap,
        moves,
    };
}
