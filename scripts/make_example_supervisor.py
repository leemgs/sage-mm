#!/usr/bin/env python3
"""Generate a SYNTHETIC reference CSV for the R-M3 AdverseShutdown experiment.

This is NOT device data. It is a hand-modeled, deterministic example showing the
schema and the *intended* result shape for the adverse-regime supervisor arm
(reviewer point R-M3). Every row is stamped data_status=simulated,
synthetic=True, a distinct seed, and the file name carries `.example`, so it can
never be mistaken for the measured bundle and is not read by make_results.py.

Two treatments in the adverse (regression) regime, n=30 per platform per arm:
  * Ridge-GIR       -- supervisor OFF (current behavior; the measured regression)
  * Ridge-GIR-sup   -- supervisor ON (AdverseShutdown latches reclamation off)

Intended, visible contrast a real measurement should reproduce:
  With the supervisor ON, input p99 and fault rate fall back toward the Stock
  baseline (the regression is *contained*), controller CPU drops (less
  thrashing), peak PSS rises slightly (no reclamation savings), and the new
  columns record how fast it latches and recovers:
    guard_activations   AdverseShutdown latch events (0 when OFF, >0 when ON)
    time_to_latch_s     detection delay from adverse onset to latch
    recovery_time_s     time to resume after signals fall below hysteresis
    oom_events          OOM count (supervisor should reduce it)

Output: paper/examples/adverse_supervisor.example.csv
Regenerate: python3 scripts/make_example_supervisor.py
"""
from __future__ import annotations
import csv
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "paper", "examples", "adverse_supervisor.example.csv")

SEED = 20260201
N = 30
PLATFORMS = ["ARM32-scenario", "ARM64-scenario"]

COLUMNS = [
    "data_status", "synthetic", "n_runs", "seed", "scenario", "platform_scenario",
    "treatment", "run_id", "run_status",
    "peak_pss_mb", "allocation_rate_mb_s", "gc_p99_ms", "fault_rate_s",
    "input_p99_ms", "controller_cpu_pct",
    "guard_activations", "time_to_latch_s", "recovery_time_s", "oom_events",
]

# Anchors from the measured adverse (regression) regime; the OFF arm reproduces
# the measured Ridge-GIR regression, the ON arm contains it toward Stock.
# means keyed by platform -> metric.
OFF = {  # supervisor OFF == measured Ridge-GIR adverse
    "ARM32-scenario": dict(pss=249.8, alloc=41.7, gc=55.6, fault=126.5, inp=119.5, cpu=2.2),
    "ARM64-scenario": dict(pss=336.8, alloc=50.5, gc=44.5, fault=160.4, inp=95.9, cpu=2.2),
}
STOCK = {  # measured Stock adverse (the containment target)
    "ARM32-scenario": dict(pss=239.8, fault=80.0, inp=99.8),
    "ARM64-scenario": dict(pss=320.6, fault=98.7, inp=79.3),
}


def jit(rng, mean, rel=0.05, lo=None):
    v = mean * (1.0 + rng.normal(0, rel))
    return max(v, lo) if lo is not None else v


def rows_for(rng, plat, arm):
    off, stock = OFF[plat], STOCK[plat]
    out = []
    for run_id in range(1, N + 1):
        if arm == "Ridge-GIR":  # supervisor OFF
            pss, alloc, gc = off["pss"], off["alloc"], off["gc"]
            fault, inp, cpu = off["fault"], off["inp"], off["cpu"]
            guard, latch, recov = 0, "", ""
            oom = 1 if rng.random() < 0.05 else 0
        else:  # Ridge-GIR-sup : supervisor ON, regression contained toward Stock
            # latch off reclamation once adverse detected: metrics move ~85% of
            # the way from OFF back to STOCK, plus a small detection-delay residual.
            def contain(off_v, stock_v, frac=0.85):
                return off_v - frac * (off_v - stock_v)
            pss = contain(off["pss"], stock["pss"], 0.75) + 3.0   # no reclaim -> near stock, small residual
            fault = contain(off["fault"], stock["fault"], 0.82)
            inp = contain(off["inp"], stock["inp"], 0.80)
            alloc = off["alloc"]
            gc = off["gc"] - 0.55 * (off["gc"] - (off["gc"] * 0.93))  # slight GC relief
            cpu = 0.9  # supervisor monitors but reclamation latched off
            guard = int(rng.integers(1, 4))          # 1-3 latch events
            latch = round(jit(rng, 3.0, 0.25, lo=0.5), 2)      # detection delay (s)
            recov = round(jit(rng, 10.0, 0.25, lo=1.0), 2)     # recovery time (s)
            oom = 0
        out.append({
            "data_status": "simulated", "synthetic": True, "n_runs": N, "seed": SEED,
            "scenario": "regression", "platform_scenario": plat, "treatment": arm,
            "run_id": run_id, "run_status": "completed",
            "peak_pss_mb": round(jit(rng, pss, 0.03), 2),
            "allocation_rate_mb_s": round(jit(rng, alloc, 0.03), 2),
            "gc_p99_ms": round(jit(rng, gc, 0.05), 2),
            "fault_rate_s": round(jit(rng, fault, 0.06, lo=0.0), 2),
            "input_p99_ms": round(jit(rng, inp, 0.04), 2),
            "controller_cpu_pct": round(jit(rng, cpu, 0.08, lo=0.0), 3) if cpu else 0.0,
            "guard_activations": guard,
            "time_to_latch_s": latch,
            "recovery_time_s": recov,
            "oom_events": oom,
        })
    return out


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rng = np.random.default_rng(SEED)
    allrows = []
    for plat in PLATFORMS:
        for arm in ["Ridge-GIR", "Ridge-GIR-sup"]:
            allrows.extend(rows_for(rng, plat, arm))
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(allrows)
    print(f"Wrote {len(allrows)} SYNTHETIC rows to {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
