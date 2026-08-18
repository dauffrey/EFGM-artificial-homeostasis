# AH-EXP-0007 — Adversarial robustness and failure-boundary search

## Purpose

Attempt to falsify the Phase-1 coupled-margin mechanism by deliberately degrading the regulator's information, changing the environment's operating assumptions, and searching a bounded disturbance space for trajectories where the frozen uncoupled controller outperforms the frozen full regulator.

## Frozen components

The following are frozen from AH-EXP-0005/AH-EXP-0006 and may not be tuned after outcome inspection:

- `Regulator` implementation and thresholds.
- `NoCoupledMarginRegulator` implementation.
- Queue-service baseline constants unless explicitly modified by a preregistered model-mismatch condition below.
- Controller comparison is paired: both controllers receive the same true disturbance trajectory and the same observation distortion for each condition.

## Attack A — Partial observability

Use the four AH-EXP-0005 schedules and the eight AH-EXP-0006 seeds. Generate the same bounded stochastic disturbance trajectories as AH-EXP-0006, then distort only the controller's observed disturbance while the environment continues to evolve under the true disturbance.

Preregistered observation conditions:

1. `delay_1`: controller observes the previous step's disturbance; step 0 observes 0.0.
2. `biased_low`: observed disturbance is `max(0, true_disturbance - 0.20)`.
3. `noisy_sensor`: add independent deterministic sensor noise `U(-0.20,+0.20)` using seed `10000 + seed` and clamp to `[0,1]`.

This yields 96 paired trajectories per controller (3 conditions × 4 families × 8 seeds).

## Attack B — Model mismatch

Reuse the same 32 true stochastic trajectories from AH-EXP-0006 but change environment mechanics without changing either regulator:

1. `expensive_service`: multiply service base and stress costs by 1.35.
2. `weak_recovery`: multiply maintenance resource gain by 0.45.
3. `fragile_service`: reduce normal and cautious success thresholds by 0.12.

This yields 96 paired trajectories per controller.

## Attack C — Bounded adversarial disturbance search

Generate 256 candidate schedules of length 12 from a deterministic search seed `7001`.

Each candidate disturbance is constrained to `[0,1]`, with no more than 6 values above `0.80`, and mean disturbance constrained to `[0.25,0.70]`.

For each candidate, run both frozen controllers in the unmodified queue-service environment. Rank candidates by the preregistered paired advantage function:

`advantage = utility(no_coupled_margin) - utility(full)`

where per-controller utility is:

- +4 if completed
- +3 if viable
- +2 × progress
- +1 × remaining resource
- −0.25 × failures
- −0.50 × repeated_failures

Retain the maximum observed uncoupled advantage and the corresponding schedule. The search procedure itself is part of the attack and does not modify controller parameters.

## Primary falsification conditions

The Phase-1 coupled-margin robustness claim is materially weakened if **any** of the following occurs:

1. Across Attack A, the uncoupled controller has greater total utility than the full regulator.
2. Across Attack B, the uncoupled controller has greater total utility than the full regulator.
3. Attack C finds at least one bounded schedule with uncoupled advantage >= 1.0 utility point.
4. Across either Attack A or Attack B, full-regulator viability falls below 60% of paired trajectories.
5. Post-outcome retuning is required to preserve the result.

## Secondary observations

Record completion, viability, progress, remaining resource, failures, repeated failures, and the number of paired trajectories won by each controller. Also record the worst observed full-controller utility margin and the adversarial schedule that produced it.

## Interpretation constraint

Passing AH-EXP-0007 would show only that the frozen coupled-margin mechanism resisted these bounded synthetic attacks. It would not establish universal robustness, production safety, autonomous-agent alignment, biological equivalence, or immunity to adversarial conditions outside the preregistered search space.
