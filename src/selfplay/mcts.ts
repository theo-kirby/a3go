/*
 * Classical MCTS (UCT) agent for 3D Go. Selection by UCB1, expansion one node
 * at a time, simulation by eye-aware random rollout (reusing RandomAgent),
 * backprop of the win/loss from the perspective of the side that moved.
 *
 * A classical baseline above uniform-random, intended as a reference opponent
 * for the komi / board-balance / strength questions.
 */
import { BoardState3D } from "../engine/BoardState3D";
import { JGOFNumericPlayerColor } from "../engine/formats/JGOF";
import { scoreTrompTaylor } from "../engine/Scorer3D";
import { Agent, Move, RandomAgent, emptyPoints, isLegalMove, isSimpleEye, makeRng } from "./agents";

const other = (c: JGOFNumericPlayerColor): JGOFNumericPlayerColor =>
    c === JGOFNumericPlayerColor.BLACK
        ? JGOFNumericPlayerColor.WHITE
        : JGOFNumericPlayerColor.BLACK;

const moveKey = (m: Move): string => (m === "pass" ? "pass" : `${m.x},${m.y},${m.z}`);

/** Candidate moves for the tree: legal non-self-eye plays, plus pass. */
function candidateMoves(state: BoardState3D): Move[] {
    const color = state.player;
    const moves: Move[] = [];
    for (const p of emptyPoints(state)) {
        if (isSimpleEye(state, p.x, p.y, p.z, color)) {
            continue;
        }
        if (isLegalMove(state, p.x, p.y, p.z)) {
            moves.push(p);
        }
    }
    moves.push("pass");
    return moves;
}

class TreeNode {
    public visits = 0;
    public wins = 0; // from the perspective of `moverColor` (who moved into this node)
    public readonly children = new Map<string, TreeNode>();
    public untried: Move[];
    constructor(
        public readonly state: BoardState3D,
        public readonly moverColor: JGOFNumericPlayerColor | null, // null at root
        public readonly consecutivePasses: number,
        public readonly parent: TreeNode | null,
        public readonly move: Move | null,
    ) {
        this.untried = candidateMoves(state);
    }
    public get isTerminal(): boolean {
        return this.consecutivePasses >= 2;
    }
}

export interface MCTSOptions {
    playouts: number;
    seed: number;
    komi?: number;
    /** UCB exploration constant. */
    c?: number;
    name?: string;
}

export class MCTSAgent implements Agent {
    public readonly name: string;
    private playouts: number;
    private komi: number;
    private c: number;
    private rng: () => number;
    private rolloutSeed: number;

    constructor(opts: MCTSOptions) {
        this.playouts = opts.playouts;
        this.komi = opts.komi ?? 0;
        this.c = opts.c ?? Math.SQRT2;
        this.rng = makeRng(opts.seed);
        this.rolloutSeed = (opts.seed ^ 0x9e3779b9) >>> 0;
        this.name = opts.name ?? `mcts(${this.playouts})`;
    }

    public selectMove(state: BoardState3D): Move {
        const root = new TreeNode(state.clone(), null, 0, null, null);
        if (root.isTerminal) {
            return "pass";
        }
        for (let i = 0; i < this.playouts; i++) {
            this.iterate(root);
        }
        // Pick the most-visited child (robust child).
        let best: TreeNode | null = null;
        for (const child of root.children.values()) {
            if (!best || child.visits > best.visits) {
                best = child;
            }
        }
        return best && best.move ? best.move : "pass";
    }

    private iterate(root: TreeNode): void {
        // 1. Selection
        let node = root;
        while (!node.isTerminal && node.untried.length === 0 && node.children.size > 0) {
            node = this.bestUCB(node);
        }
        // 2. Expansion
        if (!node.isTerminal && node.untried.length > 0) {
            const idx = Math.floor(this.rng() * node.untried.length);
            const move = node.untried.splice(idx, 1)[0];
            const childState = node.state.clone();
            let passes: number;
            if (move === "pass") {
                childState.pass();
                passes = node.consecutivePasses + 1;
            } else {
                childState.play(move.x, move.y, move.z);
                passes = 0;
            }
            const child = new TreeNode(childState, node.state.player, passes, node, move);
            node.children.set(moveKey(move), child);
            node = child;
        }
        // 3. Simulation (rollout) -> winner color
        const winner = this.rollout(node);
        // 4. Backprop
        for (let n: TreeNode | null = node; n !== null; n = n.parent) {
            n.visits++;
            if (n.moverColor !== null && winner === n.moverColor) {
                n.wins++;
            } else if (n.moverColor !== null && winner === "draw") {
                n.wins += 0.5;
            }
        }
    }

    private bestUCB(node: TreeNode): TreeNode {
        let best: TreeNode | null = null;
        let bestVal = -Infinity;
        const logN = Math.log(node.visits + 1);
        for (const child of node.children.values()) {
            const exploit = child.wins / child.visits;
            const explore = this.c * Math.sqrt(logN / child.visits);
            const val = exploit + explore;
            if (val > bestVal) {
                bestVal = val;
                best = child;
            }
        }
        return best!;
    }

    private rollout(node: TreeNode): JGOFNumericPlayerColor | "draw" {
        if (node.isTerminal) {
            const s = scoreTrompTaylor(node.state, { komi: this.komi });
            return s.winner === "black"
                ? JGOFNumericPlayerColor.BLACK
                : s.winner === "white"
                  ? JGOFNumericPlayerColor.WHITE
                  : "draw";
        }
        const state = node.state.clone();
        this.rolloutSeed = (this.rolloutSeed + 0x6d2b79f5) >>> 0;
        const black = new RandomAgent(this.rolloutSeed, "rollout");
        const white = new RandomAgent((this.rolloutSeed ^ 0x85ebca6b) >>> 0, "rollout");
        let consecutivePasses = node.consecutivePasses;
        const maxMoves = state.topology.numPoints * 8;
        let moves = 0;
        while (consecutivePasses < 2 && moves < maxMoves) {
            const agent = state.player === JGOFNumericPlayerColor.BLACK ? black : white;
            const m = agent.selectMove(state);
            if (m === "pass") {
                state.pass();
                consecutivePasses++;
            } else {
                state.play(m.x, m.y, m.z);
                consecutivePasses = 0;
            }
            moves++;
        }
        const s = scoreTrompTaylor(state, { komi: this.komi });
        return s.winner === "black"
            ? JGOFNumericPlayerColor.BLACK
            : s.winner === "white"
              ? JGOFNumericPlayerColor.WHITE
              : "draw";
    }
}
