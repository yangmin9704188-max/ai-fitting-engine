# Round24 실행 가이드

## Round24 실행 명령

### 1) XLSX→CSV 변환 (mm -> m)

```bash
py verification/tools/convert_scan_xlsx_to_csv.py \
  --input_xlsx "./20F_data.xlsx" \
  --out_dir "verification/datasets/golden/s1_mesh_v0/metadata" \
  --source_id "scan_6th_20F" \
  --raw_unit "mm" \
  --meta_unit "m" \
  --precision "0.001" \
  --major_names "키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레"
```

**기대 산출물**:
- `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20F_measurements_m.csv`
- `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20F_major_measurements_m.csv`

### 2) OBJ 파일 복사 (수동)

```bash
# OBJ 파일이 레포 루트에 있다면:
cp 6차_20대_여성.obj verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj

# 또는 data/raw/scans_3d/에 있다면:
cp data/raw/scans_3d/6차_20대_여성.obj verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj
```

### 3) Round24 실행

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round24_$(date +%Y%m%d_%H%M%S)" \
make geo_v0_s1_round \
RUN_DIR="$RUN_DIR"
```

## 실행 후 확인 사항

1. **CSV 파일 존재 확인**:
   - [ ] `scan_6th_20F_measurements_m.csv` 존재 및 파일 크기 확인
   - [ ] `scan_6th_20F_major_measurements_m.csv` 존재 및 파일 크기 확인

2. **OBJ 파일 존재 확인**:
   - [ ] `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj` 존재 및 파일 크기 확인

3. **S1 manifest 확인**:
   - [ ] `s1_manifest_v0.json`에 proxy 연결 확인 (mesh_path, measurements_csv, note)

4. **Round24 산출물 확인**:
   - [ ] RUN_DIR에 `KPI.md` 존재
   - [ ] RUN_DIR에 `KPI_DIFF.md` 존재
   - [ ] RUN_DIR에 `lineage/manifest` 또는 `LINEAGE.md` 존재
   - [ ] RUN_DIR에 `PROMPT_SNAPSHOT.md` 존재
   - [ ] RUN_DIR에 `artifacts/visual/` 또는 `SKIPPED.txt` 존재

5. **coverage_backlog 확인**:
   - [ ] `reports/validation/coverage_backlog.md` 업데이트 확인 (있다면)
