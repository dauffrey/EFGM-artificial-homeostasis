from ahomeostasis.core import Mode
from ahomeostasis.counterfactual_regulation import (
    BACKLOG_FLOOR,
    CALIBRATION_CANDIDATES,
    CALIBRATION_SEED,
    CF_THRESHOLD,
    HOLDOUT_CANDIDATES,
    HOLDOUT_SEED,
    RESOURCE_FLOOR,
    DecisionSnapshot,
    DetectorState,
    bounded_candidates,
    calibration_structural_validation,
    counterfactual_advantage,
    should_relax,
)
from ahomeostasis.queue_replication import QueueTelemetry


def test_frozen_seeds_and_sizes_are_distinct():
    assert CALIBRATION_SEED == 9001
    assert HOLDOUT_SEED == 9011
    assert CALIBRATION_CANDIDATES == 256
    assert HOLDOUT_CANDIDATES == 512
    calibration = bounded_candidates(CALIBRATION_SEED, 8)
    holdout = bounded_candidates(HOLDOUT_SEED, 8)
    assert calibration != holdout


def test_counterfactual_matches_frozen_low_disturbance_model():
    disturbance = 0.40
    # NORMAL: 2 units, cost .133; CAUTION: 1 unit, cost .073.
    expected = 1.0 - 2.0 * (0.133 - 0.073)
    assert abs(counterfactual_advantage(Mode.CAUTION, disturbance) - expected) < 1e-12
    assert counterfactual_advantage(Mode.CAUTION, disturbance) >= CF_THRESHOLD


def test_counterfactual_penalizes_normal_failure():
    disturbance = 0.70
    assert counterfactual_advantage(Mode.CAUTION, disturbance) < CF_THRESHOLD


def test_detector_requires_all_frozen_trajectory_gates():
    telemetry = QueueTelemetry()
    telemetry.resource = RESOURCE_FLOOR
    telemetry.backlog = BACKLOG_FLOOR
    telemetry.work_cleared = 1
    state = DetectorState(
        history=[
            DecisionSnapshot(Mode.CAUTION, 0, 3),
            DecisionSnapshot(Mode.NORMAL, 1, 3),
        ]
    )
    assert should_relax(Mode.CAUTION, telemetry, state, disturbance=0.40)


def test_detector_does_not_fire_on_elapsed_protection_alone():
    telemetry = QueueTelemetry()
    telemetry.resource = 0.35
    telemetry.backlog = 3
    telemetry.work_cleared = 0
    state = DetectorState(
        history=[
            DecisionSnapshot(Mode.CAUTION, 0, 3),
            DecisionSnapshot(Mode.RECOVERY, 0, 3),
        ]
    )
    assert not should_relax(Mode.CAUTION, telemetry, state, disturbance=0.40)


def test_detector_requires_two_prior_decision_snapshots():
    telemetry = QueueTelemetry()
    telemetry.resource = 0.8
    telemetry.backlog = 5
    state = DetectorState(history=[DecisionSnapshot(Mode.CAUTION, 0, 5)])
    assert not should_relax(Mode.RECOVERY, telemetry, state, disturbance=0.30)


def test_calibration_validation_does_not_observe_holdout_outcomes():
    result = calibration_structural_validation()
    assert result["phase"] == "calibration_structural_validation_only"
    assert result["calibration_seed"] == CALIBRATION_SEED
    assert result["candidate_count"] == CALIBRATION_CANDIDATES
    assert result["holdout_seed"] == HOLDOUT_SEED
    assert result["holdout_outcomes_observed"] is False
    assert result["protective_trajectories"] > 0
    assert result["trajectories_with_normal_actions"] > 0
