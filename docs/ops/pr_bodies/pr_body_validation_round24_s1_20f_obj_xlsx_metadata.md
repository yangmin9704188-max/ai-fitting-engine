# validation: round24 S1 20F OBJ/XLSX proxy mesh + metadata normalization

## 목적

Round24를 통해 20대 여성 OBJ(6차_20대_여성.obj) + 스캔 치수 XLSX(20F_data.xlsx)를 프로젝트 규칙에 맞게 정규화/추출/저장하고, S1 manifest에 proxy로 연결합니다.
PASS/FAIL 판정 금지. Semantic 재해석/단위 재논의 금지. 대규모 리팩터링 금지.

## 변경 파일 목록

### 커밋 1: validation: add xlsx->csv converter
- `verification/tools/convert_scan_xlsx_to_csv.py`: XLSX→CSV 변환 스크립트 (mm→m 단위 정규화, major 항목 필터링)

### 커밋 2: validation: add 6th 20F obj + link into S1 manifest
- `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json`: proxy mesh 연결 (mesh_path, measurements_csv, note)

### 커밋 3: reports(validation): add round24 entry
- `reports/validation/INDEX.md`: Round24 항목 추가

### 커밋 4: docs(ops): add round24 registry line + sync(current_state)
- `docs/ops/INDEX.md`: Round Registry에 Round24 1줄 추가
- `docs/sync/CURRENT_STATE.md`: 변경 경로 기록 (verification/tools/, verification/datasets/golden/s1_mesh_v0/)

## 재현 커맨드

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

**주의**: Round24 실행 후 산출물 확인 및 DoD Self-check 수행 필요.

## 단위 변환 계약

### 변환 규칙
- **raw_unit**: "mm" (기본값, 명시적 옵션)
- **meta_unit**: "m" (프로젝트 규칙)
- **변환식**: `value_m = value_raw_mm / 1000.0`
- **precision**: 0.001m (반올림)

### CSV 컬럼
- `source_id`: 소스 식별자 (e.g., "scan_6th_20F")
- `gender`: 성별 (F/M, 메타 라인에서 파싱)
- `age`: 연령 (메타 라인에서 파싱)
- `no`: 번호
- `item_code`: 측정항목 코드
- `item_name_ko`: 측정항목명 (한국어)
- `value_raw`: 원본 값
- `raw_unit`: 원본 단위 (mm)
- `value_m`: 변환된 값 (m)
- `meta_unit`: 메타 단위 (m)

### Major 항목
- `--major_names`로 받은 항목명만 필터링:
  - 키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레
- 별도 CSV 파일 생성: `{source_id}_major_measurements_m.csv`

## XLSX 파싱 규칙

### 파일 구조 (현재 파일 형태 고정)
- **0행**: "성별 : F / 연령 : 20" 메타 라인 (gender/age 파싱)
- **1행**: 헤더 (No., 측정항목 코드, 측정항목명, 측정값)
- **2행부터**: 데이터

### 주의사항
- 표준키로 매핑하거나 정답 검증하지 않음 (금지)
- 단위 변환만 수행 (의미 매핑 금지)

## OBJ 파일 정리

### 원본
- `data/raw/scans_3d/6차_20대_여성.obj`

### 목적 경로
- `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj`

### 재현성
- 파일이 크지 않으므로 git에 포함 가능 (정책 위반 경로 아님)
- PR에 포함할지 여부는 "재현성" 기준으로 판단

## S1 manifest proxy 연결

### 업데이트 내용
- 첫 번째 케이스에 proxy mesh 연결:
  - `mesh_path`: `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj`
  - `measurements_csv`: `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20F_measurements_m.csv`
  - `note`: "proxy mesh for S1 pipeline validation; not 1:1 identity with curated_v0 case"

### 주의사항
- **proxy mesh (정합 주장 금지)**: curated_v0 case_id와 1:1 정합 주장 금지
- note로 명시: "not 1:1 identity with curated_v0 case"
- null vs file-missing SKIPPED 구분 로직은 Round23 runner 규칙 유지

## 금지사항 준수 확인

- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 runner/측정 로직 의미 변경 없음 (연결만 수행)
- ✅ no PASS/FAIL 판정: facts-only 유지
- ✅ verification/runs/** 및 data/processed/** 커밋 금지 준수
- ✅ INDEX.md 중복 생성 금지: 기존 파일만 업데이트
- ✅ semantic 재해석 금지: 단위 변환만 수행, 의미 매핑 금지

## DoD 체크리스트

### Round24 실행 전 (현재 PR)
- [x] XLSX→CSV 변환 스크립트 추가 (mm→m, major 필터)
- [x] OBJ 파일 복사 경로 준비
- [x] S1 manifest에 proxy 연결
- [x] reports/validation/INDEX.md 업데이트 (Round24 항목)
- [x] docs/ops/INDEX.md 업데이트 (Round Registry)
- [x] docs/sync/CURRENT_STATE.md 업데이트 (변경 경로 기록)
- [x] 커밋 및 푸시 완료

### Round24 실행 후 (후속 PR 예정)
- [ ] XLSX→CSV 변환 실행
- [ ] OBJ 파일 복사 확인
- [ ] Round24 실행 (`make geo_v0_s1_round RUN_DIR=...`)
- [ ] 산출물 점검 (KPI.md, KPI_DIFF.md, lineage/manifest, PROMPT_SNAPSHOT.md, visual/SKIPPED.txt)
- [ ] reports/validation/geo_v0_s1_facts_round24.md 생성
- [ ] 커밋: "validation: round24 geo v0 S1 facts + postprocess closure"

## DoD Self-check (facts-only)

**주의**: 아래는 "존재/경로/관측값"으로만 기입 (판정 금지).

### 1) CSV 파일 존재 확인
- [ ] `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20F_measurements_m.csv` exists
  - 파일 크기: [실행 후 기록]
- [ ] `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20F_major_measurements_m.csv` exists
  - 파일 크기: [실행 후 기록]

### 2) OBJ 파일 존재 확인
- [ ] `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj` exists
  - 파일 크기: [실행 후 기록]

### 3) S1 manifest proxy 연결 확인
- [ ] `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json`에 proxy 연결 확인
  - `mesh_path`: `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj`
  - `measurements_csv`: `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20F_measurements_m.csv`
  - `note`: "proxy mesh for S1 pipeline validation; not 1:1 identity with curated_v0 case"

### 4) Round24 RUN_DIR 산출물 확인
- [ ] RUN_DIR 경로: `verification/runs/facts/geo_v0_s1/round24_<timestamp>`
- [ ] `KPI.md` exists
- [ ] `KPI_DIFF.md` exists
- [ ] `lineage/manifest` 또는 `LINEAGE.md` exists
- [ ] `PROMPT_SNAPSHOT.md` exists
- [ ] `artifacts/visual/` 또는 `SKIPPED.txt` exists

### 5) coverage_backlog 업데이트 확인
- [ ] `reports/validation/coverage_backlog.md` 업데이트 발생 여부
  - 추가된 키 (있다면): [실행 후 기록]

## 스모크 테스트

### 변환 스크립트 확인
```bash
python verification/tools/convert_scan_xlsx_to_csv.py --help
# 예상: --input_xlsx, --out_dir, --source_id, --raw_unit, --meta_unit, --precision, --major_names 옵션 표시
```

### Manifest 확인
```bash
py -c "import json; m = json.load(open('verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json')); c = m['cases'][0]; print(f'mesh_path: {c.get(\"mesh_path\")}, measurements_csv: {c.get(\"measurements_csv\")}, note: {c.get(\"note\")}')"
# 예상: mesh_path와 measurements_csv가 설정됨, note에 "proxy" 및 "not 1:1 identity" 포함
```

### 링크 유효성 확인
- [x] `verification/tools/convert_scan_xlsx_to_csv.py` 존재 확인
- [x] `reports/validation/INDEX.md`에서 Round24 링크 유효성 확인
- [x] `docs/ops/INDEX.md`에서 Round Registry 링크 유효성 확인

## 롤백

```bash
git revert HEAD~3 HEAD~2 HEAD~1 HEAD
```

또는 브랜치 삭제:
```bash
git branch -D validation/round24-s1-20f-obj-xlsx-metadata
git push origin --delete validation/round24-s1-20f-obj-xlsx-metadata
```
