# AH-EXP-0005 — Results

## Status

Observed after preregistration and successful protected-PR CI execution.

## Environment

Bounded queue/service environment with finite backlog, disturbance-driven arrivals, service reliability changes, cautious service, maintenance/recovery actions, and operational-capacity costs.

The Phase-0 regulator coefficients and mode thresholds were carried forward unchanged. No post-outcome retuning was used.

## Aggregate scores

| Controller | Score |
|---|---:|
| Full frozen regulator | 16 |
| No coupled resilience margin | 5 |

## Falsification outcome

- `uncoupled_matches_or_exceeds_full = false`
- `full_viable_on_fewer_than_3_schedules = false`
- `uncoupled_completes_two_where_full_fails = false`
- `post_outcome_retuning_required = false`

None of the preregistered AH-EXP-0005 falsification criteria were triggered.

## Schedule observations

### alternating_load

- Full regulator: completed, viable, 8 work cleared, 0 failures, 0 repeated failures, ~0.5054 resource remaining.
- Uncoupled: did not complete, non-viable, 7 work cleared, 2 failures, 0 repeated failures, resource exhausted.

### bursty_arrivals

- Full regulator: completed, viable, 9 work cleared, 0 failures, 0 repeated failures, ~0.5070 resource remaining.
- Uncoupled: did not complete, non-viable, 7 work cleared, 2 failures, 1 repeated failure, resource exhausted.

### late_surge

- Both controllers completed and remained viable with identical work cleared and remaining resource. This family produced no separation.

### sustained_pressure

- Full regulator: completed, viable, 8 work cleared, 0 failures, 0 repeated failures, ~0.5230 resource remaining.
- Uncoupled: did not complete, non-viable, 7 work cleared, 2 failures, 1 repeated failure, resource exhausted.

## Interpretation

AH-EXP-0005 supports cross-environment transfer of the narrower coupled-margin effect between two controlled toy architectures. The full frozen regulator materially separated from the uncoupled variant on alternating load, bursty arrivals, and sustained pressure, while late surge produced no separation.

This result is stronger than a within-environment retest because the Phase-0 regulator was not retuned and the environment uses different state transitions and action semantics. It still does not establish a universal stability law, biological equivalence, production readiness, or autonomous-agent safety.

## Next test

A stronger next step should introduce stochasticity and seed replication so that the effect must survive probabilistic variation rather than one deterministic trajectory per disturbance family.
