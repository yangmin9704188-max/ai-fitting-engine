# ops: update .cursorrules project-wide rules

## 변경 파일
- `.cursorrules`

## 목적
project-wide rules 정렬(역할 분담/round charter/KPI header/금지사항)

## 주요 변경 내용
- Prime Directive 추가: 작업 범위 준수 및 Semantic 재해석 금지
- Mandatory Pre-Read: cursor_prompt_header.md, round charter, KPI header 사용 규칙
- Facts KPI Header Rule: facts-only runner 리포트에 한정하여 KPI Header 포함
- PR/Merge Rule: 기본값으로 PR 생성 + merge까지 수행
- Strict Safety Rules: NO DELETIONS, NO MOVES, NO REFACTORING, NO SEMANTIC DRIFT, NO SMART GUESSING
- Conditional Scope Lock: 문서/운영/DB 최소화 PR일 때 추가 제약

## 금지사항 준수 확인
- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code changes: 코드 로직 변경 없음 (규칙/운영 문서 업데이트만)

## 재현
N/A (규칙 파일 업데이트만)
