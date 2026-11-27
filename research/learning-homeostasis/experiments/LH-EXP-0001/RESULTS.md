# LH-EXP-0001 — Exploratory result, 2026-11-27

**Disposition: specified divergence NOT OBSERVED. Guarded update benefit NOT DEMONSTRATED.** Not an independently preregistered or confirmatory experiment.

## Shifted test distribution, mean across 12 paired seeds, step 200

| Method | Puzzle accuracy | Ineligible answer rate | Permitted and correct | Eligible abstention | Gate Brier |
|---|---:|---:|---:|---:|---:|
| Task only | 63.4500% | 43.7149% | 36.4406% | 42.2349% | 0.249884 |
| Joint 1 | 66.0925% | 0% | 66.0925% | 0% | 0.001120 |
| Joint 4 | 66.5553% | 0% | 66.5553% | 0% | 0.000115 |
| Guarded 1 | 66.0925% | 0% | 66.0925% | 0% | 0.001120 |

Primary joint-1 result from step 20 to 200: capability +15.3241 percentage points; ineligible answer rate -0.7388 points, rather than the required +5 points. Therefore the specified conjunction fails.

Guarded learning accepted all 2,400 updates without scaling or rejection; 4,800 additional gate-loss forward evaluations. Every endpoint metric and trajectory metric matches joint-1 (apart from extra-forward bookkeeping). Nearest-checkpoint comparison to joint-4: mean absolute capability mismatch 0.6577 points; zero ineligible-answer difference; guarded minus joint-4 permitted-correct +0.3304 points. Descriptive only, not evidence of superiority.

Paired final differences relative to joint-1 (mean ± sample SD, percentage points except Brier):
- Task-only: capability -2.6425 ± 5.9665; permitted correct -29.6519 ± 16.8260; ineligible answer +43.7149 ± 20.4916; eligible abstention +42.2349 ± 24.2083; Brier +0.248764 ± 0.074817.
- Joint-4: capability and permitted correct +0.4628 ± 1.5381; ineligible answer and eligible abstention 0 ± 0; Brier -0.001004 ± 0.000599.
- Guarded-1: all differences exactly zero.

## Local execution and verification

NumPy 2.3.5; 48 training runs, 2,016 recorded checkpoint/distribution rows. Locally specified protocol and source hashed before first execution. Both analytic gradients compared to central finite differences (max absolute errors 1.814e-11 and 9.986e-12). A second local execution produced byte-identical CSV and summary JSON. GitHub code and protocol blob identities matched the local originals. No independent holdout custodian or CI execution was used.

Reproduce from this directory: install NumPy 2.3.5 and run `OPENBLAS_NUM_THREADS=1 python experiment.py` (set equivalent environment variable on Windows). It writes trajectories.csv and summary.json locally. Generated raw outputs supplied separately; not committed here.

SHA-256:
- PROTOCOL.md: 9f15323330290fd5829f8bc868b1c7d1e484939e6e94551db53073d832d8dc52
- experiment.py: fde3e58e79eb709c28d0383579c823473484968ba31a478afdd15450586355fd
- trajectories.csv: d805bade8764857098bcb24eb0012d70633d6842bc92f67fa1e6f2dad11c7654
- summary.json: 92ec357b0798a012d64dd2d0b2b98377d84b27bbcad5c02e81ddb38921a497a6

## Interpretation and next experiment

A direct, unambiguous eligibility bit and balanced regulation supervision make this a deliberately simple task. Joint optimization already learns eligibility; the guard is inactive. This is not evidence of general LLM safety or proof that regulation is unnecessary. The task-only model is an ablation, not a competitive safety-trained baseline. Update opportunities are matched, not compute; test data is locally accessible, and independent validation is absent. The model is not an LLM, does not learn a sequential policy, and does not execute actions. Zero observed ineligible responses is not a formal guarantee. The protocol mentions always-abstain as a conceptual comparator (0 permitted-correct, 0 ineligible answer, 100% eligible abstention); no additional model was trained for it.

For LH-EXP-0002, preregister a benign sequential-learning study: learn a shared representation for two abstract supervised tasks; first establish regulation, then vary task-learning curriculum, replay, capacity and optimization while keeping evaluation independent. Test retention and generalization, measure gradient alignment and causal ablations, compare conventional joint training, rehearsal and standard constrained optimization at matched capability and compute. Do not alter LH-EXP-0001 to manufacture divergence. No general alignment claims or operational deployment follow.
