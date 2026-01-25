# ops: move PR body drafts under docs and add repo structure guide

## 목적
루트 폴더 가독성 회복을 위한 정리 작업:
- PR 본문 초안을 `docs/ops/pr_bodies/`로 이동
- 루트 폴더 구조 가이드 추가

## 변경 사항

### 1. PR 본문 초안 이동
- 루트의 `pr_body_*.md` 파일 9개를 `docs/ops/pr_bodies/`로 이동:
  - `pr_body_ops_round_charter.md`
  - `pr_body_round1_postprocess.md`
  - `pr_body_round14.md`
  - `pr_body_round18_golden_s0_freeze.md`
  - `pr_body_round2_kpi_diff.md`
  - `pr_body_round20.md`
  - `pr_body_team_system_v0_2.md`
  - `pr_body_team_system_v0_3.md`
  - `pr_body_update_cursorrules.md`

### 2. 문서 추가
- `REPO_STRUCTURE_GUIDE.md` (루트): 폴더 구조 가이드
- `docs/ops/pr_bodies/README.md`: PR 본문 초안 폴더 설명

## 변경 파일 목록

### 신규 파일
- `REPO_STRUCTURE_GUIDE.md` (루트)
- `docs/ops/pr_bodies/README.md`
- `docs/ops/pr_bodies/pr_body_*.md` (9개 파일)

### 이동된 파일
- 루트 → `docs/ops/pr_bodies/`: 9개 PR 본문 초안

## 중요 사항

### SYNC_HUB_FILE_INDEX.md는 루트 유지
- **절대 이동 금지**: LLM 학습/탐색용이므로 루트에 유지합니다.
- 이번 PR에서 이동하지 않았습니다.

### 원칙 준수
- ✅ git rm 금지: 파일 이동만 수행 (git mv 또는 일반 이동 후 git add)
- ✅ 코드 로직 변경 없음: 문서 이동만 수행
- ✅ core/, pipelines/, verification/, tests/ 이동 없음

## 검증

### git status 확인
```
Changes to be committed:
  new file:   REPO_STRUCTURE_GUIDE.md
  new file:   docs/ops/pr_bodies/README.md
  new file:   docs/ops/pr_bodies/pr_body_*.md (9개)
```

✅ 루트에서 `pr_body_*.md` 파일이 모두 사라지고 `docs/ops/pr_bodies/`로 이동됨

## 결과

- 루트 가독성 향상: 임시 PR 본문 초안이 루트에서 제거됨
- 문서 구조 명확화: `REPO_STRUCTURE_GUIDE.md`로 폴더 구조 가이드 제공
- 운영 추적성 유지: PR 본문 초안을 `docs/ops/pr_bodies/`에서 보관
