from ahomeostasis.robust_counterfactual_abstention import HOLDOUT_CANDIDATES, HOLDOUT_SEED
from ahomeostasis.robust_counterfactual_holdout import evaluate_rows, holdout_candidates


def _row(*, frozen_completed: bool, adaptive_completed: bool, frozen_viable: bool, adaptive_viable: bool, frozen_utility: float, adaptive_utility: float, interventions: int) -> dict:
    return {
        "frozen": {"completed": frozen_completed, "viable": frozen_viable},
        "adaptive": {"completed": adaptive_completed, "viable": adaptive_viable},
        "interventions": interventions,
        "utility": {"frozen": frozen_utility, "adaptive": adaptive_utility},
    }


def test_holdout_generator_is_frozen_and_deterministic() -> None:
    first = holdout_candidates()
    second = holdout_candidates()
    assert first == second
    assert len(first) == HOLDOUT_CANDIDATES == 512
    assert HOLDOUT_SEED == 10011
    assert all(len(schedule) == 12 for schedule in first)


def test_evaluate_rows_can_express_surviving_result_without_running_holdout() -> None:
    rows = [
        _row(
            frozen_completed=False,
            adaptive_completed=True,
            frozen_viable=True,
            adaptive_viable=True,
            frozen_utility=1.0,
            adaptive_utility=2.0,
            interventions=1,
        ),
        _row(
            frozen_completed=False,
            adaptive_completed=False,
            frozen_viable=True,
            adaptive_viable=True,
            frozen_utility=1.0,
            adaptive_utility=1.0,
            interventions=0,
        ),
    ]
    result = evaluate_rows(rows)
    assert result["hypothesis_survives"] is True
    assert result["aggregate"]["intervention_schedules"] == {
        "beneficial": 1,
        "harmful": 0,
        "neutral": 0,
        "total": 1,
    }


def test_evaluate_rows_falsifies_when_harmful_is_not_less_than_beneficial() -> None:
    rows = [
        _row(
            frozen_completed=False,
            adaptive_completed=True,
            frozen_viable=True,
            adaptive_viable=True,
            frozen_utility=1.0,
            adaptive_utility=3.0,
            interventions=1,
        ),
        _row(
            frozen_completed=False,
            adaptive_completed=True,
            frozen_viable=True,
            adaptive_viable=True,
            frozen_utility=3.0,
            adaptive_utility=2.0,
            interventions=1,
        ),
    ]
    result = evaluate_rows(rows)
    assert result["falsification"]["harmful_intervention_schedules_greater_or_equal_beneficial"] is True
    assert result["hypothesis_survives"] is False
