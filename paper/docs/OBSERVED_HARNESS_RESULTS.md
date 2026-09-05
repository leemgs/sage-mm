# Observed proxy-harness factorial (ARM64 Linux) — not firmware evidence

> **Status: observed / non-synthetic, but a proxy harness.** This document
> records a real, measured factorial run supplied as a provenance-backed
> bundle (`data_status=observed`, `synthetic=false`). It is **not** vendor DTV
> Mono/.NET6 firmware evidence and does not satisfy the measured-result bar in
> [`MEASURED_DEVICE_RUN_VALUES.md`](MEASURED_DEVICE_RUN_VALUES.md). The vendor
> DTV result cells therefore remain `NA`; nothing here may be quoted in the
> abstract, Results, or conclusion as an achieved deployment effect.

## What the bundle is

The raw bundle lives in [`code/experiments/observed/`](../../code/experiments/observed/):

| File | Contents |
|---|---|
| `manifest_sage_mm_observed.json` | Run manifest: 16 treatments × 3 runs = 48 runs, generated UTC, disclaimers. |
| `provenance_sage_mm_observed.csv` | Collector identity, kernel/platform, firmware fields, hashes. |
| `per_run_measurements_sage_mm_observed.csv` | 48 independent run rows with per-run metrics. |
| `observed_runs.csv` | Analysis-contract projection produced by `convert_observed_bundle.py`. |
| `observed_factorial_summary.json` | Deterministic bootstrap summary from `summarize_results.py`. |

## Provenance (carried verbatim, not fabricated)

- **Collector:** `Python resource + /proc/self/smaps_rollup + monotonic_ns`.
- **Substrate:** `Linux-6.18.35-arm64`, Python `3.12.13-arm64`.
- **GC field:** `gc_p99_ms` is **Python `gc.collect` timing**, a proxy for — not
  a measurement of — a managed .NET/Mono GC pause.
- **Memory field:** PSS is the process-wide `smaps_rollup` share; it is **not**
  per-mapping `Private_Clean` reclaimed bytes.
- **EventPipe:** `used_non_dotnet_research_actual_data` — no vendor GC/EventPipe trace.
- **Firmware vendor / version / date:** `unavailable` (not independently recoverable).
- **Target environment:** `DTV Mono/.NET6` is **user-specified**, not verified from provenance.
- **`provenance_verification`:** `partial`.
- **Device id (sha256 prefix):** `bb2498ecbe619967`.
- **Collector sha256:** `413a1d7e0a574cfc9e6d8e4f689e2a802701cfd26be6b8be85383971bf00fa5e`.

## Reproduction

Deterministic; no network, no hidden state:

```bash
cd code
python3 scripts/convert_observed_bundle.py      # bundle -> observed_runs.csv (fail-closed on synthetic)
python3 scripts/summarize_results.py \
    experiments/observed/observed_runs.csv \
    --output experiments/observed/observed_factorial_summary.json
python3 scripts/make_observed_results_tex.py    # summary -> paper/generated/observed-results.tex
```

## Observed factorial (run-level means, fixed-seed 95% bootstrap CI)

Cells are the 2⁴ `GIRC` treatments (heap, interop, reclamation, controller);
`G0I0R0C0` is the Stock reference. Means and 95% CIs are over `n=3` independent
runs per cell, seed `20260829`, 10 000 resamples. Values as `mean [lo, hi]`.

| Cell | Peak PSS (MiB) | Alloc (MiB/s) | GC-proxy p99 (ms) | Ctrl. CPU (%) |
|---|---|---|---|---:|
| G0I0R0C0 | 19.97 [19.97, 19.98] | 1062.3 [1028.2, 1112.5] | 0.807 [0.788, 0.832] | 0.000 |
| G0I0R0C1 | 12.68 [12.66, 12.71] | 1378.6 [1365.7, 1387.5] | 0.791 [0.773, 0.804] | 0.694 |
| G0I0R1C0 | 12.22 [12.22, 12.22] | 1396.2 [1360.1, 1414.3] | 0.810 [0.797, 0.825] | 0.000 |
| G0I0R1C1 | 12.22 [12.22, 12.22] | 1388.8 [1379.5, 1401.1] | 0.788 [0.785, 0.792] | 0.029 |
| G0I1R0C0 | 21.64 [21.60, 21.68] | 1694.1 [1653.9, 1734.2] | 0.817 [0.811, 0.827] | 0.000 |
| G0I1R0C1 | 18.71 [18.71, 18.71] | 1807.3 [1763.4, 1851.5] | 0.862 [0.823, 0.931] | 0.314 |
| G0I1R1C0 | 18.71 [18.71, 18.71] | 1903.4 [1882.7, 1941.2] | 0.860 [0.832, 0.889] | 0.000 |
| G0I1R1C1 | 18.72 [18.72, 18.72] | 1879.3 [1861.7, 1895.0] | 0.830 [0.811, 0.856] | 0.014 |
| G1I0R0C0 | 18.72 [18.72, 18.72] | 750.2 [663.2, 797.8] | 1.043 [0.829, 1.374] | 0.000 |
| G1I0R0C1 | 18.72 [18.72, 18.72] | 940.5 [906.0, 981.1] | 0.815 [0.769, 0.840] | 0.519 |
| G1I0R1C0 | 18.73 [18.72, 18.73] | 958.8 [924.7, 976.0] | 0.806 [0.773, 0.866] | 0.000 |
| G1I0R1C1 | 18.73 [18.73, 18.73] | 922.6 [893.5, 955.4] | 0.828 [0.782, 0.891] | 0.028 |
| G1I1R0C0 | 19.16 [19.11, 19.22] | 1557.6 [1525.4, 1582.1] | 0.840 [0.799, 0.898] | 0.000 |
| G1I1R0C1 | 18.74 [18.74, 18.74] | 1552.6 [1518.8, 1575.0] | 0.805 [0.792, 0.815] | 0.356 |
| G1I1R1C0 | 18.74 [18.74, 18.74] | 1546.4 [1509.8, 1566.0] | 0.841 [0.809, 0.869] | 0.000 |
| G1I1R1C1 | 18.74 [18.74, 18.74] | 1585.5 [1501.6, 1643.3] | 0.853 [0.810, 0.930] | 0.017 |

## Honest reading of these numbers

- **Directionally mixed.** Reclamation (`R=1`) lowers PSS in the `G0I0` corner
  but interop (`I=1`) raises the allocation-rate proxy rather than lowering it,
  contrary to the preregistered hypotheses. On a proxy harness this is expected
  and is reported, not smoothed away.
- **Near the noise floor.** Per-run wall time is a sub-10 ms micro-run and
  `input_p99` sits in fractions of a millisecond, so several metrics are
  dominated by measurement noise. `fault_rate_s` collapses to ≈0 for most
  non-Stock cells — an artifact of the Python collector, not a .NET page-fault
  result — and is omitted from the headline table for that reason (it remains in
  the raw CSV).
- **Controller CPU** is well under the 1.5% policy ceiling in every cell where
  the controller is active (`C=1`), consistent with a lightweight scheduler.

## Why the vendor cells stay `NA`

Per [`MEASURED_DEVICE_RUN_VALUES.md`](MEASURED_DEVICE_RUN_VALUES.md), a measured
DTV result requires a vendor Mono/.NET GC or EventPipe trace, per-mapping
`Private_Clean` before/after accounting, ≥30 independent cold-reset runs per
cell, and ≥30 min / 8 h durations. This bundle supplies none of those: it is a
Python proxy, `n=3`, micro-run, firmware-unverified. It is genuine observed
evidence **for the harness and analysis pipeline**, and is included on that
basis only.
