# Cursor Prompt Header 표준화

## Role Split

### Cursor does
- 코드 수정/테스트 실행/PR 생성/merge

### Human does
- 명령 실행 결과 붙여넣기/A-B 결정/최종 승인

## Output contract
- 수정/생성 파일 목록

## Forbidden actions
- semantic 재해석
- 자동 대체
- 무단 리팩터링
- 경로 임의 변경

## 기본 규칙
**PR/merge까지 수행**을 기본 규칙으로 명시합니다.
