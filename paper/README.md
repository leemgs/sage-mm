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

## Zero-cost publication compliance (author fee = $0)

ACM TECS is a **traditional subscription (hybrid)** journal. Publishing is free
of charge to authors **unless** you opt into ACM Open / Gold Open Access. To
keep the author-facing Article Processing Charge (APC) at **$0**:

1. **Do not** select ACM Open / Gold OA at submission or acceptance. Publish
   under the default subscription model.
2. **Do not** use a Creative Commons copyright option in LaTeX
   (`\setcopyright{cc}` and the `acmcopyright`/CC variants signal the paid OA
   route). This manuscript uses `\setcopyright{rightsretained}` as a neutral
   placeholder; ACM supplies the final rights block at acceptance based on the
   (no-fee) e-rights form.
3. TECS has **no mandatory page charge** and **no color charge** for the
   subscription route. There is no per-page fee to stay under.
4. If your institution has an **ACM Open** agreement, OA is provided at **no
   cost to you** — but that is an institutional arrangement, not an author
   payment. Only rely on it if your institution is confirmed to participate.

> Net: with the settings in this repo and the default subscription route,
> author cost is $0.

## Length

ACM `acmsmall` (TECS) does **not** impose a hard page cap, and the subscription
route carries **no per-page charge**, so page count does not affect author cost.

The manuscript includes a generated simulation-only Results dry run containing
RQ1--RQ3 mock prose, three in-document figures, the complete 16-row factorial
table with synthetic confidence intervals, and additional-platform/adverse/
endurance tables. This is intended to expose analysis and layout defects before
device experiments and to approximate the eventual paper structure. Page count
is not a quality target: replace the generated fragment with concise observed
evidence rather than padding toward 18--25 pages.

## Results discipline

Per `docs/REVISION_NOTES.md` and `docs/EXPECTED_RESULTS.md`, normalized targets
are labeled preregistered hypotheses and generated mock values are visibly
marked **SIMULATED---NOT OBSERVED**. Fill the same schemas from one versioned
observed-result bundle, remove the generated fragment, and never quote a mock
value as an achieved improvement.
