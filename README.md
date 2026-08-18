# EFGM Artificial Homeostasis

Experimental research into EFGM-inspired artificial homeostasis: internal self-regulation, resilience, recovery, and stable behavior in autonomous AI agents.

## Research question

Can an internally regulated agent preserve a viable, recoverable operating state under increasing disturbance better than an otherwise identical goal-driven baseline?

This repository is intentionally separate from the main EFGM project. It is a clean laboratory for testing the artificial-homeostasis hypothesis without changing or contaminating the existing EFGM evidence base.

## Phase 0

The first experiment, **AH-EXP-0001**, compares two deterministic toy agents under identical disturbance schedules:

- `baseline`: pursues the task and retries while budget remains.
- `homeostatic`: observes disturbance and recovery signals, computes a resilience margin, and changes operating mode between `NORMAL`, `CAUTION`, and `RECOVERY`.

The regulator is not given a catalogue of forbidden actions. It is tested on whether state feedback alone can reduce destructive persistence while preserving useful task completion.

## Candidate state variable

The initial candidate is deliberately simple:

```text
resilience_margin(t) = recovery_capacity(t) - disturbance_load(t)
```

This is a hypothesis, not an established EFGM result.

## Scientific guardrails

AH-EXP-0001 is preregistered before outcome analysis. The repository records the primary hypothesis, controls, success criteria, falsification criteria, disturbance schedule, metrics, and analysis rules in `experiments/AH-EXP-0001/PREREGISTRATION.md`.

A positive result is not enough. Any apparent advantage must later survive simpler competing baselines such as retry limits and circuit breakers before it can be interpreted as evidence for an EFGM-specific regulatory effect.

## Run

```bash
python -m pip install -e .
python -m pytest
python -m ahomeostasis.experiment
```

The experiment is deterministic by default and emits JSON summaries for both agents.

## Status

**Phase 0: scientific baseline under review.** No claim of artificial homeostasis has been established.
