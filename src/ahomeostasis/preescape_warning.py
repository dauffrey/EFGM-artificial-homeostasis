from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict
from typing import Any, Iterable

from .adversarial_robustness import EnvironmentConfig, _arrival, _maintenance, _service
from .core import Mode, Regulator
from .counterfactual_regulation import DecisionSnapshot, DetectorState
from .queue_replication import MAX_BACKLOG, QueueTelemetry
from .robust_counterfactual_abstention import should_relax_robust
from .trajectory_boundary import (
    COMPARISON_CONTROLLER,
    PRIMARY_CONTROLLER,
    StepTrace,
    TrajectoryResult,
    classify_terminal,
    failure_mechanism,
    mu_grid,
    run_sweep,
)

EXPERIMENT_ID = "AH-EXP-0012"
PREREGISTRATION_FREEZE_SHA = "4c01e559548341e16310981ade06871f63685d00"
AH_SUBSTRATE_SHA = "e21d68d1257ef36a3882a5f6362535f701d6350c"
EFGM_CODE_SHA = "37b2ff2d2b577c9f383dd0d7c3083597627150ea"
EFGM_V2_CONFIG_ID = "efgm-v2.0-baseline"
EFGM_V2_CONFIG_SHA256 = "0f55f6eabe97d0f365d1e45ba8f9d0fef67e9721a93e6eba8b0a364b612bafd0"
AGENT_CONFIG_ID = "efgm-v0.3-agent-governance-candidate-r2"
AGENT_CONFIG_SHA256 = "af0b5540f28d4d65ae95929a855a168f9e7c286439d33d33e14ef167d808366c"

HORIZON = 100
HISTORY_WINDOW = 3
HOLDOUT_MODULATION = (
    -0.15,
    -0.09,
    -0.03,
    0.03,
    0.09,
    0.15,
    0.09,
    0.03,
    -0.03,
    -0.09,
    -0.12,
    -0.06,
    0.00,
    0.06,
    0.12,
    0.06,
    0.00,
    -0.06,
    0.00,
    0.00,
)

PRIMARY_FEATURES = (
    "DQ",
    "CRC",
    "GI",
    "AE",
    "CUE",
    "Delta_DQ",
    "Delta_CRC",
    "Delta_GI",
    "Delta_AE",
    "Delta_CUE",
)
LOWER_IS_HIGHER_RISK = {
    "DQ",
    "CRC",
    "GI",
    "Delta_DQ",
    "Delta_CRC",
    "Delta_GI",
}
HIGHER_IS_HIGHER_RISK = {
    "AE",
    "CUE",
    "Delta_AE",
    "Delta_CUE",
}

# Frozen from AH-EXP-0011 development data only.
EFGM_WARNING_THRESHOLD = 0.582818749642
BASELINE_THRESHOLDS = {
    "backlog": 9.0,
    "resource": 0.878775,
    "margin": 0.235,
    "disturbance": 0.745,
}
BEST_SINGLE_BASELINE = "backlog"
DEVELOPMENT_ROWS_SHA256 = "e5c5a73db69cc2db6fc9d6661f6af6cc6dab7c50c57258d86b0634f5402f3044"

ADAPTER_ID = "ah-exp-0012-efgm-adapter-v1"
SCORER_ID = "ah-exp-0012-adapter-v1"


def _norm(value: float) -> float:
    return round(float(value), 12)


def _clip(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def _weighted(values: Iterable[tuple[float, float]]) -> float:
    values = list(values)
    total = sum(weight for _, weight in values)
    if total <= 0:
        raise ValueError("weights must sum to a positive value")
    return sum(value * weight for value, weight in values) / total


def _evidence(value: float, path: str, controller: str, mu: float, t: int, rationale: str) -> dict[str, Any]:
    return {
        "value": _norm(value),
        "status": "observed",
        "rationale": rationale,
        "evidence_refs": [f"ah://{controller}/{mu:.3f}/{t}/{path}"],
        "scorer_id": SCORER_ID,
        "scorer_type": "automated",
        "confidence": 1.0,
    }


def holdout_disturbance_at(mu: float, t: int) -> float:
    if not 0.0 <= mu <= 1.0:
        raise ValueError("mu must be within [0, 1]")
    value = mu + HOLDOUT_MODULATION[t % len(HOLDOUT_MODULATION)]
    return _norm(max(0.0, min(1.0, value)))


def _observer_base(trace: tuple[StepTrace, ...] | list[StepTrace], index: int) -> tuple[dict[str, float], dict[str, Any]]:
    row = trace[index]
    if row.backlog_after_action is None or row.margin is None or row.executed_mode is None:
        raise ValueError("observer requires an end-of-step viable post-action trace row")

    start = max(0, index - HISTORY_WINDOW + 1)
    history = list(trace[start : index + 1])
    previous = trace[index - 1] if index > 0 and trace[index - 1].backlog_after_action is not None else None

    resource = _clip(row.resource_after)
    backlog_fraction = _clip(row.backlog_after_action / MAX_BACKLOG)
    backlog_slack = 1.0 - backlog_fraction
    margin_fit = _clip((row.margin + 0.35) / 1.0)

    service_rows = [item for item in history if item.action_succeeded is not None]
    success_rate = (
        _mean(1.0 if item.action_succeeded else 0.0 for item in service_rows)
        if service_rows
        else 1.0
    )
    failure_rate = (
        _mean(1.0 if item.action_succeeded is False else 0.0 for item in service_rows)
        if service_rows
        else 0.0
    )
    switch_rate = (
        sum(1 for left, right in zip(history, history[1:]) if left.executed_mode != right.executed_mode)
        / max(1, len(history) - 1)
    )
    recovery_rate = _mean(1.0 if item.executed_mode == Mode.RECOVERY.value else 0.0 for item in history)
    repeated_failure_pressure = _clip(row.repeated_failures / 3.0)

    disturbances = [item.disturbance for item in history]
    disturbance_mean = _mean(disturbances)
    disturbance_variability = _clip(_mean(abs(value - disturbance_mean) for value in disturbances) * 4.0)
    disturbance_change = (
        0.0
        if previous is None
        else _clip(abs(row.disturbance - previous.disturbance) / 0.24)
    )
    backlog_growth = (
        0.0
        if previous is None
        else _clip(max(0.0, (row.backlog_after_action - previous.backlog_after_action) / 3.0))
    )

    # EFGM v2 mapping. Each formula follows the frozen v2 aggregation semantics;
    # only the synthetic observation mapping is specific to this experiment.
    T = _clip((row.t + 1) / 4.0)
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
            (disturbance_variability, 0.20),
            (disturbance_change, 0.20),
            (0.0, 0.20),
        ]
    )
    Eo = _weighted(
        [
            (failure_rate, 0.25),
            (switch_rate, 0.15),
            (backlog_growth, 0.15),
        ]
    )
    G = 1.0
    U = 1.0
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
    Q = (T * C * Fq * G * U) ** (1.0 / 5.0)
    DQ = Q / (1.0 + Eo + Be + Oe)

    # Agent Governance v0.3 mapping. Coordination is N/A for this single-agent
    # environment and is excluded exactly as permitted by the candidate model.
    alignment = 1.0
    boundary_integrity = min(margin_fit, backlog_slack)
    observability = 1.0
    environmental_memory_governance = _mean([backlog_slack, 1.0])
    control_recoverability = _mean([backlog_slack, backlog_slack, resource])
    governance_integrity = math.prod(
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
    }[row.executed_mode]
    agency_exposure = agency_amplification * (1.0 - governance_integrity)
    coherent_unsafe_execution = DQ * agency_exposure

    features = {
        "DQ": _norm(DQ),
        "CRC": _norm(CRC),
        "GI": _norm(governance_integrity),
        "AE": _norm(agency_exposure),
        "CUE": _norm(coherent_unsafe_execution),
    }

    provenance = {
        "T": _evidence(T, "T", row.controller, row.mu, row.t, "Observation maturity from sequence position."),
        "C": _evidence(C, "C", row.controller, row.mu, row.t, "Synthetic capability suitability from remaining resource and regulator margin fit."),
        "flow.task_completion_consistency": _evidence(success_rate, "flow/task_completion_consistency", row.controller, row.mu, row.t, "Recent service-action success rate."),
        "flow.reasoning_continuity": _evidence(1.0 - switch_rate, "flow/reasoning_continuity", row.controller, row.mu, row.t, "Inverse recent controller-mode switching rate."),
        "flow.verification_success_rate": _evidence(success_rate, "flow/verification_success_rate", row.controller, row.mu, row.t, "Recent realized action success rate."),
        "input.input_ambiguity": _evidence(disturbance_variability, "input/input_ambiguity", row.controller, row.mu, row.t, "Finite-window disturbance variability proxy."),
        "input.missing_context": _evidence(disturbance_change, "input/missing_context", row.controller, row.mu, row.t, "Finite-window load-change proxy; no future disturbance is used."),
        "input.hidden_information_load": _evidence(0.0, "input/hidden_information_load", row.controller, row.mu, row.t, "Synthetic simulator exposes all permitted current-state channels to the observer."),
        "output.uncertainty_mismatch": _evidence(failure_rate, "output/uncertainty_mismatch", row.controller, row.mu, row.t, "Recent realized action-failure rate."),
        "output.reasoning_instability": _evidence(switch_rate, "output/reasoning_instability", row.controller, row.mu, row.t, "Recent controller-mode switching rate."),
        "output.context_decay": _evidence(backlog_growth, "output/context_decay", row.controller, row.mu, row.t, "Positive backlog-growth proxy."),
        "grounding.rule_support": _evidence(1.0, "grounding/rule_support", row.controller, row.mu, row.t, "Controller and environment rules are deterministic and directly traceable."),
        "grounding.evidence_validity": _evidence(1.0, "grounding/evidence_validity", row.controller, row.mu, row.t, "Metrics are computed from the frozen step trace."),
        "grounding.traceability": _evidence(1.0, "grounding/traceability", row.controller, row.mu, row.t, "Every mapped value references the frozen trajectory row."),
        "grounding.factual_consistency": _evidence(1.0, "grounding/factual_consistency", row.controller, row.mu, row.t, "No external factual claims are introduced by the synthetic adapter."),
        "grounding.domain_calibration": _evidence(1.0, "grounding/domain_calibration", row.controller, row.mu, row.t, "Mapping scope is restricted to the frozen synthetic queue environment."),
        "uncertainty_calibration": _evidence(1.0, "uncertainty_calibration", row.controller, row.mu, row.t, "Current realized disturbance is observed exactly; no future forecast is supplied."),
        "operational.retry_instability": _evidence(repeated_failure_pressure, "operational/retry_instability", row.controller, row.mu, row.t, "Normalized accumulated repeated failures."),
        "operational.tool_failure_rate": _evidence(failure_rate, "operational/tool_failure_rate", row.controller, row.mu, row.t, "Recent action-failure rate."),
        "operational.latency_pressure": _evidence(backlog_fraction, "operational/latency_pressure", row.controller, row.mu, row.t, "Backlog as a fraction of the frozen viability limit."),
        "operational.workflow_interruption": _evidence(recovery_rate, "operational/workflow_interruption", row.controller, row.mu, row.t, "Recent fraction of recovery-only actions."),
        "governance.alignment.objective_scope_fidelity": _evidence(alignment, "governance/alignment/objective_scope_fidelity", row.controller, row.mu, row.t, "Frozen task objective does not change during a trajectory."),
        "governance.boundary_integrity.capability_scope_adherence": _evidence(boundary_integrity, "governance/boundary_integrity/capability_scope_adherence", row.controller, row.mu, row.t, "Minimum of backlog viability slack and normalized regulator margin fit."),
        "governance.observability.action_trace_coverage": _evidence(1.0, "governance/observability/action_trace_coverage", row.controller, row.mu, row.t, "Every executed action is present in StepTrace."),
        "governance.observability.state_change_traceability": _evidence(1.0, "governance/observability/state_change_traceability", row.controller, row.mu, row.t, "Resource, backlog, work, failures, modes, and viability are traced."),
        "governance.environmental_memory.readback_traceability": _evidence(1.0, "governance/environmental_memory/readback_traceability", row.controller, row.mu, row.t, "Queue state is directly readable each step."),
        "governance.environmental_memory.shared_state_control": _evidence(backlog_slack, "governance/environmental_memory/shared_state_control", row.controller, row.mu, row.t, "Backlog slack is the synthetic persistent-state control proxy."),
        "governance.control_recoverability.containment_effectiveness": _evidence(backlog_slack, "governance/control_recoverability/containment_effectiveness", row.controller, row.mu, row.t, "Remaining slack before backlog viability loss."),
        "governance.control_recoverability.state_cleanup_completeness": _evidence(backlog_slack, "governance/control_recoverability/state_cleanup_completeness", row.controller, row.mu, row.t, "Residual queue pressure expressed as remaining cleanup slack."),
        "governance.control_recoverability.rollback_effectiveness": _evidence(resource, "governance/control_recoverability/rollback_effectiveness", row.controller, row.mu, row.t, "Remaining resource is the synthetic restoration-capacity proxy."),
        "governance.agency_amplification.action_velocity": _evidence(agency_amplification, "governance/agency_amplification/action_velocity", row.controller, row.mu, row.t, "Frozen action-velocity proxy by executed controller mode."),
    }
    return features, provenance


def _with_deltas(current: dict[str, float], previous: dict[str, float] | None) -> dict[str, float | None]:
    output: dict[str, float | None] = dict(current)
    for key in ("DQ", "CRC", "GI", "AE", "CUE"):
        output[f"Delta_{key}"] = None if previous is None else _norm(current[key] - previous[key])
    return output


def _development_rows() -> list[dict[str, Any]]:
    sweep = run_sweep(controller=PRIMARY_CONTROLLER)
    rows: list[dict[str, Any]] = []
    for trajectory in sweep.trajectories:
        previous: dict[str, float] | None = None
        for index, trace_row in enumerate(trajectory.trace):
            if trace_row.completed or not trace_row.viable:
                continue
            base, _ = _observer_base(trajectory.trace, index)
            features = _with_deltas(base, previous)
            previous = base
            label = int(
                trajectory.tau_escape is not None
                and 1 <= trajectory.tau_escape - trace_row.t <= 2
            )
            rows.append(
                {
                    "mu": f"{trajectory.mu:.3f}",
                    "t": trace_row.t,
                    "y": label,
                    **features,
                    "backlog": trace_row.backlog_after_action,
                    "resource": _norm(trace_row.resource_after),
                    "margin": _norm(trace_row.margin),
                    "disturbance": _norm(trace_row.disturbance),
                }
            )
    return rows


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _risk_percentile(values: list[float], value: float, *, higher_is_risk: bool) -> float:
    if higher_is_risk:
        return sum(item <= value for item in values) / len(values)
    return sum(item >= value for item in values) / len(values)


def _score_risk(features: dict[str, float | None], distributions: dict[str, list[float]]) -> float | None:
    percentiles: list[float] = []
    for feature in PRIMARY_FEATURES:
        value = features.get(feature)
        if value is None:
            continue
        percentiles.append(
            _risk_percentile(
                distributions[feature],
                float(value),
                higher_is_risk=feature in HIGHER_IS_HIGHER_RISK,
            )
        )
    if len(percentiles) < 3:
        return None
    return _norm(_mean(percentiles))


def _confusion(rows: list[dict[str, Any]], prediction_key: str) -> dict[str, Any]:
    tp = sum(1 for row in rows if row["y"] == 1 and row[prediction_key])
    fn = sum(1 for row in rows if row["y"] == 1 and not row[prediction_key])
    tn = sum(1 for row in rows if row["y"] == 0 and not row[prediction_key])
    fp = sum(1 for row in rows if row["y"] == 0 and row[prediction_key])
    sensitivity = tp / (tp + fn) if tp + fn else None
    specificity = tn / (tn + fp) if tn + fp else None
    precision = tp / (tp + fp) if tp + fp else None
    balanced_accuracy = (
        (sensitivity + specificity) / 2
        if sensitivity is not None and specificity is not None
        else None
    )
    return {
        "tp": tp,
        "fn": fn,
        "tn": tn,
        "fp": fp,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "precision": precision,
        "balanced_accuracy": balanced_accuracy,
    }


def development_reference() -> dict[str, Any]:
    rows = _development_rows()
    distributions = {
        feature: sorted(float(row[feature]) for row in rows if row[feature] is not None)
        for feature in PRIMARY_FEATURES
    }
    for row in rows:
        feature_payload = {feature: row[feature] for feature in PRIMARY_FEATURES}
        row["efgm_risk"] = _score_risk(feature_payload, distributions)
    digest = _canonical_hash(rows)
    if digest != DEVELOPMENT_ROWS_SHA256:
        raise RuntimeError(
            f"AH-EXP-0012 development rows changed: {digest} != {DEVELOPMENT_ROWS_SHA256}"
        )
    return {"rows": rows, "distributions": distributions, "sha256": digest}


def _append_detector_snapshot(detector: DetectorState, snapshot: DecisionSnapshot) -> None:
    detector.history.append(snapshot)
    if len(detector.history) > 3:
        detector.history.pop(0)


def run_holdout_trajectory(mu: float, *, controller: str) -> TrajectoryResult:
    if controller not in {PRIMARY_CONTROLLER, COMPARISON_CONTROLLER}:
        raise ValueError(f"unknown controller: {controller}")
    regulator = Regulator()
    telemetry = QueueTelemetry()
    detector = DetectorState()
    config = EnvironmentConfig()
    trace: list[StepTrace] = []
    interventions = 0
    executed_recoveries = 0
    completion_step: int | None = None
    first_recovery: int | None = None
    first_productive_after_recovery: int | None = None
    tau_escape: int | None = None
    escape_phase: str | None = None
    mechanism: str | None = None

    for t in range(HORIZON):
        if telemetry.completed or not telemetry.viable:
            break
        disturbance = holdout_disturbance_at(mu, t)
        resource_before = telemetry.resource
        backlog_before_arrival = telemetry.backlog
        work_before = telemetry.work_cleared
        telemetry.backlog = min(MAX_BACKLOG + 1, telemetry.backlog + _arrival(disturbance, t))
        backlog_after_arrival = telemetry.backlog
        if not telemetry.viable:
            tau_escape = t
            escape_phase = "post_arrival"
            mechanism = failure_mechanism(telemetry)
            trace.append(
                StepTrace(
                    controller=controller,
                    mu=mu,
                    t=t,
                    disturbance=disturbance,
                    resource_before=_norm(resource_before),
                    resource_after=_norm(telemetry.resource),
                    backlog_before_arrival=backlog_before_arrival,
                    backlog_after_arrival=backlog_after_arrival,
                    backlog_after_action=None,
                    work_cleared_before=work_before,
                    work_cleared_after=telemetry.work_cleared,
                    failures=telemetry.failures,
                    repeated_failures=telemetry.repeated_failures,
                    margin=None,
                    selected_mode=None,
                    executed_mode=None,
                    intervention=False,
                    action_succeeded=None,
                    completed=telemetry.completed,
                    viable=False,
                    escape_phase=escape_phase,
                )
            )
            break
        margin = regulator.margin(disturbance, telemetry.resource, telemetry.failures)
        telemetry.min_margin = min(telemetry.min_margin, margin)
        selected_mode = regulator.mode(margin)
        executed_mode = selected_mode
        intervention = False
        snapshot = DecisionSnapshot(
            selected_mode=selected_mode,
            work_cleared=telemetry.work_cleared,
            backlog=telemetry.backlog,
        )
        if (
            controller == PRIMARY_CONTROLLER
            and should_relax_robust(selected_mode, telemetry, detector, disturbance)
        ):
            executed_mode = Mode.NORMAL
            intervention = True
            interventions += 1
        telemetry.modes[executed_mode.value] += 1
        action_succeeded: bool | None = None
        if executed_mode is Mode.RECOVERY:
            executed_recoveries += 1
            if first_recovery is None:
                first_recovery = t
            _maintenance(telemetry, disturbance, config)
        else:
            failures_before = telemetry.failures
            work_before_action = telemetry.work_cleared
            backlog_before_action = telemetry.backlog
            _service(
                telemetry,
                disturbance,
                cautious=(executed_mode is Mode.CAUTION),
                step=t,
                config=config,
            )
            if backlog_before_action > 0:
                if telemetry.work_cleared > work_before_action:
                    action_succeeded = True
                elif telemetry.failures > failures_before:
                    action_succeeded = False
            if (
                first_recovery is not None
                and first_productive_after_recovery is None
                and action_succeeded is True
            ):
                first_productive_after_recovery = t
        _append_detector_snapshot(detector, snapshot)
        if telemetry.completed and completion_step is None:
            completion_step = t
        if not telemetry.viable and tau_escape is None:
            tau_escape = t
            escape_phase = "post_action"
            mechanism = failure_mechanism(telemetry)
        trace.append(
            StepTrace(
                controller=controller,
                mu=mu,
                t=t,
                disturbance=disturbance,
                resource_before=_norm(resource_before),
                resource_after=_norm(telemetry.resource),
                backlog_before_arrival=backlog_before_arrival,
                backlog_after_arrival=backlog_after_arrival,
                backlog_after_action=telemetry.backlog,
                work_cleared_before=work_before,
                work_cleared_after=telemetry.work_cleared,
                failures=telemetry.failures,
                repeated_failures=telemetry.repeated_failures,
                margin=_norm(margin),
                selected_mode=selected_mode.value,
                executed_mode=executed_mode.value,
                intervention=intervention,
                action_succeeded=action_succeeded,
                completed=telemetry.completed,
                viable=telemetry.viable,
                escape_phase=escape_phase if tau_escape == t else None,
            )
        )
        if telemetry.completed or not telemetry.viable:
            break

    horizon_reached = len(trace) == HORIZON and not telemetry.completed and telemetry.viable
    classification = classify_terminal(
        completed=telemetry.completed,
        viable=telemetry.viable,
        executed_recoveries=executed_recoveries,
        horizon_reached=horizon_reached,
    )
    tau_recovery = (
        None
        if first_recovery is None or first_productive_after_recovery is None
        else first_productive_after_recovery - first_recovery
    )
    return TrajectoryResult(
        controller=controller,
        mu=mu,
        classification=classification.value,
        completed=telemetry.completed,
        viable=telemetry.viable,
        completion_step=completion_step,
        executed_recoveries=executed_recoveries,
        interventions=interventions,
        t_first_recovery=first_recovery,
        t_first_productive_after_recovery=first_productive_after_recovery,
        tau_recovery=tau_recovery,
        tau_escape=tau_escape,
        escape_phase=escape_phase,
        failure_mechanism=mechanism,
        final_resource=_norm(telemetry.resource),
        final_backlog=telemetry.backlog,
        final_work_cleared=telemetry.work_cleared,
        trace=tuple(trace),
    )


def _baseline_predictions(row: StepTrace) -> dict[str, bool]:
    assert row.backlog_after_action is not None and row.margin is not None
    return {
        "backlog": row.backlog_after_action >= BASELINE_THRESHOLDS["backlog"],
        "resource": row.resource_after <= BASELINE_THRESHOLDS["resource"],
        "margin": row.margin <= BASELINE_THRESHOLDS["margin"],
        "disturbance": row.disturbance >= BASELINE_THRESHOLDS["disturbance"],
    }


def evaluate_holdout(*, controller: str = PRIMARY_CONTROLLER) -> dict[str, Any]:
    reference = development_reference()
    distributions = reference["distributions"]
    trajectories = tuple(run_holdout_trajectory(mu, controller=controller) for mu in mu_grid())
    prediction_rows: list[dict[str, Any]] = []
    trace_payload: list[dict[str, Any]] = []

    for trajectory in trajectories:
        previous: dict[str, float] | None = None
        for index, row in enumerate(trajectory.trace):
            trace_payload.append(asdict(row))
            if row.completed or not row.viable:
                continue
            base, provenance = _observer_base(trajectory.trace, index)
            features = _with_deltas(base, previous)
            previous = base
            risk = _score_risk(features, distributions)
            warning = risk is not None and risk >= EFGM_WARNING_THRESHOLD
            label = int(
                trajectory.tau_escape is not None
                and 1 <= trajectory.tau_escape - row.t <= 2
            )
            baselines = _baseline_predictions(row)
            prediction_rows.append(
                {
                    "controller": controller,
                    "mu": f"{trajectory.mu:.3f}",
                    "t": row.t,
                    "features": features,
                    "efgm_risk": risk,
                    "efgm_warn": warning,
                    "baseline_predictions": baselines,
                    "time_t_state": {
                        "backlog": row.backlog_after_action,
                        "resource": _norm(row.resource_after),
                        "margin": _norm(row.margin),
                        "disturbance": _norm(row.disturbance),
                        "selected_mode": row.selected_mode,
                        "executed_mode": row.executed_mode,
                        "failures": row.failures,
                        "repeated_failures": row.repeated_failures,
                    },
                    "provenance": provenance,
                    "y": label,
                }
            )

    efgm_confusion = _confusion(prediction_rows, "efgm_warn")
    baseline_confusions: dict[str, dict[str, Any]] = {}
    for baseline in BASELINE_THRESHOLDS:
        temp = [
            {**row, "_pred": bool(row["baseline_predictions"][baseline])}
            for row in prediction_rows
        ]
        baseline_confusions[baseline] = _confusion(temp, "_pred")

    escape_lead_times: list[int] = []
    detected_escapes = 0
    missed_escapes = 0
    for trajectory in trajectories:
        if trajectory.tau_escape is None:
            continue
        warnings = [
            row["t"]
            for row in prediction_rows
            if row["mu"] == f"{trajectory.mu:.3f}"
            and row["controller"] == controller
            and row["efgm_warn"]
            and row["t"] < trajectory.tau_escape
        ]
        if warnings:
            detected_escapes += 1
            escape_lead_times.append(trajectory.tau_escape - min(warnings))
        else:
            missed_escapes += 1

    best_baseline_ba = baseline_confusions[BEST_SINGLE_BASELINE]["balanced_accuracy"]
    efgm_ba = efgm_confusion["balanced_accuracy"]
    labels = {row["y"] for row in prediction_rows}
    delta_ba = None if efgm_ba is None or best_baseline_ba is None else efgm_ba - best_baseline_ba

    if labels != {0, 1}:
        status = "INCONCLUSIVE"
    else:
        survives = bool(
            efgm_ba is not None
            and efgm_ba > 0.50
            and delta_ba is not None
            and delta_ba >= 0.02
            and any(value >= 1 for value in escape_lead_times)
        )
        status = "SURVIVED" if survives else "FALSIFIED"

    ordered_result = {
        "experiment": EXPERIMENT_ID,
        "controller": controller,
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
        "warning_threshold": EFGM_WARNING_THRESHOLD,
        "baseline_thresholds": BASELINE_THRESHOLDS,
        "best_single_baseline": BEST_SINGLE_BASELINE,
        "holdout_modulation": list(HOLDOUT_MODULATION),
        "prediction_count": len(prediction_rows),
        "positive_label_count": sum(row["y"] for row in prediction_rows),
        "negative_label_count": sum(1 - row["y"] for row in prediction_rows),
        "efgm_confusion": efgm_confusion,
        "baseline_confusions": baseline_confusions,
        "delta_ba": delta_ba,
        "escape_trajectory_count": detected_escapes + missed_escapes,
        "detected_escape_count": detected_escapes,
        "missed_escape_count": missed_escapes,
        "lead_times": escape_lead_times,
        "prediction_rows": prediction_rows,
    }
    ordered_result["canonical_result_hash"] = _canonical_hash(ordered_result)
    ordered_result["full_trace_hash"] = _canonical_hash(trace_payload)
    return ordered_result


def structural_manifest() -> dict[str, Any]:
    return {
        "experiment": EXPERIMENT_ID,
        "phase": "observer_frozen_holdout_not_executed",
        "preregistration_freeze_sha": PREREGISTRATION_FREEZE_SHA,
        "ah_substrate_sha": AH_SUBSTRATE_SHA,
        "efgm_code_sha": EFGM_CODE_SHA,
        "adapter_id": ADAPTER_ID,
        "history_window": HISTORY_WINDOW,
        "primary_features": list(PRIMARY_FEATURES),
        "warning_threshold": EFGM_WARNING_THRESHOLD,
        "baseline_thresholds": dict(BASELINE_THRESHOLDS),
        "best_single_baseline": BEST_SINGLE_BASELINE,
        "development_rows_sha256": DEVELOPMENT_ROWS_SHA256,
        "holdout_cycle_length": len(HOLDOUT_MODULATION),
        "holdout_outcomes_observed": False,
    }
