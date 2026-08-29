# Evaluation and reviewer-facing reporting protocol

This document specifies measurements to collect; it does not invent commercial-device results. All manuscript numbers must be regenerated from one versioned result bundle.

## Research-question traceability

| RQ | Claim | Experiment and primary outcomes |
|---|---|---|
| RQ1 | architecture-aware heap configuration reduces compaction cost | ARM32/ARM64 heap sweep; peak RSS, collection count, p50/p95/p99/max pause |
| RQ2 | value-type interop reduces allocation | identical interop micro/macro traces; allocated bytes, RSS, throughput, ABI checks |
| RQ3 | guarded reclamation/controller reduces RSS without responsiveness loss | factorial ablation plus hot-reuse/switch stress; clean bytes, faults, reload latency, frame/input latency |

## Full factorial ablation

Run all 16 combinations of heap patch (H), interop (I), reclamation (R), and adaptive controller (C), including the default `0000` and full `1111`. Report, for every row: independent runs `n`, duration, peak/mean RSS, allocated bytes, GC count and p50/p95/p99/max pause, reclaimed private-clean bytes, minor/major faults, reload and storage latency, frame/input p95/p99, controller CPU time, syscall time/failures, and 95% confidence intervals. Do not label expected impacts as ablation results.

Use at least 30 independently reset/seeded runs per short workload unless a preregistered power analysis supports another `n`. Construct run-level, two-sided percentile bootstrap CIs (10,000 resamples); do not treat within-run samples as independent. Randomize treatment order, lock firmware/thermal/network state, and separate controller training traces from final reporting traces.

## Baselines and scope

Compare static, EWMA, and online-ridge policies under the same trace. Where ports are feasible, add low-latency/concurrent collectors; otherwise explicitly explain that LXR and Platinum require different runtime/collector integrations and are not drop-in embedded-.NET configurations. AGC and DumpKV address SSD/LSM storage garbage collection and are conceptual adaptive-policy comparisons, not managed-heap baselines. Report this domain mismatch rather than implying empirical equivalence.

## Reclamation adversity tests

Test cold steady state, immediate hot-page reuse, 1/5/10-second app switching, slow-storage injection, concurrent execution of targeted mappings, `madvise` failure injection, and a fault storm above 500 faults/s. Collect `Private_Clean` before/after from `smaps`, minor/major faults, bytes read, page-in/reload latency, syscall errno/duration, frame drops, input latency, and guard activations. Verify no writable/anonymous/shared mapping is selected and that failure leaves process correctness intact.

## Endurance and field evidence

Define the scripted state machine and dwell distributions. Report each eight-hour run separately, not as five “short runs”: number/duration, app transitions, OOM definition and event logs, censored runs, memory trajectory, thermal state, and watchdog/restart counts. Broad production-stability language requires a substantially longer prespecified observation window and denominators (device-hours and sessions).

## Quantitative consistency checklist

Generate every table, figure, abstract percentage, and conclusion from one data file. Remove duplicate tables and unresolved references. Annotate the ARM32 2.6x factor directly on its figure if supported. Use milliseconds (not “ms squared”), ensure narrative winners match tables, and define whether percentages are absolute or relative. Group design as Static/Compile-time Mechanisms, Adaptive Controller, and Safety; group evaluation as Setup, Baselines, Component Results, Stress/Generality, and Field Evidence.
