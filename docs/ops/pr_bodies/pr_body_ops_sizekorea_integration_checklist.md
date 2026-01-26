# PR Body: ops(docs): add sizekorea integration checklist

## 무엇을 만들었는지

- **문서 1개**: `docs/ops/sizekorea_integration_checklist.md`
  - SizeKorea 통합 상태를 한눈에 보는 체크리스트 문서
  - SYNC_HUB.md + CURRENT_STATE.md를 1차 근거로 삼아 레포 스캔 결과 정리
  - Integration Map (Area/Layer/Path/Role/Inputs/Outputs/Notes 표)
  - Evidence Anchors (CURRENT_STATE/SYNC_HUB 링크 목록)
  - Quick Checks (human checklist 12개 항목)

## 변경 파일

1. `docs/ops/sizekorea_integration_checklist.md` (신규)
2. `docs/ops/pr_bodies/pr_body_ops_sizekorea_integration_checklist.md` (신규, 이 파일)

## 스모크

### git grep -n "sizekorea"
```
SYNC_HUB.md:37:- Contract(sizekorea_v2.json) exact-match 매핑 정리로 column_not_found=0 달성
core/measurements/metadata_v0.py:112:        "source": "sizekorea",
data/normalize_sizekorea_headers.py:129:        default="data/column_map/sizekorea_v0.json",
pipelines/build_curated_v0.py:6:1. Extracts columns based on sizekorea column mapping (v2 by default)
pipelines/build_curated_v0.py:2474:        default='data/column_map/sizekorea_v2.json',
tests/test_build_curated_v0.py:55:    mapping_path = Path(__file__).parent.parent / "data" / "column_map" / "sizekorea_v2.json"
tools/observe_sizekorea_columns.py:125:            "data/raw/sizekorea_raw/7th_data.csv",
... (총 118개 매칭)
```

### git grep -n "curated_v0"
```
SYNC_HUB.md:33:Current Milestone: curated_v0 Data Contract & Pipeline Stabilization v3 (Freeze Candidate)
SYNC_HUB.md:36:- SizeKorea 7th/8th(Direct/3D) 3-source 통합 파이프라인 구축: curated_v0.parquet 산출
data/README.md:46:- 정규화 워크플로우: `raw` (한국어 헤더) → `raw_normalized_v0` (영문 헤더) → `curated_v0` (통합 정제 DB)
pipelines/build_curated_v0.py:3:Build curated_v0 dataset from SizeKorea raw data.
pipelines/build_curated_v0.py:52:- curated_v0 데이터셋 생성 파이프라인 추가 (pipelines/build_curated_v0.py)
... (총 526개 매칭)
```

### git grep -n "normalize_sizekorea_headers"
```
docs/sync/CURRENT_STATE.md:45:- SizeKorea 헤더 정규화 스크립트 추가 (data/normalize_sizekorea_headers.py)
data/README.md:88:- 정규화 스크립트: data/normalize_sizekorea_headers.py
```

### git grep -n "build_curated_v0"
```
docs/sync/CURRENT_STATE.md:52:- curated_v0 데이터셋 생성 파이프라인 추가 (pipelines/build_curated_v0.py)
pipelines/build_curated_v0.py:3:Build curated_v0 dataset from SizeKorea raw data.
tests/test_build_curated_v0.py:17:from pipelines.build_curated_v0 import (
```

### git diff 확인
```
(변경 파일 2개만 포함: 체크리스트 + PR 바디)
```

## DoD 체크리스트

- [x] 문서 작성 완료 (facts-only, 판정 금지)
- [x] Integration Map 표 작성 (Area/Layer/Path/Role/Inputs/Outputs/Notes)
- [x] Evidence Anchors 섹션 작성 (CURRENT_STATE/SYNC_HUB 링크 목록)
- [x] Quick Checks 섹션 작성 (질문형/확인형, 판정 금지)
- [x] PR 바디 작성 완료
- [x] 스모크 실행 (git grep 결과 확인)
- [x] git diff로 allowed scope 밖 파일 변경 없음 확인
- [ ] CI green 확인 후 머지 (CI red면 머지 금지)
