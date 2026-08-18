# AH-EXP-0008 Results

## Status

**FALSIFIED**

The preregistered over-regulation detector did not improve the frozen regulator on the independent holdout set. The detector and holdout are preserved unchanged; no post-outcome retuning was performed.

## Frozen design

- Holdout seed: `8009`
- Holdout schedules: `512`
- Schedule length: `12`
- Detector trigger: four consecutive `CAUTION`/`RECOVERY` decisions
- Minimum resource to relax: `0.30`
- Minimum backlog to relax: `2`
- Intervention: permit one `NORMAL` service action, then reset the protective streak

## Observed aggregate result

| Measure | Frozen regulator | Detector-assisted regulator |
|---|---:|---:|
| Completed | 421 / 512 | 404 / 512 |
| Viable | 449 / 512 | 434 / 512 |
| Total utility | 4163.46 | 3969.75 |
| Paired utility wins | 138 | 34 |
| Ties | 340 | 340 |
| Detector interventions | n/a | 218 |
| Mean interventions/run | n/a | 0.426 |

## Preregistered falsification criteria

- `adaptive_completion_not_greater = true`
- `adaptive_utility_not_greater = true`
- `adaptive_viability_loss_exceeds_5_percent = false`
- `detector_never_intervenes = false`
- `post_outcome_retuning_required = false`

Two preregistered falsification conditions fired. The detector therefore failed its stated hypothesis.

## Interpretation

Persistence in a protective state is not, by itself, sufficient evidence that protection has become maladaptive. Forcing a `NORMAL` action after a fixed protective streak caused premature relaxation often enough to reduce both completion and total utility, while also reducing viability modestly.

The negative result narrows the next hypothesis: detecting pathological over-regulation likely requires trajectory evidence about the consequences of protection, not merely elapsed time in `CAUTION`/`RECOVERY`.

## Scientific constraint

AH-EXP-0008 is closed as observed. The detector thresholds, holdout seed, holdout candidate set, and implementation are not to be tuned or reused to convert this result into a positive one.
