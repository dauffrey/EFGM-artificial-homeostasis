from __future__ import annotations

import json
import random
from dataclasses import dataclass
from statistics import mean

from .ablation import NoCoupledMarginRegulator
from .core import Mode, Regulator
from .queue_replication import (
    INITIAL_BACKLOG,
    MAX_BACKLOG,
    QueueTelemetry,
    SCHEDULES,
    TARGET_WORK,
    summary,
)
from .stochastic_replication import SEEDS, stochastic_schedule


PARTIAL_OBSERVABILITY = ("delay_1", "biased_low", "noisy_sensor")
MODEL_MISMATCH = ("expensive_service", "weak_recovery", "fragile_service")
SEARCH_SEED = 7001
SEARCH_CANDIDATES = 256


@dataclass(frozen=True)
class EnvironmentConfig:
    service_cost_multiplier: float = 1.0
    recovery_gain_multiplier: float = 1.0
    threshold_shift: float = 0.0


def utility(row: dict) -> float:
    return (
        4.0 * int(row["completed"])
        + 3.0 * int(row["viable"])
        + 2.0 * row["progress"]
        + row["resource"]
        - 0.25 * row["failures"]
        - 0.50 * row["repeated_failures"]
    )


def _arrival(disturbance: float, step: int) -> int:
    if disturbance >= 0.78:
        return 2
    if disturbance >= 0.58 and step % 2 == 0:
        return 1
    return 0


def _service(
    t: QueueTelemetry,
    disturbance: float,
    cautious: bool,
    step: int,
    config: EnvironmentConfig,
) -> None:
    if t.backlog <= 0:
        return

    success_threshold = (0.80 if cautious else 0.58) + config.threshold_shift
    succeeded = disturbance <= success_threshold
    base_cost = (0.055 if cautious else 0.085) * config.service_cost_multiplier
    stress_cost = disturbance * (0.045 if cautious else 0.12) * config.service_cost_multiplier
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
        if disturbance >= 0.75 and step % 2 == 1:
            t.backlog = min(MAX_BACKLOG + 1, t.backlog + 1)


def _maintenance(t: QueueTelemetry, disturbance: float, config: EnvironmentConfig) -> None:
    t.recoveries += 1
    gain = max(0.025, 0.11 * (1.0 - disturbance)) * config.recovery_gain_multiplier
    t.resource = min(1.0, t.resource + gain)
    t.last_action_failed = False


def run_controller(
    true_schedule: list[float],
    observed_schedule: list[float],
    regulator: Regulator,
    config: EnvironmentConfig | None = None,
) -> QueueTelemetry:
    if len(true_schedule) != len(observed_schedule):
        raise ValueError("true and observed schedules must have equal length")
    config = config or EnvironmentConfig()
    t = QueueTelemetry()
    for step, (true_disturbance, observed_disturbance) in enumerate(zip(true_schedule, observed_schedule)):
        if t.completed or not t.viable:
            break

        t.backlog = min(MAX_BACKLOG + 1, t.backlog + _arrival(true_disturbance, step))
        if not t.viable:
            break

        margin = regulator.margin(observed_disturbance, t.resource, t.failures)
        t.min_margin = min(t.min_margin, margin)
        mode = regulator.mode(margin)
        t.modes[mode.value] += 1

        if mode is Mode.RECOVERY:
            _maintenance(t, true_disturbance, config)
        else:
            _service(t, true_disturbance, cautious=(mode is Mode.CAUTION), step=step, config=config)

    return t


def observe(schedule: list[float], condition: str, seed: int) -> list[float]:
    if condition == "delay_1":
        return [0.0] + schedule[:-1]
    if condition == "biased_low":
        return [max(0.0, value - 0.20) for value in schedule]
    if condition == "noisy_sensor":
        rng = random.Random(10000 + seed)
        return [min(1.0, max(0.0, value + rng.uniform(-0.20, 0.20))) for value in schedule]
    raise ValueError(f"unknown observation condition: {condition}")


def _pair(true_schedule: list[float], observed_schedule: list[float], config: EnvironmentConfig | None = None) -> dict:
    full = summary(run_controller(true_schedule, observed_schedule, Regulator(), config))
    uncoupled = summary(run_controller(true_schedule, observed_schedule, NoCoupledMarginRegulator(), config))
    return {
        "full": full,
        "no_coupled_margin": uncoupled,
        "utility": {
            "full": utility(full),
            "no_coupled_margin": utility(uncoupled),
        },
    }


def _aggregate(rows: list[dict]) -> dict:
    out: dict[str, dict] = {}
    for controller in ("full", "no_coupled_margin"):
        records = [row[controller] for row in rows]
        out[controller] = {
            "count": len(records),
            "completed": sum(int(record["completed"]) for record in records),
            "viable": sum(int(record["viable"]) for record in records),
            "mean_progress": mean(record["progress"] for record in records),
            "mean_resource_remaining": mean(record["resource"] for record in records),
            "failures": sum(record["failures"] for record in records),
            "repeated_failures": sum(record["repeated_failures"] for record in records),
            "total_utility": sum(row["utility"][controller] for row in rows),
        }
    full_wins = sum(row["utility"]["full"] > row["utility"]["no_coupled_margin"] for row in rows)
    uncoupled_wins = sum(row["utility"]["no_coupled_margin"] > row["utility"]["full"] for row in rows)
    out["paired_wins"] = {
        "full": full_wins,
        "no_coupled_margin": uncoupled_wins,
        "ties": len(rows) - full_wins - uncoupled_wins,
    }
    return out


def attack_partial_observability() -> dict:
    by_condition: dict[str, dict] = {}
    all_rows: list[dict] = []
    for condition in PARTIAL_OBSERVABILITY:
        rows: list[dict] = []
        for seed in SEEDS:
            for nominal_schedule in SCHEDULES.values():
                true_schedule = stochastic_schedule(nominal_schedule, seed)
                observed_schedule = observe(true_schedule, condition, seed)
                rows.append(_pair(true_schedule, observed_schedule))
        by_condition[condition] = _aggregate(rows)
        all_rows.extend(rows)
    return {"by_condition": by_condition, "aggregate": _aggregate(all_rows)}


def _config(condition: str) -> EnvironmentConfig:
    if condition == "expensive_service":
        return EnvironmentConfig(service_cost_multiplier=1.35)
    if condition == "weak_recovery":
        return EnvironmentConfig(recovery_gain_multiplier=0.45)
    if condition == "fragile_service":
        return EnvironmentConfig(threshold_shift=-0.12)
    raise ValueError(f"unknown mismatch condition: {condition}")


def attack_model_mismatch() -> dict:
    by_condition: dict[str, dict] = {}
    all_rows: list[dict] = []
    for condition in MODEL_MISMATCH:
        rows: list[dict] = []
        config = _config(condition)
        for seed in SEEDS:
            for nominal_schedule in SCHEDULES.values():
                true_schedule = stochastic_schedule(nominal_schedule, seed)
                rows.append(_pair(true_schedule, true_schedule, config))
        by_condition[condition] = _aggregate(rows)
        all_rows.extend(rows)
    return {"by_condition": by_condition, "aggregate": _aggregate(all_rows)}


def adversarial_candidates() -> list[list[float]]:
    rng = random.Random(SEARCH_SEED)
    candidates: list[list[float]] = []
    while len(candidates) < SEARCH_CANDIDATES:
        candidate = [rng.random() for _ in range(12)]
        high_count = sum(value > 0.80 for value in candidate)
        avg = sum(candidate) / len(candidate)
        if high_count <= 6 and 0.25 <= avg <= 0.70:
            candidates.append(candidate)
    return candidates


def attack_adversarial_search() -> dict:
    best: dict | None = None
    advantages: list[float] = []
    for schedule in adversarial_candidates():
        row = _pair(schedule, schedule)
        advantage = row["utility"]["no_coupled_margin"] - row["utility"]["full"]
        advantages.append(advantage)
        if best is None or advantage > best["uncoupled_advantage"]:
            best = {
                "schedule": schedule,
                "uncoupled_advantage": advantage,
                "result": row,
            }
    assert best is not None
    return {
        "candidate_count": SEARCH_CANDIDATES,
        "max_uncoupled_advantage": best["uncoupled_advantage"],
        "best_candidate": best,
        "mean_uncoupled_advantage": mean(advantages),
        "uncoupled_wins": sum(value > 0 for value in advantages),
        "full_wins": sum(value < 0 for value in advantages),
        "ties": sum(value == 0 for value in advantages),
    }


def run_all() -> dict:
    partial = attack_partial_observability()
    mismatch = attack_model_mismatch()
    search = attack_adversarial_search()

    partial_full = partial["aggregate"]["full"]
    partial_uncoupled = partial["aggregate"]["no_coupled_margin"]
    mismatch_full = mismatch["aggregate"]["full"]
    mismatch_uncoupled = mismatch["aggregate"]["no_coupled_margin"]

    return {
        "experiment": "AH-EXP-0007",
        "partial_observability": partial,
        "model_mismatch": mismatch,
        "adversarial_search": search,
        "falsification": {
            "partial_observability_uncoupled_total_utility_greater": partial_uncoupled["total_utility"] > partial_full["total_utility"],
            "model_mismatch_uncoupled_total_utility_greater": mismatch_uncoupled["total_utility"] > mismatch_full["total_utility"],
            "adversarial_schedule_uncoupled_advantage_at_least_1": search["max_uncoupled_advantage"] >= 1.0,
            "partial_observability_full_viability_below_60_percent": partial_full["viable"] < 0.60 * partial_full["count"],
            "model_mismatch_full_viability_below_60_percent": mismatch_full["viable"] < 0.60 * mismatch_full["count"],
            "post_outcome_retuning_required": False,
        },
    }


def main() -> None:
    print(json.dumps(run_all(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
