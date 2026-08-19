# AH-EXP-0009 Final Result

## Status

**FALSIFIED — FINAL HOLDOUT**

The canonical AH-EXP-0009 result is the first completed execution of the preregistered independent final holdout: GitHub Actions run **#101** on branch `ah-exp-0009-final-holdout`.

## Frozen holdout

- Holdout seed: `9011`
- Candidate schedules: `512`
- Schedule length: `12`
- No post-outcome detector, generator, utility, threshold, coefficient, or falsification parameter changes were made.

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

Accordingly, aggregate outcome improvement is not sufficient evidence that the intervention policy itself has positive decision-level value. AH-EXP-0009 is retained as a genuine negative result.

## Audit note — one-shot workflow enforcement

A post-result PR review identified that the original GitHub Actions condition for the one-shot holdout matched every push to `ah-exp-0009-final-holdout`, not only the initial evaluation push. That automation bug could cause later result-recording/documentation pushes to execute the deterministic holdout again.

The canonical evidentiary result remains the **first completed final-holdout run, #101**. Any later automatic executions, if produced by the flawed branch-level gate, are explicitly **non-evidentiary protocol artifacts** and do not replace, average with, or otherwise modify run #101. The final-holdout workflow step was removed immediately after this review finding so subsequent pushes cannot execute the holdout again.

This audit correction changes only execution governance and documentation; it does not retune or reinterpret the observed run-#101 result.

Any successor hypothesis must be preregistered separately and must not modify this result.
