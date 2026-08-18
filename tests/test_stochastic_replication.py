from ahomeostasis.stochastic_replication import SEEDS, run_all, stochastic_schedule
from ahomeostasis.queue_replication import SCHEDULES


def test_stochastic_schedule_is_deterministic_per_seed():
    schedule = SCHEDULES["bursty_arrivals"]
    assert stochastic_schedule(schedule, SEEDS[0]) == stochastic_schedule(schedule, SEEDS[0])


def test_stochastic_schedule_changes_with_seed():
    schedule = SCHEDULES["bursty_arrivals"]
    assert stochastic_schedule(schedule, SEEDS[0]) != stochastic_schedule(schedule, SEEDS[1])


def test_stochastic_schedule_remains_bounded():
    for seed in SEEDS:
        for schedule in SCHEDULES.values():
            realized = stochastic_schedule(schedule, seed)
            assert all(0.0 <= value <= 1.0 for value in realized)


def test_ah_exp_0006_has_32_paired_trajectories_per_controller():
    result = run_all()
    assert result["trajectory_count_per_controller"] == 32
    assert len(result["by_seed"]) == 8


def test_ah_exp_0006_falsification_fields_are_present():
    result = run_all()
    assert set(result["falsification"]) == {
        "uncoupled_matches_or_exceeds_full",
        "full_viable_on_fewer_than_24_of_32",
        "full_wins_fewer_than_5_of_8_seeds",
        "uncoupled_completes_6_where_full_fails",
        "post_outcome_retuning_required",
    }
