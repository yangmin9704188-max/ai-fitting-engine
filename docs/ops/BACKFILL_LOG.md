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

### 2026-01-27: Round46 - Coverage expansion from 5 to 20 cases

- **Trigger**: Manual Tier2 backfill to expand manifest coverage from 5 to 20 mesh_path-enabled cases
- **Scope**: `verification/manifests/s1_manifest_v0_round46.json`, geo_v0_s1 lane
- **What changed**: 
  - 15 case_ids: mesh_path null -> set to known-good OBJ files
  - Selected case_ids: `211608191617`, `21_F_6338`, `121607180555`, `21_F_5759`, `20_F_3012`, `20_M_2444`, `20_M_0969`, `111609012195`, `20_M_0356`, `21_F_3588`, `20_F_0723`, `20_M_3296`, `21_F_6076`, `21_F_6854`, `20_F_3016`
  - OBJ assignment: 5 cases each for `6th_20M.obj`, `6th_30M.obj`, `6th_40M.obj`
- **Rationale**: Coverage scale-up from 5 to 20 cases for better statistical validation
- **How selected**: First 15 null cases from manifest, assigned to diverse known-good OBJ files (proxy meshes)
- **Timestamp**: 2026-01-27

---
