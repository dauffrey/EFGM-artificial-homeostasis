# AH-EXP-0013 Frozen Observer Specification

## Status

**OBSERVER, DEVELOPMENT DATA, WARNING RULE, AND BASELINES FROZEN — CONFIRMATORY AH-EXP-0013 HOLDOUT NOT EXECUTED**

This specification follows the merged AH-EXP-0013 preregistration and is built only from development-visible evidence.

## Frozen identities

```text
Preregistration freeze:
c766a3534d9d8ae8d4134b9995b0a22510dd0310

Observer algorithm commit:
b0b9f1f82c0794765991663a2231fe72156bcd82

Observer + structural-test head before this specification:
baba5b025d67861384a6a360438b725f6718cd68

AH operational substrate:
e21d68d1257ef36a3882a5f6362535f701d6350c

EFGM reference code:
37b2ff2d2b577c9f383dd0d7c3083597627150ea

EFGM v2 config:
efgm-v2.0-baseline
0f55f6eabe97d0f365d1e45ba8f9d0fef67e9721a93e6eba8b0a364b612bafd0

Agent Governance config:
efgm-v0.3-agent-governance-candidate-r2
af0b5540f28d4d65ae95929a855a168f9e7c286439d33d33e14ef167d808366c

Adapter/scorer:
ah-exp-0013-integrity-adapter-v1
```

The exact post-review implementation SHA is frozen only after exact-head CI; that SHA is recorded separately and does not alter the observer mapping or thresholds below.

## Controller / event implementation

AH-EXP-0013 uses the frozen `Regulator` controller directly. The actual executed mode is the mode selected from the **observed** disturbance. No AH-EXP-0010 robust-relaxation intervention is invoked in this experiment.

At each step, an oracle comparator uses the same pre-action telemetry but computes its mode from the **true** disturbance. The oracle is used only for future-label construction and is never included in a predictor payload.

Protection order is:

```text
NORMAL < CAUTION < RECOVERY
```

A harmful-underprotection event requires all of the preregistered conditions: the actual mode is less protective than the oracle mode; the actual action fails or immediately loses viability; and the oracle counterfactual does not produce that same failure from the cloned pre-action state.

## Development-data isolation

Only development-visible sources were used:

- the four existing queue schedules;
- stochastic seeds `7, 19, 43, 71, 101, 149, 211, 307`;
- development profiles derived from already-known AH-EXP-0007 mechanisms: `healthy`, `delay_1`, `biased_low`, and `noisy_sensor`.

Development metadata mapping is frozen as:

```text
healthy:
  freshness = 1.00
  calibration = 1.00
  provenance = 1.00
  uncertainty = 0.00

delay_1:
  freshness = 0.50
  calibration = 1.00
  provenance = 1.00
  uncertainty = 0.10

biased_low (-0.20):
  freshness = 1.00
  calibration = 0.40
  provenance = 1.00
  uncertainty = 0.20

noisy_sensor (+/-0.20, frozen seed rule):
  freshness = 1.00
  calibration = 0.60
  provenance = 1.00
  uncertainty = 0.20
```

Development evidence reproduced:

```text
trajectories:              128
prediction rows:           436
positive y_t_2 rows:        65
negative y_t_2 rows:       371
harmful-event trajectories: 42

ordered development rows SHA-256:
3f7dfba41f5a50a88d6550064d1ae2c8eaa960f092e0e5a039e6f9078aedf611
```

No P0..P4 AH-EXP-0013 confirmatory trajectory was executed to select these values.

## Time-t causal evidence boundary

The observer receives only current/past operational evidence and current/past observation-integrity metadata. Predictor rows do not contain:

- true disturbance;
- direct true-minus-observed error;
- oracle mode or oracle outcome;
- future integrity state;
- `tau_harm`;
- final trajectory outcome;
- confirmatory profile identity.

Confirmatory trajectory IDs are opaque (`holdout-NNN`) so profile identity is not encoded in predictor/provenance identifiers.

## EFGM v2 synthetic mapping

History window:

```text
3 realized observations, including the current completed action
```

### Capability and flow

```text
T = clip((t + 1) / 4, 0, 1)
margin_fit = clip((observed_margin + 0.35) / 1.0, 0, 1)
C = mean(resource, margin_fit)
```

Flow-quality observations use recent action success and inverse controller-mode switching. Unmapped linguistic semantic-coherence dimensions are not fabricated.

### Input entropy

Mapped observations:

```text
observed variability
1 - freshness
hidden_information_load
```

with:

```text
hidden_information_load = mean(
    1 - calibration_confidence,
    1 - freshness,
    declared_uncertainty
)
```

### Output / operational entropy

Mapped observations use recent action-failure rate, mode switching, positive backlog growth, repeated failures, backlog pressure, and recovery-only interruption.

### Grounding and uncertainty

Grounding is no longer fixed at 1.0. The canonical grounding-family weights are applied to:

```text
rule_support        = 1.0
evidence_validity   = calibration_confidence
traceability        = provenance_completeness
factual_consistency = calibration_confidence
domain_calibration  = 1.0
```

Current uncertainty calibration is:

```text
U = mean(
    calibration_confidence,
    1 - declared_uncertainty,
    freshness
)
```

Canonical synthetic outputs remain:

```text
CRC = (Ei - Eo) / max(Ei, 0.01)
Q   = (T * C * Fq * G * U)^(1/5)
DQ  = Q / (1 + Eo + Be + Oe)
```

## Agent Governance v0.3 synthetic mapping

Coordination remains not applicable because the experiment is single-controller.

```text
alignment = 1.0

boundary_integrity = mean(
    margin_fit,
    calibration_confidence,
    provenance_completeness
)

observability = mean(
    freshness,
    provenance_completeness
)

environmental_memory_governance = mean(
    backlog_slack,
    provenance_completeness,
    freshness
)

control_recoverability = mean(
    backlog_slack,
    resource,
    calibration_confidence
)

GI = geometric_mean(
    alignment,
    boundary_integrity,
    observability,
    environmental_memory_governance,
    control_recoverability
)
```

Agency amplification is frozen as:

```text
NORMAL   = 1.0
CAUTION  = 0.6
RECOVERY = 0.2
```

and:

```text
AE  = agency_amplification * (1 - GI)
CUE = DQ * AE
```

Temporal deltas are retained for evidence/reporting but are not used in the primary frozen warning score.

## Frozen EFGM warning rule

Development-visible diagnostics showed that including the broader DQ/CRC temporal risk family reproduced the over-warning tendency seen in AH-EXP-0012. For the new governance-specific event, the permitted transparent monotonic Form B was selected before confirmatory execution:

```text
EFGM_RISK = mean(
    1 - GI,
    AE,
    CUE
)
```

This is not a retuning of AH-EXP-0012; it is the separately preregistered AH-EXP-0013 observer chosen on development evidence for the distinct observation-integrity event.

Frozen warning threshold:

```text
EFGM_RISK >= 0.133389161231 => WARN
```

Development-only performance:

```text
balanced accuracy = 0.7744972009122952
sensitivity       = 0.7538461538461538
specificity       = 0.7951482479784366
precision         = 0.392
```

These numbers are not confirmatory AH-EXP-0013 evidence.

## Frozen B1..B9 baselines

```text
B1 backlog high:               backlog >= 4.0
B2 resource low:               resource <= 0.913889707027
B3 observed margin low:        margin <= -0.325538685979
B4 observed disturbance high:  observed_disturbance >= 1.0
B5 calibration low:            calibration <= 0.4
B6 freshness low:              freshness <= 0.5
B7 provenance low:             provenance <= 1.0
B8 recent failures high:       failure_rate >= 1.0
B9 simple integrity risk high: SIMPLE_INTEGRITY_RISK >= 0.15
```

`SIMPLE_INTEGRITY_RISK` is exactly:

```text
mean(
    1 - calibration_confidence,
    1 - freshness,
    1 - provenance_completeness,
    declared_uncertainty
)
```

Development-selected strongest simple baseline:

```text
B9_simple_integrity
```

Development-only B9 balanced accuracy:

```text
0.6981132075471699
```

The confirmatory comparison is frozen against B9 even if another baseline happens to score better on the unseen holdout; all B1..B9 holdout metrics will still be reported descriptively.

## Confirmatory design freeze

The confirmatory generator/profile manifest is represented without executing trajectories.

```text
trajectory count: 355
base grid: 0.450 .. 0.800 by 0.005
profiles: P0, P1, P2, P3, P4
horizon: 100
prediction horizon: 2

holdout design SHA-256:
c318557fd646a72a2253bba2027746a0a2471c31b29eb867318bc9c1ff7824b5
```

The profile values are exactly those in `PREREGISTRATION.md` and in the frozen implementation constants.

## Freeze rule

After structure-only review and exact-head CI, the exact implementation SHA is frozen. No observer mapping, development generator, EFGM rule, threshold, B1..B9 threshold, best-baseline identity, confirmatory profile, event definition, prediction horizon, or survival criterion may change after the first confirmatory outcome is observed.
