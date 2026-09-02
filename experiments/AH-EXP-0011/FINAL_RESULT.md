# AH-EXP-0011 Final Result

## Status

**SURVIVED — primary measurement hypothesis**

AH-EXP-0011 was evaluated only after preregistration review, exact-head structural CI success, and implementation freeze.

- Preregistration baseline: `0baeab969e17374966ab8e7b400405e6eb576c56`
- Frozen implementation: `e21d68d1257ef36a3882a5f6362535f701d6350c`
- Implementation preservation branch: `ah-exp-0011-implementation-freeze`

The canonical workflow explicitly checked out the frozen implementation SHA in detached-HEAD mode before execution.

## Primary-controller result

Controller: `robust_counterfactual_abstention`

Across the frozen 201-value modulated-disturbance sweep:

| Class | Count | Observed mu range |
|---|---:|---|
| STABLE | 116 | `0.000`–`0.575` |
| RECOVERED | 25 | `0.580`–`0.700` |
| FAILED | 60 | `0.705`–`1.000` |
| CENSORED | 0 | none |

Measured adjacent-class boundaries:

1. `STABLE -> RECOVERED` in `[0.575, 0.580]`
2. `RECOVERED -> FAILED` in `[0.700, 0.705]`

Primary canonical result hash:

`f90f47bc51481b030d3693fa682ad7122ae427c330d1b29406e33ededa03d7bc`

All 60 failed trajectories had a finite `tau_escape` and an unambiguous escape phase. All 60 failures were backlog overflows and first lost viability at `post_arrival`. Observed escape times ranged from step 2 through step 7, with median 4.

All 25 RECOVERED trajectories had a measurable recovery latency; observed `tau_recovery` ranged from 2 through 4 steps, with median 3.

The robust-counterfactual relaxation mechanism executed zero interventions on this sweep. Therefore AH-EXP-0011 provides evidence for measurable trajectory regions and escape time, but not for an effect of the AH-EXP-0010 adaptive override on these boundaries.

## Secondary comparison

Controller: `coupled_margin`

The comparison controller produced the same class counts and boundary intervals:

- STABLE: 116
- RECOVERED: 25
- FAILED: 60
- CENSORED: 0
- boundaries: `[0.575, 0.580]` and `[0.700, 0.705]`

Comparison canonical result hash:

`6f78aec9a711b41835723102c95a0d2ab8329ca7983371a32a3e90087198d931`

The hashes differ because controller identity and controller-specific trajectory fields are part of the canonical rows, even though the observed class regions, boundaries, failure mechanisms, and escape-time behavior were the same.

## Preregistered survival criteria

The primary measurement hypothesis survived because:

1. three distinct non-censored classes were observed (`STABLE`, `RECOVERED`, `FAILED`);
2. all 201 primary-controller trajectories were classifiable using the frozen rules;
3. every failed trajectory had one finite `tau_escape` and one recorded escape phase;
4. two adjacent-class boundary intervals were measurable at the frozen `0.005` grid resolution;
5. the exact reproducibility rerun reproduced the complete canonical result bytes and full-trace bytes exactly;
6. no controller, environment, disturbance, horizon, classification, escape, or boundary parameter was changed after canonical outcomes were observed.

## First canonical execution

- Workflow run: `33592925408`
- Artifact ID: `9832378448`
- Artifact ZIP SHA-256: `94fc9070ced445ee2f0f0c5ae3304f98abaf99bda0349375aaa18cb6bdedfb08`
- Canonical result file SHA-256: `4eeb41cc6f6ff420ada359ad767528fb26de9478479c3ae5562aec891b32a5be`
- Full-trace file SHA-256: `e325c76c012ecbcac3f6ba9ecf587712b03146b7a645af3fe6bf541215ef6861`

The first-run artifact was uploaded and timestamped before the reproducibility rerun was triggered.

## Exact reproducibility rerun

The same evaluation PR was closed and reopened without changing its head SHA, producing a second independent workflow run from the same workflow definition and frozen implementation SHA.

- Workflow run: `33593005664`
- Artifact ID: `9832403635`
- Artifact ZIP SHA-256: `bb4c988400cde82fbf74acb17593e9489669b1fee4df6d0506965bc29e987e31`
- Canonical result file SHA-256: `4eeb41cc6f6ff420ada359ad767528fb26de9478479c3ae5562aec891b32a5be`
- Full-trace file SHA-256: `e325c76c012ecbcac3f6ba9ecf587712b03146b7a645af3fe6bf541215ef6861`

The ZIP digests differ because they are distinct artifact archives, but the canonical result file and full-trace file hashes are byte-for-byte identical across runs.

## Interpretation

AH-EXP-0011 establishes, within the frozen synthetic queue/service environment and preregistered modulated-disturbance family, that stable completion, recovery-dependent completion, failure boundaries, and escape time can be defined and reproduced objectively.

It does **not** establish that these boundaries generalize to real AI agents or other environments, and it does not test whether EFGM metrics predict approach to the boundary. That predictive question remains a separate future experiment.
