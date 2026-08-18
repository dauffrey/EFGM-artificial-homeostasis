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
