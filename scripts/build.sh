#!/usr/bin/env bash
# Build the SAGE-MM Journal of Systems Architecture (Elsevier elsarticle) PDF.
#
#   bash scripts/build.sh
#
# Steps:
#   1. Regenerate the results fragments from the evaluation bundle under
#      paper/generated/evaluation-data/ via scripts/make_results.py.
#   2. Compile paper/main.tex with pdflatex + bibtex (elsarticle class).
#   3. Copy the result to ./code/main.pdf (the build output the project ships).
#
# Requirements: a TeX Live install providing pdflatex, bibtex, and the
# elsarticle class (Debian/Ubuntu: texlive-latex-base texlive-latex-recommended
# texlive-latex-extra texlive-science texlive-publishers).
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

echo "[1/3] regenerating results fragments from paper/generated/evaluation-data/"
python3 "$root/scripts/make_results.py"

if ! command -v pdflatex >/dev/null || ! command -v bibtex >/dev/null; then
  echo "error: pdflatex and bibtex are required (install TeX Live)" >&2
  exit 2
fi
if ! kpsewhich elsarticle.cls >/dev/null; then
  echo "error: elsarticle.cls not found (install texlive-publishers)" >&2
  exit 2
fi

echo "[2/3] compiling paper/main.tex"
cd "$root/paper"
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
bibtex main >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null
pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null

echo "[3/3] copying build output to code/main.pdf"
mkdir -p "$root/code"
cp "$root/paper/main.pdf" "$root/code/main.pdf"

echo "done: $root/code/main.pdf"
