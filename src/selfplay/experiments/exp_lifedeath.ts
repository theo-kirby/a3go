/*
 * Q4 — life & death in 3D Go. What eye space is unconditionally alive on a
 * 6-neighbor lattice, and does it differ from 2D?
 *
 * Construction: fill an N^3 board entirely with the defender's stones except a
 * carved-out empty "cavity" (the eye space). The defender group's ONLY liberties
 * are the cavity points (the board boundary seals the outside), so the whole
 * life/death question reduces to a finite search inside the cavity.
 *
 * Test (unconditional life): with the ATTACKER moving first and both sides
 * playing optimally, can the attacker capture the defender group? If not, the
 * shape is unconditionally alive. This is the standard "killer plays first" test,
 * so e.g. a three-in-a-row eye space is DEAD (killer takes the vital point),
 * while two separated eyes are ALIVE (killer has no legal move).
 *
 * We run identical eye-space shapes in genuinely-2D topology (depth=1) and in the
 * 3D interior to isolate what 6-connectivity changes.
 *
 *   npx tsx src/selfplay/experiments/exp_lifedeath.ts
 */
import * as fs from "fs";
import { BoardState3D, Intersection3D } from "../../engine/BoardState3D";
import { JGOFNumericPlayerColor } from "../../engine/formats/JGOF";

const B = JGOFNumericPlayerColor.BLACK;
const W = JGOFNumericPlayerColor.WHITE;
const EMPTY = JGOFNumericPlayerColor.EMPTY;
const other = (c: JGOFNumericPlayerColor) => (c === B ? W : B);

const MAX_NODES = 4_000_000;

interface Budget {
    n: number;
    over: boolean;
}

const seedAlive = (s: BoardState3D, seed: Intersection3D, def: JGOFNumericPlayerColor) =>
    s.getStone(seed.x, seed.y, seed.z) === def;

function emptyPoints(s: BoardState3D): Intersection3D[] {
    const pts: Intersection3D[] = [];
    s.topology.forEachPoint((x, y, z) => {
        if (s.getStone(x, y, z) === EMPTY) pts.push({ x, y, z });
    });
    return pts;
}

/* Memo across the search: position hash (excludes side-to-move) + side + role.
 * Depth is intentionally generous (cavities are tiny + superko bounds repetition),
 * so we memoize on position rather than depth. */
type Role = "atk" | "def";
function key(s: BoardState3D, player: JGOFNumericPlayerColor, role: Role): string {
    return `${role}:${player}:${s.hashPosition()}`;
}

function attackerCanKill(
    s: BoardState3D,
    seed: Intersection3D,
    def: JGOFNumericPlayerColor,
    depth: number,
    budget: Budget,
    memo: Map<string, boolean>,
): boolean {
    if (!seedAlive(s, seed, def)) return true; // group already captured
    if (depth <= 0) return false; // survived the horizon -> treat as alive
    if (budget.n++ > MAX_NODES) {
        budget.over = true;
        return false;
    }
    const atk = other(def);
    const k = key(s, atk, "atk");
    const cached = memo.get(k);
    if (cached !== undefined) return cached;

    let result = false;
    for (const L of emptyPoints(s)) {
        const t = s.clone();
        t.player = atk;
        try {
            t.play(L.x, L.y, L.z);
        } catch {
            continue; // illegal (e.g. suicide into an eye) — try another point
        }
        if (!seedAlive(t, seed, def)) {
            result = true; // this move captured the group
            break;
        }
        if (!defenderCanLive(t, seed, def, depth - 1, budget, memo)) {
            result = true;
            break;
        }
    }
    memo.set(k, result);
    return result;
}

function defenderCanLive(
    s: BoardState3D,
    seed: Intersection3D,
    def: JGOFNumericPlayerColor,
    depth: number,
    budget: Budget,
    memo: Map<string, boolean>,
): boolean {
    if (!seedAlive(s, seed, def)) return false;
    if (depth <= 0) return true;
    if (budget.n++ > MAX_NODES) {
        budget.over = true;
        return true;
    }
    const k = key(s, def, "def");
    const cached = memo.get(k);
    if (cached !== undefined) return cached;

    let result = false;
    // Option 1: defender passes (usually correct — playing in your own eyes is bad).
    if (!attackerCanKill(s, seed, def, depth - 1, budget, memo)) {
        result = true;
    }
    // Option 2: defender plays a point (e.g. to split a big eye into two).
    if (!result) {
        for (const L of emptyPoints(s)) {
            const t = s.clone();
            t.player = def;
            try {
                t.play(L.x, L.y, L.z);
            } catch {
                continue;
            }
            if (!seedAlive(t, seed, def)) continue; // self-destructive
            if (!attackerCanKill(t, seed, def, depth - 1, budget, memo)) {
                result = true;
                break;
            }
        }
    }
    memo.set(k, result);
    return result;
}

interface Shape {
    label: string;
    dims: "2D" | "3D";
    size: { w: number; h: number; d: number };
    cavity: Intersection3D[];
    seed: Intersection3D;
}

/** Build the filled board minus the cavity; defender = Black. */
function buildBoard(sh: Shape): BoardState3D {
    const s = new BoardState3D({ width: sh.size.w, height: sh.size.h, depth: sh.size.d });
    s.topology.forEachPoint((x, y, z) => s.setStone(x, y, z, B));
    for (const c of sh.cavity) s.setStone(c.x, c.y, c.z, EMPTY);
    return s;
}

const P = (x: number, y: number, z: number): Intersection3D => ({ x, y, z });

// 2D shapes live in a depth=1 plane; 3D shapes are carved in the interior of a
// bulk board (seed at a corner is always part of the sealing wall).
const shapes: Shape[] = [
    {
        label: "1 point (single eye)",
        dims: "3D",
        size: { w: 3, h: 3, d: 3 },
        cavity: [P(1, 1, 1)],
        seed: P(0, 0, 0),
    },
    {
        label: "2 points adjacent (domino)",
        dims: "3D",
        size: { w: 4, h: 3, d: 3 },
        cavity: [P(1, 1, 1), P(2, 1, 1)],
        seed: P(0, 0, 0),
    },
    {
        label: "2 separated eyes",
        dims: "3D",
        size: { w: 5, h: 3, d: 3 },
        cavity: [P(1, 1, 1), P(3, 1, 1)],
        seed: P(0, 0, 0),
    },
    {
        label: "straight-3",
        dims: "2D",
        size: { w: 5, h: 3, d: 1 },
        cavity: [P(1, 1, 0), P(2, 1, 0), P(3, 1, 0)],
        seed: P(0, 0, 0),
    },
    {
        label: "straight-3",
        dims: "3D",
        size: { w: 5, h: 3, d: 3 },
        cavity: [P(1, 1, 1), P(2, 1, 1), P(3, 1, 1)],
        seed: P(0, 0, 0),
    },
    {
        label: "straight-4",
        dims: "2D",
        size: { w: 6, h: 3, d: 1 },
        cavity: [P(1, 1, 0), P(2, 1, 0), P(3, 1, 0), P(4, 1, 0)],
        seed: P(0, 0, 0),
    },
    {
        label: "straight-4",
        dims: "3D",
        size: { w: 6, h: 3, d: 3 },
        cavity: [P(1, 1, 1), P(2, 1, 1), P(3, 1, 1), P(4, 1, 1)],
        seed: P(0, 0, 0),
    },
    {
        label: "2x2 square (square-four)",
        dims: "2D",
        size: { w: 4, h: 4, d: 1 },
        cavity: [P(1, 1, 0), P(2, 1, 0), P(1, 2, 0), P(2, 2, 0)],
        seed: P(0, 0, 0),
    },
    {
        label: "2x2 square (planar, in 3D bulk)",
        dims: "3D",
        size: { w: 4, h: 4, d: 3 },
        cavity: [P(1, 1, 1), P(2, 1, 1), P(1, 2, 1), P(2, 2, 1)],
        seed: P(0, 0, 0),
    },
    {
        label: "bent-3 (planar L)",
        dims: "3D",
        size: { w: 4, h: 4, d: 3 },
        cavity: [P(1, 1, 1), P(2, 1, 1), P(1, 2, 1)],
        seed: P(0, 0, 0),
    },
    {
        label: "bent-3 (non-planar, uses +z)",
        dims: "3D",
        size: { w: 4, h: 3, d: 4 },
        cavity: [P(1, 1, 1), P(2, 1, 1), P(1, 1, 2)],
        seed: P(0, 0, 0),
    },
    {
        label: "3D tripod-4 (pt + 1 step per axis)",
        dims: "3D",
        size: { w: 4, h: 4, d: 4 },
        cavity: [P(1, 1, 1), P(2, 1, 1), P(1, 2, 1), P(1, 1, 2)],
        seed: P(0, 0, 0),
    },
    {
        label: "straight-5",
        dims: "2D",
        size: { w: 7, h: 3, d: 1 },
        cavity: [P(1, 1, 0), P(2, 1, 0), P(3, 1, 0), P(4, 1, 0), P(5, 1, 0)],
        seed: P(0, 0, 0),
    },
    {
        label: "straight-5",
        dims: "3D",
        size: { w: 7, h: 3, d: 3 },
        cavity: [P(1, 1, 1), P(2, 1, 1), P(3, 1, 1), P(4, 1, 1), P(5, 1, 1)],
        seed: P(0, 0, 0),
    },
    {
        label: "planar cross-5 (+ shape)",
        dims: "3D",
        size: { w: 5, h: 5, d: 3 },
        cavity: [P(2, 2, 1), P(1, 2, 1), P(3, 2, 1), P(2, 1, 1), P(2, 3, 1)],
        seed: P(0, 0, 0),
    },
    {
        label: "3D octahedron-7 (pt + all 6 nbrs)",
        dims: "3D",
        size: { w: 3, h: 3, d: 3 },
        cavity: [
            P(1, 1, 1),
            P(0, 1, 1),
            P(2, 1, 1),
            P(1, 0, 1),
            P(1, 2, 1),
            P(1, 1, 0),
            P(1, 1, 2),
        ],
        seed: P(0, 0, 0),
    },
    {
        label: "2x2x2 cube",
        dims: "3D",
        size: { w: 4, h: 4, d: 4 },
        cavity: [
            P(1, 1, 1),
            P(2, 1, 1),
            P(1, 2, 1),
            P(2, 2, 1),
            P(1, 1, 2),
            P(2, 1, 2),
            P(1, 2, 2),
            P(2, 2, 2),
        ],
        seed: P(0, 0, 0),
    },
];

console.log("# Q4 — life & death: which eye-space shapes are unconditionally alive?\n");
console.log("(attacker moves first; ALIVE = attacker cannot capture with optimal play)\n");
console.log("shape                                | dims | vol | VERDICT   | nodes      | note");
console.log("-------------------------------------|------|-----|-----------|------------|-----");

const out: Record<string, unknown>[] = [];
for (const sh of shapes) {
    const s = buildBoard(sh);
    const vol = sh.cavity.length;
    const depth = vol * 2 + 8;
    const budget: Budget = { n: 0, over: false };
    const memo = new Map<string, boolean>();
    const killed = attackerCanKill(s, sh.seed, B, depth, budget, memo);
    const alive = !killed && !budget.over;
    const note = budget.over ? "INCOMPLETE (node budget hit)" : "";
    out.push({
        label: sh.label,
        dims: sh.dims,
        volume: vol,
        alive,
        searchComplete: !budget.over,
        nodes: budget.n,
    });
    console.log(
        `${sh.label.padEnd(36)} | ${sh.dims.padEnd(4)} | ${String(vol).padStart(3)} | ` +
            `${(budget.over ? "?UNKNOWN" : alive ? "ALIVE" : "DEAD").padEnd(9)} | ` +
            `${String(budget.n).padStart(10)} | ${note}`,
    );
}

console.log(
    "\nReading: compare each shape's 2D vs 3D verdict and the minimum volume that\n" +
        "is unconditionally alive. Two separated eyes should be ALIVE in both; small\n" +
        "single eye spaces DEAD. Differences between the 2D and 3D rows are exactly\n" +
        "what 6-connectivity changes about life & death.",
);

const outfile = process.env.OUT;
if (outfile) {
    fs.writeFileSync(outfile, JSON.stringify(out, null, 2));
    console.log(`\nWrote → ${outfile}`);
}
