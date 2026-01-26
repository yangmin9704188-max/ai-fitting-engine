# Validation Reports Index

Round-specific facts reports (fixed filenames). **Baseline**: Round 17.

| Round | Filename |
|-------|----------|
| 13 | `geo_v0_facts_round13_fastmode_normal1_runner.md` |
| 15 | `geo_v0_facts_round15_bust_verts_aligned_normal1.md` |
| 16 | `geo_v0_facts_round16_waist_hip_verts_aligned_normal1.md` |
| **17** | **`geo_v0_facts_round17_valid10_expanded.md`** (현재 기준선) |
| 20 | `curated_v0_facts_round1.md` |
| 21 | `curated_v0_facts_round21.md` (Gate: [docs/policies/validation/curated_v0_realdata_gate_v0.md](../policies/validation/curated_v0_realdata_gate_v0.md)) |
| 22 | `curated_v0_facts_round22.md` (Freeze: [docs/verification/golden_real_data_freeze_v0.1.md](../../verification/golden_real_data_freeze_v0.1.md)) |
| 23 | `geo_v0_s1_facts_round23.md` (S1 manifest: [verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json](../../../verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json)) |

See `docs/verification/golden_s0_freeze_v0.md` for S0 reproduce commands and freeze rule.

## Round 20 (Curated v0 Real Data Golden)

- **NPZ**: `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz`
- **Report**: `reports/validation/curated_v0_facts_round1.md`
- **Facts summary**: `verification/runs/facts/curated_v0/round20_<timestamp>/facts_summary.json`

### Run commands

```bash
# 1) Create real-data golden NPZ (smoke: --n_cases 30)
py verification/datasets/golden/core_measurements_v0/create_real_data_golden.py \
  --n_cases 200 \
  --out_npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz

# 2) Facts runner (out_dir default: round20_<timestamp>)
py verification/runners/run_curated_v0_facts_round1.py \
  --npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz \
  --out_dir verification/runs/facts/curated_v0/round20_$(date +%Y%m%d_%H%M%S)
```

## Round 21 (Curated v0 Real Data Golden - Gate v0)

- **NPZ**: `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz` (Round20과 동일)
- **Report**: `reports/validation/curated_v0_facts_round21.md`
- **Gate Document**: [`docs/policies/validation/curated_v0_realdata_gate_v0.md`](../policies/validation/curated_v0_realdata_gate_v0.md)
- **Facts summary**: `verification/runs/facts/curated_v0/round21_<timestamp>/facts_summary.json`

### Run commands

```bash
RUN_DIR="verification/runs/facts/curated_v0/round21_$(date +%Y%m%d_%H%M%S)" \
make curated_v0_round \
RUN_DIR="$RUN_DIR"
```

## Round 22 (Curated v0 Real Data Golden - Freeze v0.1)

- **NPZ**: `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz` (manifest 기반 재생성)
- **Manifest**: `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.case_ids.json` (SSoT)
- **Report**: `reports/validation/curated_v0_facts_round22.md`
- **Freeze Document**: [`docs/verification/golden_real_data_freeze_v0.1.md`](../../verification/golden_real_data_freeze_v0.1.md)
- **Facts summary**: `verification/runs/facts/curated_v0/round22_<timestamp>/facts_summary.json`

### Run commands

```bash
# 1) Recreate NPZ from manifest (SSoT mode - bypasses sampling)
py verification/datasets/golden/core_measurements_v0/create_real_data_golden.py \
  --case_ids_json verification/datasets/golden/core_measurements_v0/golden_real_data_v0.case_ids.json \
  --out_npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz

# 2) Facts runner
RUN_DIR="verification/runs/facts/curated_v0/round22_$(date +%Y%m%d_%H%M%S)" \
make curated_v0_round \
RUN_DIR="$RUN_DIR"
```

**주의**: Round22는 동일 케이스 재실행이므로 원칙상 KPI_DIFF는 0에 수렴하는 것이 정상입니다.
0이 아니면 "재생성 로직의 결정성(Determinism) 문제 가능성"이라는 강력 경고 신호입니다.

## Round 23 (Geo v0 S1 Facts - Mesh/Verts Input Contract)

- **Manifest**: `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json` (S1 입력 계약, meta_unit="m")
- **Report**: `reports/validation/geo_v0_s1_facts_round23.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round23_<timestamp>/facts_summary.json`

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round23_$(date +%Y%m%d_%H%M%S)" \
make geo_v0_s1_round \
RUN_DIR="$RUN_DIR"
```

**주의**: 
- S1 manifest는 입력 계약이며 meta_unit="m" 포함
- skip 사유는 Type A (manifest_path_is_null) / Type B (manifest_path_set_but_file_missing)로 구분 기록
- 알고리즘 변경이 아니라 "연결/입력/프로비넌스"만 수행

## Round 24 (Geo v0 S1 Facts - 20F OBJ/XLSX Proxy)

- **Manifest**: `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json` (proxy mesh 연결)
- **Mesh**: `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj` (6차_20대_여성.obj)
- **Measurements**: `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20F_measurements_m.csv` (XLSX→CSV, mm→m)
- **Report**: `reports/validation/geo_v0_s1_facts_round24.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round24_<timestamp>/facts_summary.json`

### Run commands

```bash
# 1) Convert XLSX to CSV (mm -> m)
python verification/tools/convert_scan_xlsx_to_csv.py \
  --input_xlsx "20F_data.xlsx" \
  --out_dir "verification/datasets/golden/s1_mesh_v0/metadata" \
  --source_id "scan_6th_20F" \
  --raw_unit "mm" \
  --meta_unit "m" \
  --precision "0.001" \
  --major_names "키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레" \
  && \
# 2) Copy OBJ file (if not already copied)
# cp data/raw/scans_3d/6차_20대_여성.obj verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj \
# 3) Facts runner
RUN_DIR="verification/runs/facts/geo_v0_s1/round24_$(date +%Y%m%d_%H%M%S)" \
make geo_v0_s1_round \
RUN_DIR="$RUN_DIR"
```

**주의**: 
- 단위 변환 계약: raw mm -> meta_unit m, precision 0.001m
- proxy mesh (정합 주장 금지): curated_v0 case_id와 1:1 정합 주장 금지, note로 명시
- major 항목: 키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레

## Round 25 (Geo v0 S1 Facts - 20F OBJ Processing)

- **Manifest**: `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json` (20F OBJ 실존 경로 연결)
- **Mesh**: `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj` (실존 파일, 903222 bytes)
- **Measurements**: `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20F_measurements_m.csv`
- **Report**: `reports/validation/geo_v0_s1_facts_round25.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round25_<timestamp>/facts_summary.json`

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round25_$(date +%Y%m%d_%H%M%S)" \
make geo_v0_s1_round \
RUN_DIR="$RUN_DIR"
```

**주의**: 
- Round24에서 200/200 skipped(verts 없음) 관측 → Round25는 OBJ 직접 로드로 processed>0 목표
- 입력 로딩 방식: A안 (OBJ 직접 로드, trimesh 또는 fallback parser 사용)
- SKIPPED 사유: Type A (null), Type B (file missing), Type C (parse error) 구분

## Round 26 (Geo v0 S1 Facts - Baseline Lock & Proxy Coverage)

- **Baseline**: `verification/runs/facts/geo_v0_s1/round25_20260127_003039` (geo_v0_s1 lane 초기 기준선)
- **Manifest**: `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json` (proxy mesh 5개 이상 연결)
- **Mesh**: `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj` (동일 OBJ를 여러 case_id에 연결)
- **Report**: `reports/validation/geo_v0_s1_facts_round26.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round26_<timestamp>/facts_summary.json`

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round26_$(date +%Y%m%d_%H%M%S)" \
make geo_v0_s1_round \
RUN_DIR="$RUN_DIR"
```

**주의**: 
- Round25에서 baseline/prev가 UNSET으로 떨어짐 → Round26은 baseline/prev 비교 정합성 잠금
- proxy 처리 커버리지 확대: 1→N (최소 5개, 동일 OBJ 재사용)
- create_weight_metadata() 경고 축소: A안 (weight 값이 없으면 metadata 생성 스킵 + reason 기록)
- 목표: processed >= 5 확보 (정확도 검증 금지)

## Round 28 (Geo v0 S1 Facts - 20M Proxy Switch)

- **Baseline**: `verification/runs/facts/geo_v0_s1/round25_20260127_003039` (geo_v0_s1 lane baseline, alias: geo-v0-s1-proxy-v0.1)
- **Manifest**: `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json` (proxy mesh 5개를 20M으로 전환)
- **Mesh**: `verification/datasets/golden/s1_mesh_v0/meshes/6th_20M.obj` (20F 오염 확인 → 20M으로 전환)
- **Report**: `reports/validation/geo_v0_s1_facts_round28.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round28_<timestamp>/facts_summary.json`

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round28_$(date +%Y%m%d_%H%M%S)" \
make geo_v0_s1_round \
RUN_DIR="$RUN_DIR"
```

**주의**: 
- 20F OBJ 오염 확인 → S1 proxy 입력을 20M으로 전환
- 목적: 정확도가 아니라 S1 입력 계약 + processed 확보 + 운영 마감(postprocess)
- proxy 슬롯 5개: 311610164126, 20_F_1049, 121607160426, 21_F_4430, 511609194879
- baseline alias 등록: geo-v0-s1-proxy-v0.1 (Git tag 아님, lane 내부 alias)

## Round 28 (Geo v0 S1 Facts - 20M XLSX→CSV Metadata Conversion)

- **입력 XLSX**: `data/raw/scans_3d/ORIGINAL_6th_20M_data.xlsx` (레포 루트 기준 상대경로)
- **변환 스크립트**: `verification/tools/convert_scan_xlsx_to_csv.py`
- **출력 CSV**: 
  - `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20M_measurements_m.csv` (전체)
  - `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20M_major_measurements_m.csv` (major subset)
- **Manifest**: `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json` (measurements_csv 경로 업데이트)
- **Report**: `reports/validation/geo_v0_s1_facts_round28.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round28_<timestamp>/facts_summary.json`

### 변환 커맨드

```bash
py verification/tools/convert_scan_xlsx_to_csv.py \
  --input_xlsx "data/raw/scans_3d/ORIGINAL_6th_20M_data.xlsx" \
  --out_dir "verification/datasets/golden/s1_mesh_v0/metadata" \
  --source_id "scan_6th_20M" \
  --raw_unit "mm" \
  --meta_unit "m" \
  --precision "0.001" \
  --major_names "키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레"
```

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round28_$(date +%Y%m%d_%H%M%S)" \
make geo_v0_s1_round \
RUN_DIR="$RUN_DIR"
```

**주의**: 
- 단위 변환: raw_unit="mm" → meta_unit="m", precision=0.001m
- S1 입력 계약 강화: 20M OBJ + 20M CSV 일치
- 원본 XLSX는 data/raw 아래에 있으므로 git 추적 대상 아님 (.gitignore에 *.xlsx 포함)

## Round 29 (Geo v0 S1 Facts - Per-Case Skip Reasons Logging)

- **Runner**: `verification/runners/run_geo_v0_s1_facts.py` (케이스별 스킵 사유 로깅 추가)
- **Skip Reasons Log**: `verification/runs/facts/geo_v0_s1/round29_<timestamp>/artifacts/skip_reasons.jsonl` (SSoT)
- **Report**: `reports/validation/geo_v0_s1_facts_round29.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round29_<timestamp>/facts_summary.json`

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round29_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

**주의**: 
- Round28에서 processed=0이고 artifacts/visual/SKIPPED.txt는 헤더 4줄만 존재하여 케이스별 원인 추적 불가
- Round29는 케이스별 스킵 사유를 skip_reasons.jsonl에 기록 (SSoT)
- proxy 슬롯 5개는 반드시 attempted_load=True까지 진입하여 로드 시도
- artifacts/visual/SKIPPED.txt는 헤더만 유지, 케이스별 사유는 skip_reasons.jsonl에 기록 (overwrite 방지)

## Round 30 (Geo v0 S1 Facts - Load Failed Diagnostics)

- **Runner**: `verification/runners/run_geo_v0_s1_facts.py` (load_failed 진단 필드 추가)
- **Skip Reasons Log**: `verification/runs/facts/geo_v0_s1/round30_<timestamp>/artifacts/skip_reasons.jsonl` (mesh_path_resolved, mesh_exists, exception_1line 추가)
- **Report**: `reports/validation/geo_v0_s1_facts_round30.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round30_<timestamp>/facts_summary.json`

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round30_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

**주의**: 
- Round29 로깅: 200 중 195는 manifest_path_is_null(정상), proxy 5개는 stage=load_mesh, reason=load_failed로 전부 실패
- Round30은 load_failed의 "구체 예외/경로 resolve"를 facts로 남김
- 상대경로 mesh_path는 Path.cwd() 기준으로 resolve
- 목표: processed>=1 복구

## Round 31 (Geo v0 S1 Facts - Loader Fallback & Exceptions)

- **Runner**: `verification/runners/run_geo_v0_s1_facts.py` (2단 OBJ 로더: trimesh 옵션 + pure Python parser 필수)
- **Skip Reasons Log**: `verification/runs/facts/geo_v0_s1/round31_<timestamp>/artifacts/skip_reasons.jsonl` (loader_name, loaded_verts, loaded_faces 추가)
- **Report**: `reports/validation/geo_v0_s1_facts_round31.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round31_<timestamp>/facts_summary.json`

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round31_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

**주의**: 
- Round30 관측: proxy 5개는 mesh_exists=true인데 load_mesh에서 전부 load_failed
- Round31은 예외 1줄을 facts로 남기면서도 processed=5까지 바로 찍을 수 있도록 로더를 이중화
- Loader A: trimesh (옵션, MTL/재질 의존 최소화)
- Loader B: pure Python OBJ parser (필수, 'v '와 'f ' 라인만 파싱)
- 목표: processed>=5 복구

## Round 33 (Geo v0 S1 Facts - OBJ Loader Fallback + Verts NPZ Evidence)

- **Runner**: `verification/runners/run_geo_v0_s1_facts.py` (OBJ 로더 fallback 개선 + verts NPZ 생성)
- **Skip Reasons Log**: `verification/runs/facts/geo_v0_s1/round33_<timestamp>/artifacts/skip_reasons.jsonl` (A/B/C/D 구분)
- **Verts NPZ**: `verification/runs/facts/geo_v0_s1/round33_<timestamp>/artifacts/verts_proxy.npz` (postprocess용 증거)
- **Report**: `reports/validation/geo_v0_s1_facts_round33.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round33_<timestamp>/facts_summary.json` (npz_path, npz_has_verts 포함)

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round33_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

**주의**: 
- Round32 관측: skip_reasons.jsonl records=200, has_mesh_path_true=5 달성
- Round33 목표: proxy 5개 케이스가 Processed>=5로 집계되고, verts NPZ 증거를 남겨 postprocess가 NPZ_PATH_NOT_FOUND로 끝나지 않도록 함
- OBJ 로더 fallback 개선: MTL/재질 완전 무시, encoding='utf-8', errors='ignore'
- 단위 canonicalization: max_abs > 10.0이면 mm->m 변환, SCALE_ASSUMED_MM_TO_M warning 기록
- skip_reasons.jsonl 개선: Type A (manifest_path_is_null), B (mesh_exists_false), C (npz_has_verts=False), D (load_failed) 구분
- postprocess_round.py 보강: npz_path/verts_npz_path/dataset_path 다중 키 지원

## Round 32 (Geo v0 S1 Facts - Skip Reasons Invariant)

- **Runner**: `verification/runners/run_geo_v0_s1_facts.py` (케이스당 1레코드 로깅 불변식 보장)
- **Skip Reasons Log**: `verification/runs/facts/geo_v0_s1/round32_<timestamp>/artifacts/skip_reasons.jsonl` (invariant: records=200, has_mesh_path_true=5)
- **Report**: `reports/validation/geo_v0_s1_facts_round32.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round32_<timestamp>/facts_summary.json`

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round32_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

**주의**: 
- Round31 관측: skip_reasons.jsonl records=195, has_mesh_path_true=0 (proxy 5개 누락)
- Round32는 "케이스당 1레코드 로깅 불변식"을 복구하여 records=200, has_mesh_path_true=5 보장
- has_mesh_path 판정 단일화: (mesh_path is not None) and (str(mesh_path).strip() != "")
- 성공 케이스도 로깅 (stage="measure", reason="success")
- 누락된 케이스는 자동 채우기 (stage="invariant_fill", reason="missing_log_record")

## Round 33 (Geo v0 S1 Facts - OBJ Loader Fallback + Verts NPZ Evidence)

- **Runner**: `verification/runners/run_geo_v0_s1_facts.py` (OBJ 로더 fallback 개선 + verts NPZ 생성)
- **Skip Reasons Log**: `verification/runs/facts/geo_v0_s1/round33_<timestamp>/artifacts/skip_reasons.jsonl` (A/B/C/D 구분)
- **Verts NPZ**: `verification/runs/facts/geo_v0_s1/round33_<timestamp>/artifacts/verts_proxy.npz` (postprocess용 증거)
- **Report**: `reports/validation/geo_v0_s1_facts_round33.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round33_<timestamp>/facts_summary.json` (npz_path, npz_has_verts 포함)

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round33_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

**주의**: 
- Round32 관측: skip_reasons.jsonl records=200, has_mesh_path_true=5 달성
- Round33 목표: proxy 5개 케이스가 Processed>=5로 집계되고, verts NPZ 증거를 남겨 postprocess가 NPZ_PATH_NOT_FOUND로 끝나지 않도록 함
- OBJ 로더 fallback 개선: MTL/재질 완전 무시, encoding='utf-8', errors='ignore'
- 단위 canonicalization: max_abs > 10.0이면 mm->m 변환, SCALE_ASSUMED_MM_TO_M warning 기록
- skip_reasons.jsonl 개선: Type A (manifest_path_is_null), B (mesh_exists_false), C (npz_has_verts=False), D (load_failed) 구분
- postprocess_round.py 보강: npz_path/verts_npz_path/dataset_path 다중 키 지원

## Round 34 (Geo v0 S1 Facts - NPZ 경로 연결 + KPI 집계 필드 보강)

- **Runner**: `verification/runners/run_geo_v0_s1_facts.py` (NPZ 경로 연결 + KPI 필드 보강)
- **Verts NPZ**: `verification/runs/facts/geo_v0_s1/round34_<timestamp>/artifacts/visual/verts_proxy.npz` (postprocess용)
- **Report**: `reports/validation/geo_v0_s1_facts_round34.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round34_<timestamp>/facts_summary.json` (n_samples, summary.valid_cases, npz_path_abs 포함)

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round34_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

**주의**: 
- Round33 관측: proxy 5개는 stage=measure, reason=success로 성공했지만, postprocess KPI가 N/A이며 Visual provenance가 NPZ_PATH_NOT_FOUND로 스킵됨
- Round34 목표: NPZ 증거(verts 포함) 생성/연결 + KPI 집계 입력 잠금
- NPZ 저장 위치: `artifacts/visual/verts_proxy.npz` (postprocess가 찾는 위치)
- facts_summary.json에 KPI 필드 추가: `n_samples`, `summary.valid_cases`
- facts_summary.json에 NPZ 경로 추가: `npz_path`, `dataset_path`, `npz_path_abs` (visual_provenance.py가 찾는 키)

## Round 35 (Geo v0 S1 Facts - KPI 분포 통계 스키마 연결)

- **Runner**: `verification/runners/run_geo_v0_s1_facts.py` (기존 구조 유지)
- **KPI Generator**: `tools/summarize_facts_kpi.py` (value_stats 경로 fallback 추가)
- **Report**: `reports/validation/geo_v0_s1_facts_round35.md`
- **Facts summary**: `verification/runs/facts/geo_v0_s1/round35_<timestamp>/facts_summary.json`

### Run commands

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round35_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

**주의**: 
- Round34 관측: Processed=5, NPZ/Visual 생성 성공, NaN Rate는 집계되었으나 KPI 분포 통계(p50/p95)와 BUST/WAIST/HIP p50이 N/A로 남음
- Round35 원인: summarize_facts_kpi.py가 `summary[key]["median"]`을 찾지만, 실제로는 `summary[key]["value_stats"]["median"]`에 있음
- Round35 해결: summarize_facts_kpi.py의 get_value_distribution 함수에 value_stats 경로 fallback 추가
- 최소 수정 원칙: runner는 변경하지 않고, KPI 요약기만 보강
