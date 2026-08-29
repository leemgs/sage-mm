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

As committed, this draft compiles to **9 `acmsmall` pages** including
references — it is the full narrative skeleton with results rendered as
`[to be measured]` placeholders. Once the measured RQ1–RQ3 figures and the
complete 16-row factorial table (Section 6) are inserted from the observed
bundle, it is expected to grow into the normal TECS research-paper range of
roughly **18–25 pages**. Keep required definitions and quantitative evidence in
the main text; host code, configs, scripts, and traces as the external artifact
rather than a supplemental PDF.

## Results discipline

Per `docs/REVISION_NOTES.md` and `docs/EXPECTED_RESULTS.md`, unmeasured
quantities are rendered as **`[to be measured]`** (the `\TBM` macro) and the
normalized numbers in the expectations table are labeled **preregistered
hypotheses, not results**. Fill these from a single versioned observed-result
bundle before submission; never fabricate or quote them as achieved
improvements.
