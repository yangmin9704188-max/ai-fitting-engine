# Judgments Runbook

**Purpose**: Human 절차 체크리스트 for creating judgment/decision documents.

## Prerequisites

다음 중 하나 이상이 준비되어 있어야 합니다:

- `run_dir/CANDIDATES/GOLDEN_CANDIDATE.md` 존재
- `run_dir/CANDIDATES/BASELINE_CANDIDATE.md` 존재
- `run_dir/CANDIDATES/GOLDEN_REGISTRY_PATCH.json` 존재
- `run_dir/CANDIDATES/BASELINE_UPDATE_PROPOSAL.md` 존재

## Procedure Checklist

### 1. CANDIDATES 문서 확인
- [ ] 어떤 CANDIDATES 문서(또는 patch/proposal)를 근거로 하는지 확인
- [ ] 해당 문서의 Evidence links 확인
- [ ] CANDIDATES 문서의 내용 검토 (facts-only)

### 2. Evidence Links 수집
다음 증거 링크를 반드시 포함해야 합니다:

- [ ] ROUND_CHARTER.md (run_dir 상대경로)
- [ ] PROMPT_SNAPSHOT.md (run_dir 상대경로)
- [ ] KPI_DIFF.md (run_dir 상대경로)
- [ ] LINEAGE.md (run_dir 상대경로)
- [ ] KPI.md (run_dir 상대경로, 있으면)
- [ ] CANDIDATES 문서 링크 (GOLDEN_CANDIDATE, BASELINE_CANDIDATE 등)
- [ ] Registry 링크 (round_registry.json, golden_registry.json 등)

**경로 규칙**: `docs/judgments/`에서 run_dir로 가는 상대경로는 `../../verification/runs/...` 형태

### 3. 파일명 결정
- [ ] 파일명 규약 준수: `YYYYMMDD_lane_roundXX_short_title.md`
- [ ] 예시: `20260126_curated_v0_round20_baseline_update.md`

### 4. Judgment 문서 작성
- [ ] [`docs/judgments/templates/JUDGMENT_ENTRY_TEMPLATE.md`](../judgments/templates/JUDGMENT_ENTRY_TEMPLATE.md) 사용
- [ ] Metadata 섹션 작성 (lane, round, run_dir, baseline 등)
- [ ] Evidence Links 섹션 작성 (모든 링크 포함)
- [ ] Decision Record 섹션 작성 (facts-only, 판정 없음)
- [ ] Follow-ups 섹션 작성 (후속 작업 체크리스트)

### 5. INDEX.md 업데이트
- [ ] [`docs/judgments/INDEX.md`](../judgments/INDEX.md)의 "Entry List" 섹션에 새 judgment 링크 추가

### 6. 커밋/태그 권고
- [ ] 커밋 메시지: `judgment: [short_title] for [lane] [round_id]`
- [ ] 태그 후보 (필요 시): 예: `curated-v0-realdata-v0.2`
- [ ] 태그는 "후보"로만, 확정은 별도 승인 필요

### 7. SYNC_HUB 업데이트 검토
다음 항목을 검토하세요 (체크는 하지 말고, 필요 여부만 확인):

- [ ] SYNC_HUB.md 업데이트가 필요한가?
- [ ] T1 또는 T3 트리거에 해당하는 변경인가?
- [ ] baseline alias 또는 baseline_run_dir 변경이 포함되는가?

**참고**: SYNC_HUB 업데이트는 baseline 갱신과 별도로 검토해야 합니다.

## Example Workflow

1. `postprocess_round.py` 실행 후 `CANDIDATES/` 폴더 확인
2. `CANDIDATES/GOLDEN_CANDIDATE.md` 또는 `BASELINE_UPDATE_PROPOSAL.md` 검토
3. Evidence links 수집 (KPI_DIFF, LINEAGE 등)
4. Judgment 문서 작성 (템플릿 사용)
5. `docs/judgments/INDEX.md` 업데이트
6. 커밋 및 PR 생성
7. (선택) 태그 생성

## Reference

- **Policy**: [`JUDGMENTS_POLICY.md`](JUDGMENTS_POLICY.md)
- **Template**: [`../judgments/templates/JUDGMENT_ENTRY_TEMPLATE.md`](../judgments/templates/JUDGMENT_ENTRY_TEMPLATE.md)
- **Index**: [`../judgments/INDEX.md`](../judgments/INDEX.md)
- **Commit Policy**: [`COMMIT_POLICY.md`](COMMIT_POLICY.md)
- **Baseline Update Runbook**: [`BASELINE_UPDATE_RUNBOOK.md`](BASELINE_UPDATE_RUNBOOK.md)
