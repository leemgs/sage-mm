# Reviewer 4 manuscript-ready revision

This file contains replacement prose for the manuscript. Bracketed fields require results from the protocol in `REVISION_NOTES.md`; they must not be populated from the previous five-run data unless that dataset actually supports the stated statistic.

## Revised title

**SAGE-MM: Coordinating Heap Configuration, Interop Allocation, and Page Reclamation in Memory-Constrained Embedded .NET Firmware**

The title deliberately removes “self-adaptive framework” as the umbrella description: only the runtime controller adapts online.

## Revised abstract

Memory-constrained embedded devices combine managed heaps, native interoperability, and file-backed executable mappings within one process budget, but these layers are commonly tuned independently. We present SAGE-MM, an engineering design that coordinates a static architecture-specific heap configuration, source-reviewed value-type interop conversion, and bounded online control of compaction and clean-page reclamation. SAGE-MM does not introduce a new collector, interop representation, reclamation syscall, or learning algorithm; its contribution is an implementable cross-layer policy, explicit safety guards, and deployment evidence from embedded .NET firmware. The controller uses normalized GC-pause, fragmentation, page-fault, and RSS-growth telemetry and selects a reclamation interval using either a tuned threshold rule, EWMA, or online ridge regression. Invalid telemetry disables reclamation and restores compaction without updating the model. Across **[N devices/platforms]**, **[N workloads]**, and **[N independent runs per condition]**, the full system changed peak PSS by **[effect, 95% CI]**, GC p99 pause by **[effect, 95% CI]**, and input/frame p99 latency by **[effect, 95% CI]** relative to **[canonical baseline]**. A full factorial ablation attributes these changes to each mechanism and reports controller overhead and refault cost. The evidence applies to the tested Linux-based firmware and workloads; generality to other embedded managed runtimes remains to be established.

## Revised introduction: scope and contributions

The systems question is not whether larger nursery sizes, value types, `madvise`, or lightweight online predictors work in isolation. Each is established. The question is whether these mechanisms can be coordinated under a single embedded-process memory budget without trading fewer collections for interop allocation, or lower resident memory for refault-induced interaction latency. This framing makes the work a measured integration and control study rather than a claim that its constituent mechanisms are new.

This paper makes four bounded contributions:

1. It characterizes managed-heap, interop-allocation, and file-backed executable-page pressure using identical application transitions on the evaluated firmware and reports architecture-specific rather than universal effects.
2. It specifies a cross-layer action boundary: heap sizing is a runtime-build decision, value-type conversion is a reviewed source/recompile decision, and only reclamation scheduling and compaction gating change online.
3. It provides an implementable controller definition with dimensionless features and target, causal update order, bounded actions, hysteresis, cooldown, fail-closed telemetry handling, and an explicit non-learning threshold fallback.
4. It evaluates individual and interaction effects through a factorial ablation and compares fixed, tuned-threshold, EWMA, and ridge policies on held-out traces while reporting runtime overhead, page faults, reload latency, and tail responsiveness.

We make no claim that SAGE-MM is a new garbage collector or that results from two DTV models establish all embedded .NET deployments. Claims outside the measured device, memory, runtime revision, and workload matrix are hypotheses for future evaluation.

## Related-work positioning

Organize related work by mechanism rather than listing systems chronologically:

* **Managed-runtime collection and adaptive GC:** compare action space, concurrency, pause/throughput objective, runtime changes, and hardware assumptions. Explain that advanced collectors such as LXR and Platinum change collection itself, whereas SAGE-MM coordinates an existing vendor collector with process-level actions. If these collectors cannot be ported to the exact firmware, say so and do not claim empirical superiority.
* **Heuristic and learned controllers:** compare fixed intervals, a tuned pressure threshold, EWMA, and ridge under the same trace split and action bounds. Storage-GC learning systems are conceptual precedents, not executable managed-runtime baselines.
* **Application-directed reclamation:** compare `madvise`/discard mechanisms by candidate identification, dirty-page safety, concurrency with unload/execution, refault behavior, and feedback signals.
* **Managed/native interop:** distinguish ABI/source transformations from transparent runtime optimization and state ownership, layout, and recompilation requirements.

End each subsection with a limitation matrix rather than a generic novelty statement. The differentiator to test is whether coordination reduces cross-layer regressions relative to independently tuned components.

## Controller and robustness paragraph

At decision interval `t`, the controller normalizes pause, fragmentation, page-fault rate, and positive RSS growth against declared service objectives. The target is the maximum normalized objective violation, clamped to `[0,2]`; the ridge prediction is computed before its causal SGD update. Training and reporting traces are disjoint, and reporting freezes weights. Actions are bounded to `[Tmin,Tmax]`; two fragmentation thresholds and a maximum of three deferrals prevent compaction starvation. Non-finite or out-of-range telemetry holds the bounded prior interval, enables compaction, suppresses reclamation, records `InvalidTelemetry`, and skips learning. Native syscall failure, no eligible cold module, active cooldown, or hot-reuse exclusion is a measured no-op. Persistent prediction saturation triggers the predeclared tuned-threshold policy. Evaluation reports the frequency, duration, and outcome of every fallback class.

## Evaluation replacement

### Platforms and workloads

The main table must include at least one additional independently assembled embedded Linux platform beyond the 1 GB ARM32 and 3 GB ARM64 DTV-class devices. For every platform report SoC/core count, ISA, physical/cgroup memory, swap, storage, kernel, runtime name and commit, GC patch hash, firmware image, compiler, and thermal/power policy. Include steady playback, allocation burst, interop-intensive, hot-code reuse, rapid switching, slow-storage, and multi-hour endurance workloads with published state transitions and seeds.

### Baselines

Use these names without aliases: `Stock`, `Static-G`, `Static-GI`, `Static-GIR`, `Threshold-GIR`, `EWMA-GIR`, and `Ridge-GIR`. Tune threshold/EWMA/ridge only on training traces. Apply identical bounds, telemetry, cooldown, and candidate budget to controller comparisons. Report why any advanced collector cannot execute on the vendor runtime instead of treating its absence as evidence of advantage.

### Component attribution

Replace the expected-impact Table V with measured rows for the complete `G × I × R × C` design. Report independent-run `n`, effect and 95% bootstrap CI for peak PSS, allocation rate, collection/compaction counts, mean/p95/p99/max pause, reclaimed bytes, minor/major faults, refault latency, frame/input tail latency, controller CPU, and controller allocation. Analyze main and interaction effects; do not infer a component contribution by subtracting results collected under different device states.

### Duration and statistics

Thirty-minute/five-run results may be retained only as pilot evidence. The main claims require preregistered independent repetitions and multi-hour endurance runs. Bootstrap across independent runs, not telemetry samples from one run. Publish per-run aggregates, OOM/kernel events, censoring, missing-data handling, and both tuning and held-out trace identifiers.

## Results-writing constraints

Use a single generated results source for the abstract, tables, figures, and conclusion. Every benefit must name baseline, workload aggregation, statistic, denominator, and confidence interval. Do not interchange RSS, PSS, managed heap, or `Private_Clean`. Annotate the ARM32/ARM64 compaction ratio on its figure only if regenerated data support it. Remove `Appendix ??`, duplicate tables, “4 ms squared,” and all inconsistent aliases. Required definitions and quantitative evidence belong in the main paper; the external artifact contains code and traces, not arguments necessary to interpret the paper.

## Revised limitations

SAGE-MM combines known mechanisms and its novelty is therefore limited to their specified coordination and empirical interaction analysis. Static heap and interop changes require runtime or application rebuilding, and only controller actions are adaptive. `MADV_DONTNEED` can trade PSS for page faults and storage-dependent latency; the guards reduce but do not eliminate that risk. The ridge model is deliberately lightweight and may offer no benefit over a tuned threshold policy; results must report such cases. Firmware hooks, telemetry fidelity, and executable mapping behavior are platform-specific. Consequently, conclusions are restricted to the tested runtime commits, devices, memory limits, storage configurations, and scripted workloads.
