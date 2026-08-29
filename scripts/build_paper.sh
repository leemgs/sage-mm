#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
python3 "$root/scripts/generate_simulated_results.py" --check

if ! command -v pdflatex >/dev/null || ! command -v bibtex >/dev/null; then
  echo "pdflatex and bibtex are required" >&2
  exit 2
fi
if ! kpsewhich acmart.cls >/dev/null; then
  echo "acmart.cls is required (for example, install texlive-publishers)" >&2
  exit 2
fi

cd "$root/paper"
pdflatex -interaction=nonstopmode -halt-on-error sagemm-tecs.tex
bibtex sagemm-tecs
pdflatex -interaction=nonstopmode -halt-on-error sagemm-tecs.tex
pdflatex -interaction=nonstopmode -halt-on-error sagemm-tecs.tex
echo "built paper/sagemm-tecs.pdf"
