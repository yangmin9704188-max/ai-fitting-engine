# Backfill Log

이 문서는 Tier2(Full Back-fill) 실행 기록을 append-only로 관리합니다.

**Tier2 실행 시 반드시 기록 의무**

## 로그 템플릿

| Date | Trigger | Scope | Before/After | Deprecated Golden Set | New Golden Set |
|------|---------|-------|--------------|----------------------|----------------|
| YYYY-MM-DD | Tier2 사유 | 모듈/데이터셋/기간 | KPI_DIFF/Top reasons 변화 | 폐기된 골든셋 freeze 문서/커밋 해시 | 새 기준 커밋 해시/문서 |

## 기록 예시

### 2026-01-27: Contract 변경으로 인한 Full Back-fill

- **Trigger**: Contract 변경으로 동일 제품성이 깨짐
- **Scope**: `modules/body/measurements/`, 전체 데이터셋
- **Before/After**: 
  - Before: KPI_DIFF = 0.15
  - After: KPI_DIFF = 0.02
  - Top reasons 변화: circumference 계산 로직 변경
- **Deprecated Golden Set**: 
  - 문서: `docs/verification/golden_s0_freeze_v0.md`
  - 커밋: `cc15544bc26b244d28463568d1d32660679979d3`
- **New Golden Set**: 
  - 커밋: `[새 기준 커밋 해시]`
  - 문서: `[새 기준 문서 경로]`

---
