from ahomeostasis.queue_replication import SCHEDULES, run_all


def test_replication_uses_four_distinct_queue_schedules() -> None:
    assert set(SCHEDULES) == {
        "bursty_arrivals",
        "sustained_pressure",
        "alternating_load",
        "late_surge",
    }
    assert len({tuple(values) for values in SCHEDULES.values()}) == 4


def test_replication_reports_both_frozen_controllers() -> None:
    report = run_all()
    assert report["experiment"] == "AH-EXP-0005"
    assert report["environment"] == "bounded_queue_service"
    assert set(report["scores"]) == {"full", "no_coupled_margin"}
    assert all(set(schedule) == {"full", "no_coupled_margin"} for schedule in report["results"].values())


def test_queue_metrics_are_reported() -> None:
    report = run_all()
    required = {
        "completed",
        "viable",
        "progress",
        "work_cleared",
        "backlog",
        "resource",
        "resource_consumed",
        "failures",
        "repeated_failures",
        "recoveries",
        "min_margin",
        "modes",
    }
    for schedule in report["results"].values():
        for result in schedule.values():
            assert required <= set(result)


def test_replication_falsification_is_machine_reported() -> None:
    report = run_all()
    assert set(report["falsification"]) == {
        "uncoupled_matches_or_exceeds_full",
        "full_viable_on_fewer_than_3_schedules",
        "uncoupled_completes_two_where_full_fails",
        "post_outcome_retuning_required",
    }
    assert all(isinstance(value, bool) for value in report["falsification"].values())
