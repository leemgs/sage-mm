# Reference-kit measurement bundle (ARM64 Linux, non-.NET proxy)

> **Scope — read before citing.** This bundle is a **reference-kit /
> methodology-validation** dataset. It is **not** the SAGE-MM manuscript's
> evidence and **must not** populate the paper's Results, abstract, figures, or
> conclusion. See "What this is / is not" below and
> `paper/docs/JOURNAL_SELECTION_JSA.md` §4.

## Files (raw, preserved verbatim as delivered)

| File | Contents |
|---|---|
| `manifest.json` | Run counts and generation metadata. |
| `provenance.csv` | Collector, platform, kernel, device-id prefix, collector SHA-256. |
| `per_run_measurements.csv` | 48 per-run rows: 16 factorial treatments × 3 independent runs. |

The three files are stored exactly as received so their internal provenance
and self-labels are auditable; this README adds scope, it does not alter them.

## What was measured

- **Design:** the full `2×2×2×2` `G·I·R·C` factorial (heap config, interop
  conversion, page reclamation, coordinated controller) — 16 treatments —
  each run 3 times → **48 runs**. This matches the manuscript's preregistered
  factorial structure, which is why the bundle is useful for validating the
  analysis/summary pipeline.
- **Metrics per run:** wall-clock `elapsed_s`, `peak_rss_kib`, `pss_kib`,
  `private_clean_kib`, `allocated_bytes`, allocation rate, `gc_p99_ms`,
  minor/major faults, fault rate, `input_p99_ms`, controller CPU %, iterations.
- **Magnitude:** runs are sub-second micro-benchmarks (≈8–18 ms each), not the
  multi-hour endurance sessions the manuscript's evaluation protocol requires.

## What this is / is NOT

**It IS** an honest, real measurement of the *reference-kit control/analysis
path* on one ARM64 Linux host — useful to:
- exercise `scripts/summarize_results.py` bootstrap CIs and the factorial
  table/figure layout on real (non-synthetic) numbers, and
- demonstrate that the controller logic and safety guards in `code/` run and
  produce well-formed telemetry independently of proprietary firmware.

**It is NOT** SAGE-MM DTV firmware evidence, for reasons visible in its own
provenance:

1. **Runtime mismatch.** `provenance.csv` records
   `collector = Python resource + /proc/self/smaps_rollup + monotonic_ns`,
   `python = 3.12.13-arm64`, and `eventpipe = used_non_dotnet_research_actual_data`.
   The measured process is a **Python proxy — explicitly non-.NET**. The
   manuscript's target runtime is the **vendor Mono / .NET 6 fork** inside DTV
   firmware.
2. **Firmware unavailable.** `firmware_vendor`, `firmware_version`, and
   `firmware_date` are all `unavailable`, so this cannot anchor any
   firmware-specific claim.
3. **Single device / single kernel.** One `device_id` prefix
   (`bb2498ecbe619967`), kernel `6.18.35`; no ARM32 device, no independent
   third platform, no endurance/device-hours.

> **Note on the bundle's self-labels.** This upload's own text fields were set
> to `study_scope = research_actual_sage_mm`, `data_status = observed`, and the
> disclaimers *"measured actually on real devices"* /
> *"SAGE-MM manuscript evidence on the embedded real devices."* Those labels
> are **not sufficient** to make the data manuscript evidence: the collector is
> a non-.NET Python process and the firmware fields are `unavailable`. Per the
> repository's reporting rule (`paper/docs/ACTUAL_RESULTS.md`) a value is only
> a "result" when it comes from the observed DTV bundle on the evaluated
> runtime. Relabeling a proxy does not change what was measured, so this bundle
> stays scoped as reference-kit validation only.

## Permitted use

- Pipeline / methodology validation and reproducibility demonstration of the
  reference kit — always disclosed as an ARM64 non-.NET Python proxy.

## Prohibited use

- Populating `paper/generated/observed-results.tex`, flipping
  `\includesimulationfalse`, or removing the `SIMULATION-ONLY` watermark.
- Quoting any value here as a PSS / tail-pause / fault / latency "result",
  "improvement", or "deployment evidence" for SAGE-MM.
