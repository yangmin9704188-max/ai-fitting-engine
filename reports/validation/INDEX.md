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
