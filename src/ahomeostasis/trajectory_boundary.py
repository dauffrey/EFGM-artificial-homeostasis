from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable, Sequence

from .adversarial_robustness import EnvironmentConfig, _arrival, _maintenance, _service
from .core import Mode, Regulator
from .counterfactual_regulation import DecisionSnapshot, DetectorState
from .queue_replication import MAX_BACKLOG, QueueTelemetry
from .robust_counterfactual_abstention import should_relax_robust


EXPERIMENT_ID = "AH-EXP-0011"
PREREGISTRATION_BASELINE_SHA = "0baeab969e17374966ab8e7b400405e6eb576c56"
PRIMARY_CONTROLLER = "robust_counterfactual_abstention"
COMPARISON_CONTROLLER = "coupled_margin"
MU_STEP = 0.005
MU_COUNT = 201
HORIZON = 100
MODULATION = (
    -0.12,
    -0.08,
    -0.04,
    0.00,
    0.04,
    0.08,
    0.12,
    0.08,
    0.04,
    0.00,
    -0.04,
    -0.08,
)


class TrajectoryClass(str, Enum):
    STABLE = "STABLE"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"
    CENSORED = "CENSORED"


@dataclass(frozen=True)
class StepTrace:
    controller: str
    mu: float
    t: int
    disturbance: float
    resource_before: float
    resource_after: float
    backlog_before_arrival: int
    backlog_after_arrival: int
    backlog_after_action: int | None
    work_cleared_before: int
    work_cleared_after: int
    failures: int
    repeated_failures: int
    margin: float | None
    selected_mode: str | None
    executed_mode: str | None
    intervention: bool
    action_succeeded: bool | None
    completed: bool
    viable: bool
    escape_phase: str | None


@dataclass(frozen=True)
class TrajectoryResult:
    controller: str
    mu: float
    classification: str
    completed: bool
    viable: bool
    completion_step: int | None
    executed_recoveries: int
    interventions: int
    t_first_recovery: int | None
    t_first_productive_after_recovery: int | None
    tau_recovery: int | None
    tau_escape: int | None
    escape_phase: str | None
    failure_mechanism: str | None
    final_resource: float
    final_backlog: int
    final_work_cleared: int
    trace: tuple[StepTrace, ...]


@dataclass(frozen=True)
class SweepResult:
    experiment: str
    controller: str
    preregistration_baseline_sha: str
    trajectory_count: int
    class_counts: dict[str, int]
    boundaries: tuple[dict[str, str], ...]
    canonical_result_hash: str
    trajectories: tuple[TrajectoryResult, ...]


def _norm(value: float) -> float:
    return round(float(value), 12)


def mu_grid() -> tuple[float, ...]:
    """Return the frozen 201-value preregistered base-disturbance grid."""
    return tuple(round(index * MU_STEP, 3) for index in range(MU_COUNT))


def disturbance_at(mu: float, t: int) -> float:
    """Return the frozen modulated disturbance for one step."""
    if not 0.0 <= mu <= 1.0:
        raise ValueError("mu must be within [0, 1]")
    disturbance = mu + MODULATION[t % len(MODULATION)]
    return _norm(min(1.0, max(0.0, disturbance)))


def classify_terminal(
    *,
    completed: bool,
    viable: bool,
    executed_recoveries: int,
    horizon_reached: bool,
) -> TrajectoryClass:
    """Apply only the frozen AH-EXP-0011 classification rules.

    A simultaneous completed/non-viable terminal state is intentionally not
    reinterpreted here because the preregistration does not assign that state to a
    class. If it occurs in canonical validation it must remain an unclassifiable
    outcome rather than being silently post-hoc assigned.
    """
    if completed and viable:
        return TrajectoryClass.RECOVERED if executed_recoveries >= 1 else TrajectoryClass.STABLE
    if not completed and not viable:
        return TrajectoryClass.FAILED
    if not completed and viable and horizon_reached:
        return TrajectoryClass.CENSORED
    raise ValueError(
        "Terminal state is not classifiable under the frozen AH-EXP-0011 rules: "
        f"completed={completed}, viable={viable}, "
        f"executed_recoveries={executed_recoveries}, horizon_reached={horizon_reached}"
    )


def failure_mechanism(telemetry: QueueTelemetry) -> str | None:
    resource_failed = telemetry.resource <= 0.0
    backlog_failed = telemetry.backlog > MAX_BACKLOG
    if resource_failed and backlog_failed:
        return "both"
    if resource_failed:
        return "resource_depletion"
    if backlog_failed:
        return "backlog_overflow"
    return None


def _append_detector_snapshot(detector: DetectorState, snapshot: DecisionSnapshot) -> None:
    detector.history.append(snapshot)
    if len(detector.history) > 3:
        detector.history.pop(0)


def run_trajectory(mu: float, *, controller: str) -> TrajectoryResult:
    """Execute one preregistered AH-EXP-0011 trajectory.

    This function is the canonical trajectory engine. Structural tests must not call
    it with values from the frozen validation grid before implementation review and
    exact-head CI are complete.
    """
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
    t_first_recovery: int | None = None
    t_first_productive_after_recovery: int | None = None
    tau_escape: int | None = None
    escape_phase: str | None = None
    mechanism: str | None = None

    for t in range(HORIZON):
        if telemetry.completed or not telemetry.viable:
            break

        disturbance = disturbance_at(mu, t)
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

        current_snapshot = DecisionSnapshot(
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
            if t_first_recovery is None:
                t_first_recovery = t
            _maintenance(telemetry, disturbance, config)
        else:
            failures_before_action = telemetry.failures
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
                elif telemetry.failures > failures_before_action:
                    action_succeeded = False

            if (
                t_first_recovery is not None
                and t_first_productive_after_recovery is None
                and action_succeeded is True
                and telemetry.work_cleared > work_before_action
            ):
                t_first_productive_after_recovery = t

        _append_detector_snapshot(detector, current_snapshot)

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

    tau_recovery = None
    if t_first_recovery is not None and t_first_productive_after_recovery is not None:
        tau_recovery = t_first_productive_after_recovery - t_first_recovery

    return TrajectoryResult(
        controller=controller,
        mu=mu,
        classification=classification.value,
        completed=telemetry.completed,
        viable=telemetry.viable,
        completion_step=completion_step,
        executed_recoveries=executed_recoveries,
        interventions=interventions,
        t_first_recovery=t_first_recovery,
        t_first_productive_after_recovery=t_first_productive_after_recovery,
        tau_recovery=tau_recovery,
        tau_escape=tau_escape,
        escape_phase=escape_phase,
        failure_mechanism=mechanism,
        final_resource=_norm(telemetry.resource),
        final_backlog=telemetry.backlog,
        final_work_cleared=telemetry.work_cleared,
        trace=tuple(trace),
    )


def boundary_intervals(
    classifications: Sequence[tuple[float, str]],
) -> tuple[dict[str, str], ...]:
    boundaries: list[dict[str, str]] = []
    for (left_mu, left_class), (right_mu, right_class) in zip(
        classifications,
        classifications[1:],
    ):
        if left_class != right_class:
            boundaries.append(
                {
                    "lower_mu": f"{left_mu:.3f}",
                    "upper_mu": f"{right_mu:.3f}",
                    "from_class": left_class,
                    "to_class": right_class,
                }
            )
    return tuple(boundaries)


def canonical_row(result: TrajectoryResult) -> dict:
    """Canonical summary row used for exact deterministic reproducibility hashing."""
    return {
        "controller": result.controller,
        "mu": f"{result.mu:.3f}",
        "classification": result.classification,
        "completed": result.completed,
        "viable": result.viable,
        "completion_step": result.completion_step,
        "executed_recoveries": result.executed_recoveries,
        "interventions": result.interventions,
        "t_first_recovery": result.t_first_recovery,
        "t_first_productive_after_recovery": result.t_first_productive_after_recovery,
        "tau_recovery": result.tau_recovery,
        "tau_escape": result.tau_escape,
        "escape_phase": result.escape_phase,
        "failure_mechanism": result.failure_mechanism,
        "final_resource": _norm(result.final_resource),
        "final_backlog": result.final_backlog,
        "final_work_cleared": result.final_work_cleared,
    }


def canonical_result_hash(rows: Iterable[dict]) -> str:
    payload = json.dumps(list(rows), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def run_sweep(*, controller: str) -> SweepResult:
    trajectories = tuple(run_trajectory(mu, controller=controller) for mu in mu_grid())
    classifications = tuple((row.mu, row.classification) for row in trajectories)
    boundaries = boundary_intervals(classifications)
    counts = {trajectory_class.value: 0 for trajectory_class in TrajectoryClass}
    for row in trajectories:
        counts[row.classification] += 1
    digest = canonical_result_hash(canonical_row(row) for row in trajectories)
    return SweepResult(
        experiment=EXPERIMENT_ID,
        controller=controller,
        preregistration_baseline_sha=PREREGISTRATION_BASELINE_SHA,
        trajectory_count=len(trajectories),
        class_counts=counts,
        boundaries=boundaries,
        canonical_result_hash=digest,
        trajectories=trajectories,
    )


def run_canonical_validation() -> dict[str, SweepResult]:
    """Execute both frozen AH-EXP-0011 sweeps.

    Do not call this during implementation construction or structural CI. It is
    intentionally exposed as a pure API for the later canonical validation step.
    """
    return {
        PRIMARY_CONTROLLER: run_sweep(controller=PRIMARY_CONTROLLER),
        COMPARISON_CONTROLLER: run_sweep(controller=COMPARISON_CONTROLLER),
    }


def structural_manifest() -> dict:
    """Return design identity without executing any validation trajectory."""
    return {
        "experiment": EXPERIMENT_ID,
        "phase": "implementation_structure_only",
        "preregistration_baseline_sha": PREREGISTRATION_BASELINE_SHA,
        "primary_controller": PRIMARY_CONTROLLER,
        "comparison_controller": COMPARISON_CONTROLLER,
        "mu_step": MU_STEP,
        "mu_count": MU_COUNT,
        "horizon": HORIZON,
        "modulation": list(MODULATION),
        "validation_outcomes_observed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", action="store_true")
    args = parser.parse_args()
    if not args.manifest:
        raise SystemExit(
            "AH-EXP-0011 canonical validation is intentionally unavailable from the CLI "
            "during implementation construction; use --manifest for structure-only output"
        )
    print(json.dumps(structural_manifest(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
