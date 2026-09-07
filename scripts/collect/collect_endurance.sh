#!/usr/bin/env bash
# RQ3-extended: endurance + adverse-injection battery.
# Emits endurance_adverse_30run.csv (see docs/EXPERIMENT_SCHEMAS.md).
set -euo pipefail

OUT="${1:-endurance_adverse_30run.csv}"
PLATFORM="${PLATFORM:?set PLATFORM to the device id}"
SEED="${SEED:-20260906}"
N_RUNS="${N_RUNS:-30}"
TREATMENT="${TREATMENT:-Ridge-GIR}"
STRESSES="${STRESSES:-cold hot_reuse switch_1s switch_5s switch_10s slow_storage madvise_fail fault_storm endurance_8h}"

header="data_status,synthetic,n_runs,seed,platform,treatment,stress,run_id,duration_s,private_clean_before_mb,private_clean_after_mb,minor_faults,major_faults,bytes_read_mb,reload_latency_ms,input_p99_ms,frame_drops,guard_activations,oom_events,censored,censor_reason"
echo "$header" > "$OUT"

# Replace with real measurement: echo one row of metrics
# (duration_s..oom_events) for one run, or exit non-zero.
run_one_condition() {
  local stress="$1" run_id="$2"
  echo "TODO: measure ${TREATMENT}/${stress} run ${run_id} on ${PLATFORM}" >&2
  return 3
}

for stress in $STRESSES; do
  for run_id in $(seq 1 "$N_RUNS"); do
    if metrics="$(run_one_condition "$stress" "$run_id")"; then
      echo "measured,false,${N_RUNS},${SEED},${PLATFORM},${TREATMENT},${stress},${run_id},${metrics},false," >> "$OUT"
    else
      echo "measured,false,${N_RUNS},${SEED},${PLATFORM},${TREATMENT},${stress},${run_id},,,,,,,,,,,true,run_failed" >> "$OUT"
    fi
  done
done
echo "wrote $OUT" >&2
