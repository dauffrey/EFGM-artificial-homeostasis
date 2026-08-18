from __future__ import annotations

import json
from dataclasses import asdict

from .core import Mode, Regulator, StepObservation, Telemetry, apply_action, recover

DISTURBANCE = [0.05, 0.10, 0.20, 0.35, 0.55, 0.70, 0.85, 0.65, 0.45, 0.25, 0.10]


def environment_step(disturbance: float, cautious: bool = False) -> StepObservation:
    """Deterministic environment: higher disturbance makes normal actions fail/cost more.

    Cautious actions trade speed for lower cost and improved success under moderate stress.
    """
    threshold = 0.78 if cautious else 0.50
    success = disturbance < threshold
    if cautious:
        cost = 0.055 + 0.04 * disturbance
        progress = 0.07 if success else 0.0
    else:
        cost = 0.075 + 0.07 * disturbance
        progress = 0.12 if success else 0.0
    return StepObservation(disturbance, success, cost, progress)


def run_baseline(schedule: list[float] = DISTURBANCE) -> Telemetry:
    t = Telemetry()
    for disturbance in schedule:
        if not t.viable or t.progress >= 0.75:
            break
        t.modes[Mode.NORMAL.value] += 1
        apply_action(t, environment_step(disturbance, cautious=False))
    return t


def run_homeostatic(schedule: list[float] = DISTURBANCE) -> Telemetry:
    t = Telemetry()
    regulator = Regulator()
    for disturbance in schedule:
        if not t.viable or t.progress >= 0.75:
            break
        margin = regulator.margin(disturbance, t.resource, t.failures)
        t.min_margin = min(t.min_margin, margin)
        mode = regulator.mode(margin)
        t.modes[mode.value] += 1

        if mode is Mode.RECOVERY:
            recover(t, disturbance)
            continue

        cautious = mode is Mode.CAUTION
        apply_action(t, environment_step(disturbance, cautious=cautious))
    return t


def summary(t: Telemetry) -> dict:
    result = asdict(t)
    result["viable"] = t.viable
    result["completed"] = t.progress >= 0.75
    result["resource_consumed"] = 1.0 - t.resource
    return result


def main() -> None:
    print(json.dumps({
        "experiment": "AH-EXP-0001",
        "schedule": DISTURBANCE,
        "baseline": summary(run_baseline()),
        "homeostatic": summary(run_homeostatic()),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
