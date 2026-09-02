from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any, Iterable, Sequence

from .adversarial_robustness import EnvironmentConfig, _arrival, _maintenance, _service
from .core import Mode, Regulator
from .queue_replication import MAX_BACKLOG, QueueTelemetry, SCHEDULES
from .stochastic_replication import SEEDS, stochastic_schedule


EXPERIMENT_ID = "AH-EXP-0013"
PREREGISTRATION_FREEZE_SHA = "c766a3534d9d8ae8d4134b9995b0a22510dd0310"
AH_SUBSTRATE_SHA = "e21d68d1257ef36a3882a5f6362535f701d6350c"
EFGM_CODE_SHA = "37b2ff2d2b577c9f383dd0d7c3083597627150ea"
EFGM_V2_CONFIG_ID = "efgm-v2.0-baseline"
EFGM_V2_CONFIG_SHA256 = "0f55f6eabe97d0f365d1e45ba8f9d0fef67e9721a93e6eba8b0a364b612bafd0"
AGENT_CONFIG_ID = "efgm-v0.3-agent-governance-candidate-r2"
AGENT_CONFIG_SHA256 = "af0b5540f28d4d65ae95929a855a168f9e7c286439d33d33e14ef167d808366c"
ADAPTER_ID = "ah-exp-0013-integrity-adapter-v1"
SCORER_ID = "ah-exp-0013-integrity-adapter-v1"

HORIZON = 100
HISTORY_WINDOW = 3
PREDICTION_HORIZON = 2

CONFIRMATORY_CYCLE = (
    -0.12, -0.08, -0.04, 0.00,
     0.04,  0.08,  0.12, 0.08,
     0.04,  0.00, -0.04, -0.08,
    -0.10, -0.05,  0.05, 0.10,
)
STALE_LAG_CYCLE = (0, 0, 1, 1, 1, 2, 2, 2, 1, 1, 0, 0, 1, 2, 2, 1)
SAMPLE_HOLD_CYCLE = (
    "FRESH", "HOLD", "HOLD", "FRESH",
    "FRESH", "HOLD", "FRESH", "HOLD",
    "FRESH", "HOLD", "HOLD", "FRESH",
    "FRESH", "FRESH", "HOLD", "FRESH",
)
MIXED_LAG_CYCLE = (0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0)
MIXED_BIAS_CYCLE = (
    0.00, 0.02, 0.04, 0.04,
    0.06, 0.08, 0.06, 0.04,
    0.02, 0.00, 0.03, 0.05,
    0.07, 0.05, 0.03, 0.01,
)
CONFIRMATORY_PROFILES = ("P0", "P1", "P2", "P3", "P4")
DEVELOPMENT_PROFILES = ("healthy", "delay_1", "biased_low", "noisy_sensor")

PRIMARY_FEATURES = (
    "DQ", "CRC", "GI", "AE", "CUE",
    "Delta_DQ", "Delta_CRC", "Delta_GI", "Delta_AE", "Delta_CUE",
)

# Frozen from development-visible data only. The implementation verifies these
# constants by regenerating the permitted AH-EXP-0013 development set.
EFGM_WARNING_THRESHOLD = 0.133389161231
BASELINE_THRESHOLDS = {
    "B1_backlog": 4.0,
    "B2_resource": 0.913889707027,
    "B3_margin": -0.325538685979,
    "B4_observed_disturbance": 1.0,
    "B5_calibration": 0.4,
    "B6_freshness": 0.5,
    "B7_provenance": 1.0,
    "B8_failure_rate": 1.0,
    "B9_simple_integrity": 0.15,
}
BEST_BASELINE = "B9_simple_integrity"
DEVELOPMENT_ROWS_SHA256 = "3f7dfba41f5a50a88d6550064d1ae2c8eaa960f092e0e5a039e6f9078aedf611"

PROTECTION_ORDER = {
    Mode.NORMAL: 0,
    Mode.CAUTION: 1,
    Mode.RECOVERY: 2,
}
BASELINE_ORIENTATION = {
    "B1_backlog": "high",
    "B2_resource": "low",
    "B3_margin": "low",
    "B4_observed_disturbance": "high",
    "B5_calibration": "low",
    "B6_freshness": "low",
    "B7_provenance": "low",
    "B8_failure_rate": "high",
    "B9_simple_integrity": "high",
}


@dataclass(frozen=True)
class IntegrityMetadata:
    freshness: float
    calibration_confidence: float
    provenance_completeness: float
    declared_uncertainty: float
    source_state: str


@dataclass
class ObservationState:
    last_observed: float | None = None
    hold_streak: int = 0


@dataclass(frozen=True)
class HarmRecord:
    t: int
    true_disturbance: float
    observed_disturbance: float
    actual_mode: str
    oracle_mode: str
    actual_failed: bool
    oracle_failed: bool
    actual_viable_after: bool
    oracle_viable_after: bool


@dataclass
class TrajectoryEvidence:
    trajectory_id: str
    profile: str
    mu: float | None
    seed: int | None
    schedule_name: str | None
    tau_harm: int | None
    prediction_rows: list[dict[str, Any]]
    full_trace: list[dict[str, Any]]
    harm_record: HarmRecord | None
    terminal_completed: bool
    terminal_viable: bool


def _norm(value: float) -> float:
    return round(float(value), 12)


def _clip(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _mean(values: Iterable[float]) -> float:
    data = list(values)
    return sum(data) / len(data) if data else 0.0


def _weighted(values: Iterable[tuple[float, float]]) -> float:
    data = list(values)
    total = sum(weight for _, weight in data)
    if total <= 0:
        raise ValueError("weights must sum to a positive value")
    return sum(value * weight for value, weight in data) / total


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _clone_telemetry(value: QueueTelemetry) -> QueueTelemetry:
    return copy.deepcopy(value)


def _apply_mode(
    telemetry: QueueTelemetry,
    mode: Mode,
    true_disturbance: float,
    step: int,
) -> tuple[bool, bool]:
    """Apply one mode and return (harm-like failure, action_failed).

    A RECOVERY action is maintenance and is not defined as an action failure.
    For a service action, a failed attempt is an action failure. Any immediate
    viability loss after the action also counts for event construction.
    """
    was_viable = telemetry.viable
    action_failed = False
    config = EnvironmentConfig()
    if mode is Mode.RECOVERY:
        _maintenance(telemetry, true_disturbance, config)
    else:
        failures_before = telemetry.failures
        _service(
            telemetry,
            true_disturbance,
            cautious=(mode is Mode.CAUTION),
            step=step,
            config=config,
        )
        action_failed = telemetry.failures > failures_before
    return action_failed or (was_viable and not telemetry.viable), action_failed


def confirmatory_mu_grid() -> tuple[float, ...]:
    return tuple(round(0.450 + 0.005 * index, 3) for index in range(71))


def confirmatory_true_schedule(mu: float) -> tuple[float, ...]:
    if mu not in confirmatory_mu_grid():
        raise ValueError("mu must be one of the 71 frozen confirmatory grid values")
    return tuple(
        _norm(_clip(mu + CONFIRMATORY_CYCLE[t % len(CONFIRMATORY_CYCLE)]))
        for t in range(HORIZON)
    )


def holdout_design_manifest() -> dict[str, Any]:
    """Return the confirmatory design identity without executing trajectories."""
    return {
        "experiment": EXPERIMENT_ID,
        "preregistration_freeze_sha": PREREGISTRATION_FREEZE_SHA,
        "horizon": HORIZON,
        "prediction_horizon": PREDICTION_HORIZON,
        "mu_grid": [f"{value:.3f}" for value in confirmatory_mu_grid()],
        "true_cycle": list(CONFIRMATORY_CYCLE),
        "profiles": {
            "P0": {"kind": "healthy"},
            "P1": {"kind": "progressive_low_bias", "max_bias": 0.24, "bias_step": 0.02},
            "P2": {"kind": "progressive_staleness", "lag_cycle": list(STALE_LAG_CYCLE)},
            "P3": {"kind": "sample_and_hold", "cycle": list(SAMPLE_HOLD_CYCLE)},
            "P4": {
                "kind": "mixed_mild_degradation",
                "lag_cycle": list(MIXED_LAG_CYCLE),
                "bias_cycle": list(MIXED_BIAS_CYCLE),
            },
        },
        "trajectory_count": 355,
        "confirmatory_outcomes_observed": False,
    }


def holdout_design_hash() -> str:
    return _canonical_hash(holdout_design_manifest())


def _development_observation(
    profile: str,
    true_schedule: Sequence[float],
    t: int,
    seed: int,
) -> tuple[float, IntegrityMetadata]:
    """Development-visible observation mechanisms derived from AH-EXP-0007."""
    true_value = true_schedule[t]
    if profile == "healthy":
        return _norm(true_value), IntegrityMetadata(1.0, 1.0, 1.0, 0.0, "fresh")
    if profile == "delay_1":
        observed = 0.0 if t == 0 else true_schedule[t - 1]
        return _norm(observed), IntegrityMetadata(0.5, 1.0, 1.0, 0.10, "delayed")
    if profile == "biased_low":
        observed = max(0.0, true_value - 0.20)
        return _norm(observed), IntegrityMetadata(1.0, 0.40, 1.0, 0.20, "fresh")
    if profile == "noisy_sensor":
        rng = random.Random(10000 + seed)
        noise = 0.0
        for _ in range(t + 1):
            noise = rng.uniform(-0.20, 0.20)
        observed = _clip(true_value + noise)
        return _norm(observed), IntegrityMetadata(1.0, 0.60, 1.0, 0.20, "fresh")
    raise ValueError(f"unknown development profile: {profile}")


def _confirmatory_observation(
    profile: str,
    true_schedule: Sequence[float],
    t: int,
    state: ObservationState,
) -> tuple[float, IntegrityMetadata]:
    """Generate one frozen AH-EXP-0013 confirmatory observation.

    Calling this function does not itself execute a trajectory, but the
    confirmatory profiles must not be passed to the trajectory engine during
    observer construction.
    """
    true_value = true_schedule[t]
    if profile == "P0":
        observed = true_value
        metadata = IntegrityMetadata(1.0, 1.0, 1.0, 0.0, "fresh")
        state.hold_streak = 0
    elif profile == "P1":
        bias = min(0.24, 0.02 * (t + 1))
        observed = _clip(true_value - bias)
        metadata = IntegrityMetadata(
            1.0,
            _clip(1.0 - bias / 0.24),
            1.0,
            _clip(bias),
            "fresh",
        )
        state.hold_streak = 0
    elif profile == "P2":
        lag = STALE_LAG_CYCLE[t % len(STALE_LAG_CYCLE)]
        source_index = max(0, t - lag)
        observed = true_schedule[source_index]
        metadata = IntegrityMetadata(
            1.0 / (1.0 + lag),
            1.0,
            1.0,
            min(1.0, 0.10 * lag),
            "fresh" if lag == 0 else "delayed",
        )
        state.hold_streak = 0
    elif profile == "P3":
        phase = SAMPLE_HOLD_CYCLE[t % len(SAMPLE_HOLD_CYCLE)]
        if phase == "FRESH" or state.last_observed is None:
            observed = true_value
            state.hold_streak = 0
            metadata = IntegrityMetadata(1.0, 0.90, 1.0, 0.02, "fresh")
        else:
            observed = state.last_observed
            state.hold_streak += 1
            freshness = 0.5 if state.hold_streak == 1 else (1.0 / 3.0)
            metadata = IntegrityMetadata(
                freshness,
                0.90,
                0.75,
                0.12,
                "reused",
            )
    elif profile == "P4":
        lag = MIXED_LAG_CYCLE[t % len(MIXED_LAG_CYCLE)]
        bias = MIXED_BIAS_CYCLE[t % len(MIXED_BIAS_CYCLE)]
        source_index = max(0, t - lag)
        raw = true_schedule[source_index]
        observed = _clip(raw - bias)
        metadata = IntegrityMetadata(
            1.0 / (1.0 + lag),
            _clip(1.0 - bias / 0.20),
            0.85 if lag > 0 else 0.95,
            min(1.0, bias + 0.08 * lag),
            "fresh" if lag == 0 else "reconstructed",
        )
        state.hold_streak = 0
    else:
        raise ValueError(f"unknown confirmatory profile: {profile}")

    state.last_observed = _norm(observed)
    return _norm(observed), metadata


def _recent_service_rates(history: Sequence[dict[str, Any]]) -> tuple[float, float]:
    service = [row for row in history if row["action_succeeded"] is not None]
    if not service:
        return 1.0, 0.0
    success = _mean(1.0 if row["action_succeeded"] else 0.0 for row in service)
    failure = _mean(1.0 if row["action_succeeded"] is False else 0.0 for row in service)
    return success, failure


def _provenance_entry(
    value: float,
    trajectory_id: str,
    t: int,
    path: str,
    rationale: str,
) -> dict[str, Any]:
    return {
        "value": _norm(value),
        "status": "observed",
        "rationale": rationale,
        "evidence_refs": [f"ah://{trajectory_id}/{t}/{path}"],
        "scorer_id": SCORER_ID,
        "scorer_type": "automated",
        "confidence": 1.0,
    }


def _observer_features(
    trajectory_id: str,
    history: list[dict[str, Any]],
    current: dict[str, Any],
) -> tuple[dict[str, float | None], float, float, float, dict[str, Any]]:
    """Map causal time-t evidence to EFGM v2 / Agent Governance v0.3 outputs."""
    finite = (history + [current])[-HISTORY_WINDOW:]
    previous = history[-1] if history else None

    resource = _clip(current["resource"])
    backlog_fraction = _clip(current["backlog"] / MAX_BACKLOG)
    backlog_slack = 1.0 - backlog_fraction
    margin_fit = _clip((current["margin"] + 0.35) / 1.0)
    metadata: IntegrityMetadata = current["metadata"]

    success_rate, failure_rate = _recent_service_rates(finite)
    switch_rate = (
        sum(
            1
            for left, right in zip(finite, finite[1:])
            if left["executed_mode"] != right["executed_mode"]
        )
        / max(1, len(finite) - 1)
    )
    recovery_rate = _mean(
        1.0 if row["executed_mode"] == Mode.RECOVERY.value else 0.0
        for row in finite
    )
    repeated_failure_pressure = _clip(current["repeated_failures"] / 3.0)

    observed_values = [float(row["observed_disturbance"]) for row in finite]
    observed_mean = _mean(observed_values)
    observed_variability = _clip(
        _mean(abs(value - observed_mean) for value in observed_values) * 4.0
    )
    backlog_growth = (
        0.0
        if previous is None
        else _clip(max(0.0, (current["backlog"] - previous["backlog"]) / 3.0))
    )

    freshness = _clip(metadata.freshness)
    calibration = _clip(metadata.calibration_confidence)
    provenance = _clip(metadata.provenance_completeness)
    uncertainty = _clip(metadata.declared_uncertainty)
    hidden_information_load = _mean(
        [1.0 - calibration, 1.0 - freshness, uncertainty]
    )

    # EFGM v2 synthetic bridge. Canonical family weights are retained for the
    # mapped observations; N/A dimensions are excluded by renormalizing here.
    T = _clip((current["t"] + 1) / 4.0)
    C = _mean([resource, margin_fit])
    Fq = _weighted(
        [
            (success_rate, 0.30),
            (1.0 - switch_rate, 0.25),
            (success_rate, 0.20),
        ]
    )
    Ei = _weighted(
        [
            (observed_variability, 0.20),
            (1.0 - freshness, 0.20),
            (hidden_information_load, 0.20),
        ]
    )
    Eo = _weighted(
        [
            (failure_rate, 0.25),
            (switch_rate, 0.15),
            (backlog_growth, 0.15),
        ]
    )
    G = (
        1.0 * 0.25
        + calibration * 0.25
        + provenance * 0.20
        + calibration * 0.20
        + 1.0 * 0.10
    )
    U = _mean([calibration, 1.0 - uncertainty, freshness])
    Be = 0.0
    Oe = _weighted(
        [
            (repeated_failure_pressure, 0.20),
            (failure_rate, 0.25),
            (backlog_fraction, 0.15),
            (recovery_rate, 0.15),
        ]
    )
    CRC = (Ei - Eo) / max(Ei, 0.01)
    Q = max(0.0, T * C * Fq * G * U) ** (1.0 / 5.0)
    DQ = Q / (1.0 + Eo + Be + Oe)

    # Agent Governance v0.3 synthetic bridge. Coordination is N/A because this
    # experiment has one controller. Observation integrity is intentionally
    # allowed to affect governance families rather than being fixed perfect.
    alignment = 1.0
    boundary_integrity = _mean([margin_fit, calibration, provenance])
    observability = _mean([freshness, provenance])
    environmental_memory_governance = _mean(
        [backlog_slack, provenance, freshness]
    )
    control_recoverability = _mean([backlog_slack, resource, calibration])
    GI = math.prod(
        [
            alignment,
            boundary_integrity,
            observability,
            environmental_memory_governance,
            control_recoverability,
        ]
    ) ** (1.0 / 5.0)

    agency_amplification = {
        Mode.NORMAL.value: 1.0,
        Mode.CAUTION.value: 0.6,
        Mode.RECOVERY.value: 0.2,
    }[current["executed_mode"]]
    AE = agency_amplification * (1.0 - GI)
    CUE = DQ * AE

    features: dict[str, float | None] = {
        "DQ": _norm(DQ),
        "CRC": _norm(CRC),
        "GI": _norm(GI),
        "AE": _norm(AE),
        "CUE": _norm(CUE),
    }
    if previous is None:
        for name in ("DQ", "CRC", "GI", "AE", "CUE"):
            features[f"Delta_{name}"] = None
    else:
        previous_features = previous["efgm_features"]
        for name in ("DQ", "CRC", "GI", "AE", "CUE"):
            features[f"Delta_{name}"] = _norm(
                float(features[name]) - float(previous_features[name])
            )

    # Form B, chosen and frozen on development-visible evidence: for this
    # governance-specific event use only the three Agent Governance outputs.
    # The rule is monotonic and transparent.
    efgm_risk = _mean(
        [
            _clip(1.0 - float(features["GI"])),
            _clip(float(features["AE"])),
            _clip(float(features["CUE"])),
        ]
    )
    simple_integrity_risk = _mean(
        [
            1.0 - calibration,
            1.0 - freshness,
            1.0 - provenance,
            uncertainty,
        ]
    )

    provenance_payload = {
        "adapter_id": ADAPTER_ID,
        "scorer_id": SCORER_ID,
        "EFGM_v2": {
            "T": _provenance_entry(
                T, trajectory_id, current["t"], "T",
                "Observation maturity from causal sequence position.",
            ),
            "C": _provenance_entry(
                C, trajectory_id, current["t"], "C",
                "Capability suitability from remaining resource and observed-margin fit.",
            ),
            "grounding.evidence_validity": _provenance_entry(
                calibration, trajectory_id, current["t"], "grounding/evidence_validity",
                "Calibration-confidence metadata for the current observation.",
            ),
            "grounding.traceability": _provenance_entry(
                provenance, trajectory_id, current["t"], "grounding/traceability",
                "Current observation provenance completeness.",
            ),
            "uncertainty_calibration": _provenance_entry(
                U, trajectory_id, current["t"], "uncertainty_calibration",
                "Mean of calibration confidence, inverse declared uncertainty, and freshness.",
            ),
            "input.hidden_information_load": _provenance_entry(
                hidden_information_load,
                trajectory_id,
                current["t"],
                "input/hidden_information_load",
                "Causal proxy from calibration loss, staleness, and declared uncertainty.",
            ),
        },
        "Agent_Governance_v0_3": {
            "boundary_integrity": _provenance_entry(
                boundary_integrity,
                trajectory_id,
                current["t"],
                "governance/boundary_integrity",
                "Observed margin fit combined with calibration and provenance integrity.",
            ),
            "observability": _provenance_entry(
                observability,
                trajectory_id,
                current["t"],
                "governance/observability",
                "Mean of measurement freshness and provenance completeness.",
            ),
            "control_recoverability": _provenance_entry(
                control_recoverability,
                trajectory_id,
                current["t"],
                "governance/control_recoverability",
                "Backlog slack, remaining resource, and calibration confidence.",
            ),
        },
    }

    return (
        features,
        _norm(efgm_risk),
        _norm(simple_integrity_risk),
        _norm(failure_rate),
        provenance_payload,
    )


def _make_predictor_row(
    trajectory_id: str,
    t: int,
    current: dict[str, Any],
    features: dict[str, float | None],
    efgm_risk: float,
    simple_integrity_risk: float,
    failure_rate: float,
    provenance_payload: dict[str, Any],
) -> dict[str, Any]:
    metadata: IntegrityMetadata = current["metadata"]
    baseline_values = {
        "B1_backlog": float(current["backlog"]),
        "B2_resource": _norm(current["resource"]),
        "B3_margin": _norm(current["margin"]),
        "B4_observed_disturbance": _norm(current["observed_disturbance"]),
        "B5_calibration": _norm(metadata.calibration_confidence),
        "B6_freshness": _norm(metadata.freshness),
        "B7_provenance": _norm(metadata.provenance_completeness),
        "B8_failure_rate": _norm(failure_rate),
        "B9_simple_integrity": _norm(simple_integrity_risk),
    }
    return {
        "trajectory_id": trajectory_id,
        "t": t,
        "operational": {
            "backlog": current["backlog"],
            "resource": _norm(current["resource"]),
            "observed_disturbance": _norm(current["observed_disturbance"]),
            "margin": _norm(current["margin"]),
            "failure_rate": _norm(failure_rate),
        },
        "integrity": {
            "freshness": _norm(metadata.freshness),
            "calibration": _norm(metadata.calibration_confidence),
            "provenance": _norm(metadata.provenance_completeness),
            "uncertainty": _norm(metadata.declared_uncertainty),
            "source_state": metadata.source_state,
        },
        "efgm": features,
        "efgm_risk": _norm(efgm_risk),
        "simple_integrity_risk": _norm(simple_integrity_risk),
        "baseline_values": baseline_values,
        "provenance": provenance_payload,
    }


def _run_trajectory(
    *,
    trajectory_id: str,
    profile: str,
    true_schedule: Sequence[float],
    observation_factory,
    seed: int | None = None,
    mu: float | None = None,
    schedule_name: str | None = None,
) -> TrajectoryEvidence:
    telemetry = QueueTelemetry()
    regulator = Regulator()
    observation_state = ObservationState()
    observer_history: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []
    full_trace: list[dict[str, Any]] = []
    harm_record: HarmRecord | None = None
    tau_harm: int | None = None

    for t, true_disturbance in enumerate(true_schedule[:HORIZON]):
        if telemetry.completed or not telemetry.viable:
            break

        backlog_before_arrival = telemetry.backlog
        telemetry.backlog = min(
            MAX_BACKLOG + 1,
            telemetry.backlog + _arrival(true_disturbance, t),
        )
        if not telemetry.viable:
            full_trace.append(
                {
                    "t": t,
                    "true_disturbance": _norm(true_disturbance),
                    "phase": "post_arrival_capacity_loss",
                    "backlog_before_arrival": backlog_before_arrival,
                    "backlog_after_arrival": telemetry.backlog,
                }
            )
            break

        if seed is None:
            observed_disturbance, metadata = observation_factory(
                profile, true_schedule, t, observation_state
            )
        else:
            observed_disturbance, metadata = observation_factory(
                profile, true_schedule, t, seed
            )

        pre_action = _clone_telemetry(telemetry)
        actual_margin = regulator.margin(
            observed_disturbance,
            telemetry.resource,
            telemetry.failures,
        )
        actual_mode = regulator.mode(actual_margin)

        oracle_regulator = Regulator()
        oracle_margin = oracle_regulator.margin(
            true_disturbance,
            pre_action.resource,
            pre_action.failures,
        )
        oracle_mode = oracle_regulator.mode(oracle_margin)
        oracle_state = _clone_telemetry(pre_action)

        actual_harm_like, actual_action_failed = _apply_mode(
            telemetry, actual_mode, true_disturbance, t
        )
        oracle_harm_like, oracle_action_failed = _apply_mode(
            oracle_state, oracle_mode, true_disturbance, t
        )

        harmful = (
            PROTECTION_ORDER[actual_mode] < PROTECTION_ORDER[oracle_mode]
            and actual_harm_like
            and not oracle_harm_like
        )

        trace_row = {
            "trajectory_id": trajectory_id,
            "profile": profile,
            "t": t,
            "true_disturbance": _norm(true_disturbance),
            "observed_disturbance": _norm(observed_disturbance),
            "metadata": asdict(metadata),
            "backlog_before_arrival": backlog_before_arrival,
            "backlog_after_arrival": pre_action.backlog,
            "resource_before_action": _norm(pre_action.resource),
            "failures_before_action": pre_action.failures,
            "actual_margin": _norm(actual_margin),
            "oracle_margin": _norm(oracle_margin),
            "actual_mode": actual_mode.value,
            "oracle_mode": oracle_mode.value,
            "actual_action_failed": actual_action_failed,
            "oracle_action_failed": oracle_action_failed,
            "actual_viable_after": telemetry.viable,
            "oracle_viable_after": oracle_state.viable,
            "actual_backlog_after": telemetry.backlog,
            "oracle_backlog_after": oracle_state.backlog,
            "actual_resource_after": _norm(telemetry.resource),
            "oracle_resource_after": _norm(oracle_state.resource),
            "harmful_underprotection": harmful,
        }
        full_trace.append(trace_row)

        if harmful:
            tau_harm = t
            harm_record = HarmRecord(
                t=t,
                true_disturbance=_norm(true_disturbance),
                observed_disturbance=_norm(observed_disturbance),
                actual_mode=actual_mode.value,
                oracle_mode=oracle_mode.value,
                actual_failed=actual_action_failed,
                oracle_failed=oracle_action_failed,
                actual_viable_after=telemetry.viable,
                oracle_viable_after=oracle_state.viable,
            )
            break

        if telemetry.completed or not telemetry.viable:
            break

        action_succeeded = (
            None if actual_mode is Mode.RECOVERY else (not actual_action_failed)
        )
        observer_current = {
            "t": t,
            "observed_disturbance": _norm(observed_disturbance),
            "metadata": metadata,
            "margin": _norm(actual_margin),
            "selected_mode": actual_mode.value,
            "executed_mode": actual_mode.value,
            "action_succeeded": action_succeeded,
            "resource": _norm(telemetry.resource),
            "backlog": telemetry.backlog,
            "failures": telemetry.failures,
            "repeated_failures": telemetry.repeated_failures,
        }
        features, efgm_risk, simple_risk, failure_rate, provenance_payload = (
            _observer_features(trajectory_id, observer_history, observer_current)
        )
        observer_current["efgm_features"] = features
        prediction_rows.append(
            _make_predictor_row(
                trajectory_id,
                t,
                observer_current,
                features,
                efgm_risk,
                simple_risk,
                failure_rate,
                provenance_payload,
            )
        )
        observer_history.append(observer_current)

    # Future labels are attached only after the trajectory is complete.
    for row in prediction_rows:
        t = int(row["t"])
        row["y_t_2"] = int(
            tau_harm is not None
            and tau_harm in (t + 1, t + 2)
        )

    return TrajectoryEvidence(
        trajectory_id=trajectory_id,
        profile=profile,
        mu=mu,
        seed=seed,
        schedule_name=schedule_name,
        tau_harm=tau_harm,
        prediction_rows=prediction_rows,
        full_trace=full_trace,
        harm_record=harm_record,
        terminal_completed=telemetry.completed,
        terminal_viable=telemetry.viable,
    )


def development_trajectories() -> list[TrajectoryEvidence]:
    """Regenerate only development-visible AH-EXP-0013 cases."""
    results: list[TrajectoryEvidence] = []
    for seed in SEEDS:
        for schedule_name, nominal in SCHEDULES.items():
            realized = stochastic_schedule(nominal, seed)
            for profile in DEVELOPMENT_PROFILES:
                results.append(
                    _run_trajectory(
                        trajectory_id=f"dev-{profile}-{seed}-{schedule_name}",
                        profile=profile,
                        true_schedule=realized,
                        observation_factory=_development_observation,
                        seed=seed,
                        schedule_name=schedule_name,
                    )
                )
    return results


def _development_canonical_rows(
    trajectories: Sequence[TrajectoryEvidence],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for trajectory in trajectories:
        for row in trajectory.prediction_rows:
            rows.append(
                {
                    "trajectory_id": row["trajectory_id"],
                    "profile": trajectory.profile,
                    "t": row["t"],
                    "operational": row["operational"],
                    "integrity": row["integrity"],
                    "efgm": row["efgm"],
                    "efgm_risk": row["efgm_risk"],
                    "simple_integrity_risk": row["simple_integrity_risk"],
                    "y_t_2": row["y_t_2"],
                }
            )
    return rows


def _confusion(predictions: Sequence[bool], labels: Sequence[int]) -> dict[str, Any]:
    tp = sum(int(pred and label == 1) for pred, label in zip(predictions, labels))
    fp = sum(int(pred and label == 0) for pred, label in zip(predictions, labels))
    tn = sum(int((not pred) and label == 0) for pred, label in zip(predictions, labels))
    fn = sum(int((not pred) and label == 1) for pred, label in zip(predictions, labels))
    sensitivity = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "precision": precision,
        "balanced_accuracy": (sensitivity + specificity) / 2.0,
    }


def _threshold_predictions(
    values: Sequence[float],
    threshold: float,
    orientation: str,
) -> list[bool]:
    if orientation == "high":
        return [value >= threshold for value in values]
    if orientation == "low":
        return [value <= threshold for value in values]
    raise ValueError(f"unknown orientation: {orientation}")


def _select_threshold(
    values: Sequence[float],
    labels: Sequence[int],
    orientation: str,
) -> tuple[float, dict[str, Any]]:
    best: tuple[tuple[float, float, float, float], float, dict[str, Any]] | None = None
    for threshold in sorted(set(float(value) for value in values)):
        metrics = _confusion(
            _threshold_predictions(values, threshold, orientation),
            labels,
        )
        conservative = threshold if orientation == "high" else -threshold
        key = (
            metrics["balanced_accuracy"],
            metrics["specificity"],
            metrics["precision"],
            conservative,
        )
        if best is None or key > best[0]:
            best = (key, threshold, metrics)
    if best is None:
        raise ValueError("threshold selection requires at least one value")
    return _norm(best[1]), best[2]


def development_calibration() -> dict[str, Any]:
    trajectories = development_trajectories()
    canonical_rows = _development_canonical_rows(trajectories)
    labels = [int(row["y_t_2"]) for row in canonical_rows]

    values: dict[str, tuple[list[float], str]] = {
        "EFGM": ([float(row["efgm_risk"]) for row in canonical_rows], "high"),
        "B1_backlog": ([float(row["operational"]["backlog"]) for row in canonical_rows], "high"),
        "B2_resource": ([float(row["operational"]["resource"]) for row in canonical_rows], "low"),
        "B3_margin": ([float(row["operational"]["margin"]) for row in canonical_rows], "low"),
        "B4_observed_disturbance": (
            [float(row["operational"]["observed_disturbance"]) for row in canonical_rows],
            "high",
        ),
        "B5_calibration": (
            [float(row["integrity"]["calibration"]) for row in canonical_rows],
            "low",
        ),
        "B6_freshness": (
            [float(row["integrity"]["freshness"]) for row in canonical_rows],
            "low",
        ),
        "B7_provenance": (
            [float(row["integrity"]["provenance"]) for row in canonical_rows],
            "low",
        ),
        "B8_failure_rate": (
            [float(row["operational"]["failure_rate"]) for row in canonical_rows],
            "high",
        ),
        "B9_simple_integrity": (
            [float(row["simple_integrity_risk"]) for row in canonical_rows],
            "high",
        ),
    }

    selected: dict[str, dict[str, Any]] = {}
    for name, (series, orientation) in values.items():
        threshold, metrics = _select_threshold(series, labels, orientation)
        selected[name] = {
            "threshold": threshold,
            "orientation": orientation,
            "metrics": metrics,
        }

    baseline_names = [name for name in selected if name.startswith("B")]
    best_baseline = max(
        baseline_names,
        key=lambda name: (
            selected[name]["metrics"]["balanced_accuracy"],
            selected[name]["metrics"]["specificity"],
            selected[name]["metrics"]["precision"],
            name,
        ),
    )

    return {
        "experiment": EXPERIMENT_ID,
        "phase": "development_only",
        "trajectory_count": len(trajectories),
        "prediction_count": len(canonical_rows),
        "positive_label_count": sum(labels),
        "negative_label_count": len(labels) - sum(labels),
        "harmful_trajectory_count": sum(
            int(trajectory.tau_harm is not None) for trajectory in trajectories
        ),
        "development_rows_sha256": _canonical_hash(canonical_rows),
        "selected": selected,
        "best_baseline": best_baseline,
        "confirmatory_outcomes_observed": False,
    }


def verify_frozen_development_calibration() -> dict[str, Any]:
    result = development_calibration()
    if result["development_rows_sha256"] != DEVELOPMENT_ROWS_SHA256:
        raise AssertionError(
            "AH-EXP-0013 development rows changed: "
            f"{result['development_rows_sha256']} != {DEVELOPMENT_ROWS_SHA256}"
        )
    if result["selected"]["EFGM"]["threshold"] != EFGM_WARNING_THRESHOLD:
        raise AssertionError("Frozen EFGM threshold no longer reproduces")
    for name, expected in BASELINE_THRESHOLDS.items():
        if result["selected"][name]["threshold"] != expected:
            raise AssertionError(
                f"Frozen baseline threshold {name} no longer reproduces: "
                f"{result['selected'][name]['threshold']} != {expected}"
            )
    if result["best_baseline"] != BEST_BASELINE:
        raise AssertionError("Frozen best baseline no longer reproduces")
    return result


def run_confirmatory_trajectories() -> list[TrajectoryEvidence]:
    """Execute the frozen 355-trajectory holdout.

    This function must not be called during observer construction or ordinary
    structural CI. It exists for the post-freeze evaluation workflow only.
    """
    results: list[TrajectoryEvidence] = []
    trajectory_index = 0
    for mu in confirmatory_mu_grid():
        true_schedule = confirmatory_true_schedule(mu)
        for profile in CONFIRMATORY_PROFILES:
            results.append(
                _run_trajectory(
                    trajectory_id=f"holdout-{trajectory_index:03d}",
                    profile=profile,
                    true_schedule=true_schedule,
                    observation_factory=_confirmatory_observation,
                    mu=mu,
                )
            )
            trajectory_index += 1
    return results


def _baseline_predicate(name: str, value: float) -> bool:
    return _threshold_predictions(
        [float(value)],
        BASELINE_THRESHOLDS[name],
        BASELINE_ORIENTATION[name],
    )[0]


def _holdout_prediction_row(row: dict[str, Any]) -> dict[str, Any]:
    baseline_predictions = {
        name: _baseline_predicate(name, float(row["baseline_values"][name]))
        for name in BASELINE_THRESHOLDS
    }
    return {
        "trajectory_id": row["trajectory_id"],
        "t": row["t"],
        "operational": row["operational"],
        "integrity": row["integrity"],
        "efgm": row["efgm"],
        "efgm_risk": row["efgm_risk"],
        "simple_integrity_risk": row["simple_integrity_risk"],
        "efgm_warn": float(row["efgm_risk"]) >= EFGM_WARNING_THRESHOLD,
        "baseline_values": row["baseline_values"],
        "baseline_predictions": baseline_predictions,
        "y_t_2": row["y_t_2"],
        "provenance": row["provenance"],
    }


def evaluate_holdout() -> dict[str, Any]:
    """Execute and score the previously unseen AH-EXP-0013 holdout."""
    verify_frozen_development_calibration()
    trajectories = run_confirmatory_trajectories()

    prediction_rows = [
        _holdout_prediction_row(row)
        for trajectory in trajectories
        for row in trajectory.prediction_rows
    ]
    labels = [int(row["y_t_2"]) for row in prediction_rows]
    efgm_predictions = [bool(row["efgm_warn"]) for row in prediction_rows]
    efgm_confusion = _confusion(efgm_predictions, labels)

    baseline_confusions: dict[str, dict[str, Any]] = {}
    for name in BASELINE_THRESHOLDS:
        baseline_confusions[name] = _confusion(
            [bool(row["baseline_predictions"][name]) for row in prediction_rows],
            labels,
        )

    best_confusion = baseline_confusions[BEST_BASELINE]
    delta_ba = (
        efgm_confusion["balanced_accuracy"]
        - best_confusion["balanced_accuracy"]
    )

    event_trajectories = [
        trajectory for trajectory in trajectories if trajectory.tau_harm is not None
    ]
    lead_times: list[int] = []
    missed = 0
    for trajectory in event_trajectories:
        warnings = [
            int(row["t"])
            for row in prediction_rows
            if row["trajectory_id"] == trajectory.trajectory_id
            and bool(row["efgm_warn"])
            and int(row["t"]) < int(trajectory.tau_harm)
        ]
        if warnings:
            lead_times.append(int(trajectory.tau_harm) - min(warnings))
        else:
            missed += 1

    positive_count = sum(labels)
    negative_count = len(labels) - positive_count
    if not event_trajectories or negative_count == 0:
        status = "INCONCLUSIVE"
    else:
        survived = (
            efgm_confusion["balanced_accuracy"] > 0.50
            and delta_ba >= 0.02
            and len(lead_times) >= 1
        )
        status = "SURVIVED" if survived else "FALSIFIED"

    compact_rows = [
        {
            "trajectory_id": row["trajectory_id"],
            "t": row["t"],
            "efgm_risk": row["efgm_risk"],
            "efgm_warn": row["efgm_warn"],
            "baseline_values": row["baseline_values"],
            "baseline_predictions": row["baseline_predictions"],
            "y_t_2": row["y_t_2"],
        }
        for row in prediction_rows
    ]
    full_trace = [
        {
            "trajectory_id": trajectory.trajectory_id,
            "profile": trajectory.profile,
            "mu": trajectory.mu,
            "tau_harm": trajectory.tau_harm,
            "harm_record": (
                None if trajectory.harm_record is None else asdict(trajectory.harm_record)
            ),
            "terminal_completed": trajectory.terminal_completed,
            "terminal_viable": trajectory.terminal_viable,
            "trace": trajectory.full_trace,
        }
        for trajectory in trajectories
    ]

    profile_results: dict[str, dict[str, Any]] = {}
    for profile in CONFIRMATORY_PROFILES:
        profile_ids = {
            trajectory.trajectory_id
            for trajectory in trajectories
            if trajectory.profile == profile
        }
        rows = [row for row in prediction_rows if row["trajectory_id"] in profile_ids]
        profile_labels = [int(row["y_t_2"]) for row in rows]
        profile_results[profile] = {
            "trajectory_count": len(profile_ids),
            "harmful_trajectory_count": sum(
                int(trajectory.tau_harm is not None)
                for trajectory in trajectories
                if trajectory.profile == profile
            ),
            "prediction_count": len(rows),
            "positive_label_count": sum(profile_labels),
            "negative_label_count": len(profile_labels) - sum(profile_labels),
            "efgm_confusion": _confusion(
                [bool(row["efgm_warn"]) for row in rows],
                profile_labels,
            ) if rows else None,
        }

    return {
        "experiment": EXPERIMENT_ID,
        "status": status,
        "preregistration_freeze_sha": PREREGISTRATION_FREEZE_SHA,
        "ah_substrate_sha": AH_SUBSTRATE_SHA,
        "efgm_code_sha": EFGM_CODE_SHA,
        "efgm_v2_config_id": EFGM_V2_CONFIG_ID,
        "efgm_v2_config_sha256": EFGM_V2_CONFIG_SHA256,
        "agent_config_id": AGENT_CONFIG_ID,
        "agent_config_sha256": AGENT_CONFIG_SHA256,
        "adapter_id": ADAPTER_ID,
        "development_rows_sha256": DEVELOPMENT_ROWS_SHA256,
        "holdout_design_hash": holdout_design_hash(),
        "efgm_warning_rule": "mean(1-GI, AE, CUE)",
        "efgm_warning_threshold": EFGM_WARNING_THRESHOLD,
        "baseline_thresholds": BASELINE_THRESHOLDS,
        "best_baseline": BEST_BASELINE,
        "trajectory_count": len(trajectories),
        "prediction_count": len(prediction_rows),
        "positive_label_count": positive_count,
        "negative_label_count": negative_count,
        "harmful_trajectory_count": len(event_trajectories),
        "efgm_confusion": efgm_confusion,
        "baseline_confusions": baseline_confusions,
        "delta_ba": delta_ba,
        "detected_harmful_trajectory_count": len(lead_times),
        "missed_harmful_trajectory_count": missed,
        "lead_times": lead_times,
        "profile_results": profile_results,
        "canonical_result_hash": _canonical_hash(compact_rows),
        "full_trace_hash": _canonical_hash(full_trace),
        "prediction_rows": prediction_rows,
        "full_trace": full_trace,
    }


def structural_manifest() -> dict[str, Any]:
    return {
        "experiment": EXPERIMENT_ID,
        "phase": "implementation_structure_only",
        "preregistration_freeze_sha": PREREGISTRATION_FREEZE_SHA,
        "ah_substrate_sha": AH_SUBSTRATE_SHA,
        "efgm_code_sha": EFGM_CODE_SHA,
        "adapter_id": ADAPTER_ID,
        "efgm_warning_rule": "mean(1-GI, AE, CUE)",
        "efgm_warning_threshold": EFGM_WARNING_THRESHOLD,
        "baseline_thresholds": BASELINE_THRESHOLDS,
        "best_baseline": BEST_BASELINE,
        "development_rows_sha256": DEVELOPMENT_ROWS_SHA256,
        "holdout_design_hash": holdout_design_hash(),
        "confirmatory_trajectory_count": 355,
        "confirmatory_outcomes_observed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", action="store_true")
    parser.add_argument("--development", action="store_true")
    args = parser.parse_args()

    if args.development:
        print(json.dumps(verify_frozen_development_calibration(), indent=2, sort_keys=True))
        return
    if args.manifest:
        print(json.dumps(structural_manifest(), indent=2, sort_keys=True))
        return
    raise SystemExit(
        "AH-EXP-0013 confirmatory validation is intentionally unavailable from the "
        "construction CLI. Use --manifest or --development; the post-freeze "
        "evaluation workflow calls evaluate_holdout() explicitly."
    )


if __name__ == "__main__":
    main()
