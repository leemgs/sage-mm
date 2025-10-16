# SAGE-MM Reproducibility Kit

This repository contains a minimal, **production-minded** reference implementation of the components described in the SAGE‑MM paper (Self‑Adaptive Memory Management for Smart TV runtimes). It includes:

- A **Self‑Adaptive Controller** with EWMA and online ridge‑regression schedulers
- Runtime **telemetry collectors** (GC pause, fragmentation, page‑fault proxy, RSS deltas)
- **Policy Enforcer** for compaction gating and page‑cache flush scheduling
- **`FlushPECaches()`** per‑process clean‑page dropping via `madvise(MADV_DONTNEED)` (Linux)
- **Value‑type interop** examples and a small **Roslyn analyzer** (DTV0001) to suggest struct conversion
- A **demo workload** that simulates app switches and allocation bursts
- Scripts for building native helpers and running the demo

> ⚠️ This kit focuses on reproducibility and clarity, not drop‑in replacement of .NET internals. Hooks are exposed in user space with safe fallbacks so you can validate behaviors on a dev machine before porting deeper into a vendor runtime.

## Quick Start

### Prerequisites
- Linux (recommended) or WSL2
- .NET 6 SDK or later
- GCC / Clang and `make`
- Permissions to call `madvise()` (normal user is fine)

### Build
```bash
git clone <your-fork-url> sage-mm-repro
cd sage-mm-repro/native/peflush && make
cd ../../src/SageMM.Demo && dotnet build
```

### Run
```bash
cd src/SageMM.Demo
dotnet run -- --mode ml --minutes 2 --flush-min 20 --flush-max 60
```

You should see periodic telemetry prints, adaptive intervals, and successful clean‑page drops. Try `--mode ewma` to compare strategies.

### Project Layout
```
src/
  SageMM.Core/            # controller, telemetry, policy enforcer, interop examples
  SageMM.Demo/            # console demo simulating DTV-like patterns
  RoslynAnalyzer/         # DTV0001 analyzer skeleton to suggest struct conversion
native/
  peflush/                # libpeflush.so exposing per-process clean-page dropping
scripts/
  build.sh                # convenience build
  run_demo.sh             # demo runner
docs/
  ARCHITECTURE.md         # component overview, signals, safety notes
```

## How It Maps to the Paper
- **Self‑Adaptive Controller (EWMA + ML)** controls `T_flush` and compaction gating with bounds and hysteresis. See `SageMM.Core/DecisionEngine.cs` and `SelfAdaptiveController.cs`.
- **FlushPECaches()** enumerates current mappings and issues `madvise(MADV_DONTNEED)` for *clean, read‑only* candidates through `libpeflush.so`. See `FlushPECaches.cs` and `native/peflush/peflush.c`.
- **Value‑type interop** shows how to convert POD wrappers to `struct` and marshal without heap churn. See `Interop/ValueTypes.cs` and `InteropMarshalling.cs`.
- **Telemetry** approximates GC pause, fragmentation, page faults, and RSS drift using managed hooks and `/proc`. See `Telemetry.cs`.
- **Ablations**: Run with `--mode static`, `--mode ewma`, or `--mode ml` to compare behavior.

For the full problem statement, design, and evaluation targets, refer to the SAGE‑MM paper (uploaded with this kit).

## Porting Notes
- The **compaction gating** hook here is a user‑mode analogue. In real firmware, wire it to CoreCLR GC knobs or host APIs.
- The **per‑assembly** flush API in the paper can be built by filtering `maps` entries by module and symbol metadata. The demo drops clean read‑only mappings conservatively.
- Analyzer rules (DTV0001/0002) can be integrated into CI to guide struct migration.

## License
Apache-2.0 (see `LICENSE.md`)

## Acknowledgments
This code is an illustrative companion to the SAGE‑MM research, enabling reproducibility and adaptation to embedded runtimes.
