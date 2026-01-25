# ops: add PR template checklist for round artifacts (round2)

## 목적
PR마다 라운드 산출물 누락을 방지하기 위해 PR 템플릿을 추가/보강합니다.

## 구현 범위

### 1. `.github/pull_request_template.md` (신규)
- 체크박스 형태로 라운드 산출물 체크리스트 추가
- 섹션:
  - Round Info: lane / run_dir / baseline alias
  - Artifacts: KPI.md / KPI_DIFF.md / LINEAGE.md / (visual: images or SKIPPED.txt)
  - Registry Updates: reports/validation/round_registry.json 갱신 여부, docs/verification/coverage_backlog.md 갱신 여부
  - Smoke logs: postprocess 로그/스크립트 실행 로그
- 40줄 내외로 유지

## 변경 파일 목록

- `.github/pull_request_template.md` (신규)

## 금지사항 준수 확인
- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 runner/측정 로직 의미 변경 없음
- ✅ no PASS/FAIL 판정: facts-only 유지

## PR 템플릿 내용

```markdown
## Round Artifacts Checklist

### Round Info
- [ ] Lane: `curated_v0` / `geo_v0` / etc.
- [ ] Run directory: `verification/runs/facts/<lane>/<round_id>`
- [ ] Baseline alias: `curated-v0-realdata-v0.1` / etc.

### Artifacts
- [ ] `KPI.md` generated
- [ ] `KPI_DIFF.md` generated
- [ ] `LINEAGE.md` generated
- [ ] Visual provenance:
  - [ ] Images (`front_xy.png`, `side_zy.png`) OR
  - [ ] `SKIPPED.txt` (for measurement-only NPZ)

### Registry Updates
- [ ] `reports/validation/round_registry.json` updated
- [ ] `docs/verification/coverage_backlog.md` updated (if applicable)
- [ ] `docs/verification/round_registry.json` updated
- [ ] `docs/verification/golden_registry.json` updated (if applicable)

### Smoke Test Logs
<!-- Paste postprocess or script execution logs here -->
```

## 참고

- GitHub는 `.github/pull_request_template.md` 파일을 자동으로 PR 템플릿으로 인식합니다
- PR 생성 시 이 템플릿이 자동으로 채워집니다
- 체크박스를 통해 라운드 산출물 누락을 방지할 수 있습니다
