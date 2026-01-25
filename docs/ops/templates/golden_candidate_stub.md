# Golden Candidate: [Round ID]

**NOTE: 이 문서는 참고용 후보 스텁입니다. 확정 시 별도 보관(예: docs/judgments/)을 권장합니다.**

## Metadata
- **lane**: [lane]
- **run_dir**: [run_dir]
- **generated_by**: `tools/postprocess_round.py`
- **generated_at**: [timestamp]

## Evidence Links

다음 증거 파일을 확인하세요 (CANDIDATES 기준 상대경로):

- [KPI_DIFF.md](../KPI_DIFF.md)
- [LINEAGE.md](../LINEAGE.md)
- [KPI.md](../KPI.md) (있으면)
- [ROUND_CHARTER.md](../ROUND_CHARTER.md)
- [PROMPT_SNAPSHOT.md](../PROMPT_SNAPSHOT.md)

## KPI_DIFF Summary

### 상위 변화 항목
- [KPI_DIFF.md](../KPI_DIFF.md)에서 확인:
  - Total cases 변화
  - HEIGHT_M p50/p95 변화
  - BUST/WAIST/HIP p50 변화
  - NaN Rate Top5 변화
  - Failure Reason Top5 변화

## Warning Summary

- [KPI_DIFF.md](../KPI_DIFF.md)의 Degradation Signals 확인
- [LINEAGE.md](../LINEAGE.md)의 warnings 확인 (있으면)

## Next Actions (권고/체크리스트)

- [ ] KPI_DIFF.md의 Degradation Signals 검토
- [ ] LINEAGE.md의 code fingerprints 안정성 확인
- [ ] Coverage backlog 상태 확인 (`docs/verification/coverage_backlog.md`)
- [ ] Registry 연속성 확인 (`docs/verification/round_registry.json`)
- [ ] Golden freeze 선언 고려 (`docs/verification/golden_s0_freeze_v0.md` 참조)

**주의**: 위 항목은 "확정"이 아니라 "고려/검토" 사항입니다.
