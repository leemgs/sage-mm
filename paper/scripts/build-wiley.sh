#!/usr/bin/env bash
# Build the SAGE-MM Software: Practice and Experience submission PDF using the
# official Wiley New Journal Design class (paper/main-wiley.tex).
#
#   bash paper/scripts/build-wiley.sh
#
# The Wiley class (paper/wiley/WileyNJD-v2.cls) additionally requires the
# standard `soul' package and the STIX2/Lato fonts. These ship with any full
# TeX Live and with Overleaf's "Wiley NJD v2" template, but may be absent from
# a minimal TeX install; if `soul.sty' is missing this script says so and
# stops, and you should either install it (TeX Live: tlmgr install soul) or
# build on Overleaf instead.
set -euo pipefail

paper=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

echo "[1/3] regenerating results fragments from paper/measured/evaluation-data/"
python3 "$paper/scripts/make_results.py"

if ! command -v pdflatex >/dev/null || ! command -v bibtex >/dev/null; then
  echo "error: pdflatex and bibtex are required (install TeX Live)" >&2
  exit 2
fi
if ! kpsewhich soul.sty >/dev/null; then
  echo "error: soul.sty not found. The Wiley class requires it." >&2
  echo "       Install it (tlmgr install soul) or build on Overleaf's" >&2
  echo "       'Wiley NJD v2' template. The standard build" >&2
  echo "       (bash paper/scripts/build.sh) needs no extra packages." >&2
  exit 2
fi

echo "[2/3] compiling paper/main-wiley.tex with the Wiley NJD class"
cd "$paper"
# Make the vendored class/style/bst discoverable.
export TEXINPUTS="$paper/wiley:${TEXINPUTS:-}"
export BSTINPUTS="$paper/wiley:${BSTINPUTS:-}"
pdflatex -interaction=nonstopmode -halt-on-error main-wiley.tex >/dev/null
bibtex main-wiley >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main-wiley.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main-wiley.tex >/dev/null

echo "[3/3] copying build output to paper/output/main-wiley.pdf"
mkdir -p "$paper/output"
cp "$paper/main-wiley.pdf" "$paper/output/main-wiley.pdf"
echo "done: $paper/output/main-wiley.pdf"
