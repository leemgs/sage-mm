# SAGE-MM — ACM TECS Manuscript

This directory holds the manuscript source reframed for submission to
**ACM Transactions on Embedded Computing Systems (TECS)**.

- `sagemm-tecs.tex` — main manuscript (`acmart` class, `acmsmall` journal format).
- `sagemm.bib` — bibliography (verify all DOIs before submission; see the note at the top of the file).

## Why TECS

TECS is the closest scope match for this work: memory-constrained **embedded
runtime memory management** with empirical, engineering-integration framing.
The paper was reframed from the previous "self-adaptive framework" umbrella to
an explicit **cross-layer coordination + bounded online control** contribution,
which TECS's systems/experience track accepts.

## Building the PDF

Requires a TeX Live (2021+) installation that includes the ACM `acmart` class.

```bash
cd paper
pdflatex sagemm-tecs
bibtex   sagemm-tecs
pdflatex sagemm-tecs
pdflatex sagemm-tecs
```

Or run `bash ../scripts/build_paper.sh`, which first verifies that every
simulation-only generated artifact matches the fixed seed and source script.

If `acmart.cls` is not installed, get it from CTAN (<https://ctan.org/pkg/acmart>)
or `tlmgr install acmart`. Do **not** vendor a modified `acmart.cls`; ACM
requires the unmodified current class.

## Publication-cost warning for 2026

Do not rely on the earlier assumption that a traditional subscription route
guarantees a zero author fee. ACM announced a transition to fully open-access
publication beginning in 2026. Whether the corresponding author pays nothing
depends on current ACM policy, ACM Open institutional participation, geographic
or discretionary waivers, and the acceptance year. Confirm coverage in writing
before submission: <https://libraries.acm.org/subscriptions-access/acmopen> and
<https://www.acm.org/publications/openaccess>.

The copyright command in this draft is only a placeholder; ACM supplies the
accepted-paper rights metadata. It is not a mechanism for avoiding an APC.

## Length

Verify the current TECS author instructions for page limits, excess-page policy,
and artifact/supplement rules. This repository makes no zero-fee or unlimited-
length guarantee.

The manuscript includes a generated simulation-only Results dry run containing
RQ1--RQ3 mock prose, three in-document figures, the complete 16-row factorial
table with synthetic confidence intervals, and additional-platform/adverse/
endurance tables. This is intended to expose analysis and layout defects before
device experiments and to approximate the eventual paper structure. Page count
is not a quality target: replace the generated fragment with concise observed
evidence rather than padding toward 18--25 pages.

## Results discipline

Per `docs/REVISION_NOTES.md` and `docs/ACTUAL_RESULTS.md`, normalized targets
are labeled preregistered hypotheses and generated mock values are visibly
marked **SIMULATED---NOT OBSERVED**. Fill the same schemas from one versioned
observed-result bundle, remove the generated fragment, and never quote a mock
value as an achieved improvement.

## Submission gate

Normal `bash ../scripts/build_paper.sh` builds the visibly watermarked internal
simulation draft. `bash ../scripts/build_paper.sh --submission` first runs a
hard gate and currently fails by design: simulation mode, author-affiliation
placeholders, unverified bibliography records, and the absent observed-results
fragment are blockers. See `SUBMISSION_READINESS.md`.
