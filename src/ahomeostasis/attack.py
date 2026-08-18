from __future__ import annotations

import json

from .controls import SCHEDULES, run_circuit_breaker, run_homeostatic_frozen, run_resource_throttle, run_retry_limit
from .experiment import run_baseline, summary

CONTROLLERS = {
    "baseline": run_baseline,
    "retry_limit": run_retry_limit,
    "circuit_breaker": run_circuit_breaker,
    "resource_throttle": run_resource_throttle,
    "homeostatic": run_homeostatic_frozen,
}


def score(results: dict[str, dict[str, dict]]) -> dict[str, int]:
    scores = {name: 0 for name in CONTROLLERS}
    for schedule_results in results.values():
        eligible = {k: v for k, v in schedule_results.items() if v["progress"] >= 0.50}
        min_consumed = min((v["resource_consumed"] for v in eligible.values()), default=None)
        for name, result in schedule_results.items():
            scores[name] += int(result["completed"])
            scores[name] += int(result["viable"])
            scores[name] += int(result["repeated_failures"] == 0)
            if min_consumed is not None and name in eligible and abs(result["resource_consumed"] - min_consumed) < 1e-12:
                scores[name] += 1
    return scores


def run_attack() -> dict:
    results: dict[str, dict[str, dict]] = {}
    for schedule_name, schedule in SCHEDULES.items():
        results[schedule_name] = {
            name: summary(runner(schedule)) for name, runner in CONTROLLERS.items()
        }
    scores = score(results)
    homeostatic_viable = sum(int(results[s]["homeostatic"]["viable"]) for s in SCHEDULES)
    simple_best = max(scores[n] for n in ("retry_limit", "circuit_breaker", "resource_throttle"))
    return {
        "experiment": "AH-EXP-0002",
        "results": results,
        "scores": scores,
        "falsification": {
            "simple_control_matches_or_exceeds_homeostatic": simple_best >= scores["homeostatic"],
            "homeostatic_viable_on_fewer_than_3_schedules": homeostatic_viable < 3,
        },
    }


def main() -> None:
    print(json.dumps(run_attack(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
