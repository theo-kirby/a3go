---
node_id: bcf93cd3-8d8b-5924-a570-3232f7f1d065
slug: polished-field-7944
title: ARCH-3 — Richer input planes (history, liberties, ko-ban, capture-parity) [RESOLVED P18 — DECISIVE +; liberties carry +0.144 CI-sep; ko-ban prior falsified on 5³]
created_at: '2026-06-09T07:00:13.833192+00:00'
parents:
- gentle-glitter-1363
- weathered-frog-1610
- proud-king-2753
summary: 'RESOLVED (PASS 18) — decision criterion MET, the FIRST EXPANSION branch to beat its 3-plane baseline decisively. Richer KataGo-style input planes lift 5³ strength vs classical: liberties-alone 0.449 [0.400,0.499] (+0.144, CI-separated) and full-stack 0.411 (+0.106); ablation isolates LIBERTY planes as the carrier (strongest arm, even > full stack). ko-ban does NOT help on 5³ (−0.027; KataGo prior falsified — ko too sparse). Wall-clock neutral, +12k params only → genuine input effect. Closest-to-parity 5³ net yet but still short of beating classical absolutely (lo 0.400<0.5). Revises PASS-17: 5³ ceiling NOT robust to input representation. Next: push liberties toward parity (capacity/sims/7³).'
flywheel:
  node_id: bcf93cd3-8d8b-5924-a570-3232f7f1d065
  slug: polished-field-7944
  revision: 3
  pushed_at: '2026-08-07T20:21:22.456999+00:00'
  content_sha256: a7a10162670e0bbd8375e1b883f9ff5953d1ca42160c5bf55e2ca7322c7ef2a7
---
# ARCH-3 — Richer input planes (history, liberties, ko-ban, capture-parity) [MED, cheap high-upside]

## Objective
Expand `A3GoNet`'s 3 input planes (B/W/stm) to a KataGo-style stack: **recent-move history** planes, **per-group liberty-count** planes, a **ko-ban / superko-forbidden** plane, and **capture/turn-parity** — features the net currently must (and largely can't) infer.

## Why it matters (which finding it extends)
The net is **blind to ko**, yet ko is *ubiquitous* in 3D: ~98% of single-stone captures trigger a superko ban and ko frequency rises with board size (`31dae43b`). Without a ko-ban plane the net cannot represent the single most common tactical constraint on the board — a cheap omission with plausibly large cost. History planes give it move context (needed because superko makes value history-dependent — PROOF-3 `22d59c45`); liberty planes hand it the atari/capture signal directly. KataGo uses exactly these. Extends ALGO-2 `792c4ec2` (input representation).

## Implementation route
Compute the planes from engine state (the C++/Python engine already tracks liberties, superko bans via Zobrist, move history); concatenate into the input tensor; retrain distilled nets. Ablate plane groups (history / liberties / ko-ban / parity) to attribute the gain. The ko-ban plane is the cheapest single ablation and the prime suspect.

## Decision criterion (CI-based, n≥128)
At n≥128: the augmented-input net beats the 3-plane baseline vs classical with CI separation on ≥1 board size, with an ablation isolating which planes carry it (expect ko-ban + liberties). SPRT-gate.

## Preconditions / risks
Train-side + a small input-builder; engine already exposes the needed state (`a3go_engine.py`, Zobrist superko from INFRA-2). GPU free. Risk: more planes slow the forward slightly (measure per-wallclock). Cheapest plausibly-large win in the expansion.

## Cost · value
MED build (likely a day). Value: high upside per cost — closes an obvious representational gap (ko) the campaign's own findings flag as ubiquitous.

## Expected artifacts
Augmented input builder, plane-ablation JSON (n≥128), strength A/B vs 3-plane baseline.

## Inspiration source
KataGo richer input features. Extends ALGO-2 `792c4ec2`, ko-ubiquitous `31dae43b`.

*STAGED — not executed. Budget $0/local. Pick against the EXPANSION index + hub `e917c9e4`.*


---

## RESULTS — RESOLVED (PASS 18) · decision criterion MET · liberties carry the gain

**First EXPANSION branch to beat its 3-plane baseline DECISIVELY.** Richer input planes lift 5³ absolute strength vs classical with non-overlapping CIs; an ablation isolates **per-group liberty planes** as the carrier — *not* ko-ban (the KataGo prior is falsified at this board size).

### Protocol (identical to AUX-3/ARCH-2 — only the INPUT varies)
5³, net@512 vs classical@48 (cap50), n=128/seed × seeds {0,1,2} pooled (≈384 decided). SAME deterministic soft-policy data (52,901 ex — byte-for-byte the AUX-3 games), SAME soft target (T=4/W=8/prune=0.02), SAME trunk (A3GoNet 64×6). `base` reproduces the AUX-3 soft baseline (0.305 [0.261,0.353] vs AUX-3's 0.298) — control validated.

### Strength A/B (pooled n≈384, Wilson 95%)
| input cfg | planes | winrate vs classical | Δ vs base | CI-separated | holdout vmse |
|---|---|---|---|---|---|
| base | 3 (B/W/stm) | 0.305 [0.261,0.353] | — | — | 0.0293 |
| +ko-ban | 4 | 0.278 [0.235,0.324] | −0.027 | no | 0.0328 |
| +capture | 4 | 0.333 [0.287,0.381] | +0.028 | no | 0.0345 |
| +history | 5 | 0.356 [0.310,0.406] | +0.051 | no | 0.0320 |
| all | 10 | 0.411 [0.363,0.461] | +0.106 | **YES** | 0.0256 |
| **+liberties** | **6** | **0.449 [0.400,0.499]** | **+0.144** | **YES** | 0.0336 |

Per-seed liberties: 0.383/0.422/0.543 — every seed beats the baseline's best seed (0.320), so not a lucky-init artifact (augmented stem adds only ~12k params, 0.85%). Wall-clock neutral (0.045 g/s, same as base — addresses the "more planes slow the forward" risk: NO slowdown; liberty/ko-ban feature build is cheap vs the per-leaf engine clone).

### Attribution (the ablation the criterion required)
- **Liberty planes (lib1/lib2/lib3+) carry the ENTIRE gain (+0.144) — the strongest single arm, even beating the full 10-plane stack (0.449 > 0.411).** Handing the net the per-group atari/safety signal directly is the lever; it must currently infer liberties from raw stones (3D 6-connectivity makes this hard).
- **ko-ban does NOT help on 5³** (−0.027, the only negative arm). The KataGo "ko-ban prime suspect" prior is **falsified at this board size**: ko is too sparse on 5³ (validated: every ko ban is a recapture-capture, but they're rare — ~22 hits / 12k positions on 4³). Ko-ban may yet matter on bigger boards where ko frequency rises (`31dae43b`).
- capture (+0.028) and history (+0.051) give mild, non-decisive single lifts; the kitchen-sink `all` (10 planes) is DILUTED relative to liberties-alone → **focused high-signal features beat a feature dump** (methodology note).

### Verdict
**Decision criterion MET** — augmented input beats the 3-plane baseline with CI separation on 5³ (libs +0.144, all +0.106), with the ablation isolating liberties as the carrier. **branch stop_reason = `objective_met` (decisive POSITIVE).** Caveat: still does NOT beat classical *absolutely* (libs lo 0.400 < 0.5) — but `libs` (0.449, upper CI 0.499) is the closest any 5³ net has come to parity, and the FIRST cheap lever to move absolute strength at all.

### Campaign impact
Revises the PASS-17 meta-conclusion. The 5³ ceiling is **NOT** robust to *input* representation, only to target-rep (AUX-1/AUX-3) and capacity-reshaping (ARCH-2). The cheap-tweak cluster was **not** exhausted — liberty input was the missing lever. Next: push liberties toward parity (libs + capacity scale-up; libs at higher net sims; libs on 7³ where value calibration is cleanest). See control `62ab093f` PASS-18 replan.

### Built (all additive; npm 48/48, crossval 60/60 3³+4³; base planes == net.encode byte-for-byte)
`input_planes.py` (10-plane stack + per-config channel slices; capture-aware ko-ban, validated koban ⊆ engine-illegal over 12k positions), `net_arch3.py` (`A3GoNetIn`, in_planes=3 == A3GoNet byte-for-byte → clean control), `collect_arch3.py` (re-runs the SAME AUX-3 games storing the full stack), `train_arch3.py`, `eval_arch3.py` (BatchedMCTS encoder swap), `arch3_pipeline.sh` / `arch3_ablation.sh` / `arch3_finalize.py`. Engine: additive `last_move`/`last_move2` (rules-neutral; a3go-authored Python port, VENDORED.md = TS engine only, unaffected).

### Artifacts
`arch3_ab_summary.json` (full pooled + per-seed A/B + attribution + holdout); `arch3_attribution.png` (winrate-with-CI bar chart). Per-seed eval JSONs `experiments_arch3_<cfg>_s<seed>.json` and `*_train.json` on disk.

*RESOLVED PASS 18 · $0/local (RTX 5090 + 32t free; $10 credit untouched) · ~17h compute (collect+18 trains+18 evals).*