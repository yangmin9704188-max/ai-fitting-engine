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

### 2026-01-27: Round58 - Coverage expansion from 20 to 50 cases

- **Trigger**: Manual Tier2 backfill to expand manifest coverage from 20 to 50 mesh_path-enabled cases
- **Scope**: `verification/manifests/s1_manifest_v0_round58.json`, geo_v0_s1 lane
- **What changed**: 
  - 30 case_ids: mesh_path null -> set to known-good OBJ files
  - Selected case_ids: `311610124091`, `21_F_5991`, `21_M_4196`, `511607194699`, `21_M_3322`, `20_M_2956`, `311607283902`, `221608221798`, `21_M_3414`, `20_F_2830`, `21_M_3539`, `21_F_3593`, `311609134042`, `521607176332`, `20_F_2354`, `21_M_3451`, `21_F_4497`, `21_F_7273`, `20_F_1995`, `20_F_2507`, `21_M_3835`, `21_F_6241`, `21_F_5324`, `121610203387`, `21_F_4128`, `20_F_1830`, `21_F_5348`, `20_F_1471`, `20_M_3150`, `21_F_6188`
  - OBJ assignment: Round-robin distribution across `6th_20M.obj` (10 cases), `6th_30M.obj` (10 cases), `6th_40M.obj` (10 cases)
- **Rationale**: Coverage scale-up from 20 to 50 cases to observe boundary recovery usage at larger sample size
- **How selected**: First 30 null cases from Round46 manifest, assigned deterministically via round-robin to diverse known-good OBJ files
- **Timestamp**: 2026-01-27

---

### 2026-01-27: Round60 - Coverage expansion from 50 to 100 cases

- **Trigger**: Manual Tier2 backfill to expand manifest coverage from 50 to 100 mesh_path-enabled cases
- **Scope**: `verification/manifests/s1_manifest_v0_round60.json`, geo_v0_s1 lane
- **What changed**: 
  - 50 case_ids: mesh_path null -> set to known-good OBJ files
  - Selected case_ids: `21_F_6996`, `20_F_0882`, `20_F_0494`, `221608111273`, `211608221812`, `21_M_6330`, `21_M_6682`, `511607184667`, `121607270908`, `511610314830`, `21_M_3503`, `20_F_2186`, `321607265203`, `21_M_4168`, `21_M_5628`, `20_F_1028`, `111609232739`, `20_F_0005`, `121609032290`, `21_M_3426`, `421608075746`, `21_M_3572`, `20_M_2058`, `21_F_4515`, `21_M_5500`, `20_F_0179`, `121607180571`, `211608221803`, `20_F_1489`, `21_M_3342`, `21_F_5412`, `321609065463`, `20_M_3194`, `21_F_5205`, `20_F_1006`, `21_M_3366`, `20_F_2527`, `121608282084`, `21_M_6609`, `21_F_3610`, `21_M_3352`, `21_F_7256`, `21_F_3899`, `121607160406`, `121607180584`, `20_F_2636`, `20_M_1147`, `21_F_5680`, `21_M_4193`, `21_F_6999`
  - OBJ assignment: Round-robin distribution across `6th_20M.obj` (17 cases), `6th_30M.obj` (17 cases), `6th_40M.obj` (16 cases)
- **Rationale**: Coverage scale-up from 50 to 100 cases to observe boundary recovery usage rate at larger sample size
- **How selected**: First 50 null cases from Round58 manifest, assigned deterministically via round-robin to diverse known-good OBJ files (balanced distribution)
- **Timestamp**: 2026-01-27

---
