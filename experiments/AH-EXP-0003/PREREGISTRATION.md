# AH-EXP-0003 — Preregistration

## Title

Ablation study of the artificial-homeostasis regulator

## Status

Preregistered before outcome analysis.

## Primary question

Which components of the AH-EXP-0001 internal regulator are causally responsible for the performance separation observed in AH-EXP-0002?

## Frozen reference

The full homeostatic regulator, thresholds, environment dynamics, completion threshold, resource accounting, and the four AH-EXP-0002 unseen disturbance schedules are frozen.

No parameter tuning is permitted after observing AH-EXP-0003 outcomes.

## Ablations

The full regulator is compared against four ablations:

1. **No recovery action** — retains the resilience-margin state estimate and NORMAL/CAUTION switching, but RECOVERY becomes CAUTION rather than restoring capacity.
2. **No resource awareness** — recovery capacity no longer depends on current resource; it depends only on accumulated failures.
3. **No failure-history awareness** — recovery capacity no longer depends on accumulated failures; it depends only on current resource.
4. **No coupled margin** — current disturbance is removed from the resilience-margin calculation; mode selection is driven only by recovery capacity.

Each ablation changes exactly one conceptual component while preserving the remaining logic.

## Disturbance schedules

The frozen AH-EXP-0002 schedules are reused:

- `spike`
- `plateau`
- `oscillation`
- `late_shock`

## Primary metrics

For each controller and schedule:

- completion
- viability
- progress
- resource retained
- failures
- repeated failures
- recoveries
- minimum resilience margin

## Aggregate score

The frozen AH-EXP-0002 scoring function is reused without modification.

## Interpretation

A component is treated as mechanistically important if removing it causes a material reduction in aggregate score or causes loss of viability/completion on at least one schedule where the full regulator succeeds.

A component is treated as non-essential in this toy environment if its removal produces no meaningful degradation relative to the full regulator.

## Falsification / weakening conditions

The stronger claim that the observed advantage depends on an integrated homeostatic mechanism is weakened if any single ablation matches or exceeds the full regulator's aggregate score across all four schedules.

If multiple ablations match or exceed the full regulator, the current regulator should be regarded as over-specified and the simpler surviving mechanism should become the new research target.

## Interpretation constraints

AH-EXP-0003 can identify mechanism within this toy architecture only. It cannot establish biological equivalence, universal agent stability, or a general law of artificial homeostasis.
