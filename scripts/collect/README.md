# Extension-experiment collectors

Skeleton collectors for the three future-work experiments. Each script writes a
CSV that matches `docs/EXPERIMENT_SCHEMAS.md` and calls a single device hook
(`run_one_condition`) where the **real on-device measurement** must be plugged
in. As shipped they refuse to invent numbers: the hook body is a `TODO` that you
replace with your instrumentation (EventPipe/vendor GC telemetry, `smaps`
`Private_Clean`, `mincore`, workload driver, etc.).

Workflow:
1. Implement the `run_one_condition` hook in the relevant script.
2. Run it on the target device to produce `*_30run.csv`.
3. Copy the CSV into `paper/generated/evaluation-data/`.
4. `python3 scripts/validate_bundle.py` to check schema + provenance.
5. Extend `scripts/make_results.py` to render the new tables/figures.
