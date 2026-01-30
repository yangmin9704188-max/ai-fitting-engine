# SSOT_PACK_v1
STATUS: CANONICAL (Evidence-first)
Last updated: 2026-01-30
Owner: Human (민영)

> 선언: **이제부터 프로젝트의 모든 판단 근거는 SSoT Pack v1에 있다.**
> 이 문서에 명시되지 않은 문서는 근거가 될 수 없으며, 필요 시 LEGACY로 취급한다.

---

## 0) Purpose

SSoT Pack v1은 AI Fitting Engine 프로젝트에서 “무엇이 근거 문서인지”를 고정한다.
향후 어떤 정리/이동/자동화/대시보드 재결선 작업도 반드시 본 Pack을 기준으로 한다.

---

## 1) Canonical Documents (SSoT Pack v1 = 5 docs)

아래 5개 문서는 “모듈 계획/언락/페이즈”의 단일 정본이다.

| ID | Document | Canonical Path | Role |
|---:|---|---|---|
| S1 | Body Module Plan v1 | docs/plans/Body_Module_Plan_v1.md | body 모듈 목표/산출물/범위 |
| S2 | Fitting Module Plan v1 | docs/plans/fitting_module_plan_v1.md | fitting 모듈 목표/산출물/범위 |
| S3 | Garment Product Contract v0.9-revC | docs/plans/garment_Product_Contract_v0.9-revC.md | garment 입력/계약/산출물 |
| S4 | Unlock Conditions u1/u2 | docs/plans/unlock_conditions_u1_u2.md | 모듈 간 언락 조건(DoD 기반) |
| S5 | Phase Plan (Unlock-driven) | docs/plans/phase_plan_unlock_driven.md | 페이즈 구성(언락 기반 병렬) |

Notes:
- 위 경로가 아직 존재하지 않거나 파일명이 다르면, **Round 2~4 정리에서 해당 경로로 귀속**한다.
- 경로 변경(이동)은 가능하나, 이동 후에는 본 표의 Canonical Path만 갱신한다(본문 중복 금지).

---

## 2) What is NOT SSoT (Non-canonical)

아래 범주의 문서는 “근거”로 사용할 수 없다:
- 과거 플랜/초안/리포트/실험 메모(레거시)
- 라운드 결과 문서(docs/ops/rounds/...) 자체는 사실 기록이며 “계획/정의의 근거”가 아니다
- 어떤 문서가 SSoT로 승격되어야 한다면, 본 문서(SSOT_PACK_v1) 표에 ID로 등재되어야 한다

---

## 3) SYNC_HUB / CURRENT_STATE의 지위(운영 헌법/변경 로그)

SSoT Pack v1(계획/언락/페이즈)과 별개로, 아래 2개 문서는 “운영 레이어”의 정본으로 유지한다.

### 3.1 SYNC_HUB.md (Ops Constitution)
- 역할: 운영 트리거/업데이트 분기 규칙, facts-only 원칙, 변경 분류(T1~T7) 등 “운영 헌법”
- 지위: **운영 규칙의 정본(CANONICAL)**  
- 주의: SYNC_HUB는 모듈 플랜(SSoT Pack)을 “대체”하지 않는다.  
  (즉, 계획/언락/페이즈의 내용은 SSoT Pack이 정본)

### 3.2 CURRENT_STATE.md (State Log)
- 역할: 현재 상태/최근 변경/관측(facts) 로그 기록
- 지위: **변경 로그의 정본(CANONICAL)**  
- 주의: CURRENT_STATE는 “근거 문서(플랜)”가 아니라 “현황 기록”이다.

---

## 4) Conflict Resolution Order (충돌 시 우선순위)

문서 간 내용이 충돌하거나 근거가 애매할 때는 아래 순서로 판단한다:

1) `contracts/` (기계 파싱 가능한 계약/스키마가 최우선)
2) `docs/ssot/SSOT_PACK_v1.md` + §1의 5개 문서(S1~S5)
3) `docs/ops/DIRECTORY_CHARTER_v1.md` (구조/배치 규칙)
4) `docs/ops/SYNC_HUB.md` (운영 헌법: 트리거/규율)
5) `docs/ops/CURRENT_STATE.md` (현황 기록: facts-only)

---

## 5) Legacy Handling Pointer

- SSoT Pack v1에 포함되지 않은 문서는 `docs/legacy/`로 이동될 수 있다.
- 이동 시 `docs/legacy/LEGACY_INDEX.md`에 “어떤 SSoT 문서로 대체되었는지”를 1줄로 기록한다.
- 레거시 문서는 상단에 `STATUS: LEGACY (SUPERSEDED)` 스탬프를 둔다.

---
End of SSOT_PACK_v1
