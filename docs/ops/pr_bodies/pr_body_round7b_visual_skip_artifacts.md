# ops: always create visual artifact dir and record skip reason (round7b)

## 목적
Visual Provenance 정책을 "A(verts가 있는 lane에서만)"로 고정하고,
measurement-only NPZ(curated_v0 realdata 등)에서는 visual을 생성하지 않되
항상 artifacts/visual 폴더를 만들고, 스킵 이유를 폴더 파일로 남기며,
postprocess 콘솔에도 고정 문구를 더 명확히 출력합니다.

## 구현 범위

### 1. Visual 대상 정책(A로 고정)
- Visual Provenance는 "verts 기반 NPZ"에서만 생성합니다.
- NPZ에 'verts' 키가 없으면 (예: measurements-only realdata NPZ):
  - visual 생성은 스킵이 정상이며, 이를 명시적으로 문서/로그/폴더 파일로 기록합니다.
- 이 정책을 `docs/verification/visual_provenance_contract_v0.md`에 명문화:
  - "measurement-only lane(curated_v0 realdata)은 visual N/A가 정상"을 1문단으로 고정.

### 2. 폴더는 항상 생성
- postprocess 실행 시 무조건 아래 경로를 생성:
  - `<current_run_dir>/artifacts/visual/`
- 생성 실패 시에도 postprocess 전체가 죽지 않도록 warnings + LINEAGE 기록.

### 3. 스킵 사유를 폴더 파일로 남김
- visual 생성이 스킵되는 경우, `artifacts/visual/` 안에 `SKIPPED.txt` 생성
- 내용(필수 포함):
  - visual_status: skipped
  - reason: measurement-only npz (no verts key)
  - npz_keys: [...] (실제 키 목록)
  - lane: <lane>
  - run_dir: <abs or rel>
  - timestamp

### 4. LINEAGE.md에도 동일 요약 기록
- visual_status, visual_reason, npz_has_verts=false, npz_keys

### 5. 콘솔 고정 문구 강화
- visual이 스킵되면 postprocess 로그에 반드시 아래 고정 문구를 포함:
  - "Visual provenance unavailable: measurement-only NPZ (no 'verts' key). This is expected for curated_v0 realdata lane."
- 단, lane 이름을 하드코딩하지 말고,
  - no 'verts' key 인 상황이면 항상 출력하되,
  - "expected" 문구는 lane이 curated_v0이거나 schema_version에 realdata 힌트가 있으면 추가로 붙이는 식으로 "조건부"로.

## 변경 파일 목록

- `tools/visual_provenance.py` (업데이트: 항상 폴더 생성, SKIPPED.txt 생성, npz_keys 기록)
- `tools/postprocess_round.py` (업데이트: lane 전달, 콘솔 고정 문구 강화, LINEAGE 업데이트)
- `docs/verification/visual_provenance_contract_v0.md` (업데이트: Visual 대상 정책 명문화)

## 금지사항 준수 확인
- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 runner/측정 로직 의미 변경 없음
- ✅ no PASS/FAIL 판정: facts-only 유지

## 스모크 테스트

### 실행 명령
```bash
py tools/postprocess_round.py \
  --current_run_dir verification/runs/facts/curated_v0/round20_20260125_164801
```

### 기대 결과
- ✅ `<run_dir>/artifacts/visual/` 폴더가 존재
- ✅ 그 안에 `SKIPPED.txt` 생성
- ✅ 콘솔에 고정 문구 출력
- ✅ LINEAGE.md에 visual_status=skipped 및 reason 기록

### 스모크 테스트 결과

```
Lane: curated_v0
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Prev: verification\runs\facts\curated_v0\round20_20260125_164801
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Facts summary: verification\runs\facts\curated_v0\round20_20260125_164801\facts_summary.json
Generated: KPI.md
Generated: KPI_DIFF.md
Updated: reports/validation/round_registry.json (10 entries)
Updated: docs/verification/coverage_backlog.md (6 entries)
Updated: docs/verification/round_registry.json
Generated: LINEAGE.md
Updated: docs/verification/golden_registry.json (1 entries)
Visual provenance unavailable: measurement-only NPZ (no 'verts' key). This is expected for curated_v0 realdata lane.

Postprocessing complete!
```

✅ 모든 기대 결과 확인:
- `<run_dir>/artifacts/visual/` 폴더 생성 확인
- `SKIPPED.txt` 파일 생성 확인
- 콘솔에 고정 문구 출력 확인 ("Visual provenance unavailable: measurement-only NPZ (no 'verts' key). This is expected for curated_v0 realdata lane.")
- LINEAGE.md에 Visual Provenance 섹션 추가 확인:
  - status: `skipped`
  - reason: `measurement-only npz (no verts key)`
  - npz_has_verts: `False`
  - npz_keys: `measurements`, `case_id`, `case_class`, `case_metadata`, `meta_unit`, `schema_version`, `created_at`, `source_path_abs`
- postprocess 정상 종료 (exit code 0)

## 생성된 SKIPPED.txt 내용 (핵심 라인)

```
Visual Provenance: SKIPPED
==================================================

visual_status: skipped
reason: measurement-only npz (no verts key)
npz_path: C:\Users\caino\Desktop\AI_model\verification\datasets\golden\core_measurements_v0\golden_real_data_v0.npz
npz_keys: ['measurements', 'case_id', 'case_class', 'case_metadata', 'meta_unit', 'schema_version', 'created_at', 'source_path_abs']
npz_has_verts: False
lane: curated_v0
run_dir: verification\runs\facts\curated_v0\round20_20260125_164801
timestamp: 2026-01-25T21:09:48.303507
```

## LINEAGE.md의 Visual Provenance 섹션 일부

```markdown
## Visual Provenance

- **status**: `skipped`
- **reason**: `measurement-only npz (no verts key)`
- **npz_has_verts**: `False`
- **npz_keys**: `measurements`, `case_id`, `case_class`, `case_metadata`, `meta_unit`, `schema_version`, `created_at`, `source_path_abs`
```

## 참고

- 루트에 파일 추가하지 않음 (tools/ 및 docs/verification/ 안에서만 해결)
- Visual Provenance는 각 run_dir에 생성 (라운드별 산출물)
- measurement-only NPZ의 경우 graceful하게 스킵하고 사실만 기록 (판정 없음)
- 이는 오류가 아니라 해당 lane의 데이터 특성에 따른 예상된 동작입니다.
