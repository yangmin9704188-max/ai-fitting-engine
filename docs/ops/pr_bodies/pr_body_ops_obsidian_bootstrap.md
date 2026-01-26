# PR Body: ops(docs): bootstrap Obsidian vault navigation (home + canvas)

## 무엇을 만들었는지

- **Home 노트**: `docs/ops/OBSIDIAN_HOME.md`
  - 프로젝트 탐색의 단일 진입점
  - 5-Layer Navigation (Semantic/Contract/Geometric/Validation/Judgment 링크)
  - Current Baseline (facts-only)
  - Key Registries (round_registry.json, golden_registry.json, coverage_backlog.md 링크)
  - SizeKorea Integration (sizekorea_integration_checklist.md 링크 + 관련 핵심 경로)
  - Ops Cross-cutting (SYNC_HUB.md, CURRENT_STATE.md, .cursorrules, cursor_prompt_header.md 링크)
  - How to Use (30 sec) - 옵시디언에서 클릭 3개로 탐색하는 루틴

- **Setup 가이드**: `docs/ops/OBSIDIAN_SETUP.md`
  - 민영이 Obsidian에서 해야 할 UI 작업 최소 6줄 요약
  - LLM 세션에 첨부할 최소 3파일 섹션

- **Canvas 파일**: `docs/ops/canvas/PROJECT_MAP.canvas`
  - Obsidian Canvas JSON 포맷
  - 9개 노드: Home, 5-Layer 5개, Baseline, SizeKorea Integration, Registries
  - 노드 간 연결 관계 (edges)

- **INDEX.md 업데이트**: `docs/ops/INDEX.md`
  - Obsidian Navigation 섹션 추가 (Home, Setup Guide, Project Canvas 링크)

## 변경 파일

1. `docs/ops/OBSIDIAN_HOME.md` (신규)
2. `docs/ops/OBSIDIAN_SETUP.md` (신규)
3. `docs/ops/canvas/PROJECT_MAP.canvas` (신규)
4. `docs/ops/INDEX.md` (업데이트: Obsidian Navigation 섹션 추가)
5. `docs/ops/pr_bodies/pr_body_ops_obsidian_bootstrap.md` (신규, 이 파일)

## 스모크

### git diff가 Allowed scope 밖 변경이 없는지 확인
```
✅ 모든 변경 파일이 docs/ops/** 범위 내
```

### 생성한 md 링크들이 실제로 존재하는 경로를 가리키는지 확인

**OBSIDIAN_HOME.md 링크 확인**:
- ✅ `docs/semantic/measurement_semantics_v0.md` - 존재 확인
- ✅ `docs/policies/measurements/INDEX.md` - 존재 확인
- ✅ `docs/semantic/evidence/sizekorea_measurement_methods_v0.md` - 존재 확인
- ✅ `docs/contract/UNIT_STANDARD.md` - 존재 확인
- ✅ `core/measurements/` - 디렉토리 존재 확인
- ✅ `reports/validation/` - 디렉토리 존재 확인
- ✅ `docs/judgments/INDEX.md` - 존재 확인
- ✅ `reports/validation/curated_v0_facts_round1.md` - 존재 확인
- ✅ `docs/verification/round_registry.json` - 존재 확인
- ✅ `docs/verification/golden_registry.json` - 존재 확인
- ✅ `docs/verification/coverage_backlog.md` - 존재 확인
- ✅ `docs/ops/sizekorea_integration_checklist.md` - 존재 확인
- ✅ `SYNC_HUB.md` - 존재 확인
- ✅ `docs/sync/CURRENT_STATE.md` - 존재 확인
- ✅ `.cursorrules` - 존재 확인
- ✅ `docs/ops/cursor_prompt_header.md` - 존재 확인

**Canvas 파일 링크 확인**:
- ✅ Canvas JSON 내부 링크들이 상대경로로 올바르게 구성됨

### Canvas 파일이 JSON 파싱 가능한지 확인
```
✅ Python json.tool로 파싱 성공
```

## DoD 체크리스트

- [x] OBSIDIAN_HOME.md 생성 (Start Here, 5-Layer Navigation, Current Baseline, Key Registries, SizeKorea Integration, Ops Cross-cutting, How to Use)
- [x] OBSIDIAN_SETUP.md 생성 (UI 작업 6줄, LLM 세션 첨부 파일 3개)
- [x] PROJECT_MAP.canvas 생성 (9개 노드, 연결 관계)
- [x] INDEX.md 업데이트 (Obsidian Navigation 섹션 추가)
- [x] PR 바디 작성 완료
- [x] 스모크 실행 (변경 범위 확인, 링크 존재 확인, JSON 파싱 확인)
- [x] git diff로 allowed scope 밖 파일 변경 없음 확인
- [ ] CI green 확인 후 머지 (CI red면 머지 금지)

## 롤백 포인트

**커밋 해시**: (커밋 후 업데이트)

**롤백 방법**:
```bash
git revert <commit_hash>
```

또는

```bash
git checkout main
git branch -D ops/obsidian-bootstrap
```
