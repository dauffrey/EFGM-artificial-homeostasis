from __future__ import annotations

import json

from .ablation import NoCoupledMarginRegulator, run_with_regulator
from .attack import score
from .core import Regulator
from .experiment import summary

SCHEDULES = {
    "ramp_reversal": [0.08, 0.16, 0.28, 0.42, 0.58, 0.74, 0.88, 0.62, 0.38, 0.18, 0.08],
    "double_pulse": [0.08, 0.12, 0.82, 0.86, 0.18, 0.12, 0.10, 0.78, 0.84, 0.16, 0.08],
    "chatter": [0.12, 0.68, 0.16, 0.72, 0.14, 0.76, 0.18, 0.70, 0.12, 0.66, 0.10],
    "creep": [0.16, 0.20, 0.24, 0.29, 0.34, 0.39, 0.45, 0.51, 0.57, 0.62, 0.66],
}


def _frozen_score(results: dict[str, dict[str, dict]]) -> dict[str, int]:
    """Apply the AH-EXP-0002 score criteria to the two AH-EXP-0004 controllers."""
    totals = {"full": 0, "no_coupled_margin": 0}
    for controller_name in totals:
        projected = {}
        for schedule_name, schedule_results in results.items():
            candidate = schedule_results[controller_name]
            projected[schedule_name] = {
                "baseline": candidate,
                "retry_limit": candidate,
                "circuit_breaker": candidate,
                "resource_throttle": candidate,
                "homeostatic": candidate,
            }
        totals[controller_name] = score(projected)["homeostatic"]
    return totals


def run_all() -> dict:
    controllers = {
        "full": lambda schedule: run_with_regulator(schedule, Regulator()),
        "no_coupled_margin": lambda schedule: run_with_regulator(schedule, NoCoupledMarginRegulator()),
    }

    results: dict[str, dict[str, dict]] = {}
    for schedule_name, schedule in SCHEDULES.items():
        results[schedule_name] = {
            name: summary(runner(schedule)) for name, runner in controllers.items()
        }

    scores = _frozen_score(results)
    full_viable = sum(int(results[name]["full"]["viable"]) for name in SCHEDULES)
    uncoupled_completes_when_full_fails = sum(
        int(results[name]["no_coupled_margin"]["completed"] and not results[name]["full"]["completed"])
        for name in SCHEDULES
    )
    full_wins_distinct = sum(
        int(
            results[name]["full"]["completed"]
            and results[name]["full"]["viable"]
            and (
                not results[name]["no_coupled_margin"]["completed"]
                or not results[name]["no_coupled_margin"]["viable"]
                or results[name]["full"]["resource"] > results[name]["no_coupled_margin"]["resource"] + 0.10
            )
        )
        for name in SCHEDULES
    )

    return {
        "experiment": "AH-EXP-0004",
        "results": results,
        "scores": scores,
        "falsification": {
            "uncoupled_matches_or_exceeds_full": scores["no_coupled_margin"] >= scores["full"],
            "full_viable_on_fewer_than_3_schedules": full_viable < 3,
            "full_fails_two_where_uncoupled_completes": uncoupled_completes_when_full_fails >= 2,
        },
        "support": {
            "full_viable_and_complete_all_four": all(
                results[name]["full"]["viable"] and results[name]["full"]["completed"]
                for name in SCHEDULES
            ),
            "full_materially_wins_on_at_least_two_families": full_wins_distinct >= 2,
            "families_with_material_full_win": full_wins_distinct,
        },
    }


def main() -> None:
    print(json.dumps(run_all(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
