# AH-EXP-0010 Preregistration

## Title

Robust counterfactual abstention: can an adaptive regulator improve aggregate outcomes while maintaining positive intervention-level causal value?

## Status

**PREREGISTERED — NO AH-EXP-0010 OUTCOMES OBSERVED**

This experiment is motivated by the immutable AH-EXP-0009 falsification. AH-EXP-0009 improved aggregate completion, viability, and utility but failed its intervention-level governance criterion because harmful intervention schedules (62) were greater than beneficial intervention schedules (57).

AH-EXP-0010 does not modify, retune, or reinterpret AH-EXP-0009.

## Primary hypothesis

A regulator that **abstains from relaxation unless the predicted benefit is robust to bounded uncertainty in the observed disturbance** will improve aggregate performance while producing more beneficial than harmful intervention schedules on an independent holdout.

In plain language: the system should intervene only when its reason for overriding protective behavior remains favorable even if its local disturbance estimate is slightly wrong.

## Frozen baseline

The comparison baseline is the frozen AH-EXP-0009 regulator without adaptive relaxation.

The AH-EXP-0009 trajectory gates remain structurally unchanged:

1. selected action is `CAUTION` or `RECOVERY`;
2. at least 2 of the current plus two preceding selected modes are protective;
3. work cleared has increased by no more than 1 unit relative to the snapshot from 2 decision points earlier;
4. backlog is at least 3 and is not lower than it was 2 decision points earlier;
5. resource is at least 0.40.

A successful intervention may change **exactly one** protective action to `NORMAL`. Ordinary regulator control resumes on the next decision.

## New AH-EXP-0010 mechanism: robust counterfactual abstention

AH-EXP-0009 used a one-step counterfactual score:

`CF(d) = progress_gain - 2.0 * excess_resource_cost - 0.75 * normal_failure_indicator`

AH-EXP-0010 retains that score and its coefficients unchanged, but does not trust a single point estimate of disturbance.

For the current disturbance observation `d`, compute the same frozen counterfactual at three bounded views:

- `d_low = clip(d - 0.08, 0, 1)`
- `d_mid = d`
- `d_high = clip(d + 0.08, 0, 1)`

Define:

`robust_CF = min(CF(d_low), CF(d_mid), CF(d_high))`

The detector may relax a protective action only when **all frozen trajectory gates hold and `robust_CF >= 0.50`**.

Otherwise it abstains and leaves the frozen regulator's selected action unchanged.

No other confidence model, adaptive threshold, learning rule, multi-step override, or post-outcome tuning is permitted.

## Evaluation sets

### Structural validation set

- seed: `10010`
- schedules: `256`
- schedule length: `12`
- same bounded schedule generator constraints used by AH-EXP-0009
- purpose: implementation/invariant validation only
- performance on this set may not be used to tune thresholds, coefficients, uncertainty width, generator constraints, or falsification criteria

### Independent final holdout

- seed: `10011`
- schedules: `512`
- schedule length: `12`
- same bounded generator constraints
- must remain unobserved until implementation fidelity, invariant tests, and exact-head CI are green
- execute once for canonical evidentiary evaluation

The holdout execution mechanism must be commit-bound or otherwise technically one-shot before final evaluation; branch-name-only execution gating is prohibited.

## Primary measures

For frozen and adaptive variants record:

- completed schedules;
- viable schedules;
- total utility;
- paired utility wins/ties;
- total interventions;
- number of schedules containing interventions;
- beneficial intervention schedules;
- harmful intervention schedules;
- neutral intervention schedules.

An intervention schedule is beneficial when adaptive utility exceeds frozen utility, harmful when adaptive utility is lower, and neutral when equal.

## Preregistered falsification criteria

AH-EXP-0010 is falsified/weakened if **any** of the following occurs on the independent final holdout:

1. adaptive completion is not greater than frozen completion;
2. adaptive total utility is not greater than frozen total utility;
3. adaptive viability is more than 5 percentage points below frozen viability;
4. harmful intervention schedules are greater than or equal to beneficial intervention schedules;
5. the detector never intervenes;
6. any detector gate, counterfactual coefficient, robust uncertainty width (`±0.08`), threshold (`0.50`), generator constraint, seed, utility definition, or falsification criterion changes after holdout outcomes are observed.

## Interpretation rule

Aggregate improvement alone is insufficient. The hypothesis survives only if the adaptive regulator improves completion and total utility, preserves viability within the declared tolerance, **and** demonstrates a positive intervention-level balance (`beneficial > harmful`).

A failed result will be preserved as a negative result. No threshold search or holdout retuning will be used to convert failure into success.

## Claims explicitly not tested

AH-EXP-0010 does not test or establish:

- consciousness or subjective awareness;
- biological homeostasis;
- universal AI-agent safety;
- production readiness;
- capability-regulation divergence across real model families.

Those require separate experiments.
