import pytest

from ahomeostasis.trajectory_boundary import (
    COMPARISON_CONTROLLER,
    EXPERIMENT_ID,
    HORIZON,
    MODULATION,
    MU_COUNT,
    MU_STEP,
    PREREGISTRATION_BASELINE_SHA,
    PRIMARY_CONTROLLER,
    TrajectoryClass,
    boundary_intervals,
    canonical_result_hash,
    classify_terminal,
    disturbance_at,
    mu_grid,
    structural_manifest,
)


def test_frozen_design_constants() -> None:
    assert EXPERIMENT_ID == "AH-EXP-0011"
    assert PREREGISTRATION_BASELINE_SHA == "0baeab969e17374966ab8e7b400405e6eb576c56"
    assert PRIMARY_CONTROLLER == "robust_counterfactual_abstention"
    assert COMPARISON_CONTROLLER == "coupled_margin"
    assert MU_STEP == 0.005
    assert MU_COUNT == 201
    assert HORIZON == 100
    assert MODULATION == (
        -0.12,
        -0.08,
        -0.04,
        0.00,
        0.04,
        0.08,
        0.12,
        0.08,
        0.04,
        0.00,
        -0.04,
        -0.08,
    )
    assert sum(MODULATION) == pytest.approx(0.0)


def test_mu_grid_is_exact_frozen_shape() -> None:
    grid = mu_grid()
    assert len(grid) == 201
    assert grid[0] == 0.000
    assert grid[1] == 0.005
    assert grid[-2] == 0.995
    assert grid[-1] == 1.000
    assert all(round(grid[i + 1] - grid[i], 3) == 0.005 for i in range(len(grid) - 1))


def test_disturbance_modulation_and_clipping() -> None:
    assert disturbance_at(0.50, 0) == 0.38
    assert disturbance_at(0.50, 6) == 0.62
    assert disturbance_at(0.00, 0) == 0.0
    assert disturbance_at(0.00, 6) == 0.12
    assert disturbance_at(1.00, 0) == 0.88
    assert disturbance_at(1.00, 6) == 1.0
    assert disturbance_at(0.50, 12) == disturbance_at(0.50, 0)


def test_terminal_classification_rules_are_frozen() -> None:
    assert classify_terminal(
        completed=True,
        viable=True,
        executed_recoveries=0,
        horizon_reached=False,
    ) is TrajectoryClass.STABLE
    assert classify_terminal(
        completed=True,
        viable=True,
        executed_recoveries=1,
        horizon_reached=False,
    ) is TrajectoryClass.RECOVERED
    assert classify_terminal(
        completed=False,
        viable=False,
        executed_recoveries=0,
        horizon_reached=False,
    ) is TrajectoryClass.FAILED
    assert classify_terminal(
        completed=False,
        viable=True,
        executed_recoveries=0,
        horizon_reached=True,
    ) is TrajectoryClass.CENSORED


def test_unpreregistered_terminal_state_is_not_silently_reinterpreted() -> None:
    with pytest.raises(ValueError):
        classify_terminal(
            completed=True,
            viable=False,
            executed_recoveries=0,
            horizon_reached=False,
        )


def test_boundary_intervals_preserve_disconnected_transitions() -> None:
    rows = (
        (0.000, "STABLE"),
        (0.005, "STABLE"),
        (0.010, "FAILED"),
        (0.015, "RECOVERED"),
        (0.020, "RECOVERED"),
        (0.025, "FAILED"),
    )
    assert boundary_intervals(rows) == (
        {
            "lower_mu": "0.005",
            "upper_mu": "0.010",
            "from_class": "STABLE",
            "to_class": "FAILED",
        },
        {
            "lower_mu": "0.010",
            "upper_mu": "0.015",
            "from_class": "FAILED",
            "to_class": "RECOVERED",
        },
        {
            "lower_mu": "0.020",
            "upper_mu": "0.025",
            "from_class": "RECOVERED",
            "to_class": "FAILED",
        },
    )


def test_canonical_hash_is_deterministic_for_identical_ordered_payload() -> None:
    rows = [
        {"mu": "0.000", "classification": "STABLE"},
        {"mu": "0.005", "classification": "FAILED"},
    ]
    first = canonical_result_hash(rows)
    second = canonical_result_hash(rows)
    assert first == second
    assert len(first) == 64


def test_structure_manifest_does_not_execute_or_claim_validation() -> None:
    manifest = structural_manifest()
    assert manifest["experiment"] == "AH-EXP-0011"
    assert manifest["phase"] == "implementation_structure_only"
    assert manifest["preregistration_baseline_sha"] == PREREGISTRATION_BASELINE_SHA
    assert manifest["mu_count"] == 201
    assert manifest["validation_outcomes_observed"] is False
