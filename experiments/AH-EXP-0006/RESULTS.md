# AH-EXP-0006 — Stochastic Multi-Seed Replication Results

## Status

Completed successfully under protected pull-request CI (#68).

## Preregistered design

- Environment: frozen AH-EXP-0005 bounded queue/service environment.
- Controllers: frozen full regulator vs. frozen `no_coupled_margin` regulator.
- Disturbance noise: bounded `U(-0.12,+0.12)` perturbation around each nominal disturbance.
- Seeds: `7, 19, 43, 71, 101, 149, 211, 307`.
- Families: `alternating_load`, `bursty_arrivals`, `late_surge`, `sustained_pressure`.
- Scale: 32 paired stochastic trajectories per controller.
- No post-outcome tuning permitted.

## Aggregate observed results

| Metric | Full regulator | No coupled margin |
|---|---:|---:|
| Aggregate score | 128 | 46 |
| Completed trajectories | 32 / 32 | 10 / 32 |
| Viable trajectories | 32 / 32 | 10 / 32 |
| Mean progress | 1.0000 | 0.859375 |
| Mean resource remaining | 0.529875 | 0.180247 |
| Failures | 2 | 53 |
| Repeated failures | 0 | 17 |

## Seed-level result

- Full regulator seed wins: **8 / 8**
- Uncoupled seed wins: **0 / 8**
- Ties: **0**

## Falsification evaluation

All preregistered falsification flags were **false**:

- `uncoupled_matches_or_exceeds_full = false`
- `full_viable_on_fewer_than_24_of_32 = false`
- `full_wins_fewer_than_5_of_8_seeds = false`
- `uncoupled_completes_6_where_full_fails = false`
- `post_outcome_retuning_required = false`

## Interpretation

AH-EXP-0006 survived its preregistered stochastic robustness attack. Within this controlled queue/service model, the frozen full regulator retained the coupled-margin advantage across all 8 fixed seeds and all 32 stochastic trajectories, while the uncoupled ablation completed and remained viable on only 10 trajectories.

This materially strengthens the evidence that the Phase-1 effect is not an artifact of a single deterministic disturbance path. It does **not** establish a universal stability law, biological equivalence, production readiness, or autonomous-agent safety. The evidence remains confined to controlled toy environments and this specific frozen regulator family.
