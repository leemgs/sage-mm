# Prospective actual values for the additional experiments

> **NOT MEASURED RESULTS.** The numbers below are preregistered engineering hypotheses, normalized to `Stock=100`. They are included because the revision requires explicit actual values before additional experiments. They must be replaced by observed run-level estimates and 95% confidence intervals, and must not be quoted in the abstract, Results, or conclusion as achieved improvements.

## Factorial actual measurements

The complete machine-readable 2×2×2×2 target matrix is `experiments/actual_factorial_targets.csv`. `G`, `I`, `R`, and `C` denote heap configuration, interop conversion, page reclamation, and coordinated controller. Lower indices are better. The prospective target for the full `1111` treatment is PSS 77, allocation rate 72, GC p99 64, fault rate 125, and input p99 82 relative to Stock 100, with controller CPU below 1.5%. The deliberately adverse hypothesis is that unguarded/static reclamation (`R=1,C=0`) raises fault-rate index to 160; successful coordination should hold it near 125. Expected raw-collection fields and baseline-relative ARM32/ARM64 planning bands are specified in [`EXPECTED_DEVICE_RUN_VALUES.md`](EXPECTED_DEVICE_RUN_VALUES.md).

These imply prospective full-system changes of −23% peak PSS, −28% allocation rate, −36% GC p99, +25% page-fault rate, and −18% input p99. A result is considered directionally consistent if its run-level 95% CI excludes zero in the predicted direction, while the safety criteria below are all met. These values are not substitutes for measurements.

## Controller-policy actual measurements with G/I/R enabled

| Baseline | Peak PSS index | GC p99 index | Fault index | Input p99 index | Controller CPU target |
|---|---:|---:|---:|---:|---:|
| Stock | 100 | 100 | 100 | 100 | 0.0% |
| Static-G | 94 | 75 | 100 | 90 | ≤0.1% |
| Static-GI | 87 | 71 | 100 | 86 | ≤0.2% |
| Static-GIR | 79 | 71 | 160 | 91 | ≤0.4% |
| Threshold-GIR | 78 | 66 | 132 | 85 | ≤0.8% |
| EWMA-GIR | 77 | 64 | 125 | 82 | ≤1.0% |
| Ridge-GIR | 76 | 62 | 122 | 80 | ≤1.5% |

The policy hypothesis is modest: Ridge is targeted to improve PSS by only 1 point and input p99 by 2 points over EWMA. If its 95% CI overlaps EWMA or overhead exceeds 1.5%, the paper must report that ML offers no demonstrated advantage and prefer the simpler policy.

## Preregistered safety and robustness thresholds

* No OOM, watchdog restart, correctness failure, writable/anonymous mapping selection, or use-after-unload is acceptable in any completed run.
* Relative to `Static-GI`, guarded reclamation may increase fault rate by at most 35% and storage bytes read by at most 10%; input/frame p99 must not regress by more than 5%.
* Hot-reuse reload p99 should remain below 25 ms on normal storage and 75 ms under injected slow storage.
* Native syscall failures, invalid telemetry, no-candidate, cooldown, fault-storm, and saturation fallbacks must each be counted. A fallback rate above 5% of decisions triggers root-cause analysis rather than exclusion.
* Controller CPU must remain below the policy-specific targets above, with managed allocation below 0.5 MiB/hour.
* Under the current experiment request, endurance success requires at least 30 independent eight-hour runs per tested cell (240 device-hours per cell), zero OOMs, and reporting of all started and censored runs. This is a prospective minimum, not current evidence; testing fewer preselected endurance cells must be disclosed as a narrowed design.

## Additional-platform actual range

On the independently assembled constrained ARM64 Linux platform, the actual full-system range is PSS index 75–85, GC p99 index 60–75, input p99 index 78–90, fault index 115–140, and controller CPU ≤1.5%. Results outside this range are still reported; they narrow generality rather than being discarded.

## Reporting rule

Observed data replace—not silently overwrite—these hypotheses. The final table must show `Actual`, `Observed effect`, `95% CI`, `n`, and `Pass/Fail` columns. All paper claims must be generated from the versioned observed result bundle. A projected target is never labeled “result,” “improvement,” or “deployment evidence.”
