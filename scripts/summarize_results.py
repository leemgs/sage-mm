#!/usr/bin/env python3
"""Summarize independent-run CSV data with deterministic percentile bootstrap CIs."""
import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

KEYS = ("treatment", "platform", "workload", "run_id")
METRICS = ("peak_pss_mb", "allocation_rate_mb_s", "gc_p99_ms", "fault_rate_s", "input_p99_ms", "controller_cpu_pct")

def percentile(values, q):
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction

def summarize(values, rng, resamples):
    mean = sum(values) / len(values)
    boot = []
    for _ in range(resamples):
        boot.append(sum(rng.choice(values) for _ in values) / len(values))
    return {"n": len(values), "mean": mean, "ci95": [percentile(boot, .025), percentile(boot, .975)]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resamples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20260829)
    args = parser.parse_args()
    if args.resamples < 100: raise SystemExit("--resamples must be at least 100")
    groups = defaultdict(lambda: defaultdict(list))
    seen = set()
    with args.csv_file.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        missing = set(KEYS + METRICS) - set(reader.fieldnames or ())
        if missing: raise SystemExit(f"missing columns: {', '.join(sorted(missing))}")
        for line, row in enumerate(reader, 2):
            identity = tuple(row[key] for key in KEYS)
            if identity in seen: raise SystemExit(f"duplicate independent run at line {line}: {identity}")
            seen.add(identity)
            group = tuple(row[key] for key in KEYS[:3])
            for metric in METRICS:
                groups[group][metric].append(float(row[metric]))
    rng = random.Random(args.seed)
    output = {"seed": args.seed, "resamples": args.resamples, "groups": []}
    for group in sorted(groups):
        output["groups"].append({
            "treatment": group[0], "platform": group[1], "workload": group[2],
            "metrics": {metric: summarize(groups[group][metric], rng, args.resamples) for metric in METRICS}
        })
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

if __name__ == "__main__": main()
