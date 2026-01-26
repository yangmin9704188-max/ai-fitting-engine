# SizeKorea Integration Checklist

## 1. Scope (facts-only)

**기준 문서**: `SYNC_HUB.md`, `docs/sync/CURRENT_STATE.md`

**생성일**: 2026-01-26

**커밋 해시**: 03fb0318be97fbdbcbfe8ace17a71710c73b49d4

**주의**: 이 문서는 위치/연결을 요약하며, 의미론적 정의는 포함하지 않음

---

## 2. Integration Map (핵심 표)

| Area | Layer | Path | Role | Inputs | Outputs | Notes |
|------|-------|------|------|--------|---------|-------|
| raw ingest | Ops-crosscut | `data/raw/sizekorea_raw/7th_data.csv` | SizeKorea 7th 원천 데이터 (CSV, 한국어 헤더) | - | - | XLSX 우선, CSV는 fallback |
| raw ingest | Ops-crosscut | `data/raw/sizekorea_raw/8th_data_direct.csv` | SizeKorea 8th Direct 원천 데이터 (CSV, 한국어 헤더) | - | - | - |
| raw ingest | Ops-crosscut | `data/raw/sizekorea_raw/8th_data_3d.csv` | SizeKorea 8th 3D 원천 데이터 (CSV, 한국어 헤더) | - | - | - |
| header normalize | Contract | `data/normalize_sizekorea_headers.py` | 한국어 헤더 → 영문 표준 키 변환 스크립트 | `data/raw/sizekorea_raw/*.csv`, `data/column_map/sizekorea_v0.json` | `data/processed/raw_normalized_v0/*.csv` | 예외 금지, warnings 기록, 산출물 커밋 금지 |
| mapping | Contract | `data/column_map/sizekorea_v0.json` | SizeKorea v0 매핑 테이블 (한국어 → 영문 최소 세트) | - | - | unmapped 컬럼은 ko__ 접두사 + __unmapped 접미사로 보존 |
| mapping | Contract | `data/column_map/sizekorea_v2.json` | SizeKorea v2 매핑 테이블 (exact-match, 45 keys) | - | - | primary/secondary 헤더 exact-match, column_not_found=0 달성 |
| curated build | Contract | `pipelines/build_curated_v0.py` | curated_v0 데이터셋 생성 파이프라인 | `data/raw/sizekorea_raw/*.csv`, `data/column_map/sizekorea_v2.json` | `data/processed/curated_v0/curated_v0.parquet` | 단위 canonicalization (mm/cm/m → m), warnings 기록, 예외 금지 |
| curated build | Contract | `data/processed/raw_normalized_v0/` | 영문 헤더 정규화 중간 단계 데이터 저장 경로 | `data/normalize_sizekorea_headers.py` 출력 | `pipelines/build_curated_v0.py` 입력 (간접) | - |
| curated build | Contract | `data/processed/curated_v0/curated_v0.parquet` | curated_v0 최종 산출물 (7th/8th 통합, meters 단위) | `pipelines/build_curated_v0.py` | - | 산출물 커밋 금지 (경로/명령만 기록) |
| validation registry | Validation | `docs/data/curated_v0_warnings_schema.md` | curated_v0 warnings 스키마 문서 (JSONL 형식, reason 코드 정의) | - | - | - |
| validation registry | Validation | `verification/runs/curated_v0/` | curated_v0 실행 요약 기록 경로 | `pipelines/build_curated_v0.py` 실행 결과 | - | 산출물 커밋 금지 |
| docs | Ops-crosscut | `docs/data/curated_v0_plan.md` | curated_v0 데이터셋 생성 계획 문서 | - | - | - |
| docs | Semantic | `docs/semantic/evidence/sizekorea_measurement_methods_v0.md` | SizeKorea 측정 방법 Evidence 문서 | - | - | - |
| docs | Semantic | `docs/semantic/measurement_semantics_v0.md` | 측정 항목 Semantic 정의 (SizeKorea Evidence 참조) | - | - | - |
| tools | Ops-crosscut | `tools/observe_sizekorea_columns.py` | SizeKorea raw 데이터 컬럼명 관측 스크립트 | `data/raw/sizekorea_raw/*.csv` | `verification/runs/column_observation/` | 산출물 커밋 금지 |
| tools | Ops-crosscut | `tools/build_glossary_and_mapping.py` | SizeKorea glossary 및 v1 매핑 테이블 생성 도구 | - | `data/column_map/sizekorea_v1.json` | - |
| tools | Ops-crosscut | `tools/update_contract_from_table.py` | sizekorea_v2.json contract 업데이트 도구 (exact match only) | - | `data/column_map/sizekorea_v2.json` | - |
| tests | Validation | `tests/test_build_curated_v0.py` | curated_v0 파이프라인 테스트 (dry-run, 매핑/헤더/경고 포맷 검증) | - | - | - |
| metadata | Contract | `core/measurements/metadata_v0.py` | 측정 메타데이터 (source="sizekorea", evidence_ref 경로) | - | - | - |

---

## 3. Evidence Anchors (facts-only 링크 목록)

### CURRENT_STATE에 명시된 sizekorea 관련 파일/디렉토리

- `tools/observe_sizekorea_columns.py`: raw CSV 파일별 row 수, 컬럼 목록, 공통 컬럼 교집합/차집합 요약 관측
- `data/column_map/sizekorea_v0.json`: 한국어 컬럼명 → 영문 표준 키 매핑 테이블 v0 (최소 세트)
- `data/normalize_sizekorea_headers.py`: raw CSV (한국어 헤더) → raw_normalized_v0 (영문 헤더) 변환
- `data/processed/raw_normalized_v0/`: 영문 헤더 정규화 중간 단계 데이터 저장 경로
- `pipelines/build_curated_v0.py`: sizekorea_v2 매핑 기반 컬럼 추출, 단위 canonicalization, warnings 기록
- `data/column_map/sizekorea_v2.json`: exact-match 매핑 (primary/secondary 헤더, column_not_found=0)
- `data/processed/curated_v0/curated_v0.parquet`: curated_v0 최종 산출물 (7th/8th 통합, meters 단위)
- `docs/data/curated_v0_warnings_schema.md`: warnings 스키마 문서
- `tests/test_build_curated_v0.py`: curated_v0 파이프라인 테스트
- `verification/runs/curated_v0/`: 실행 요약 기록 경로

### SYNC_HUB에 언급된 sizekorea/curated_v0 관련 요약 포인트

1. **SizeKorea 7th/8th(Direct/3D) 3-source 통합 파이프라인 구축**: curated_v0.parquet 산출
2. **Contract(sizekorea_v2.json) exact-match 매핑 정리**: column_not_found=0 달성
3. **Sentinel 정책 정합성 확립**: 8th_direct의 9999 dtype 무관 필터링 + SENTINEL_MISSING 스키마 정합
4. **단위/스케일 조용한 오답 리스크 표면화**: completeness_report 기반 센서 (ALL_NULL_BY_SOURCE, ALL_NULL_EXTRACTED, MASSIVE_NULL_INTRODUCED, RANGE_SUSPECTED)
5. **시스템 무결성 원칙 확정**: 특정 키 하드코딩 금지, "m 기대 컬럼 판별" 규칙을 패턴/토큰 기반으로 정본화
6. **Unit canonicalization**: meters(m) 정본화, "m 기대 컬럼 판별"은 시스템 규칙(패턴/토큰 기반)으로만 결정
7. **Current Milestone**: curated_v0 Data Contract & Pipeline Stabilization v3 (Freeze Candidate)
8. **Current Track**: Track A (Data): Contract + curated_v0 Stabilization (Freeze -> Tag)

---

## 4. Quick Checks (human checklist)

- [ ] `data/processed/curated_v0/curated_v0.parquet` 생성 경로 확인 (pipelines/build_curated_v0.py 실행 후)
- [ ] `data/column_map/sizekorea_v2.json` 버전(v2) 사용 여부 확인 (pipelines/build_curated_v0.py 기본값)
- [ ] 단위 canonicalization(m) 적용 위치 확인 (pipelines/build_curated_v0.py의 apply_unit_canonicalization 함수)
- [ ] 로컬 산출물 커밋 금지 규칙 재확인 (data/processed/**, verification/runs/** 커밋 금지)
- [ ] `data/raw/sizekorea_raw/` 원천 파일 존재 여부 확인 (7th_data.csv, 8th_data_direct.csv, 8th_data_3d.csv)
- [ ] `data/normalize_sizekorea_headers.py` 실행 시 warnings 기록 여부 확인 (예외 금지 정책)
- [ ] `pipelines/build_curated_v0.py` 실행 시 warnings 스키마 정합성 확인 (docs/data/curated_v0_warnings_schema.md 참조)
- [ ] `tests/test_build_curated_v0.py` 테스트 통과 여부 확인 (dry-run 모드)
- [ ] `data/processed/raw_normalized_v0/` 중간 단계 데이터 생성 여부 확인 (normalize_sizekorea_headers.py 실행 후)
- [ ] `verification/runs/curated_v0/` 실행 요약 기록 경로 확인 (산출물 커밋 금지)
- [ ] `docs/semantic/evidence/sizekorea_measurement_methods_v0.md` Evidence 문서 참조 경로 확인 (metadata_v0.py에서 사용)
- [ ] `core/measurements/metadata_v0.py`에서 source="sizekorea" 설정 확인
