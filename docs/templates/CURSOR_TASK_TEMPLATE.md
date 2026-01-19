# Cursor Task Template

## CONTEXT INPUT

```
[여기에 make ai-prompt 또는 make ai-prompt-json 출력을 붙여넣기]
```

## TASK

[실제 작업 지시를 여기에 작성]

## CONSTRAINTS

- 금지: L0/L1 문서 변경 (docs/constitution/*, schema_contract 등)
- 금지: Sync Hub(CURRENT_STATE)의 의미 해석/요약/설명 추가
- 금지: 판단/이유/추천 로직 추가
- 금지: CURRENT_STATE 내용 요약/재정의
- 금지: Sync Hub 구조에 새로운 문장/서술 추가

## BRANCH NAMING

- 기본: [브랜치명]
- 충돌 시: [브랜치명]-2, [브랜치명]-3, ...
- 금지: 날짜/임의문자열/사용자명

## DONE CHECKLIST

- [ ] 코드 구현 완료
- [ ] 로컬 테스트 완료
- [ ] git add 완료
- [ ] git commit 완료 (메시지: [커밋 메시지])
- [ ] git push 완료
- [ ] PR 생성 완료
- [ ] PR 링크: [PR 링크]
- [ ] CI Guard 포함 모든 Checks PASS 확인
- [ ] Checks run 링크 또는 run id: [링크 또는 ID]
- [ ] 변경 파일 리스트:
  - [파일1]
  - [파일2]
