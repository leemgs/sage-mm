# Architecture and implementable control definition

## System boundary

SAGE-MM coordinates three deliberately distinct interventions:

1. **Runtime-build configuration (static):** changing `INITIAL_ALLOC` requires rebuilding the vendor Mono runtime. It is not in this public kit and is not an online control.
2. **Interop representation (source time):** DTV0001 suggests candidates, but a developer must review the ownership and ABI implications and recompile the application. It is not transparent to existing binaries.
3. **Online policy (adaptive):** the controller changes only the reclamation interval and the compaction gate exposed by the runtime host. This kit models the latter as an event; it does not claim that stock .NET 6 exposes that hook.

The reference projects target `net6.0`. “Mono CoreCLR” is not a runtime name: the deployment studied by the paper must be identified as its vendor revision of the Mono runtime, while this kit runs on any .NET 6-compatible implementation. Supported native reclamation here is Linux on architectures that provide `/proc/self/maps` and `madvise`; the C helper has no architecture-specific instruction code.

## Signals and sampling

Each decision uses the preceding interval's `Lgc` (milliseconds), `Fh` (ratio), `Pf` (minor plus major faults/second), and positive `ΔM` (MiB). The demo's forced Gen-0 pause and fragmentation estimate are proxies; production experiments must use EventPipe/vendor GC telemetry. Fault rate is divided by measured wall-clock sample duration rather than an assumed one-second interval.

## Controller

All initialization, feature scales, thresholds, and update constants reside in `ControllerOptions`. Features are `[1, clamp(Lgc/30), clamp(Fh/0.12), clamp(Pf/100), clamp(max(0,ΔM)/50)]`, each clamped to `[0,2]`. The dimensionless observed pressure is

`y = clamp(max(Lgc/30 ms, Pf/100 s⁻¹, max(0,ΔM)/50 MiB), 0, 2)`.

Thus no coefficient silently combines milliseconds, counts, and MiB. The service-objective maximum makes a breach in any dimension actionable. EWMA uses `T' = βT + (1-β)T/clamp(y,0.5,2)`, with `β=0.85`. The learner predicts `ŷ=clamp(wᵀx,0,2)` and performs online ridge SGD:

`wᵢ ← wᵢ - η[xᵢ(ŷ-y)+λwᵢ]`, where the bias starts at 1 and other weights at 0, `η=5×10⁻⁴`, and `λ=10⁻⁴` initially.

It chooses `T'=T/clamp(0.5+ŷ,0.5,1.5)`, bounded by `[Tmin,Tmax]`. Reported loss is `(ŷ-y)²/2`, computed before the update. Training must occur only on a designated tuning trace; passing `updateModel:false` freezes weights for held-out reporting (alternatively reset and report causal prequential loss). The static comparator changes neither interval nor weights.

In adaptive modes, compaction is disabled below fragmentation 0.05 and forcibly re-enabled at 0.12 or after three deferrals. This two-threshold guard prevents starvation. Static mode leaves compaction enabled, so it is a genuine no-controller baseline. There is no unused “GC interval” variable.

### Fallback and failure cases

Every sample is checked before feature processing. NaN/infinite values, negative pauses or fault rates, and fragmentation outside `[0,1]` trigger a fail-closed decision: hold the previous bounded interval, keep compaction enabled, suppress page reclamation, report `InvalidTelemetry`, and do not update model weights. Valid samples resume normal control. The deployment must separately treat native-helper errors, an unavailable `/proc`, an empty candidate set, and reclamation cooldown as no-op actions and expose counters for each case. Model saturation at 0 or 2 is observable through prediction/loss telemetry; persistent saturation is an operator alert and a reason to revert to the predeclared threshold controller, not to retrain on the reporting trace.

## Coldness and K

For eligible module `a`, idle for at least a configured guard period:

`Cold(a)=0.6 age(a)/maxAge + 0.3[1-accesses(a)/maxAccesses] + 0.1 cleanBytes(a)/totalCleanBytes`.

Candidates are descending by score. K is the smallest prefix whose cumulative clean bytes reaches the configured reclamation byte budget; it is not fixed at five. A recent-access exclusion is the hot-reuse safety guard.

## Native reclamation safety

The helper considers page-aligned ranges supplied by the kernel in `/proc/self/maps`, accepts private `r--p`/`r-xp` file mappings, and rejects anonymous, writable, shared, and deleted-file mappings. `madvise(MADV_DONTNEED)` never unmaps a range: later access can fault file content back in. Each syscall result is checked; zero means no candidate, a positive value is the number dropped, and a negative value is `-errno`/`-EIO`. Callers retain the mapping after failure.

The demo cannot establish that every mapped page is clean because `maps` lacks per-page residency/dirty state. A production port must cross-check `Private_Clean` in `/proc/self/smaps`, use `mincore` only for residency, serialize against module unload, and allowlist executable modules. Experiments must measure minor/major faults, bytes reclaimed, refault/reload latency, storage latency, frame time, and input latency under hot reuse and rapid switching.
