#!/usr/bin/env python3
"""Fail closed when the TECS source still contains known submission blockers."""
from pathlib import Path

# Since commit 4b6ef73 the paper/ tree lives at the repository root, not under
# code/. This file is code/scripts/check_submission_readiness.py, so the repo
# root is parents[2]; parents[1] (code/) no longer contains paper/.
root = Path(__file__).resolve().parents[2]
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
observed = root / "paper/generated/observed-results.tex"
if not observed.exists():
    blockers.append("provenance-backed observed-results.tex is absent")
else:
    body = observed.read_text(encoding="utf-8")
    if "not firmware evidence" in body or "proxy" in body.lower():
        blockers.append(
            "observed-results.tex holds the ARM64-Linux proxy-harness fragment, "
            "not vendor DTV Mono/.NET6 firmware measurements")
if "Verify" in bib or "verify" in bib:
    blockers.append("bibliography still contains publisher-verification notes")
if blockers:
    print("NOT SUBMISSION READY:")
    for blocker in blockers:
        print(f"- {blocker}")
    raise SystemExit(1)
print("submission readiness gate passed")
