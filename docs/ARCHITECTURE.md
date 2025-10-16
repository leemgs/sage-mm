# Architecture Overview

**Signals**
- `Lgc` – last GC pause (ms), measured via `GC.RegisterForFullGCNotification` fallback / Stopwatch regions
- `Fh` – heap fragmentation proxy (%), estimated from LOH + pinned bytes + allocation churn
- `Pf` – page-fault proxy (faults/s), read from `/proc/self/status` (`MajFLT`, `MinFLT`) deltas
- `ΔM` – RSS delta (MB), from `/proc/self/statm`

**Control**
- `T_flush ∈ [Tmin, Tmax]` – page-cache flush interval
- Compaction gating via policy hook: `if Fh < H -> disable_compaction` (demo: print & record)

**Schedulers**
- EWMA: `T_flush(t+1) = β·T_flush(t) + (1-β)·Lgc/L_target`
- Online ridge regression (SGD step): `w_{t+1} = w_t - η(x_t(x_t^T w_t - y_t) + λ w_t)`

**Safety**
- Flush only **read-only** mappings; skip dirty/writable segments
- Hysteresis on intervals; cooldown between flushes
- Bounded GC gating; never starve compaction under high Fh

**Extensibility**
- Replace Telemetry readers with runtime/ETW/GCEventPipe
- Replace Policy hooks with actual CoreCLR hosting APIs on your platform
