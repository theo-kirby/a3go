/*
 * Public engine API for a3go. a3go-owned barrel over the vendored 3D Go engine
 * slice (see ./VENDORED.md for provenance). Import the engine from here rather
 * than reaching into individual files.
 */
export {
    BoardState3D,
    type Intersection3D,
    type RawStoneString3D,
    type BoardState3DConfig,
    type PlaceResult3D,
} from "./BoardState3D";
export { Topology2D, Topology3D, type Topology } from "./Topology";
export {
    scoreTrompTaylor,
    estimateScoreInfluence,
    type ScoreResult,
    type ScoreColorBreakdown,
    type ScoreOptions,
} from "./Scorer3D";
export { JGOFNumericPlayerColor } from "./formats/JGOF";
