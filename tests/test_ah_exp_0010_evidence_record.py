from __future__ import annotations

import json
from pathlib import Path

from ahomeostasis.robust_counterfactual_abstention import HOLDOUT_CANDIDATES, HOLDOUT_SEED


BASELINE_SHA = "10b8072a856856c73f497f64efb88e226dac7e96"
AUTHORIZATION_SHA = "0332e9611759dbc5faca31079071846def676b17"
EVIDENCE_SHA256 = "952e8b89a2c8f1d82f1ad302469c9199cf923709036d83c3173d7b1aaf8eb220"
RECORD_PATH = Path("experiments/AH-EXP-0010/FINAL_EVIDENCE_RECORD.json")
WORKFLOW_PATH = Path(".github/workflows/ah-exp-0010-final-holdout.yml")

EXPECTED_FALSIFICATION_KEYS = {
    "adaptive_completion_not_greater",
    "adaptive_utility_not_greater",
    "adaptive_viability_loss_exceeds_5_percent",
    "harmful_intervention_schedules_greater_or_equal_beneficial",
    "detector_never_intervenes",
    "post_outcome_parameter_change",
}


def _record() -> dict:
    return json.loads(RECORD_PATH.read_text(encoding="utf-8"))


def test_final_evidence_record_is_bound_to_frozen_evaluation() -> None:
    record = _record()
    assert record["experiment"] == "AH-EXP-0010"
    assert record["classification"] == "SURVIVED"
    assert record["hypothesis_survives"] is True
    assert record["authorized_baseline_sha"] == BASELINE_SHA
    assert record["authorization_workflow_commit"] == AUTHORIZATION_SHA
    assert record["holdout_seed"] == HOLDOUT_SEED == 10011
    assert record["holdout_candidates"] == HOLDOUT_CANDIDATES == 512
    assert record["workflow_run_number"] == 1
    assert record["workflow_run_attempt"] == 1
    assert record["evidence_json_sha256"] == EVIDENCE_SHA256


def test_survival_record_has_no_falsification_flag() -> None:
    falsification = _record()["falsification_criteria"]
    assert set(falsification) == EXPECTED_FALSIFICATION_KEYS
    assert not any(falsification.values())


def test_one_shot_workflow_remains_bound_to_same_baseline() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert f"BASELINE_SHA: {BASELINE_SHA}" in workflow
    assert f"ref: {BASELINE_SHA}" in workflow
    assert "github.run_attempt == 1" in workflow
    assert "Refuse any prior AH-EXP-0010 holdout run" in workflow
    assert "holdout_seed=10011" in workflow
    assert "holdout_candidates=512" in workflow


def test_recorded_evidence_hash_has_sha256_shape() -> None:
    digest = _record()["evidence_json_sha256"]
    assert len(digest) == 64
    int(digest, 16)
