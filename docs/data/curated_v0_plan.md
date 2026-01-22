# Curated v0 Data Plan

SizeKorea 원천 데이터를 통합 정제하여 curated_v0 데이터셋을 생성하는 계획 문서.

## Scope

이 문서는 Data 정제 스펙만 다룹니다. 구현 코드는 별도 PR에서 처리합니다.

## Input Sources

다음 원천 파일을 입력으로 사용합니다:

- `data/raw/sizekorea_raw/7th_data.csv` (또는 `7th_data.xlsx`에서 변환된 CSV)
- `data/raw/sizekorea_raw/8th_data_direct.csv`
- `data/raw/sizekorea_raw/8th_data_3d.csv`

## Processing Steps

### Step (a): Column Extraction and Header Standardization

- 매핑 테이블: `data/column_map/sizekorea_v1.json` 사용
- 각 원천 파일에서 `sizekorea_v1.json`의 `sources.{source_key}.column`에 매핑된 컬럼만 추출
- 컬럼명을 `standard_key`로 변환
- 매핑되지 않은 컬럼은 제외 (또는 `ko__{original_name}__unmapped` 형식으로 보존, 정책 결정 필요)

**매핑 규칙:**
- Exact match만 사용 (fuzzy matching 금지)
- `present: false`인 키는 해당 소스에서 제외
- `column: null`인 경우 해당 소스에서 제외

### Step (b): Unit Sampling and Ingestion

- 단위 샘플링: 원천 데이터의 주요 측정 컬럼 값 범위를 샘플링하여 단위 확인
- Ingestion 적용: `docs/contract/UNIT_STANDARD.md` 참조
  - mm/cm/m → m 변환
  - 0.001m (1mm) 해상도로 양자화 (ROUND_HALF_UP)
  - Provenance 기록: source_unit, conversion_applied, canonical_unit="m", quantization="0.001m"
- `data/ingestion.py::canonicalize_units_to_m` 함수 사용 (이미 존재)

**단위 가정:**
- SizeKorea 원천 데이터는 mm 단위 (확인 필요)
- 변환: `meters = mm / 1000`

### Step (c): Outlier Removal

- 기존 규칙 유지: Z-Score ±3σ 이상치 제거 (기존 `SizeKorea_Final` 처리와 동일)
- 단위만 m로 변경 (기존 cm 기반 규칙을 m로 적용)
- 연령 범위: 20대~50대 (기존 규칙 유지)

### Step (d): Missing Value Handling

- 결측값 처리: NaN + warnings (예외 금지)
- Warnings 리스트에 다음 정보 기록:
  - source: 파일 소스 (7th, 8th_direct, 8th_3d)
  - file: 파일명
  - column: 표준 키
  - reason: 결측 사유 (예: "column_not_present", "value_missing", "unit_conversion_failed")

## Output

### Output Path

`data/processed/curated_v0/curated_v0.parquet` (또는 `curated_v0.csv`)

**형식 선택 기준:**
- Parquet: 권장 (타입 보존, 압축 효율)
- CSV: 대안 (호환성 우선 시)

### Output Schema

**컬럼:**
- Coverage v0의 45개 standard_key 컬럼
- 각 컬럼은 `docs/contract/standard_keys.md`의 표준 키 사용
- 단위: meters (m) 또는 kg (WEIGHT_KG의 경우)

**메타데이터:**
- Provenance 정보: 각 행의 source 파일, 변환 이력
- Warnings: 결측/변환 경고 목록

## Logging and Warning Format

### Warning Entry Format

```json
{
  "source": "7th|8th_direct|8th_3d",
  "file": "7th_data.csv",
  "column": "HEIGHT_M",
  "reason": "column_not_present|value_missing|unit_conversion_failed|outlier_removed",
  "row_index": 123,
  "original_value": "...",
  "details": "..."
}
```

### Logging Output

- 처리 통계: 총 행 수, 변환 성공/실패 수, 이상치 제거 수
- 결측률: 키별 결측률 통계
- 단위 변환 이력: source_unit → m 변환 통계

## Next PR Rules

**구현 PR 규칙:**

다음 PR에서 구현 코드를 추가할 때, 변경되는 경로가 다음을 포함하면:
- `pipelines/`
- `tools/`
- `tests/`
- `verification/`
- `core/`
- `.github/workflows/`

해당 구현 PR에 `docs/sync/CURRENT_STATE.md`를 facts-only로 업데이트해야 합니다.

**업데이트 내용 (사실만):**
- "curated_v0 데이터셋 생성 파이프라인 추가"
- "curated_v0 출력 경로: data/processed/curated_v0/"
- 기타 사실 기록 (판정/액션 지시 금지)

## References

- 매핑 테이블: `data/column_map/sizekorea_v1.json`
- 단위 정책: `docs/contract/UNIT_STANDARD.md`
- 표준 키: `docs/contract/standard_keys.md`
- SoT: `SYNC_HUB.md`
- Ingestion 함수: `data/ingestion.py::canonicalize_units_to_m`
