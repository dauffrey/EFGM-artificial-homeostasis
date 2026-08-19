from __future__ import annotations

import json
from statistics import mean

from .adversarial_robustness import utility
from .counterfactual_regulation import bounded_candidates
from .queue_replication import summary
from .robust_counterfactual_abstention import (
    HOLDOUT_CANDIDATES,
    HOLDOUT_SEED,
    run_with_robust_abstention,
)


def holdout_candidates() -> list[list[float]]:
    return bounded_candidates(HOLDOUT_SEED, HOLDOUT_CANDIDATES)


def _row(schedule: list[float]) -> dict:
    frozen_t, _ = run_with_robust_abstention(schedule, enabled=False)
    adaptive_t, interventions = run_with_robust_abstention(schedule, enabled=True)
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


def evaluate_rows(rows: list[dict]) -> dict:
    frozen_completion = sum(int(row["frozen"]["completed"]) for row in rows)
    adaptive_completion = sum(int(row["adaptive"]["completed"]) for row in rows)
    frozen_viability = sum(int(row["frozen"]["viable"]) for row in rows)
    adaptive_viability = sum(int(row["adaptive"]["viable"]) for row in rows)
    frozen_utility = sum(row["utility"]["frozen"] for row in rows)
    adaptive_utility = sum(row["utility"]["adaptive"] for row in rows)
    interventions = sum(row["interventions"] for row in rows)

    adaptive_wins = sum(row["utility"]["adaptive"] > row["utility"]["frozen"] for row in rows)
    frozen_wins = sum(row["utility"]["frozen"] > row["utility"]["adaptive"] for row in rows)

    intervention_rows = [row for row in rows if row["interventions"] > 0]
    beneficial = sum(row["utility"]["adaptive"] > row["utility"]["frozen"] for row in intervention_rows)
    harmful = sum(row["utility"]["adaptive"] < row["utility"]["frozen"] for row in intervention_rows)
    neutral = len(intervention_rows) - beneficial - harmful

    falsification = {
        "adaptive_completion_not_greater": adaptive_completion <= frozen_completion,
        "adaptive_utility_not_greater": adaptive_utility <= frozen_utility,
        "adaptive_viability_loss_exceeds_5_percent": (
            adaptive_viability < frozen_viability - 0.05 * HOLDOUT_CANDIDATES
        ),
        "harmful_intervention_schedules_greater_or_equal_beneficial": harmful >= beneficial,
        "detector_never_intervenes": interventions == 0,
        "post_outcome_parameter_change": False,
    }

    return {
        "experiment": "AH-EXP-0010",
        "phase": "final_holdout",
        "holdout_seed": HOLDOUT_SEED,
        "candidate_count": HOLDOUT_CANDIDATES,
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
            "paired_utility_wins": {
                "adaptive": adaptive_wins,
                "frozen": frozen_wins,
                "ties": len(rows) - adaptive_wins - frozen_wins,
            },
            "intervention_schedules": {
                "beneficial": beneficial,
                "harmful": harmful,
                "neutral": neutral,
                "total": len(intervention_rows),
            },
            "mean_interventions": mean(row["interventions"] for row in rows),
        },
        "falsification": falsification,
        "hypothesis_survives": not any(falsification.values()),
    }


def run_final_holdout() -> dict:
    rows = [_row(schedule) for schedule in holdout_candidates()]
    return evaluate_rows(rows)


def main() -> None:
    raise SystemExit(
        "AH-EXP-0010 final holdout is implemented but intentionally locked. "
        "Execute only through the separately authorized commit-bound holdout workflow."
    )


if __name__ == "__main__":
    main()
