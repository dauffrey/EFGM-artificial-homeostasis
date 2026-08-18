from __future__ import annotations

import json

from .core import Mode, Regulator, Telemetry, apply_action, recover
from .experiment import environment_step, summary
from .attack import SCHEDULES, score


class NoResourceAwarenessRegulator(Regulator):
    def margin(self, disturbance: float, resource: float, failures: int) -> float:
        self.recovery_capacity = max(0.0, 1.0 / (1.0 + failures))
        return self.recovery_capacity - disturbance


class NoFailureHistoryRegulator(Regulator):
    def margin(self, disturbance: float, resource: float, failures: int) -> float:
        self.recovery_capacity = max(0.0, resource)
        return self.recovery_capacity - disturbance


class NoCoupledMarginRegulator(Regulator):
    def margin(self, disturbance: float, resource: float, failures: int) -> float:
        self.recovery_capacity = max(0.0, 0.65 * resource + 0.35 * (1.0 / (1.0 + failures)))
        return self.recovery_capacity


def run_with_regulator(schedule: list[float], regulator: Regulator, *, allow_recovery: bool = True) -> Telemetry:
    t = Telemetry()
    for disturbance in schedule:
        if not t.viable or t.progress >= 0.75:
            break
        margin = regulator.margin(disturbance, t.resource, t.failures)
        t.min_margin = min(t.min_margin, margin)
        mode = regulator.mode(margin)

        if mode is Mode.RECOVERY and not allow_recovery:
            mode = Mode.CAUTION

        t.modes[mode.value] += 1

        if mode is Mode.RECOVERY:
            recover(t, disturbance)
            continue

        apply_action(t, environment_step(disturbance, cautious=(mode is Mode.CAUTION)))
    return t


def run_all() -> dict:
    controllers = {
        "full": lambda schedule: run_with_regulator(schedule, Regulator()),
        "no_recovery_action": lambda schedule: run_with_regulator(schedule, Regulator(), allow_recovery=False),
        "no_resource_awareness": lambda schedule: run_with_regulator(schedule, NoResourceAwarenessRegulator()),
        "no_failure_history": lambda schedule: run_with_regulator(schedule, NoFailureHistoryRegulator()),
        "no_coupled_margin": lambda schedule: run_with_regulator(schedule, NoCoupledMarginRegulator()),
    }

    results: dict[str, dict[str, dict]] = {}
    for schedule_name, schedule in SCHEDULES.items():
        results[schedule_name] = {
            controller_name: summary(runner(schedule))
            for controller_name, runner in controllers.items()
        }

    totals = score(results)
    full_score = totals["full"]
    matched_or_exceeded = [
        name for name, value in totals.items()
        if name != "full" and value >= full_score
    ]

    return {
        "experiment": "AH-EXP-0003",
        "results": results,
        "scores": totals,
        "falsification": {
            "single_ablation_matches_or_exceeds_full": bool(matched_or_exceeded),
            "matching_ablations": matched_or_exceeded,
        },
    }


def main() -> None:
    print(json.dumps(run_all(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
