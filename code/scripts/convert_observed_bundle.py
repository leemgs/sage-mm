#!/usr/bin/env python3
"""Convert the observed SAGE-MM raw bundle into the run-level analysis contract.

Input is the provenance-backed, non-synthetic bundle under
``experiments/observed/`` (manifest + provenance + per-run CSV). Output is a
CSV with exactly the columns ``scripts/summarize_results.py`` consumes:

    treatment,platform,workload,run_id,peak_pss_mb,allocation_rate_mb_s,
    gc_p99_ms,fault_rate_s,input_p99_ms,controller_cpu_pct

This converter is intentionally conservative and fail-closed:

* It refuses to run unless the bundle declares ``data_status=observed`` and
  ``synthetic=false``. Synthetic or unlabeled inputs are rejected so simulated
  rows can never be laundered into an observed CSV.
* It carries the raw provenance forward unchanged; it does NOT invent a
  firmware identity, does NOT relabel the Python ``/proc`` collector as a
  vendor GC/EventPipe trace, and does NOT promote the process-wide
  ``smaps_rollup`` PSS into per-mapping ``Private_Clean`` reclaimed bytes.
* ``treatment`` keeps the full 2x2x2x2 ``GxIyRzCw`` cell code so every one of
  the 16 factorial cells stays distinct; ``platform`` records the *actual*
  measurement substrate (ARM64 Linux, Python collector), not the user-specified
  target environment, so no reader mistakes the proxy harness for firmware.

The output of this script is observed evidence for the proxy harness only. It
does not satisfy the vendor DTV Mono/.NET6 measured-result bar documented in
``paper/docs/MEASURED_DEVICE_RUN_VALUES.md``.
"""
import argparse
import csv
import json
from pathlib import Path

# The measurement substrate actually recorded in the provenance, NOT the
# user-specified target environment. Kept explicit so the proxy harness is
# never read as the vendor firmware.
PLATFORM = "arm64-linux-proxy"
WORKLOAD = "switch-burst"

OUT_FIELDS = (
    "treatment", "platform", "workload", "run_id",
    "peak_pss_mb", "allocation_rate_mb_s", "gc_p99_ms",
    "fault_rate_s", "input_p99_ms", "controller_cpu_pct",
)


def _require(condition, message):
    if not condition:
        raise SystemExit(f"refusing to convert bundle: {message}")


def load_manifest(path):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    _require(manifest.get("data_status") == "observed",
             f"manifest data_status is {manifest.get('data_status')!r}, expected 'observed'")
    _require(manifest.get("synthetic") is False,
             f"manifest synthetic is {manifest.get('synthetic')!r}, expected false")
    return manifest


def convert(rows):
    out = []
    seen = set()
    for line, row in enumerate(rows, 2):
        # Row-level guard: never let a synthetic row through.
        _require(row.get("data_status") == "observed" and row.get("synthetic") == "False",
                 f"non-observed row at line {line}: "
                 f"data_status={row.get('data_status')!r} synthetic={row.get('synthetic')!r}")
        treatment = row["treatment"]
        run_id = row["run"]
        identity = (treatment, PLATFORM, WORKLOAD, run_id)
        _require(identity not in seen, f"duplicate independent run at line {line}: {identity}")
        seen.add(identity)
        out.append({
            "treatment": treatment,
            "platform": PLATFORM,
            "workload": WORKLOAD,
            "run_id": run_id,
            # pss_kib is the shared/proportional set size from smaps_rollup.
            "peak_pss_mb": f"{float(row['pss_kib']) / 1024.0:.6f}",
            "allocation_rate_mb_s": row["allocation_rate_mib_s"],
            # gc_p99_ms here is Python gc.collect timing, a proxy for -- not a
            # measurement of -- a managed .NET/Mono GC pause. Carried verbatim.
            "gc_p99_ms": row["gc_p99_ms"],
            "fault_rate_s": row["fault_rate_s"],
            "input_p99_ms": row["input_p99_ms"],
            "controller_cpu_pct": row["controller_cpu_percent"],
        })
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parents[1]
    parser.add_argument("--bundle", type=Path,
                        default=here / "experiments" / "observed")
    parser.add_argument("--output", type=Path,
                        default=here / "experiments" / "observed" / "observed_runs.csv")
    args = parser.parse_args()

    manifest = load_manifest(args.bundle / "manifest_sage_mm_observed.json")
    # utf-8-sig tolerates a byte-order mark on the first header cell.
    with (args.bundle / "per_run_measurements_sage_mm_observed.csv").open(
            newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))

    _require(len(rows) == manifest["total_runs"],
             f"row count {len(rows)} != manifest total_runs {manifest['total_runs']}")

    converted = convert(rows)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUT_FIELDS)
        writer.writeheader()
        writer.writerows(converted)

    treatments = sorted({r["treatment"] for r in converted})
    print(f"wrote {args.output} ({len(converted)} runs, "
          f"{len(treatments)} factorial cells, platform={PLATFORM})")


if __name__ == "__main__":
    main()
