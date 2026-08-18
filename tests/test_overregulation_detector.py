from ahomeostasis.core import Mode
from ahomeostasis.overregulation_detector import (
    HOLDOUT_CANDIDATES,
    HOLDOUT_SEED,
    DetectorState,
    holdout_candidates,
    run_all,
    should_relax,
)
from ahomeostasis.queue_replication import QueueTelemetry


def test_holdout_candidates_are_frozen_and_distinct():
    first = holdout_candidates()
    second = holdout_candidates()
    assert first == second
    assert len(first) == HOLDOUT_CANDIDATES
    assert HOLDOUT_SEED == 8009


def test_detector_requires_sustained_protection_and_spare_capacity():
    telemetry = QueueTelemetry()
    telemetry.resource = 0.5
    telemetry.backlog = 3
    state = DetectorState()
    assert not should_relax(Mode.CAUTION, telemetry, state)
    assert not should_relax(Mode.RECOVERY, telemetry, state)
    assert not should_relax(Mode.CAUTION, telemetry, state)
    assert should_relax(Mode.RECOVERY, telemetry, state)


def test_detector_does_not_relax_when_resource_is_low():
    telemetry = QueueTelemetry()
    telemetry.resource = 0.1
    telemetry.backlog = 3
    state = DetectorState(protective_streak=3)
    assert not should_relax(Mode.CAUTION, telemetry, state)


def test_ah_exp_0008_runs_holdout_evaluation():
    result = run_all()
    assert result["experiment"] == "AH-EXP-0008"
    assert result["candidate_count"] == HOLDOUT_CANDIDATES
    assert result["holdout_seed"] == HOLDOUT_SEED
    assert "adaptive" in result["aggregate"]
    assert "frozen" in result["aggregate"]
    assert "falsification" in result
