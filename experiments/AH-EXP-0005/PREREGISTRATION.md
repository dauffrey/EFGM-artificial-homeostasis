# AH-EXP-0005 — Cross-environment replication preregistration

## Phase

Phase 1 — cross-environment replication.

## Research question

Does the narrower Phase-0 coupled-margin effect transfer to a materially different environment implementation without retuning the Phase-0 regulator?

## Frozen mechanism

The Phase-0 full regulator is carried forward without threshold or coefficient changes. The primary comparison is the same regulator with the disturbance term removed from the resilience margin (`no_coupled_margin`). Failure-history awareness is not treated as a required mechanism because AH-EXP-0003 falsified that broader component-necessity claim.

## Environment independence requirement

AH-EXP-0005 must not reuse the Phase-0 `environment_step()` dynamics. It will use a different state-transition model with different action semantics, resource-cost mapping, disturbance injection, and completion dynamics. The new environment may adapt raw observables into the frozen regulator inputs, but it may not tune regulator thresholds or coefficients using outcome results.

## Planned environment

A bounded queue-service environment:

- work arrives into a finite backlog;
- the agent chooses between service, cautious service, and recovery/maintenance behavior through the frozen regulator modes;
- resource state represents remaining operational capacity;
- disturbances alter service reliability and action cost rather than directly reusing Phase-0 progress dynamics;
- failure can increase backlog or waste capacity;
- completion requires clearing a preregistered target amount of work while remaining viable.

## Primary comparison

For identical disturbance schedules and initial states:

1. full frozen Phase-0 regulator;
2. frozen `no_coupled_margin` regulator.

## Metrics

- task completion;
- viability;
- work cleared;
- remaining operational capacity;
- failures;
- repeated failures;
- recoveries;
- minimum observed resilience margin;
- mode counts.

## Primary falsification criteria

The cross-environment coupled-margin hypothesis is weakened if any of the following occur:

1. the uncoupled controller matches or exceeds the full regulator under the frozen aggregate scoring rule;
2. the full regulator is viable on fewer than 3 of 4 preregistered disturbance families;
3. the uncoupled controller completes while the full regulator fails on at least 2 families;
4. the full regulator requires any post-outcome retuning to achieve the comparison.

## Interpretation rule

A positive result is evidence only of cross-environment transfer between two controlled toy architectures. It is not evidence of a universal stability law, biological equivalence, production readiness, or autonomous-agent safety.

A negative result must be retained and must narrow or reject the transfer hypothesis rather than triggering post-hoc tuning.
