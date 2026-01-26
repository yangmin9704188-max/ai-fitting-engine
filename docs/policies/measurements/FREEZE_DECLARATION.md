---
title: "Measurement Semantic + Interface Freeze"
version: "v1.0.0"
status: "legacy"
created_date: "2026-01-21"
frozen_commit_sha: "9731aa4"
author: "Yang"
---

> **⚠️ LEGACY DOCUMENT**  
> **status**: legacy  
> **superseded_by**: [docs/policies/measurements/INDEX.md](INDEX.md)  
> **reason**: pre-sizekorea definition; anchors updated  
> **note**: do not treat as SoT

---

# Measurement Semantic + Interface Freeze v1.0.0

> Doc Type: Contract  
> Layer: Meta

---

## 1. Summary

본 선언은 측정 관련 Semantic 및 Interface 문서들이 정의/계약의 단일 진실원이며, 이 시점 이후에는 "무엇을 재는가"와 "단위/인터페이스"를 다시 의심하지 않음을 의미한다.

---

## 2. Scope

### In Scope

- 측정 의미(Semantic) 정의 고정
- 인터페이스 규약 고정
- 변경 제어 규칙

### Out of Scope

- Geometric 구현(알고리즘), 성능, 정확도, 품질 판단
- PASS/FAIL 판단 (Report에서만 수행)

---

## 3. Invariants (Normative)

### 3.1 MUST (필수)

- 아래 Frozen Artifacts는 변경 제어 규칙에 따라만 수정 가능
- 변경 시 새 버전 문서 + 새 Freeze + 새 Tag 필수

### 3.2 MUST NOT (금지)

- 기존 Freeze 선언의 무단 변경 금지
- 의미/계약 변경 시 기존 Freeze 무시 금지

---

## 4. Frozen Artifacts

1. `docs/policies/measurements/README.md`  
   - Body Measurement Meta-Policy (Semantic Invariants)

2. `docs/policies/measurements/BUST.md`  
3. `docs/policies/measurements/WAIST.md`  
4. `docs/policies/measurements/HIP.md`  
   - Item Contracts (Selection Rules only)

5. `docs/policies/measurements/INTERFACE_TO_GEOMETRIC.md`  
   - Semantic → Geometric Minimal Interface Contract

---

## 5. Prohibitions (Explicit)

- Geometric 구현(알고리즘), 성능, 정확도, 품질 판단
- PASS/FAIL 판단 (Report에서만 수행)

---

## 6. Change Notes

v1.0.0:
- Measurement Semantic + Interface Freeze 초기 선언

---

## 7. Freeze Notes

**Frozen Artifacts:**
- `docs/policies/measurements/README.md`
- `docs/policies/measurements/BUST.md`
- `docs/policies/measurements/WAIST.md`
- `docs/policies/measurements/HIP.md`
- `docs/policies/measurements/INTERFACE_TO_GEOMETRIC.md`

**Change Control:**
- 위 문서들의 변경은 "의미/계약 변경"에 해당한다
- 변경이 필요할 경우:
  - 기존 Freeze는 유지하며,
  - **새 버전 문서 + 새 Freeze + 새 Tag**로만 진행한다

**Approved by:** Project Owner (Human)  
**Date:** 2026-01-21 (KST)
