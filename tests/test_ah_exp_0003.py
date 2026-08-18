from ahomeostasis.ablation import run_all


def test_ablation_experiment_reports_all_controllers() -> None:
    report = run_all()
    assert report["experiment"] == "AH-EXP-0003"
    expected = {
        "full",
        "no_recovery_action",
        "no_resource_awareness",
        "no_failure_history",
        "no_coupled_margin",
    }
    assert set(report["scores"]) == expected


def test_full_reference_remains_viable_on_at_least_three_schedules() -> None:
    report = run_all()
    viable = sum(
        1 for schedule in report["results"].values()
        if schedule["full"]["viable"]
    )
    assert viable >= 3


def test_ablation_outcome_is_machine_reported_not_assumed() -> None:
    report = run_all()
    matching = report["falsification"]["matching_ablations"]
    assert report["falsification"]["single_ablation_matches_or_exceeds_full"] == bool(matching)


def test_corrected_scoring_triggers_preregistered_weakening_condition() -> None:
    report = run_all()
    assert report["scores"] == {
        "full": 13,
        "no_recovery_action": 11,
        "no_resource_awareness": 11,
        "no_failure_history": 15,
        "no_coupled_margin": 6,
    }
    assert report["falsification"]["single_ablation_matches_or_exceeds_full"] is True
    assert report["falsification"]["matching_ablations"] == ["no_failure_history"]
