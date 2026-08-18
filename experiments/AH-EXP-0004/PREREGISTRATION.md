# AH-EXP-0004 — Preregistration

## Title

Robustness attack on the coupled resilience-margin mechanism

## Status

Preregistered before outcome analysis.

## Primary question

Does the frozen full regulator retain an advantage over the uncoupled-margin ablation when exposed to new disturbance families that were not used in AH-EXP-0001 through AH-EXP-0003?

## Frozen components

The following are frozen before execution:

- full regulator implementation
- regulator thresholds
- recovery behavior
- resource accounting
- completion threshold
- viability rule
- environment action dynamics
- AH-EXP-0002 scoring rule
- no-coupled-margin ablation implementation

No parameter tuning is permitted after observing AH-EXP-0004 outcomes.

## New disturbance families

Four new deterministic schedules are introduced:

1. **ramp_reversal** — disturbance rises progressively and then falls rapidly.
2. **double_pulse** — two separated high-disturbance pulses with a low-disturbance recovery interval.
3. **chatter** — rapid low/high switching intended to stress mode switching and hysteresis-like behavior.
4. **creep** — sustained low-to-moderate disturbance that increases slowly and never produces a single extreme spike.

These schedules are not modifications of the AH-EXP-0002 spike, plateau, oscillation, or late-shock schedules.

## Controllers

- `full` — frozen full regulator
- `no_coupled_margin` — frozen AH-EXP-0003 uncoupled-margin ablation

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

The frozen AH-EXP-0002 scoring criteria are reused without changing the criteria.

## Primary falsification condition

The coupled-margin hypothesis is weakened if the `no_coupled_margin` controller matches or exceeds the full regulator's aggregate score across the four new disturbance families.

## Secondary weakening conditions

The result is also weakened if:

- the full regulator is viable on fewer than three of four schedules; or
- the full regulator fails completion on two or more schedules where the uncoupled controller completes.

## Stronger supporting pattern

A stronger result would be observed if the full regulator remains viable and completes across all four schedules while the uncoupled controller loses viability, completion, or materially more resources on at least two distinct disturbance families.

## Interpretation constraints

AH-EXP-0004 is a robustness test of one mechanism in a deterministic toy system. Passing it does not establish generalization to real AI agents, stochastic environments, different model architectures, or real-world safety.
