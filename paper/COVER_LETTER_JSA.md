# Cover Letter — Journal of Systems Architecture

> **How to use this draft.** Fill every `[...]` field, delete the two bracketed
> *optional* paragraphs if you prefer not to include them, and paste the body
> (from "Dear Editors" to the signature) into the JSA submission system's cover
> letter box, or attach it as a PDF.
>
> ⚠️ **Do not submit until the manuscript's Results are real.** The current
> draft carries `SIMULATION-ONLY` watermarks and will not pass an honest
> review; this letter describes the evaluation *methodology*, which is true
> regardless, but the paper itself must contain observed measurements before
> you send it. Also, at the submission "publishing option" step, choose the
> **subscription** route (no APC), not Gold Open Access.

---

[Date]

To the Editors-in-Chief
*Journal of Systems Architecture*

Dear Editors,

Please consider our manuscript, **"SAGE-MM: Coordinating Heap Configuration,
Interop Allocation, and Page Reclamation in Memory-Constrained Embedded .NET
Firmware,"** for publication in the *Journal of Systems Architecture* as a
regular research paper.

**What the paper is about.** Memory-constrained embedded consumer devices —
digital televisions and similar appliances — run a managed application stack
(a garbage-collected heap, native interoperability, and file-backed executable
code pages) inside a single, swapless process budget, yet these layers are
conventionally tuned in isolation. SAGE-MM is an engineering design that
*coordinates* three deliberately distinct interventions under one embedded
memory budget: a static, architecture-specific managed-heap build
configuration; a source-reviewed value-type interop conversion that removes
allocation; and a bounded, online-controlled reclamation of clean file-backed
pages together with runtime compaction gating. Only the last adapts at runtime;
the first two reduce the load presented to the controller. We contribute an
implementable cross-layer policy with an explicit action boundary, fail-closed
safety guards, and a falsifiable evaluation protocol, rather than a new
collector, interop representation, reclamation syscall, or learning algorithm.

**Why the Journal of Systems Architecture.** This is a single-node embedded
systems-architecture study at the boundary between a managed runtime and the
operating system: runtime/memory-management design, hardware/software
co-consideration across ARM32 and ARM64 devices, and OS-assisted page
reclamation under a hard resident-memory constraint. That places it squarely
within JSA's scope of embedded systems design and their software/runtime
support, and its architecture-specific findings (for example, the differing
heap-configuration trade-off on ARM32 versus ARM64) are of direct interest to
JSA's embedded-systems readership.

[*Optional — prior-review transparency; delete if you prefer not to disclose.*
An earlier version of this work was reviewed at a parallel-and-distributed-
systems venue. That feedback made clear the study is fundamentally a
single-node embedded runtime/memory-management contribution rather than a
parallel or distributed one, so we have re-scoped the paper accordingly —
narrowing the claims to coordinated engineering and empirical interaction
analysis, and strengthening the evaluation — and now submit it to JSA, whose
scope it fits directly.]

**Contributions.** The paper makes four bounded contributions:

1. It characterizes managed-heap, interop-allocation, and file-backed
   executable-page pressure under identical application transitions on the
   evaluated firmware, reporting architecture-specific rather than universal
   effects.
2. It specifies a cross-layer action boundary that separates a build-time heap
   decision and a source-time allocation decision from a single online policy
   that adjusts one reclamation interval and one compaction gate.
3. It provides an implementable controller definition with dimensionless
   features and target, a causal (prequential) update order, bounded actions,
   hysteresis, cooldown, fail-closed telemetry handling, and an explicit
   non-learning threshold fallback.
4. It evaluates individual and interaction effects through a full-factorial
   ablation with held-out policy comparison (fixed, tuned-threshold, EWMA,
   ridge), adverse-workload stress, and multi-hour endurance runs, reporting
   per-mechanism cost and run-level confidence intervals.

**Scope and honesty of claims.** We deliberately limit the novelty claim to the
coordination and its safety-aware control: static heap sizing, class-to-struct
conversion, `madvise`-based reclamation, EWMA, and ridge regression are not
individually new, and we say so. Conclusions are scoped to the evaluated
runtime commits, devices, memory limits, storage configurations, and workloads;
where a lightweight learned policy shows no advantage over a tuned threshold, we
report that rather than hiding it. A reference kit reproduces the control logic
and safety guards independently of the proprietary firmware integration.

We confirm that this manuscript is original, has not been published previously,
and is not under consideration by any other journal. All authors have approved
the submission and agree to its content. [*We declare no competing financial or
personal interests.* / *We declare the following competing interests: [...]*]
[*Optional: A preprint of this work is available at [arXiv/repository URL].*]

We suggest the following qualified reviewers who are not close collaborators and
have no conflict of interest: [Name, affiliation, email]; [Name, affiliation,
email]; [Name, affiliation, email]. We request that the following be excluded,
if any: [none / Name].

Thank you for considering our submission. We look forward to the reviewers'
feedback.

Sincerely,

Geunsik Lim (corresponding author)
[Institution], [City], [Country]
leemgs@gmail.com
[On behalf of all co-authors: [names]]
