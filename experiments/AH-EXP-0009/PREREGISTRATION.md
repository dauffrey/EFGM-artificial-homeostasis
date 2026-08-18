# AH-EXP-0009 Preregistration

## Title

Trajectory-evidence / counterfactual regulation detector

## Motivation

AH-EXP-0008 was falsified. A fixed-duration protective streak was not sufficient evidence that protection had become maladaptive. The next hypothesis is therefore narrower: relaxation should occur only when recent trajectory evidence suggests that continued protection is preserving capacity while materially degrading task completion, and when a one-step counterfactual predicts that controlled relaxation has positive net value.

## Scientific question

Can a regulator distinguish **necessary protection** from **pathological over-regulation** using trajectory consequences rather than elapsed time in protective modes?

## Frozen parent evidence

AH-EXP-0008 remains unchanged and serves only as negative evidence. Its detector thresholds, holdout seed, holdout schedules, and implementation are not to be modified or reused for threshold tuning.

## Candidate mechanism to be implemented after preregistration

The AH-EXP-0009 detector may consider only pre-action information available from the current and recent trajectory. It must not use future outcomes from the schedule being evaluated.

A relaxation candidate must require all of the following evidence classes:

1. **Protection persistence:** recent controller decisions contain sustained CAUTION/RECOVERY behavior.
2. **Task degradation:** recent progress is low or zero while backlog remains materially positive or increasing.
3. **Capacity preservation:** resource remains above a frozen safety floor rather than approaching exhaustion.
4. **Counterfactual advantage:** a one-step model of NORMAL versus the controller-selected protective action predicts a positive task-value advantage after accounting for expected resource cost and failure risk.

The detector must not relax solely because a fixed number of protective steps elapsed.

## Evaluation design

- Use a new deterministic holdout generator and seed distinct from AH-EXP-0007 and AH-EXP-0008.
- Minimum holdout size: 512 bounded schedules of length 12.
- Compare the frozen full regulator against one detector-assisted variant.
- The detector logic, coefficients, thresholds, holdout seed, utility function, and falsification criteria must be committed before outcome evaluation.
- No post-outcome tuning on the evaluation holdout.
- If development/calibration examples are needed, they must be generated from a separate declared calibration seed and may not overlap the final holdout.

## Primary outcomes

- Completion rate
- Viability rate
- Total preregistered utility
- Paired utility wins/losses/ties
- Number of detector interventions
- Harmful interventions: cases where the detector changes the action and produces lower paired utility than the frozen regulator
- Beneficial interventions: cases where the detector changes the action and produces higher paired utility

## Preregistered falsification criteria

The trajectory/counterfactual detector hypothesis will be weakened or falsified if **any** of the following occur on the independent holdout:

1. Detector-assisted completion is not greater than frozen-regulator completion.
2. Detector-assisted total utility is not greater than frozen-regulator total utility.
3. Detector-assisted viability is more than 5 percentage points below frozen-regulator viability.
4. Harmful interventions are greater than or equal to beneficial interventions.
5. The detector never intervenes.
6. Any detector parameter, counterfactual coefficient, holdout definition, or utility weight is changed after observing holdout outcomes.

## Interpretation constraints

A positive result would support only the narrow claim that trajectory evidence plus a preregistered one-step counterfactual can improve over the frozen regulator in this synthetic bounded queue/service environment. It would not establish general self-awareness, consciousness, universal homeostasis, alignment, or safety.

A negative result will be retained as evidence and will not be converted into a positive result by tuning on the holdout.

## Status

**PREREGISTERED — implementation and evaluation not yet performed.**
