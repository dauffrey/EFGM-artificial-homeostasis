from ahomeostasis.core import Mode, Regulator
from ahomeostasis.experiment import DISTURBANCE, run_baseline, run_homeostatic


def test_regulator_mode_boundaries_are_frozen():
    assert Regulator.mode(0.36) is Mode.NORMAL
    assert Regulator.mode(0.35) is Mode.CAUTION
    assert Regulator.mode(0.01) is Mode.CAUTION
    assert Regulator.mode(0.0) is Mode.RECOVERY


def test_default_schedule_is_frozen():
    assert DISTURBANCE == [0.05, 0.10, 0.20, 0.35, 0.55, 0.70, 0.85, 0.65, 0.45, 0.25, 0.10]


def test_runs_are_deterministic():
    assert run_baseline() == run_baseline()
    assert run_homeostatic() == run_homeostatic()


def test_homeostatic_agent_exercises_internal_modes():
    result = run_homeostatic()
    assert result.modes[Mode.CAUTION.value] > 0
    assert result.modes[Mode.RECOVERY.value] > 0


def test_homeostatic_agent_does_not_trivially_refuse_work():
    assert run_homeostatic().progress > 0.0
