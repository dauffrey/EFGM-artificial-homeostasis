from __future__ import annotations

import json
import random
from statistics import mean

from .ablation import NoCoupledMarginRegulator
from .attack import score
from .core import Regulator
from .queue_replication import SCHEDULES, run_controller, summary

SEEDS = [7, 19, 43, 71, 101, 149, 211, 307]
NOISE_AMPLITUDE = 0.12


def stochastic_schedule(schedule: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    return [
        min(1.0, max(0.0, disturbance + rng.uniform(-NOISE_AMPLITUDE, NOISE_AMPLITUDE)))
        for disturbance in schedule
    ]


def _controller_results(schedule: list[float]) -> dict[str, dict]:
    return {
        "full": summary(run_controller(schedule, Regulator())),
        "no_coupled_margin": summary(run_controller(schedule, NoCoupledMarginRegulator())),
    }


def _aggregate(controller: str, trajectories: list[dict[str, dict]]) -> dict:
    rows = [trajectory[controller] for trajectory in trajectories]
    return {
        "completed": sum(int(row["completed"]) for row in rows),
        "viable": sum(int(row["viable"]) for row in rows),
        "mean_progress": mean(row["progress"] for row in rows),
        "mean_resource_remaining": mean(row["resource"] for row in rows),
        "failures": sum(row["failures"] for row in rows),
        "repeated_failures": sum(row["repeated_failures"] for row in rows),
    }


def run_all() -> dict:
    by_seed: dict[str, dict] = {}
    trajectories: list[dict[str, dict]] = []
    aggregate_scores = {"full": 0, "no_coupled_margin": 0}
    seed_wins = {"full": 0, "no_coupled_margin": 0, "ties": 0}
    uncoupled_only_completions = 0

    for seed in SEEDS:
        seed_results: dict[str, dict[str, dict]] = {}
        for schedule_name, nominal_schedule in SCHEDULES.items():
            realized = stochastic_schedule(nominal_schedule, seed)
            controller_results = _controller_results(realized)
            seed_results[schedule_name] = controller_results
            trajectories.append(controller_results)
            if controller_results["no_coupled_margin"]["completed"] and not controller_results["full"]["completed"]:
                uncoupled_only_completions += 1

        seed_scores = score(seed_results)
        aggregate_scores["full"] += seed_scores["full"]
        aggregate_scores["no_coupled_margin"] += seed_scores["no_coupled_margin"]
        if seed_scores["full"] > seed_scores["no_coupled_margin"]:
            seed_wins["full"] += 1
        elif seed_scores["no_coupled_margin"] > seed_scores["full"]:
            seed_wins["no_coupled_margin"] += 1
        else:
            seed_wins["ties"] += 1

        by_seed[str(seed)] = {
            "results": seed_results,
            "scores": seed_scores,
        }

    aggregate = {
        "full": _aggregate("full", trajectories),
        "no_coupled_margin": _aggregate("no_coupled_margin", trajectories),
    }

    return {
        "experiment": "AH-EXP-0006",
        "environment": "bounded_queue_service_stochastic",
        "noise_amplitude": NOISE_AMPLITUDE,
        "seeds": SEEDS,
        "trajectory_count_per_controller": len(trajectories),
        "by_seed": by_seed,
        "aggregate": aggregate,
        "aggregate_scores": aggregate_scores,
        "seed_wins": seed_wins,
        "falsification": {
            "uncoupled_matches_or_exceeds_full": aggregate_scores["no_coupled_margin"] >= aggregate_scores["full"],
            "full_viable_on_fewer_than_24_of_32": aggregate["full"]["viable"] < 24,
            "full_wins_fewer_than_5_of_8_seeds": seed_wins["full"] < 5,
            "uncoupled_completes_6_where_full_fails": uncoupled_only_completions >= 6,
            "post_outcome_retuning_required": False,
        },
    }


def main() -> None:
    print(json.dumps(run_all(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
