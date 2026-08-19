# EFGM Artificial Homeostasis

Experimental research into EFGM-inspired artificial homeostasis: internal self-regulation, resilience, recovery, and stable behavior in autonomous AI agents.

This repository is intentionally separate from the main EFGM project. It is a clean laboratory for testing whether internally regulated agents can preserve useful operation under disturbance without contaminating the existing EFGM evidence base.

## Research question

Can an internally regulated agent preserve a viable, recoverable operating state under increasing disturbance better than an otherwise identical goal-driven baseline?

A narrower question has emerged from the experiments:

> Can an agent use internal state, disturbance, remaining operational reserve, and trajectory evidence to regulate its own behavior without either exhausting itself or over-regulating itself into task failure?

## Core candidate mechanism

The initial candidate state variable is deliberately simple:

```text
resilience_margin(t) = recovery_capacity(t) - disturbance_load(t)
```

Experiments increasingly point to a narrower mechanism: **coupling current disturbance pressure to remaining operational reserve when selecting behavior**.

This is an experimental hypothesis, not an established law of AI behavior or a validated production-safety mechanism.

## Experimental progression

### Phase 0 — establish and attack the initial effect

- **AH-EXP-0001** — internally regulated toy agent separated from an unregulated baseline under deterministic disturbance.
- **AH-EXP-0002** — the frozen regulator outperformed simpler retry-limit, circuit-breaker, and resource-throttle controls.
- **AH-EXP-0003** — genuine weakening result: removing failure history improved the score, falsifying the broader claim that every regulator component was necessary.
- **AH-EXP-0004** — the narrower coupled-margin mechanism remained stronger across new disturbance geometries after corrected comparative scoring.

Phase 0 therefore narrowed the hypothesis rather than confirming the original architecture wholesale.

### Phase 1 — replication, stochasticity, and failure-boundary search

- **AH-EXP-0005** — cross-environment replication in a materially different bounded queue/service environment. Full frozen regulator score: **16** vs **5** for the uncoupled variant.
- **AH-EXP-0006** — stochastic multi-seed replication across 32 paired trajectories. Full regulator completed and remained viable on **32/32** trajectories; the uncoupled variant completed and remained viable on **10/32**. Full regulator won **8/8** preregistered seeds.
- **AH-EXP-0007** — adversarial robustness study. The coupled-margin controller remained strongly advantageous overall under partial observability and model mismatch, but bounded adversarial search found a real failure boundary where excessive protection prevented task completion. The broad claim of uniform superiority was therefore partially falsified.
- **AH-EXP-0008** — simple over-regulation detector based on prolonged CAUTION/RECOVERY state. **FALSIFIED.** Completion and total utility both decreased. Persistence in a protective mode was not sufficient evidence that protection had become maladaptive.
- **AH-EXP-0009** — trajectory/counterfactual regulation detector. **FALSIFIED on the final independent holdout.** Aggregate completion, viability, and total utility improved, but the preregistered intervention-level governance criterion failed: harmful intervention schedules (**62**) were greater than beneficial intervention schedules (**57**).

## Current evidence

The strongest supported result so far is narrower than "artificial homeostasis works":

> **Coupling disturbance pressure to remaining operational reserve appears robustly useful across several controlled synthetic environments, but adaptive relaxation of protective regulation remains unresolved.**

The experiments also reveal an important distinction:

```text
better aggregate outcome != better intervention-level governance
```

AH-EXP-0009 improved aggregate completion, viability, and utility while still failing its preregistered decision-level criterion. This means outcome improvement alone is not treated as evidence that the intervention policy itself is well governed.

## Scientific guardrails

This repository is intentionally falsification-driven.

- Experiments are preregistered before outcome analysis where applicable.
- Negative and weakening results are preserved rather than tuned away.
- Holdout seeds and detector parameters are frozen before final evaluation.
- Post-outcome retuning is not used to convert a failed experiment into a successful one.
- Protected pull requests and CI preserve a reviewable experimental history.

The repository does **not** currently establish:

- a universal law of agent stability;
- biological equivalence to cellular homeostasis;
- consciousness, self-preservation, or intrinsic agency;
- production readiness;
- autonomous-agent safety or alignment.

## Why the negative results matter

AH-EXP-0003, AH-EXP-0007, AH-EXP-0008, and AH-EXP-0009 each constrained the theory.

The resulting research path is now:

```text
robust regulatory effect
    -> discover failure boundary
    -> simple corrective detector falsified
    -> counterfactual detector improves aggregate outcomes
    -> intervention-level governance criterion still falsified
```

That sequence is the evidence base for the next experiment rather than a reason to erase or retune earlier failures.

## Run

```bash
python -m pip install -e .
python -m pytest
python -m ahomeostasis.experiment
```

Additional experiment modules are executed through CI and their preregistrations/results are stored under `experiments/`.

## Status

**Phase 1: active falsification and mechanism-discovery research.**

AH-EXP-0009 is retained as a falsified final-holdout result. The next experiment must be preregistered separately and should test whether an adaptive regulator can improve aggregate outcomes **and** demonstrate positive intervention-level causal value on unseen trajectories.