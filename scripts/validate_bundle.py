#!/usr/bin/env python3
"""Validate evaluation-bundle CSVs against their schemas and the measurement gate.

Usage:
    python3 scripts/validate_bundle.py             # all known bundle files
    python3 scripts/validate_bundle.py PATH.csv    # one specific file

Checks, per file:
  * the header matches the expected schema (order-independent, prefix-tolerant);
  * provenance columns are present and consistent (data_status/synthetic/n_runs);
  * run_id covers 1..n_runs within each condition;
  * no reporting row is synthetic=true (which would keep the gate closed).

Exit code is non-zero if any checked file fails. This validator checks
structure and provenance flags only; it cannot certify that numbers came from
real hardware.
"""
import csv
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "paper", "generated", "evaluation-data")

# base column name -> allowed optional prefixes are stripped before matching
_PREFIXES = ("measured_", "simulated_")

# Expected schemas keyed by filename. Condition keys identify a distinct
# experimental cell over which run_id must run 1..n_runs.
SCHEMAS = {
    "absolute_results_30run.csv": {
        "required": {"data_status", "synthetic", "scenario",
                     "platform_scenario", "treatment", "run_id",
                     "run_status",
                     "peak_pss_mb", "allocation_rate_mb_s", "gc_p99_ms",
                     "fault_rate_s", "input_p99_ms", "controller_cpu_pct"},
        "condition": ("scenario", "platform_scenario", "treatment"),
    },
    "heap_sweep_30run.csv": {
        "required": {"data_status", "synthetic", "n_runs", "platform",
                     "initial_alloc_mb", "run_id", "peak_pss_mb", "gc_p99_ms"},
        "condition": ("platform", "initial_alloc_mb"),
    },
    "interop_30run.csv": {
        "required": {"data_status", "synthetic", "n_runs", "platform",
                     "treatment", "benchmark", "run_id", "allocation_rate_mb_s",
                     "peak_pss_mb", "native_abi_ok"},
        "condition": ("platform", "treatment", "benchmark"),
    },
    "endurance_adverse_30run.csv": {
        "required": {"data_status", "synthetic", "n_runs", "platform",
                     "treatment", "stress", "run_id", "duration_s",
                     "input_p99_ms"},
        "condition": ("platform", "treatment", "stress"),
    },
}


def norm(col):
    for p in _PREFIXES:
        if col.startswith(p):
            return col[len(p):]
    return col


def truthy(v):
    return str(v).strip().lower() in {"true", "1", "yes"}


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def validate(path, schema):
    problems, notes = [], []
    rows = load(path)
    if not rows:
        return ["empty file (header only)"], []
    have = {norm(c) for c in rows[0].keys()}
    missing = schema["required"] - have
    if missing:
        problems.append(f"missing columns: {sorted(missing)}")

    def get(row, key):
        for p in ("",) + _PREFIXES:
            if p + key in row:
                return row[p + key]
        return None

    synth = sum(1 for r in rows if truthy(get(r, "synthetic")))
    if synth:
        problems.append(f"{synth}/{len(rows)} rows are synthetic=true "
                        f"(measurement gate stays closed)")
    measured = sum(1 for r in rows
                   if str(get(r, "data_status") or "").startswith("measured"))
    if measured != len(rows):
        notes.append(f"{len(rows)-measured} rows are not data_status=measured")
    bad_status = [get(r, "run_status") for r in rows
                  if str(get(r, "run_status") or "").lower()
                  not in {"completed", "failed", "censored"}]
    if bad_status:
        problems.append(f"{len(bad_status)} rows have an invalid run_status")

    # run_id coverage per condition
    cond_runs = defaultdict(set)
    cond_n = {}
    for r in rows:
        key = tuple(get(r, k) for k in schema["condition"])
        rid = get(r, "run_id")
        if rid not in (None, ""):
            try:
                cond_runs[key].add(int(float(rid)))
            except ValueError:
                pass
        n = get(r, "n_runs")
        if n not in (None, ""):
            try:
                cond_n[key] = int(float(n))
            except ValueError:
                pass
    for key, ids in sorted(cond_runs.items()):
        n = cond_n.get(key, max(ids) if ids else 0)
        expected = set(range(1, n + 1))
        if ids != expected:
            miss = sorted(expected - ids)[:5]
            extra = sorted(ids - expected)[:5]
            problems.append(
                f"condition {key}: run_id coverage != 1..{n} "
                f"(missing {miss}{'...' if len(miss)==5 else ''}, "
                f"extra {extra})")
    notes.append(f"{len(rows)} rows, {len(cond_runs)} conditions")
    return problems, notes


def main(argv):
    if len(argv) > 1:
        targets = [(os.path.basename(p), p) for p in argv[1:]]
    else:
        targets = [(name, os.path.join(DATA, name)) for name in SCHEMAS]

    any_fail, any_checked = False, False
    for name, path in targets:
        schema = SCHEMAS.get(os.path.basename(name))
        if not os.path.exists(path):
            if len(argv) > 1:
                print(f"[MISS] {name}: not found")
                any_fail = True
            continue
        if schema is None:
            print(f"[SKIP] {name}: no schema registered")
            continue
        any_checked = True
        problems, notes = validate(path, schema)
        tag = "FAIL" if problems else "OK"
        any_fail = any_fail or bool(problems)
        print(f"[{tag}] {name}  ({'; '.join(notes)})")
        for p in problems:
            print(f"       - {p}")

    if not any_checked and len(argv) == 1:
        print("no bundle files present yet; drop CSVs into "
              "paper/generated/evaluation-data/ (see docs/EXPERIMENT_SCHEMAS.md)")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
