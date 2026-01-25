# ops: add postprocess_round entrypoint and round registry (round1)

## 목적
라운드 마감을 단일 엔트리포인트로 강제하기 위한 최소 시스템 구현.
`current_run_dir`만 주면 KPI 생성 + prev/baseline 자동해석 + 라운드 레지스트리 기록까지 1회 실행으로 완료.

## 구현 범위

### 1. tools/postprocess_round.py (재작성)
- CLI:
  - `--current_run_dir` (필수)
  - `--lane` (옵션; 없으면 current_run_dir 경로에서 추론)
  - `--baseline_run_dir` (옵션; 없으면 docs/ops/baselines.json에서 lane 키로 로드)
  - `--registry_path` (옵션; 기본: reports/validation/round_registry.json)
- 동작:
  - facts_summary.json 자동 탐색 (우선순위: 직접 경로 → 하위 디렉토리)
  - prev_run_dir 결정: registry에서 같은 lane의 마지막 entry 사용, 없으면 baseline으로 fallback
  - KPI.md 생성: tools/summarize_facts_kpi.py 재사용
  - round_registry.json 업데이트 (append-only)

### 2. docs/ops/baselines.json (신규)
- Lane별 baseline 설정 파일
- 구조: `{ "lane": { "baseline_tag_alias", "baseline_run_dir", "baseline_report" } }`

### 3. reports/validation/round_registry.json (자동 생성)
- Round 레지스트리 (JSON 배열)
- Entry 필드:
  - created_at, lane
  - current_run_dir (상대/절대 경로)
  - facts_summary_path, kpi_path (절대 경로)
  - baseline_run_dir, prev_run_dir (상대/절대 경로)
  - git_commit, baseline_tag_alias

## 변경 파일 목록

- `tools/postprocess_round.py` (재작성: round1 버전)
- `docs/ops/baselines.json` (신규)

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
- ✅ `verification/runs/facts/curated_v0/round20_20260125_164801/KPI.md` 생성
- ✅ `reports/validation/round_registry.json` 생성 및 1개 entry append
- ✅ 콘솔에 prev/baseline 해석 결과 요약 출력

### 스모크 테스트 결과

```
Lane: curated_v0
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Prev: verification\runs\facts\curated_v0\round20_20260125_164801
Facts summary: verification\runs\facts\curated_v0\round20_20260125_164801\facts_summary.json
Generated: KPI.md
Updated: reports/validation/round_registry.json (1 entries)

Postprocessing complete!
```

✅ 모든 기대 결과 확인:
- KPI.md 생성 확인
- round_registry.json 생성 및 entry 추가 확인
- Lane/Baseline/Prev 자동 해석 확인

## 참고
- 이번 PR에서는 KPI_DIFF, coverage_backlog, lineage, visual은 구현하지 않음 (다음 rounds 예정)
- Python 3.10 기준으로 동작 확인
