# PR: Round38 - S1 Proxy 다양화 (20M/30M/40M)

## 목적

data/raw/scans_3d에 있는 30M/40M OBJ+XLSX를 레포 표준 구조로 정리하고, S1 proxy 5슬롯을 3개 OBJ(20M, 30M, 40M)로 2-2-1 분산 매핑하여 입력 다양성을 검증합니다.

**정확도 튜닝 금지**: 이번 라운드는 입력 다양성 검증이 목적이며, 측정 로직 정답 맞추기 변경 금지.

## 변경 사항

### 1. OBJ 파일 복사/리네임

- **30M OBJ**: `data/raw/scans_3d/ORIGINAL_6th_30M.obj` → `verification/datasets/golden/s1_mesh_v0/meshes/6th_30M.obj`
  - 파일 크기: 23,042,786 bytes
- **40M OBJ**: `data/raw/scans_3d/ORIGINAL_6th_40M.obj` → `verification/datasets/golden/s1_mesh_v0/meshes/6th_40M.obj`
  - 파일 크기: 15,829,583 bytes

### 2. XLSX → CSV 변환 (메타데이터 정규화)

**변환 스크립트**: `verification/tools/convert_scan_xlsx_to_csv.py`

**30M 변환**:
```bash
python verification/tools/convert_scan_xlsx_to_csv.py \
  --input_xlsx "data/raw/scans_3d/6th_30M_data.xlsx" \
  --out_dir "verification/datasets/golden/s1_mesh_v0/metadata" \
  --source_id "scan_6th_30M" \
  --raw_unit "mm" \
  --meta_unit "m" \
  --precision "0.001" \
  --major_names "키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레"
```

**40M 변환**:
```bash
python verification/tools/convert_scan_xlsx_to_csv.py \
  --input_xlsx "data/raw/scans_3d/6th_40M_data.xlsx" \
  --out_dir "verification/datasets/golden/s1_mesh_v0/metadata" \
  --source_id "scan_6th_40M" \
  --raw_unit "mm" \
  --meta_unit "m" \
  --precision "0.001" \
  --major_names "키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레"
```

**생성된 CSV 파일**:
- `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_30M_measurements_m.csv`
- `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_30M_major_measurements_m.csv`
- `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_40M_measurements_m.csv`
- `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_40M_major_measurements_m.csv`

### 3. S1 manifest proxy 5슬롯을 3개 OBJ로 2-2-1 분산 매핑

**파일**: `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json`

**매핑 규칙 (2-2-1)**:
- **2개 케이스 → 6th_20M.obj**:
  - `311610164126` (measurements_csv 포함)
  - `20_F_1049`
- **2개 케이스 → 6th_30M.obj**:
  - `121607160426` (measurements_csv 포함)
  - `21_F_4430`
- **1개 케이스 → 6th_40M.obj**:
  - `511609194879` (measurements_csv 포함)

**유지 사항**:
- `note`: "proxy mesh for S1 pipeline validation; not 1:1 identity with curated_v0 case"
- `meta_unit`: "m"
- 다른 195케이스는 변경하지 않음

## 재현 커맨드

### 1. OBJ 파일 복사/리네임
```bash
mkdir -p verification/datasets/golden/s1_mesh_v0/meshes
cp -f data/raw/scans_3d/ORIGINAL_6th_30M.obj verification/datasets/golden/s1_mesh_v0/meshes/6th_30M.obj
cp -f data/raw/scans_3d/ORIGINAL_6th_40M.obj verification/datasets/golden/s1_mesh_v0/meshes/6th_40M.obj
```

### 2. XLSX → CSV 변환
```bash
python verification/tools/convert_scan_xlsx_to_csv.py \
  --input_xlsx "data/raw/scans_3d/6th_30M_data.xlsx" \
  --out_dir "verification/datasets/golden/s1_mesh_v0/metadata" \
  --source_id "scan_6th_30M" \
  --raw_unit "mm" \
  --meta_unit "m" \
  --precision "0.001" \
  --major_names "키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레"

python verification/tools/convert_scan_xlsx_to_csv.py \
  --input_xlsx "data/raw/scans_3d/6th_40M_data.xlsx" \
  --out_dir "verification/datasets/golden/s1_mesh_v0/metadata" \
  --source_id "scan_6th_40M" \
  --raw_unit "mm" \
  --meta_unit "m" \
  --precision "0.001" \
  --major_names "키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레"
```

### 3. Round38 실행 및 postprocess 마감
```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round38_$(date +%Y%m%d_%H%M%S)" && \
python verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
python tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## DoD Self-check (facts-only)

### 1. OBJ 파일 존재 확인
```bash
ls -lh verification/datasets/golden/s1_mesh_v0/meshes/6th_30M.obj
ls -lh verification/datasets/golden/s1_mesh_v0/meshes/6th_40M.obj
```

**예상 결과**: 
- 6th_30M.obj: ~23MB
- 6th_40M.obj: ~16MB

### 2. CSV 파일 존재 확인
```bash
ls -lh verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_30M_*.csv
ls -lh verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_40M_*.csv
```

**예상 결과**: 
- scan_6th_30M_measurements_m.csv 존재
- scan_6th_30M_major_measurements_m.csv 존재
- scan_6th_40M_measurements_m.csv 존재
- scan_6th_40M_major_measurements_m.csv 존재

### 3. S1 manifest 매핑 확인
```bash
cat verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json | python -m json.tool | grep -A 5 -E "(311610164126|20_F_1049|121607160426|21_F_4430|511609194879)"
```

**예상 결과**:
- 311610164126, 20_F_1049 → 6th_20M.obj
- 121607160426, 21_F_4430 → 6th_30M.obj
- 511609194879 → 6th_40M.obj

### 4. Round38 실행 결과 확인

#### Processed/Skipped 확인
```bash
cat verification/runs/facts/geo_v0_s1/round38_*/facts_summary.json | python -c "import json, sys; data = json.load(sys.stdin); print(f\"Processed: {data.get('processed_cases', 0)}\"); print(f\"Skipped: {data.get('skipped_cases', 0)}\")"
```

**예상 결과**: Processed = 5

#### skip_reasons.jsonl 라인 수 확인
```bash
wc -l verification/runs/facts/geo_v0_s1/round38_*/artifacts/skip_reasons.jsonl
```

**예상 결과**: 200 lines

#### KPI.md에서 값 다양성 확인
```bash
# HEIGHT_M, BUST_CIRC_M, WAIST_CIRC_M, HIP_CIRC_M 값 확인
cat verification/runs/facts/geo_v0_s1/round38_*/KPI.md | grep -E "(HEIGHT_M|BUST_CIRC_M|WAIST_CIRC_M|HIP_CIRC_M)" | grep -E "(p50|median|mean)"
```

**예상 결과**: 
- "완전 동일 5개 반복"에서 벗어났는지 확인 (최소 1개 키라도 다양성 확인)
- Round37 대비 값 분산이 증가했는지 확인

#### PERIMETER_LARGE 경고 확인
```bash
cat verification/runs/facts/geo_v0_s1/round38_*/KPI.md | grep -i "PERIMETER_LARGE"
cat verification/runs/facts/geo_v0_s1/round38_*/facts_summary.json | python -c "import json, sys; data = json.load(sys.stdin); summary = data.get('summary', {}); circ_keys = ['WAIST_CIRC_M', 'BUST_CIRC_M', 'HIP_CIRC_M']; [print(f\"{k}: {summary.get(k, {}).get('warnings', {})}\") for k in circ_keys]"
```

**예상 결과**: 
- PERIMETER_LARGE 경고가 없거나, 있으면 경고 라인만 기록

### 5. postprocess 산출물 생성 확인
```bash
ls -la verification/runs/facts/geo_v0_s1/round38_*/KPI.md
ls -la verification/runs/facts/geo_v0_s1/round38_*/KPI_DIFF.md
ls -la verification/runs/facts/geo_v0_s1/round38_*/LINEAGE.md
```

**예상 결과**: 모든 파일 존재

## 준수 사항

- ✅ PASS/FAIL 판정 금지 (facts-only)
- ✅ Semantic 재해석/단위 재논의 금지 (단, raw_unit=mm → meta_unit=m 변환은 도구 규격대로 수행)
- ✅ 대규모 리팩터링/폴더 이동/삭제(git rm) 금지
- ✅ 측정 로직 정답 맞추기 변경 금지 (입력 다양성 검증만)
- ✅ verification/runs/** 커밋 금지
- ✅ 라운드 완료는 postprocess_round.py 마감까지
