# AH-EXP-0013 Final Result

## Status

**SURVIVED — preregistered observation-integrity incremental warning hypothesis**

AH-EXP-0013 was executed only after preregistration, merge/freeze, development-only observer construction, frozen B1..B9 thresholds, structure-only review, exact-head CI success, and implementation freeze.

Frozen identities:

```text
Preregistration freeze:
c766a3534d9d8ae8d4134b9995b0a22510dd0310

Observer implementation freeze:
35af0e3d19b35d3a300cd67c1476d79f841d97be

AH operational substrate:
e21d68d1257ef36a3882a5f6362535f701d6350c

EFGM reference code:
37b2ff2d2b577c9f383dd0d7c3083597627150ea
```

## Primary question

AH-EXP-0013 asked whether a causal EFGM-derived governance observer could detect degradation in observation/evidence integrity before that degradation produced a harmful under-protective controller action, and whether the observer provided incremental short-horizon information beyond the strongest frozen transparent operational/sensor-quality baseline selected from development data.

This was intentionally a different test from AH-EXP-0012. AH-EXP-0012 remains falsified and was not retuned.

## Confirmatory holdout

The frozen holdout contained:

```text
355 trajectories
1953 eligible prediction rows
32 positive y_t_2 rows
1921 negative y_t_2 rows
22 trajectories with a harmful-underprotection event
```

The healthy P0 profile produced no harmful-underprotection events, while the degraded P1..P4 profiles produced the confirmatory event diversity required for pooled evaluation.

## Frozen EFGM observer

Primary warning rule:

```text
EFGM_RISK = mean(1 - GI, AE, CUE)
WARN when EFGM_RISK >= 0.133389161231
```

Confirmatory confusion matrix:

```text
TP = 15
FN = 17
TN = 1533
FP = 388
```

Performance:

```text
sensitivity       = 0.46875
specificity       = 0.7980218636127017
precision         = 0.03722084367245657
balanced accuracy = 0.6333859318063508
```

The observer therefore performed above the `0.50` balanced-accuracy chance criterion, but its absolute precision was low because warnings were much more common than the rare two-step harmful-event labels.

## Frozen strongest simple baseline

The strongest baseline selected on development data was:

```text
B9_simple_integrity
```

with frozen score:

```text
SIMPLE_INTEGRITY_RISK = mean(
    1 - calibration_confidence,
    1 - freshness,
    1 - provenance_completeness,
    declared_uncertainty
)

WARN when SIMPLE_INTEGRITY_RISK >= 0.15
```

Confirmatory confusion matrix:

```text
TP = 15
FN = 17
TN = 1316
FP = 605
```

Performance:

```text
sensitivity       = 0.46875
specificity       = 0.6850598646538262
precision         = 0.024193548387096774
balanced accuracy = 0.5769049323269131
```

## Primary incremental result

The preregistered comparison was:

```text
Delta_BA = BA_EFGM - BA_BASE
```

Observed:

```text
Delta_BA
= 0.6333859318063508 - 0.5769049323269131
= 0.05648099947943774
```

The survival criterion required:

```text
Delta_BA >= +0.02
```

Therefore the incremental criterion passed by approximately `+0.03648` beyond the preregistered minimum.

The difference came from specificity: both EFGM and B9 detected the same number of positive two-step rows (`TP=15`, `FN=17`), while EFGM produced fewer false positives (`388` versus `605`).

## Early-warning behavior

Of the 22 trajectories that eventually reached a harmful-underprotection event:

```text
received an EFGM pre-event warning: 14
missed:                              8
```

Earliest positive lead times were:

```text
[2, 1, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 1, 1]
```

Thus at least one genuine positive-lead warning occurred, satisfying the preregistered lead-time condition. This should not be interpreted as reliable detection of every harmful trajectory; the observer missed 8 of 22.

## Preregistered result determination

The pooled holdout had adequate positive and negative samples, so the experiment was not inconclusive.

Required survival conditions:

```text
positive + negative holdout labels             PASS
BA_EFGM > 0.50                                  PASS
Delta_BA >= 0.02                                PASS
at least one positive-lead true warning         PASS
time-t-only causal predictor boundary           PASS
frozen provenance / implementation identities   PASS
first-run evidence preserved before rerun       PASS
exact reproducibility                           PASS
no post-outcome retuning                        PASS
```

Therefore the preregistered primary AH-EXP-0013 hypothesis **SURVIVED**.

## Exact reproducibility

The first confirmatory result was preserved at commit:

```text
0598629acd19c5be1f7fa52834990f67107dc7ce
```

before the exact rerun.

First execution:

```text
workflow run: 33598457736
job:          100146681800
artifact ID:  9834237567
```

Exact rerun:

```text
workflow run: 33598457736 (rerun attempt)
job:          100147112202
artifact ID:  9834287715
```

Both runs produced identical scientific identities:

```text
canonical result hash:
3cb754f44e4ce29345dac37ab970b0030c9fc334a1d489ffbaccf0d472f3c117

full trace hash:
fea34589ea3e388a16db66e8e0a53f1317a672c18105e9ae59d1d53c06130dd4

complete result file SHA-256:
6fa2e0af7b5870a6ee674e5f539dc8cde915c8f1756169b288e22fdfca31fcd1
```

The complete result file was byte-for-byte reproducible.

## What the result means

AH-EXP-0013 supports one narrow statement:

> In this frozen synthetic artificial-homeostasis system, under the preregistered observation-integrity perturbations, the tested EFGM-derived governance observer contained incremental short-horizon information about harmful under-protective control divergence beyond the strongest development-selected transparent operational/sensor-quality baseline.

The result is scientifically different from AH-EXP-0012. In 0012, simple backlog telemetry dominated the broader EFGM observer. In 0013, once the failure mechanism was shifted to degraded evidence integrity rather than direct capacity overflow, the frozen EFGM governance construction provided a modest incremental advantage over the frozen simple integrity aggregate.

## Important limitations

This is a narrow synthetic success, not evidence of production-grade failure prediction.

The pooled balanced accuracy was only about `0.633`, sensitivity was `0.469`, precision was about `0.037`, and 8 of 22 harmful trajectories received no EFGM pre-event warning. P3 sample-and-hold was particularly weak in the descriptive profile analysis. These limitations are part of the result and should not be hidden by the aggregate survival classification.

AH-EXP-0013 does **not** establish:

- real-world AI-agent safety or alignment;
- reliable production sensor-fault diagnosis;
- universal early-warning behavior;
- superiority to arbitrary statistical or machine-learning predictors;
- causal validity of EFGM outside this synthetic laboratory;
- that EFGM can infer hidden true state without evidence.

## Scientific progression

The current sequence is now:

```text
AH-EXP-0011:
measurable stable / recovery / failure boundaries and escape time — SURVIVED

AH-EXP-0012:
EFGM pre-escape warning beyond simple backlog telemetry — FALSIFIED

AH-EXP-0013:
EFGM observation-integrity warning beyond frozen simple integrity telemetry — SURVIVED
```

The scientifically appropriate next question is not to inflate the 0013 result. A subsequent experiment should test whether the incremental effect survives a new disturbance/integrity family, alternative transparent multivariate baselines, and a failure event that is not constructed from the same integrity metadata supplied to the observer.
