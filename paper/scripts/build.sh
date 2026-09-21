#!/usr/bin/env bash
# Build the SAGE-MM IEEE Transactions on Consumer Electronics (IEEEtran) PDF.
#
#   bash paper/scripts/build.sh
#
# Steps:
#   1. Regenerate the results fragments from the evaluation bundle under
#      paper/measured/evaluation-data/ via paper/scripts/make_results.py.
#   2. Compile paper/main.tex with pdflatex + bibtex (IEEEtran class).
#   3. Copy the result to paper/output/main.pdf (the build output the project ships).
#
# Requirements: a TeX Live install providing pdflatex, bibtex, and the
# IEEEtran class (Debian/Ubuntu: texlive-latex-base texlive-latex-recommended
# texlive-latex-extra texlive-science texlive-publishers).
set -euo pipefail

# This script lives in paper/scripts/, so its parent is the paper/ directory.
paper=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

echo "[1/3] regenerating results fragments from paper/measured/evaluation-data/"
python3 "$paper/scripts/make_results.py"

if ! command -v pdflatex >/dev/null || ! command -v bibtex >/dev/null; then
  echo "error: pdflatex and bibtex are required (install TeX Live)" >&2
  exit 2
fi
if ! kpsewhich elsarticle.cls >/dev/null; then
  echo "error: elsarticle.cls not found (install texlive-publishers)" >&2
  exit 2
fi

echo "[2/3] compiling paper/main.tex"
cd "$paper"
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
bibtex main >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null

echo "[3/3] copying build output to paper/output/main.pdf"
mkdir -p "$paper/output"
cp "$paper/main.pdf" "$paper/output/main.pdf"

# Graphical abstract (standalone). Also export a PNG when a rasterizer exists.
if [ -f "$paper/graphical_abstract.tex" ]; then
  echo "[extra] building graphical abstract"
  pdflatex -interaction=nonstopmode -halt-on-error graphical_abstract.tex >/dev/null
  cp "$paper/graphical_abstract.pdf" "$paper/output/graphical_abstract.pdf"
  if command -v pdftoppm >/dev/null; then
    pdftoppm -png -r 600 -singlefile "$paper/graphical_abstract.pdf" \
      "$paper/output/graphical_abstract" >/dev/null 2>&1 || true
  fi
fi

echo "done: $paper/output/main.pdf"
