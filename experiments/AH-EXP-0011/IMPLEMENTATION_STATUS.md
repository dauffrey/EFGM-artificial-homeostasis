# AH-EXP-0011 Implementation Status

## Status

**IMPLEMENTATION CONSTRUCTION — CANONICAL VALIDATION OUTCOMES NOT OBSERVED**

AH-EXP-0011 was preregistered and merged before implementation began.

Frozen preregistration baseline:

```text
0baeab969e17374966ab8e7b400405e6eb576c56
```

A dedicated preservation branch points at that exact merged preregistration commit:

```text
ah-exp-0011-preregistered-freeze
```

Implementation began from that exact commit on:

```text
ah-exp-0011-implementation
```

## Construction rule

During implementation construction, tests and CI may validate only design identity, frozen constants, disturbance generation, classification logic, boundary extraction, canonical hashing, and other structural invariants that do not execute the frozen 201-value validation sweep.

The canonical functions exist in code so the later evaluation is defined before outcomes are observed, but they must not be invoked during construction or structural CI:

```text
run_trajectory(...)
run_sweep(...)
run_canonical_validation()
```

The module CLI intentionally exposes only a structure-only manifest during this phase and does not provide a canonical validation execution switch.

## Required pre-evaluation sequence

Before any AH-EXP-0011 canonical validation outcomes are observed:

1. review the implementation against `PREREGISTRATION.md`;
2. verify that structural tests do not execute validation-grid trajectories;
3. obtain exact-head CI success for the implementation branch/PR;
4. freeze the reviewed implementation commit SHA;
5. only then execute the canonical validation sweep;
6. preserve the first canonical results before performing the exact reproducibility rerun.

No controller parameter, environment parameter, disturbance cycle, `mu` grid, horizon, classification rule, escape definition, or boundary rule may be changed in response to canonical validation outcomes.
