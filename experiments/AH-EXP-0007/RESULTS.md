# AH-EXP-0007 Results

## Status

AH-EXP-0007 **partially falsified** the broad coupled-margin robustness claim by finding a bounded adversarial schedule where the uncoupled controller materially outperformed the full controller.

Protected-PR CI #73 passed with 30 tests and the full experiment chain.

## Partial observability

Across 96 paired trajectories:

- Full controller completed 88/96 and remained viable on 95/96.
- Uncoupled controller completed 30/96 and remained viable on 30/96.
- Full total utility: 852.3366
- Uncoupled total utility: 327.0537
- Paired wins: full 66, uncoupled 2, ties 28.

The preregistered partial-observability falsification criteria were not triggered.

## Model mismatch

Across 96 paired trajectories:

- Full controller completed and remained viable on 96/96.
- Uncoupled controller completed 31/96 and remained viable on 28/96.
- Full total utility: 903.8515
- Uncoupled total utility: 308.3014
- Paired wins: full 71, uncoupled 1, ties 24.

The preregistered model-mismatch falsification criteria were not triggered.

## Bounded adversarial search

A deterministic search over 256 bounded schedules found:

- Full wins: 227
- Uncoupled wins: 10
- Ties: 19
- Mean uncoupled advantage: -5.5970
- Maximum uncoupled advantage: **3.8672**

The best adversarial schedule was:

```text
[0.8828513529, 0.2931291513, 0.3240279467, 0.4889575052,
 0.5446018642, 0.9093763549, 0.7905302974, 0.9765406460,
 0.4969285891, 0.7028562794, 0.5797649502, 0.2627159327]
```

On that schedule:

- Full controller: incomplete, progress 0.875, viable, resource 0.5137, utility 5.0137.
- Uncoupled controller: complete, progress 1.0, viable, resource 0.1310, utility 8.8810.
- Uncoupled advantage: **3.8672**.

This triggered the preregistered falsification criterion:

`adversarial_schedule_uncoupled_advantage_at_least_1 = true`

## Interpretation

The coupled-margin mechanism remains strongly advantageous on aggregate under partial observability and model mismatch, and it wins most of the bounded adversarial search space. However, AH-EXP-0007 demonstrates that the mechanism is **not uniformly dominant**. A bounded disturbance sequence can make the full controller over-regulate—spending five steps in recovery and six in caution—while the uncoupled controller continues acting and completes the task.

The appropriate conclusion is therefore a narrower one: coupled-margin regulation appears robust across broad tested conditions, but it has a discoverable failure boundary where excessive protective regulation can reduce task completion.

No post-outcome tuning was performed.
