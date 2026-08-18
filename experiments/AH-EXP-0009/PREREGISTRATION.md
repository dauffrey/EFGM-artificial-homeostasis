# AH-EXP-0009 Preregistration

## Title

Trajectory-evidence / counterfactual regulation detector

## Motivation

AH-EXP-0008 was falsified. A fixed-duration protective streak was not sufficient evidence that protection had become maladaptive. The next hypothesis is therefore narrower: relaxation should occur only when recent trajectory evidence suggests that continued protection is preserving capacity while materially degrading task completion, and when a one-step counterfactual predicts that controlled relaxation has positive net value.

## Scientific question

Can a regulator distinguish **necessary protection** from **pathological over-regulation** using trajectory consequences rather than elapsed time in protective modes?

## Frozen parent evidence

AH-EXP-0008 remains unchanged and serves only as negative evidence. Its detector thresholds, holdout seed, holdout schedules, and implementation are not to be modified or reused for threshold tuning.

## Frozen design

The full operational freeze is recorded in `experiments/AH-EXP-0009/DESIGN_FREEZE.md` and is part of this preregistration.

Key frozen values:

- calibration seed: `9001`;
- calibration size: `256` schedules;
- final holdout seed: `9011`;
- final holdout size: `512` schedules;
- schedule length: `12`;
- resource safety floor: `0.40`;
- backlog floor: `3`;
- protection-persistence gate: at least 2 protective decisions in the current/previous 3-decision window;
- task-stagnation gate: no more than 1 unit of work cleared across the previous 2 completed decision intervals;
- backlog-pressure gate: backlog not lower than 2 decision points earlier;
- counterfactual threshold: `CF >= 0.50`;
- counterfactual coefficients: resource-cost multiplier `2.0`, NORMAL-failure penalty `0.75`;
- intervention: exactly one NORMAL action, followed by ordinary regulator control on the next step;
- evaluation utility: unchanged AH-EXP-0007 utility.

No detector gate, coefficient, seed, generator constraint, utility weight, or falsification criterion may be altered after final-holdout outcomes are observed.

## Detector evidence classes

A relaxation candidate requires all four evidence classes simultaneously:

1. **Protection persistence:** recent controller decisions contain sustained CAUTION/RECOVERY behavior.
2. **Task degradation:** recent progress is low while backlog remains materially positive and non-improving.
3. **Capacity preservation:** resource remains above the frozen safety floor.
4. **Counterfactual advantage:** the frozen one-step model predicts that a single NORMAL action has at least `0.50` greater net task value than the selected protective action after resource cost and failure risk are accounted for.

The detector may use only current or historical pre-action information. It may not inspect future disturbances or outcomes.

## Calibration / holdout separation

Calibration is limited to implementation sanity checks using seed `9001`; it is not permitted to drive parameter tuning. The independent final holdout uses seed `9011` and must remain unobserved until the implementation and invariant tests pass with the frozen constants unchanged.

The AH-EXP-0007 search seed `7001` and AH-EXP-0008 holdout seed `8009` are not reused.

## Primary outcomes

- Completion rate
- Viability rate
- Total preregistered utility
- Paired utility wins/losses/ties
- Number of detector interventions
- Harmful interventions
- Beneficial interventions
- Neutral interventions
- Mean interventions per schedule

## Preregistered falsification criteria

The trajectory/counterfactual detector hypothesis will be weakened or falsified if **any** of the following occur on the independent 512-schedule holdout:

1. Detector-assisted completion is not greater than frozen-regulator completion.
2. Detector-assisted total utility is not greater than frozen-regulator total utility.
3. Detector-assisted viability is more than 5 percentage points below frozen-regulator viability.
4. Harmful interventions are greater than or equal to beneficial interventions.
5. The detector never intervenes.
6. Any detector parameter, counterfactual coefficient, generator constraint, holdout seed, utility weight, or falsification criterion is changed after observing holdout outcomes.

## Interpretation constraints

A positive result would support only the narrow claim that trajectory evidence plus a preregistered one-step counterfactual can improve over the frozen regulator in this synthetic bounded queue/service environment. It would not establish general self-awareness, consciousness, universal homeostasis, alignment, or safety.

A negative result will be retained as evidence and will not be converted into a positive result by tuning on the holdout.

## Execution order

1. Freeze preregistration and design.
2. Implement the detector exactly as frozen.
3. Add invariant/unit tests without inspecting final holdout aggregate outcomes.
4. Run calibration/structural validation only for implementation sanity.
5. Confirm exact-head CI is green.
6. Execute the final holdout once.
7. Record the result whether positive or negative.

## Status

**DESIGN FROZEN BEFORE HOLDOUT — implementation and evaluation not yet performed.**
