from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass, field
from statistics import mean

from .adversarial_robustness import EnvironmentConfig, _arrival, _maintenance, _service
from .core import Mode, Regulator
from .queue_replication import MAX_BACKLOG, QueueTelemetry

CALIBRATION_SEED = 9001
CALIBRATION_CANDIDATES = 256
HOLDOUT_SEED = 9011
HOLDOUT_CANDIDATES = 512
SCHEDULE_LENGTH = 12
RESOURCE_FLOOR = 0.40
BACKLOG_FLOOR = 3
CF_THRESHOLD = 0.50
RESOURCE_COST_WEIGHT = 2.0
NORMAL_FAILURE_PENALTY = 0.75


@dataclass(frozen=True)
class DecisionSnapshot:
    selected_mode: Mode
    work_cleared: int
    backlog: int


@dataclass
class DetectorState:
    history: list[DecisionSnapshot] = field(default_factory=list)
    interventions: int = 0


def bounded_candidates(seed: int, count: int) -> list[list[float]]:
    rng = random.Random(seed)
    candidates: list[list[float]] = []
    while len(candidates) < count:
        candidate = [rng.random() for _ in range(SCHEDULE_LENGTH)]
        high_count = sum(value > 0.80 for value in candidate)
        avg = sum(candidate) / len(candidate)
        if high_count <= 6 and 0.25 <= avg <= 0.70:
            candidates.append(candidate)
    return candidates


def calibration_candidates() -> list[list[float]]:
    return bounded_candidates(CALIBRATION_SEED, CALIBRATION_CANDIDATES)


def holdout_candidates() -> list[list[float]]:
    return bounded_candidates(HOLDOUT_SEED, HOLDOUT_CANDIDATES)


def _normal_prediction(disturbance: float) -> tuple[int, float, int]:
    failure = int(disturbance > 0.58)
    units = 0 if failure else 2
    cost = 0.085 + 0.12 * disturbance + (0.14 if failure else 0.0)
    return units, cost, failure


def _selected_prediction(mode: Mode, disturbance: float) -> tuple[int, float]:
    if mode is Mode.CAUTION:
        failure = disturbance > 0.80
        units = 0 if failure else 1
        cost = 0.055 + 0.045 * disturbance + (0.055 if failure else 0.0)
        return units, cost
    if mode is Mode.RECOVERY:
        gain = max(0.025, 0.11 * (1.0 - disturbance))
        return 0, -gain
    raise ValueError("counterfactual is defined only for protective actions")


def counterfactual_advantage(mode: Mode, disturbance: float) -> float:
    normal_units, normal_cost, normal_failure = _normal_prediction(disturbance)
    selected_units, selected_cost = _selected_prediction(mode, disturbance)
    progress_gain = normal_units - selected_units
    excess_resource_cost = normal_cost - selected_cost
    return (
        progress_gain
        - RESOURCE_COST_WEIGHT * excess_resource_cost
        - NORMAL_FAILURE_PENALTY * normal_failure
    )


def should_relax(
    mode: Mode,
    telemetry: QueueTelemetry,
    state: DetectorState,
    disturbance: float,
) -> bool:
    if mode not in (Mode.CAUTION, Mode.RECOVERY):
        return False
    if len(state.history) < 2:
        return False

    two_steps_ago = state.history[-2]
    recent_modes = [snapshot.selected_mode for snapshot in state.history[-2:]] + [mode]
    protective_count = sum(m in (Mode.CAUTION, Mode.RECOVERY) for m in recent_modes)
    if protective_count < 2:
        return False

    if telemetry.work_cleared - two_steps_ago.work_cleared > 1:
        return False
    if telemetry.backlog < BACKLOG_FLOOR:
        return False
    if telemetry.backlog < two_steps_ago.backlog:
        return False
    if telemetry.resource < RESOURCE_FLOOR:
        return False

    return counterfactual_advantage(mode, disturbance) >= CF_THRESHOLD


def run_with_detector(schedule: list[float], enabled: bool) -> tuple[QueueTelemetry, int]:
    regulator = Regulator()
    telemetry = QueueTelemetry()
    detector = DetectorState()
    config = EnvironmentConfig()

    for step, disturbance in enumerate(schedule):
        if telemetry.completed or not telemetry.viable:
            break

        telemetry.backlog = min(MAX_BACKLOG + 1, telemetry.backlog + _arrival(disturbance, step))
        if not telemetry.viable:
            break

        margin = regulator.margin(disturbance, telemetry.resource, telemetry.failures)
        telemetry.min_margin = min(telemetry.min_margin, margin)
        selected_mode = regulator.mode(margin)
        executed_mode = selected_mode

        if enabled and should_relax(selected_mode, telemetry, detector, disturbance):
            executed_mode = Mode.NORMAL
            detector.interventions += 1

        telemetry.modes[executed_mode.value] += 1
        if executed_mode is Mode.RECOVERY:
            _maintenance(telemetry, disturbance, config)
        else:
            _service(
                telemetry,
                disturbance,
                cautious=(executed_mode is Mode.CAUTION),
                step=step,
                config=config,
            )

        detector.history.append(
            DecisionSnapshot(
                selected_mode=selected_mode,
                work_cleared=telemetry.work_cleared,
                backlog=telemetry.backlog,
            )
        )
        if len(detector.history) > 3:
            detector.history.pop(0)

    return telemetry, detector.interventions


def calibration_structural_validation() -> dict:
    schedules = calibration_candidates()
    interventions = []
    protective_trajectories = 0
    nonprotective_trajectories = 0
    for schedule in schedules:
        telemetry, count = run_with_detector(schedule, enabled=True)
        interventions.append(count)
        protective_steps = telemetry.modes[Mode.CAUTION.value] + telemetry.modes[Mode.RECOVERY.value]
        if protective_steps > 0:
            protective_trajectories += 1
        if telemetry.modes[Mode.NORMAL.value] > 0:
            nonprotective_trajectories += 1

    return {
        "experiment": "AH-EXP-0009",
        "phase": "calibration_structural_validation_only",
        "calibration_seed": CALIBRATION_SEED,
        "candidate_count": len(schedules),
        "detector_interventions": sum(interventions),
        "mean_interventions": mean(interventions),
        "protective_trajectories": protective_trajectories,
        "trajectories_with_normal_actions": nonprotective_trajectories,
        "holdout_seed": HOLDOUT_SEED,
        "holdout_outcomes_observed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--calibration-only", action="store_true")
    args = parser.parse_args()
    if not args.calibration_only:
        raise SystemExit("AH-EXP-0009 final holdout execution is intentionally disabled in this implementation phase")
    print(json.dumps(calibration_structural_validation(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
