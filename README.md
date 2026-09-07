# SAGE-MM

## Title

**SAGE-MM: Coordinating Heap Configuration, Interop Allocation, and Page Reclamation in Memory-Constrained Embedded .NET Firmware**

- Author: Geunsik Lim (Sungkyunkwan University, Suwon, South Korea)

- Submission Target: *Journal of Systems Architecture* (Elsevier)

## Abstract

Severely memory-constrained embedded devices (digital TVs, set-top boxes, etc.) handle the **managed heap**, **native interop**, and **file-based execution code mapping** together within a single process budget. However, these layers are conventionally tuned independently of each other; while reasonable locally, this is vulnerable overall. (e.g., growing the nursery reduces GC frequency but increases resident memory, while aggressively reclaiming code pages reduces resident memory but causes page faults and latency to spike during app switching.)

SAGE-MM is a design that **cooperatively coordinates** these three layers under a single memory budget. Its components are (1) build-time managed heap configuration, (2) reviewed source-time interop conversion, and (3) online reclamation scheduling including runtime host compression gates. The design combines existing proven mechanisms through **constrained action space, normalized telemetry, hysteresis, and threshold fallback**.

The public implementation provides a controller and native mapping helpers, while actual deployment requires vendor runtime integration and device instrumentation. The evaluation records device identification information, runtime/firmware revision, workload and treatment configuration, standalone execution times, and raw measurement sources. Performance metrics (peak PSS, allocation rate, GC tail pause, page fault rate, input tail latency, controller CPU) are reported individually for each measurement condition, and failed or terminated runs are retained in the inventory. **Empirical claims are limited to the scope of the provided experiment manifest and do not assume benefits for unmeasured configurations.**

## Key Ideas

### 1. Problem Statement — The Vulnerability of Independent Tuning
The effectiveness of individual mechanisms (larger nurseries, value types, `madvise`-based reclamation, lightweight online predictors) is already established. The core question is whether they can be **coordinated without compromising each other under a single process memory budget**. In other words, it is not about creating a new GC, but **cross-layer integration/control research**.

### 2. Distinguishing Action Boundaries Based on Lifecycle and Adaptability

| Mechanism | Lifecycle | Online Adaptability? |

|---|---|---|

| Heap build configuration (`INITIAL_ALLOC`) | Vendor runtime build | No |

| Value type interop conversion (class→struct) | Source/recompile | No |

| Reclamation & compression control | Runtime, Online | **Yes** |

The first two (static interventions) **pre-reduce** the load the controller will handle, and only the third adapts at runtime. It is clear that calling all three "adaptive components" is an overstatement.

### 3. Narrow and Safe Online Controller

- **Normalized Telemetry**: GC latency $L_{gc}$, fragmentation $F_h$, page fault rate $P_f$, and resident increase $\Delta M$ are normalized to dimensionless and clamped to $[0,2]$.

Pressure $y$ is defined as the maximum value of service goal violation (preventing unit mixing).

- **Narrow Action Space**: Adjust only one **Recovery Cycle $T$** and one **Compression Gate** →

Ensures all safety attributes can be specified and enforced.

- **3 Policies**: Threshold (non-learning), EWMA, Ridge (online learning). Can be swapped under the same boundary, telemetry, and cooldown.

- **Prequential Learning**: Calculates predictions before updates and freezes weights during reporting. Separates tuning and reporting traces.

- **Hysteresis & Fail-Closed**: Dual threshold gate to prevent compression starvation,

Prioritizing safety by maintaining previous values, enabling compression, and suppressing recovery in case of incorrect telemetry.

### 4. Conservative Page Recovery

- Ranks modules by **coldness score** (Recency 0.6 + Frequency 0.3 + Size 0.1) and recovers only the minimum prefix $K$ that fills the byte budget (not a fixed number).

- Native helpers accept only private `r--p`/`r-xp` file mappings, rejecting anonymous, writable, shared, and deleted mappings. `madvise(MADV_DONTNEED)` is not unmapped, so it may fail again upon re-access. Recently accessed modules are excluded via a hot-reuse guard.

### 5. Design for Falsifiable Evaluation

- **RQ1**: Does heap configuration by architecture change GC/compression costs?

- **RQ2**: Does value type conversion + guarded retrieval safely reduce the footprint without faults?

- **RQ3**: Does online scaling improve robustness compared to fixed/threshold/EWMA?

- 16 full-factor experiments (G, I, R, C), held-out policy comparisons, adversity workload stress, 8-hour endurance runs. Minimum 30 independent resets per case, bootstrap confidence interval reporting, failure/mid-run preservation.

### 6. Core Principles — Honest Measurement Contracts

- Specify that the demo signals in the public kit are not production instruments.

- Only conditions with a measurement manifest appear in the results table (no extrapolation).

- Missing metrics are left as missing rather than being replaced with zeros. The script does not insert predicted improvements or assumed safety results.

## Repository Configuration

```
paper/
├── main.tex                     # Authoritative manuscript (Elsevier elsarticle class)
├── sagemm.bib                   # References
├── elsarticle.cls / .bst        # Elsevier templates
└── generated/
    ├── evaluation-data/         # 30-run measurement bundle (per-run CSVs + summary)
    └── *.tex / *.json           # Result fragments generated from the bundle
scripts/
├── make_results.py              # Render evaluation-data/ into the results fragments
└── build.sh                     # Regenerate results, compile, and emit code/main.pdf
code/
└── main.pdf                     # Build output (Journal of Systems Architecture PDF)
```

## Building the PDF

```bash
bash scripts/build.sh
```

This regenerates the results fragments from
`paper/generated/evaluation-data/`, compiles `paper/main.tex` with `pdflatex`
+ `bibtex` (Elsevier `elsarticle` class), and writes the result to
**`code/main.pdf`**.

Requirements (Debian/Ubuntu): a TeX Live install providing `pdflatex`,
`bibtex`, and the `elsarticle` class, e.g.

```bash
sudo apt-get install -y --no-install-recommends \
  texlive-latex-base texlive-latex-recommended texlive-latex-extra \
  texlive-science texlive-fonts-recommended texlive-publishers
```

### Results and the measurement gate

`scripts/make_results.py` reads the 30-run bundle under
`paper/generated/evaluation-data/`: it computes each table cell as the mean with
a two-sided 95% **percentile bootstrap** CI (10,000 resamples) directly from the
per-run values in `absolute_results_30run.csv`, and renders the normalized
policy-index table and the three figures from `policy_indices_30run.csv`. The
manuscript is marked submission-ready only when the bundle holds genuine
measurements (`data_status=measured`, `synthetic=false`, `n>0`); otherwise the
build stays fail-closed with a NOT-FOR-SUBMISSION watermark. Edit the CSV bundle
and rerun the build to refresh every table, figure, and the readiness gate.

### Submission materials

- `paper/HIGHLIGHTS_JSA.md` — Elsevier Highlights (≤85 chars each).
- `paper/COVER_LETTER_JSA.md` — cover letter to the JSA editor.

### Extending the evaluation

The future-work experiments (per-architecture heap sweep, isolated interop
benchmarks, endurance/adverse battery) have drop-in schemas and collectors:

- `docs/EXPERIMENT_SCHEMAS.md` — CSV schemas and conventions.
- `paper/generated/evaluation-data/templates/` — header-only CSV templates.
- `scripts/collect/` — collector skeletons; implement the `run_one_condition`
  device hook, run on the target device, then drop the CSV into the bundle.
- `scripts/validate_bundle.py` — validates a bundle CSV against its schema and
  the measurement gate (`python3 scripts/validate_bundle.py`).