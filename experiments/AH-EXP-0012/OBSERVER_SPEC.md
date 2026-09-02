# AH-EXP-0012 Frozen Observer Specification

## Status

**OBSERVER / THRESHOLDS FROZEN FROM AH-EXP-0011 DEVELOPMENT DATA ONLY — AH-EXP-0012 HOLDOUT NOT EXECUTED**

Preregistration freeze:

```text
4c01e559548341e16310981ade06871f63685d00
```

Frozen AH operational substrate:

```text
e21d68d1257ef36a3882a5f6362535f701d6350c
```

EFGM reference implementation:

```text
repository: dauffrey/efgm
code SHA:   37b2ff2d2b577c9f383dd0d7c3083597627150ea
```

EFGM configuration identities:

```text
EFGM v2 config: efgm-v2.0-baseline
canonical config SHA-256: 0f55f6eabe97d0f365d1e45ba8f9d0fef67e9721a93e6eba8b0a364b612bafd0

Agent Governance config: efgm-v0.3-agent-governance-candidate-r2
canonical config SHA-256: af0b5540f28d4d65ae95929a855a168f9e7c286439d33d33e14ef167d808366c
```

Adapter identity:

```text
ah-exp-0012-efgm-adapter-v1
```

## Development-data isolation

Only the already-observed AH-EXP-0011 primary-controller trajectories were used to construct this adapter and select thresholds.

The canonical ordered development rows hash is:

```text
e5c5a73db69cc2db6fc9d6661f6af6cc6dab7c50c57258d86b0634f5402f3044
```

The new AH-EXP-0012 20-step disturbance family was not executed during adapter construction or threshold selection.

## Observation timing

The adapter executes only after action completion at a step where:

```text
completed == False
viable == True
```

No future disturbance, future state, final trajectory class, escape time, future recovery action, future completion state, or future failure mechanism is available to the adapter.

History is limited to the current step and previous two realized steps.

## EFGM v2 mapping

The adapter follows the frozen EFGM v2 aggregation equations but maps the synthetic queue state to research observations as follows.

### T — observation maturity

```text
T = clip((t + 1) / 4, 0, 1)
```

### C — capability suitability

```text
margin_fit = clip((margin + 0.35) / 1.0, 0, 1)
C = mean(resource, margin_fit)
```

### Flow quality

Applied observations:

- `task_completion_consistency` = recent service-action success rate;
- `reasoning_continuity` = 1 minus recent controller-mode switching rate;
- `verification_success_rate` = recent realized service-action success rate.

`semantic_coherence` is not mapped because the synthetic controller does not produce linguistic semantics. Applicable EFGM v2 weights are renormalized exactly as in the canonical scorer.

### Input entropy

Applied observations:

- `input_ambiguity` = scaled finite-window realized-disturbance variability;
- `missing_context` = scaled change from the previous realized disturbance; this is a synthetic load-change proxy and does not use future disturbance;
- `hidden_information_load` = 0 because all permitted current simulator channels are visible to the adapter.

Unmapped cognitive-input dimensions are treated as not applicable for this synthetic bridge.

### Output entropy

Applied observations:

- `uncertainty_mismatch` = recent realized action-failure rate;
- `reasoning_instability` = recent controller-mode switching rate;
- `context_decay` = positive backlog-growth proxy.

### Grounding and uncertainty calibration

The simulator is deterministic and every mapped observation is traceable to the step record. The applicable grounding observations and current-state uncertainty calibration are therefore fixed at 1.0. This does not imply real-world perfect grounding; it describes this frozen synthetic environment only.

### Behavioral entropy

The behavioral-entropy family is not applicable to this queue controller and contributes the canonical all-N/A value of zero.

### Operational entropy

Applied observations:

- `retry_instability` = normalized accumulated repeated failures;
- `tool_failure_rate` = recent action-failure rate;
- `latency_pressure` = backlog / frozen maximum backlog;
- `workflow_interruption` = recent fraction of recovery-only actions.

### Canonical outputs

Using the frozen v2 equations:

```text
CRC = (Ei - Eo) / max(Ei, 0.01)
Q   = (T * C * Fq * G * U)^(1/5)
DQ  = Q / (1 + Eo + Be + Oe)
```

## Agent Governance v0.3 mapping

The adapter uses the candidate's frozen family aggregation semantics.

Applied family proxies:

```text
alignment = 1.0
boundary_integrity = min(margin_fit, backlog_slack)
observability = 1.0
environmental_memory_governance = mean(backlog_slack, 1.0)
control_recoverability = mean(backlog_slack, backlog_slack, resource)
```

Coordination governance is entirely `not_applicable` because the environment is strictly single-agent; it is excluded from GI as permitted by Agent Governance v0.3.

The action-velocity agency-amplification proxy is frozen as:

```text
NORMAL   = 1.0
CAUTION  = 0.6
RECOVERY = 0.2
```

The candidate equations are then:

```text
GI  = geometric_mean(applicable governance family scores)
AE  = agency_amplification * (1 - GI)
CUE = DQ * AE
```

## Temporal features

For consecutive viable observations in the same trajectory:

```text
Delta_DQ  = DQ_t  - DQ_(t-1)
Delta_CRC = CRC_t - CRC_(t-1)
Delta_GI  = GI_t  - GI_(t-1)
Delta_AE  = AE_t  - AE_(t-1)
Delta_CUE = CUE_t - CUE_(t-1)
```

Deltas are unavailable for the first viable observation and are omitted from that observation's risk mean.

## Risk-percentile normalization

The empirical development distribution for each applicable primary feature is regenerated from the frozen AH-EXP-0011 implementation and must reproduce the frozen development-row hash before any holdout scoring can proceed.

Risk directions are exactly those in the preregistration. The AH-EXP-0012 risk score is the unweighted arithmetic mean of available empirical risk percentiles. At least three features are required.

## Frozen warning threshold

Selected once from AH-EXP-0011 development data by maximum balanced accuracy with the preregistered tie-break procedure:

```text
EFGM_RISK >= 0.582818749642 => WARN
```

Development-only diagnostic performance at this threshold:

```text
TP = 109
FN = 11
TN = 457
FP = 254
balanced accuracy = 0.7755450070
```

This development result is not confirmatory AH-EXP-0012 evidence.

## Frozen operational baselines

Development-only threshold selection produced:

```text
B1 backlog high:        backlog >= 9
B2 resource low:        resource <= 0.878775
B3 regulator margin low: margin <= 0.235
B4 disturbance high:    disturbance >= 0.745
```

The frozen best single-variable development baseline is:

```text
B1 — backlog high
```

Development balanced accuracy for B1 was approximately `0.9489275668`. This is intentionally preserved even though it substantially exceeds the EFGM observer on development data. The confirmatory holdout must not be altered or abandoned to protect the EFGM hypothesis from this unfavorable development diagnostic.

## Holdout generator

The holdout cycle remains exactly as preregistered:

```text
[-0.15, -0.09, -0.03, +0.03, +0.09,
 +0.15, +0.09, +0.03, -0.03, -0.09,
 -0.12, -0.06,  0.00, +0.06, +0.12,
 +0.06,  0.00, -0.06,  0.00,  0.00]
```

The implementation defines the holdout execution API but normal CI and structural tests must not call it.

## Freeze rule

After this observer implementation passes review and exact-head CI, its exact commit SHA must be frozen. No mapping, normalization, threshold, baseline, holdout cycle, horizon, label, or survival criterion may change after the first holdout outcome is observed.
