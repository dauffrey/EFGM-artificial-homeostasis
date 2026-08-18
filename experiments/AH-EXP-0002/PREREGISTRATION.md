# AH-EXP-0002 — Preregistration

## Title

Attack the AH-EXP-0001 effect with simpler controllers and unseen disturbances

## Status

Preregistered before AH-EXP-0002 outcome analysis.

## Purpose

AH-EXP-0001 produced a separation between an ordinary goal-driven baseline and the candidate homeostatic regulator. AH-EXP-0002 attempts to explain that separation away using simpler control mechanisms.

## Competing controllers

All controllers use the same deterministic environment and resource accounting.

1. **Baseline** — always takes the normal progress action.
2. **RetryLimit** — after two consecutive failed actions, spends one step idle/resetting the failure streak; otherwise takes the normal progress action.
3. **CircuitBreaker** — opens after two consecutive failures, spends one recovery step, then resumes normal progress.
4. **ResourceThrottle** — switches to the cautious action whenever remaining resource is below 0.55; otherwise uses the normal action.
5. **Homeostatic** — frozen AH-EXP-0001 regulator; no threshold changes are permitted.

The simple controls are intentionally small. If any one reproduces the homeostatic result across the preregistered attack schedules, the distinctiveness claim is weakened.

## Attack schedules

The original schedule remains included as a reference, but the primary attack uses schedules not used to construct AH-EXP-0001:

```text
spike       = 0.10, 0.15, 0.20, 0.90, 0.90, 0.25, 0.15, 0.10, 0.10, 0.10, 0.10
plateau     = 0.25, 0.35, 0.55, 0.62, 0.68, 0.72, 0.68, 0.62, 0.50, 0.35, 0.20
oscillation = 0.20, 0.70, 0.25, 0.72, 0.30, 0.75, 0.25, 0.68, 0.20, 0.55, 0.15
late_shock  = 0.10, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.85, 0.90, 0.65, 0.20
```

No schedule-specific parameter tuning is allowed after execution.

## Primary outcomes

For every controller and schedule record:

- task completion
- viable end state
- progress
- resource consumed
- total failures
- repeated failures
- recoveries

A controller receives one point per schedule for each of:

1. completion,
2. viability,
3. zero repeated failures,
4. lowest resource consumption among controllers that make at least 0.50 progress.

The aggregate score is descriptive, not a statistical significance test.

## Falsification conditions

The stronger homeostasis interpretation is **not supported** if either condition holds:

1. A fixed RetryLimit, CircuitBreaker, or ResourceThrottle matches or exceeds Homeostatic on the aggregate primary score across the four unseen schedules.
2. Homeostatic fails to remain viable on at least three of the four unseen schedules.

Even if Homeostatic wins, AH-EXP-0002 does not establish a novel scientific phenomenon; it only justifies harder ablation, randomization, and stochastic testing.

## Frozen implementation constraint

The AH-EXP-0001 `Regulator.margin()` formula and mode thresholds must remain unchanged during AH-EXP-0002.
