# AH-EXP-0013 First Confirmatory Run Evidence

## Preservation status

**PRESERVED BEFORE EXACT RERUN**

This record was committed after the first confirmatory execution and before requesting any reproducibility rerun.

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

## First confirmatory execution

```text
workflow run: 33598457736
job:          100146681800
artifact ID:  9834237567
artifact ZIP SHA-256:
7650e029fd343d6a32a6d4b374983644bc0b8430de69792a1d3e13bf43de2e99
```

The evaluation workflow explicitly checked out detached HEAD:

```text
35af0e3d19b35d3a300cd67c1476d79f841d97be
```

before executing the holdout.

## First-run summary

```text
trajectory count:             355
prediction rows:             1953
positive y_t_2 rows:           32
negative y_t_2 rows:         1921
harmful-event trajectories:    22
```

### Frozen EFGM observer

```text
TP = 15
FN = 17
TN = 1533
FP = 388

sensitivity       = 0.46875
specificity       = 0.7980218636127017
precision         = 0.03722084367245657
balanced accuracy = 0.6333859318063508
```

### Frozen strongest development-selected baseline

```text
B9_simple_integrity

TP = 15
FN = 17
TN = 1316
FP = 605

sensitivity       = 0.46875
specificity       = 0.6850598646538262
precision         = 0.024193548387096774
balanced accuracy = 0.5769049323269131
```

Primary incremental quantity:

```text
Delta_BA = 0.6333859318063508 - 0.5769049323269131
         = 0.05648099947943774
```

The preregistered minimum was:

```text
Delta_BA >= 0.02
```

The first run therefore satisfies the primary numeric incremental-value criterion.

## Early-warning behavior

```text
harmful-event trajectories:          22
with at least one pre-event warning: 14
missed by EFGM observer:               8
```

Frozen earliest-warning lead times:

```text
[2, 1, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 1, 1]
```

All credited warnings have positive lead time.

## Profile-stratified descriptive counts

```text
P0 healthy:
  harmful trajectories = 0
  positive rows         = 0

P1 progressive low bias:
  harmful trajectories = 9
  positive rows         = 8

P2 progressive staleness:
  harmful trajectories = 4
  positive rows         = 8

P3 sample-and-hold:
  harmful trajectories = 2
  positive rows         = 2

P4 mixed degradation:
  harmful trajectories = 7
  positive rows         = 14
```

Profile-stratified metrics are descriptive only and do not override the pooled preregistered result.

## Scientific payload identities

```text
canonical result hash:
3cb754f44e4ce29345dac37ab970b0030c9fc334a1d489ffbaccf0d472f3c117

full trace hash:
fea34589ea3e388a16db66e8e0a53f1317a672c18105e9ae59d1d53c06130dd4

complete result file SHA-256:
6fa2e0af7b5870a6ee674e5f539dc8cde915c8f1756169b288e22fdfca31fcd1
```

## Determination at this checkpoint

The first run reports `SURVIVED` under the frozen numeric/event criteria: balanced accuracy is above chance, `Delta_BA` exceeds `+0.02`, and positive-lead warnings occur.

The final AH-EXP-0013 determination remains conditional on the preregistered exact reproducibility requirement. No mapping, threshold, baseline, profile, label, or survival rule may be changed before the rerun.
