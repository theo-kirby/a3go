/*
 * Experiment: do ladders work in 3D Go?
 *
 * A ladder is a forced capture that works by keeping the victim at exactly 2
 * liberties: attacker ataris (->1 liberty), defender must extend (->2), repeat
 * until the edge. We implement a correct minimax ladder solver (with the
 * standard "victim reaches >=3 liberties => escaped" pruning) and run it on
 * identical setups in a genuinely-2D plane (depth=1) vs open 3D space.
 *
 * Mechanism under test: a ladder depends on the attacker being able to keep the
 * victim pinned at 2 liberties. The crux variable is how many liberties a forced
 * extension gains, which depends on the local connectivity (4-neighbor 2D vs
 * 6-neighbor 3D). The `libsAfter1stExtend` column and the WORKS? verdict per
 * scenario are what answer whether ladders survive 6-connectivity — read them
 * off the output rather than assuming.
 *
 *   npx tsx src/selfplay/experiments/exp_ladders.ts
 */
import * as fs from "fs";
import { BoardState3D, Intersection3D } from "../../engine/BoardState3D";
import { JGOFNumericPlayerColor } from "../../engine/formats/JGOF";

const other = (c: JGOFNumericPlayerColor): JGOFNumericPlayerColor =>
    c === JGOFNumericPlayerColor.BLACK
        ? JGOFNumericPlayerColor.WHITE
        : JGOFNumericPlayerColor.BLACK;

const victimGroup = (s: BoardState3D, seed: Intersection3D) =>
    s.getRawStoneString(seed.x, seed.y, seed.z);
const victimAlive = (s: BoardState3D, seed: Intersection3D, c: JGOFNumericPlayerColor) =>
    s.getStone(seed.x, seed.y, seed.z) === c;
const libCount = (s: BoardState3D, seed: Intersection3D) => s.countLiberties(victimGroup(s, seed));

const DEPTH = 24;
/* A ladder keeps the victim at <=2 liberties (attacker ataris to 1, defender
 * extends back to 2). If the victim ever reaches 3+ liberties, no single-move
 * atari threatens it and the ladder is broken — so 3 is the correct escape
 * threshold for the solver. Whether a given scenario's forced extension stays
 * at 2 or jumps past the cap is exactly what the experiment measures. */
const LIBCAP = 3;

/* Full bounded minimax. attackerCanCapture: atk to move, returns true iff the
 * attacker has a forced capture of the seed group. defenderCanEscape: defender
 * to move, returns true iff the defender can avoid capture. Both sides try every
 * liberty of the victim group (the only moves that change the capturing race);
 * bounded by depth and the LIBCAP escape prune. */
function attackerCanCapture(
    s: BoardState3D,
    seed: Intersection3D,
    atk: JGOFNumericPlayerColor,
    victimColor: JGOFNumericPlayerColor,
    depth: number,
): boolean {
    if (!victimAlive(s, seed, victimColor)) return true;
    const libs = s.getLiberties(victimGroup(s, seed));
    if (libs.length >= LIBCAP) return false; // victim escaped
    if (depth <= 0) return false;
    for (const L of libs) {
        const t = s.clone();
        t.player = atk;
        try {
            t.play(L.x, L.y, L.z);
        } catch {
            continue;
        }
        if (!victimAlive(t, seed, victimColor)) return true;
        if (!defenderCanEscape(t, seed, atk, victimColor, depth - 1)) return true;
    }
    return false;
}

function defenderCanEscape(
    s: BoardState3D,
    seed: Intersection3D,
    atk: JGOFNumericPlayerColor,
    victimColor: JGOFNumericPlayerColor,
    depth: number,
): boolean {
    if (!victimAlive(s, seed, victimColor)) return false; // captured
    const libs = s.getLiberties(victimGroup(s, seed));
    if (libs.length >= LIBCAP) return true; // safely escaped
    if (depth <= 0) return true; // not captured within horizon -> treat as escaped
    for (const L of libs) {
        const t = s.clone();
        t.player = victimColor;
        try {
            t.play(L.x, L.y, L.z);
        } catch {
            continue; // this extension illegal (e.g. suicide); try another liberty
        }
        if (
            victimAlive(t, seed, victimColor) &&
            !attackerCanCapture(t, seed, atk, victimColor, depth - 1)
        ) {
            return true; // found a surviving line
        }
    }
    return false; // every defender move leads to capture
}

interface Scenario {
    label: string;
    state: BoardState3D;
    seed: Intersection3D;
    attacker: JGOFNumericPlayerColor;
    victim: JGOFNumericPlayerColor;
    initialLibs: number;
    libsAfterFirstExtend: number | null;
}

const B = JGOFNumericPlayerColor.BLACK;
const W = JGOFNumericPlayerColor.WHITE;

/** Build a victim at exactly 2 liberties, attacker to move, leaving `open`
 *  directions free. Also measures the victim's liberties after the first forced
 *  atari+extend, which is the crux of the 2D-vs-3D difference. */
function build(
    label: string,
    size: { w: number; h: number; d: number },
    seed: Intersection3D,
    openDirs: Intersection3D[],
): Scenario {
    const s = new BoardState3D({ width: size.w, height: size.h, depth: size.d, player: W });
    s.setStone(seed.x, seed.y, seed.z, B); // victim is black
    // Fill every in-bounds neighbor of the seed with white EXCEPT the open dirs.
    const openKey = new Set(openDirs.map((o) => `${seed.x + o.x},${seed.y + o.y},${seed.z + o.z}`));
    s.topology.forEachNeighbor(seed.x, seed.y, seed.z, (nx, ny, nz) => {
        if (!openKey.has(`${nx},${ny},${nz}`)) {
            s.setStone(nx, ny, nz, W);
        }
    });
    const initialLibs = libCount(s, seed);
    // Measure libs after attacker ataris on the first open dir and defender extends the other.
    let libsAfterFirstExtend: number | null = null;
    const libs = s.getLiberties(victimGroup(s, seed));
    if (libs.length === 2) {
        const t = s.clone();
        t.player = W;
        try {
            t.play(libs[0].x, libs[0].y, libs[0].z); // atari
            const l2 = t.getLiberties(victimGroup(t, seed));
            if (l2.length === 1) {
                t.player = B;
                t.play(l2[0].x, l2[0].y, l2[0].z); // extend
                if (victimAlive(t, seed, B)) {
                    libsAfterFirstExtend = libCount(t, seed);
                }
            }
        } catch {
            /* ignore measurement failure */
        }
    }
    return { label, state: s, seed, attacker: W, victim: B, initialLibs, libsAfterFirstExtend };
}

const scenarios: Scenario[] = [
    // (A) Genuinely 2D plane (depth=1): victim at (1,1) chased INTO the (0,0)
    // corner. Attacker on the two center-ward neighbors; victim's 2 liberties
    // point at the corner. The depth=1 control: local topology is genuinely 2D.
    build("A. 2D plane 5x5x1, chased into corner", { w: 5, h: 5, d: 1 }, { x: 1, y: 1, z: 0 }, [
        { x: -1, y: 0, z: 0 },
        { x: 0, y: -1, z: 0 },
    ]),
    // (B) IDENTICAL attack, but the board has a 2nd z-layer (depth=2). The only
    // difference is the victim now has a z+1 neighbor into the bulk. Isolates
    // the single variable: does one extra dimension change the outcome?
    build("B. 3D surface 5x5x2 (same attack +z leak)", { w: 5, h: 5, d: 2 }, { x: 1, y: 1, z: 0 }, [
        { x: -1, y: 0, z: 0 },
        { x: 0, y: -1, z: 0 },
        { x: 0, y: 0, z: 1 },
    ]),
    // (C) Open 3D interior: victim deep inside a 5^3, 2 liberties toward a corner.
    // The fully-3D case (6-neighbor interior point).
    build("C. 3D open interior 5x5x5", { w: 5, h: 5, d: 5 }, { x: 2, y: 2, z: 2 }, [
        { x: -1, y: 0, z: 0 },
        { x: 0, y: 0, z: -1 },
    ]),
];

console.log("# Do ladders work in 3D Go?\n");
console.log(
    "scenario                                  | initLibs | libsAfter1stExtend | LADDER WORKS?",
);
console.log(
    "------------------------------------------|----------|--------------------|-------------",
);
const out: Record<string, unknown>[] = [];
for (const sc of scenarios) {
    const works = attackerCanCapture(sc.state.clone(), sc.seed, sc.attacker, sc.victim, DEPTH);
    out.push({
        label: sc.label,
        initialLibs: sc.initialLibs,
        libsAfterFirstExtend: sc.libsAfterFirstExtend,
        ladderWorks: works,
    });
    console.log(
        `${sc.label.padEnd(41)} | ${String(sc.initialLibs).padStart(8)} | ` +
            `${String(sc.libsAfterFirstExtend ?? "n/a").padStart(18)} | ${works ? "YES (capture)" : "NO (escapes)"}`,
    );
}

console.log(
    "\nReading: a ladder needs the victim pinned at 2 liberties. Track\n" +
        "libsAfter1stExtend per scenario: if a forced extension leaves the victim at 2\n" +
        "it can be re-ataried and the ladder continues; if it climbs past the escape cap,\n" +
        "atari cannot be maintained. Compare the genuinely-2D plane (A), the surface\n" +
        "scenario (B), and the open 3D interior (C) to see how connectivity affects the\n" +
        "outcome.",
);

const outfile = process.env.OUT;
if (outfile) {
    fs.writeFileSync(outfile, JSON.stringify(out, null, 2));
    console.log(`\nWrote → ${outfile}`);
}
