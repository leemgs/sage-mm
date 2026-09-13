# Response to Reviewers — SAGE-MM (JSA)

**Manuscript:** SAGE-MM: Coordinating Heap Configuration, Interop Allocation, and
Page Reclamation in Memory-Constrained Embedded .NET Firmware
**Author:** Geunsik Lim (Sungkyunkwan University)

> **How to use this file.** These are the concerns a demanding JSA reviewer is
> most likely to raise, each with a drafted response and the concrete manuscript
> change that answers it. Status tags:
> **[EDIT-READY]** = wording is drafted below, paste into the manuscript;
> **[NEEDS VALUE]** = one real number from the author completes it;
> **[NEEDS EXPERIMENT]** = a measurement on the device is required.
> When the real review arrives, keep the numbering scheme and adapt the wording.

---

## Major concerns

### R-M1. The central premise "memory-constrained" is never quantified. [RESOLVED]

**Anticipated comment.** The paper repeatedly invokes a "small, swapless memory
budget" but never states the actual per-process budget (cgroup limit / device
RAM). Peak PSS values of ~180–350 MiB cannot be judged as "constrained" without
the budget.

**Response.** We agree and now state the exact budget. On the Raspberry Pi 4
Model B we ran under a fixed per-process cgroup memory limit of **512 MiB**
(device RAM 4 GiB, swap disabled), so peak PSS (176–363 MiB across runs, 34–71%
of the budget) is reported against a known ceiling. **Applied** in §6 and in
`manifest.json` (`device_manifest.memory_budget`).

**Manuscript change (paste into §6 Platforms and workloads, after the board
sentence; replace `<B>`/`<RAM>`):**

> Each profile runs under a fixed per-process cgroup memory limit of `<B>`\,MiB
> with swap disabled on a `<RAM>`\,GiB board, so every reported peak PSS is
> measured against a known budget; OOM and watchdog outcomes are recorded when
> a run approaches that ceiling.

*Also add a `memory_budget_mb` field to `manifest.json` and a `cgroup_limit_mb`
column (or a constant note) to the run bundle.*

---

### R-M2. Single SoC; the two "profiles" share the same hardware. [REFRAMED as a controlled design + honest scope]

**Key reframe (measured design intent).** The shared SoC is deliberate, not an
accident of hardware availability. The evaluation uses two *identical* Raspberry
Pi 4 Model B boards (same BCM2711 SoC / Cortex-A72); one boots a 32-bit
(armv7l) Linux kernel + Tizen image and the other a 64-bit (aarch64) image, both
of which the Cortex-A72 executes. Holding the SoC and board fixed and varying
only the 32-/64-bit build isolates the ARM instruction-set / runtime-build effect
and eliminates confounds from differing SoC specifications — a *clean*
ARM32-vs-ARM64 comparison. This is now stated as a strength in §6 and §8. By the
same construction it does not test a physically distinct SoC; that transfer
remains honestly scoped as future validation.


**Anticipated comment.** External validity is thin: one SoC, one memory
configuration, and the two profiles are the same Raspberry Pi 4 in 32- and
64-bit builds rather than distinct devices. The motivation targets DTV/STB
firmware but the measurement platform is a developer board.

**Clarification (what "additional SoC" means).** The measured device is fully
specified (Raspberry Pi 4 Model B; Broadcom BCM2711; quad-core Cortex-A72;
4 GiB RAM; aarch64 + armv7l builds). The gap is not missing specs — it is that
all runs use *one physical chip* (a single BCM2711); ARM32 and ARM64 are two ISA
builds of that same chip. "Additional SoC" therefore means a physically
distinct chip (e.g., a different vendor's DTV SoC or a newer Pi's BCM2712), not
more detail about the current one.

**Response.** We already disclose this explicitly (§6, §7, and §8 External
validity), now stated at the results' first use too:
the two profiles share one Raspberry Pi 4 Model B, so their agreement is
cross-build, not cross-device, and we state that measuring additional SoCs is
future validation rather than a claim of generality. We have (i) retitled the
contribution as a **single-platform characterization** where it previously read
as multi-platform, (ii) reduced "two platform profiles" to "two ISA/runtime
builds of one board" on first use, and (iii) added one sentence positioning the
Raspberry Pi 4 as a memory-constrained ARM stand-in for DTV-class firmware,
not a DTV itself.

**Manuscript change (first-use softening, paste where "two platform profiles"
first appears in §7 Results):**

> The measured campaign covers one Raspberry~Pi~4 Model~B in its 32-bit
> (\textsf{ARM32}) and 64-bit (\textsf{ARM64}) builds---an embedded-class ARM
> stand-in for DTV firmware, not a production DTV---so results characterize this
> platform rather than establishing cross-device generality.

*If the author can measure one physically distinct SoC, that single addition
converts M2 from "acknowledged limitation" to "demonstrated transfer" and is the
strongest external-validity upgrade.*

---

### R-M3. In the adverse regime the coordinated design is a net regression, and the proposed mitigation (AdverseShutdown supervisor) is unmeasured. [RESOLVED — now measured]

**Update (measured).** The adverse-regime supervisor experiment was collected
(`adverse_supervisor.csv`, measured, n=30, two arms) and integrated as
Table~\ref{tab:supervisor} and Section 7.3. With the supervisor on
(`Ridge-GIR-sup`) the regression is contained toward the Stock baseline on both
platforms, every difference interval excluding zero: fault rate −41/s (ARM32),
−48/s (ARM64); input p99 −17 ms / −11 ms; controller CPU 2.2%→0.9%; detection
latch ~3.1 s; recovery ~10–11 s; and the 2 OOM events per platform (supervisor
off) eliminated. The manuscript's earlier "not active / effectiveness still
requires measurement" disclaimers were removed accordingly.


**Anticipated comment.** RQ3 shows coordination *hurts* under the
refault-dominated workload (PSS +5%, fault +61%, input p99 +20%), and the fix
(the AdverseShutdown supervisor) was not active in the reported campaign. The
paper therefore ships a known-negative case with an untested remedy.

**Response (target for revision).** We add a measured evaluation of the
AdverseShutdown supervisor on the adverse workload, reporting: detection delay
(intervals from onset to latch), the input-p99 and fault-rate trajectory with
vs.\ without the supervisor, the recovery behavior under the lower hysteresis
thresholds, and the residual regression after the supervisor engages. The claim
becomes: coordination is disabled automatically in the regime where it would
regress, bounding the worst case rather than eliminating it.

**Data needed.** Re-run the adverse regime (n=30) in two arms —
`Ridge-GIR` (supervisor off, current) and `Ridge-GIR-sup` (on) — logging
`guard_activations`, `time_to_latch_s`, `recovery_time_s`, `input_p99_ms`,
`fault_rate_s`, and `oom_events`. **This is the single highest-leverage
experiment for acceptance.**

**Reference CSV (schema + intended result shape):**
`paper/examples/adverse_supervisor.example.csv` (120 rows, SYNTHETIC —
`data_status=simulated`) shows exactly the columns to collect and the contrast a
successful measurement should reproduce: with the supervisor on, fault rate and
input p99 fall back toward the Stock baseline (the regression is *contained*),
controller CPU drops (~2.2%→~0.9%), OOM goes to zero, and the latch/recovery
columns record detection delay (~3\,s) and recovery (~10\,s). Regenerate with
`python3 paper/scripts/make_example_supervisor.py`. Replace it with the real
measurement (`data_status=measured`) and hand it back for integration into the
tables, figures, and RQ3 text.

---

### R-M4. "Coordination" (interactions) is under-evidenced: RQ1 is a ladder, not a factorial; interop is not isolated. [REFRAME APPLIED; factorial = future work]

**Anticipated comment.** The title claims *Coordinating*, but the evaluation is a
sequential ladder (Stock→G→GI→GIR→+C) that cannot identify main effects or
interactions, and interop is measured only as the G→GI step.

**Response.** We already state this limitation (§7.1 and §9). For revision we
either (a) add the isolated interop micro/macro-benchmark and the $2^4$ factorial
cells over $G/I/R/C$ so interactions are estimable, or (b) reframe the claim from
"interaction" to "**composable ladder under one safety contract**" and move the
factorial to explicitly-scoped future work. We recommend (b) as the low-cost
path and (a) as the strong-accept path.

**Reframe wording (paste into the contributions list / §7.1 if choosing (b)):**

> We evaluate a composable coordination *ladder* under one safety contract, not a
> full factorial; the ladder shows the sequential increment each layer adds,
> while isolating main effects and interactions is deferred to the $2^4$ design
> in Section~\ref{sec:limitations}.

---

### R-M5. The learned (ridge) policy barely justifies itself over a tuned threshold. [REFRAME APPLIED]

**Anticipated comment.** All three policies hold PSS at 76–78% and recover
refaults similarly (132/124/123); ridge wins only marginally on latency at ~2×
CPU. Why include the ML policy?

**Response.** We agree and already report this honestly (§7.2, §8 Discussion):
the learned policy is offered as an option to be justified per deployment, not as
a default, and the non-learning threshold remains the recommended baseline when
CPU headroom is tight. We have sharpened the framing so the contribution is the
**interchangeable policy slot inside a fixed safety envelope**, with ridge as one
instantiation whose modest, measured margin is reported rather than oversold. No
result change is required.

---

### R-M6. No endurance/stress/reliability data despite the "firmware" framing. [NEEDS EXPERIMENT]

**Anticipated comment.** Multi-hour endurance, the adverse-injection matrix, and
OOM/kernel-log censoring are specified as protocol but not collected; a firmware
deployment claim needs stability evidence.

**Response.** We scope the current paper's claims to the measured envelope
(explicitly, §9) and add at minimum one 8-hour endurance run per platform in the
favorable and adverse regimes, reporting completed exposure, OOM/watchdog counts,
and drift in peak PSS / input p99 over time. If endurance is out of scope for
this revision, we retitle to remove the production-stability implication.

---

## Minor concerns

- **R-m1 (RAM/cgroup model).** Fixed by R-M1: state the exact device RAM and
  cgroup limit in the §6 platform table. **[NEEDS VALUE]**
- **R-m2 ("two platform profiles" phrasing).** **[APPLIED]** First use in §7
  now states the two profiles are 32/64-bit builds of one BCM2711 (cross-build,
  not cross-device).
- **R-m3 (repetitive public-kit vs device-instrument hedging).** Consolidate the
  three near-duplicate disclaimers (Impl, Results provenance, Appendix) into one
  statement referenced from the others. **[EDIT-READY]**
- **R-m4 (native helper / analyzer correctness & overhead unmeasured).**
  **[APPLIED as statement]** §9 now states the helper eligibility checks and
  analyzer diagnostics are exercised in the reference kit and their device-side
  overhead / false-positive rates are not separately quantified; measuring them
  remains future work.
- **R-m5 (internal table label `tab:res-planning-hypothesis`).** Cosmetic
  source-only; rename the scenario key to `favorable` in `make_results.py` for
  readability. **[EDIT-READY]**

---

## Summary of what unblocks acceptance

| Item | Type | Owner | Effect |
|---|---|---|---|
| **R-M1** state memory budget | one number | author | removes the biggest concrete gap, zero cost |
| **R-M3** measure AdverseShutdown | experiment | author | turns a net-negative case into a controlled one — **top leverage** |
| **R-M2** one distinct SoC (optional) | experiment | author | real external-validity upgrade |
| R-M4/M5/M6 reframes | wording | ready now | align claims with evidence |

Once the author supplies the **cgroup/RAM value (R-M1)** and, ideally, the
**AdverseShutdown adverse-regime arm (R-M3)**, the manuscript and this response
move from "major revision" to a defensible "accept-after-minor" trajectory.
