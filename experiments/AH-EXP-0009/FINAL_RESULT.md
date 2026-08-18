# AH-EXP-0009 Final Result

## Status

**FALSIFIED — FINAL HOLDOUT**

AH-EXP-0009 was evaluated once on the preregistered independent final holdout after the implementation and evaluation procedure were frozen.

## Frozen holdout

- Holdout seed: `9011`
- Candidate schedules: `512`
- Schedule length: `12`
- No post-outcome parameter changes were made.

## Observed aggregate result

| Measure | Adaptive detector | Frozen regulator |
| --- | ---: | ---: |
| Completed | 462 | 441 |
| Viable | 469 | 464 |
| Total utility | 4417.230886178029 | 4313.458567353334 |
| Paired utility wins | 57 | 62 |

- Paired utility ties: `393`
- Adaptive interventions: `142`
- Mean interventions: `0.27734375`
- Intervention schedules: `119`
- Beneficial intervention schedules: `57`
- Harmful intervention schedules: `62`
- Neutral intervention schedules: `0`

## Preregistered falsification outcome

The following preregistered criterion fired:

`harmful_intervention_schedules_greater_or_equal_beneficial = true`

The remaining falsification flags were false:

- `adaptive_completion_not_greater = false`
- `adaptive_utility_not_greater = false`
- `adaptive_viability_loss_exceeds_5_percent = false`
- `detector_never_intervenes = false`
- `post_outcome_parameter_change = false`

Therefore:

`hypothesis_survives = false`

## Scientific interpretation

The counterfactual regulator improved aggregate completion, viability, and total utility on the frozen holdout, but its intervention-level causal record failed the preregistered governance criterion: harmful intervention schedules (`62`) were greater than beneficial intervention schedules (`57`).

Accordingly, aggregate outcome improvement is not sufficient evidence that the intervention policy itself has positive decision-level value. AH-EXP-0009 is retained as a genuine negative result. The detector, generator, utility function, holdout seed, thresholds, coefficients, and falsification criteria are not retuned after observing this result.

Any successor hypothesis must be preregistered separately and must not modify this result.