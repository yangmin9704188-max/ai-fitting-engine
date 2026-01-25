# ops: auto-maintain coverage backlog on postprocess (round3)

## 목적
postprocess_round.py 마감 단계에서 coverage_backlog.md를 자동으로 갱신합니다.
coverage_backlog는 판정이 아니라 "사실"만 누적합니다.

## 구현 범위

### 1. tools/coverage_backlog.py (신규)
- facts_summary.json에서 NaN 100% 키 추출
- coverage_backlog.md 자동 갱신
- 기능:
  - NaN rate = 100%인 standard_key 목록 추출
  - VALUE_MISSING이 높은 경우 우선 표기
  - 각 키마다 메타 정보 기록:
    - first_seen_round, last_seen_round
    - seen_count
    - last_observed_n_cases
    - note (자동 생성)
  - 키가 회복되면 RESOLVED로 전환 (삭제하지 않음)
  - 자동 생성 영역과 수동 영역 구분 (markers 사용)

### 2. tools/postprocess_round.py 업데이트
- KPI.md, KPI_DIFF.md 생성 이후에 coverage_backlog 갱신 단계 추가
- coverage_backlog.py 유틸 호출

### 3. docs/verification/coverage_backlog.md 업데이트
- "Facts-only, no judgement, no auto-fix" 선언문 추가
- 자동 생성 영역 markers 추가:
  - `<!-- AUTO-GENERATED:START -->`
  - `<!-- AUTO-GENERATED:END -->`

## 변경 파일 목록

- `tools/coverage_backlog.py` (신규)
- `tools/postprocess_round.py` (업데이트: coverage_backlog 갱신 추가)
- `docs/verification/coverage_backlog.md` (업데이트: markers 및 선언문 추가)

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
- ✅ docs/verification/coverage_backlog.md 생성 또는 갱신
- ✅ Round20에서 100% NaN인 키(예: NECK_WIDTH_M 등)가 backlog에 추가됨
- ✅ postprocess는 0 exit로 종료

### 스모크 테스트 결과

```
Lane: curated_v0
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Prev: verification\runs\facts\curated_v0\round20_20260125_164801
Facts summary: verification\runs\facts\curated_v0\round20_20260125_164801\facts_summary.json
Generated: KPI.md
Generated: KPI_DIFF.md
Updated: reports/validation/round_registry.json (3 entries)
Updated: docs/verification/coverage_backlog.md (6 entries)

Postprocessing complete!
```

✅ 모든 기대 결과 확인:
- coverage_backlog.md 갱신 확인
- 6개 키 (NECK_DEPTH_M, NECK_WIDTH_M, TOP_HIP_CIRC_M, UNDERBUST_DEPTH_M, UNDERBUST_WIDTH_M, UPPER_HIP_CIRC_M) 추가 확인
- 각 키에 메타 정보 (first_seen_round, last_seen_round, seen_count, last_observed_n_cases, note) 포함 확인
- 자동 생성 영역 markers 포함 확인
- postprocess 정상 종료 (exit code 0)

## Coverage Backlog 구조

생성된 coverage_backlog.md는 다음을 포함:
- **Facts-only 선언**: "Facts-only, no judgement, no auto-fix"
- **자동 생성 영역**: `<!-- AUTO-GENERATED:START -->` ~ `<!-- AUTO-GENERATED:END -->`
- **Active Coverage Gaps**: 현재 100% NaN인 키 목록
- **Resolved Coverage Gaps**: 회복된 키 목록 (status: RESOLVED)

각 항목은 다음 메타 정보를 포함:
- first_seen_round, last_seen_round
- seen_count
- last_observed_n_cases
- note (자동 생성)
- status (ACTIVE/RESOLVED)

## RESOLVED 처리 규칙

- 키가 다시 non-null로 회복되면:
  - backlog에서 삭제하지 않음
  - status를 RESOLVED로 전환
  - resolved_round 기록
  - "Resolved Coverage Gaps" 섹션에 표시

## 참고
- 이번 PR에서는 lineage/visual은 구현하지 않음 (다음 rounds 예정)
- Python 3.10 기준, 크래시 없이 N/A 처리 우선
