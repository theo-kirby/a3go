/*
 * Q5 — structural oddity: how 6-connectivity reshapes the board. For each N³ we
 * classify every intersection by its neighbor degree (3 = corner, 4 = edge,
 * 5 = face, 6 = interior) and report the counts/fractions, plus the mean degree.
 * This is the geometric substrate behind the tactical/L&D differences: in 2D an
 * interior point has 4 liberties and corners have 2; in 3D interior points have
 * 6 and corners have 3, and the high-degree interior dominates much faster as N
 * grows. Deterministic, instant.
 *
 *   npx tsx src/selfplay/experiments/exp_geometry.ts [sizesCSV]
 */
import * as fs from "fs";
import { BoardState3D } from "../../engine/BoardState3D";

const SIZES = (process.argv[2] ?? "3,4,5,7,9").split(",").map(Number);

interface Row {
    n: number;
    points: number;
    corner3: number; // degree-3 points (cube corners)
    edge4: number; // degree-4 points (cube edges)
    face5: number; // degree-5 points (cube faces)
    interior6: number; // degree-6 points (bulk)
    interiorFraction: number;
    meanDegree: number;
}

const rows: Row[] = [];
for (const n of SIZES) {
    const s = new BoardState3D({ width: n, height: n, depth: n });
    const counts: Record<number, number> = {};
    let degreeSum = 0;
    let points = 0;
    s.topology.forEachPoint((x, y, z) => {
        let deg = 0;
        s.topology.forEachNeighbor(x, y, z, () => deg++);
        counts[deg] = (counts[deg] ?? 0) + 1;
        degreeSum += deg;
        points++;
    });
    rows.push({
        n,
        points,
        corner3: counts[3] ?? 0,
        edge4: counts[4] ?? 0,
        face5: counts[5] ?? 0,
        interior6: counts[6] ?? 0,
        interiorFraction: (counts[6] ?? 0) / points,
        meanDegree: degreeSum / points,
    });
}

console.log("# Q5 — board geometry under 6-connectivity (degree distribution)\n");
console.log("N   | points | corner(3) | edge(4) | face(5) | interior(6) | interior% | meanDeg");
console.log("----|--------|-----------|---------|---------|-------------|-----------|--------");
for (const r of rows) {
    console.log(
        `${String(r.n).padStart(2)}³ | ${String(r.points).padStart(6)} | ` +
            `${String(r.corner3).padStart(9)} | ${String(r.edge4).padStart(7)} | ` +
            `${String(r.face5).padStart(7)} | ${String(r.interior6).padStart(11)} | ` +
            `${(100 * r.interiorFraction).toFixed(1).padStart(8)}% | ${r.meanDegree.toFixed(2).padStart(6)}`,
    );
}

console.log(
    "\nReading: 3D cube corners have degree 3 (vs 2 in a 2D square) and the bulk\n" +
        "has degree 6 (vs 4). The degree-6 interior — where extending a stone gains\n" +
        "liberties fast — overtakes the boundary as N grows, which is exactly why the\n" +
        "ladder (a 2-liberty pin) fails in the interior and why life needs more space.",
);

const out = process.env.OUT;
if (out) {
    fs.writeFileSync(out, JSON.stringify({ rows }, null, 2));
    console.log(`\nWrote → ${out}`);
}
