# AH-EXP-0013 Exact Reproducibility Record

## Status

**PASS — exact scientific result reproduced**

AH-EXP-0013 was rerun only after the first confirmatory evidence had been preserved in `FIRST_RUN_EVIDENCE.md` at commit:

```text
0598629acd19c5be1f7fa52834990f67107dc7ce
```

Both executions evaluated the identical frozen observer implementation:

```text
35af0e3d19b35d3a300cd67c1476d79f841d97be
```

under preregistration freeze:

```text
c766a3534d9d8ae8d4134b9995b0a22510dd0310
```

## Execution identities

### First confirmatory execution

```text
workflow run: 33598457736
job:          100146681800
artifact ID:  9834237567
artifact ZIP SHA-256:
7650e029fd343d6a32a6d4b374983644bc0b8430de69792a1d3e13bf43de2e99
```

### Exact rerun

```text
workflow run: 33598457736 (rerun attempt)
job:          100147112202
artifact ID:  9834287715
artifact ZIP SHA-256:
7146ea8e750038563d542df57c6944a4c9b449e8c92eca9fdf2df969321e1ffc
```

The artifact ZIP digests differ because the executions produced separate workflow archives. The scientific result file inside the workflow reproduced exactly.

## Exact matched scientific identities

Both executions produced:

```text
canonical result hash:
3cb754f44e4ce29345dac37ab970b0030c9fc334a1d489ffbaccf0d472f3c117

full trace hash:
fea34589ea3e388a16db66e8e0a53f1317a672c18105e9ae59d1d53c06130dd4

complete result file SHA-256:
6fa2e0af7b5870a6ee674e5f539dc8cde915c8f1756169b288e22fdfca31fcd1
```

The following also matched exactly:

```text
trajectory count             = 355
prediction count             = 1953
positive label count         = 32
negative label count         = 1921
harmful trajectory count     = 22
EFGM TP/FN/TN/FP             = 15 / 17 / 1533 / 388
B9 TP/FN/TN/FP               = 15 / 17 / 1316 / 605
BA_EFGM                      = 0.6333859318063508
BA_B9                        = 0.5769049323269131
Delta_BA                     = 0.05648099947943774
detected harmful trajectories = 14
missed harmful trajectories   = 8
lead times                   = [2,1,3,1,3,1,3,1,1,1,1,1,1,1]
status                       = SURVIVED
```

Profile-stratified result payloads also reproduced exactly.

## Reproducibility determination

The preregistered reproducibility condition required the exact rerun to reproduce prediction rows, labels, metrics, lead-time records, canonical-result hash, and full-trace hash. Those identities reproduced, and the complete result-file SHA-256 also matched.

Therefore:

```text
AH-EXP-0013 exact reproducibility = PASS
```

No observer mapping, threshold, baseline threshold, best-baseline identity, confirmatory profile, label, prediction horizon, or survival criterion was changed between executions.
