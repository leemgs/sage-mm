# SAGE-MM Reproducibility Kit

This repository contains a minimal reference implementation of components described in the SAGE‑MM study. **The adaptive part is the controller that coordinates reclamation and compaction policy; heap sizing is a build-time runtime patch, and interop conversion is a source-time optimization.** They are complementary interventions, not three independently adaptive algorithms. It includes:

- A **Self‑Adaptive Controller** with EWMA and online ridge‑regression schedulers
- Runtime **telemetry collectors** (GC pause, fragmentation, page‑fault proxy, RSS deltas)
- **Policy Enforcer** for compaction gating and page‑cache flush scheduling
- **`FlushPECaches()`** conservative file-backed mapping reclamation via `madvise(MADV_DONTNEED)` (Linux)
- **Value‑type interop** examples and a small **Roslyn analyzer** (DTV0001) to suggest struct conversion
- A **demo workload** that simulates app switches and allocation bursts
- Scripts for building native helpers and running the demo

> ⚠️ This kit focuses on reproducibility and clarity, not drop‑in replacement of .NET internals. It does not contain the vendor runtime patch or production traces and must not be used as evidence for the paper's reported numbers. Hooks are exposed in user space with safe fallbacks so behaviors can be validated before a vendor-runtime port.

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

You should see periodic telemetry prints, adaptive intervals, and reclamation attempts. Use `--mode static`, `--mode threshold`, `--mode ewma`, or `--mode ml` to compare the declared controller baselines.

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
- **FlushPECaches()** enumerates current mappings and issues `madvise(MADV_DONTNEED)` only for private, file-backed, non-writable candidates. The demo does not prove page cleanliness; production ports must validate `Private_Clean`. See `FlushPECaches.cs` and `native/peflush/peflush.c`.
- **Value‑type interop** shows how to convert POD wrappers to `struct` and marshal without heap churn. See `Interop/ValueTypes.cs` and `InteropMarshalling.cs`.
- **Telemetry** approximates GC pause, fragmentation, page faults, and RSS drift using managed hooks and `/proc`. See `Telemetry.cs`.
- **Controller comparisons**: Run with `--mode static`, `--mode threshold`, `--mode ewma`, or `--mode ml`. These modes do not substitute for the full component ablation or commercial-device evidence.

The exact implementation boundary, controller equations, coldness score, experimental protocol, ablation schema, related-work comparison, and claim audit requested during review are recorded in [`docs/REVISION_NOTES.md`](docs/REVISION_NOTES.md). Raw measurements must be inserted into its schemas; this repository intentionally does not invent missing results.

Reviewer 4's requested manuscript changes are provided as manuscript-ready replacement sections in [`docs/MANUSCRIPT_REVISION.md`](docs/MANUSCRIPT_REVISION.md), including a narrower title/abstract, novelty positioning, controller failure behavior, expanded multi-platform evaluation, quantitative ablation requirements, canonical baseline names, and limitations.

For the full problem statement, design, and evaluation targets, refer to the SAGE‑MM paper (uploaded with this kit).

## Porting Notes
- The **compaction gating** hook here is a user‑mode analogue. In real firmware, wire it to CoreCLR GC knobs or host APIs.
- `ReclamationCandidateTracker` defines a reproducible recency/frequency/size coldness score and selects K from a byte budget. It is **not wired into the demo controller**: the demo currently calls process-wide `FlushAll`, so per-module selection must not be claimed as an end-to-end result. A production integration must connect tracked candidates to `FlushModule`, verify `Private_Clean` from `/proc/self/smaps`, and apply its executable-module allowlist.
- Analyzer rules (DTV0001/0002) can be integrated into CI to guide struct migration.

## License
Apache-2.0 (see `LICENSE.md`)

## Acknowledgments
This code is an illustrative companion to the SAGE‑MM research, enabling reproducibility and adaptation to embedded runtimes.
