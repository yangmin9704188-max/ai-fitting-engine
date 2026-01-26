# validation: round28 S1 20M proxy switch (S1 입력 계약 + processed 확보)

## 목적

Round28을 통해 20F OBJ 오염 확인에 따라 S1 proxy 입력을 20M으로 전환하고, geo_v0_s1 lane baseline alias를 등록합니다.
목적은 정확도가 아니라 S1 입력 계약 + processed 확보 + 운영 마감(postprocess)입니다.
PASS/FAIL 판정 금지. Semantic 재해석/단위 재논의 금지. 대규모 리팩터링 금지.

## 변경 파일 목록

### 커밋 1: validation: switch S1 proxy mesh from 20F to 20M (round28)
- `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json`: proxy 슬롯 5개의 mesh_path를 6th_20M.obj로 교체

### 커밋 2: ops: register geo_v0_s1 baseline alias (round28)
- `docs/ops/baselines.json`: geo_v0_s1 lane의 baseline_tag_alias를 geo-v0-s1-proxy-v0.1로 등록

### 커밋 3: docs(ops,reports): record round28 outputs and commands
- `reports/validation/INDEX.md`: Round28 항목 추가
- `docs/ops/INDEX.md`: Round Registry에 Round28 1줄 추가

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round28_$(date +%Y%m%d_%H%M%S)" \
make geo_v0_s1_round \
RUN_DIR="$RUN_DIR"
```

## Round26 → Round28 변경

### Round26 상태
- proxy mesh: 6th_20F.obj (5개 케이스에 연결)
- baseline alias: geo-v0-s1-baseline-v0.1

### Round28 변경
- **20F OBJ 오염 확인**: 20F OBJ가 오염으로 확인됨
- **S1 proxy 입력 전환**: 20F → 20M
  - OBJ 경로: `verification/datasets/golden/s1_mesh_v0/meshes/6th_20M.obj`
  - proxy 슬롯 5개: 311610164126, 20_F_1049, 121607160426, 21_F_4430, 511609194879
  - note: "proxy mesh for S1 pipeline validation; not 1:1 identity with curated_v0 case" (유지)
  - meta_unit="m" 유지
- **baseline alias 등록**: geo-v0-s1-proxy-v0.1 (Git tag 아님, lane 내부 alias)
  - baseline_run_dir: `verification/runs/facts/geo_v0_s1/round25_20260127_003039`
  - postprocess 출력에서 Baseline alias가 UNSET이 아니게 만듦

## 구현 선택 (facts-only)

### 1) S1 Proxy 입력 전환
- **방식**: s1_manifest_v0.json에서 proxy 슬롯 5개의 mesh_path를 6th_20M.obj로 교체
- **연결된 case_id**: 311610164126, 20_F_1049, 121607160426, 21_F_4430, 511609194879
- **효과**: 20M OBJ로 S1 입력 계약 검증 + processed 확보

### 2) Baseline Alias 등록
- **방식**: docs/ops/baselines.json에서 geo_v0_s1 lane의 baseline_tag_alias를 geo-v0-s1-proxy-v0.1로 등록
- **효과**: postprocess 출력에서 Baseline alias가 UNSET이 아니게 됨

### 3) (옵션) 20M XLSX 변환
- **조건**: 20M xlsx가 제공되면
- **방식**: verification/tools/convert_scan_xlsx_to_csv.py로 mm->m 변환 CSV 생성
- **out_dir**: verification/datasets/golden/s1_mesh_v0/metadata
- **source_id**: scan_6th_20M
- **major_names**: 키,가슴둘레,배꼽수준허리둘레,엉덩이둘레,넙다리둘레

## 금지사항 준수 확인

- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 측정 알고리즘 변경 없음 (입력/manifest만)
- ✅ no PASS/FAIL 판정: facts-only 유지
- ✅ verification/runs/** 커밋 금지 준수
- ✅ semantic 재해석 금지: 단위 변환만 수행 (의미 매핑 금지)

## DoD 체크리스트

### Round28 실행 전 (현재 PR)
- [x] s1_manifest_v0.json에서 proxy 슬롯 5개의 mesh_path를 6th_20M.obj로 교체
- [x] baselines.json에서 geo_v0_s1 baseline alias 등록 (geo-v0-s1-proxy-v0.1)
- [x] reports/validation/INDEX.md 업데이트 (Round28 항목)
- [x] docs/ops/INDEX.md 업데이트 (Round Registry)
- [x] 커밋 및 푸시 완료

### Round28 실행 후 (후속 PR 예정)
- [ ] Round28 실행 (`make geo_v0_s1_round RUN_DIR=...`)
- [ ] 산출물 점검 (KPI.md, KPI_DIFF.md, lineage/manifest, PROMPT_SNAPSHOT.md, visual/SKIPPED.txt)
- [ ] processed/skipped 수치 확인
- [ ] reports/validation/geo_v0_s1_facts_round28.md 생성
- [ ] 커밋: "validation: round28 geo v0 S1 facts + postprocess closure"

## DoD Self-check (facts-only)

**주의**: 아래는 "존재/경로/관측값"으로만 기입 (판정 금지).

### 1) 20M OBJ 파일 확인
- [ ] `verification/datasets/golden/s1_mesh_v0/meshes/6th_20M.obj` exists
  - 파일 크기: [실행 후 기록]
  - sha256: [실행 후 기록] (민영 실행 결과를 그대로 붙여도 됨)
  - verts 수: [실행 후 기록]
  - faces 수: [실행 후 기록]
  - bbox: [실행 후 기록] (min/max 또는 extent)

### 2) Manifest Proxy 슬롯 확인
- [ ] `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json`에서 proxy 슬롯 5개가 6th_20M.obj를 가리킴
  - 연결된 case_id: 311610164126, 20_F_1049, 121607160426, 21_F_4430, 511609194879
  - mesh_path: `verification/datasets/golden/s1_mesh_v0/meshes/6th_20M.obj`

### 3) Baseline Alias 확인
- [ ] `docs/ops/baselines.json`에서 geo_v0_s1 lane의 baseline_tag_alias가 geo-v0-s1-proxy-v0.1로 등록됨
  - baseline_run_dir: `verification/runs/facts/geo_v0_s1/round25_20260127_003039`

### 4) Round28 RUN_DIR 산출물 확인
- [ ] RUN_DIR 경로: `verification/runs/facts/geo_v0_s1/round28_<timestamp>`
- [ ] `KPI.md` exists
- [ ] `KPI_DIFF.md` exists (상단 경고 라인 존재 여부: [실행 후 기록])
- [ ] `lineage/manifest` 또는 `LINEAGE.md` exists
- [ ] `PROMPT_SNAPSHOT.md` exists
- [ ] `artifacts/visual/` 또는 `SKIPPED.txt` exists

### 5) processed/skipped 수치 (facts-only)
- [ ] processed cases: [실행 후 기록]
- [ ] skipped cases: [실행 후 기록]
- [ ] processed > 0 여부: [실행 후 기록]

### 6) Runner 경고/스킵 사유 (facts-only)
- [ ] processed가 0이면, proxy 슬롯(5개)에 대해 "왜 로드가 안 됐는지" facts-only reason 기록
  - 파일 존재 여부: [실행 후 기록]
  - 로드 조건: [실행 후 기록]
  - 예외 메시지: [실행 후 기록]

### 7) Baseline Alias 출력 확인 (postprocess)
- [ ] postprocess 출력에서 Baseline alias가 UNSET이 아님
  - Baseline alias: [실행 후 기록] (예: geo-v0-s1-proxy-v0.1)

## 스모크 테스트

### Manifest Proxy 확인
```bash
py -c "import json; m = json.load(open('verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json')); cases = [c for c in m['cases'] if c.get('mesh_path') == 'verification/datasets/golden/s1_mesh_v0/meshes/6th_20M.obj']; print(f'Proxy 20M cases: {len(cases)}'); print([c['case_id'] for c in cases])"
# 예상: 5개, ['311610164126', '20_F_1049', '121607160426', '21_F_4430', '511609194879']
```

### Baseline Alias 확인
```bash
py -c "import json; b = json.load(open('docs/ops/baselines.json')); print(b.get('geo_v0_s1', {}).get('baseline_tag_alias'))"
# 예상: geo-v0-s1-proxy-v0.1
```

### 링크 유효성 확인
- [x] `docs/ops/baselines.json`에서 geo_v0_s1 lane 링크 유효성 확인
- [x] `reports/validation/INDEX.md`에서 Round28 링크 유효성 확인
- [x] `docs/ops/INDEX.md`에서 Round Registry 링크 유효성 확인

## 롤백

```bash
git revert HEAD~2 HEAD~1 HEAD
```

또는 브랜치 삭제:
```bash
git branch -D validation/round28-s1-20m-proxy-switch
git push origin --delete validation/round28-s1-20m-proxy-switch
```
