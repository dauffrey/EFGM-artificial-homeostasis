# AH-EXP-0003 — Results

## Status

Observed after preregistration and successful CI execution.

## Summary

AH-EXP-0003 tested whether the performance separation observed for the full artificial-homeostasis regulator depended on any single regulator component.

The full regulator remained the highest-scoring controller under the frozen AH-EXP-0002 disturbance schedules.

## Aggregate scores

| Controller | Score |
|---|---:|
| Full regulator | 16 |
| No failure-history awareness | 15 |
| No recovery action | 15 |
| No resource awareness | 14 |
| No coupled resilience margin | 10 |

## Falsification outcome

- `single_ablation_matches_or_exceeds_full = false`
- `matching_ablations = []`

The preregistered weakening condition was therefore not triggered.

## Mechanistic interpretation

Within this toy architecture, removing the coupled resilience margin produced the largest degradation. In particular, the uncoupled variant failed viability and completion under oscillation and plateau disturbances where the full regulator completed and remained viable.

This supports a narrower hypothesis: the observed advantage is not explained solely by retry suppression, recovery actions, resource awareness, or failure-history awareness in isolation. The interaction between estimated recovery capacity and current disturbance appears to be the strongest contributor among the tested components.

## Limits

This result is confined to the deterministic toy environment. It does not establish biological equivalence, general agent safety, universal stability, or a general law of artificial homeostasis.

## Next test

AH-EXP-0004 will attack the coupled-margin mechanism using new disturbance families not used in AH-EXP-0001 through AH-EXP-0003, while keeping the full regulator and all thresholds frozen.
