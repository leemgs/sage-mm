# Wiley NJD template kit (Software: Practice and Experience)

This folder holds the **official Wiley New Journal Design (NJD) LaTeX class**
and its support files, used by `paper/main-wiley.tex` to produce a manuscript in
the exact *Software: Practice and Experience* (SP&E) house style.

```
WileyNJD-v2.cls     Wiley NJD v2 document class (© SPi Technologies, via Wiley)
NJDnatbib.sty       Wiley NJD natbib reference support
WileyNJD-AMA.bst    Wiley NJD "AMA" numbered reference style
ulem.sty            standard package the class requires (vendored for convenience)
```

## Two builds, one shared body

The manuscript body is written once and shared by both front ends through
`abstract.tex`, `keywords.tex`, `body.tex`, and `bio.tex`:

| Build | Command | Class | Status |
|-------|---------|-------|--------|
| Standard single column | `bash paper/scripts/build.sh` | `article` | **Verified** — builds here, valid SP&E submission format |
| Wiley house style | `bash paper/scripts/build-wiley.sh` | `WileyNJD-v2` | Needs `soul` + STIX2/Lato fonts (see below) |

SP&E accepts submissions in a standard, consistent format, so **`main.pdf` from
the standard build is a complete, submittable artifact**. The Wiley-class build
reproduces the journal's exact look and is what you would use on Overleaf or a
full TeX Live.

## Building the Wiley version

The Wiley class additionally requires the standard `soul` package and the
STIX2/Lato fonts. These are present in any full TeX Live and on Overleaf, but
may be missing from a minimal TeX install.

**Option A — Overleaf (recommended, one click).** Create a project from
Overleaf's *"Wiley NJD v2"* template (it bundles the class, `soul`, and the
fonts), then upload `paper/main-wiley.tex`, the four shared fragments, the
`measured/` folder, and `sagemm.bib`; set the main document to `main-wiley.tex`.

**Option B — Local full TeX Live.**
```
tlmgr install soul stix2-otf   # if not already present
bash paper/scripts/build-wiley.sh
```
The script points `TEXINPUTS`/`BSTINPUTS` at this folder so the vendored class
is found, and stops with a clear message if `soul.sty` is missing.

## Notes

- `main-wiley.tex` follows the documented Wiley NJD front-matter interface
  (`\articletype`, `\title`, `\author[1]`, `\address[1]`, `\corres`, `\email`,
  `\abstract`, `\keywords`, `\maketitle`). It was prepared against the class but
  not compiled in the authoring container (which lacks `soul`/STIX); finalize it
  on Overleaf, where it compiles against the official template.
- Figures are generated with pgfplots/TikZ; if a journal build environment
  restricts TikZ, the standard build's `paper/output/main.pdf` already contains
  the rendered figures.
- The class file is Wiley/SPi copyright and is vendored here only to build this
  manuscript; it is redistributed under the terms Wiley provides with the NJD
  authoring template.
