# AH-EXP-0010 — Final Result

## Classification

**SURVIVED**

AH-EXP-0010 survived its preregistered, one-shot final holdout without post-outcome parameter changes.

## Immutable evaluation baseline

- Authorized baseline SHA: `10b8072a856856c73f497f64efb88e226dac7e96`
- Holdout seed: `10011`
- Holdout schedules: `512`
- Frozen mechanism: robust counterfactual abstention
- Uncertainty width: `0.08`
- Frozen counterfactual threshold: `0.50`
- AH-EXP-0009 trajectory gates and counterfactual coefficients remained unchanged.

## One-shot run identity

- Workflow: `AH-EXP-0010 one-shot final holdout`
- Workflow file: `.github/workflows/ah-exp-0010-final-holdout.yml`
- Workflow run number: `1`
- Workflow run attempt: `1`
- Authorization workflow commit: `0332e9611759dbc5faca31079071846def676b17`
- Authorization commit message: `Authorize one-shot AH-EXP-0010 final holdout`

The workflow checked out the immutable baseline SHA above and refused evaluation if the checked-out SHA differed. It also refused prior runs and required `github.run_attempt == 1`.

## Evidence identity

- Evidence artifact name: `ah-exp-0010-final-holdout-evidence`
- Evidence JSON: `ah-exp-0010-final-holdout.json`
- Evidence manifest: `ah-exp-0010-evidence-manifest.txt`
- Evidence JSON SHA-256: `952e8b89a2c8f1d82f1ad302469c9199cf923709036d83c3173d7b1aaf8eb220`

The evidence hash above is the run-time SHA-256 displayed by the one-shot workflow summary. The complete run-time JSON and manifest were preserved as the workflow artifact; this repository record intentionally does not regenerate or rerun the holdout.

## Preregistered falsification criteria

The frozen evaluator classifies AH-EXP-0010 as **FALSIFIED** if any of the following is true:

1. adaptive completion is not greater than frozen completion;
2. adaptive total utility is not greater than frozen total utility;
3. adaptive viability loss exceeds 5 percentage points;
4. harmful intervention schedules are greater than or equal to beneficial intervention schedules;
5. the detector never intervenes;
6. a post-outcome parameter change occurs.

The one-shot evaluator returned `hypothesis_survives = true`; therefore none of the frozen falsification flags fired in the evidentiary run. No criterion was changed after outcome exposure.

## Scientific interpretation boundary

This result establishes only that the preregistered robust-counterfactual-abstention mechanism survived this frozen synthetic holdout. It does not establish a universal property of AI agents, biological homeostasis, consciousness, or general real-world safety.

## Sequence integrity

The preserved Phase-1 sequence is:

`robust effect -> failure boundary -> AH-EXP-0008 FALSIFIED -> AH-EXP-0009 FALSIFIED -> AH-EXP-0010 SURVIVED`

AH-EXP-0011 must not be designed or preregistered until this record is merged into protected `main`.
