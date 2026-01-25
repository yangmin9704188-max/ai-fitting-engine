# Baseline Update Runbook

**목적**: baseline 갱신 절차를 명확히 정의 (판정 금지, facts-only)

## 원칙

- **Baseline 갱신은 별도 PR로만 수행**: postprocess_round.py는 제안서만 생성
- **자동 갱신 금지**: baseline alias/run_dir 자동 변경 금지
- **판정 금지**: "좋아졌다/나빠졌다" 같은 판정 문구 금지
- **Facts-only**: 관찰 가능한 사실만 기록

## 업데이트 대상 파일

다음 파일들이 baseline 갱신 시 검토 대상입니다 (검토 후 확정):

- `docs/ops/baselines.json`: baseline alias/run_dir/report 설정
- `docs/verification/round_registry.json`: lanes.<lane>.baseline 설정
- `docs/ops/INDEX.md`: baseline 정보 링크/요약
- `SYNC_HUB.md`: T1/T3 트리거에 해당하는 경우만

## 태그 추천

태그는 "후보"로만 제안:

- 예: `curated-v0-realdata-v0.2` (v0.1 → v0.2)
- 예: `curated-v0-realdata-v0.1.1` (패치 버전)

**주의**: 태그는 "추천"일 뿐, 확정은 별도 승인 필요

## 절차

1. **제안서 검토**: `run_dir/CANDIDATES/BASELINE_UPDATE_PROPOSAL.md` 확인
2. **KPI_DIFF 검토**: Baseline vs Current 비교 확인
3. **Evidence 검토**: LINEAGE, KPI, ROUND_CHARTER 확인
4. **SYNC_HUB 체크**: T1/T3 트리거 여부 확인
5. **Baseline 갱신 PR 생성**: 별도 PR로 baseline 설정 업데이트
6. **태그 생성 (선택)**: 필요 시 태그 생성 및 문서화

## Rollback

Baseline 갱신 후 문제가 발견되면:

1. `docs/ops/baselines.json`을 이전 값으로 되돌리기
2. `docs/verification/round_registry.json`의 baseline 설정 되돌리기
3. 이후 round의 baseline 비교 기준이 변경됨을 인지

## 참고

- `docs/ops/COMMIT_POLICY.md`: Golden candidate signals 및 action mapping
- `docs/verification/golden_s0_freeze_v0.md`: Golden freeze 예시
