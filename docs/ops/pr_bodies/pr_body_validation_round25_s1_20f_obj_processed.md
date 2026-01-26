# validation: round25 S1 20F OBJ processing (processed>0 목표)

## 목적

Round25를 통해 Round24에서 관측된 200/200 skipped(verts 없음) 문제를 해결하고, S1 입력(OBJ)을 실제로 채워 processed>0을 만듭니다.
PASS/FAIL 판정 금지. Semantic 재해석/단위 재논의 금지. 대규모 리팩터링 금지.

## 변경 파일 목록

### 커밋 1: validation: wire 6th 20F obj into S1 manifest
- `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json`: 20F OBJ 실존 경로 확인 (이미 연결됨)

### 커밋 2: validation: enable OBJ/verts loading path
- `verification/runners/run_geo_v0_s1_facts.py`: OBJ 직접 로드 기능 추가 (A안)

### 커밋 3: docs(ops,reports): record round25
- `reports/validation/INDEX.md`: Round25 항목 추가
- `docs/ops/INDEX.md`: Round Registry에 Round25 1줄 추가

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round25_$(date +%Y%m%d_%H%M%S)" \
make geo_v0_s1_round \
RUN_DIR="$RUN_DIR"
```

## 입력 로딩 방식 (A안: OBJ 직접 로드)

### 구현 선택
- **A안 (선택)**: runner가 OBJ를 직접 로드하여 verts를 얻고, 기존 측정 경로로 전달
- **B안 (미선택)**: OBJ->verts(npz) 변환기 추가

### OBJ 로딩 구현
- `load_verts_from_path()` 함수에 OBJ 지원 추가
- trimesh 라이브러리 우선 사용 (있으면)
- fallback: 간단한 OBJ 파서 (v lines만 파싱)
- 단위 변환: OBJ가 mm/cm 스케일이면 자동으로 m로 변환 (max_abs > 10.0 기준)

### SKIPPED 사유 구분
- **Type A**: manifest_path_is_null (기존)
- **Type B**: manifest_path_set_but_file_missing (기존)
- **Type C**: parse_error (신규) - OBJ/NPZ 파싱 실패, verts shape 오류 등

## Round24 → Round25 개선

### Round24 관측
- 200/200 cases skipped (verts 없음)
- 모든 케이스가 Type A 또는 Type B로 skip

### Round25 목표
- 최소 1 케이스 processed>0
- OBJ 직접 로드로 verts 추출
- 기존 측정 로직 그대로 사용 (알고리즘 변경 금지)

## 금지사항 준수 확인

- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 측정 알고리즘 변경 없음 (입력 로딩만 추가)
- ✅ no PASS/FAIL 판정: facts-only 유지
- ✅ verification/runs/** 커밋 금지 준수
- ✅ semantic 재해석 금지: 단위 변환만 수행 (의미 매핑 금지)

## DoD 체크리스트

### Round25 실행 전 (현재 PR)
- [x] 20F OBJ 파일 경로 확인 (verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj)
- [x] S1 manifest에 실존 경로 연결 확인
- [x] OBJ 직접 로드 기능 추가 (A안)
- [x] SKIPPED 사유 Type C 추가 (parse_error)
- [x] reports/validation/INDEX.md 업데이트 (Round25 항목)
- [x] docs/ops/INDEX.md 업데이트 (Round Registry)
- [x] 커밋 및 푸시 완료

### Round25 실행 후 (후속 PR 예정)
- [ ] Round25 실행 (`make geo_v0_s1_round RUN_DIR=...`)
- [ ] 산출물 점검 (KPI.md, KPI_DIFF.md, lineage/manifest, PROMPT_SNAPSHOT.md, visual/SKIPPED.txt)
- [ ] processed/skipped 수치 확인
- [ ] reports/validation/geo_v0_s1_facts_round25.md 생성
- [ ] 커밋: "validation: round25 geo v0 S1 facts + postprocess closure"

## DoD Self-check (facts-only)

**주의**: 아래는 "존재/경로/관측값"으로만 기입 (판정 금지).

### 1) OBJ 파일 존재 확인
- [ ] `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj` exists
  - 파일 크기: 903222 bytes (실행 전 확인)

### 2) S1 manifest 실존 경로 확인
- [ ] `verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json`에 20F proxy 연결
  - `mesh_path`: `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj`
  - `note`: "proxy mesh for S1 pipeline validation; not 1:1 identity with curated_v0 case"

### 3) Round25 RUN_DIR 산출물 확인
- [ ] RUN_DIR 경로: `verification/runs/facts/geo_v0_s1/round25_<timestamp>`
- [ ] `KPI.md` exists
- [ ] `KPI_DIFF.md` exists (상단 경고 라인 존재 여부: [실행 후 기록])
- [ ] `lineage/manifest` 또는 `LINEAGE.md` exists
- [ ] `PROMPT_SNAPSHOT.md` exists
- [ ] `artifacts/visual/` 또는 `SKIPPED.txt` exists

### 4) processed/skipped 수치 (facts-only)
- [ ] processed cases: [실행 후 기록]
- [ ] skipped cases: [실행 후 기록]
- [ ] processed > 0 여부: [실행 후 기록]

### 5) SKIPPED 상단 5줄 (facts-only)
```
[실행 후 SKIPPED.txt 상단 5줄 복사]
```

### 6) 사용한 OBJ/verts 경로
- [ ] OBJ 경로: `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj`
- [ ] 로딩 방식: A안 (OBJ 직접 로드, trimesh 또는 fallback parser)

## 스모크 테스트

### OBJ 로딩 확인
```bash
py -c "from verification.runners.run_geo_v0_s1_facts import load_verts_from_path; import numpy as np; v = load_verts_from_path('verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj'); print(f'Loaded verts: shape={v.shape if v is not None else None}')"
# 예상: verts shape (V, 3) 또는 None
```

### Manifest 확인
```bash
py -c "import json; m = json.load(open('verification/datasets/golden/s1_mesh_v0/s1_manifest_v0.json')); c = m['cases'][0]; print(f'mesh_path: {c.get(\"mesh_path\")}, exists: {__import__(\"pathlib\").Path(c.get(\"mesh_path\")).exists() if c.get(\"mesh_path\") else False}')"
# 예상: mesh_path가 설정되고 파일 존재
```

### 링크 유효성 확인
- [x] `verification/datasets/golden/s1_mesh_v0/meshes/6th_20F.obj` 존재 확인
- [x] `reports/validation/INDEX.md`에서 Round25 링크 유효성 확인
- [x] `docs/ops/INDEX.md`에서 Round Registry 링크 유효성 확인

## 롤백

```bash
git revert HEAD~2 HEAD~1 HEAD
```

또는 브랜치 삭제:
```bash
git branch -D validation/round25-s1-20f-obj-processed
git push origin --delete validation/round25-s1-20f-obj-processed
```
