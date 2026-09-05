# 저널 선정 메모 — Journal of Systems Architecture (JSA) 목표

> **목적.** SAGE-MM 원고의 투고 저널을 **Journal of Systems Architecture (JSA, Elsevier)**
> 로 확정하는 근거와, 그 목표에 도달하기 위한 준비 상태·잔여 과제를 정리한다.
> 본 메모는 내부 판단용이며 원고 본문이 아니다.

## 1. 결론 (권고)

- **투고 저널: Journal of Systems Architecture (JSA) — 권고함.** 연구의 성격(단일
  노드 임베디드 시스템 아키텍처, 관리형 런타임/OS 경계, ARM32/ARM64 HW·SW
  공동 고려, OS 보조 페이지 회수)이 JSA 스코프와 직접 맞는다.
- **투고 시점: 아직 준비되지 않음(Not ready).** 원고의 Results가 여전히
  시뮬레이션/목표값 기반이며, `SIMULATION-ONLY` 워터마크가 살아 있다. 이번에
  업로드된 관측 데이터(48런)는 **실제 측정값이지만 원고가 요구하는 플랫폼/런타임이
  아니어서 그대로는 원고 근거로 쓸 수 없다**(§4 참조).
- **다음 마일스톤:** 실제 DTV 펌웨어(ARM32/ARM64, 벤더 Mono/.NET6) 위에서의
  전요인(full-factorial) 관측 번들 확보. 이것이 확보되기 전까지 JSA 투고는 보류한다.

## 2. 왜 JSA인가 (스코프 적합성)

| 항목 | 원고의 성격 | JSA 스코프 부합 |
|---|---|---|
| 대상 | 단일 노드 임베디드 소비자 기기(DTV) | 임베디드 시스템 설계 및 소프트웨어/런타임 지원 — 부합 |
| 계층 | 관리형 런타임(GC)–interop–OS 페이지 회수의 교차 계층 정책 | 런타임/메모리 관리 설계, OS 경계 — 부합 |
| HW/SW | ARM32(1 GiB) vs ARM64(3 GiB) 아키텍처별 트레이드오프 | HW/SW 공동 고려, 아키텍처 특이 결과 — 부합 |
| 기여 유형 | 새 알고리즘이 아닌 **조정(coordination) + 안전 인지 제어**의 공학적 통합·실측 | 시스템 아키텍처 설계·평가 연구 — 부합 |

- 커버레터(`paper/COVER_LETTER_JSA.md`)의 "Why JSA" 문단이 이미 이 적합성을
  정확히 진술하고 있어 재사용 가능하다.
- **비용:** JSA는 하이브리드 저널. 제출 시 "publishing option"에서 **구독(subscription)
  경로**를 선택하면 APC 없이 무료. JSA 원본 소스에는 OA/CC 옵션이 없어 APC를
  유발하지 않는다(`sagemm-jsa.tex` 상단 주석에 명시).

## 3. 대안 대비 JSA의 우위 (요약)

- **vs. ACM TECS(`sagemm-tecs.tex`):** TECS도 스코프상 가능하나, ACM Open/APC
  또는 면제 확인과 아티팩트 평가 절차 확인이 필요하다(`SUBMISSION_READINESS.md`
  과제 10). JSA는 구독 경로로 확정적 무비용이며 elsarticle 변환본이 이미
  준비되어 있다.
- **vs. 병렬·분산(PDS) 계열 저널:** 커버레터의 선택적 문단대로, 본 연구는
  병렬/분산이 아닌 **단일 노드 임베디드 런타임/메모리 관리** 기여로 재스코프
  되었다. JSA가 이 성격에 정확히 부합한다.
- 두 변형본은 `scripts/make_jsa.py`로 TECS 소스에서 JSA(elsarticle)본을 생성하여
  동기화한다. **JSA를 정본으로 삼되, 본문 편집은 TECS 소스에서 하고 재생성**하는
  현재 워크플로를 유지한다(이중 편집 방지).

## 4. 결정적 이슈 — 업로드된 관측 데이터의 적합성

이번에 제공된 3개 파일(`manifest.json`, `provenance.csv`, `per_run_measurements.csv`)은
**전요인 2×2×2×2(G·I·R·C) × 3런 = 48런의 진짜 측정값**이다. 구조적으로는
원고의 사전등록 요인 설계와 일치하여 **방법론 리허설/레퍼런스 킷 검증**으로는
유용하다. 그러나 원고 본문 Results 근거로는 **부적합**하다. 이유:

1. **플랫폼 불일치.** provenance상 수집 환경은 `Linux-x86_64`(kernel 6.18.35,
   glibc2.39)이다. 원고는 **ARM32(1 GiB)/ARM64(3 GiB) DTV급 하드웨어**를 주
   평가 대상으로 명시한다(`sagemm-jsa.tex` §Setup).
2. **런타임 불일치.** 수집기는 `Python resource + /proc/self/smaps_rollup +
   monotonic_ns`, `python 3.12.13`. 원고의 대상 런타임은 **Tizen .NET 6 이미지
   내 벤더 Mono 포크**다. 즉 측정된 프로세스가 논문이 주장하는 런타임이 아니다.
3. **데이터 자체의 자기 부인(disclaimer).**
   - `provenance.csv`: *"Not SAGE-MM hardware/software evidence; measured
     research only (as actual evaluation experiment)."*
   - `manifest.json`: *"...as a proof-of-concept (POC) SAGE-MM manuscript evidence."*
   데이터 생산자가 스스로 "SAGE-MM HW/SW 증거가 아님"을 표기했으므로, 이를
   Results로 승격하면 정직성 원칙과 `ACTUAL_RESULTS.md`의 보고 규칙("목표값을
   result/improvement/evidence로 라벨하지 말 것")에 정면으로 위배된다.

**활용 가능한 범위:** 레퍼런스 킷(`code/`)의 컨트롤러 로직·안전 가드가 독립적으로
동작함을 보이는 **재현성/방법론 검증 자료**로는 인용 가능하다(원고는 이미 킷을
"보고 수치의 증거가 아님"으로 스코프함). 단, x86_64/Python 프록시임을 명시해야
한다. **원고의 핵심 주장(PSS·tail pause·fault·latency 개선)의 근거로는 쓰지 말 것.**

## 5. JSA 투고까지의 잔여 과제 (준비도 체크리스트)

`SUBMISSION_READINESS.md`, `LITERATURE_AUDIT.md`, `ACTUAL_RESULTS.md` 기준으로
JSA 문맥에 맞춰 재정리.

### A. 차단 과제 (이게 안 되면 투고 불가)
1. **[증거] 실제 DTV 관측 번들:** ARM32/ARM64 벤더 Mono/.NET6 펌웨어에서
   사전등록 실험을 실측하고, 런별 provenance·실패·검열·원시/집계 트레이스를
   보존하여 `paper/generated/observed-results.tex`를 생성. → 업로드 데이터는
   이 요건을 **충족하지 못함**(§4).
2. **[증거] 전요인 실행:** 동일 리셋·랜덤화·열·펌웨어·워크로드 조건에서 가능한
   모든 G×I×R×C 셀 실행, 상호작용·오버헤드·n·런별 95% CI 보고.
3. **[일반화] 3번째 제약 플랫폼 추가 또는 주장 축소:** 독립 조립한 제약형
   ARM64 Linux 플랫폼을 추가하거나, 제목·초록·주장을 **두 DTV 기기로 한정**.
4. **[안전] 회수 안전 측정:** `Private_Clean`, minor/major fault, 읽은 바이트,
   재적재/스토리지 지연, frame/input tail, native errno 클래스, hot reuse, 급속
   전환, 동시 실행, 언로드 동기화.
5. **[내구] 지속 실행:** 독립 8시간 런(주 플랫폼당 ≥10회, 80 device-hours),
   OOM/워치독 로그, device-hours·궤적·검열·모든 실패 보고.
6. **[비교] 대조군:** Static/Threshold/EWMA/Ridge held-out 결과. SOTA 컬렉터는
   가능하면 포팅, 불가 시 정확한 비호환 매트릭스 제시(우월성 주장 금지).

### B. 원고 품질 과제 (데이터 확보 후)
7. **시뮬레이션 프래그먼트 제거:** `\includesimulationtrue` → `false`,
   `SIMULATION-ONLY` 워터마크·목표 기반 표 전면 교체(재라벨 금지). 초록·Results·
   그림·결론·아티팩트를 **단일 관측 소스**에서 재조정.
8. **참고문헌:** 현재 `sagemm.bib` 항목 7개로 부족. publisher 확인 DOI로 교체·
   확장하고, 오인용 제거(JS 동적 taint 논문, Concurrent Pascal OS 논문). 리뷰어
   제안 문헌 정확 반영: AGC(IEEE TC 2025), LXR(PLDI 2022), Platinum(USENIX ATC
   2020), DumpKV(PVLDB 2024) — DOI/식별자 검증 후 도메인별 위치화.
9. **저자 메타데이터:** `[Institution]`,`[City]`,`[Country]` 등 플레이스홀더 교체,
   저자 순서·기여·이해상충·펀딩 확정.
10. **커버레터 마감:** `paper/COVER_LETTER_JSA.md`의 `[...]` 필드 채우기, 추천/
    제외 리뷰어 지정, 구독 경로(무 APC) 선택.

### C. 최종 게이트
11. `bash scripts/build_paper.sh --submission`(fail-closed 게이트)로 워터마크
    잔존·오버풀·인용·메타데이터 경고 해소 후 elsarticle 빌드 통과 확인.

## 6. 상태 요약 (한 눈에)

| 영역 | 상태 | 비고 |
|---|---|---|
| 저널 적합성 | ✅ 확정 | JSA 스코프에 직접 부합 |
| 비용(무 APC) | ✅ 경로 확인 | 구독 경로 선택 |
| elsarticle 변환본 | ✅ 생성됨 | `make_jsa.py`로 동기화 |
| 커버레터 초안 | 🟡 초안 존재 | `[...]` 필드 미완 |
| **실측 증거(DTV)** | ❌ 없음 | **최대 차단 요인** |
| 업로드 48런 데이터 | ⚠️ 부적합 | x86_64/Python, 자기 부인 — 킷 검증용만 |
| 3번째 플랫폼/일반화 | ❌ 미정 | 추가 또는 주장 축소 필요 |
| 안전/내구/대조군 | ❌ 미측정 | 차단 과제 |
| 참고문헌/메타데이터 | 🟡 미비 | 7개 항목, 플레이스홀더 |

**한 줄 판단:** *JSA는 올바른 목표다. 그러나 지금 투고하면 안 된다 — 실제
DTV 펌웨어 관측 증거가 확보될 때까지 보류하고, 그 사이 §5-B/C의 원고 품질
과제를 병행 정리한다.*
