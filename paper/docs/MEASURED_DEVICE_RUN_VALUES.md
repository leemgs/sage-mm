# ARM32/ARM64 장치의 measured per-run 값

> **현재 상태: 측정 데이터 미제공.** 이 문서는 measured 결과를 기록하는
> 표준 형식이다. 저장소에는 vendor Mono 패치, 상용 DTV raw trace, EventPipe/GC
> 로그, `smaps` snapshot 또는 run manifest가 없으므로 숫자를 measured 값으로
> 승격하지 않는다. 실제 bundle을 추가하기 전까지 결과 셀은 `NA`로 유지한다.

## Measured 결과 표

아래 표는 실제 raw bundle에서 생성해야 한다. 수기 입력이나 기존 prospective
target의 복사는 허용하지 않는다.

| Platform | Cell | Duration | n started/completed/censored | Peak PSS | Allocation | GC count | GC pause p99 | `Private_Clean` drop | Minor/major faults | Input p99 | Controller CPU |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ARM32 DTV | Stock | ≥30 min | NA | NA | NA | NA | NA | NA | NA | NA | NA |
| ARM32 DTV | EWMA-GIR / `1111` | ≥30 min | NA | NA | NA | NA | NA | NA | NA | NA | NA |
| ARM64 DTV | Stock | ≥30 min | NA | NA | NA | NA | NA | NA | NA | NA | NA |
| ARM64 DTV | EWMA-GIR / `1111` | ≥30 min | NA | NA | NA | NA | NA | NA | NA | NA | NA |
| ARM32 DTV | selected endurance cells | 8 h | NA | NA | NA | NA | NA | NA | NA | NA | NA |
| ARM64 DTV | selected endurance cells | 8 h | NA | NA | NA | NA | NA | NA | NA | NA | NA |

최종 표에는 모든 16개 factorial cell과 모든 workload가 들어가야 한다. 각
platform × workload × cell은 독립 cold reset/seed run을 최소 30회 수행하며,
한 run 안의 interval sample은 독립 `n`으로 세지 않는다.

## EventPipe/vendor GC measured 필드

각 run에서 원본 trace와 함께 다음 값을 event timestamp로 계산한다.

* `gc_count_gen0/gen1/gen2`, compacting 및 blocking GC count;
* `pause_ms_p50/p95/p99/max`, total pause 및 wall-time 대비 pause ratio;
* allocated/promoted bytes, MiB/min, heap size와 fragmentation trajectory;
* trace loss/dropped-event count, provider와 keyword, runtime commit, clock source.

vendor Mono build에서 필요한 EventPipe event가 없으면 `0`으로 기록하지 않고
`unsupported`로 기록한다. 동등한 vendor GC trace를 사용할 경우 collector 이름,
버전, event mapping을 manifest에 남긴다. GC event가 없는 정상 run의 pause p99는
`0`이 아니라 `NA (zero events)`이다. demo의 forced Gen-0 stopwatch 값은 실제
runtime pause 측정과 합치지 않는다.

## `smaps` `Private_Clean` measured 필드

reclamation 직전과 syscall 직후 동일 mapping identity(`start-end`, inode,
offset, pathname)를 연결해 byte 단위로 저장한다.

```text
eligible_private_clean_before
eligible_private_clean_after
private_clean_drop = before - after
requested_candidate_bytes
reclaim_efficiency = private_clean_drop / requested_candidate_bytes
refault_private_clean_1s
refault_private_clean_10s
refault_private_clean_60s
```

프로세스 전체 `Private_Clean` 차이는 mapping load/unload와 kernel accounting이
섞이므로 reclaimed bytes로 보고하지 않는다. 음수 drop, 요청 byte보다 큰 drop,
identity 변경은 0으로 clamp하여 성공 처리하지 말고 각각 원값과 anomaly flag를
남긴다. `R=0` matched control window의 noise도 함께 보고한다. writable,
anonymous, shared mapping이 선택되면 해당 run은 안전성 실패다.

## 30분 및 8시간 run

warm-up은 측정 구간과 분리하고 짧은 run의 측정 구간은 최소 30분으로 고정한다.
16 cells × 2 architectures × 30 runs × 0.5 h의 최소 raw 실행 시간은
**480 device-hours**이며, workloadㆍwarm-upㆍreset 시간은 별도다.

8시간 조건에도 셀당 30회를 적용하면 cell당 **240 device-hours**이다. 16개 셀과
두 architecture 전체에는 **7,680 device-hours**가 필요하다. 비용 때문에
endurance cell을 사전에 줄였다면 실제 실행한 셀만 보고하고 “모든 셀 ≥30”으로
표현하지 않는다. 성공한 run만 선택하지 말고 시작한 run의 OOM, watchdog,
correctness failure, trace loss 및 censoring을 모두 포함한다.

8시간 run은 aggregate와 5분 또는 10분 bin trajectory를 함께 보존한다. 최소
보고 항목은 첫 안정 1시간과 마지막 1시간의 median PSS, robust PSS slope,
GC-pause p99 ratio, fault-rate ratio, OOM/kernel/watchdog log다. 0/30 OOM은 장애
확률 0의 증거가 아니며, 독립 Bernoulli 가정의 rule-of-three 95% 단측 상한은
약 10%다.

## Measured 판정 및 집계

각 cell은 사전 지정 statistic, 동일 randomized block의 Stock 대비 effect,
10,000회 run-level bootstrap 95% CI, `n_started/n_completed/n_censored`, 총
device-hours를 보고한다. 30분과 8시간 run은 별도 population으로 유지한다.
thermal throttle, OOM, trace loss와 syscall errno는 결과이므로 예상 범위 밖이라는
이유로 제외하지 않는다.

관측 bundle이 추가되면 이 문서의 `NA`를 직접 고치는 대신 versioned raw data에서
표를 재생성하고, commit/hash와 생성 명령을 표 아래에 기록한다. 그 전까지 이
저장소가 제공하는 모든 숫자는 prospective 또는 simulation이며 measured 결과가
아니다.
