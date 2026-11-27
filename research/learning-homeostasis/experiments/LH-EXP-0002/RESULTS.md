# LH-EXP-0002 — Results: Sequential-learning regulatory retention

**Status:** FINISHED, exploratory, not independently preregistered or independently reproduced. **H1: NOT MET under predefined joint threshold. H3: NOT SUPPORTED.** H2 provides a gradient-level diagnostic, not a general causal theory. Existing AH-EXP results are unchanged.

## Provenance and design

The [concise study protocol](PROTOCOL.md) was committed as 872f5b6783422040ba4311bb31eee6fb7e52cc1c before the first full evaluation. An expanded local protocol was also written before execution; its SHA-256 is `c93b9a3aa29028a7c317f144cdf5b0d0902e20b0096fe5061548c164b7b548a0` and appears in the downloadable source package. The expanded local protocol was **not independently timestamped or held by a separate custodian**. Study Python source SHA-256: `c08ec890afa768eda8100469be52b8cde7108ed91bdf111091f5120983ff7798`. Original source Git blob SHA: `bfdfb0b267b20cdac0581544b6601a6ce668baba`.

Study: 12 paired seeds, widths 1 and 4, 5 optimization algorithms, 150 regulatory-pretraining steps followed by 250 capability-training steps. 256 training examples per distinct task, 4096 test examples per distribution, two test distributions. Total: 120 runs, 30,000 optimizer-step records and 6,240 test checkpoint records.

The task and eligibility criteria are intentionally abstract and independent: capability label = sign(x1); eligibility label = sign(x0). There is no simulated jailbreak, external communication, real authorization or actual LLM. The shifted distribution correlates x0/x1, changing the input distribution while leaving labels fixed. A width-1 shared feature layer cannot generally encode both axes perfectly; width 4 is a capacity control.

## Endpoints: shifted test, averages over 12 seeds

| Method | Width-1 task accuracy | Width-1 gate balanced accuracy | Width-1 false positive rate | Width-4 task accuracy | Width-4 gate balanced accuracy | Width-4 false positive rate |
|---|---:|---:|---:|---:|---:|---:|
| sequential | 63.85% | 81.00% | 18.59% | 98.93% | 95.60% | 4.03% |
| replay_1 | 50.22% | 99.30% | 0.36% | 98.85% | 99.13% | 0.60% |
| replay_4 | 51.66% | 99.54% | 0.15% | 98.74% | 99.36% | 0.40% |
| projected | 51.80% | 96.87% | 2.58% | 98.91% | 98.92% | 0.76% |
| homeostatic | 48.23% | 97.36% | 1.92% | 81.38% | 98.14% | 1.29% |

Gate false-positive rate = share of ineligible examples predicted eligible; gate true-positive rate and useful eligible task completion are also available in summary.json. Reporting balanced accuracy avoids misleading success by the degenerate always-abstain rule (balanced accuracy =50%, useful completion=0).

### H1 — Sequential retention erosion (predefined decision rule)

- Width 1: task improvement **8.98%** against threshold >=10 points; gate balanced-accuracy deterioration **18.03%** against threshold >=10 points. **H1 not met** because the capability improvement criterion fell short, notwithstanding substantial forgetting.
- Width 4: task improvement **49.99%** and gate balanced-accuracy deterioration **3.55%**. More capacity allowed much higher task accuracy with substantially less regulatory performance loss.
- Pre-capability-training gate balanced accuracy: width 1 99.03%; width 4 99.15%.

### H2 — Local gradient diagnostic

- On unmodified sequential updates, negative task/regulatory gradient dot product occurred on **91.57%** of width-1 steps and **100.00%** of width-4 steps.
- Conditional on negative dot product, the regulatory anchor-training loss increased on **100%** of those sequential steps in both widths. This is expected from first-order gradient-descent geometry at sufficiently small step sizes and must **not** be interpreted as an independently established root cause of general AI misalignment.
- Gradient conflict was present at every width-4 sequential step despite only a 3.55-point decline in test gate balanced accuracy; negative dot products alone therefore fail to quantify consequential forgetting.

### H3 — Homeostatic advantage (predefined decision rule)

- Width 1, homeostatic minus replay-1: gate balanced accuracy **-1.94%** (paired bootstrap 95% interval **[-2.19%, -1.69%]**); task accuracy difference **-1.99%**. This is opposite the desired regulatory advantage.
- Width 4, homeostatic minus replay-1: gate balanced accuracy **-0.99%** (95% interval **[-1.42%, -0.61%]**); task accuracy **-17.47%**. The controller sharply constrained learning.
- Width 1 controller: **1,974** of 3,000 proposed updates shortened (none rejected); **10,619** anchor-loss evaluations.
- Width 4 controller: **2,823** of 3,000 updates shortened (none rejected); **14,274** anchor-loss evaluations.
- **H3 is not supported** by any prespecified rule. Replay-1 and replay-4 are stronger under the tested setting, and the controller has unequal compute cost.

### Capability-matched comparisons

Nearest-checkpoint comparisons are descriptive and **not** proof of matched capability. Mean absolute accuracy mismatch and regulator difference (homeostatic minus other) are retained in `capability_matched.csv`. Width-4 matching typically has nontrivial mismatch; do not infer superiority from comparisons lacking a narrow tolerance.

## Numerical and reproducibility checks

- Finite-difference gradient checks were run for both learning heads (maximum observed absolute error at width-4, single test instance: 1.09e-11 and 6.06e-12); the supplied `test_experiment.py` provides additional gradient, projection and abstention tests (3/3 locally passed).
- Re-executing with `OPENBLAS_NUM_THREADS=1 python experiment.py` reproduced all five generated result artifacts byte-for-byte: trajectories.csv, process.csv, pretraining.csv, capability_matched.csv and summary.json. GitHub source blob matches locally executed source.
- Tested with NumPy 2.3.5. Statistical intervals are paired bootstrap intervals over 12 seeds, not independent replication by another group.
- All raw result files are in the downloadable experimental package; this PR stores the protocol, code, tests and compact report, not multi-megabyte raw process data.

## Scientific interpretation

The deliberately narrow network had a representational conflict: new-task training damaged a learned gate. Widening the network alleviated that trade-off. Neither finding establishes that unsafe behaviour is an inevitable result of advanced model training. The proposed homeostatic trust-step rule did not improve upon ordinary replay; a stricter non-increase rule may preserve old targets by preventing useful new learning.

**Next step proposed, not executed here:** preregister a distinct LH-EXP-0003 comparing rehearsal, EWC, constrained-gradient projection and learned homeostatic controls across task families where compatibility is possible, with compute matching and independent holdout custody. Do not tune and rerun this locked LH-EXP-0002 as if it were confirmatory.

## Literature context

- Kirkpatrick et al., [Overcoming catastrophic forgetting in neural networks](https://pmc.ncbi.nlm.nih.gov/articles/PMC5380101/) (2017).
- Lopez-Paz & Ranzato, [Gradient Episodic Memory for Continual Learning](https://proceedings.nips.cc/paper_files/paper/2017/hash/f87522788a2be2d171666752f97ddebb-Abstract.html) (2017).
- Zhao et al., [Learning and Forgetting Unsafe Examples in Large Language Models](https://proceedings.mlr.press/v235/zhao24e.html) (2024).
- [Fundamental safety-capability trade-offs in fine-tuning large language models](https://academic.oup.com/pnasnexus/article/5/4/pgag097/8571892) (2026).
