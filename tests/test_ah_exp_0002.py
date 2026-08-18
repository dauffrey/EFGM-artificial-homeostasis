from ahomeostasis.attack import run_attack, score
from ahomeostasis.controls import SCHEDULES, run_homeostatic_frozen


def test_attack_schedules_are_frozen_shape():
    assert set(SCHEDULES) == {"spike", "plateau", "oscillation", "late_shock"}
    assert all(len(v) == 11 for v in SCHEDULES.values())


def test_homeostatic_runner_uses_existing_regulator_behavior():
    result = run_homeostatic_frozen(SCHEDULES["plateau"])
    assert sum(result.modes.values()) > 0
    assert result.resource >= 0.0


def test_attack_returns_all_controllers_and_falsification_flags():
    attack = run_attack()
    assert set(attack["scores"]) == {"baseline", "retry_limit", "circuit_breaker", "resource_throttle", "homeostatic"}
    assert set(attack["falsification"]) == {
        "simple_control_matches_or_exceeds_homeostatic",
        "homeostatic_viable_on_fewer_than_3_schedules",
    }


def test_resource_efficiency_is_compared_across_actual_controllers():
    result = {
        "completed": True,
        "viable": True,
        "repeated_failures": 0,
        "progress": 0.75,
    }
    results = {
        "one": {
            "efficient": {**result, "resource_consumed": 0.25},
            "costly": {**result, "resource_consumed": 0.75},
        }
    }
    scores = score(results)
    assert scores["efficient"] == 4
    assert scores["costly"] == 3
