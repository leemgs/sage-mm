# Extension-Experiment Data Schemas

This document defines the CSV schemas for the three parts of the evaluation
protocol that are currently stated as future work in the manuscript
(Section "Limitations"): the per-architecture **heap sweep** (RQ1-extended),
the isolated **interop** micro/macro benchmarks (RQ2-extended), and the
**endurance & adverse** battery (RQ3-extended).

Collect real device runs into files matching these schemas, drop them under
`paper/generated/evaluation-data/`, validate with
`python3 scripts/validate_bundle.py`, and the results pipeline
(`scripts/make_results.py`) can be extended to render them. **You run the
experiments; the schema and validator make the data drop-in.**

## Conventions (shared with the existing bundle)

- One row **per run** (not per aggregate). Aggregation (mean, bootstrap CI) is
  computed by the pipeline, never pre-baked.
- Provenance columns on every row:
  - `data_status` — `measured` for real device runs.
  - `synthetic` — `false` for real measurements. The pipeline's measurement
    gate stays closed while any reporting row is `synthetic=true`.
  - `n_runs` — the intended number of independent runs for that condition.
  - `seed` — the workload/state-machine seed used for reproducibility (this is
    a *workload* seed, not a data-generation seed).
  - `run_id` — 1..`n_runs`, unique within a condition.
- `platform` uses the real device identifier (e.g. `ARM32`, `ARM64`, or a
  concrete model string), not a placeholder.
- Failed or censored runs are **kept**, with `censored=true` and a
  `censor_reason`; they are excluded from performance means but counted.

## 1. Heap sweep — `heap_sweep_30run.csv` (RQ1-extended)

Isolates the effect of the runtime build's `INITIAL_ALLOC` per architecture.

| column | type | meaning |
|---|---|---|
| `data_status` | enum | `measured` |
| `synthetic` | bool | `false` for real runs |
| `n_runs` | int | intended runs per (platform, initial_alloc) |
| `seed` | int | workload seed |
| `platform` | str | device id (e.g. `ARM32`, `ARM64`) |
| `initial_alloc_mb` | float | swept `INITIAL_ALLOC` value (MiB) |
| `run_id` | int | 1..n_runs |
| `peak_pss_mb` | float | peak proportional set size (MiB) |
| `gc_count` | int | completed collections in the run |
| `gc_p50_ms` | float | median GC pause (ms) |
| `gc_p95_ms` | float | 95th-percentile GC pause (ms) |
| `gc_p99_ms` | float | 99th-percentile GC pause (ms) |
| `gc_max_ms` | float | max GC pause (ms) |
| `compaction_ms` | float | total compaction work (ms) |
| `resident_mb` | float | mean resident memory (MiB) |
| `censored` | bool | true if the run was censored |
| `censor_reason` | str | reason, or empty |

## 2. Interop — `interop_30run.csv` (RQ2-extended)

Isolates value-type (class→struct) interop conversion with native-ABI checks.

| column | type | meaning |
|---|---|---|
| `data_status` | enum | `measured` |
| `synthetic` | bool | `false` |
| `n_runs` | int | runs per (platform, treatment, benchmark) |
| `seed` | int | workload seed |
| `platform` | str | device id |
| `treatment` | enum | `class` (baseline) or `struct` (value-type) |
| `benchmark` | enum | `micro` or `macro` |
| `run_id` | int | 1..n_runs |
| `allocated_bytes` | float | total managed bytes allocated |
| `allocation_rate_mb_s` | float | allocation rate (MiB/s) |
| `peak_pss_mb` | float | peak PSS (MiB) |
| `gc_p99_ms` | float | 99th-percentile GC pause (ms) |
| `throughput_ops_s` | float | benchmark throughput (ops/s) |
| `copy_cost_ns` | float | mean per-call marshalling/copy cost (ns) |
| `native_abi_ok` | bool | native-ABI correctness check passed |
| `censored` | bool | true if censored |
| `censor_reason` | str | reason, or empty |

## 3. Endurance & adverse — `endurance_adverse_30run.csv` (RQ3-extended)

Multi-hour endurance and the adverse-injection battery.

| column | type | meaning |
|---|---|---|
| `data_status` | enum | `measured` |
| `synthetic` | bool | `false` |
| `n_runs` | int | runs per (platform, treatment, stress) |
| `seed` | int | workload seed |
| `platform` | str | device id |
| `treatment` | str | one of the named baselines (e.g. `Ridge-GIR`) |
| `stress` | enum | `cold`, `hot_reuse`, `switch_1s`, `switch_5s`, `switch_10s`, `slow_storage`, `madvise_fail`, `fault_storm`, `endurance_8h` |
| `run_id` | int | 1..n_runs |
| `duration_s` | float | run wall-clock duration (s) |
| `private_clean_before_mb` | float | `Private_Clean` from smaps before (MiB) |
| `private_clean_after_mb` | float | `Private_Clean` from smaps after (MiB) |
| `minor_faults` | int | minor page faults |
| `major_faults` | int | major page faults |
| `bytes_read_mb` | float | storage bytes read during refault (MiB) |
| `reload_latency_ms` | float | code-reload latency (ms) |
| `input_p99_ms` | float | 99th-percentile input latency (ms) |
| `frame_drops` | int | dropped frames |
| `guard_activations` | int | hot-reuse / cooldown / fail-closed guard hits |
| `oom_events` | int | OOM-killer or watchdog events |
| `censored` | bool | true if censored (e.g. OOM) |
| `censor_reason` | str | reason, or empty |

## Validation

```bash
python3 scripts/validate_bundle.py            # validate all known bundle files
python3 scripts/validate_bundle.py PATH.csv   # validate one file
```

The validator checks the header against the schema, that provenance columns are
present and consistent, that `run_id` covers `1..n_runs` per condition, and that
no reporting row is `synthetic=true`. It does **not** and cannot certify that
the numbers came from real hardware — that is the investigator's responsibility.
