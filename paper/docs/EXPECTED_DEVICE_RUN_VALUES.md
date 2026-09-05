# ARM32/ARM64 장치 실험의 예상 per-run 값

> **사전등록용 예상 범위이며 측정 결과가 아니다.** 이 저장소에는 vendor Mono
> 패치, 상용 DTV trace, 또는 장치별 stock 기준값이 없다. 따라서 아래 값은
> 합성 관측치나 논문의 결과로 인용할 수 없다. 절대값은 반드시 각 장치의
> `Stock` pilot에서 정하고, 본 실험에서는 아래의 stock 대비 비율과 안전 한계를
> 검증한다. 범위를 벗어난 run도 삭제하지 않고 그대로 보고한다.

## 먼저 결론: 기대할 수 있는 크기

동일한 장치ㆍworkloadㆍ30분 구간에서 얻은 `Stock` run의 지표를 각각 100으로
놓으면, full treatment인 `1111`/`EWMA-GIR`의 현실적인 중심 가설은 다음과 같다.

| per-run 지표 | ARM32 기대 범위 | ARM64 기대 범위 | 중앙 계획값 |
|---|---:|---:|---:|
| peak PSS / Stock | 0.72--0.82 | 0.78--0.88 | 0.77 / 0.83 |
| allocation bytes / Stock | 0.65--0.80 | 0.68--0.84 | 0.72 / 0.76 |
| GC count / Stock | 0.65--0.85 | 0.72--0.92 | 0.75 / 0.82 |
| GC pause p99 / Stock | 0.55--0.72 | 0.65--0.82 | 0.64 / 0.73 |
| compacting-GC count / Stock | 0.30--0.55 | 0.55--0.80 | 0.40 / 0.67 |
| minor faults/s / Stock | 1.15--1.35 | 1.10--1.30 | 1.25 / 1.20 |
| major faults/s / Stock | 1.00--1.20 | 1.00--1.15 | 별도 보고 |
| input-latency p99 / Stock | 0.75--0.88 | 0.80--0.92 | 0.82 / 0.86 |
| controller CPU | 0.5--1.5% | 0.4--1.3% | 1% 이하 선호 |

이 표의 architecture 차이는 검증할 가설이지 이미 알려진 사실이 아니다. 특히
ARM64에서 ARM32보다 큰 개선이 관찰되어도 실패로 처리하지 않는다. Ridge의
추가 이득은 EWMA 대비 PSS 0--3 percentage points, GC/input p99 0--4 points 정도만
기대한다. run-level 95% CI가 겹치거나 CPU가 1.5%를 넘으면 “ML 우위 없음”으로
판정한다.

절대값이 필요한 경우에는 임의의 MiB/ms 값을 만들지 말고 다음처럼 변환한다.
예를 들어 같은 block의 Stock median peak PSS가 420 MiB이고 GC p99가 25 ms라면,
ARM32 full-treatment 예상 범위는 각각 **302--344 MiB**와 **13.8--18.0 ms**이다.
ARM64 Stock 값이 700 MiB와 16 ms라면 각각 **546--616 MiB**와
**10.4--13.1 ms**이다. 이는 계산 예일 뿐 장치 예측값이 아니다.

## EventPipe/vendor GC trace에서 한 run마다 남길 값

Mono build가 EventPipe를 완전히 지원할 때는 runtime provider의 GC start/stop,
suspend/restart, allocation tick, heap stats 이벤트를 사용한다. vendor build에서
이벤트가 빠지면 “0”으로 채우지 말고 `unsupported`로 기록하고 동등한 vendor GC
trace를 별도 원천으로 보존한다. demo의 forced Gen-0 stopwatch 값은 여기 섞지
않는다.

각 run에서 다음을 event timestamp로 계산한다.

* `gc_count_gen0/gen1/gen2`, compacting 및 blocking GC count;
* `pause_ms_p50/p95/p99/max` (GC-induced suspension 구간의 wall-clock duration);
* `gc_pause_total_ms`와 run wall time 대비 pause ratio;
* allocated bytes 및 MiB/min, promoted bytes, heap size/fragmentation의 시계열;
* trace loss count, dropped events, provider/keyword, runtime commit 및 clock source.

30분 run에서 GC가 100회 미만이면 p99는 사실상 최대값에 매우 민감하다. 이때도
interval sample을 독립 반복으로 늘리지 말고 count와 max를 함께 보고한다. 예상
방향은 `G`가 pause/count를, `I`가 allocation/promoted bytes를 주로 낮추고, `C`가
compacting GC와 tail을 낮추는 것이다. GC가 전혀 없는 run은 pause p99=0이 아니라
`NA (zero events)`이다.

## `smaps`의 `Private_Clean`

reclamation 직전과 syscall 완료 직후에 동일 mapping identity
(`start-end`, inode, offset, pathname)를 맞춰 다음을 byte 단위로 저장한다.

```text
eligible_private_clean_before
eligible_private_clean_after
private_clean_drop = max(0, before - after)
reclaim_efficiency = private_clean_drop / requested_candidate_bytes
refault_private_clean_1s, refault_private_clean_10s, refault_private_clean_60s
```

프로세스 전체 `Private_Clean` 변화는 mapping load/unload와 kernel accounting이
섞이므로 “회수 byte”가 아니다. 예상 가능한 값은 절대 MiB가 아니라 다음 비율이다.

| 상황 | action당 `before-after` / 요청 byte | 60초 내 refault / drop | 기대 해석 |
|---|---:|---:|---|
| cold, guarded | 0.35--0.75 | 0--0.20 | 유효한 회수 |
| 정상 switching, guarded | 0.25--0.60 | 0.10--0.40 | 허용 가능 |
| hot reuse | 0.10--0.45 | 0.40--0.90 | guard가 action을 억제해야 함 |
| static/unguarded | 0.40--0.85 | 0.30--0.90 | PSS는 낮아져도 fault 위험 |

`Private_Clean` drop이 요청 byte보다 큰 경우, 음수인 경우, 또는 mapping identity가
달라진 경우는 자동 성공으로 보지 않고 concurrent mapping 변화로 표시한다.
`R=0` cell에서 자연 변동이 있으므로 paired action window의 noise floor를 먼저
측정한다. 유효 회수의 최소 기준은 `(drop - matched control noise) > 0`이며, writable,
anonymous, shared mapping 선택은 단 한 건도 허용하지 않는다.

## 30분 이상 run의 예상치와 판정

warm-up은 통계 구간에서 분리하고, 측정 구간은 최소 30분으로 고정한다. 각
platform × workload × cell에 독립 cold reset/seed run을 **최소 30회** 수행한다.
각 run은 하나의 관측치이며, 한 run 안의 초 단위 샘플은 `n`을 늘리지 않는다.

* full treatment의 계획 효과: peak PSS -18%~-28%, allocation -20%~-35%,
  GC p99 -28%~-45%, input p99 -12%~-25%;
* guarded reclamation의 대가: minor-fault rate +15%~+35%;
* `Static-GIR`의 예상 adverse control: fault-rate index 145--175 및 input p99
  -2%~+8% (즉 tail 개선이 사라질 수 있음);
* guarded policy는 `Static-GI` 대비 fault +35%, storage bytes read +10%,
  input/frame p99 +5%를 넘지 않아야 한다;
* run 간 coefficient of variation의 초기 planning band는 PSS 3--8%, GC p99
  10--25%, fault rate 15--35%, latency p99 10--25%이다. 이 값으로 pilot 후
  power analysis를 다시 하되, 관측된 변동이 크다는 이유로 run을 버리지 않는다.

16개 factorial cell × 2개 architecture × 30 runs × 0.5 h만으로도 최소
**480 device-hours**이다(추가 workload, warm-up, reset, 실패 재시도 제외).

## 8시간 endurance

사용자 요구를 동일하게 적용하면 각 endurance cell도 성공 run만 골라 30회가
아니라, 시작한 독립 run **30개 전부**를 결과에 포함한다. 최소 원시 시간은
cell당 240 device-hours이다. 16 cell과 두 architecture 모두에 적용하면
**7,680 device-hours**이므로, 비용 때문에 primary endurance cell을 사전에
축소한다면 “모든 cell ≥30”이라고 주장해서는 안 된다.

8시간 run에는 위의 per-run aggregate뿐 아니라 5분 또는 10분 bin trajectory를
보존한다. 기대 안정 범위는 다음과 같다.

* 첫 30분 이후 PSS robust slope: full treatment **-0.5~+1.0 MiB/hour**;
* 마지막 1시간 median PSS / 첫 안정 1시간 median PSS: **0.95--1.08**;
* GC pause p99와 fault rate의 마지막/첫 안정 1시간 비: 각각 **0.8--1.2** 및
  **0.8--1.3**;
* OOM, watchdog restart, correctness failure, use-after-unload: **0건**;
* trace loss: **0건**이 목표이며, 발생 시 run을 숨기지 않고 해당 구간을
  censoring 사유와 함께 표시한다.

OOM 0/30은 “OOM 확률 0”을 증명하지 않는다. 실패가 0건일 때 독립 Bernoulli
가정의 rule-of-three 상 95% 단측 상한은 약 **10% (3/30)**이다. 따라서
production 안정성을 강하게 주장하려면 30회보다 훨씬 많은 독립 run 또는 더
좁은 사전등록 reliability 목표가 필요하다.

## 집계와 최종 보고

각 cell은 median(또는 사전 지정한 mean), effect vs 같은 randomized block의
Stock, 10,000회 run-level bootstrap 95% CI, `n_started/n_completed/n_censored`,
device-hours를 함께 표시한다. 30분 run과 8시간 run을 합쳐 하나의 `n`으로 만들지
않는다. thermal throttle, OOM, trace loss, syscall errno도 결과이며 사후 제외
조건으로 사용하지 않는다. 위 예상 범위에 들어왔다는 사실만으로 PASS가 되지
않고, 안전 한계와 CI를 모두 만족해야 한다.

