# ops: auto-maintain round registry on postprocess (round4)

## 목적
postprocess_round.py 마감 단계에서 round_registry.json을 자동으로 갱신합니다.
round_registry는 "사실(어떤 run_dir가 있었고 무엇을 생성했는지)"만 기록합니다.

## 구현 범위

### 1. tools/round_registry.py (신규)
- round_registry.json read/update/write 담당
- 기능:
  - lane/round_num/round_id 파싱
  - baseline 불변 규칙 적용 (이미 있으면 유지, 없으면 초기값 설정)
  - round 등록 정책 (없으면 append, 있으면 업데이트)
  - 산출물 존재 여부 기록 (KPI.md, KPI_DIFF.md, coverage_backlog_touched)
  - source_npz, source_path_abs 추출
  - Atomic write (임시파일 -> rename)

### 2. tools/postprocess_round.py 업데이트
- 마지막 단계에서 `update_new_round_registry()` 호출 추가
- coverage_backlog_touched 플래그 전달

### 3. docs/verification/round_registry.json (신규)
- 새로운 스키마로 생성
- lanes 기반 구조:
  - `lanes.<lane>.baseline`: baseline 정보 (불변)
  - `lanes.<lane>.rounds[]`: round 엔트리 배열
  - `lanes.<lane>.latest`: 최신 round 정보

### 4. docs/verification/round_registry_contract_v0.md (신규)
- 레지스트리 스키마 및 정책 문서
- baseline 불변 규칙 명시
- 필드 의미 요약

## 변경 파일 목록

- `tools/round_registry.py` (신규)
- `tools/postprocess_round.py` (업데이트: round_registry 업데이트 호출 추가)
- `docs/verification/round_registry.json` (신규)
- `docs/verification/round_registry_contract_v0.md` (신규)

## Baseline 불변 규칙

**중요**: baseline은 "사람이 선언한 값"이므로, 자동으로 바꾸지 않습니다.

- 레지스트리에 baseline이 이미 존재하면 변경하지 않음
- 레지스트리에 baseline이 없으면 `docs/ops/baselines.json`에서 초기값으로 설정
- 이번 PR에서는 curated_v0 lane baseline을 초기값으로 설정:
  - alias: curated-v0-realdata-v0.1
  - run_dir: verification/runs/facts/curated_v0/round20_20260125_164801
  - report: reports/validation/curated_v0_facts_round1.md

## 레지스트리 스키마 요약

```json
{
  "schema_version": "round_registry@1",
  "updated_at": "ISO timestamp",
  "lanes": {
    "<lane>": {
      "baseline": { "alias", "run_dir", "report" },
      "rounds": [
        {
          "round_id", "round_num", "run_dir",
          "facts_summary", "report", "kpi", "kpi_diff",
          "coverage_backlog_touched", "created_at",
          "source_npz", "source_path_abs", "notes"
        }
      ],
      "latest": { "round_id", "run_dir" }
    }
  }
}
```

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
- ✅ docs/verification/round_registry.json 생성 또는 갱신
- ✅ lanes.curated_v0.baseline가 초기값으로 설정
- ✅ lanes.curated_v0.latest가 round20으로 설정
- ✅ rounds 배열에 round20 엔트리 존재
- ✅ postprocess는 0 exit로 종료

### 스모크 테스트 결과

```
Lane: curated_v0
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Prev: verification\runs\facts\curated_v0\round20_20260125_164801
Facts summary: verification\runs\facts\curated_v0\round20_20260125_164801\facts_summary.json
Generated: KPI.md
Generated: KPI_DIFF.md
Updated: reports/validation/round_registry.json (4 entries)
Updated: docs/verification/coverage_backlog.md (6 entries)
Updated: docs/verification/round_registry.json

Postprocessing complete!
```

✅ 모든 기대 결과 확인:
- round_registry.json 생성 확인
- lanes.curated_v0.baseline 초기값 설정 확인:
  - alias: curated-v0-realdata-v0.1
  - run_dir: verification/runs/facts/curated_v0/round20_20260125_164801
  - report: reports/validation/curated_v0_facts_round1.md
- lanes.curated_v0.latest 설정 확인:
  - round_id: round20_20260125_164801
- rounds 배열에 round20 엔트리 포함 확인:
  - round_id, round_num, run_dir, facts_summary, kpi, kpi_diff
  - coverage_backlog_touched: true
  - source_npz, source_path_abs 포함
- postprocess 정상 종료 (exit code 0)

## Round 등록 정책

- `round_id`가 registry에 없으면 append
- `round_id`가 registry에 있으면 업데이트(덮어쓰기)
- 생성된 산출물 존재 여부를 boolean으로 기록:
  - `kpi`: KPI.md 존재 여부
  - `kpi_diff`: KPI_DIFF.md 존재 여부
  - `coverage_backlog_touched`: coverage_backlog 업데이트 여부

## 안전장치

- JSON write는 atomic하게 구현 (임시파일 -> rename)
- 상대경로를 저장(가능하면)하되, source_path_abs 같은 필드는 abs로 기록
- facts_summary.json이 없으면 registry 업데이트는 하되, facts_summary 경로는 null로 기록하고 warning 출력

## 참고

- 기존 `reports/validation/round_registry.json`은 유지 (backward compatibility)
- 새로운 `docs/verification/round_registry.json`은 새로운 스키마로 생성
- 루트에 파일 추가하지 않음 (docs/verification/와 tools/ 안에서만 해결)
