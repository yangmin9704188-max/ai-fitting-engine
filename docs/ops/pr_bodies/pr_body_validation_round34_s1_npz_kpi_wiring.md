# PR: Round34 - S1 NPZ 경로 연결 + KPI 집계 필드 보강

## 목적

Round33에서 proxy 5개 케이스는 stage=measure, reason=success로 성공했지만, postprocess KPI가 N/A이며 Visual provenance가 NPZ_PATH_NOT_FOUND로 스킵되었습니다.

이번 라운드는 **"NPZ 증거(verts 포함) 생성/연결 + KPI 집계 입력"**을 잠그는 라운드입니다.

## 변경 사항

### 1. `verification/runners/run_geo_v0_s1_facts.py`

#### NPZ 저장 위치 변경
- 기존: `artifacts/verts_proxy.npz`
- 변경: `artifacts/visual/verts_proxy.npz` (postprocess가 찾는 위치)

#### facts_summary.json에 KPI 필드 추가
- `n_samples`: total_cases와 동일 (summarize_facts_kpi.py가 기대하는 필드)
- `summary.valid_cases`: processed_cases와 동일 (KPI가 기대하는 형태)

#### facts_summary.json에 NPZ 경로 필드 보강
- `npz_path`: 상대 경로 (run_dir 기준)
- `dataset_path`: 상대 경로 (visual_provenance.py가 찾는 키)
- `npz_path_abs`: 절대 경로 (postprocess_round.py가 찾는 키)
- `npz_has_verts`: true/false
- `missing_key`: "" (verts 있음) 또는 "verts" (없음)

### 2. `docs/ops/INDEX.md`
- Round34 엔트리 추가

### 3. `reports/validation/INDEX.md`
- Round34 섹션 추가

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round34_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## DoD Self-check (facts-only)

### 1. KPI.md에서 Total/Valid가 N/A가 아닌지 확인
```bash
# KPI.md에서 확인
cat verification/runs/facts/geo_v0_s1/round34_*/KPI.md | grep -A 3 "Case Counts"
```

**예상 결과**: 
- Total cases: 200 (N/A 아님)
- Valid cases: 5 이상 (N/A 아님)

### 2. postprocess 출력에 NPZ_PATH_NOT_FOUND가 없는지 확인
```bash
# postprocess 로그 또는 LINEAGE.md에서 확인
grep -i "NPZ_PATH_NOT_FOUND" verification/runs/facts/geo_v0_s1/round34_*/LINEAGE.md || echo "NPZ_PATH_NOT_FOUND not found (expected)"
```

**예상 결과**: NPZ_PATH_NOT_FOUND가 없거나, 최소한 proxy 케이스는 해당되지 않음

### 3. LINEAGE에 npz_has_verts True / npz_path 존재 확인
```bash
# LINEAGE.md에서 확인
grep -A 5 "Visual Provenance" verification/runs/facts/geo_v0_s1/round34_*/LINEAGE.md
```

**예상 결과**:
- `npz_has_verts`: `true`
- `npz_path` 또는 관련 경로 존재

### 4. facts_summary.json 필드 확인
```bash
# facts_summary.json에서 확인
cat verification/runs/facts/geo_v0_s1/round34_*/facts_summary.json | python -m json.tool | grep -E "(n_samples|valid_cases|npz_path|npz_has_verts)"
```

**예상 결과**:
- `n_samples`: 200
- `summary.valid_cases`: 5 이상
- `npz_path`: "artifacts/visual/verts_proxy.npz" (또는 유사한 상대 경로)
- `npz_path_abs`: 절대 경로
- `npz_has_verts`: true

### 5. verts_proxy.npz 존재 및 내용 확인
```bash
# NPZ 파일 존재 확인
ls -la verification/runs/facts/geo_v0_s1/round34_*/artifacts/visual/verts_proxy.npz

# NPZ 내용 확인 (Python)
python -c "import numpy as np; data = np.load('verification/runs/facts/geo_v0_s1/round34_*/artifacts/visual/verts_proxy.npz', allow_pickle=True); print('Keys:', list(data.keys())); print('case_id:', data['case_id'] if 'case_id' in data else 'N/A'); print('meta_unit:', data['meta_unit'] if 'meta_unit' in data else 'N/A')"
```

**예상 결과**: 
- 파일 존재, 크기 > 0
- Keys: ['verts', 'case_id', 'meta_unit', 'schema_version']
- case_id: 5개 케이스 ID
- meta_unit: "m"

### 6. Processed >= 5 확인
```bash
# facts_summary.json에서 확인
cat verification/runs/facts/geo_v0_s1/round34_*/facts_summary.json | python -m json.tool | grep "processed_cases"
```

**예상 결과**: `"processed_cases": 5` 이상

## 준수 사항

- ✅ PASS/FAIL 판정 금지 (facts-only)
- ✅ Semantic 재해석/단위 재논의 금지
- ✅ 측정 알고리즘 정답 튜닝 금지
- ✅ 대규모 리팩터링/폴더 이동/삭제(git rm) 금지
- ✅ verification/runs/** 커밋 금지
- ✅ 라운드 완료는 postprocess 마감까지
