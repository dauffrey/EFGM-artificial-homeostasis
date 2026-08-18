# AH-EXP-0001 — Preregistration

## Title

Internal regulation under deterministic disturbance

## Status

Preregistered before outcome analysis.

## Primary question

Can an internally regulated agent preserve a viable, recoverable operating state under increasing disturbance better than an otherwise identical goal-driven baseline?

## Agents

Both agents use the same deterministic environment, goal, action set, disturbance schedule, and step budget.

### Baseline

The baseline agent pursues progress whenever an action is available and retries after failure until its step budget is exhausted or the task completes.

### Homeostatic

The homeostatic agent receives the same observations plus an internal regulatory state derived only from current and accumulated telemetry. It is not given a blacklist of dangerous actions or a hand-coded answer to the task.

The initial candidate regulator computes:

```text
resilience_margin = recovery_capacity - disturbance_load
```

and maps it to three modes:

```text
NORMAL   margin > 0.35
CAUTION  0.0 < margin <= 0.35
RECOVERY margin <= 0.0
```

In `CAUTION`, the agent prefers lower-cost progress and avoids repeated failed actions when alternatives exist. In `RECOVERY`, it spends a step on recovery rather than task advancement.

## Disturbance schedule

The default schedule is fixed before execution:

```text
0.05, 0.10, 0.20, 0.35, 0.55, 0.70, 0.85, 0.65, 0.45, 0.25, 0.10
```

Disturbance is treated as an environmental condition, not as a moral or semantic label.

## Primary outcome

A run is considered viable if the agent either completes the task or remains recoverable at the end of the fixed horizon without exhausting its resource budget.

## Metrics

Primary metrics:

- task completion
- viable end state
- cumulative progress
- resource consumed
- failed actions
- repeated failures
- recovery actions
- minimum resilience margin
- number of steps spent in each regulatory mode

## Primary hypothesis

Relative to the baseline, the homeostatic agent will reduce repeated failures and preserve more resource under high disturbance while retaining non-zero task progress.

## Null / falsification conditions

The initial hypothesis is not supported if any of the following hold across the preregistered schedule:

1. The homeostatic agent consumes at least as much resource and incurs at least as many repeated failures as the baseline without greater progress.
2. The homeostatic agent trivially avoids failure by refusing useful work, operationalized as zero progress when the baseline makes progress.
3. The apparent benefit is completely reproduced by a simple fixed retry limit or fixed circuit breaker in later controls.
4. Results require tuning thresholds after observing outcomes.

## Interpretation constraints

A positive AH-EXP-0001 result would demonstrate only that this specific internal feedback controller changes behavior beneficially in this deterministic toy environment. It would not establish a universal law, AI safety guarantee, biological equivalence, or proof of EFGM.

The next stage after any positive result must attack the result with simpler baselines, ablations, unseen disturbance schedules, parameter perturbation, and stochastic environments.
