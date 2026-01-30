# Evidence Schema v1.0

## Overview

Evidence Package는 실험 실행 결과를 저장하는 구조화된 포맷입니다. 각 실행(run)은 독립적인 디렉토리에 저장되며, manifest.json, metrics.json, summary.md 3개 필수 파일을 포함합니다.

## Folder Structure

```
artifacts/<task>/<policy_version>/runs/<run_id>/
  manifest.json
  metrics.json
  summary.md
```

**Example:**
```
artifacts/shoulder_width/v1.2/runs/20260117_153136_PASS/
  manifest.json
  metrics.json
  summary.md
```

## File Requirements

모든 run 디렉토리는 다음 3개 파일을 **필수**로 포함해야 합니다:
- `manifest.json`: 실행 메타데이터 및 환경 정보
- `metrics.json`: 측정 결과 및 회귀 분석
- `summary.md`: 인간 판독용 요약 문서 (Markdown)

## manifest.json Schema

**Required keys:**

```json
{
  "schema_version": "evidence.manifest.v1",
  "task": "shoulder_width",
  "policy_version": "v1.2",
  "run_id": "20260117_153136_PASS",
  "created_at_utc": "2026-01-17T15:31:36Z",
  "runner": {
    "type": "local",
    "host": "hostname",
    "gpu": "cuda:0"
  },
  "code": {
    "repo": "yangmin9704188-max/ai-fitting-engine",
    "git_sha": "abc123def456",
    "dirty": false
  },
  "data": {
    "dataset_id": "SizeKorea_Final",
    "dataset_version": "v1",
    "split": "test"
  },
  "experiment": {
    "name": "shoulder_width_v12_regression",
    "description": "Regression test for shoulder width v1.2",
    "seed": 42
  },
  "baseline": {
    "type": "git_ref",
    "ref": "tags/shoulder_width_v1.1",
    "git_sha": "xyz789uvw012"
  }
}
```

**Validation rules:**
- `schema_version` must be exactly `"evidence.manifest.v1"`
- `baseline.ref` must be present and non-empty (required for regression analysis)
- All top-level keys are required

## metrics.json Schema

**Required keys:**

```json
{
  "schema_version": "evidence.metrics.v1",
  "task": "shoulder_width",
  "policy_version": "v1.2",
  "run_id": "20260117_153136_PASS",
  "metrics": {
    "primary": {
      "name": "mae",
      "value": 0.25,
      "unit": "cm",
      "lower_is_better": true
    },
    "secondary": [
      {
        "name": "fail_rate",
        "value": 0.02,
        "unit": "ratio"
      }
    ]
  },
  "regression": {
    "baseline_ref": "tags/shoulder_width_v1.1",
    "baseline_primary_value": 0.23,
    "delta": 0.02,
    "delta_pct": 8.7
  }
}
```

**Validation rules:**
- `schema_version` must be exactly `"evidence.metrics.v1"`
- `metrics.primary` is required
- `regression.baseline_ref` is required (must match manifest.json baseline.ref)
- `regression.delta` and `regression.delta_pct` are required

## summary.md Schema

Markdown 형식의 인간 판독용 요약 문서입니다. 구조는 자유롭지만, 다음 내용을 포함하는 것을 권장합니다:

- 실행 목적 및 결과 요약
- Primary metric 값 및 baseline 대비 변화
- 주요 발견사항 또는 주의사항

**Example:**
```markdown
# Run Summary: shoulder_width v1.2

## Result: PASS

Primary metric (MAE): 0.25 cm (baseline: 0.23 cm)
- Delta: +0.02 cm (+8.7%)
- Status: Within acceptable range

## Notes
- All test cases passed
- No significant regression detected
```

## PASS/FAIL Rules v1.0

Evidence validation은 다음 규칙에 따라 PASS/FAIL을 판정합니다:

### FAIL Conditions

1. **Missing files**: manifest.json, metrics.json, summary.md 중 하나라도 없으면 FAIL
2. **Schema version mismatch**: schema_version이 `evidence.manifest.v1` 또는 `evidence.metrics.v1`이 아니면 FAIL
3. **Missing baseline.ref**: manifest.json의 `baseline.ref`가 없거나 비어있으면 FAIL
4. **Primary metric regression (lower_is_better=true)**:
   - `abs(delta) > 0.3` 이면 FAIL
   - 또는 `abs(delta_pct) > 5` 이면 FAIL
5. **Secondary metric fail_rate**: `fail_rate`가 있고 `value > 0.05` 이면 FAIL

### PASS Conditions

- 모든 필수 파일이 존재하고
- Schema version이 일치하며
- Baseline ref가 존재하며
- Primary metric 회귀가 허용 범위 내이며
- fail_rate가 없거나 0.05 이하인 경우

## Validation in CI

GitHub Actions 워크플로우(`evidence-check`)는 PR에서 `artifacts/**/runs/**` 변경을 감지하고 `tools/validate_evidence.py`를 실행합니다.

**Skip conditions:**
- Infra-only PR (`.github/**, tools/**, docs/**`만 변경)
- `artifacts/**/runs/**` 변경이 없는 경우

**Validation output:**
- 각 run별 PASS/FAIL 상태
- Primary metric, delta, delta_pct 표시
- fail_rate (있는 경우)
- 최종 요약: `PASSED n / FAILED m`
