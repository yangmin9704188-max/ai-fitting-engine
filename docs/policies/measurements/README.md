---
title: "Body Measurement Meta-Policy"
version: "v1.3"
status: "frozen"
created_date: "2026-01-16"
frozen_commit_sha: "9731aa4"
author: "Yang"
---

# Body Measurement Meta-Policy v1.3

> Doc Type: Contract  
> Layer: Semantic

---

## 1. Summary

본 계약은 모든 신체 둘레 측정의 의미(Semantic) 정의를 고정한다.  
이 계약이 깨질 경우 측정 결과의 일관성과 재현성이 보장되지 않으며, Semantic Layer와 Geometric Layer 간 인터페이스 혼란이 발생한다.

---

## 2. Scope

### In Scope

- 측정 의미(Semantic) 정의
- 둘레 측정의 개념적 정의
- 측정 의미의 자세 독립성
- 좌표계 해석 위임 규칙

### Out of Scope

- 구현 세부 (특정 알고리즘, 정점 인덱스, 파라미터)
- 정확도 비교
- 성능
- Gate, PASS/FAIL 판단
- 서비스 레이어

---

## 3. Invariants (Normative)

### 3.1 MUST (필수)

- **둘레의 정의**: 모든 둘레 측정은 인체 장축에 직교하는 단면상의 폐곡선(Closed curve) 길이로 정의한다.
- **의미 독립성**: 측정의 의미는 인체의 자세(A-pose, T-pose 등)나 특정 메시의 토폴로지에 의존하지 않는다.

### 3.2 MUST NOT (금지)

- 특정 정점 인덱스(Vertex Index) 언급 금지
- SMPL-X 파라미터($\beta$) 언급 금지
- 특정 기하학 알고리즘 언급 금지

### 3.3 SHOULD (권장)

- **좌표계 위임**: "수평" 및 "수직"에 대한 물리적 좌표계 해석은 Geometric Layer의 구현체로 위임한다.

---

## 4. Interface / Schema (If Applicable)

N/A (Semantic-only 계약)

---

## 5. Terminology

- **Cross-section**: 인체 장축에 수직인 절단면
- **Closed Curve**: 단면 상에서 인체 표면을 따라 형성되는 닫힌 경로

---

## 6. Change Notes

v1.3:
- Semantic Layer 정의 명확화
- 좌표계 위임 규칙 추가

---

## 7. Freeze Notes

**Frozen Artifacts:**
- 본 문서 (Body Measurement Meta-Policy v1.3)
- 관련 측정 항목 계약 (BUST, WAIST, HIP)

**Change Control:**
- 변경은 새 버전 + 새 Freeze + 새 Tag로만 가능

---

## 8. Measurement Policy Documents Index

### Chest Family (가슴 계열)

**Standard (표준):**
- L1 Semantic: [SEMANTIC_DEFINITION_UNDERBUST_VNEXT.md](SEMANTIC_DEFINITION_UNDERBUST_VNEXT.md)
- L1 Semantic: [SEMANTIC_DEFINITION_BUST_VNEXT.md](SEMANTIC_DEFINITION_BUST_VNEXT.md)
- L2 Contract: [CONTRACT_INTERFACE_BUST_UNDERBUST_V0.md](CONTRACT_INTERFACE_BUST_UNDERBUST_V0.md)

**Deprecated (레거시):**
- ⚠️ L1 Semantic: [SEMANTIC_DEFINITION_CHEST_VNEXT.md](SEMANTIC_DEFINITION_CHEST_VNEXT.md) - Deprecated (UNDERBUST/BUST로 전환)
- ⚠️ L2 Contract: [CONTRACT_INTERFACE_CHEST_V0.md](CONTRACT_INTERFACE_CHEST_V0.md) - Deprecated (UNDERBUST/BUST로 전환)

### Other Measurements

- L1 Semantic: [SEMANTIC_DEFINITION_CIRCUMFERENCE_VNEXT.md](SEMANTIC_DEFINITION_CIRCUMFERENCE_VNEXT.md)
- L1 Semantic: [SEMANTIC_DEFINITION_HIP_VNEXT.md.txt](SEMANTIC_DEFINITION_HIP_VNEXT.md.txt)
- L1 Semantic: [SEMANTIC_DEFINITION_THIGH_VNEXT.md.txt](SEMANTIC_DEFINITION_THIGH_VNEXT.md.txt)
- L2 Contract: [CONTRACT_INTERFACE_CIRCUMFERENCE_V0.md](CONTRACT_INTERFACE_CIRCUMFERENCE_V0.md)
- L2 Contract: [CONTRACT_INTERFACE_HIP_V0.md.txt](CONTRACT_INTERFACE_HIP_V0.md.txt)
- L2 Contract: [CONTRACT_INTERFACE_THIGH_V0.md.txt](CONTRACT_INTERFACE_THIGH_V0.md.txt)
