/*
 * Agents for headless 3D-Go self-play. An Agent looks at a board state and
 * returns a move; it must not mutate the state it is given. The uniform-random
 * agent here is the baseline; stronger agents (e.g. MCTS) implement the same
 * interface.
 */
import { BoardState3D, Intersection3D } from "../engine/BoardState3D";
import { JGOFNumericPlayerColor } from "../engine/formats/JGOF";

export type Move = Intersection3D | "pass";

export interface Agent {
    readonly name: string;
    /** Choose a move for the side to play. Must treat `state` as read-only. */
    selectMove(state: BoardState3D): Move;
}

/** Small deterministic PRNG (mulberry32) so games are reproducible from a seed. */
export function makeRng(seed: number): () => number {
    let a = seed >>> 0;
    return () => {
        a |= 0;
        a = (a + 0x6d2b79f5) | 0;
        let t = Math.imul(a ^ (a >>> 15), 1 | a);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

/** Is playing (x,y,z) legal for the side to move? Checked on a clone so the
 *  real game state is never touched. Relies on clone() preserving superko
 *  history, so superko-illegal moves are correctly reported illegal. */
export function isLegalMove(state: BoardState3D, x: number, y: number, z: number): boolean {
    const probe = state.clone();
    try {
        probe.play(x, y, z);
        return true;
    } catch {
        return false;
    }
}

/**
 * Is (x,y,z) a simple "eye" of `color` — an empty point whose every in-bounds
 * neighbor is a stone of that color? Filling your own eye is self-destructive
 * and (for single-point eyes) actually illegal as suicide, so the standard
 * rollout policy skips it. This is the pragmatic rollout definition (it does not
 * detect false eyes).
 */
export function isSimpleEye(
    state: BoardState3D,
    x: number,
    y: number,
    z: number,
    color: JGOFNumericPlayerColor,
): boolean {
    if (state.getStone(x, y, z) !== JGOFNumericPlayerColor.EMPTY) {
        return false;
    }
    let hasNeighbor = false;
    let allOwn = true;
    state.topology.forEachNeighbor(x, y, z, (nx, ny, nz) => {
        hasNeighbor = true;
        if (state.getStone(nx, ny, nz) !== color) {
            allOwn = false;
        }
    });
    return hasNeighbor && allOwn;
}

/** All empty intersections (candidate points, before legality filtering). */
export function emptyPoints(state: BoardState3D): Intersection3D[] {
    const pts: Intersection3D[] = [];
    state.topology.forEachPoint((x, y, z) => {
        if (state.getStone(x, y, z) === JGOFNumericPlayerColor.EMPTY) {
            pts.push({ x, y, z });
        }
    });
    return pts;
}

/**
 * Uniform-random agent over legal moves, with the standard rollout refinement
 * of NOT filling its own simple eyes. Passes when no legal non-eye move remains.
 *
 * Set `fillEyes: true` to recover the naive everything-legal behavior, for
 * comparison against the eye-aware policy.
 */
export class RandomAgent implements Agent {
    public readonly name: string;
    private rng: () => number;
    private fillEyes: boolean;

    constructor(seed: number, name = "random", opts: { fillEyes?: boolean } = {}) {
        this.rng = makeRng(seed);
        this.name = name;
        this.fillEyes = opts.fillEyes ?? false;
    }

    public selectMove(state: BoardState3D): Move {
        const color = state.player;
        const pts = emptyPoints(state);
        // Fisher–Yates shuffle, then return the first acceptable legal point.
        for (let i = pts.length - 1; i > 0; i--) {
            const j = Math.floor(this.rng() * (i + 1));
            [pts[i], pts[j]] = [pts[j], pts[i]];
        }
        for (const p of pts) {
            if (!this.fillEyes && isSimpleEye(state, p.x, p.y, p.z, color)) {
                continue;
            }
            if (isLegalMove(state, p.x, p.y, p.z)) {
                return p;
            }
        }
        return "pass";
    }
}
