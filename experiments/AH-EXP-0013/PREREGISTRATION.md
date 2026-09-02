# AH-EXP-0013 Preregistration

## Title

Latent observation-integrity degradation: can an EFGM-derived governance observer warn of harmful control divergence before ordinary operational telemetry makes the problem obvious?

## Status

**PREREGISTERED — CONFIRMATORY AH-EXP-0013 HOLDOUT OUTCOMES HAVE NOT BEEN OBSERVED**

AH-EXP-0013 follows the falsified AH-EXP-0012 incremental early-warning hypothesis.

AH-EXP-0012 established two facts that motivate this experiment:

1. the frozen EFGM-derived observer contained genuine pre-escape signal and warned before all observed escape trajectories in that holdout; and
2. a simple backlog threshold was substantially more discriminating, so the tested EFGM composite did not add predictive value beyond direct operational telemetry.

AH-EXP-0013 does **not** retune AH-EXP-0012 and does not attempt to rescue its result. It changes the scientific question.

AH-EXP-0012 primarily tested a capacity/viability failure whose near-term mechanism was backlog overflow. AH-EXP-0013 instead tests a governance-specific failure mode: degradation of observation integrity causes the controller to act on misleading evidence before backlog, resource, or other ordinary queue-state variables necessarily indicate imminent failure.

## Frozen provenance

### Artificial-homeostasis result baseline

AH-EXP-0013 is preregistered on top of the preserved AH-EXP-0012 evidence branch at:

```text
744fa9d65cf21999c22f630e9635254d4313497d
```

### Frozen operational substrate

The queue/service dynamics and controller mechanics remain anchored to:

```text
e21d68d1257ef36a3882a5f6362535f701d6350c
```

The existing distinction between true disturbance and observed disturbance used by the adversarial-robustness laboratory is retained conceptually. AH-EXP-0013 may add a new deterministic observation-integrity layer, but it may not retune queue arrival rules, service thresholds, resource costs, maintenance gain, backlog viability limit, or regulator switching thresholds after confirmatory outcomes are observed.

### EFGM research implementation

The EFGM observer remains anchored to:

```text
repository: dauffrey/efgm
code SHA:   37b2ff2d2b577c9f383dd0d7c3083597627150ea
canonical:  EFGM v2 — Decision Integrity
extension:  Agent Governance v0.3
```

Actual implementation and configuration hashes must be preserved in the observer freeze and result evidence.

## Why AH-EXP-0013 is a different test

The frozen AH-EXP-0012 observer treated synthetic grounding, observability, and current uncertainty calibration as effectively perfect because all permitted simulator channels were directly visible and traceable. Its governance mapping therefore depended heavily on operational quantities such as backlog slack, margin fit, resource, and action outcomes.

AH-EXP-0013 deliberately introduces **evidence-quality degradation** so that the EFGM constructs most relevant to governance can vary meaningfully:

- grounding / evidence validity;
- uncertainty calibration;
- hidden-information load;
- observability;
- boundary integrity;
- control recoverability;
- temporal change in those constructs.

The experiment is not designed to make EFGM win. It is designed to determine whether EFGM provides incremental information in a failure mode for which direct backlog proximity is not the complete causal story.

## Research question

Can a frozen EFGM-derived governance observer, using only evidence available at time `t`, predict that degraded observation integrity will produce a harmful under-protective control action within the next two steps, and can it outperform simple operational and sensor-quality baselines?

In plain language:

> **Can EFGM see that the controller is beginning to trust bad information before that bad information causes an objectively harmful decision?**

## Primary hypothesis

On a previously unobserved deterministic observation-integrity holdout, a frozen EFGM-derived warning rule will:

1. predict harmful control divergence within the next two steps with balanced accuracy above chance;
2. issue at least one true warning before the harmful event occurs; and
3. exceed the strongest frozen simple baseline by at least `0.02` balanced-accuracy points.

Primary prediction horizon:

```text
h = 2 future steps
```

## Primary event: harmful under-protection

AH-EXP-0013 does **not** use backlog overflow as its primary failure label.

At each decision step, define:

```text
true_disturbance     = d_t
observed_disturbance = d_hat_t
```

The actual controller computes its mode from `d_hat_t` and the current telemetry.

An oracle comparator computes the mode from `d_t` using the **same current pre-action telemetry** and the same frozen regulator equations.

Protection ordering is frozen as:

```text
NORMAL < CAUTION < RECOVERY
```

A step is a `HARMFUL_UNDERPROTECTION_EVENT` only if all of the following are true:

1. the actual selected/executed mode is strictly less protective than the oracle mode;
2. the actual action is executed against the true disturbance;
3. the actual action fails or causes immediate loss of viability; and
4. the oracle mode, evaluated counterfactually from a cloned pre-action state under the same true disturbance, does not produce that same failure at that step.

The oracle is used only to create the **future label**. It is prohibited from the time-t observer and all predictor baselines.

The first such event in a trajectory is:

```text
tau_harm = first t with HARMFUL_UNDERPROTECTION_EVENT
```

If no such event occurs before completion or horizon, `tau_harm` is not observed.

## Prediction samples

Predictions are emitted only at an end-of-step observation point where:

```text
completed == False
viable == True
no harmful-underprotection event has yet occurred
```

For each eligible observation at time `t`:

```text
y_t_2 = 1  if tau_harm occurs at t+1 or t+2
        0  otherwise
```

The observer may not use `tau_harm`, future true disturbance, future observed disturbance, future sensor-integrity state, oracle mode, final trajectory class, or any field derived from future labels.

## Lead time

For a trajectory with a harmful event, define:

```text
t_warning = earliest eligible t where WARN == True and t < tau_harm
lead_time = tau_harm - t_warning
```

A warning at the same step as the harmful event receives no early-warning credit.

## Development data

Only already-known / development-visible experiment families may be used to construct the AH-EXP-0013 observer and select thresholds.

Permitted development sources are:

- AH-EXP-0011 trajectory records;
- AH-EXP-0012 development and confirmatory records, treated only as already-observed development evidence for AH-EXP-0013;
- existing AH-EXP-0007 partial-observability mechanisms (`delay_1`, `biased_low`, `noisy_sensor`) and their development-visible schedules/seeds;
- synthetic development-only cases derived from those already-known mechanisms, provided their exact generator is preserved and they are never reported as AH-EXP-0013 confirmatory evidence.

The new AH-EXP-0013 confirmatory profiles defined below may not be executed during observer construction or threshold selection.

## Time-t evidence permitted to the AH-EXP-0013 observer

The EFGM adapter may use only evidence available at or before the current observation point:

### Operational state

- backlog;
- resource;
- work cleared / progress;
- failure count;
- repeated-failure count;
- current and prior **observed** disturbance values;
- observed regulator margin;
- selected mode;
- executed mode;
- action success/failure from completed prior/current actions;
- recovery execution;
- recent finite history of the above.

### Observation-integrity metadata

- measurement age / freshness;
- calibration-confidence metadata;
- provenance completeness / trace coverage;
- whether the current observation was fresh, delayed, reused, or reconstructed;
- declared uncertainty width or confidence associated with the observed disturbance;
- finite history of those metadata fields.

### Explicitly prohibited

The observer may not use:

- current or future true disturbance;
- direct `true_disturbance - observed_disturbance` error;
- oracle mode;
- future sensor profile identity;
- future integrity metadata;
- hidden profile parameters not represented in time-t evidence;
- `tau_harm`;
- final outcome labels.

## EFGM feature family

The implementation must expose a frozen, evidence-backed EFGM mapping before holdout execution.

Primary candidate outputs remain:

```text
DQ
CRC
GI
AE
CUE
Delta_DQ
Delta_CRC
Delta_GI
Delta_AE
Delta_CUE
```

However, unlike AH-EXP-0012, grounding, uncertainty, hidden-information load, and observability must be allowed to vary when the synthetic evidence supports such variation.

The implementation must not fabricate a value merely to make the observer predictive. `unknown` and `not_applicable` remain explicit.

The frozen observer specification must document, at minimum:

- exact operational-to-EFGM mapping;
- exact observation-integrity-metadata-to-EFGM mapping;
- evidence references and automated scorer identity;
- applicability / N/A rules;
- history windows;
- EFGM and Agent Governance configuration hashes;
- normalization method;
- warning-score equation;
- selected threshold;
- baseline thresholds;
- development dataset hash;
- observer implementation SHA.

## Warning-score construction

AH-EXP-0013 may use development data to choose a single transparent EFGM composite rule, but the rule must be frozen before any confirmatory holdout execution.

The primary implementation must remain interpretable. Permitted forms are:

```text
A. unweighted mean of normalized EFGM risk features; or
B. a preregistered deterministic monotonic rule over normalized EFGM outputs.
```

A learned opaque model, neural model, tree ensemble, or post-hoc feature search is outside the primary experiment.

If form B is selected during development, the complete rule and rationale must be committed before holdout execution.

## Baseline family

AH-EXP-0013 deliberately uses stronger baselines than AH-EXP-0012.

Thresholds are selected using development data only and frozen before holdout execution.

Single-variable baselines:

```text
B1  backlog high
B2  resource low
B3  observed regulator margin low
B4  observed disturbance high
B5  calibration confidence low
B6  measurement freshness low
B7  provenance completeness low
B8  recent action-failure rate high
```

A transparent multivariate baseline is also required:

```text
B9  SIMPLE_INTEGRITY_RISK
```

`SIMPLE_INTEGRITY_RISK` is the unweighted arithmetic mean of the normalized raw risk orientations of:

```text
1 - calibration_confidence
1 - freshness
1 - provenance_completeness
declared_uncertainty
```

using only fields available at time `t`.

If a field is legitimately not applicable for a profile, the mean is renormalized over applicable fields. Unknown values may not be replaced by zero.

The **strongest simple baseline** is the development-selected baseline with the highest balanced accuracy among `B1..B9`.

The primary incremental-value comparison is therefore against the strongest of both ordinary operational telemetry and a simple governance-metadata aggregate.

## Threshold selection

For the EFGM warning rule and each baseline:

1. candidate thresholds are distinct development values;
2. choose the threshold maximizing balanced accuracy for `y_t_2`;
3. ties are resolved by higher specificity, then higher precision, then the more conservative warning threshold;
4. all thresholds are frozen in the observer specification before holdout execution.

No confirmatory threshold tuning is permitted.

## New confirmatory true-disturbance family

The true disturbance uses a frozen zero-sum 16-step cycle:

```text
[-0.12, -0.08, -0.04,  0.00,
 +0.04, +0.08, +0.12, +0.08,
 +0.04,  0.00, -0.04, -0.08,
 -0.10, -0.05, +0.05, +0.10]
```

For base level `mu`:

```text
d_t = clip(mu + cycle[t mod 16], 0.0, 1.0)
```

Base grid:

```text
mu = 0.450, 0.455, 0.460, ..., 0.795, 0.800
```

Exactly 71 base values.

Horizon:

```text
100 steps
```

Trajectories terminate earlier on completion, loss of viability, or the first harmful-underprotection event for primary event analysis.

## New confirmatory observation-integrity profiles

Each base `mu` is evaluated under all five frozen profiles below.

Exactly:

```text
71 x 5 = 355 trajectories
```

### P0 — healthy control

```text
observed disturbance = current true disturbance
freshness = 1.0
calibration_confidence = 1.0
provenance_completeness = 1.0
declared_uncertainty = 0.0
```

### P1 — progressive low bias

For step `t`:

```text
bias_t = min(0.24, 0.02 * (t + 1))
observed disturbance = clip(d_t - bias_t, 0.0, 1.0)
freshness = 1.0
calibration_confidence = max(0.0, 1.0 - bias_t / 0.24)
provenance_completeness = 1.0
declared_uncertainty = bias_t
```

### P2 — progressive staleness

Frozen lag cycle:

```text
[0,0,1,1,1,2,2,2,1,1,0,0,1,2,2,1]
```

At step `t` with lag `L_t`:

```text
observed disturbance = d_max(0, t - L_t)
freshness = 1 / (1 + L_t)
calibration_confidence = 1.0
provenance_completeness = 1.0
declared_uncertainty = min(1.0, 0.10 * L_t)
```

### P3 — deterministic sample-and-hold

Frozen freshness cycle:

```text
[FRESH, HOLD, HOLD, FRESH, FRESH, HOLD, FRESH, HOLD,
 FRESH, HOLD, HOLD, FRESH, FRESH, FRESH, HOLD, FRESH]
```

`FRESH` samples `d_t`.

`HOLD` reuses the most recent observed disturbance.

Metadata:

```text
freshness = 1.0 for FRESH
freshness = 0.5 for first consecutive HOLD
freshness = 1/3 for second consecutive HOLD
calibration_confidence = 0.90
provenance_completeness = 0.75 on HOLD, otherwise 1.0
declared_uncertainty = 0.12 on HOLD, otherwise 0.02
```

### P4 — mixed mild degradation

Frozen 16-step lag cycle:

```text
[0,0,0,1,1,0,1,1,0,0,1,0,1,1,0,0]
```

Frozen 16-step bias cycle:

```text
[0.00,0.02,0.04,0.04,0.06,0.08,0.06,0.04,
 0.02,0.00,0.03,0.05,0.07,0.05,0.03,0.01]
```

For each step:

```text
raw = d_max(0, t - L_t)
observed disturbance = clip(raw - bias_t, 0.0, 1.0)
freshness = 1 / (1 + L_t)
calibration_confidence = max(0.0, 1.0 - bias_t / 0.20)
provenance_completeness = 0.85 if L_t > 0 else 0.95
declared_uncertainty = min(1.0, bias_t + 0.08 * L_t)
```

The values, ordering, starting phase, clipping rules, and profile identities are frozen by this preregistration.

The observer may know the current metadata values but may **not** receive the profile name as a feature.

## Primary metrics

Report for the EFGM observer and every baseline:

- TP, FP, TN, FN;
- sensitivity;
- specificity;
- precision;
- balanced accuracy;
- warning-positive rate;
- number of harmful-event trajectories;
- number/fraction receiving at least one pre-event warning;
- lead-time distribution;
- missed harmful events.

Also report profile-stratified results, but those are secondary/descriptive unless they directly determine an inconclusive condition.

## Primary comparison

Let:

```text
BA_EFGM = holdout balanced accuracy of frozen EFGM warning rule
BA_BASE = holdout balanced accuracy of frozen strongest simple baseline
Delta_BA = BA_EFGM - BA_BASE
```

## Primary survival criteria

AH-EXP-0013 **SURVIVES** only if all conditions hold on the pooled confirmatory holdout:

1. at least one positive and one negative `y_t_2` sample exist;
2. `BA_EFGM > 0.50`;
3. `Delta_BA >= 0.02` against the strongest frozen `B1..B9` baseline;
4. at least one harmful-event trajectory receives a warning with `lead_time >= 1`;
5. no future true disturbance, oracle information, profile identity, or future label enters any time-t predictor;
6. EFGM observation provenance and configuration identities are complete under the frozen adapter specification;
7. first-run evidence is preserved before exact rerun;
8. exact rerun reproduces all prediction rows, labels, metrics, lead-time records, canonical result hash, and full-trace hash;
9. no observer mapping, threshold, baseline, profile, label, or survival rule is changed after confirmatory outcomes are observed.

## Falsification criteria

AH-EXP-0013 is **FALSIFIED** if the holdout has adequate positive/negative diversity and any required survival criterion fails.

Explicit falsifying outcomes include:

- `BA_EFGM <= 0.50`;
- `Delta_BA < 0.02`;
- no positive-lead warning;
- a raw sensor-quality baseline or simple integrity aggregate outperforming the EFGM observer such that the incremental criterion fails;
- future-information leakage;
- post-hoc threshold or metric remapping;
- irreproducible deterministic evidence.

A result in which EFGM warns early but a simple metadata score performs better is a valid falsification and must be preserved, exactly as AH-EXP-0012 was preserved.

## Inconclusive conditions

AH-EXP-0013 is **INCONCLUSIVE** rather than falsified if:

- the frozen holdout produces no harmful-underprotection events;
- the holdout produces no negative prediction samples;
- fewer than three EFGM primary outputs can be mapped consistently under the frozen evidence rules;
- the oracle counterfactual cannot be evaluated deterministically from the cloned pre-action state;
- implementation defects invalidate the preregistered event definition before scientific interpretation.

An inconclusive result may motivate a new experiment but may not be repaired by modifying AH-EXP-0013 after outcomes are observed.

## Secondary analyses

Descriptive only:

- performance by profile P0..P4;
- `h = 1` and `h = 3` horizons;
- performance of individual EFGM features;
- performance of individual integrity metadata fields;
- relationship between EFGM risk and observation-integrity degradation;
- eventual queue completion/viability after the first harmful event;
- whether warnings precede visible backlog growth;
- counterfactual difference between actual and oracle resource/progress state;
- calibration plots.

Secondary analyses cannot rescue a failed primary result.

## Required evidence preservation

Before the exact rerun, preserve:

- preregistration SHA;
- frozen AH substrate SHA;
- frozen EFGM code/config hashes;
- observer-spec hash;
- development-data hash;
- EFGM threshold;
- B1..B9 thresholds and selected strongest baseline;
- holdout generator/profile hash;
- every time-t feature payload presented to EFGM;
- every EFGM observation and provenance reference;
- every baseline input;
- future label stored separately from time-t predictor payload where practical;
- oracle-comparator records used only for label generation;
- `tau_harm` and warning lead-time records;
- confusion matrices and performance metrics;
- canonical ordered result hash;
- full-trace hash.

## Claims explicitly not tested

AH-EXP-0013 does not establish:

- real-world AI-agent failure prediction;
- production sensor-fault diagnosis;
- general AI safety or alignment;
- superiority to arbitrary machine-learning predictors;
- causal validity of EFGM outside this synthetic environment;
- that EFGM can infer hidden true state without evidence;
- fractal, Mandelbrot, chaos, or Lyapunov behavior;
- consciousness, biological equivalence, or autonomous self-awareness.

## Interpretation rule

A surviving result permits only the following narrow interpretation:

> In the frozen synthetic artificial-homeostasis system, under the preregistered observation-integrity perturbations, a causal EFGM-derived governance observer contained incremental short-horizon information about harmful control divergence beyond the strongest tested transparent operational/sensor-quality baseline.

A falsified result means the tested EFGM observer did not demonstrate that incremental value under AH-EXP-0013.

Neither result permits post-hoc rewriting.

## Required execution order

```text
1. review this preregistration
2. merge/freeze preregistration SHA
3. build AH-EXP-0013 observation-integrity harness without running confirmatory profiles
4. build EFGM observer using development-visible data only
5. freeze OBSERVER_SPEC, EFGM rule, B1..B9 thresholds, and best baseline
6. structure-only review
7. exact-head CI
8. freeze implementation SHA
9. execute first confirmatory holdout exactly once
10. preserve first-run evidence
11. execute exact reproducibility rerun
12. record SURVIVED / FALSIFIED / INCONCLUSIVE without retuning
```
