# AH-EXP-0009 Implementation Freeze

## Status

**IMPLEMENTATION FROZEN BEFORE FINAL HOLDOUT**

The detector implementation and its preregistered parameters are frozen before any final holdout outcomes are observed.

## Frozen implementation

- Detector source: `src/ahomeostasis/counterfactual_regulation.py`
- Frozen detector source blob SHA: `78926600bb3e860d5f1087c2277d88b96bb58a75`
- Frozen implementation branch head before evaluation harness: `1817175ea6018a94ae17269a9a49f7094cb20b28`
- Calibration seed: `9001`
- Calibration schedules: `256`
- Final holdout seed: `9011`
- Final holdout schedules: `512`
- Schedule length: `12`
- Resource floor: `0.40`
- Backlog floor: `3`
- Counterfactual threshold: `0.50`
- Resource-cost multiplier: `2.0`
- NORMAL-failure penalty: `0.75`

## Frozen detector gates

Relaxation may occur only when all preregistered trajectory and counterfactual gates are satisfied. A firing detector changes exactly one protective action to `NORMAL`; ordinary regulator control resumes on the next decision.

## Evaluation rule

The final holdout evaluator may aggregate the already-preregistered completion, viability, utility, paired-win, intervention, and falsification measures. It may not alter detector logic, generator constraints, seeds, utility weights, thresholds, coefficients, or falsification criteria.

The final `9011` holdout is to be executed once, only after exact-head CI passes with the detector source blob above unchanged.

## Holdout exposure

At the time of this freeze, final holdout outcomes have not been observed.
