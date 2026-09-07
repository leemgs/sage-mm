#!/usr/bin/env bash
# RQ1-extended: per-architecture INITIAL_ALLOC heap sweep.
# Emits heap_sweep_30run.csv (see docs/EXPERIMENT_SCHEMAS.md).
set -euo pipefail

OUT="${1:-heap_sweep_30run.csv}"
PLATFORM="${PLATFORM:?set PLATFORM to the device id, e.g. ARM32}"
SEED="${SEED:-20260906}"
N_RUNS="${N_RUNS:-30}"
ALLOCS="${ALLOCS:-8 16 32 64 128}"   # INITIAL_ALLOC values (MiB) to sweep

header="data_status,synthetic,n_runs,seed,platform,initial_alloc_mb,run_id,peak_pss_mb,gc_count,gc_p50_ms,gc_p95_ms,gc_p99_ms,gc_max_ms,compaction_ms,resident_mb,censored,censor_reason"
echo "$header" > "$OUT"

# Replace this hook with real device measurement. It MUST echo one CSV row of
# metrics (peak_pss_mb..resident_mb) for one run, or exit non-zero on failure.
run_one_condition() {
  local alloc="$1" run_id="$2"
  echo "TODO: measure INITIAL_ALLOC=${alloc}MiB run ${run_id} on ${PLATFORM}" >&2
  return 3   # not implemented: do not fabricate data
}

for alloc in $ALLOCS; do
  for run_id in $(seq 1 "$N_RUNS"); do
    if metrics="$(run_one_condition "$alloc" "$run_id")"; then
      echo "measured,false,${N_RUNS},${SEED},${PLATFORM},${alloc},${run_id},${metrics},false," >> "$OUT"
    else
      echo "measured,false,${N_RUNS},${SEED},${PLATFORM},${alloc},${run_id},,,,,,,,true,run_failed" >> "$OUT"
    fi
  done
done
echo "wrote $OUT" >&2
