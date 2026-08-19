from __future__ import annotations

import argparse
import json
from statistics import mean

from .adversarial_robustness import EnvironmentConfig, _arrival, _maintenance, _service
from .core import Mode, Regulator
from .counterfactual_regulation import (
    BACKLOG_FLOOR,
    CF_THRESHOLD,
    DecisionSnapshot,
    DetectorState,
    RESOURCE_FLOOR,
    bounded_candidates,
    counterfactual_advantage,
)
from .queue_replication import MAX_BACKLOG, QueueTelemetry

STRUCTURAL_SEED = 10010
STRUCTURAL_CANDIDATES = 256
HOLDOUT_SEED = 10011
HOLDOUT_CANDIDATES = 512
UNCERTAINTY_WIDTH = 0.08


def structural_candidates() -> list[list[float]]:
    return bounded_candidates(STRUCTURAL_SEED, STRUCTURAL_CANDIDATES)


def bounded_views(disturbance: float) -> tuple[float, float, float]:
    return (
        max(0.0, disturbance - UNCERTAINTY_WIDTH),
        disturbance,
        min(1.0, disturbance + UNCERTAINTY_WIDTH),
    )


def robust_counterfactual_advantage(mode: Mode, disturbance: float) -> float:
    return min(counterfactual_advantage(mode, d) for d in bounded_views(disturbance))


def should_relax_robust(
    mode: Mode,
    telemetry: QueueTelemetry,
    state: DetectorState,
    disturbance: float,
) -> bool:
    # AH-EXP-0009 trajectory gates are intentionally unchanged.
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

    return robust_counterfactual_advantage(mode, disturbance) >= CF_THRESHOLD


def run_with_robust_abstention(schedule: list[float], enabled: bool) -> tuple[QueueTelemetry, int]:
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

        current_snapshot = DecisionSnapshot(
            selected_mode=selected_mode,
            work_cleared=telemetry.work_cleared,
            backlog=telemetry.backlog,
        )

        if enabled and should_relax_robust(selected_mode, telemetry, detector, disturbance):
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

        detector.history.append(current_snapshot)
        if len(detector.history) > 3:
            detector.history.pop(0)

    return telemetry, detector.interventions


def structural_validation() -> dict:
    schedules = structural_candidates()
    interventions: list[int] = []
    protective_trajectories = 0
    normal_trajectories = 0

    for schedule in schedules:
        telemetry, count = run_with_robust_abstention(schedule, enabled=True)
        interventions.append(count)
        if telemetry.modes[Mode.CAUTION.value] + telemetry.modes[Mode.RECOVERY.value] > 0:
            protective_trajectories += 1
        if telemetry.modes[Mode.NORMAL.value] > 0:
            normal_trajectories += 1

    return {
        "experiment": "AH-EXP-0010",
        "phase": "structural_validation_only",
        "structural_seed": STRUCTURAL_SEED,
        "candidate_count": len(schedules),
        "uncertainty_width": UNCERTAINTY_WIDTH,
        "threshold": CF_THRESHOLD,
        "detector_interventions": sum(interventions),
        "mean_interventions": mean(interventions),
        "protective_trajectories": protective_trajectories,
        "trajectories_with_normal_actions": normal_trajectories,
        "holdout_seed": HOLDOUT_SEED,
        "holdout_candidate_count": HOLDOUT_CANDIDATES,
        "holdout_outcomes_observed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structural-only", action="store_true")
    args = parser.parse_args()
    if not args.structural_only:
        raise SystemExit(
            "AH-EXP-0010 final holdout execution is intentionally unavailable during structural validation"
        )
    print(json.dumps(structural_validation(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
