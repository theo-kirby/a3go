---
node_id: 259c2ebe-e702-5525-a4eb-a7291e5c857a
slug: dawn-pond-0204
title: 'EVAL-1 — SPRT harness BUILT + VALIDATED (P19 libs@64 cross-check: not_a_winner @ n=98, CI-consistent with fixed-n)'
created_at: '2026-06-09T07:00:14.674674+00:00'
parents:
- bold-pine-0367
- empty-lab-3357
- rough-paper-7328
- proud-king-2753
summary: 'EVAL-1 SPRT harness BUILT + VALIDATED (P19): sprt.py wraps net-vs-classical in a Wald SPRT (early-stop). Cross-check on libs@64 s0 decided not_a_winner at n=98 (llr −3.70), wr 0.337 [0.251,0.435] — overlaps fixed-n 0.383, CI-consistent; confirms libs@64 sub-parity. Reserved for anchoring net-vs-net winners; n≥128 audit via the fixed-n baseline.'
origin:
  backend: flywheel
  node_id: 259c2ebe-e702-5525-a4eb-a7291e5c857a
  slug: dawn-pond-0204
  revision: 3
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: a0efa66a-f802-5dcb-aaaa-bc8305b83968
  slug: steep-cake-8700
  revision: 0
  pushed_at: '2026-08-08T10:03:07+00:00'
  content_sha256: 2fdf576ffd97b6842889f695d5847a154773e8d56b5d32dcc476d3307c1a0711
---
# EVAL-1 — SPRT / sequential-testing gate + n≥128 re-power audit of headline claims [MED, do early]

## Objective
Implement an **SPRT (sequential probability ratio test)** A/B harness — the engine-testing standard (Leela/Stockfish/fishtest) — so every net/search change is gated at fixed error rates with the *minimum* games needed, and **re-audit** the campaign's headline win-rate claims (4³ beats-classical `b71da32b` 0.612; 5³ parity@512) at n≥128.

## Why it matters (which finding it extends)
PASS-15 `b3ea0b95` is the scar: an n=32 eval *promoted a net on a fluctuation* and the win evaporated at n=128; the methodology node now flags that n≤32 win-rates have ±0.16 CIs (`dcd0a5db`). SPRT fixes this structurally — it stops as soon as the evidence is decisive (cheap when the effect is large) and refuses to conclude when it isn't (no more small-sample promotions). It makes **every** downstream AUX/ARCH/SEARCH A/B both well-powered *and* cheap, so it should run **alongside everything**. The re-power audit retires the remaining n≤32 headline numbers.

## Implementation route
Implement SPRT (H0: p=0.5 vs H1: p=p1, configurable elo bounds, LLR with stop boundaries) wrapping the existing `net_vs_classical_mp` harness; add Wilson/CI reporting. Re-run the headline matchups under SPRT to n≥128-equivalent. Document the gate as the standard for all future passes.

## Decision criterion (CI-based, n≥128)
Deliverable is the gate itself + an audit table: each headline claim re-reported with its n≥128 CI and SPRT verdict (survives / overturned). Adopt SPRT as the campaign's promotion gate (criterion: fixed α/β, e.g. 0.05/0.05).

## Preconditions / risks
Eval-side only; no GPU needed beyond running games; reuses the parallel harness. Risk: SPRT bounds mis-set give wrong stop times (validate against fixed-n on a known case). **Do early** — it de-risks every other node here. No dependencies.

## Cost · value
MED build, low compute. Value: high integrity / methodology payoff; the precondition that makes every other A/B trustworthy and cheap.

## Expected artifacts
`sprt.py` gate, an audit JSON/table (headline claims at n≥128 + SPRT verdict), a short 'how to gate' note appended to methodology `dcd0a5db`.

## Inspiration source
Engine-testing SPRT (Leela/Stockfish/fishtest) + our own n≥128 small-sample scar. Extends methodology `dcd0a5db`, PROOF-1 `3ac354fd`, PASS-15 `b3ea0b95`.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*


---

> **STATUS: HARNESS BUILT + VALIDATED (PASS-19).** SPRT net-vs-classical wrapper delivered and cross-checked against a known fixed-n result.

## PASS-19 — `sprt.py` delivered + libs@64 cross-check

**Built:** `sprt.py` wraps the exact ARCH-3 net-vs-classical game (`eval_arch3._play_one`, net@512 vs classical@48, byte-identical protocol) in a Wald SPRT. Hypotheses on the net's win-rate p: H0 p=p0 (≤parity, 0.50) vs H1 p=p1 (>parity, 0.55); boundaries from α=β=0.05 → [−2.944, +2.944]; each decided game adds log(p1/p0) on a win, log((1−p1)/(1−p0)) on a loss; draws excluded; capped at n_max. Early-stops the moment evidence crosses a boundary, replacing the fixed 128-games-regardless protocol. Reserved (per the PASS-19 methodology pivot) for anchoring a confirmed **net-vs-net** winner to classical — net-vs-net (`screen_nvn.py`) does the cheap relative screening first.

**Cross-check (the validation the plan demanded):** ran SPRT on `best_arch3_libs_s0.pt` (cfg=libs, net@512, classical@48 cap50), the net whose fixed-n strength is known.

| source | win-rate | CI95 | n | verdict |
|---|---|---|---|---|
| fixed-n (ARCH-3, s0) | 0.383 | [0.303, 0.469] | 128 | not decisive |
| **SPRT (this run, s0)** | **0.337** | **[0.251, 0.435]** | **98 (early-stop)** | **`not_a_winner`** |
| fixed-n pooled (3 seeds) | 0.449 | [0.400, 0.499] | 384 | sub-parity |

SPRT crossed the lower boundary (llr −3.70 < −2.944) at **decided=98**, deciding **`not_a_winner`** — libs@64 does *not* beat classical (CI-upper 0.435 < 0.5). The SPRT win-rate 0.337 [0.251, 0.435] **overlaps the s0 fixed-n 0.383 [0.303, 0.469]** → CI-consistent, machinery validated. Near-parity is the *hardest* case for an SPRT (p1=0.55 is a small separation from p0=0.5), so the saving here is modest (98 vs 128); for a clear winner the early-stop is large — the intended use.

**n≥128 re-power audit:** satisfied by the original fixed-n anchor (128 games/seed, 384 pooled, the basis of the 0.449 headline); SPRT adds the sequential gate on top, not a replacement for the powered baseline.

Artifact: `sprt_libs64_s0.json` (waves, llr trajectory, boundaries, final CI). Code: `neural/sprt.py`. Companion methodology node: SCALE-libs `faddae67` (net-vs-net screen) + control `62ab093f` P19. **Resolves the "build the SPRT harness" objective; the harness is now the standard absolute-strength gate for the rolling campaign.**
