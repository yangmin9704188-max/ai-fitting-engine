---
title: "..."            # DB: policies.name
version: "vX.Y"         # DB: policies.version
status: "draft|candidate|frozen|archived|deprecated"
created_date: "YYYY-MM-DD"
frozen_commit_sha: "abcdef0"   # status=frozen일 때 필수, 그 외 생략 가능

author: "Yang"
latest_report: "AN-v11-R1"
---

# <Policy Title> <version>

## 1. Summary
- (이 정책이 **무엇을 위한 정책인지** 1~3줄 요약)

---

## 2. Goal
- **Primary Objective**
  - (이 정책이 최우선으로 보장하려는 것)
- **Constraints**
  - (비용, 성능, 안정성, 재현성 등 제약 조건)

---

## 3. Scope
- **In Scope**
  - (이 정책이 적용되는 파이프라인/단계/환경)
- **Out of Scope**
  - (명시적으로 다루지 않는 것)

---

## 4. Invariants / Rules
> 이 정책이 **항상 강제하는 불변 규칙**

- Coordinate system:
- Axis convention:
- dtype / device:
- Units / scale:
- 기타 강제 규약:

---

## 5. Gate Definitions (Verification Gates)
> 이 정책이 **통과되어야만 유효하다고 판단되는 검증 게이트 정의**
>  
> ⚠️ Gate의 *정의*만 포함한다.  
> ⚠️ Gate의 *결과(PASS/FAIL)* 는 Report에서 다룬다.

### Gate G1: <Gate Name>
- **Intent**
  - (이 Gate가 존재하는 이유)
- **Check**
  - (무엇을 어떻게 검증하는가)
- **Pass Criteria**
  - (어떤 상태여야 PASS인가)
- **Fail Criteria**
  - (어떤 경우 FAIL로 간주하는가)

### Gate G2: <Gate Name>
- **Intent**
- **Check**
- **Pass Criteria**
- **Fail Criteria**

*(필요한 만큼 추가)*

---

## 6. Acceptance Criteria (Freeze Decision)
> 이 정책이 **Candidate → Frozen** 으로 승격되기 위한 조건

- 모든 Gate(G1~Gn)가 **PASS** 일 것
- 재현성 테스트에서 결과 변동이 허용 범위 이내일 것
- downstream 정책에 부정적 영향이 없을 것
- 관련 Report가 최소 1개 이상 존재할 것

---

## 7. Change Notes
- vX.Y:
  - (이 버전이 왜 생겼는지, 무엇이 바뀌었는지 2~5줄)