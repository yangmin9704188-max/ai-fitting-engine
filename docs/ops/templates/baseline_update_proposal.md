# Baseline Update Proposal: [Round ID]

**NOTE: 이 문서는 참고용 후보 제안서입니다. baseline 갱신은 별도 PR로만 수행합니다.**

## Current Context

- **lane**: [lane]
- **run_dir**: [run_dir]
- **current_baseline_alias**: [baseline_alias]
- **current_baseline_run_dir**: [baseline_run_dir]
- **generated_at**: [timestamp]
- **generated_by**: `tools/postprocess_round.py`

## Evidence Links

다음 증거 파일을 확인하세요 (CANDIDATES 기준 상대경로):

- [KPI_DIFF.md](../KPI_DIFF.md)
- [LINEAGE.md](../LINEAGE.md)
- [KPI.md](../KPI.md) (있으면)
- [ROUND_CHARTER.md](../ROUND_CHARTER.md)
- [PROMPT_SNAPSHOT.md](../PROMPT_SNAPSHOT.md)
- [GOLDEN_CANDIDATE.md](./GOLDEN_CANDIDATE.md)
- [BASELINE_CANDIDATE.md](./BASELINE_CANDIDATE.md)

## KPI_DIFF Change Summary

다음은 KPI_DIFF.md에서 추출한 변화 요약입니다 (facts-only, 판정 없음):

[KPI_DIFF 변화 항목이 여기에 나열됩니다]

## Risks & Rollback

- **Rollback 방법**: baseline alias/run_dir을 이전 값으로 되돌리기
- **영향 범위**: `docs/ops/baselines.json`, `docs/verification/round_registry.json`의 baseline 설정
- **주의사항**: baseline 변경은 이후 모든 round의 비교 기준을 변경합니다

## SYNC_HUB Checklist

다음 항목을 검토하세요 (체크는 하지 말고, 필요 여부만 확인):

- [ ] SYNC_HUB.md 업데이트가 필요한가?
- [ ] T1 또는 T3 트리거에 해당하는 변경인가?
- [ ] baseline alias(curated-v0-realdata-v0.1) 또는 baseline_run_dir 변경이 포함되는가?

**참고**: SYNC_HUB 업데이트는 baseline 갱신과 별도로 검토해야 합니다.

## Next Actions (권고/체크리스트)

- [ ] KPI_DIFF.md의 Baseline vs Current 비교 검토
- [ ] LINEAGE.md의 code fingerprints 안정성 확인
- [ ] Coverage backlog 상태 확인 (`docs/verification/coverage_backlog.md`)
- [ ] Registry 연속성 확인 (`docs/verification/round_registry.json`)
- [ ] Baseline 갱신 PR 준비 (`docs/ops/BASELINE_UPDATE_RUNBOOK.md` 참조)

**주의**: 위 항목은 "확정"이 아니라 "고려/검토" 사항입니다.
