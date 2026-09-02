# AH-EXP-0011 Preregistration

## Title

Trajectory boundary and escape-time mapping: can stable, recovery-dependent, and failed operating regions be measured reproducibly?

## Status

**PREREGISTERED — VALIDATION OUTCOMES FOR THE FROZEN AH-EXP-0011 SWEEP HAVE NOT BEEN OBSERVED**

A prior exploratory analysis performed before this preregistration examined constant-disturbance trajectories using the existing controller/environment and revealed non-monotonic operating regions. Because those outcomes were already observed, a constant-disturbance sweep is **not** eligible as confirmatory AH-EXP-0011 evidence.

AH-EXP-0011 therefore uses a new, frozen, deterministic **modulated-disturbance sweep** whose outcomes must remain unobserved until implementation fidelity checks and exact-head CI are green. The prior exploratory result is motivation only and must not be counted as AH-EXP-0011 evidence.

AH-EXP-0011 does not modify, retune, or reinterpret AH-EXP-0010.

## Research question

Can the frozen artificial-homeostasis system produce reproducible, objectively measurable boundaries between:

1. stable completion;
2. recovery-dependent completion; and
3. loss of viability;

and, when viability is lost, can the first escape time be measured unambiguously?

In plain language: **does the agent have measurable operating boundaries, and can we determine how long a failing trajectory remains viable before it escapes?**

## Primary hypothesis

Across a preregistered deterministic disturbance sweep, the frozen controller/environment will produce at least two distinct trajectory classes and all non-censored trajectories will be classifiable by fixed rules. Every failed trajectory will have a unique first loss-of-viability step, and exact reruns will reproduce the same classifications, boundary intervals, and escape times.

The experiment does **not** require the classes to appear in monotonic order as disturbance increases.

## Frozen controllers

### Primary controller

The primary controller is the frozen AH-EXP-0010 robust-counterfactual-abstention controller.

Its existing mechanism remains unchanged, including:

- the coupled-margin regulator;
- the AH-EXP-0009 trajectory gates;
- robust disturbance views at `d - 0.08`, `d`, and `d + 0.08` with clipping to `[0, 1]`;
- `robust_CF = min(CF(d_low), CF(d_mid), CF(d_high))`;
- relaxation threshold `0.50`;
- at most one protective action changed to `NORMAL` per intervention;
- ordinary regulator control resuming at the next decision.

No AH-EXP-0011 threshold search, controller retuning, new recovery policy, adaptive learning rule, or altered counterfactual coefficient is permitted.

### Frozen comparison controller

The comparison controller is the existing coupled-margin `Regulator` without robust counterfactual relaxation.

The comparison is secondary. AH-EXP-0011 is primarily a measurement experiment, not a controller-improvement experiment.

## Frozen environment

Use the existing bounded queue/service environment and its current viability definition without alteration.

Existing state includes at minimum:

- `backlog`;
- `work_cleared`;
- `resource`;
- `failures`;
- `repeated_failures`;
- `recoveries`;
- `min_margin`;
- operating-mode counts.

Existing viability remains:

```text
resource > 0.0 AND backlog <= MAX_BACKLOG
```

Existing task completion remains the current queue-environment completion criterion.

No queue thresholds, service thresholds, recovery gains, costs, backlog limits, target work, or utility definitions may be changed for AH-EXP-0011 after validation outcomes are observed.

## New validation disturbance family

### Control parameter

Let `mu` denote the base disturbance level.

Evaluate:

```text
mu = 0.000, 0.005, 0.010, ..., 0.995, 1.000
```

This creates exactly **201 base-disturbance values** per controller.

### Frozen modulation cycle

For each `mu`, use the following 12-step zero-mean deterministic modulation cycle:

```text
[-0.12, -0.08, -0.04, 0.00, +0.04, +0.08,
 +0.12, +0.08, +0.04, 0.00, -0.04, -0.08]
```

At step `t`, define:

```text
d_t = clip(mu + modulation[t mod 12], 0.0, 1.0)
```

The modulation values, ordering, amplitude, cycle length, clipping rule, and starting phase are frozen by this preregistration.

They may not be changed after any AH-EXP-0011 validation outcomes are observed.

### Horizon

Maximum trajectory horizon:

```text
100 steps
```

A trajectory terminates earlier if it completes or loses viability.

A trajectory that remains viable but incomplete at step 100 is **CENSORED**, not automatically classified as stable or failed.

## Required step-level instrumentation

For every trajectory, record at least:

- controller identity;
- `mu`;
- step index `t`;
- realized disturbance `d_t`;
- resource before and after the step;
- backlog before arrival, after arrival, and after action when applicable;
- work cleared before and after the step;
- failure count;
- repeated-failure count;
- regulator margin;
- selected mode;
- executed mode;
- whether an AH-EXP-0010 relaxation intervention occurred;
- action success/failure where an action is executed;
- completion state;
- viability state;
- event phase if viability is first lost.

The instrumentation must distinguish at minimum:

```text
post_arrival
post_action
```

for the first event that causes loss of viability.

This is required so escape time cannot be made ambiguous by a backlog overflow that occurs before the controller acts.

## Frozen trajectory classifications

### STABLE

A trajectory is `STABLE` when:

```text
completed == True
viable == True
executed RECOVERY actions == 0
```

`CAUTION` actions are permitted in `STABLE` trajectories.

A protective mode that was selected but relaxed before execution does not count as an executed recovery action.

### RECOVERED

A trajectory is `RECOVERED` when:

```text
completed == True
viable == True
executed RECOVERY actions >= 1
```

This classification means active resource-restoration behavior was actually executed and the trajectory later completed while remaining viable.

### FAILED

A trajectory is `FAILED` when viability becomes false before task completion under the frozen environment definition.

The failure mechanism must also be recorded, including whether first loss of viability resulted from:

- resource depletion;
- backlog exceeding `MAX_BACKLOG`;
- or both on the same step.

### CENSORED

A trajectory is `CENSORED` when all of the following hold at the end of the 100-step horizon:

```text
completed == False
viable == True
```

Censored trajectories are reported explicitly and are not silently reassigned to another class.

## Escape time

For every `FAILED` trajectory define:

```text
tau_escape = first step index t at which viability becomes False
```

Also record:

```text
escape_phase = post_arrival | post_action
```

and the first state values that make viability false.

For trajectories that never lose viability, `tau_escape` is **not observed** and must remain null/NA. It must not be assigned the horizon value `100`.

## Recovery timing — secondary measure

For `RECOVERED` trajectories record:

```text
t_first_recovery = first step at which RECOVERY is actually executed
```

and:

```text
t_first_productive_after_recovery
```

where the latter is the first subsequent non-RECOVERY action that successfully clears at least one unit of work.

A secondary recovery-latency measure may then be reported as:

```text
tau_recovery = t_first_productive_after_recovery - t_first_recovery
```

This is descriptive only and is not a primary survival criterion for AH-EXP-0011.

## Boundary definition

AH-EXP-0011 does **not** assume a single monotonic transition such as:

```text
STABLE -> RECOVERED -> FAILED
```

For the ordered `mu` grid, define a measured class boundary wherever two adjacent values differ in classification:

```text
class(mu_i) != class(mu_(i+1))
```

Each boundary is reported as the interval:

```text
[mu_i, mu_(i+1)]
```

The nominal boundary resolution is therefore `0.005`.

No interpolation may claim a more precise boundary location unless a separate future experiment preregisters a refinement procedure before observing refinement outcomes.

Multiple disconnected regions and repeated class transitions are valid outcomes and must be preserved rather than smoothed away.

## Primary outputs

For each controller produce:

1. a complete trajectory-classification table over all 201 `mu` values;
2. the ordered list of measured boundary intervals;
3. `tau_escape(mu)` for every failed trajectory;
4. the failure mechanism and escape phase for every failed trajectory;
5. counts of `STABLE`, `RECOVERED`, `FAILED`, and `CENSORED` trajectories;
6. an exact reproducibility digest/hash over the ordered canonical result payload.

The primary visualization should show the classification strip across increasing `mu`, followed by escape time as a function of `mu` for failed trajectories.

## Reproducibility check

After the first canonical validation execution completes, rerun the exact frozen experiment without code or parameter changes.

The rerun must reproduce exactly:

- all 201 classifications for each controller;
- all boundary intervals;
- all finite `tau_escape` values;
- all escape phases;
- the canonical ordered result hash.

The reproducibility rerun is not an independent statistical holdout; it tests deterministic repeatability only.

## Primary survival criteria

AH-EXP-0011 **SURVIVES** its primary measurement hypothesis only if all of the following are true for the primary AH-EXP-0010 controller:

1. at least two distinct trajectory classes among `STABLE`, `RECOVERED`, and `FAILED` are observed across the 201-value sweep;
2. every non-censored trajectory is classifiable using only the preregistered rules;
3. every failed trajectory has one unambiguous finite `tau_escape` and one recorded escape phase;
4. at least one adjacent-class boundary interval is measurable on the frozen `mu` grid;
5. the exact reproducibility rerun produces identical classifications, boundary intervals, escape times, escape phases, and canonical result hash;
6. no controller parameter, environment parameter, disturbance pattern, horizon, class definition, boundary rule, or escape-time definition is changed after validation outcomes are observed.

## Preregistered falsification / weakening criteria

AH-EXP-0011 is **FALSIFIED or materially weakened** if any of the following occurs:

1. all 201 primary-controller trajectories fall into the same `STABLE`, `RECOVERED`, or `FAILED` class;
2. loss of viability occurs but the implementation cannot identify a unique first escape step and phase;
3. any non-censored trajectory requires post-outcome reinterpretation to assign a class;
4. exact reruns of identical deterministic inputs produce different classifications, boundaries, escape times, escape phases, or result hashes without a preregistered stochastic source;
5. boundary locations are reported with precision finer than the frozen `0.005` grid without a separately preregistered refinement study;
6. censored cases are silently reassigned to `STABLE`, `RECOVERED`, or `FAILED`;
7. the disturbance cycle, grid, horizon, classification rules, controller parameters, environment parameters, or outcome definitions are modified after validation outcomes are observed in order to create cleaner or more favorable boundaries;
8. the previously observed exploratory constant-disturbance sweep is presented as confirmatory AH-EXP-0011 evidence.

A high number of censored trajectories does not automatically falsify AH-EXP-0011, but it weakens the claim that the selected horizon exposes a useful stable/recovery/failure boundary and must be reported as such.

## Secondary comparison

Run the same frozen 201-value modulated sweep on the coupled-margin regulator without AH-EXP-0010 relaxation.

Compare descriptively:

- class counts;
- boundary intervals;
- escape-time distributions;
- failure mechanisms;
- censored counts.

No preregistered claim requires the AH-EXP-0010 controller to outperform the comparison controller in AH-EXP-0011. The comparison exists to determine whether the measurement framework is informative across more than one frozen control policy.

## Claims explicitly not tested

AH-EXP-0011 does not test or establish:

- whether EFGM metrics predict an approaching boundary;
- whether `GI`, `AE`, `CUE`, `CRC`, or `DQ` provide early warning;
- fractal geometry;
- Mandelbrot-like dynamics;
- chaos or positive Lyapunov exponents;
- a universal law of AI-agent stability;
- biological equivalence to homeostasis;
- consciousness or subjective awareness;
- safety or alignment of real autonomous LLM agents;
- production readiness;
- optimality of the AH-EXP-0010 regulator.

Those require separate experiments.

## Interpretation rule

AH-EXP-0011 is a **measurement experiment**.

A successful result means only that, in the frozen synthetic system and previously unobserved modulated-disturbance sweep, stable/recovery/failure operating regions and escape times can be defined and reproduced objectively.

It does not mean the measured boundaries generalize to other environments or real AI agents.

If AH-EXP-0011 survives, a later separately preregistered experiment may test whether EFGM observations contain predictive information before `tau_escape`, for example whether governance or entropy-related measurements provide lead time before a trajectory crosses its viability boundary.
