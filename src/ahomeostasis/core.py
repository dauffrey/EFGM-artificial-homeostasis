from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Mode(str, Enum):
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    RECOVERY = "RECOVERY"


@dataclass(frozen=True)
class StepObservation:
    disturbance: float
    action_succeeded: bool
    action_cost: float
    progress_delta: float


@dataclass
class Telemetry:
    progress: float = 0.0
    resource: float = 1.0
    failures: int = 0
    repeated_failures: int = 0
    recoveries: int = 0
    last_action_failed: bool = False
    min_margin: float = 1.0
    modes: dict[str, int] = field(default_factory=lambda: {m.value: 0 for m in Mode})

    @property
    def viable(self) -> bool:
        return self.resource > 0.0


class Regulator:
    """Minimal internal feedback controller used only for AH-EXP-0001."""

    def __init__(self) -> None:
        self.recovery_capacity = 1.0

    def margin(self, disturbance: float, resource: float, failures: int) -> float:
        # Recovery capacity falls with depleted resources and accumulated failures.
        self.recovery_capacity = max(0.0, 0.65 * resource + 0.35 * (1.0 / (1.0 + failures)))
        return self.recovery_capacity - disturbance

    @staticmethod
    def mode(margin: float) -> Mode:
        if margin <= 0.0:
            return Mode.RECOVERY
        if margin <= 0.35:
            return Mode.CAUTION
        return Mode.NORMAL


def apply_action(telemetry: Telemetry, obs: StepObservation) -> None:
    telemetry.resource = max(0.0, telemetry.resource - obs.action_cost)
    telemetry.progress += obs.progress_delta
    if not obs.action_succeeded:
        telemetry.failures += 1
        if telemetry.last_action_failed:
            telemetry.repeated_failures += 1
    telemetry.last_action_failed = not obs.action_succeeded


def recover(telemetry: Telemetry, disturbance: float) -> None:
    """Spend a step restoring limited capacity instead of pursuing progress."""
    telemetry.recoveries += 1
    telemetry.resource = min(1.0, telemetry.resource + max(0.02, 0.12 * (1.0 - disturbance)))
    telemetry.last_action_failed = False
