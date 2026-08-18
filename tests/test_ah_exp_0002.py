from ahomeostasis.attack import run_attack
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
