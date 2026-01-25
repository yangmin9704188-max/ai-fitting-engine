# ops: add round charter, gate draft, and facts KPI summarizer

## 목적
오늘 세션에서 드러난 개선 포인트(라운드 목표 흔들림/분석 비용/역할 혼선)를 과도한 거버넌스 없이 문서/템플릿/얕은 자동화로 흡수합니다.

## 변경 사항

### A) Round Charter 템플릿 추가
- `docs/verification/round_charter_template.md`: 라운드별 목표와 DOD를 명확히 정의하는 템플릿

### B) Cursor Prompt Header 표준화 문서 추가
- `docs/ops/cursor_prompt_header.md: Cursor와 Human의 역할 분리 및 금지 사항 명시

### C) curated_v0 facts 기반 Gate Draft 추가
- `docs/verification/curated_v0_gate_draft_v0.md: PASS/FAIL이 아닌 "facts 신호 → 다음 행동" 맵핑 초안

### D) facts 결과 KPI Header 생성 유틸 추가
- `tools/summarize_facts_kpi.py: facts_summary.json에서 KPI 헤더를 생성하는 스크립트

## 스모크 테스트

```bash
# KPI summarizer 테스트 (예시 경로)
py tools/summarize_facts_kpi.py verification/runs/facts/curated_v0/round20_20260125_120000/facts_summary.json
```

## 원칙 준수
- ✅ 과도한 리팩터링 금지: 기존 파이프라인/러너 구조 변경 없음
- ✅ Semantic 재해석/정책 변경 금지: 운영/문서/요약만 추가
- ✅ 결과는 PR 1개로 끝
