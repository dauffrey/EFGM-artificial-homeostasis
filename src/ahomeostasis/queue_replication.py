from __future__ import annotations

from dataclasses import dataclass, field
import json

from .ablation import NoCoupledMarginRegulator
from .attack import score
from .core import Mode, Regulator


SCHEDULES = {
    "bursty_arrivals": [0.12, 0.18, 0.76, 0.82, 0.24, 0.20, 0.78, 0.84, 0.22, 0.18, 0.14, 0.12],
    "sustained_pressure": [0.18, 0.28, 0.44, 0.62, 0.72, 0.76, 0.74, 0.68, 0.52, 0.36, 0.24, 0.16],
    "alternating_load": [0.16, 0.70, 0.20, 0.74, 0.18, 0.78, 0.22, 0.72, 0.20, 0.68, 0.16, 0.14],
    "late_surge": [0.12, 0.14, 0.16, 0.18, 0.20, 0.26, 0.34, 0.48, 0.70, 0.82, 0.86, 0.74],
}

TARGET_WORK = 8
INITIAL_BACKLOG = 8
MAX_BACKLOG = 12


@dataclass
class QueueTelemetry:
    backlog: int = INITIAL_BACKLOG
    work_cleared: int = 0
    resource: float = 1.0
    failures: int = 0
    repeated_failures: int = 0
    recoveries: int = 0
    last_action_failed: bool = False
    min_margin: float = 1.0
    modes: dict[str, int] = field(default_factory=lambda: {m.value: 0 for m in Mode})

    @property
    def progress(self) -> float:
        return min(1.0, self.work_cleared / TARGET_WORK)

    @property
    def completed(self) -> bool:
        return self.work_cleared >= TARGET_WORK

    @property
    def viable(self) -> bool:
        return self.resource > 0.0 and self.backlog <= MAX_BACKLOG


def _arrival(disturbance: float, step: int) -> int:
    # Disturbance affects queue pressure rather than directly changing progress.
    if disturbance >= 0.78:
        return 2
    if disturbance >= 0.58 and step % 2 == 0:
        return 1
    return 0


def _service(t: QueueTelemetry, disturbance: float, cautious: bool, step: int) -> None:
    if t.backlog <= 0:
        return

    success_threshold = 0.80 if cautious else 0.58
    succeeded = disturbance <= success_threshold
    base_cost = 0.055 if cautious else 0.085
    stress_cost = disturbance * (0.045 if cautious else 0.12)
    failure_penalty = 0.0 if succeeded else (0.055 if cautious else 0.14)
    t.resource = max(0.0, t.resource - base_cost - stress_cost - failure_penalty)

    if succeeded:
        units = 1 if cautious else 2
        cleared = min(units, t.backlog)
        t.backlog -= cleared
        t.work_cleared += cleared
        t.last_action_failed = False
    else:
        t.failures += 1
        if t.last_action_failed:
            t.repeated_failures += 1
        t.last_action_failed = True
        # Failed service can requeue work under heavy pressure.
        if disturbance >= 0.75 and step % 2 == 1:
            t.backlog = min(MAX_BACKLOG + 1, t.backlog + 1)


def _maintenance(t: QueueTelemetry, disturbance: float) -> None:
    t.recoveries += 1
    t.resource = min(1.0, t.resource + max(0.025, 0.11 * (1.0 - disturbance)))
    t.last_action_failed = False


def run_controller(schedule: list[float], regulator: Regulator) -> QueueTelemetry:
    t = QueueTelemetry()
    for step, disturbance in enumerate(schedule):
        if t.completed or not t.viable:
            break

        t.backlog = min(MAX_BACKLOG + 1, t.backlog + _arrival(disturbance, step))
        if not t.viable:
            break

        margin = regulator.margin(disturbance, t.resource, t.failures)
        t.min_margin = min(t.min_margin, margin)
        mode = regulator.mode(margin)
        t.modes[mode.value] += 1

        if mode is Mode.RECOVERY:
            _maintenance(t, disturbance)
        else:
            _service(t, disturbance, cautious=(mode is Mode.CAUTION), step=step)

    return t


def summary(t: QueueTelemetry) -> dict:
    return {
        "completed": t.completed,
        "viable": t.viable,
        "progress": t.progress,
        "work_cleared": t.work_cleared,
        "backlog": t.backlog,
        "resource": t.resource,
        "resource_consumed": 1.0 - t.resource,
        "failures": t.failures,
        "repeated_failures": t.repeated_failures,
        "recoveries": t.recoveries,
        "min_margin": t.min_margin,
        "modes": dict(t.modes),
    }


def run_all() -> dict:
    controllers = {
        "full": Regulator,
        "no_coupled_margin": NoCoupledMarginRegulator,
    }
    results: dict[str, dict[str, dict]] = {}
    for schedule_name, schedule in SCHEDULES.items():
        results[schedule_name] = {
            name: summary(run_controller(schedule, factory()))
            for name, factory in controllers.items()
        }

    scores = score(results)
    full_viable = sum(int(results[name]["full"]["viable"]) for name in SCHEDULES)
    uncoupled_only_completion = sum(
        int(results[name]["no_coupled_margin"]["completed"] and not results[name]["full"]["completed"])
        for name in SCHEDULES
    )

    return {
        "experiment": "AH-EXP-0005",
        "environment": "bounded_queue_service",
        "results": results,
        "scores": scores,
        "falsification": {
            "uncoupled_matches_or_exceeds_full": scores["no_coupled_margin"] >= scores["full"],
            "full_viable_on_fewer_than_3_schedules": full_viable < 3,
            "uncoupled_completes_two_where_full_fails": uncoupled_only_completion >= 2,
            "post_outcome_retuning_required": False,
        },
    }


def main() -> None:
    print(json.dumps(run_all(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
