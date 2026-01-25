# Visual Provenance Contract v0

## 목적

Visual Provenance는 시각 증거로 스케일/축/찌그러짐을 빠르게 식별하기 위한 2D 투영 이미지입니다.

**판정 금지**: 이미지로 PASS/FAIL을 내리지 않습니다. facts-only 기록입니다.

## Visual 대상 정책 (A로 고정)

Visual Provenance는 **"verts 기반 NPZ"에서만 생성**합니다.

NPZ에 `'verts'` 키가 없으면 (예: measurements-only realdata NPZ):
- visual 생성은 스킵이 정상이며, 이를 명시적으로 문서/로그/폴더 파일로 기록합니다.
- measurement-only lane(curated_v0 realdata 등)은 visual N/A가 정상입니다.
- 이는 오류가 아니라 해당 lane의 데이터 특성에 따른 예상된 동작입니다.

## 산출물 경로

- `<current_run_dir>/artifacts/visual/` (항상 생성, visual 생성 여부와 무관)
- 파일 (visual 생성 성공 시):
  - `front_xy.png` (정면: X vs Y)
  - `side_zy.png` (측면: Z vs Y)
  - `front_xy_expected_fail.png` / `side_zy_expected_fail.png` (expected_fail 케이스인 경우)
- 파일 (visual 생성 스킵 시):
  - `SKIPPED.txt` (스킵 사유, NPZ 키 목록, lane, run_dir, timestamp 포함)

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
  - 랜덤 샘플링 또는 stride로 downsample (최대 50k)
  - 샘플링 사용 시 LINEAGE.md에 기록 (`downsample_n`, `method`)

## 데이터 로딩/호환성

NPZ loader가 반환한 verts가:
- `(V,3)` ndarray 또는 list-like
- `(N,)` dtype=object로서 각 원소가 `(V,3)`인 형태

어떤 경우든 "선택한 case의 verts"를 안정적으로 얻습니다.

## 실패 시 기록 규칙

verts가 없거나 shape가 이상하면:
- 예외로 죽지 않고 warnings 출력 + visual 생성 스킵
- **항상 `artifacts/visual/` 폴더 생성**
- **스킵 시 `artifacts/visual/SKIPPED.txt` 파일 생성** (visual_status, reason, npz_keys, lane, run_dir, timestamp 포함)
- LINEAGE.md에 `visual_status: skipped`, `visual_reason`, `npz_has_verts=false`, `npz_keys` 기록
- postprocess 콘솔에 고정 문구 출력: "Visual provenance unavailable: measurement-only NPZ (no 'verts' key). This is expected for [lane] realdata lane." (lane이 curated_v0이거나 realdata 힌트가 있으면 "expected" 문구 추가)

## 통합

- `postprocess_round.py` 실행 시 KPI/KPI_DIFF/LINEAGE 생성 이후 단계에서 visual 생성 수행
- visual 생성 성공 시:
  - LINEAGE.md outputs 섹션에 이미지 상대경로 2개 추가
  - KPI.md 하단에 "Visual Provenance" 섹션 추가 (링크/경로만; 이미지 embed는 markdown 로컬 경로로)
- 라운드 마감의 "완료" 정의는 그대로 유지 (visual 실패해도 전체는 죽지 않되, LINEAGE에 사실 기록)

## Headless 환경 대응

- `import matplotlib; matplotlib.use("Agg")` 를 렌더 함수 시작에 명시
- 저장 실패 시에도 크래시 금지. warnings + lineage 기록.
