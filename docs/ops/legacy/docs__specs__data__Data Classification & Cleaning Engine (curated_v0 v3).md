## 1. 목적과 범위

### 1.1 목적

서로 다른 형태/헤더 규칙/단위 표기를 갖는 SizeKorea 원천(7th, 8th_direct, 8th_3d) 데이터를 **표준키(standard_key) 기반의 단일 정합 데이터셋(curated_v0)**으로 통합하고, 정제 과정에서 발생 가능한 “조용한 오답(Scale/Unit/NaN 붕괴)”을 **경고(warnings) + 품질 센서(quality sensors)**로 표면화한다.

### 1.2 범위(포함)

- 헤더/메타 행이 불안정한 CSV/XLSX 소스에서 **Primary/Secondary header를 안정적으로 선택**
- Contract(`data/column_map/sizekorea_v2.json`) 기반 **exact-match 표준키 추출**
- 결측 센티널(예: `"9999"`, 공란) 제거 및 숫자 파싱
- 단위 표기/추정/강제 규칙을 통한 **m 단위 정규화**
- 통합 결과를 **Parquet**으로 저장
- 정합성/안정성 신호를 **warnings JSONL** 및 **completeness report**로 출력

### 1.3 범위(비포함)

- “측정 방법(SizeKorea 정의)”의 의미론적 검증/해석(추후 Semantic/Contract 문서에서 처리)
- 모델/메쉬 기반 측정(Geometric Layer)

---

## 2. 시스템 구성 요소

### 2.1 실행 엔트리포인트

- 스크립트: `pipelines/build_curated_v0.py`

### 2.2 계약(Contract)

- 매핑 파일: `data/column_map/sizekorea_v2.json`
    - `standard_key`별로 소스별 헤더 문자열을 **exact-match**로 정의
    - “미터(m) 기대 컬럼” 판별 로직(키 규칙)과 결합되어 단위 변환 규칙의 기준이 됨

### 2.3 출력 아티팩트

- 데이터: `data/processed/curated_v0/curated_v0.parquet`
- 경고 로그: `verification/runs/curated_v0/warnings_v3.jsonl`
- 품질 리포트: `verification/runs/curated_v0/completeness_report.md`
- (선택) 단위 실패 트레이스: `verification/runs/curated_v0/unit_fail_trace.md` / summary

---

## 3. 입력 데이터 및 전제

### 3.1 입력 소스

- 7th: `data/raw/sizekorea_raw/7th_data.csv` (실제 로드는 XLSX 우선: `7th_data.xlsx`)
- 8th_direct: `data/raw/sizekorea_raw/8th_data_direct.csv`
- 8th_3d: `data/raw/sizekorea_raw/8th_data_3d.csv`

### 3.2 헤더 구조 전제

- Primary header row: row 4 (0-index) 계열
- Code row: row 5
- Secondary header row: row 6
- Data start row: row 7 이후
- 메타키(HUMAN_ID, SEX, AGE)는 Secondary header 사용, 나머지 측정치는 Primary header 사용 (per-key header policy)

---

## 4. 처리 파이프라인(단계별)

### Stage 0 — Source Load & Header Detection

**목표:** 소스별로 Primary/Secondary header와 데이터 시작 지점을 결정하고, 헤더 오염을 제거한다.

핵심 기능:

- Primary header anchor 탐지 개선: 첫 컬럼뿐 아니라 **row 내 모든 셀에서** `"표준 측정항목 명"` 앵커를 검색
- Secondary header 토큰 확장: AGE 탐지용 `'나이'` 토큰 추가
- 헤더/코드/메타 행 제거: data start row 이전 오염 행을 드롭하여 numeric_parsing_failed 같은 “헤더 값이 데이터로 들어오는” 문제 차단

---

### Stage 1 — Contract 기반 표준키 추출(Exact Match)

**목표:** 소스 원본 컬럼명 → 표준키(`standard_key`)로 1:1 매핑하여 표준 컬럼을 구성한다.

특징:

- 자동 유사매칭 금지(조용한 오답 방지): contract는 **exact header string**을 사용
- column_not_found가 발생하면 계약/헤더를 먼저 교정하도록 설계(파이프라인이 추측하지 않음)

---

### Stage 2 — 숫자 전처리(preprocess_numeric_columns)

**목표:** 소스별로 다양한 숫자 표현(문자열, object, 일부 numeric으로 로드된 값 포함)을 안정적으로 float로 변환하고, 센티널을 NaN 처리한다.

핵심 규칙:

- 센티널 결측:
    - `"9999"` 및 공란(빈 문자열) 등을 결측으로 지정
    - numeric dtype뿐 아니라 object/string에서도 `"9999"`를 검출 (예: `astype(str).strip() == "9999"`)
- Warnings 스키마 정합:
    - `SENTINEL_MISSING`에 `sentinel_value` 필드 추가
    - 집계형 `sentinel_count` 필드 추가
    - `original_value`는 집계형이면 null 유지

---

### Stage 3 — 결측/센티널 경고 집계(dedup/handle_missing_values)

**목표:** 결측 경고(value_missing)를 과도하게 중복 기록하지 않고, “센티널로 제거된 결측 vs 실제 결측”을 분리한다.

핵심:

- 집계 기반 dedup:
    - `remaining = max(missing_count_total - sentinel_count_total, 0)`
    - value_missing에는 **remaining만** 기록
    - details에 remaining과 sentinel_count를 함께 기록

---

### Stage 4 — 단위 정규화(apply_unit_canonicalization + unit policy)

**목표:** 최종 표준 데이터의 물리 단위를 canonical unit으로 통일한다.

Canonical:

- 길이/둘레/너비/두께/높이: meters (m)
- 무게: kg

주요 정책(실제 시스템에서 문제가 되었고 해결된 부분 포함):

1. **“m 기대 컬럼” 판별 로직 정상화**
    - `.endswith('_M')` 같은 단순 규칙은 `_M_REF` 등 변형 키를 누락시켜 단위 변환이 적용되지 않는 문제가 있었다.
    - 이를 **키 문자열에 `_M` 포함 여부 등** 더 보수적인 기준으로 확장하여, 특정 키 하드코딩 없이도 “m 기대 컬럼”이 일관되게 처리되도록 했다.
    - 목적: 하드코딩(if key == …)이 아니라 **키 규칙 기반 무결성** 유지
2. **7th 소스 source-level rule**
    - 7th의 길이 계열은 단위 메타/휴리스틱이 불안정하므로, “m 기대 컬럼”에 대해 source-level로 일관된 변환 규칙을 적용(예: mm→m).
    - 이는 특정 키만 처리하는 방식이 아니라 **소스 규칙 + 키 규칙**의 결합으로 적용된다.
3. **8th_direct/8th_3d unitless fallback**
    - 8th는 단위 메타가 없거나 undetermined인 경우가 많음.
    - source_key가 8th_direct/8th_3d이고, 표준키가 m 기대 컬럼이며 unit metadata가 없으면 **mm→m fallback(÷1000)** 적용.
    - 적용 시 `UNIT_DEFAULT_MM_NO_UNIT` 경고로 provenance 기록(non_null_before/after 포함)
4. non-finite(Inf/-Inf) 붕괴 방지
    - inf/-inf 감지 시 unit_conversion_failed로 집계하며, 최종 parquet write 전에 NaN normalize 수행
    - v3에서는 unit_conversion_failed 집계를 “inf/-inf only”로 정교화하여 순수 NaN과 분리

---

### Stage 5 — Output Serialization

- Parquet 저장: `df_combined.to_parquet(...)`
- pyarrow 변환 오류를 방지하기 위해 dtype 안정성(특히 object→float)을 강화
- 출력 스키마(대표):
    - 48 columns(표준키) + rows 12,365

---

## 5. 품질 센서(3대 품질 센서 + 추가 신호)

본 엔진은 “경고(warnings)”와 별도로, **조용한 오답을 탐지하기 위한 센서 기반 리포트(completeness_report)**를 제공한다.

### 5.1 completeness_report 산출 지표

- 소스별 non-null/결측률
- 분포 요약(예: p1~p99, p50)
- 범위/스케일 이상 탐지 결과

### 5.2 센서 종류(대표)

- `RANGE_SUSPECTED`: 물리적으로 비정상 범위 가능성(예: 둘레가 수 미터)
- `SCALE_SUSPECTED`: 소스간 p50 비교에서 10배 등 스케일 붕괴 의심
- `ALL_NULL_BY_SOURCE`: 특정 소스에서 해당 키가 전량 null
- `ALL_NULL_EXTRACTED`: 통합 컬럼 자체가 전량 null
- `MASSIVE_NULL_INTRODUCED`: 정규화/변환 단계에서 대량 NaN이 새로 유입된 패턴
- `NON_NUMERIC`: 비수치 컬럼(HUMAN_ID, SEX 등)을 all_null로 오탐하지 않도록 분리 라벨링

---

## 6. 경고(warnings) 시스템

### 6.1 포맷

- JSONL, 1 line = 1 warning entry
- 필드(핵심):
    - `reason`: 경고 유형
    - `standard_key`, `source`, `column` 등 식별자
    - 집계형 fields: `sentinel_count`, `invalid_values_count`, `non_null_before/after` 등

### 6.2 주요 reason 목록(대표)

- `column_not_found`: 계약은 있으나 소스에서 헤더가 탐지되지 않음(정책상 계약 교정 우선)
- `column_not_present`: 데이터 자체에 해당 항목이 없음(계약 오류가 아니라 coverage 이슈)
- `value_missing`: 실제 결측(센티널 제거분 제외)
- `SENTINEL_MISSING`: 센티널(9999 등) 제거 발생(센티널 값/카운트 기록)
- `unit_undetermined`: 단위 판정 실패
- `unit_conversion_applied`: 단위 변환 적용됨
- `unit_conversion_failed`: 변환 과정에서 inf/-inf 등 수치 붕괴 발생(정교화 후 “inf/-inf only”)
- `UNIT_DEFAULT_MM_NO_UNIT`: 8th unitless fallback 적용(provenance 기록)

---

## 7. 대표 실행 방법(Runbook)

### 7.1 기본 실행(Parquet + Warnings)

```bash
py -u pipelines/build_curated_v0.py ^
  --mapping data/column_map/sizekorea_v2.json ^
  --format parquet ^
  --output data/processed/curated_v0/curated_v0.parquet ^
  --warnings-output verification/runs/curated_v0/warnings_v3.jsonl

```

### 7.2 completeness report 포함

```bash
py -u pipelines/build_curated_v0.py ^
  --mapping data/column_map/sizekorea_v2.json ^
  --format parquet ^
  --output data/processed/curated_v0/curated_v0.parquet ^
  --warnings-output verification/runs/curated_v0/warnings_v3.jsonl ^
  --emit-completeness-report verification/runs/curated_v0/completeness_report.md

```

### 7.3 unit fail trace 포함(진단용)

```bash
py -u pipelines/build_curated_v0.py ^
  --mapping data/column_map/sizekorea_v2.json ^
  --format parquet ^
  --output data/processed/curated_v0/curated_v0.parquet ^
  --warnings-output verification/runs/curated_v0/warnings_v3.jsonl ^
  --emit-unit-fail-trace verification/runs/curated_v0/unit_fail_trace.md

```

---

## 8. 테스트 전략(결정성/회귀)

- Synthetic CSV 기반 헤더 탐지 테스트로 로컬 raw 파일 의존성 제거
- Anchor가 첫 컬럼이 아닌 경우도 탐지하는 회귀 테스트
- per-key header policy(HUMAN_ID/SEX/AGE secondary, others primary) 검증
- dtype/object 안정성 테스트(숫자 변환/pyarrow 직렬화 안정)
- unitless fallback(mm→m) 회귀 테스트(8th)
- 7th 스케일 붕괴(10배) 관련 회귀 테스트(키 하드코딩이 아닌 키 규칙 기반)

---

## 9. 알려진 제약 및 운영상의 주의

- `column_not_present`는 계약 오류가 아니라 “원천에 없는 측정항목”으로 취급(coverage backlog)
- 단위/스케일 이상은 자동 보정하지 않고, **센서/경고로 표면화**하는 것이 원칙(조용한 오답 방지)
- `verification/runs/`는 산출물 성격이므로 운영 정책에 따라 커밋/보관 전략을 별도 관리(레포 정책에 따름)