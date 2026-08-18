# AH-EXP-0009 Design Freeze

## Purpose

Freeze the calibration/holdout separation, detector inputs, coefficients, thresholds, counterfactual model, utility, and falsification rules before any AH-EXP-0009 holdout outcomes are observed.

## Data separation

### Calibration / structural-validation set

- Generator family: bounded 12-step schedules generated from independent `random.Random` draws.
- Calibration seed: `9001`.
- Calibration size: `256` schedules.
- Constraint: at most 6 values greater than `0.80`; mean disturbance between `0.25` and `0.70` inclusive.
- Permitted use: implementation debugging, detector activation sanity checks, invariant checks, and confirming that both protective and non-protective trajectories occur.
- Prohibited use: changing detector thresholds, coefficients, utility weights, or falsification criteria in response to calibration performance. The values below are frozen now.

### Final holdout

- Holdout seed: `9011`.
- Holdout size: `512` schedules.
- Schedule length: `12`.
- Same bounded generator constraints as calibration, but a distinct seed and independently generated candidate stream.
- No schedule from the AH-EXP-0007 search seed `7001`, AH-EXP-0008 seed `8009`, or calibration seed `9001` may be reused.
- Holdout outcomes must not be inspected until implementation and invariant tests pass with all frozen constants unchanged.

## Frozen detector state

The detector may use only information available at or before the current action:

- current disturbance;
- current resource;
- current backlog;
- current failure count;
- current regulator-selected mode;
- work-cleared and backlog snapshots captured at the start of the previous decision points;
- regulator modes from previous decision points.

It may not inspect future disturbances or future outcomes.

## Frozen trajectory evidence gates

A protective action is eligible for relaxation only if all gates pass.

1. **Current action is protective**: selected mode is `CAUTION` or `RECOVERY`.
2. **Protection persistence**: among the current selected mode plus the two immediately preceding selected modes, at least 2 are protective (`CAUTION` or `RECOVERY`).
3. **Task stagnation**: current `work_cleared` minus the `work_cleared` snapshot from 2 decision points earlier is no more than 1 unit.
4. **Backlog pressure**: current backlog is at least `3` and is not lower than the backlog snapshot from 2 decision points earlier.
5. **Capacity floor**: current resource is at least `0.40`.
6. **Counterfactual advantage**: the frozen one-step counterfactual score defined below is at least `0.50`.

If fewer than 2 prior decision-point snapshots exist, gates 2-4 fail and no intervention is allowed. No fixed protective-streak duration alone is sufficient to trigger relaxation.

## Frozen one-step counterfactual model

The model evaluates one NORMAL action against the regulator-selected protective action using the **current** disturbance only.

Predicted NORMAL service:

- predicted units cleared = `2` when disturbance <= `0.58`, otherwise `0`;
- predicted resource cost = `0.085 + 0.12 * disturbance`;
- add failure cost `0.14` when disturbance > `0.58`;
- predicted failure indicator = `1` when disturbance > `0.58`, otherwise `0`.

Predicted CAUTION service:

- predicted units cleared = `1` when disturbance <= `0.80`, otherwise `0`;
- predicted resource cost = `0.055 + 0.045 * disturbance`;
- add failure cost `0.055` when disturbance > `0.80`.

Predicted RECOVERY action:

- predicted units cleared = `0`;
- predicted resource change is a gain of `max(0.025, 0.11 * (1 - disturbance))`.

The frozen counterfactual advantage is:

`CF = progress_gain - 2.0 * excess_resource_cost - 0.75 * normal_failure_indicator`

where:

- `progress_gain = NORMAL predicted units - selected-action predicted units`;
- `excess_resource_cost = NORMAL predicted resource cost - selected-action predicted resource cost`, treating RECOVERY gain as negative cost.

Relaxation is permitted only when `CF >= 0.50` and all trajectory evidence gates pass.

## Frozen intervention

When the detector fires, exactly one action is changed from the regulator-selected `CAUTION`/`RECOVERY` action to `NORMAL`. The regulator itself is not modified. On the next step, the regulator again selects its normal mode and the detector reevaluates from observed trajectory evidence.

No multi-step override, threshold adaptation, or learned parameter update is permitted.

## Frozen evaluation utility

Use the existing AH-EXP-0007 utility unchanged:

`4*completed + 3*viable + 2*progress + resource - 0.25*failures - 0.50*repeated_failures`

No utility weights may change after holdout outcomes are observed.

## Primary outcomes

- completion count and rate;
- viability count and rate;
- total utility;
- paired utility wins/losses/ties;
- total interventions;
- beneficial interventions;
- harmful interventions;
- neutral interventions;
- mean interventions per schedule.

A schedule with one or more detector interventions is classified as beneficial/harmful/neutral by the final paired schedule utility relative to the frozen regulator on the identical schedule. Schedules with no intervention are not counted in these three intervention-effect categories.

## Frozen falsification criteria

AH-EXP-0009 is weakened/falsified if **any** condition is true on the final 512-schedule holdout:

1. detector-assisted completion <= frozen-regulator completion;
2. detector-assisted total utility <= frozen-regulator total utility;
3. detector-assisted viability < frozen viability - `0.05 * 512`;
4. harmful intervention schedules >= beneficial intervention schedules;
5. total interventions == 0;
6. any detector gate, threshold, coefficient, generator constraint, seed, utility weight, or falsification criterion is changed after holdout outcomes are observed.

## Execution order

1. Commit this design freeze.
2. Implement detector and generator exactly as frozen.
3. Add invariant/unit tests that do not inspect final holdout aggregate outcomes.
4. Run calibration/structural-validation only for implementation sanity; no parameter changes are permitted from its performance.
5. Confirm exact-head CI is green.
6. Execute the final holdout once.
7. Record the result whether positive or negative.

## Status

**FROZEN BEFORE HOLDOUT — no AH-EXP-0009 holdout outcomes observed.**
