# Architecture and implementable control definition

## Coordinated boundary

SAGE-MM coordinates three lifecycle stages through a shared objective: lower peak resident memory without violating pause, fault-rate, or responsiveness SLOs. The **static** runtime heap configuration establishes an architecture-appropriate operating region; the **compile-time** analyzer reduces avoidable managed/native allocations; and the **runtime-adaptive** controller gates compaction and clean-page reclamation using common telemetry. Calling the complete system “adaptive” refers to runtime selection of the latter actions, not to runtime mutation of the first two components.

## Signals, units, and objective

At sample `t`, features are divided by explicit targets and clipped to `[0,2]`: GC pause / 30 ms, fragmentation / 0.20, faults/s / 100, and positive RSS growth / 50 MB. Thus the terms are dimensionless. Observed pressure is their equal-weight mean:

`y(t) = clip((pause' + fragmentation' + faults' + rss-growth') / 4, 0, 2)`.

Equal weights (`alpha=beta=gamma=delta=0.25`) encode equal SLO importance; deployments must preregister different weights rather than optimize them on reported test traces. The ML prediction `y-hat(t)` is the online ridge model's one-step pressure prediction. At `t`, the learner updates the prediction made from `x(t-1)` against `y(t)`, preventing same-observation fit/report leakage. Features, initialization (all-zero weights), learning rate (`5e-4`), ridge penalty (`1e-4`), and update schedule are implemented in `DecisionEngine`.

## Actions and guards

The action space is flush interval `[Tmin,Tmax]` and compaction enable/disable. Pressure above 1.1 shortens the interval by 20%; below 0.9 lengthens it by 20%; the dead-band leaves it unchanged. Compaction is disabled below 7% fragmentation and re-enabled otherwise. Policy enforcement suppresses reclamation above 500 faults/s and enforces a 10-second cooldown. No “GC interval” is controlled.

The EWMA comparison uses the same normalized pressure and bounds, with coefficient 0.85. Static, EWMA, and online ridge therefore differ only in policy, not telemetry or action space.

## Assembly coldness and K

For candidate assembly `a`, normalize age since last access, access count, and clean bytes within the candidate set:

`Cold(a) = 0.6 age'(a) + 0.3 (1 - frequency'(a)) + 0.1 clean-bytes'(a)`.

Candidates are sorted descending. Selection stops when their cumulative clean bytes reaches the configured reclamation budget; consequently `K` is workload- and budget-dependent rather than arbitrarily fixed at five. `AssemblyColdness.Select` is the executable definition.

## Page-reclamation safety

The native helper parses page-aligned ranges from `/proc/self/maps`, accepts only private file-backed `r--p`/`r-xp` mappings, and never targets writable or anonymous memory. `madvise(MADV_DONTNEED)` is advisory and concurrent execution remains valid, but a later access may fault the file-backed page back in. Failures are contained per range and surfaced as a negative/partial result. A production port must additionally validate `Private_Clean` from `/proc/self/smaps`, use a module allowlist, record minor/major faults and syscall errno, and abort under the quantitative fault-rate guard. The demo's map-level approximation must not be represented as a private-clean measurement.
