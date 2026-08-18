from ahomeostasis.adversarial_robustness import (
    MODEL_MISMATCH,
    PARTIAL_OBSERVABILITY,
    SEARCH_CANDIDATES,
    adversarial_candidates,
    observe,
    run_all,
    utility,
)


def test_observation_conditions_are_preregistered_and_bounded():
    schedule = [0.1, 0.5, 0.9]
    for condition in PARTIAL_OBSERVABILITY:
        observed = observe(schedule, condition, 7)
        assert len(observed) == len(schedule)
        assert all(0.0 <= value <= 1.0 for value in observed)


def test_adversarial_candidate_space_is_deterministic_and_constrained():
    first = adversarial_candidates()
    second = adversarial_candidates()
    assert first == second
    assert len(first) == SEARCH_CANDIDATES
    for schedule in first:
        assert len(schedule) == 12
        assert sum(value > 0.80 for value in schedule) <= 6
        assert 0.25 <= sum(schedule) / len(schedule) <= 0.70


def test_utility_rewards_viability_and_penalizes_failures():
    good = {
        "completed": True,
        "viable": True,
        "progress": 1.0,
        "resource": 0.5,
        "failures": 0,
        "repeated_failures": 0,
    }
    bad = {
        "completed": False,
        "viable": False,
        "progress": 0.5,
        "resource": 0.1,
        "failures": 3,
        "repeated_failures": 2,
    }
    assert utility(good) > utility(bad)


def test_ah_exp_0007_runs_all_preregistered_attacks():
    result = run_all()
    assert result["experiment"] == "AH-EXP-0007"
    assert set(result["partial_observability"]["by_condition"]) == set(PARTIAL_OBSERVABILITY)
    assert set(result["model_mismatch"]["by_condition"]) == set(MODEL_MISMATCH)
    assert result["adversarial_search"]["candidate_count"] == SEARCH_CANDIDATES
    assert "falsification" in result
