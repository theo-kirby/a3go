---
node_id: 3f47168a-3f0c-5e7d-84a0-9a493d423f73
slug: patient-silence-7334
title: 'SYMM-1 arm A — Cube-symmetry TTA inference [RESOLVED null: k=8 0.558 + k=48 retest 0.531, both include 0.5 → no free gain; pivot to arm-B 48× aug]'
created_at: '2026-06-18T11:52:25.426347+00:00'
parents:
- proud-king-2753
summary: 'RESOLVED null (arm A). Cube-symmetry TTA-averaged inference vs plain libs: k=8 0.558 [.44,.67], k=48 retest 0.531 [.43,.63] — both include 0.5, high per-seed variance. Full 48-averaging does NOT help → no reliable free strength gain (net already ~symmetry-robust in expectation). Geometry validated 48/48. Pivot symmetry lever to arm-B 48× train-time augmentation.'
origin:
  backend: flywheel
  node_id: 3f47168a-3f0c-5e7d-84a0-9a493d423f73
  slug: patient-silence-7334
  revision: 4
  exported_at: '2026-08-08T09:53:04.831757+00:00'
flywheel:
  node_id: b77945f2-b159-54ab-826f-448f4a8336a8
  slug: dawn-moon-9298
  revision: 0
  pushed_at: '2026-08-08T10:02:15+00:00'
  content_sha256: f6bba3ba7e79bd617f1779315ea6e08e0aa3fb354aca39c52683823f16519887
---
# SYMM-1 arm A — cube-symmetry TTA inference (libs 5³, no retrain) [RESOLVED]

Average the EXISTING libs net over the order-48 cube-symmetry group at every MCTS leaf (k=8 sampled elements), no retraining. A free shot at the 0.449→0.5 parity gap that capacity could not close.

## Result
- symm-averaged net vs plain net (net-vs-net, 24 games/seed × 3 seeds, sims=48):
  **win-rate 0.558 [0.4433, 0.6727]** (per-seed [0.5, 0.6522, 0.5217])
- geometry validated: cube_symmetry self-test 48/48 (exact group action).

## Findings
**Directionally positive but UNDER-POWERED.** symm-vs-plain pooled 0.558 with all 3 seeds >=0.5 (per-seed [0.5, 0.6522, 0.5217]), but the 95% CI [0.4433, 0.6727] includes 0.5 at n=72 (k=8/sims=48). So TTA is not a CONFIRMED free win at this power — but the consistent >0.5 signal across seeds means it is NOT ruled out and merits a higher-power retest, not abandonment.

## Implication
Next (cheap): a higher-power retest with full k=48 averaging and more games to resolve the 0.558 signal; in parallel Arm B (48x train-time augmentation, a data-quality bet) is the stronger structural test. Geometry (cube_symmetry 48/48) is built and reusable. Records the under-powered-positive result so the next pass retests at power rather than re-probing blindly or dropping the lever.

## Artifact
`symm1_tta.json`. Code: `cube_symmetry.py` (48 perms + policy inverse + 48/48 self-test), `symm_tta.py` (symmetry-averaged eval over BatchedMCTS).

*Resolved PASS-20 (breadth pass, cheap-first). Budget $0/local. Engine/tests untouched (additive probe scripts only).*

---

## SYMM-1 arm-A — HIGHER-POWER RETEST (k=48 full averaging, gp=32) [RESOLVED null]
Per the under-powered k=8 result (0.558), retested with the FULL 48-element cube group and more games.
- **symm-vs-plain pooled = 0.5312 [0.4314, 0.6311]** (per-seed [0.4062, 0.6562, 0.5312], k=48, 32 games/seed × 3 = 96).
- Full 48-averaging did NOT lift the signal (0.531 vs 0.558 at k=8); CI firmly includes 0.5 with large per-seed variance (0.41–0.66).

**Verdict: cube-symmetry test-time augmentation gives NO reliable free strength gain on the 5³ libs net** — the net is already approximately symmetry-robust in expectation, so averaging over the group only re-smooths what it already knows (and the 48× inference cost is not justified). **Arm A is closed null.** The symmetry lever, if pursued, should go to **Arm B (48× train-time data augmentation)** — a data-quality bet, structurally different from inference-time averaging. Geometry (`cube_symmetry.py`, 48/48) and `symm_tta.py` are built and reusable for arm B. Artifact: `symm1_tta_k48.json`.