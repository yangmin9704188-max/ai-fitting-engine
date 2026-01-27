# Backfill Policy

## Tier 정의

### Tier 0: No Backfill
- 변경사항이 기존 골든셋과 호환되는 경우
- KPI_DIFF가 임계치 이내인 경우

### Tier 1: Partial Backfill
- 일부 케이스만 재생성이 필요한 경우
- 선택적 백필 수행

### Tier 2: Full Back-fill
- 전체 골든셋 재생성이 필요한 경우
- **Tier2 실행 시 반드시 BACKFILL_LOG.md에 기록 의무**

## Tier2 트리거 예시

다음과 같은 경우 Tier2(Full Back-fill)가 트리거됩니다:

1. **Contract 변경으로 동일 제품성이 깨지는 경우**
   - 스키마 변경으로 인한 호환성 깨짐
   - 측정 로직 변경으로 인한 결과 차이

2. **KPI_DIFF 임계치 초과**
   - 주요 KPI 지표가 임계치를 초과하는 경우

3. **Failure taxonomy 의미 변경 수준의 로직 변화**
   - 실패 분류 체계가 변경되는 경우
   - 로직 변경으로 인한 결과 해석 변화

## 자동 백필 구현

**참고**: "자동 백필" 구현은 이번 PR에서 하지 않습니다. 정책만 고정합니다.

## 기록 의무

Tier2(Full Back-fill) 실행 시 반드시 [`BACKFILL_LOG.md`](BACKFILL_LOG.md)에 기록해야 합니다.
