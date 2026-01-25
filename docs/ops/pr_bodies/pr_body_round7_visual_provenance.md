# ops: add visual provenance snapshots on postprocess (round7)

## 목적
postprocess_round.py 마감 단계에서 "Visual Provenance"를 자동 생성합니다.
대표 케이스(우선 normal_1) 또는 첫 valid case의 메쉬(verts)를
정면(front: X-Y) / 측면(side: Z-Y) 2D 투영 이미지로 저장하고,
KPI.md 또는 LINEAGE.md에 산출물 링크/경로를 기록합니다.
외부 렌더러 의존 없이(matplotlib만) 항상 동작해야 합니다.

## 구현 범위

### 1. tools/visual_provenance.py (신규)
- Visual Provenance 생성 유틸리티
- 기능:
  - NPZ에서 verts 로딩 (다양한 형식 지원: object array, batched, single)
  - Case 선택 (우선순위: normal_1 -> 첫 valid -> 첫 expected_fail)
  - 2D 투영 렌더링 (front: X-Y, side: Z-Y)
  - Downsampling (큰 메쉬의 경우 > 200k -> 50k로 샘플링)
  - Headless 환경 대응 (matplotlib.use("Agg"))
  - 실패 시 graceful handling (warnings 출력, 크래시 금지)

### 2. tools/postprocess_round.py 업데이트
- Visual Provenance 생성 로직 추가
- LINEAGE.md 업데이트 (visual metadata 추가)
- KPI.md 업데이트 (Visual Provenance 섹션 추가)

### 3. 문서
- `docs/verification/visual_provenance_contract_v0.md` (신규)

## 변경 파일 목록

- `tools/visual_provenance.py` (신규)
- `tools/postprocess_round.py` (업데이트: visual_provenance 통합)
- `docs/verification/visual_provenance_contract_v0.md` (신규)

## 산출물 경로

- `<current_run_dir>/artifacts/visual/` (자동 생성)
- 파일:
  - `front_xy.png` (정면: X vs Y)
  - `side_zy.png` (측면: Z vs Y)
  - `front_xy_expected_fail.png` / `side_zy_expected_fail.png` (expected_fail 케이스인 경우)

## Case 선택 규칙

우선순위:
1. `case_id == "normal_1"` 이 존재하고 valid로 분류되면 사용
2. 아니면 "valid cases" 중 첫 번째
3. valid가 없으면: expected_fail 중 첫 번째 (파일명에 `_expected_fail` suffix 추가)

선택 결과는 LINEAGE.md에 기록:
- `visual_case_id`
- `visual_case_class` ("valid" 또는 "expected_fail")
- `visual_case_is_valid` (boolean)
- `selection_reason`

## 2D 투영 렌더링 규칙

- **matplotlib 사용** (추가 의존성 금지)
- 포인트 클라우드 scatter로 렌더링:
  - front: `x = verts[:,0]`, `y = verts[:,1]`
  - side: `x = verts[:,2]`, `y = verts[:,1]`
- 축 설정:
  - `aspect='equal'`
  - y축이 위로 보이도록 (invert 하지 않음)
  - bbox 범위를 타이트하게 (여백 5% 정도)
- 점 개수(V)가 너무 크면(> 200k):
  - 랜덤 샘플링으로 downsample (최대 50k)
  - 샘플링 사용 시 LINEAGE.md에 기록 (`downsample_n`, `method`)

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
- ✅ Visual Provenance 생성 시도
- ✅ LINEAGE.md에 visual metadata 기록
- ✅ KPI.md에 Visual Provenance 섹션 추가
- ✅ postprocess는 0 exit로 종료 (visual 실패해도 전체는 죽지 않음)

### 스모크 테스트 결과

```
Lane: curated_v0
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Prev: verification\runs\facts\curated_v0\round20_20260125_164801
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Facts summary: verification\runs\facts\curated_v0\round20_20260125_164801\facts_summary.json
Generated: KPI.md
Generated: KPI_DIFF.md
Updated: reports/validation/round_registry.json (8 entries)
Updated: docs/verification/coverage_backlog.md (6 entries)
Updated: docs/verification/round_registry.json
Generated: LINEAGE.md
Updated: docs/verification/golden_registry.json (1 entries)
Warning: Visual generation skipped: ["VERTS_KEY_NOT_FOUND: NPZ contains keys ['measurements', 'case_id', 'case_class', 'case_metadata', 'meta_unit', 'schema_version', 'created_at', 'source_path_abs'], but no 'verts' key. Visual provenance requires vertex data.", 'CASE_ID_COUNT_MISMATCH: case_ids=200, verts=0', 'NO_VERTS_LOADED']

Postprocessing complete!
```

✅ 모든 기대 결과 확인:
- Visual Provenance 생성 시도 확인 (NPZ에 verts가 없어 스킵됨 - 예상된 동작)
- LINEAGE.md에 Visual Provenance 섹션 추가 확인:
  - status: `skipped`
  - warnings: 3 warning(s)
- KPI.md에 Visual Provenance 섹션 추가 확인:
  - 스킵 메시지 및 경고 내용 기록
- postprocess 정상 종료 (exit code 0)

**참고**: 이번 테스트에서 사용한 NPZ 파일(`golden_real_data_v0.npz`)은 measurements만 포함하고 verts를 포함하지 않습니다. Visual Provenance는 verts가 있는 NPZ에서만 이미지를 생성합니다. verts가 없는 경우 graceful하게 스킵하고 LINEAGE.md와 KPI.md에 사실을 기록합니다.

## 성능/안전

- Headless 환경 대응: `matplotlib.use("Agg")` 사용
- 모든 파일 write는 atomic하게 구현 (필요 시)
- 실패 시 예외로 죽지 않고 warnings 출력 후 계속:
  - NPZ에 verts가 없으면: visual 생성 스킵, LINEAGE에 기록
  - 파일 읽기 실패: 해당 필드만 N/A로 처리
  - 렌더링 실패: warnings 출력, 전체 프로세스는 계속

## 참고

- 루트에 파일 추가하지 않음 (tools/ 및 docs/verification/ 안에서만 해결)
- Visual Provenance는 각 run_dir에 생성 (라운드별 산출물)
- verts가 없는 NPZ의 경우 graceful하게 스킵 (판정 없이 사실만 기록)
