# validation: round28 20M xlsx to csv metadata conversion (S1 입력 계약 강화)

## 목적

Round28을 통해 20M 스캔 메타데이터 XLSX를 CSV로 변환하고, S1 facts 실행을 위한 입력 계약을 강화합니다.
목적은 정확도가 아니라 S1 입력 계약 + processed 확보 + 운영 마감(postprocess)입니다.
PASS/FAIL 판정 금지. Semantic 재해석/단위 재논의 금지. 대규모 리팩터링 금지.

## 변경 파일 목록

### 커밋 1: validation: convert 6th 20M scan xlsx to normalized metadata csv (round28)
- `docs/ops/COMMANDS.md`: 변환 커맨드 추가 (convert-scan-xlsx-to-csv)
- `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json`: measurements_csv 경로를 scan_6th_20M_measurements_m.csv로 업데이트

### 커밋 2: docs(ops,reports): record round28 xlsx-to-csv conversion
- `reports/validation/INDEX.md`: Round28 XLSX→CSV 변환 항목 추가
- `docs/ops/INDEX.md`: Round Registry에 Round28 XLSX→CSV 변환 추가

## 변환 커맨드

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

## 산출물 기대

변환 스크립트 실행 후 다음 파일들이 생성됩니다:

- `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20M_measurements_m.csv` (전체/정규화된 형태)
- `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20M_major_measurements_m.csv` (major_names subset)

## Round28 Proxy Switch → XLSX→CSV 변환

### 이전 상태 (Round28 Proxy Switch)
- proxy mesh: 6th_20M.obj (5개 케이스에 연결)
- measurements_csv: scan_6th_20F_measurements_m.csv (20F CSV 사용)

### Round28 XLSX→CSV 변환
- **입력**: `data/raw/scans_3d/ORIGINAL_6th_20M_data.xlsx` (레포 루트 기준 상대경로)
- **변환**: mm → m (precision 0.001m)
- **출력**: scan_6th_20M_measurements_m.csv, scan_6th_20M_major_measurements_m.csv
- **S1 manifest 업데이트**: measurements_csv를 scan_6th_20M_measurements_m.csv로 변경

## 구현 선택 (facts-only)

### 1) XLSX→CSV 변환
- **방식**: verification/tools/convert_scan_xlsx_to_csv.py 사용
- **입력**: data/raw/scans_3d/ORIGINAL_6th_20M_data.xlsx
- **출력**: verification/datasets/golden/s1_mesh_v0/metadata/
- **단위 변환**: raw_unit="mm" → meta_unit="m", precision=0.001
- **효과**: 20M 스캔 메타데이터를 정규화된 CSV로 변환

### 2) S1 Manifest 업데이트
- **방식**: s1_manifest_v0.json에서 첫 번째 proxy 케이스의 measurements_csv를 scan_6th_20M_measurements_m.csv로 업데이트
- **효과**: S1 입력 계약 강화 (20M OBJ + 20M CSV 일치)

### 3) Weight 경고 처리
- **현재 상태**: Round26에서 create_weight_metadata() 호출 제거됨 (A안)
- **추가 작업**: XLSX/CSV에서 weight(kg) 컬럼이 존재할 경우만 공급 (현재는 스킵 상태 유지)
- **효과**: weight 경고 없음 (facts-only: weight가 없음을 기록하지 않음)

## 금지사항 준수 확인

- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 측정 알고리즘 변경 없음 (입력/manifest만)
- ✅ no PASS/FAIL 판정: facts-only 유지
- ✅ verification/runs/** 커밋 금지 준수
- ✅ semantic 재해석 금지: 단위 변환만 수행 (의미 매핑 금지)
- ✅ .gitignore 확인: *.xlsx가 이미 있으므로 추가 작업 불필요

## DoD 체크리스트

### Round28 XLSX→CSV 변환 실행 전 (현재 PR)
- [x] docs/ops/COMMANDS.md에 변환 커맨드 추가
- [x] s1_manifest_v0.json에서 measurements_csv 경로 업데이트
- [x] reports/validation/INDEX.md 업데이트 (Round28 XLSX→CSV 변환 항목)
- [x] docs/ops/INDEX.md 업데이트 (Round Registry)
- [x] 커밋 및 푸시 완료

### Round28 XLSX→CSV 변환 실행 후 (후속 작업)
- [ ] 변환 커맨드 실행 (위 커맨드)
- [ ] 산출물 확인 (scan_6th_20M_measurements_m.csv, scan_6th_20M_major_measurements_m.csv)
- [ ] Round28 실행 (`make geo_v0_s1_round RUN_DIR=...`)
- [ ] 산출물 점검 (KPI.md, KPI_DIFF.md, lineage/manifest, PROMPT_SNAPSHOT.md, visual/SKIPPED.txt)
- [ ] processed/skipped 수치 확인
- [ ] reports/validation/geo_v0_s1_facts_round28.md 생성
- [ ] 커밋: "validation: round28 geo v0 S1 facts + postprocess closure"

## DoD Self-check (facts-only)

**주의**: 아래는 "존재/경로/관측값"으로만 기입 (판정 금지).

### 1) 변환 커맨드 및 생성된 CSV 경로
- [ ] 변환 커맨드 실행 완료
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
- [ ] 생성된 CSV 경로 2개:
  - `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20M_measurements_m.csv`
  - `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20M_major_measurements_m.csv`

### 2) CSV 일부 스니펫 (헤더/상단 3행)
```
[실행 후 CSV 헤더 및 상단 3행 복사]
```

### 3) S1 Manifest 업데이트 확인
- [ ] `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json`에서 첫 번째 proxy 케이스의 measurements_csv가 scan_6th_20M_measurements_m.csv로 업데이트됨
  - case_id: 311610164126
  - measurements_csv: `verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20M_measurements_m.csv`

### 4) Round28 실행 결과 (facts-only)
- [ ] processed cases: [실행 후 기록]
- [ ] skipped cases: [실행 후 기록]
- [ ] processed > 0 여부: [실행 후 기록]

### 5) Postprocess 산출물 생성 확인
- [ ] `KPI.md` exists
- [ ] `KPI_DIFF.md` exists (상단 경고 라인 존재 여부: [실행 후 기록])
- [ ] `lineage/manifest` 또는 `LINEAGE.md` exists
- [ ] `PROMPT_SNAPSHOT.md` exists

### 6) Runner 경고/스킵 사유 (facts-only)
- [ ] processed가 0이면, proxy 슬롯(5개)에 대해 "왜 로드가 안 됐는지" facts-only reason 기록
  - 파일 존재 여부: [실행 후 기록]
  - 로드 조건: [실행 후 기록]
  - 예외 메시지: [실행 후 기록]

## 스모크 테스트

### 변환 커맨드 확인
```bash
# 커맨드가 COMMANDS.md에 추가되었는지 확인
grep -A 10 "convert-scan-xlsx-to-csv" docs/ops/COMMANDS.md
# 예상: 변환 커맨드가 표시됨
```

### Manifest 업데이트 확인
```bash
py -c "import json; m = json.load(open('verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json')); c = m['cases'][0]; print(f'measurements_csv: {c.get(\"measurements_csv\")}')"
# 예상: verification/datasets/golden/s1_mesh_v0/metadata/scan_6th_20M_measurements_m.csv
```

### 링크 유효성 확인
- [x] `docs/ops/COMMANDS.md`에서 변환 커맨드 링크 유효성 확인
- [x] `reports/validation/INDEX.md`에서 Round28 링크 유효성 확인
- [x] `docs/ops/INDEX.md`에서 Round Registry 링크 유효성 확인

## 롤백

```bash
git revert HEAD~1 HEAD
```

또는 브랜치 삭제:
```bash
git branch -D validation/round28-20m-xlsx-to-csv-metadata
git push origin --delete validation/round28-20m-xlsx-to-csv-metadata
```
