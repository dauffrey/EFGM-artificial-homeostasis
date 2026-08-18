from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .core import Mode, Regulator, Telemetry, apply_action, recover
from .experiment import environment_step


SCHEDULES: dict[str, list[float]] = {
    "spike": [0.10, 0.15, 0.20, 0.90, 0.90, 0.25, 0.15, 0.10, 0.10, 0.10, 0.10],
    "plateau": [0.25, 0.35, 0.55, 0.62, 0.68, 0.72, 0.68, 0.62, 0.50, 0.35, 0.20],
    "oscillation": [0.20, 0.70, 0.25, 0.72, 0.30, 0.75, 0.25, 0.68, 0.20, 0.55, 0.15],
    "late_shock": [0.10, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.85, 0.90, 0.65, 0.20],
}


def _done(t: Telemetry) -> bool:
    return (not t.viable) or t.progress >= 0.75


def run_retry_limit(schedule: list[float], limit: int = 2) -> Telemetry:
    t = Telemetry()
    consecutive_failures = 0
    for disturbance in schedule:
        if _done(t):
            break
        if consecutive_failures >= limit:
            # A minimal reset: spend the opportunity but neither consume resource nor gain progress.
            consecutive_failures = 0
            t.last_action_failed = False
            continue
        before = t.failures
        t.modes[Mode.NORMAL.value] += 1
        apply_action(t, environment_step(disturbance, cautious=False))
        consecutive_failures = consecutive_failures + 1 if t.failures > before else 0
    return t


def run_circuit_breaker(schedule: list[float], threshold: int = 2) -> Telemetry:
    t = Telemetry()
    consecutive_failures = 0
    for disturbance in schedule:
        if _done(t):
            break
        if consecutive_failures >= threshold:
            t.modes[Mode.RECOVERY.value] += 1
            recover(t, disturbance)
            consecutive_failures = 0
            continue
        before = t.failures
        t.modes[Mode.NORMAL.value] += 1
        apply_action(t, environment_step(disturbance, cautious=False))
        consecutive_failures = consecutive_failures + 1 if t.failures > before else 0
    return t


def run_resource_throttle(schedule: list[float], threshold: float = 0.55) -> Telemetry:
    t = Telemetry()
    for disturbance in schedule:
        if _done(t):
            break
        cautious = t.resource < threshold
        t.modes[(Mode.CAUTION if cautious else Mode.NORMAL).value] += 1
        apply_action(t, environment_step(disturbance, cautious=cautious))
    return t


def run_homeostatic_frozen(schedule: list[float]) -> Telemetry:
    t = Telemetry()
    regulator = Regulator()
    for disturbance in schedule:
        if _done(t):
            break
        margin = regulator.margin(disturbance, t.resource, t.failures)
        t.min_margin = min(t.min_margin, margin)
        mode = regulator.mode(margin)
        t.modes[mode.value] += 1
        if mode is Mode.RECOVERY:
            recover(t, disturbance)
            continue
        apply_action(t, environment_step(disturbance, cautious=(mode is Mode.CAUTION)))
    return t
