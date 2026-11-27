# LH-EXP-0002 — Prospective exploratory protocol (2026-11-27)

Status: Protocol committed before execution; investigator-defined, not independent preregistration. Abstract classifiers only, not real AI safety or permission controls.

H1: Sequential task learning degrades a previously learned eligibility classifier in a narrow shared representation, despite capability gains.
H2: Negative task-versus-eligibility gradient dot products predict first-order increases in eligibility loss.
H3: Homeostatic backtracking improves eligibility retention over ordinary replay at matched task accuracy.

Design: 12 paired NumPy float64 seeds 1100-1111. Two input coordinates, eligibility=1[x0>0], task=1[x1>0]. Independent normal inputs in training and ID test; shifted test corr(x0,x1)=0.75. Training sets 256 samples for each objective; 4096 evaluation examples per seed/distribution. Tanh shared trunk width 1 or 4, independent sigmoid heads. Identical initialization and first-phase checkpoints for every method/seed/width. Phase 1: eligibility BCE 150 full-batch updates at SGD lr 0.15. Phase 2: 250 full-batch opportunities at lr 0.12; checkpoints every 10. Test data never used for selection/training.

Methods: sequential task-only; task+full eligibility replay with weights 1 and 4; A-GEM-like projection of task gradient when dot(task_grad,reg_grad)<0; homeostatic task-gradient step backtracked with up to 8 halvings to allow at most +0.0001 eligibility anchor-training BCE per step, else skip. Count extra regulatory gradient and loss evaluations. Equal update opportunities, NOT equal compute.

Outcomes: independent capability accuracy; eligibility balanced accuracy, TPR, FPR, Brier and useful completion among eligible. Negative gradient fraction, mean cosine, gradient sign and realized anchor loss-change contingency. Mean over seeds, full trajectories. Paired bootstrap CI (10000 samples, fixed bootstrap seed). Secondary nearest-checkpoint capability matching with mismatches reported.

Decision rules: H1 holds in width=1 only if sequential capability gain >=10 percentage points AND eligibility balanced-accuracy drop >=10 points. H3 holds only if homeostatic minus replay_1 shifted-test eligible balanced-accuracy >=5 points, paired 95% bootstrap CI strictly positive and absolute task accuracy difference <=3 points. H2 diagnostic only, not causal proof. Always compare replay_4 and projected controls. No tuning after seeing outcomes.

Constraints: A 1D bottleneck deliberately induces resource conflict, and no technique can be expected to maximize two independent task axes perfectly. No LLMs, no real autonomous actions, no formal safety claim. Model-size scaling, other generators, independent evaluation and compute matching are future work. Preserve adverse and null results.