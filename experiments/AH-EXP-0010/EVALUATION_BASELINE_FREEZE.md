# AH-EXP-0010 Evaluation Baseline Freeze

Status: **FROZEN / IMMUTABLE SCIENTIFIC BASELINE**

This record freezes the exact implementation that is authorized for the AH-EXP-0010 final holdout evaluation.

## Authorized baseline

- Commit: `10b8072a856856c73f497f64efb88e226dac7e96`
- Pull request: `#10`
- Exact-head CI: `CI #117`
- CI conclusion: `success`
- Final holdout seed: `10011`
- Final holdout candidate count: `512`
- Structural seed: `10010`
- Structural candidate count: `256`
- Robust uncertainty width: `0.08`
- Frozen robust counterfactual threshold: `0.50`

## Scientific lock

The final holdout may only evaluate repository content checked out at commit `10b8072a856856c73f497f64efb88e226dac7e96`.

Any evaluation attempted against a different commit is invalid and must terminate before generating holdout outcomes.

The detector, trajectory gates, thresholds, seed, candidate count, scoring function, falsification rules, and evaluator code may not be changed after holdout outcomes are observed.

## Pre-registered final classification

AH-EXP-0010 is **FALSIFIED** if any frozen falsification condition returned by the evaluator is true, including if:

1. adaptive completion is not greater than frozen completion;
2. adaptive utility is not greater than frozen utility;
3. adaptive viability loss exceeds the preregistered 5% bound;
4. harmful intervention schedules are greater than or equal to beneficial intervention schedules;
5. the detector never intervenes; or
6. any post-outcome parameter change occurs.

AH-EXP-0010 is **SURVIVED** only when all preregistered falsification conditions are false.

## Evidence requirement

The authorized one-shot workflow must preserve:

- the exact checked-out commit SHA;
- the complete machine-readable evaluator output;
- the derived `SURVIVED` or `FALSIFIED` classification;
- the GitHub Actions run identity;
- an immutable workflow artifact containing the evidence.

This freeze records the evaluation baseline before any AH-EXP-0010 final holdout outcomes are exposed.
