# ops: consolidate round PR bodies and sync registries

## 목적
ops 산출물 정리 + 운영 문서/레지스트리 최신화

## 구현 범위

### 1. PR 본문 정리
- `docs/ops/pr_bodies/` 아래의 모든 `pr_body_round*.md` 파일 추가
- 총 14개 PR 본문 파일 정리

### 2. 레지스트리/문서 최신화
- `docs/verification/coverage_backlog.md` 갱신
- `docs/verification/curated_v0_gate_draft_v0.md` 갱신
- `docs/verification/golden_registry.json` 갱신
- `docs/verification/round_registry.json` 갱신
- `reports/validation/curated_v0_facts_round1.md` 갱신
- `reports/validation/round_registry.json` 추가

### 3. .gitignore 업데이트
- `verification/datasets/runs/` 추가 (런타임 생성물 제외)
- `verification/tmp/` 추가 (임시 파일 제외)

### 4. 기타 문서
- `docs/semantic/legacy_handling.md` 추가

## 변경 파일 목록

**신규 파일 (16개):**
- `docs/ops/pr_bodies/pr_body_round1_make_round_wrapper.md`
- `docs/ops/pr_bodies/pr_body_round2_pr_template_round_checklist.md`
- `docs/ops/pr_bodies/pr_body_round3_auto_prev_baseline.md`
- `docs/ops/pr_bodies/pr_body_round3_coverage_backlog.md`
- `docs/ops/pr_bodies/pr_body_round3_root_cleanup.md`
- `docs/ops/pr_bodies/pr_body_round4_round_registry.md`
- `docs/ops/pr_bodies/pr_body_round4_slim_coverage_backlog.md`
- `docs/ops/pr_bodies/pr_body_round5_kpi_diff.md`
- `docs/ops/pr_bodies/pr_body_round5_kpi_diff_signal_line.md`
- `docs/ops/pr_bodies/pr_body_round6_lineage_golden_registry.md`
- `docs/ops/pr_bodies/pr_body_round6_ops_lock_text_sensor.md`
- `docs/ops/pr_bodies/pr_body_round7_visual_provenance.md`
- `docs/ops/pr_bodies/pr_body_round7b_visual_skip_artifacts.md`
- `docs/semantic/legacy_handling.md`
- `reports/validation/round_registry.json`

**수정 파일 (6개):**
- `.gitignore`
- `docs/verification/coverage_backlog.md`
- `docs/verification/curated_v0_gate_draft_v0.md`
- `docs/verification/golden_registry.json`
- `docs/verification/round_registry.json`
- `reports/validation/curated_v0_facts_round1.md`

## 제외된 항목 (별도 PR로 분리 권장)

- `reports/validation/geo_v0_facts_round*.md` (9개 파일) - 이번 PR 스코프에서 제외
- `tools/analyze_warnings_v3_final.py` - 이번 PR 목적과 무관
- `tools/diagnose_7th_xlsx_raw_cells.py` - 이번 PR 목적과 무관
- `tools/find_exact_matches_v2.py` - 이번 PR 목적과 무관
- `tools/generate_unit_fail_summary.py` - 이번 PR 목적과 무관
- 루트의 임시 엑셀 파일 (한글 파일명) - 제외

## 금지사항 준수 확인
- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 runner/측정 로직 의미 변경 없음
- ✅ no PASS/FAIL 판정: facts-only 유지

## 참고

- 루트에 파일 추가하지 않음 (docs/, reports/ 안에서만 해결)
- 런타임 생성물/임시 파일은 .gitignore로 제외 처리
- PR 본문 파일들은 운영 추적성을 위해 보관
