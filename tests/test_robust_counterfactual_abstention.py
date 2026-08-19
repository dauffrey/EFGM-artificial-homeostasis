from ahomeostasis.core import Mode
from ahomeostasis.counterfactual_regulation import (
    CF_THRESHOLD,
    DecisionSnapshot,
    DetectorState,
    counterfactual_advantage,
)
from ahomeostasis.queue_replication import QueueTelemetry
from ahomeostasis.robust_counterfactual_abstention import (
    HOLDOUT_CANDIDATES,
    HOLDOUT_SEED,
    STRUCTURAL_CANDIDATES,
    STRUCTURAL_SEED,
    UNCERTAINTY_WIDTH,
    bounded_views,
    robust_counterfactual_advantage,
    should_relax_robust,
    structural_candidates,
    structural_validation,
)


def _eligible_state() -> tuple[QueueTelemetry, DetectorState]:
    telemetry = QueueTelemetry(resource=0.75, backlog=4, work_cleared=1)
    state = DetectorState(
        history=[
            DecisionSnapshot(Mode.CAUTION, work_cleared=0, backlog=3),
            DecisionSnapshot(Mode.CAUTION, work_cleared=1, backlog=4),
        ]
    )
    return telemetry, state


def test_frozen_design_constants() -> None:
    assert STRUCTURAL_SEED == 10010
    assert STRUCTURAL_CANDIDATES == 256
    assert HOLDOUT_SEED == 10011
    assert HOLDOUT_CANDIDATES == 512
    assert UNCERTAINTY_WIDTH == 0.08
    assert CF_THRESHOLD == 0.50


def test_bounded_views_clip_to_unit_interval() -> None:
    assert bounded_views(0.03) == (0.0, 0.03, 0.11)
    assert bounded_views(0.97) == (0.89, 0.97, 1.0)


def test_robust_cf_is_worst_case_of_three_frozen_scores() -> None:
    disturbance = 0.50
    views = bounded_views(disturbance)
    expected = min(counterfactual_advantage(Mode.CAUTION, d) for d in views)
    assert robust_counterfactual_advantage(Mode.CAUTION, disturbance) == expected


def test_robust_gate_can_only_abstain_relative_to_point_gate() -> None:
    telemetry, state = _eligible_state()
    disturbance = 0.54
    robust = should_relax_robust(Mode.CAUTION, telemetry, state, disturbance)
    if robust:
        assert counterfactual_advantage(Mode.CAUTION, disturbance) >= CF_THRESHOLD


def test_structural_generator_is_deterministic() -> None:
    first = structural_candidates()
    second = structural_candidates()
    assert first == second
    assert len(first) == STRUCTURAL_CANDIDATES
    assert all(len(schedule) == 12 for schedule in first)


def test_structural_validation_does_not_observe_holdout() -> None:
    result = structural_validation()
    assert result["experiment"] == "AH-EXP-0010"
    assert result["phase"] == "structural_validation_only"
    assert result["structural_seed"] == STRUCTURAL_SEED
    assert result["candidate_count"] == STRUCTURAL_CANDIDATES
    assert result["holdout_seed"] == HOLDOUT_SEED
    assert result["holdout_candidate_count"] == HOLDOUT_CANDIDATES
    assert result["holdout_outcomes_observed"] is False
