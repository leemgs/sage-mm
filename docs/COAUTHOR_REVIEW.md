# Co-author review: TECS submission readiness and path to publication

**Reviewer role:** acting co-author, goal = get SAGE-MM into ACM TECS.
**Date:** 2026-08-31
**Manuscript reviewed:** `paper/sagemm-tecs.tex` (+ generated fragment, bib, docs).

---

## 1. Verdict

**Not submittable yet — but the gap is data, not writing.**

The manuscript is, at the *design and framing* level, at or near TECS quality:
the scope is honest and well-bounded, the system boundary (build-time heap /
source-time interop / online reclamation) is crisp, the controller is fully
specified with dimensionless features, causal update, bounds, hysteresis, and
fail-closed handling, and the evaluation protocol is preregistered and
falsifiable. That is the hard, original intellectual content and it is largely
done.

The blocker is singular and absolute: **there are no measured results.** Every
number in the current PDF is either a *preregistered hypothesis* (Table 3,
normalized to Stock=100) or *fixed-seed synthetic data* (the generated
fragment), and the paper correctly watermarks both as
`SIMULATION-ONLY … NOT FOR SUBMISSION`. The repository's own fail-closed gate
(`scripts/check_submission_readiness.py`) refuses to certify the build while
`\includesimulationtrue` is set, the author metadata is a placeholder,
`observed-results.tex` is absent, and the bibliography still carries
"Verify …" notes. All four conditions currently hold.

I did **not** fabricate any of the missing data, and as co-author I will not —
the entire architecture of this repo is built to prevent that, and a TECS
reviewer or ACM's reproducibility process would catch invented numbers
immediately. What I *can* and did do is raise the manuscript's non-empirical
quality so that the day the observed bundle lands, the paper is one clean build
away from submission.

## 2. What I changed in this pass (no data invented)

These are purely presentational / specification improvements drawn from
material already in the repo:

- **Algorithm 1 (`paper/sagemm-tecs.tex`).** Added a formal per-interval
  controller decision procedure. Reviewers 1–4 explicitly asked for the
  controller as complete pseudocode; the prose and equations existed but the
  single readable procedure did not. It ties together validation → normalize →
  predict → policy → gate → reclaim → causal update, and makes the fail-closed
  and saturation branches visible at a glance.
- **RQ traceability table (Table `tab:rqmap`).** Ported the RQ→experiment→
  outcome mapping from `docs/EVALUATION.md` into the Methodology section so no
  reported number is orphaned from a research question (Reviewer 1's request).
- Wired both into the surrounding text with cross-references.

> ⚠️ LaTeX is not installed in this environment, so I could not compile.
> Algorithm 1 uses `algorithm` + `algpseudocode` (standard in any texlive that
> already has `acmart`). **Run `bash scripts/build_paper.sh` before trusting the
> PDF**; if the minimal TeX install lacks algorithmicx, comment out the two
> `\usepackage` lines and the algorithm float together (noted inline).

## 3. The publication-blocking work — only you can do this (ranked)

This is the critical path. Nothing else matters until #1–#3 exist.

| # | Task | Why it blocks | Done when |
|---|------|---------------|-----------|
| 1 | **Observed-result bundle.** Run the preregistered experiments on the real firmware; keep per-run provenance, failures, censoring, raw+aggregate traces. Generate `paper/generated/observed-results.tex` via `scripts/summarize_results.py`. | The paper has zero measurements. This is the submission. | `observed-results.tex` exists, built from reviewed data, and `\includesimulationfalse` builds. |
| 2 | **Full 16-cell G×I×R×C factorial.** Identical reset/randomized/thermal/firmware/workload conditions; report interactions, overhead, `n`, run-level 95% CIs (≥30 runs/short workload or a power analysis). | Table V / component ablation is the core empirical claim (all 4 reviewers). | Every cell has measured effect + CI; main and interaction effects analyzed. |
| 3 | **Reclamation-safety evidence.** Measure `Private_Clean` before/after from `smaps`, minor/major faults, bytes read, reload/storage latency, frame/input tails, native errno classes, hot-reuse, 1/5/10 s switching, concurrent execution, unload sync, `madvise` failure injection, fault storm >500/s. | This is the paper's central safety differentiator; the demo cannot prove pages are clean. | Adverse matrix reported; no writable/anon/shared mapping ever selected; failures leave correctness intact. |
| 4 | **Held-out policy comparison.** Frozen-weight Static/Threshold/EWMA/Ridge on disjoint reporting traces. Report saturation & fallback frequency. **If Ridge's CI overlaps EWMA, say ML shows no benefit and prefer the simpler policy.** | RQ3; also protects credibility. | Comparison table with CIs; honest null result if that is what the data show. |
| 5 | **Endurance.** Multiple independent 8-hour runs per primary platform; OOM/kernel/watchdog logs, device-hours, per-run trajectories, censoring rules — not "five short runs." | Any production-stability language depends on it. | Each run reported separately with denominators. |
| 6 | **Platform generality.** Either add the third independently-assembled constrained Linux platform, **or** narrow title/abstract/claims to the two DTV devices. | Reviewers 3/4 generality concern. | Third platform reported, or claims scoped and generality stated as future work. |
| 7 | **Vendor artifact boundary.** Record vendor Mono commit + patch hashes, build flags, kernel/firmware IDs, host APIs, ARM32/ARM64 flags, workload seeds, measurement scripts. | Reproducibility + Reviewer 2. | Manifest present in artifact and Evidence-Availability section. |

## 4. Manuscript-polish tasks (do after data, before submission)

- Replace the **entire** generated fragment — do not relabel synthetic values as
  observations. Regenerate every table/figure/abstract percentage from one
  versioned source; never interchange RSS/PSS/managed-heap/`Private_Clean`.
- **Bibliography:** replace every "Verify …" note with a publisher-checked
  record + final DOI; drop the reviewer-supplied duplicated arXiv DOIs for
  AGC/DumpKV; add authoritative Mono/.NET and Linux references; expand related
  work beyond the current 6 entries. (The readiness gate greps for "verify" and
  fails while any remains.)
- **Author metadata:** fill `[Institution]`/`[City]`/`[Country]`; confirm author
  order, contributions, conflicts, funding, and whether ACM wants an anonymized
  submission for this track.
- **Venue/cost:** confirm current TECS scope, page policy, ACM Open coverage /
  APC / waiver, and artifact policy directly with ACM (the source note about
  2026 open access is not a guarantee).
- Flip `\includesimulationtrue` → `false`, remove the yellow watermark box, and
  run `bash scripts/build_paper.sh --submission` as the final fail-closed gate.
  Resolve any overfull-box / accessibility / citation warnings.

## 5. Honest risk note

Even with all data collected, the strongest reviewer risk remaining is
**novelty**: every constituent mechanism (heap sizing, class→struct, `madvise`,
EWMA, ridge) is known, and the paper says so. The contribution stands or falls
on the *measured interaction effects* from the factorial — i.e., evidence that
coordination beats the best independent tuning, and that the guards actually
convert the unguarded-reclamation fault regression (hypothesized ~160 index)
into a bounded one. Make that interaction result the headline; if the factorial
does not show a real interaction, the framing needs to become a rigorous
negative/measurement result rather than a coordination win.
