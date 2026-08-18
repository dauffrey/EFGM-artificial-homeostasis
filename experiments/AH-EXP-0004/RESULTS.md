# AH-EXP-0004 — Results

## Status

Observed after preregistration and corrected comparative scoring.

## Summary

AH-EXP-0004 tested the narrower coupled-margin mechanism on four new disturbance families while preserving the Phase-0 regulator parameters and thresholds.

The scoring implementation was corrected after PR review so resource-efficiency points compare the actual participating controllers within each schedule.

## Corrected aggregate scores

| Controller | Score |
|---|---:|
| Full regulator | 15 |
| No coupled resilience margin | 8 |

## Falsification outcome

- `uncoupled_matches_or_exceeds_full = false`
- `full_viable_on_fewer_than_3_schedules = false`
- `full_fails_two_where_uncoupled_completes = false`

None of the preregistered AH-EXP-0004 falsification conditions were triggered.

## Cross-disturbance observations

The full regulator completed and remained viable on all four new schedules. The uncoupled variant failed completion on chatter and double-pulse, and became non-viable under ramp reversal. Both completed and remained viable under creep.

The full regulator produced a material win on three of the four new disturbance families.

## Interpretation

AH-EXP-0003 falsified the broader claim that every tested regulator component is necessary. AH-EXP-0004 nevertheless preserves the narrower coupled-margin signal: explicitly coupling estimated recovery capacity to current disturbance remains materially beneficial under disturbance geometries not used in the earlier tests.

This remains evidence only within the deterministic toy architecture. It is not evidence of a universal law or production-safe agent governance.
