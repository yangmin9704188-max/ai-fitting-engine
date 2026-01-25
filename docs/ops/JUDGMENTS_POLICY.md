# Judgments Policy

**Purpose**: Define the lifecycle and scope of judgment/decision documents (판단/보관 문서).

## Core Principle

**CANDIDATES는 참고용 스텁이며, 확정 보관은 Human이 수행한다.**

- `run_dir/CANDIDATES/` 하위 문서는 자동 생성되는 참고용 스텁
- 확정된 결정을 기록한 문서는 `docs/judgments/`에 Human이 보관
- 자동 이동/자동 승격/자동 판정 로직 금지

## What Can Go to Judgments?

다음 신호/체크리스트 기반으로 judgments 보관을 고려할 수 있습니다 (판정 금지):

### Golden Candidate Signals
- Coverage 신호: All-null 키 감소 + 신규 등장 없음
- Distribution 신호: HEIGHT_M p50/p95 안정성 + BUST/WAIST/HIP p50 안정성
- Failure Reason 신호: Top5 reason 안정성 (교집합 높음)
- Registry 신호: Round 연속성 + Artifact 완성도
- Lineage 신호: Code fingerprint 안정성 + NPZ 메타데이터 일관성

**참고**: [`COMMIT_POLICY.md`](COMMIT_POLICY.md)의 "Golden candidate signals" 섹션 참조

### Baseline Update Signals
- KPI_DIFF에서 Baseline vs Current 비교 결과 안정성
- Coverage backlog 상태 개선
- Registry 연속성 유지
- SYNC_HUB T1/T3 트리거 해당 여부

**참고**: [`BASELINE_UPDATE_RUNBOOK.md`](BASELINE_UPDATE_RUNBOOK.md) 참조

### Checklist (판정 금지)
- [ ] CANDIDATES 문서(GOLDEN_CANDIDATE, BASELINE_CANDIDATE 등) 존재
- [ ] Evidence links (KPI_DIFF, LINEAGE, ROUND_CHARTER 등) 완성
- [ ] Golden candidate signals 또는 baseline update signals 관찰
- [ ] 후속 작업(태그, registry 적용, SYNC_HUB 업데이트) 검토 완료

**주의**: 위 체크리스트는 "판정"이 아니라 "고려 사항"입니다.

## Integration with Commit Policy

Judgments 보관은 [`COMMIT_POLICY.md`](COMMIT_POLICY.md)의 "Action mapping"과 정합됩니다:

- **Golden tag 후보 신호** → Golden candidate judgment 보관 고려
- **Baseline 후보 신호** → Baseline update judgment 보관 고려
- **Registry 업데이트 권고** → Registry patch 적용 judgment 보관 고려

**참고**: Commit policy의 "Action mapping"은 "자동 수행"이 아니라 "권고/후속 작업"입니다.

## File Naming & Location

- **Location**: `docs/judgments/`
- **Naming**: `YYYYMMDD_lane_roundXX_short_title.md`
- **Template**: [`docs/judgments/templates/JUDGMENT_ENTRY_TEMPLATE.md`](../judgments/templates/JUDGMENT_ENTRY_TEMPLATE.md)
- **Index**: [`docs/judgments/INDEX.md`](../judgments/INDEX.md)

## Prohibited Actions

- **자동 이동 금지**: CANDIDATES 문서를 자동으로 judgments로 이동 금지
- **자동 승격 금지**: CANDIDATES 스텁을 자동으로 확정 문서로 승격 금지
- **자동 판정 금지**: PASS/FAIL 판정 로직 추가 금지
- **의미 변경 금지**: CANDIDATES 문서의 의미를 변경하지 않음

## Reference

- **Runbook**: [`JUDGMENTS_RUNBOOK.md`](JUDGMENTS_RUNBOOK.md)
- **Commit Policy**: [`COMMIT_POLICY.md`](COMMIT_POLICY.md)
- **Baseline Update Runbook**: [`BASELINE_UPDATE_RUNBOOK.md`](BASELINE_UPDATE_RUNBOOK.md)
