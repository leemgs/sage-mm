#!/usr/bin/env python3
import csv
from itertools import product
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "experiments" / "expected_factorial_targets.csv"
with path.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
keys = {(int(r["g"]), int(r["i"]), int(r["r"]), int(r["c"])) for r in rows}
expected = set(product((0, 1), repeat=4))
assert len(rows) == 16 and keys == expected, "expected target matrix must contain every factorial cell exactly once"
stock = next(r for r in rows if (r["g"], r["i"], r["r"], r["c"]) == ("0", "0", "0", "0"))
for metric in ("expected_peak_pss_index", "expected_allocation_rate_index", "expected_gc_p99_index", "expected_fault_rate_index", "expected_input_p99_index"):
    assert float(stock[metric]) == 100, f"Stock {metric} must be normalized to 100"
print("validated 16 prospective factorial targets")
