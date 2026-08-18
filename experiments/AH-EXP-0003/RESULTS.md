# AH-EXP-0003 — Results

## Status

Observed after preregistration. Corrected after PR review identified a scoring implementation defect in comparative resource-efficiency accounting.

## Summary

AH-EXP-0003 tested whether the performance separation observed for the full artificial-homeostasis regulator depended on any single regulator component.

The original report incorrectly scored each ablation against cloned copies of itself for the resource-efficiency point. The scoring criteria were not changed; the implementation was corrected so all actual controllers are compared together within each schedule.

## Corrected aggregate scores

| Controller | Score |
|---|---:|
| No failure-history awareness | 15 |
| Full regulator | 13 |
| No recovery action | 11 |
| No resource awareness | 11 |
| No coupled resilience margin | 6 |

## Falsification outcome

- `single_ablation_matches_or_exceeds_full = true`
- `matching_ablations = ["no_failure_history"]`

The preregistered weakening condition **was triggered**. AH-EXP-0003 therefore does not support the stronger claim that every tested component is necessary for the observed effect.

## Mechanistic interpretation

The corrected result narrows the hypothesis in two ways.

First, failure-history awareness is not necessary in the tested form: removing it improved the aggregate frozen score from 13 to 15. That component should not be credited as a causal requirement and may be unnecessary or counterproductive in this toy architecture.

Second, removing the coupled resilience margin still caused the largest degradation, from 13 to 6. The uncoupled variant continued to fail on disturbance patterns where the full regulator remained viable and completed. This preserves a narrower mechanistic signal around coupling estimated recovery capacity to current disturbance, but it does not rescue the falsified broader component-necessity claim.

## Research integrity note

The earlier 16/15/15/14/10 values are superseded. They resulted from a scoring implementation error, not a change in the preregistered criteria. The defect, corrected output, and falsification outcome are intentionally retained in the research record. The correction was prompted by the unresolved P1 pull-request review and verified by CI with a regression test for cross-controller resource-efficiency scoring.

## Limits

This result is confined to the deterministic toy environment. It does not establish biological equivalence, general agent safety, universal stability, or a general law of artificial homeostasis.

## Next test

AH-EXP-0004 independently attacks the narrower coupled-margin mechanism using new disturbance families while keeping the full regulator and thresholds frozen.
