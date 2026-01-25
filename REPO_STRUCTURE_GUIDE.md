# Repository Structure Guide

## 루트에 남겨야 하는 파일

다음 파일들은 루트에 유지합니다:

- `README.md`: 프로젝트 개요 및 빠른 시작 가이드
- `SYNC_HUB.md`: 실시간 마일스톤 및 릴리즈 상태
- `SYNC_HUB_FILE_INDEX.md`: LLM 학습/탐색용 파일 인덱스 (절대 이동 금지)
- `DB_GUIDE.md`: 데이터베이스 가이드
- `Makefile`: 빌드/실행 명령어
- `.cursorrules`: Cursor AI 규칙
- `triggers.json`: 트리거 설정

## 문서 구조

### docs/ops/
운영 문서 및 템플릿:
- `cursor_prompt_header.md`: Cursor 프롬프트 헤더 표준화
- `baselines.json`: Lane별 baseline 설정
- `pr_bodies/`: PR 본문 초안 보관

### docs/semantic/
의미 정의 문서:
- `measurement_semantics_v0.md`
- `pose_normalization.md`
- `legacy_handling.md`

### docs/verification/
검증 정책 및 템플릿:
- `round_charter_template.md`: 라운드 헌장 템플릿
- `round_ops_v0.md`: 라운드 운영 가이드
- `coverage_backlog.md`: Coverage 백로그
- `curated_v0_gate_draft_v0.md`: Gate 초안

### docs/policies/
정책 문서:
- `measurements/`: 측정 정책
- `apose_normalization/`: A-Pose 정규화 정책

## 산출물 구조

### reports/validation/
검증 리포트:
- `round_registry.json`: 라운드 레지스트리
- `*.md`: 검증 리포트 파일들

### verification/runs/
실행 산출물 (커밋하지 않음):
- `facts/`: Facts-only runner 산출물
- `*/KPI.md`, `*/KPI_DIFF.md`: KPI 및 diff 리포트

## 원칙

- **루트에 임시 파일 쌓지 않기**: PR 본문 초안, 임시 문서는 모두 `docs/` 하위로 이동
- **SYNC_HUB_FILE_INDEX.md는 루트 유지**: LLM 학습/탐색용이므로 절대 이동 금지
- **코드 로직은 core/, pipelines/, verification/, tests/에만**: 이 폴더들은 이동/변경 금지
