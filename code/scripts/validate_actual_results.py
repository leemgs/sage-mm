#!/usr/bin/env python3
import csv
from itertools import product
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "experiments" / "actual_factorial_targets.csv"
with path.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
keys = {(int(r["g"]), int(r["i"]), int(r["r"]), int(r["c"])) for r in rows}
actual_cells = set(product((0, 1), repeat=4))
assert len(rows) == 16 and keys == actual_cells, "actual target matrix must contain every factorial cell exactly once"
stock = next(r for r in rows if (r["g"], r["i"], r["r"], r["c"]) == ("0", "0", "0", "0"))
for metric in ("actual_peak_pss_index", "actual_allocation_rate_index", "actual_gc_p99_index", "actual_fault_rate_index", "actual_input_p99_index"):
    assert float(stock[metric]) == 100, f"Stock {metric} must be normalized to 100"
print("validated 16 prospective factorial targets")
