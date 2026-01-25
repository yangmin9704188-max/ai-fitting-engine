# Round Registry Contract v0

## Purpose

Round Registry는 "사실"만 기록합니다:
- 어떤 run_dir가 있었는지
- 무엇을 생성했는지 (KPI.md, KPI_DIFF.md 등)
- coverage_backlog가 갱신되었는지

**판정/추측 없이 누적만 수행합니다.**

## Schema

File: `docs/verification/round_registry.json`

```json
{
  "schema_version": "round_registry@1",
  "updated_at": "ISO timestamp",
  "lanes": {
    "<lane>": {
      "baseline": {
        "alias": "...",
        "run_dir": "...",
        "report": "..."
      },
      "rounds": [
        {
          "round_id": "...",
          "round_num": 20,
          "run_dir": "...",
          "facts_summary": "...",
          "report": "...",
          "kpi": "...",
          "kpi_diff": "...",
          "coverage_backlog_touched": true/false,
          "created_at": "...",
          "source_npz": "...",
          "source_path_abs": "...",
          "notes": ""
        }
      ],
      "latest": {
        "round_id": "...",
        "run_dir": "..."
      }
    }
  }
}
```

## Baseline Immutability Rule

**중요**: baseline은 "사람이 선언한 값"이므로, 자동으로 바꾸지 않습니다.

- 레지스트리에 baseline이 이미 존재하면 변경하지 않음
- 레지스트리에 baseline이 없으면 `docs/ops/baselines.json`에서 초기값으로 설정
- 이후 baseline 변경은 수동으로만 가능

## Round Registration Policy

- `postprocess_round.py` 실행 시 `--current_run_dir`를 입력받음
- `current_run_dir`에서 lane/round_num/round_id를 파싱
- 해당 `round_id`가 registry에 없으면 append, 있으면 업데이트(덮어쓰기)
- 생성된 산출물 존재 여부를 boolean으로 기록:
  - `kpi`: KPI.md 존재 여부
  - `kpi_diff`: KPI_DIFF.md 존재 여부
  - `coverage_backlog_touched`: coverage_backlog 업데이트 여부

## Field Meanings

- `round_id`: run_dir 이름 (예: round20_20260125_164801)
- `round_num`: round 번호 (예: 20)
- `run_dir`: 상대 경로
- `facts_summary`: 상대 경로 (없으면 null)
- `report`: 리포트 파일 경로 (상대 경로)
- `kpi`, `kpi_diff`: 상대 경로 (없으면 null)
- `source_npz`: 소스 NPZ 경로 (상대 경로, 가능하면)
- `source_path_abs`: 소스 파일 절대 경로 (있으면)
- `coverage_backlog_touched`: 이번 라운드에서 coverage_backlog가 갱신되었는지

## Notes

- 모든 경로는 가능하면 상대 경로로 저장
- `source_path_abs` 같은 필드는 절대 경로로 기록 가능
- JSON write는 atomic하게 구현 (임시파일 -> rename)
