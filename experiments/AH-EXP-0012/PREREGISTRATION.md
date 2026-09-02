# AH-EXP-0012 Preregistration

## Title

Pre-escape governance signal detection: can an EFGM-derived temporal observer warn of viability loss before escape?

## Status

**PREREGISTERED — CONFIRMATORY AH-EXP-0012 HOLDOUT OUTCOMES HAVE NOT BEEN OBSERVED**

AH-EXP-0012 follows AH-EXP-0011, which established reproducible `STABLE`, `RECOVERED`, and `FAILED` regions and finite escape times in the frozen synthetic queue/service environment.

The AH-EXP-0011 canonical trajectories and outcomes are already known and are therefore **development data only** for AH-EXP-0012. They are not eligible as confirmatory AH-EXP-0012 evidence.

AH-EXP-0012 uses a new deterministic disturbance family whose outcomes must remain unobserved until:

1. the EFGM observer adapter is implemented and frozen;
2. the warning rule and all baseline thresholds are frozen using development data only;
3. structure-only tests are green;
4. exact-head CI is green; and
5. the reviewed implementation SHA is frozen.

No confirmatory holdout trajectory may be executed during observer construction, threshold selection, or structural CI.

## Frozen provenance

### Artificial-homeostasis system

AH-EXP-0012 uses the frozen AH-EXP-0011 trajectory implementation as its operational substrate:

```text
e21d68d1257ef36a3882a5f6362535f701d6350c
```

No AH-EXP-0012 change may retune the controller, queue environment, viability definition, service thresholds, maintenance behavior, backlog limit, resource dynamics, or controller switching logic.

### EFGM research implementation

The observer design is anchored to the current EFGM research baseline at preregistration time:

```text
repository: dauffrey/efgm
code SHA:   37b2ff2d2b577c9f383dd0d7c3083597627150ea
canonical:  EFGM v2 — Decision Integrity
extension:  Agent Governance v0.3
```

The EFGM implementation identity and candidate configuration hashes used by the actual AH-EXP-0012 observer must be recorded in the implementation freeze and result evidence.

AH-EXP-0012 does not promote Agent Governance v0.3 to a validated production model.

## Research question

Can an EFGM-derived temporal observer, using only evidence available at the current viable step, identify that the artificial-homeostasis trajectory is approaching loss of viability before the first escape event occurs?

In plain language:

> **Can EFGM provide an early warning that the system is heading toward failure while the system is still viable?**

## Primary hypothesis

On a previously unobserved deterministic disturbance family, a frozen EFGM-derived warning score will identify impending escape within the next two steps with positive lead time and will provide predictive information beyond the best frozen single-variable operational baseline.

The primary prediction horizon is:

```text
h = 2 future steps
```

AH-EXP-0012 does not require every escape to be predicted.

## Scientific separation from AH-EXP-0011

AH-EXP-0011 answered:

```text
Can stable/recovery/failure boundaries and escape time be measured?
```

AH-EXP-0012 asks:

```text
Can a causal EFGM-derived observation at time t predict escape after time t?
```

The measured AH-EXP-0011 boundaries, escape times, and trajectories may be used to construct and freeze the observer, but may not be reported as AH-EXP-0012 confirmatory performance.

## Frozen operational controllers

### Primary controller

```text
robust_counterfactual_abstention
```

The mechanism remains exactly as frozen in the AH-EXP-0011 implementation.

### Secondary controller

```text
coupled_margin
```

The secondary controller is descriptive unless otherwise stated. Primary survival is evaluated on the primary controller.

## Observation phase and causality boundary

AH-EXP-0012 predictions are made only at an **end-of-step viable observation point**.

For step `t`, the observer may use evidence available after the action for step `t` has completed, provided that:

```text
completed == False
viable == True
```

The observer may not use:

- any disturbance from step `t + 1` or later;
- any state produced by step `t + 1` or later;
- final trajectory class;
- `tau_escape`;
- future recovery actions;
- future completion state;
- future failure mechanism;
- any field computed from future labels.

If viability is first lost during `post_arrival` of step `t + 1`, a warning emitted at the end of step `t` counts as one-step lead time.

A warning generated after viability has already been lost is not an early warning and receives no credit.

## Time-t evidence channels

The AH-to-EFGM observer adapter may consume only these operational channels through the current observation point:

- current and prior realized disturbance values;
- resource;
- backlog;
- work cleared / progress;
- failure count;
- repeated-failure count;
- regulator margin;
- selected mode;
- executed mode;
- action success/failure when known;
- recovery-action execution;
- AH-EXP-0010 relaxation-intervention occurrence;
- sequence position / observation maturity;
- explicitly derived finite-window history from the above fields.

No additional hidden simulator state may be introduced after confirmatory outcomes are observed.

## EFGM observer outputs

The primary observer must expose the following EFGM research outputs when semantically applicable:

```text
DQ   — EFGM v2 decision quality
CRC  — EFGM v2 coherence recovery capacity
GI   — Agent Governance v0.3 governance integrity
AE   — Agent Governance v0.3 agency exposure
CUE  — Agent Governance v0.3 coherent unsafe execution
```

and temporal changes when two consecutive observations are available:

```text
Delta_DQ
Delta_CRC
Delta_GI
Delta_AE
Delta_CUE
```

The adapter must use evidence-backed `MetricObservation` semantics. `unknown` and `not_applicable` must remain explicit and may not be silently replaced with zero.

If a canonical EFGM or Agent Governance metric cannot be mapped meaningfully from the synthetic environment, it must be marked `not_applicable` or `unknown` according to the frozen adapter specification. A metric may not be fabricated merely to increase predictive performance.

## Observer-adapter development phase

AH-EXP-0012 deliberately separates **observer construction** from **confirmatory evaluation**.

The already-observed AH-EXP-0011 canonical trajectories are the only outcome-labelled data permitted for observer-adapter development and warning-threshold selection.

Before any AH-EXP-0012 holdout outcome is observed, the implementation must preserve an `OBSERVER_SPEC.md` (or equivalent machine-readable spec) containing:

- the exact mapping from each permitted operational channel to each EFGM observation;
- applicability / N/A rules;
- evidence references and scorer identity used for synthetic observations;
- EFGM configuration IDs and SHA-256 hashes;
- finite history-window definitions;
- risk orientation for each feature;
- normalization procedure;
- warning-score equation;
- threshold-selection procedure;
- frozen selected threshold;
- baseline thresholds;
- code SHA and input-development-data hash.

The observer specification must be committed and frozen before holdout execution.

## Primary EFGM warning feature set

The primary warning score may use only:

```text
DQ, CRC, GI, AE, CUE,
Delta_DQ, Delta_CRC, Delta_GI, Delta_AE, Delta_CUE
```

No raw backlog, resource, disturbance, margin, failure count, controller mode, or final trajectory label may enter the **primary EFGM score directly**.

Those operational variables may be used by the adapter to construct evidence-backed EFGM observations, but their mapping must be documented and frozen before holdout execution.

## Risk orientation

Risk directions are frozen as:

```text
lower DQ       = higher risk
lower CRC      = higher risk
lower GI       = higher risk
higher AE      = higher risk
higher CUE     = higher risk
lower Delta_DQ = higher risk
lower Delta_CRC= higher risk
lower Delta_GI = higher risk
higher Delta_AE= higher risk
higher Delta_CUE= higher risk
```

This directionality may not be reversed after holdout outcomes are observed.

## Frozen normalization and composite rule

Using development data only, each applicable primary feature is transformed to an empirical risk percentile in `[0, 1]` according to its frozen risk direction.

For a feature where larger values mean higher risk:

```text
risk_percentile(x) = empirical_fraction(development_feature <= x)
```

For a feature where smaller values mean higher risk:

```text
risk_percentile(x) = empirical_fraction(development_feature >= x)
```

Ties use the inclusive empirical fraction as written above.

At time `t`, the composite score is the arithmetic mean of all applicable, observed risk percentiles available at that observation point:

```text
EFGM_RISK_t = mean(applicable risk percentiles at t)
```

A minimum of three applicable primary features is required to issue a scored EFGM observation. Otherwise the observation is `INSUFFICIENT_EFGM_EVIDENCE` and cannot be counted as a positive warning.

No feature weighting is permitted in AH-EXP-0012.

## Development labels

For each viable, incomplete end-of-step observation in the AH-EXP-0011 development trajectories, define the primary label:

```text
y_t_2 = 1  if first loss of viability occurs in step t+1 or t+2
        0  otherwise
```

Only future escape is positive. Completion without escape is negative.

## Frozen warning-threshold selection

The EFGM warning threshold is selected **once** using AH-EXP-0011 development data only.

Candidate thresholds are the distinct observed `EFGM_RISK_t` values in development data.

Choose the threshold maximizing **balanced accuracy** for `y_t_2` under the rule:

```text
WARN if EFGM_RISK_t >= threshold
```

Tie-break order is frozen:

1. higher specificity;
2. higher precision;
3. higher threshold.

The selected threshold must be written into the frozen observer specification before AH-EXP-0012 holdout execution.

No threshold tuning on AH-EXP-0012 outcomes is permitted.

## Frozen operational baselines

AH-EXP-0012 compares the EFGM warning rule against four single-variable operational baselines:

```text
B1: backlog high
B2: resource low
B3: regulator margin low
B4: realized disturbance high
```

Each baseline uses only the corresponding time-t variable.

Each baseline threshold is selected from AH-EXP-0011 development data using the same primary label, balanced-accuracy objective, and tie-break procedure as the EFGM warning threshold, with the fixed risk direction shown above.

No baseline may use multiple operational variables.

The **best single-variable baseline** is the baseline with the highest development balanced accuracy; ties are resolved in order `B1`, `B2`, `B3`, `B4` solely to make the selection deterministic.

The identity and threshold of the selected best baseline must be frozen before holdout execution.

## New confirmatory disturbance family

### Base disturbance grid

Use:

```text
mu = 0.000, 0.005, 0.010, ..., 0.995, 1.000
```

Exactly 201 trajectories per controller.

### Frozen 20-step modulation cycle

For each `mu`, use this previously unevaluated deterministic cycle:

```text
[-0.15, -0.09, -0.03, +0.03, +0.09,
 +0.15, +0.09, +0.03, -0.03, -0.09,
 -0.12, -0.06,  0.00, +0.06, +0.12,
 +0.06,  0.00, -0.06,  0.00,  0.00]
```

The cycle sum is zero.

At step `t`:

```text
d_t = clip(mu + modulation[t mod 20], 0.0, 1.0)
```

The values, order, cycle length, starting phase, clipping rule, and base-disturbance grid are frozen by this preregistration.

### Horizon

```text
100 steps
```

Trajectories terminate earlier on task completion or loss of viability.

## Confirmatory prediction samples

For each holdout trajectory, evaluate every end-of-step observation satisfying:

```text
completed == False
viable == True
```

The primary target is:

```text
y_t_2 = 1  if first escape occurs within the next two steps
        0  otherwise
```

Observations fewer than two steps from a trajectory's successful completion remain negative if no escape occurs.

## Lead time

For an escape trajectory, define the first true positive warning time:

```text
t_warning = earliest viable observation t where WARN == True and t < tau_escape
```

Lead time is:

```text
lead_time = tau_escape - t_warning
```

A warning at the same step as escape is not credited.

If no pre-escape warning occurs, lead time is not observed for that trajectory and the escape is counted as missed.

## Primary performance metrics

Report for the EFGM warning rule and every baseline:

- true positives;
- false positives;
- true negatives;
- false negatives;
- sensitivity / recall;
- specificity;
- precision;
- balanced accuracy;
- warning-positive rate;
- number and fraction of escape trajectories receiving at least one pre-escape warning;
- lead-time distribution for detected escapes;
- missed escapes.

The primary predictive metric is **balanced accuracy** on the step-level `y_t_2` label.

## Primary incremental-value comparison

Let:

```text
BA_EFGM = holdout balanced accuracy of the frozen EFGM warning rule
BA_BASE = holdout balanced accuracy of the frozen best single-variable baseline
```

Define:

```text
Delta_BA = BA_EFGM - BA_BASE
```

## Primary survival criteria

AH-EXP-0012 **SURVIVES** its primary hypothesis only if all of the following hold for the primary controller:

1. the confirmatory holdout contains at least one positive and at least one negative `y_t_2` observation;
2. `BA_EFGM > 0.50`;
3. `Delta_BA >= 0.02` relative to the frozen best single-variable baseline;
4. at least one escape trajectory receives a true positive warning with `lead_time >= 1`;
5. every prediction is auditable to time-t-only evidence with no future-label leakage;
6. all EFGM configuration identities, input hashes, adapter hashes, and evidence provenance required by the frozen observer specification are present;
7. the exact reproducibility rerun produces identical prediction rows, confusion matrices, lead-time records, thresholds, and canonical result hashes;
8. no observer mapping, feature set, normalization, threshold, baseline, disturbance family, horizon, label definition, or survival criterion is changed after confirmatory outcomes are observed.

## Preregistered falsification criteria

AH-EXP-0012 is **FALSIFIED** if the holdout has adequate positive/negative label diversity and any required primary survival criterion fails.

In particular, falsifying outcomes include:

- EFGM balanced accuracy at or below chance (`<= 0.50`);
- EFGM failing to exceed the frozen best single-variable baseline by `0.02` balanced-accuracy points;
- zero pre-escape true-positive warnings;
- use of future information in any primary feature or warning;
- post-hoc changes to EFGM metric applicability or mapping in response to holdout performance;
- post-hoc threshold tuning;
- silently substituting raw operational variables into the primary EFGM score;
- irreproducible deterministic results.

## Inconclusive conditions

AH-EXP-0012 is **INCONCLUSIVE**, not automatically falsified, if the frozen holdout produces no positive `y_t_2` samples or no negative `y_t_2` samples, because balanced accuracy and discrimination cannot then test the preregistered hypothesis.

It is also inconclusive if fewer than three EFGM primary features can be meaningfully and consistently mapped across the holdout under the frozen evidence/applicability rules. Such an outcome is evidence that this synthetic environment is inadequate for the intended EFGM bridge experiment and must be reported without manufacturing replacement metrics.

## Secondary analyses

The following are descriptive only unless separately preregistered later:

- prediction horizons `h = 1` and `h = 3`;
- individual EFGM metric performance;
- individual delta-feature performance;
- primary versus comparison controller results;
- warning performance stratified by eventual `STABLE`, `RECOVERED`, and `FAILED` trajectory classes;
- warning performance near versus far from measured AH-EXP-0011 boundary regions;
- relationships between warning score and measured lead time.

Secondary analyses may not rescue a failed primary hypothesis.

## Required evidence preservation

The first confirmatory run must preserve, before any reproducibility rerun:

- frozen artificial-homeostasis implementation SHA;
- frozen EFGM code SHA;
- EFGM configuration IDs and hashes;
- observer-specification hash;
- development input/result hash used for threshold selection;
- frozen EFGM threshold;
- all four baseline thresholds;
- selected best-baseline identity;
- holdout generator identity/hash;
- every step-level prediction row;
- every underlying EFGM observation and provenance reference;
- true future label stored separately from time-t feature payload where practical;
- escape time and lead-time records;
- confusion matrices;
- balanced-accuracy values;
- canonical ordered result hash;
- complete full-trace hash.

The first-run evidence must be committed or uploaded as an immutable workflow artifact before triggering the exact rerun.

## Reproducibility rerun

After first-run evidence is preserved, rerun the exact frozen evaluation with no source, threshold, configuration, or parameter change.

The rerun must reproduce exactly:

- all step-level warning decisions;
- all future labels;
- all confusion-matrix counts;
- all lead-time records;
- all EFGM and baseline performance metrics;
- the canonical ordered result hash;
- the full-trace hash.

## Claims explicitly not tested

AH-EXP-0012 does not establish:

- real-world AI-agent failure prediction;
- general safety or alignment;
- causal validity of EFGM metrics outside this synthetic environment;
- universal critical-transition mathematics;
- fractal or Mandelbrot-like boundaries;
- chaos or Lyapunov instability;
- production-ready warning thresholds;
- optimality of the EFGM observer;
- superiority over multivariate machine-learning predictors;
- biological equivalence to homeostasis;
- consciousness or subjective awareness.

## Interpretation rule

A surviving result means only:

> In the frozen synthetic artificial-homeostasis system and previously unobserved AH-EXP-0012 disturbance family, a preregistered EFGM-derived temporal warning rule contained short-horizon information about impending viability loss beyond the strongest frozen single-variable operational baseline tested.

A failed result means the preregistered EFGM observer did not demonstrate that incremental early-warning value under this experiment.

Neither outcome permits changing the result after observation.

## Required execution order

```text
1. merge/freeze this preregistration
2. build observer adapter using AH-EXP-0011 development data only
3. freeze OBSERVER_SPEC and all selected thresholds
4. structure-only review
5. exact-head CI
6. freeze AH-EXP-0012 implementation SHA
7. execute first confirmatory holdout run
8. preserve first-run evidence
9. execute exact reproducibility rerun
10. record SURVIVED / FALSIFIED / INCONCLUSIVE without retuning
```
