# AH-EXP-0012 Final Result

## Status

**FALSIFIED — preregistered primary incremental early-warning hypothesis**

AH-EXP-0012 was executed only after preregistration, observer construction from AH-EXP-0011 development data, exact-head CI success, and observer implementation freeze.

Frozen identities:

```text
Preregistration freeze: 4c01e559548341e16310981ade06871f63685d00
Observer implementation: a1d2ef36f8dbb6ac086f8df6614de63485d30c15
AH operational substrate: e21d68d1257ef36a3882a5f6362535f701d6350c
EFGM reference code: 37b2ff2d2b577c9f383dd0d7c3083597627150ea
```

The confirmatory workflow explicitly checked out the frozen observer SHA in detached-HEAD mode before evaluation.

## Primary result

The frozen AH-EXP-0012 holdout produced adequate positive and negative label diversity:

```text
prediction rows: 832
positive y_t_2: 108
negative y_t_2: 724
```

### EFGM-derived observer

Frozen warning threshold:

```text
EFGM_RISK >= 0.582818749642
```

Confirmatory confusion matrix:

```text
TP = 99
FN = 9
TN = 470
FP = 254
```

Performance:

```text
sensitivity       = 0.9166666666666666
specificity       = 0.6491712707182320
precision         = 0.2804532577903683
balanced accuracy = 0.7829189686924494
```

The EFGM-derived observer therefore performed substantially above chance on the frozen two-step prediction label.

### Frozen best single-variable baseline

The best development-selected single-variable baseline was backlog:

```text
WARN if backlog >= 9
```

Confirmatory confusion matrix:

```text
TP = 101
FN = 7
TN = 667
FP = 57
```

Performance:

```text
sensitivity       = 0.9351851851851852
specificity       = 0.9212707182320442
precision         = 0.6392405063291139
balanced accuracy = 0.9282279517086147
```

The preregistered incremental-value quantity was:

```text
Delta_BA = BA_EFGM - BA_BASE
         = 0.7829189686924494 - 0.9282279517086147
         = -0.14530898301616535
```

The survival criterion required:

```text
Delta_BA >= +0.02
```

That criterion failed decisively. The primary AH-EXP-0012 hypothesis is therefore **FALSIFIED** and must not be rescued by post-hoc retuning.

## Early-warning behavior

The falsification does **not** mean the EFGM-derived observer had no early-warning signal.

There were 54 escape trajectories in the holdout. The observer emitted at least one pre-escape warning for all 54:

```text
detected escapes = 54
missed escapes   = 0
```

Observed earliest-warning lead times ranged from 2 through 5 steps.

This establishes that the frozen observer was sensitive to states preceding escape in this synthetic environment. However, the simple backlog signal was materially more discriminating and generated far fewer false positives.

The key negative result is therefore:

> **EFGM-derived measurements did not provide incremental predictive value over the strongest frozen single-variable operational baseline in AH-EXP-0012.**

## Why the hypothesis failed

The largest performance difference was specificity / false-warning control.

The EFGM observer produced:

```text
FP = 254
specificity = 0.6491712707182320
```

The backlog baseline produced:

```text
FP = 57
specificity = 0.9212707182320442
```

The EFGM observer detected nearly every imminent escape, but it also marked many non-imminent states as risky. In this frozen synthetic queue environment, backlog proximity to the viability limit is a more direct predictor of near-term escape than the broader EFGM composite.

## Preregistered result determination

The holdout had both positive and negative samples, so the experiment was not inconclusive.

Primary survival conditions included:

1. positive and negative holdout labels — **PASS**;
2. `BA_EFGM > 0.50` — **PASS**;
3. `Delta_BA >= 0.02` — **FAIL**;
4. at least one pre-escape true-positive warning with positive lead time — **PASS**;
5. time-t-only causal evidence — **PASS**;
6. frozen provenance / identities — **PASS**;
7. exact reproducibility — **PASS**;
8. no post-outcome retuning — **PASS**.

Because all required criteria were conjunctive, criterion 3 falsifies the primary hypothesis.

## Exact reproducibility

The first confirmatory execution was preserved before the rerun.

Both executions produced exactly the same scientific payload hashes:

```text
canonical result hash:
2052e6dd277fb92ec58125a206f8ec8e95bcaf0b18026af4f31b8ce1f6f277bd

full trace hash:
7ff86780943028b5a7dcbe62166d6709cac15a7f6ac19c5cc0b0bbddba6f99b8

result file SHA-256:
9554d4d15ed77cf03e5427048328a3e829d061c15aa3e80058d0a54ff0f4a62c
```

The confusion matrices, prediction counts, label counts, lead-time list, balanced accuracies, `Delta_BA`, canonical result hash, full-trace hash, and complete result-file hash were identical on the rerun.

### First confirmatory execution

```text
workflow run: 33596736500
job: 100141587714
artifact ID: 9833649601
artifact ZIP SHA-256: a1fd1c19baa2f364bd2cb259adf62f75ce109ca9774e458968034f6524c47ee9
```

### Exact rerun

```text
workflow run: 33596736500 (rerun attempt)
job: 100141829989
artifact ID: 9833676614
artifact ZIP SHA-256: 840b85f5bdb565505e5b010368f563308242175acd77ddd570c59fffc0d9d2c0
```

The ZIP digests differ because the workflow artifacts are separate archives. The scientific result file itself is byte-for-byte identical.

## Interpretation

AH-EXP-0012 supports a narrower observation than its primary hypothesis:

> A causal EFGM-derived temporal observer can become elevated before synthetic viability loss and can generate positive warning lead time.

But AH-EXP-0012 falsifies the stronger preregistered claim:

> The tested EFGM-derived observer did **not** outperform a simple backlog threshold and therefore did not demonstrate incremental early-warning value in this environment.

This is a useful falsification rather than a reason to alter the result. The next experiment should investigate *why* the broader EFGM composite over-warns and whether an EFGM construct predicts a failure mode that is not already directly encoded by a single operational state variable. Any such experiment must be separately preregistered; AH-EXP-0012 itself remains falsified.

## Claims not supported

AH-EXP-0012 does not establish real-world AI-agent failure prediction, production safety, universal nonlinear-transition detection, or superiority of EFGM to ordinary telemetry. It also does not justify tuning AH-EXP-0012 after seeing this result.
