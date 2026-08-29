# TECS submission-readiness review

## Verdict

**Not ready for journal submission.** The design/controller narrative and
artifact plumbing are useful, but the current PDF is an 11-page internal layout
draft whose Results are generated from the actual targets. No seeded mock
value is empirical evidence, and the synthetic PASS outcomes cannot diagnose
runtime or firmware bugs because the generator is centered on its own targets.

## Blocking tasks owned by the authors

1. **Observed result bundle:** run the preregistered independent experiments;
   preserve per-run provenance, failures, censoring, and raw/aggregate traces;
   generate `paper/generated/observed-results.tex` from reviewed data.
2. **Full factorial:** execute all feasible G×I×R×C cells under identical reset,
   randomized, thermal, firmware, and workload conditions; report interactions,
   overhead, `n`, and run-level 95% CIs.
3. **Platform/generalization:** add the constrained third platform or narrow the
   title, abstract, and claims to the two DTV devices.
4. **Reclamation safety:** measure `Private_Clean`, minor/major faults, bytes
   read, reload/storage latency, frame/input tails, native errno classes, hot
   reuse, rapid switching, concurrent execution, and unload synchronization.
5. **Endurance:** complete independent eight-hour runs, retain OOM/kernel and
   watchdog logs, report device-hours, trajectories, censoring, and every
   failure—not only successful runs.
6. **Comparators:** produce held-out Static/Threshold/EWMA/Ridge results. Port
   executable SOTA collectors where feasible; otherwise provide an exact
   incompatibility matrix and make no superiority claim.
7. **Artifact boundary:** record the vendor Mono commit, patch hashes, build
   flags, kernel/firmware, host APIs, workload seeds, and measurement scripts.
8. **Bibliography:** replace provisional `others` author lists and verification
   notes with publisher-checked records/DOIs; expand the related work beyond the
   current minimal set of citations.
9. **Authorship metadata:** replace institution/city/country placeholders and
   confirm author order, contributions, conflicts, funding, and anonymization
   requirements.
10. **Venue/cost policy:** confirm the current TECS scope, page policy, ACM Open
    coverage/APC or waiver, artifact policy, and submission checklist directly
    with ACM. The repository cannot guarantee zero cost in 2026.

## Quality tasks after data collection

* Replace—not relabel—the entire generated simulation fragment.
* Reconcile abstract, Results, figures, conclusion, and artifact from one result
  source; never promote actual/synthetic values to observations.
* Explain unanticipated failures and null effects. If Ridge overlaps EWMA, state
  that ML adds no demonstrated benefit and prefer the simpler policy.
* Add effect sizes and CIs, not only p-values; avoid treating interval samples as
  independent runs.
* Rebuild with the current unmodified `acmart` class and resolve accessibility,
  overfull-box, citation, and metadata warnings.

Run `bash ../scripts/build_paper.sh --submission` from `paper/` (or from the
repository root) as the final fail-closed gate.
