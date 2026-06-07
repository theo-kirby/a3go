/*
 * Public self-play API for a3go. Barrel over the vendored self-play stack:
 * agents (random + MCTS), the single-game runner, and the head-to-head match
 * driver. Reusable tooling for experiments under ./experiments/.
 */
export {
    type Agent,
    type Move,
    RandomAgent,
    makeRng,
    isLegalMove,
    isSimpleEye,
    emptyPoints,
} from "./agents";
export { MCTSAgent, type MCTSOptions } from "./mcts";
export { playGame, type PlayGameOptions, type GameRecord } from "./playGame";
export { playMatch, type AgentFactory, type MatchOptions, type MatchResult } from "./match";
