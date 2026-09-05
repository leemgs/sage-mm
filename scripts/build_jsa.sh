#!/usr/bin/env bash
# Build the Journal of Systems Architecture (Elsevier elsarticle) PDF.
#
#   bash scripts/build_jsa.sh              # internal draft (simulation watermark)
#   bash scripts/build_jsa.sh --submission # runs the fail-closed JSA gate first
#
# The manuscript is regenerated from the shared TECS source so the two venue
# versions never drift. A --submission build refuses to proceed until every
# blocker in check_jsa_readiness.py is cleared.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

# Keep sagemm-jsa.tex in sync with the TECS source.
python3 "$root/scripts/make_jsa.py"

# NOTE: code/scripts/generate_simulated_results.py --check is intentionally NOT
# invoked here. Since the code//paper/ split (commit 4b6ef73) its hard-coded
# ROOT no longer resolves the paper/ artifacts, so --check reports false
# staleness. Re-enable this freshness check once that generator is taught the
# split layout. The JSA gate below does not depend on it.

if [[ "${1:-}" == "--submission" ]]; then
  python3 "$root/scripts/check_jsa_readiness.py"
fi

if ! command -v pdflatex >/dev/null || ! command -v bibtex >/dev/null; then
  echo "pdflatex and bibtex are required" >&2
  exit 2
fi
if ! kpsewhich elsarticle.cls >/dev/null; then
  echo "elsarticle.cls is required (for example, install texlive-publishers)" >&2
  exit 2
fi

cd "$root/paper"
pdflatex -interaction=nonstopmode -halt-on-error sagemm-jsa.tex
bibtex sagemm-jsa
pdflatex -interaction=nonstopmode -halt-on-error sagemm-jsa.tex
pdflatex -interaction=nonstopmode -halt-on-error sagemm-jsa.tex
echo "built paper/sagemm-jsa.pdf"
