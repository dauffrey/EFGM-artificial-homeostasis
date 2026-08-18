from __future__ import annotations

import json
import random
from dataclasses import dataclass
from statistics import mean

from .adversarial_robustness import EnvironmentConfig, _arrival, _maintenance, _service, utility
from .core import Mode, Regulator
from .queue_replication import MAX_BACKLOG, QueueTelemetry, summary


HOLDOUT_SEED = 8009
HOLDOUT_CANDIDATES = 512
PROTECTIVE_STREAK = 4
MIN_RESOURCE_TO_RELAX = 0.30
MIN_BACKLOG_TO_RELAX = 2


@dataclass
class DetectorState:
    protective_streak: int = 0
    interventions: int = 0


def holdout_candidates() -> list[list[float]]:
    rng = random.Random(HOLDOUT_SEED)
    candidates: list[list[float]] = []
    while len(candidates) < HOLDOUT_CANDIDATES:
        candidate = [rng.random() for _ in range(12)]
        high_count = sum(value > 0.80 for value in candidate)
        avg = sum(candidate) / len(candidate)
        if high_count <= 6 and 0.25 <= avg <= 0.70:
            candidates.append(candidate)
    return candidates


def should_relax(mode: Mode, telemetry: QueueTelemetry, state: DetectorState) -> bool:
    protective = mode in (Mode.CAUTION, Mode.RECOVERY)
    state.protective_streak = state.protective_streak + 1 if protective else 0
    return (
        state.protective_streak >= PROTECTIVE_STREAK
        and telemetry.resource >= MIN_RESOURCE_TO_RELAX
        and telemetry.backlog >= MIN_BACKLOG_TO_RELAX
    )


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
        mode = regulator.mode(margin)

        relax = should_relax(mode, telemetry, detector)
        if enabled and relax:
            mode = Mode.NORMAL
            detector.interventions += 1
            detector.protective_streak = 0

        telemetry.modes[mode.value] += 1
        if mode is Mode.RECOVERY:
            _maintenance(telemetry, disturbance, config)
        else:
            _service(telemetry, disturbance, cautious=(mode is Mode.CAUTION), step=step, config=config)

    return telemetry, detector.interventions


def _row(schedule: list[float]) -> dict:
    frozen_t, _ = run_with_detector(schedule, enabled=False)
    adaptive_t, interventions = run_with_detector(schedule, enabled=True)
    frozen = summary(frozen_t)
    adaptive = summary(adaptive_t)
    return {
        "frozen": frozen,
        "adaptive": adaptive,
        "interventions": interventions,
        "utility": {
            "frozen": utility(frozen),
            "adaptive": utility(adaptive),
        },
    }


def run_all() -> dict:
    rows = [_row(schedule) for schedule in holdout_candidates()]
    frozen_completion = sum(int(row["frozen"]["completed"]) for row in rows)
    adaptive_completion = sum(int(row["adaptive"]["completed"]) for row in rows)
    frozen_viability = sum(int(row["frozen"]["viable"]) for row in rows)
    adaptive_viability = sum(int(row["adaptive"]["viable"]) for row in rows)
    frozen_utility = sum(row["utility"]["frozen"] for row in rows)
    adaptive_utility = sum(row["utility"]["adaptive"] for row in rows)
    interventions = sum(row["interventions"] for row in rows)

    adaptive_wins = sum(row["utility"]["adaptive"] > row["utility"]["frozen"] for row in rows)
    frozen_wins = sum(row["utility"]["frozen"] > row["utility"]["adaptive"] for row in rows)

    return {
        "experiment": "AH-EXP-0008",
        "holdout_seed": HOLDOUT_SEED,
        "candidate_count": HOLDOUT_CANDIDATES,
        "detector": {
            "protective_streak": PROTECTIVE_STREAK,
            "min_resource_to_relax": MIN_RESOURCE_TO_RELAX,
            "min_backlog_to_relax": MIN_BACKLOG_TO_RELAX,
        },
        "aggregate": {
            "frozen": {
                "completed": frozen_completion,
                "viable": frozen_viability,
                "total_utility": frozen_utility,
            },
            "adaptive": {
                "completed": adaptive_completion,
                "viable": adaptive_viability,
                "total_utility": adaptive_utility,
                "interventions": interventions,
            },
            "paired_wins": {
                "adaptive": adaptive_wins,
                "frozen": frozen_wins,
                "ties": len(rows) - adaptive_wins - frozen_wins,
            },
            "mean_interventions": mean(row["interventions"] for row in rows),
        },
        "falsification": {
            "adaptive_completion_not_greater": adaptive_completion <= frozen_completion,
            "adaptive_utility_not_greater": adaptive_utility <= frozen_utility,
            "adaptive_viability_loss_exceeds_5_percent": adaptive_viability < frozen_viability - 0.05 * HOLDOUT_CANDIDATES,
            "detector_never_intervenes": interventions == 0,
            "post_outcome_retuning_required": False,
        },
    }


def main() -> None:
    print(json.dumps(run_all(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
