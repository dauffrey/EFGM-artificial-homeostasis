from __future__ import annotations

import pytest

from ahomeostasis.observation_integrity_warning import (
    BASELINE_THRESHOLDS,
    BEST_BASELINE,
    CONFIRMATORY_CYCLE,
    DEVELOPMENT_ROWS_SHA256,
    EFGM_WARNING_THRESHOLD,
    confirmatory_mu_grid,
    holdout_design_manifest,
    structural_manifest,
    verify_frozen_development_calibration,
)


def test_ah_exp_0013_frozen_development_calibration_reproduces() -> None:
    result = verify_frozen_development_calibration()

    assert result["phase"] == "development_only"
    assert result["trajectory_count"] == 128
    assert result["prediction_count"] == 436
    assert result["positive_label_count"] == 65
    assert result["negative_label_count"] == 371
    assert result["harmful_trajectory_count"] == 42
    assert result["development_rows_sha256"] == DEVELOPMENT_ROWS_SHA256
    assert result["selected"]["EFGM"]["threshold"] == EFGM_WARNING_THRESHOLD
    assert result["best_baseline"] == BEST_BASELINE == "B9_simple_integrity"
    assert {
        name: row["threshold"]
        for name, row in result["selected"].items()
        if name.startswith("B")
    } == BASELINE_THRESHOLDS

    # Development-only diagnostic. This is not confirmatory evidence.
    assert result["selected"]["EFGM"]["metrics"]["balanced_accuracy"] == pytest.approx(
        0.7744972009122952
    )
    assert result["selected"][BEST_BASELINE]["metrics"]["balanced_accuracy"] == pytest.approx(
        0.6981132075471699
    )


def test_ah_exp_0013_holdout_design_is_frozen_without_execution() -> None:
    manifest = holdout_design_manifest()

    assert len(confirmatory_mu_grid()) == 71
    assert confirmatory_mu_grid()[0] == 0.450
    assert confirmatory_mu_grid()[-1] == 0.800
    assert sum(CONFIRMATORY_CYCLE) == pytest.approx(0.0)
    assert manifest["trajectory_count"] == 355
    assert tuple(manifest["profiles"]) == ("P0", "P1", "P2", "P3", "P4")
    assert manifest["confirmatory_outcomes_observed"] is False


def test_ah_exp_0013_structural_manifest_preserves_causal_freeze() -> None:
    manifest = structural_manifest()

    assert manifest["efgm_warning_rule"] == "mean(1-GI, AE, CUE)"
    assert manifest["efgm_warning_threshold"] == EFGM_WARNING_THRESHOLD
    assert manifest["baseline_thresholds"] == BASELINE_THRESHOLDS
    assert manifest["best_baseline"] == BEST_BASELINE
    assert manifest["development_rows_sha256"] == DEVELOPMENT_ROWS_SHA256
    assert manifest["confirmatory_trajectory_count"] == 355
    assert manifest["confirmatory_outcomes_observed"] is False
