# ops: slim coverage backlog to all-null keys only (round4)

## 목적
coverage_backlog.md를 "All-null 키(=NaN 100%)만 누적"하도록 규칙을 단순화하여 문서 비대화를 방지합니다.
판정/해석 추가 금지. facts-only 유지.

## 구현 범위

### 1. backlog 기록 조건 단순화
- facts_summary.json 기준으로 **NaN rate 100%인 standard_key만** 대상으로 합니다.
- 이미 존재하는 키면 last_seen 업데이트 + count++.
- 새 키면 first_seen/last_seen/count=1 및 lane/첫 관측 run_dir 기록.
- Top N은 유지하되(예: 30개), 조건을 만족하는 키만.

### 2. 코드 단순화
- VALUE_MISSING 체크 로직 제거
- note 단순화: "NaN 100% (all-null)"로 통일
- lane 정보 추가
- 첫 관측 run_dir 기록

## 변경 파일 목록

- `tools/coverage_backlog.py` (업데이트: 단순화, lane/run_dir 추가)
- `docs/verification/coverage_backlog.md` (업데이트: 헤더 수정)

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
- ✅ coverage_backlog.md 갱신 확인
- ✅ NaN 100% 키만 기록 (all-null keys only)
- ✅ lane 및 first_observed_run_dir 정보 포함
- ✅ postprocess는 0 exit로 종료

### 스모크 테스트 결과

```
Warning: No previous run found for lane 'curated_v0'. Using current as prev.
Lane: curated_v0
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Prev: verification\runs\facts\curated_v0\round20_20260125_164801 (fallback (no prev found, using current))
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Baseline alias: curated-v0-realdata-v0.1 (auto (new registry: curated-v0-realdata-v0.1))
Facts summary: verification\runs\facts\curated_v0\round20_20260125_164801\facts_summary.json
Generated: KPI.md
Generated: KPI_DIFF.md
Updated: reports/validation/round_registry.json (15 entries)
Updated: docs/verification/coverage_backlog.md (6 entries)
Updated: docs/verification/round_registry.json
Generated: LINEAGE.md
Updated: docs/verification/golden_registry.json (1 entries)
Visual provenance unavailable: measurement-only NPZ (no 'verts' key). This is expected for curated_v0 realdata lane.

Postprocessing complete!
```

✅ 모든 기대 결과 확인:
- coverage_backlog.md 갱신 확인 (6 entries)
- NaN 100% 키만 기록 (all-null keys only)
- lane 및 first_observed_run_dir 정보 포함 확인
- postprocess 정상 종료 (exit code 0)

## 주요 개선사항

1. **기록 조건 단순화**:
   - NaN rate 100%인 키만 대상 (VALUE_MISSING 체크 제거)
   - note 단순화: "NaN 100% (all-null)"로 통일

2. **메타데이터 추가**:
   - lane 정보 추가
   - first_observed_run_dir 기록

3. **Top N 제한**:
   - Active keys를 최대 30개로 제한 (정렬 후)

4. **문서 비대화 방지**:
   - 불필요한 복잡한 로직 제거
   - facts-only 원칙 유지

## 참고

- 루트에 파일 추가하지 않음 (tools/ 및 docs/verification/ 안에서만 해결)
- 기존 동작과 호환 (단순화만 수행)
- 판정/해석 추가 없이 facts-only 유지
