#!/usr/bin/env bash
# RQ2-extended: value-type (class vs struct) interop micro/macro benchmarks.
# Emits interop_30run.csv (see docs/EXPERIMENT_SCHEMAS.md).
set -euo pipefail

OUT="${1:-interop_30run.csv}"
PLATFORM="${PLATFORM:?set PLATFORM to the device id}"
SEED="${SEED:-20260906}"
N_RUNS="${N_RUNS:-30}"

header="data_status,synthetic,n_runs,seed,platform,treatment,benchmark,run_id,allocated_bytes,allocation_rate_mb_s,peak_pss_mb,gc_p99_ms,throughput_ops_s,copy_cost_ns,native_abi_ok,censored,censor_reason"
echo "$header" > "$OUT"

# Replace with real measurement: echo one row of metrics
# (allocated_bytes..native_abi_ok) for one run, or exit non-zero.
run_one_condition() {
  local treatment="$1" benchmark="$2" run_id="$3"
  echo "TODO: measure ${treatment}/${benchmark} run ${run_id} on ${PLATFORM}" >&2
  return 3
}

for treatment in class struct; do
  for benchmark in micro macro; do
    for run_id in $(seq 1 "$N_RUNS"); do
      if metrics="$(run_one_condition "$treatment" "$benchmark" "$run_id")"; then
        echo "measured,false,${N_RUNS},${SEED},${PLATFORM},${treatment},${benchmark},${run_id},${metrics},false," >> "$OUT"
      else
        echo "measured,false,${N_RUNS},${SEED},${PLATFORM},${treatment},${benchmark},${run_id},,,,,,,,true,run_failed" >> "$OUT"
      fi
    done
  done
done
echo "wrote $OUT" >&2
