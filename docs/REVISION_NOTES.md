# Review-driven manuscript revision notes

This document is the source-of-truth checklist for revising the manuscript. It separates implemented facts from evidence that must be rerun. Empty measurements are marked **required** rather than filled with inferred or fabricated values.

## Contribution and terminology

Use “cross-layer coordinated framework,” not “three adaptive components.” The novelty claim is the explicit coordination of (i) a static architecture-specific heap build choice, (ii) reviewed source-time allocation removal, and (iii) bounded online control of OS-assisted clean-page reclamation and runtime compaction. The first two reduce the load presented to the controller; only the third adapts at runtime. The title and abstract must state that distinction and report one consistent set of held-out measurements.

The paper is best framed as a systems practice/experience contribution unless controlled cross-platform evidence supports a broader mechanism claim. Do not claim transparent deployment: the controller and native helper require firmware integration; the heap setting requires a runtime rebuild; value-type migration requires source review and recompilation. Binary-only applications benefit only from firmware-transparent mechanisms.

## Related-work comparison and citation audit

Add a scoped comparison rather than treating storage GC as an executable baseline:

| Approach | Domain/action | Runtime/application changes | Directly comparable? | SAGE-MM distinction |
|---|---|---|---|---|
| AGC (Sun et al., 2025) | SSD burst-aware flash GC scheduling | storage firmware | No; use conceptual discussion | managed heap, interop, and process page cache are coordinated under device memory pressure |
| LXR (Zhao, Blackburn, McKinley, PLDI 2022), DOI `10.1145/3519939.3523440` | concurrent managed-heap collection | research VM/collector | Only if ported to the same runtime/device | SAGE-MM does not introduce a collector; it targets memory footprint and reclaimable code pages |
| Platinum (Wu et al., USENIX ATC 2020), DOI `10.5555/3489146.3489157` | CPU-efficient concurrent server GC | collector/runtime | Only if ported | targets tail latency on server-class interactive services rather than swapless embedded integration |
| DumpKV (Zhuang, Zeng, Chen, PVLDB 18(4)) | learned lifetime control for LSM key/value storage | storage engine | No; use conceptual discussion | online model uses runtime/process telemetry and a bounded action space |

The reviewer-provided AGC and DumpKV entries repeat arXiv `2406.01250`; verify both bibliographic records against the publishers before submission rather than reproducing that identifier. Audit every existing citation against the sentence it supports. Remove the dynamic-taint paper formerly cited as a Tizen profiler and the Concurrent Pascal paper formerly used for managed/native interop. Prefer the exact vendor Mono commit documentation, Microsoft interop/GC documentation, Linux `madvise(2)`, and the four primary papers above. Do not claim empirical superiority to an unported collector. If feasible, port LXR/Platinum; otherwise compare stock runtime, tuned static runtime, EWMA, ridge, and a lightweight threshold controller and state why storage systems are non-executable conceptual baselines.

## Evaluation plan and RQ mapping

| RQ | Claim | Experiment | Required outcomes |
|---|---|---|---|
| RQ1 | architecture/build tuning changes GC cost | controlled ARM32/ARM64 heap sweep | peak/RSS/PSS, collections, compactions, mean/p95/p99/max pause; annotate the claimed 2.6× ratio directly in the figure |
| RQ2 | representation and reclamation reduce footprint safely | component/factorial ablation plus hot-reuse stress | allocations, private-clean bytes, RSS/PSS, faults, reload and input/frame latency |
| RQ3 | online coordination improves robustness | held-out traces, static/threshold/EWMA/ridge comparison, endurance | OOM count, time-to-OOM, p95/p99 latency, controller overhead and causal prediction loss |

Run every configuration from the same rebooted device image, thermal/power state, seeded script, and initial application state. Record runtime commit and patch hash, firmware image, architecture, storage model, compiler, configuration, and workload-driver commit. Use at least the preregistered number of independent runs; report `n`, individual seeds, arithmetic mean and a 95% bootstrap confidence interval over independent runs (not samples within one trace). Preserve all observations and scripts. Training/tuning devices and traces must be disjoint from reported test traces.

### Factorial ablation results schema

Replace the paper's “expected impact” table with measured rows. `G`, `I`, `R`, and `C` denote heap build setting, interop conversion, reclamation, and adaptive controller. Include all 16 rows (or justify infeasible interactions), with identical workloads:

| G | I | R | C | n | Peak PSS MiB (95% CI) | GC p99 ms (95% CI) | alloc MiB/s | reclaimed MiB | faults/s | input p99 ms | controller CPU % |
|---|---|---|---|---:|---|---|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | **required** | **required** | **required** | **required** | 0 | **required** | **required** | 0 |
| … | … | … | … | **required** | **required** | **required** | **required** | **required** | **required** | **required** | **required** |
| 1 | 1 | 1 | 1 | **required** | **required** | **required** | **required** | **required** | **required** | **required** | **required** |

Report mechanism cost independently: analyzer/build cost, extra controller allocation and CPU time, telemetry overhead, syscall duration, faults and reload latency. Evaluate cold-rank weights and byte budgets rather than presenting only top-5 output.

### Generality and adverse workloads

Add at least one second Linux embedded platform (for example ARM64 SBC with constrained cgroup memory) and workloads spanning steady playback, allocation bursts, application switching, native interop intensity, hot-code reuse, low/slow storage, and an eight-hour endurance script. Document every state transition. For endurance evidence, provide multiple independent eight-hour runs, OOM/kernel logs, censoring rules, telemetry definitions, and aggregate traces. Five short runs must not support a production-stability claim.

## Artifacts and exact boundary table

Release, where licensing permits: vendor runtime name and source revision; minimal runtime patch; build flags and `INITIAL_ALLOC` values per architecture; exposed host interfaces; native helper; analyzer rules/CodeFix (or remove any CodeFix claim); controller config; workload driver/state machine; measurement and bootstrap scripts; anonymized per-run traces; and hashes. Clearly mark this public kit's user-space compaction event and GC telemetry as analogues, not the production patch.

## Presentation and consistency audit

1. Consolidate Design into **Static interventions**, **Adaptive controller** (telemetry, prediction, actions, guards), and **Reclamation implementation**. Consolidate Evaluation into **Method**, **Experimental results** (RQ1–RQ3), **Adverse/generalization**, and **Limitations**.
2. Remove every `Appendix ??`; integrate the useful appendix material into the main text and remove blank pages.
3. Keep one canonical quantitative-results table; delete duplicated Tables IV/IX and generate abstract/conclusion numbers from it.
4. Correct the static-baseline prose to agree with its table. Replace “4 ms squared” with the actually measured latency statistic and unit (for example, `p99 pause = 4 ms`) only if supported.
5. Reconcile 19%, 35%, OOM, eight-hour, and production claims against trace-backed outcomes. Distinguish RSS, PSS, managed heap, and `Private_Clean`; state numerator, denominator, statistic, and confidence interval.
6. Put the ARM32/ARM64 2.6× annotation on the plotted data and improve captions so figures stand alone.
7. Tighten the abstract after results are final: mechanisms, boundary, device/run count, held-out comparison, consistent effect sizes, uncertainty, and limitation.
