import pytest

from ahomeostasis.preescape_warning import (
    ADAPTER_ID,
    AGENT_CONFIG_ID,
    AGENT_CONFIG_SHA256,
    AH_SUBSTRATE_SHA,
    BASELINE_THRESHOLDS,
    BEST_SINGLE_BASELINE,
    DEVELOPMENT_ROWS_SHA256,
    EFGM_CODE_SHA,
    EFGM_V2_CONFIG_ID,
    EFGM_V2_CONFIG_SHA256,
    EFGM_WARNING_THRESHOLD,
    EXPERIMENT_ID,
    HOLDOUT_MODULATION,
    PREREGISTRATION_FREEZE_SHA,
    PRIMARY_FEATURES,
    development_reference,
    holdout_disturbance_at,
    structural_manifest,
)


def test_frozen_identity_and_thresholds() -> None:
    assert EXPERIMENT_ID == "AH-EXP-0012"
    assert PREREGISTRATION_FREEZE_SHA == "4c01e559548341e16310981ade06871f63685d00"
    assert AH_SUBSTRATE_SHA == "e21d68d1257ef36a3882a5f6362535f701d6350c"
    assert EFGM_CODE_SHA == "37b2ff2d2b577c9f383dd0d7c3083597627150ea"
    assert EFGM_V2_CONFIG_ID == "efgm-v2.0-baseline"
    assert EFGM_V2_CONFIG_SHA256 == "0f55f6eabe97d0f365d1e45ba8f9d0fef67e9721a93e6eba8b0a364b612bafd0"
    assert AGENT_CONFIG_ID == "efgm-v0.3-agent-governance-candidate-r2"
    assert AGENT_CONFIG_SHA256 == "af0b5540f28d4d65ae95929a855a168f9e7c286439d33d33e14ef167d808366c"
    assert ADAPTER_ID == "ah-exp-0012-efgm-adapter-v1"
    assert EFGM_WARNING_THRESHOLD == pytest.approx(0.582818749642)
    assert BASELINE_THRESHOLDS == {
        "backlog": 9.0,
        "resource": 0.878775,
        "margin": 0.235,
        "disturbance": 0.745,
    }
    assert BEST_SINGLE_BASELINE == "backlog"
    assert DEVELOPMENT_ROWS_SHA256 == "e5c5a73db69cc2db6fc9d6661f6af6cc6dab7c50c57258d86b0634f5402f3044"


def test_primary_feature_contract_is_frozen() -> None:
    assert PRIMARY_FEATURES == (
        "DQ",
        "CRC",
        "GI",
        "AE",
        "CUE",
        "Delta_DQ",
        "Delta_CRC",
        "Delta_GI",
        "Delta_AE",
        "Delta_CUE",
    )


def test_holdout_cycle_shape_only_does_not_execute_trajectory() -> None:
    assert len(HOLDOUT_MODULATION) == 20
    assert sum(HOLDOUT_MODULATION) == pytest.approx(0.0)
    assert holdout_disturbance_at(0.50, 0) == 0.35
    assert holdout_disturbance_at(0.50, 5) == 0.65
    assert holdout_disturbance_at(0.00, 0) == 0.0
    assert holdout_disturbance_at(1.00, 5) == 1.0
    assert holdout_disturbance_at(0.50, 20) == holdout_disturbance_at(0.50, 0)


def test_development_reference_reproduces_frozen_0011_rows() -> None:
    reference = development_reference()
    assert reference["sha256"] == DEVELOPMENT_ROWS_SHA256
    assert len(reference["rows"]) == 831
    assert sum(row["y"] for row in reference["rows"]) == 120
    assert set(reference["distributions"]) == set(PRIMARY_FEATURES)


def test_structure_manifest_declares_holdout_unobserved() -> None:
    manifest = structural_manifest()
    assert manifest["experiment"] == "AH-EXP-0012"
    assert manifest["phase"] == "observer_frozen_holdout_not_executed"
    assert manifest["holdout_outcomes_observed"] is False
    assert manifest["development_rows_sha256"] == DEVELOPMENT_ROWS_SHA256
    assert manifest["warning_threshold"] == EFGM_WARNING_THRESHOLD
