# Judgments Index

**Purpose**: Single index for archived judgment/decision documents (확정된 판단/보관 문서).

## Scope & Principles

### 범위
- **확정된 판단/보관 문서**: CANDIDATES 스텁에서 확정된 결정을 기록한 문서
- **참고용 스텁 아님**: CANDIDATES는 참고용이며, 확정 보관은 Human이 수행
- **판정 금지**: 모든 문서는 facts-only, PASS/FAIL 판정 없음

### 원칙
- **Facts-only**: 관찰 가능한 사실만 기록
- **판정 금지**: "좋아졌다/나빠졌다" 같은 판정 문구 금지
- **보관/기록 목적**: 결정 사유와 후속 작업을 기록하는 것이 목적
- **Human 결정**: 자동 확정/승격/등록 금지

## Entry List

*(초기 empty - 확정된 judgment 문서가 추가되면 여기에 링크)*

## File Naming Convention

**규약**: `YYYYMMDD_lane_roundXX_short_title.md`

**예시**:
- `20260126_curated_v0_round20_baseline_update.md`
- `20260126_curated_v0_round20_golden_candidate.md`
- `20260126_geo_v0_round17_golden_s0_freeze.md`

## Evidence Links Rules

### run_dir 상대경로
- Judgment 문서가 `docs/judgments/`에 있을 때, run_dir의 증거 파일을 참조하려면:
  - 예: `../../verification/runs/facts/curated_v0/round20_20260125_164801/KPI_DIFF.md`
  - 예: `../../verification/runs/facts/curated_v0/round20_20260125_164801/CANDIDATES/GOLDEN_CANDIDATE.md`

### 문서 링크 방식
- 다른 judgment 문서 참조: `./YYYYMMDD_lane_roundXX_short_title.md`
- ops 문서 참조: `../ops/DOCUMENT_NAME.md`
- verification 문서 참조: `../verification/DOCUMENT_NAME.md`

## Reference

- **Policy**: [`../ops/JUDGMENTS_POLICY.md`](../ops/JUDGMENTS_POLICY.md)
- **Runbook**: [`../ops/JUDGMENTS_RUNBOOK.md`](../ops/JUDGMENTS_RUNBOOK.md)
- **Template**: [`templates/JUDGMENT_ENTRY_TEMPLATE.md`](templates/JUDGMENT_ENTRY_TEMPLATE.md)
