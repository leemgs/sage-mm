#!/usr/bin/env python3
"""Fail-closed submission gate for the Journal of Systems Architecture build.

Reports every known blocker that must be cleared before the elsarticle
manuscript (paper/sagemm-jsa.tex) is honestly submittable to JSA. It never
fabricates readiness: with the repository as shipped it is expected to FAIL,
because the Results are still simulation-mode and no vendor-firmware observed
bundle exists.

Unlike the older code/scripts/check_submission_readiness.py (which assumed the
paper lived under code/), this locates the repository root correctly: this file
is scripts/check_jsa_readiness.py, so parents[1] is the repo root.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
paper = root / "paper"
tex = (paper / "sagemm-jsa.tex").read_text(encoding="utf-8")
bib = (paper / "sagemm.bib").read_text(encoding="utf-8")

blockers = []

# 1. Results must be real, not the watermarked simulation dry run.
if r"\includesimulationtrue" in tex:
    blockers.append(
        "simulation-only Results mode is enabled (\\includesimulationtrue); a "
        "submission build must set \\includesimulationfalse")

# 2. A provenance-backed observed-results fragment must exist AND represent
#    vendor-firmware evidence. Its mere presence is necessary, not sufficient:
#    the observed proxy-harness bundle does not clear this on its own.
observed = paper / "generated" / "observed-results.tex"
if not observed.exists():
    blockers.append("provenance-backed observed-results.tex is absent")
else:
    body = observed.read_text(encoding="utf-8")
    if "not firmware evidence" in body or "proxy" in body.lower():
        blockers.append(
            "observed-results.tex currently holds the ARM64-Linux proxy-harness "
            "fragment, not vendor DTV Mono/.NET6 firmware measurements")

# 3. Author affiliation placeholders must be filled.
for token, label in (("[Institution]", "institution"),
                     ("[City]", "city"),
                     ("[Country]", "country")):
    if token in tex:
        blockers.append(f"author {label} placeholder {token} is unset")

# 4. Bibliography must be publisher-verified (no lingering verify notes).
if "Verify" in bib or "verify" in bib:
    blockers.append("bibliography still contains publisher-verification notes")

# 5. Elsevier-required side artifacts must be present in the repo.
for rel in ("HIGHLIGHTS_JSA.md", "DECLARATIONS_JSA.md", "COVER_LETTER_JSA.md"):
    if not (paper / rel).exists():
        blockers.append(f"required submission artifact paper/{rel} is missing")

# 6. Elsevier-required manuscript statements must be present.
for needle, label in (
        ("Declaration of competing interest", "competing-interest statement"),
        ("Data availability", "data-availability statement"),
        ("CRediT authorship contribution statement", "CRediT statement")):
    if needle not in tex:
        blockers.append(f"manuscript is missing the {label}")

if blockers:
    print("JSA: NOT SUBMISSION READY")
    for blocker in blockers:
        print(f"- {blocker}")
    raise SystemExit(1)
print("JSA submission readiness gate passed")
