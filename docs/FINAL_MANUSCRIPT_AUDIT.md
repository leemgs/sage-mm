# Final-manuscript audit against TPDS reviews

**Audit date:** 2026-08-29  
**Audited material:** the files in this repository at the commit containing this report.

## Verdict and scope limitation

The reviewer feedback is **not fully closed**. The repository contains manuscript-ready replacement prose, an implementation analogue, and an evaluation protocol, but it contains no `.tex`, `.bib`, `.docx`, submitted PDF, figures, result tables, raw traces, or commercial-firmware patch. Consequently this audit cannot certify a “final manuscript”; it can only assess the repository material. `MANUSCRIPT_REVISION.md` still contains explicit `[N ...]` and `[effect ...]` placeholders. Do not submit it as a final paper.

TPDS's decision letter also states that the rejected paper or a modified version may not be resubmitted to TPDS. These revisions are therefore suitable only for an allowed new contribution or another venue, subject to that venue's policy.

Status meanings: **Closed in text/code**, **Partially closed**, and **Open—evidence or manuscript required**.

## Consolidated closure matrix

| Reviewer concern | Status | Repository evidence | Required before a final submission |
|---|---|---|---|
| Limited novelty / unclear unified contribution (AE, R1.2, R3.1, R4.1) | Partially closed | Revised title, abstract, contribution boundary, and limitations narrow novelty to coordinated integration. | Apply replacement prose to the actual manuscript and demonstrate interaction effects; prose alone cannot establish novelty. |
| SOTA and heuristic comparisons (R1.1, R3.2, R4.1) | Partially closed | LXR, Platinum, AGC, and DumpKV are positioned by domain; static/threshold/EWMA/ridge modes are now implementable. | Add the comparison matrix to the paper, verify every bibliography entry, and provide held-out empirical threshold/EWMA/ridge results. Port LXR/Platinum where feasible or document incompatibility without claiming superiority. |
| Static/build-time/online system boundary (R1.2, R2.1) | Closed in repository text | `SYSTEM_BOUNDARY.md` distinguishes the Mono patch, source-recompiled interop, and online actions. | Insert exact vendor runtime commit, patch hash, firmware/kernel/compiler/build flags, architectures, and host interfaces into the actual paper/artifact. These values are absent here. |
| Controller target, scaling, coefficients, initialization, loss, actions, guards (R1.3a/c, R2.2, R3.2, R4.4) | Closed in code; partially closed in manuscript | `ControllerOptions`, dimensionless SLO normalization, causal ridge loss/update, bounds, hysteresis, invalid-telemetry and fault-storm fallbacks are implemented and documented. | Put the complete pseudocode/equations in the manuscript; report frozen held-out results, overhead, saturation and fallback frequency. |
| `Cold(a)` and unexplained `K=5` (R1.3b) | Closed in code/text | Canonical 0.6/0.3/0.1 recency/frequency/size formula; K is the byte-budget prefix. | Report sensitivity to weights, idle guard, and byte budget on real traces. |
| RQ1–RQ3 traceability (R1.4) | Closed in protocol only | `EVALUATION.md` maps each RQ to experiments and outcomes. | Place the table in the actual Evaluation section and link each result subsection back to its RQ. |
| Quantitative component ablation / Table V (R1.4, R2.3, R3.4, R4.3) | **Open—evidence required** | A 16-cell factorial schema and CI method are specified. | Run the combinations under identical randomized/reset conditions and replace expected-impact cells with measured effects, uncertainty, and mechanism costs. No such data exist here. |
| Reclamation identification, alignment, concurrency, failure, `Private_Clean`, refault cost (R2.4) | Partially closed | Native demo filters private file-backed non-writable mappings and returns errors; safety requirements and adverse tests are specified. | Production implementation must parse/attribute `Private_Clean`, serialize unload, use an allowlist, and report hot-reuse/switching faults, storage/reload latency, responsiveness, failures, and guard activation. The current demo cannot prove pages are clean. |
| Field/endurance evidence and artifacts (R2.5) | **Open—evidence required** | Required manifest, workload state machine, logs, traces, and endurance reporting are enumerated. | Release permitted runtime/config/workload/measurement artifacts and independent multi-hour traces with OOM logs and denominators. Five short runs cannot support production stability. |
| Citation errors and authoritative runtime/interop references (R2.6) | Partially closed | The irrelevant JavaScript-taint and Concurrent Pascal citations are flagged; suggested works are audited for domain. | Audit the actual `.bib`, remove/replace the bad citations, add authoritative Mono/.NET and Linux sources, and verify final DOI/venue data. No bibliography is present to inspect. |
| Additional platforms/workloads and generality (R3.3, R4.2) | **Open—evidence required** | A second independent embedded Linux platform and adverse workload matrix are prescribed. | Execute and report them; otherwise limit every claim to the two tested DTV-class systems and pilot workloads. |
| Appendix/table/baseline/units/figure/organization issues (R1.4, R2.7, R4.5) | Open—actual manuscript required | A consistency checklist and canonical baseline names are supplied. | Inspect and compile the actual source: remove `Appendix ??`, blank appendix and duplicate tables; reconcile all figures/tables/abstract claims; fix `4 ms squared`; annotate 2.6× if supported; apply hierarchical section grouping. |
| Abstract and numerical claims (R2.7) | **Open—evidence required** | A narrowed abstract template exists. | Replace all placeholders from one versioned result source. Reconcile 19%, 35%, OOM, frame-latency and production claims with baseline, denominator, statistic and CI. |

## Additional implementation-to-manuscript gaps found in this audit

These gaps are easy to miss because the individual classes exist, while the end-to-end behavior claimed by the replacement prose does not yet exist:

1. **Cold-module selection now has reference wiring, not production evidence.** `SelfAdaptiveController` applies the tracker budget/idle guard and calls `FlushModule`; the demo seeds it from loaded assemblies. However, startup observation and file length are only proxies. A production access-event source, `Private_Clean` byte attribution, unload synchronization, and signed module allowlist are still absent, so this cannot support an effectiveness or safety claim.
2. **The documented saturation fallback is implemented and unit-tested.** Persistent clipped ML predictions now report `ModelSaturation`, clear the pending update, and take the declared threshold action. The evaluation still must report saturation frequency and outcomes on held-out traces.
3. **Fallback accounting is partially implemented.** Invalid telemetry, fault storms, and saturation have decision reasons; policy counters cover cooldown/fault suppression and successful flush execution; controller counters cover no-candidate and native-failure outcomes. Missing `/proc`, hot-reuse exclusion, and detailed native errno classes still need production counters.
4. **The training/reporting boundary has an API, but tuning and held-out evaluation are absent.** `BeginReporting()` clears the pending training prediction while retaining weights, and `updateModel:false` freezes reporting. There is still no tuning script, trace split manifest, model serialization, or results pipeline. “Tuned threshold” and “held-out” remain experimental requirements, not established results.
5. **The demo telemetry perturbs and approximates the workload.** It forces a Gen-0 collection to estimate pause and estimates fragmentation from pinned-object count. This is acceptable for a demo, but it cannot support production pause, fragmentation, or controller-effect claims; the vendor/EventPipe telemetry and fidelity validation requested by Reviewer 2 are absent.
6. **`Private_Clean` is not measured by the implementation.** The native helper reads `maps`, not `smaps`, and issues `MADV_DONTNEED` for conservative mapping candidates. It neither proves that selected pages are clean nor reports bytes reclaimed/refaulted. Alignment follows kernel mapping boundaries, but unload serialization and concurrent hot execution remain production-integration requirements.
7. **The analyzer is advisory only.** The repository contains diagnostic DTV0001 but no CodeFix provider. Any final manuscript statement that a CodeFix automatically converts wrappers must be removed, unless a reviewed transformation and ABI-validation workflow is actually supplied.
8. **There is no quantitative-results pipeline.** No workload driver, raw/aggregate trace, bootstrap script, canonical results file, figure generator, or table generator is present. The consistency rule that all claims come from one source cannot yet be enforced.

### Closure decision by reviewer

* **Reviewer 1:** algorithm definitions and RQ planning are substantially addressed; empirical SOTA comparison, measured ablation, figure/table fixes in the actual manuscript, and final bibliography remain open.
* **Reviewer 2:** boundary and controller specification are substantially addressed in reference text/code; exact vendor metadata, end-to-end safe reclamation, stress results, endurance evidence, artifacts, citation audit, and actual manuscript cleanup remain open.
* **Reviewer 3:** novelty language and a wider evaluation plan are addressed; additional-platform evidence, alternative-controller measurements, and component interaction results remain open.
* **Reviewer 4:** a threshold comparator and narrowed claims now exist; broader quantitative evidence, full Table V results, saturation/failure behavior, canonical baseline results, and final presentation cleanup remain open.

## Blocking checklist

A manuscript should not be described as final until all of the following are available and pass review:

1. Actual manuscript source/PDF and bibliography, compiling without unresolved references.
2. Versioned result bundle and generated tables/figures, including all declared ablations and confidence intervals.
3. Held-out static/threshold/EWMA/ridge comparison with frozen learning weights.
4. Additional-platform or explicitly narrowed generality claims.
5. Hot-reuse, rapid-switching, slow-storage, fault-storm, failure-injection, and responsiveness results.
6. Multiple independent endurance runs, OOM/kernel logs, device-hours/session denominators, and censoring rules.
7. Exact vendor runtime/firmware boundary and releasable reproduction artifacts.
8. Publisher-verified bibliography and claim-by-claim citation audit.
9. Replacement of demo module/file-size proxies with production access events, `Private_Clean` attribution, unload synchronization, and an allowlist—or explicit removal of the production claim.
10. Completion of production fallback accounting for missing `/proc`, hot reuse, and native errno classes.

## Audit conclusion

The repository now provides a substantially clearer **revision plan and reference implementation**, but it does not contain enough manuscript or experimental material to establish that all four reviewers' comments have been fully addressed. Algorithmic specification and claim scoping are the strongest closed areas. Quantitative ablation, SOTA empirical evidence, platform generality, reclamation stress evidence, field reliability, bibliography verification, and final presentation remain blocking items.
