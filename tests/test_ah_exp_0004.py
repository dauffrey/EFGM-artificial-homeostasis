from ahomeostasis.robustness import SCHEDULES, run_all


def test_robustness_experiment_reports_all_new_schedules() -> None:
    report = run_all()
    assert report["experiment"] == "AH-EXP-0004"
    assert set(report["results"]) == set(SCHEDULES)
    assert set(report["scores"]) == {"full", "no_coupled_margin"}


def test_robustness_falsification_is_machine_reported() -> None:
    report = run_all()
    falsification = report["falsification"]
    assert set(falsification) == {
        "uncoupled_matches_or_exceeds_full",
        "full_viable_on_fewer_than_3_schedules",
        "full_fails_two_where_uncoupled_completes",
    }
    assert all(isinstance(value, bool) for value in falsification.values())


def test_new_schedules_are_distinct_and_nontrivial() -> None:
    assert len(SCHEDULES) == 4
    assert len({tuple(values) for values in SCHEDULES.values()}) == 4
    assert all(len(values) >= 10 for values in SCHEDULES.values())
    assert all(0.0 <= value <= 1.0 for values in SCHEDULES.values() for value in values)


def test_corrected_scoring_preserves_coupled_margin_separation() -> None:
    report = run_all()
    assert report["scores"] == {"full": 15, "no_coupled_margin": 8}
    assert report["falsification"] == {
        "uncoupled_matches_or_exceeds_full": False,
        "full_viable_on_fewer_than_3_schedules": False,
        "full_fails_two_where_uncoupled_completes": False,
    }
