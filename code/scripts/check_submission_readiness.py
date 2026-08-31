#!/usr/bin/env python3
"""Fail closed when the TECS source still contains known submission blockers."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
tex = (root / "paper/sagemm-tecs.tex").read_text(encoding="utf-8")
bib = (root / "paper/sagemm.bib").read_text(encoding="utf-8")
blockers = []
checks = {
    r"\includesimulationtrue": "simulation-only Results mode is enabled",
    "[Institution]": "author institution is unset",
    "[City]": "author city is unset",
    "[Country]": "author country is unset",
}
for token, message in checks.items():
    if token in tex:
        blockers.append(message)
if not (root / "paper/generated/observed-results.tex").exists():
    blockers.append("provenance-backed observed-results.tex is absent")
if "Verify" in bib or "verify" in bib:
    blockers.append("bibliography still contains publisher-verification notes")
if blockers:
    print("NOT SUBMISSION READY:")
    for blocker in blockers:
        print(f"- {blocker}")
    raise SystemExit(1)
print("submission readiness gate passed")
