/*
 * Parallel self-play orchestrator. Fans self-play shards out across CPU cores by
 * spawning ./worker_selfplay.ts as independent `tsx` processes (true OS-level
 * parallelism, sidestepping Node's single-threaded execution). Each shard is a
 * (size, komi, playouts, games, seedBase) cell; this module runs a pool of them
 * with bounded concurrency and returns their parsed aggregates.
 *
 * Why processes (not worker_threads): the engine is CPU-bound and the runners are
 * single-threaded by construction (see BOOTSTRAP.md) — separate processes give
 * clean linear scaling to the 16c/32t box with no shared-state hazards.
 */
import { spawn } from "child_process";
import * as os from "os";
import * as path from "path";
import { fileURLToPath } from "url";
import type { ShardAggregate } from "./worker_selfplay";

export interface ShardJob {
    mode: "selfplay" | "vsrandom";
    n: number;
    komi: number;
    playouts: number;
    games: number;
    seedBase: number;
}

const WORKER = path.join(path.dirname(fileURLToPath(import.meta.url)), "worker_selfplay.ts");

/** Default pool size: leave a couple of threads for the OS / orchestrator. */
export function defaultConcurrency(): number {
    return Math.max(1, os.cpus().length - 2);
}

function runOne(job: ShardJob): Promise<ShardAggregate> {
    return new Promise((resolve, reject) => {
        const child = spawn("npx", ["tsx", WORKER, JSON.stringify(job)], {
            stdio: ["ignore", "pipe", "pipe"],
        });
        let out = "";
        let err = "";
        child.stdout.on("data", (d) => (out += d.toString()));
        child.stderr.on("data", (d) => (err += d.toString()));
        child.on("error", reject);
        child.on("close", (code) => {
            if (code !== 0) {
                reject(new Error(`shard exited ${code}: ${err.slice(0, 500)}`));
                return;
            }
            try {
                resolve(JSON.parse(out.trim()) as ShardAggregate);
            } catch (e) {
                reject(new Error(`shard bad JSON (${String(e)}): ${out.slice(0, 300)}`));
            }
        });
    });
}

/**
 * Run all `jobs` with at most `concurrency` workers active at once. Resolves to
 * the aggregates in the same order as `jobs`. Progress is logged to stderr.
 */
export async function runShards(
    jobs: ShardJob[],
    concurrency = defaultConcurrency(),
): Promise<ShardAggregate[]> {
    const results = new Array<ShardAggregate>(jobs.length);
    let next = 0;
    let done = 0;

    async function worker(): Promise<void> {
        while (true) {
            const idx = next++;
            if (idx >= jobs.length) return;
            results[idx] = await runOne(jobs[idx]);
            done++;
            process.stderr.write(`\r  shards ${done}/${jobs.length} done`);
        }
    }

    const pool = Array.from({ length: Math.min(concurrency, jobs.length) }, () => worker());
    await Promise.all(pool);
    process.stderr.write("\n");
    return results;
}
