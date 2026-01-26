# Measurements Policies Index (SoT)

**목적**: SizeKorea 정의/기준점/측정방법이 유입된 상태에서 measurements 정책 문서의 단일 진입점(SoT)을 제공합니다.

**원칙**: 
- 현재 유효한 문서는 Current SoT 섹션에서 확인
- Legacy 문서는 참조용으로만 유지 (SoT 아님)
- SizeKorea Evidence는 모든 측정 정의의 기준점(anchor)으로 사용

---

## Current SoT (현재 유효한 문서)

| Key | Status | Current Doc | SizeKorea Evidence | Notes |
|-----|--------|-------------|-------------------|-------|
| Semantic Layer (All Keys) | SoT | [docs/semantic/measurement_semantics_v0.md](../../semantic/measurement_semantics_v0.md) | [docs/semantic/evidence/sizekorea_measurement_methods_v0.md](../../semantic/evidence/sizekorea_measurement_methods_v0.md) | 45개 표준 키 의미론 봉인 |
| BUST | SoT | [SEMANTIC_DEFINITION_BUST_VNEXT.md](SEMANTIC_DEFINITION_BUST_VNEXT.md) | [SizeKorea Evidence - bust_circ_m](../../semantic/evidence/sizekorea_measurement_methods_v0.md#bust_circ_m) | - |
| UNDERBUST | SoT | [SEMANTIC_DEFINITION_UNDERBUST_VNEXT.md](SEMANTIC_DEFINITION_UNDERBUST_VNEXT.md) | [SizeKorea Evidence - underbust_circ_m](../../semantic/evidence/sizekorea_measurement_methods_v0.md#underbust_circ_m) | - |
| CHEST (Legacy) | Deprecated | [SEMANTIC_DEFINITION_CHEST_VNEXT.md](SEMANTIC_DEFINITION_CHEST_VNEXT.md) | - | UNDERBUST/BUST로 전환, REF로만 유지 |
| CIRCUMFERENCE | SoT | [SEMANTIC_DEFINITION_CIRCUMFERENCE_VNEXT.md](SEMANTIC_DEFINITION_CIRCUMFERENCE_VNEXT.md) | [SizeKorea Evidence](../../semantic/evidence/sizekorea_measurement_methods_v0.md) | 둘레 측정 패밀리 |
| HIP | SoT | [SEMANTIC_DEFINITION_HIP_VNEXT.md.txt](SEMANTIC_DEFINITION_HIP_VNEXT.md.txt) | [SizeKorea Evidence - hip_circ_m](../../semantic/evidence/sizekorea_measurement_methods_v0.md#hip_circ_m) | - |
| THIGH | SoT | [SEMANTIC_DEFINITION_THIGH_VNEXT.md.txt](SEMANTIC_DEFINITION_THIGH_VNEXT.md.txt) | [SizeKorea Evidence - thigh_circ_m](../../semantic/evidence/sizekorea_measurement_methods_v0.md#thigh_circ_m) | - |
| BUST/UNDERBUST Contract | SoT | [CONTRACT_INTERFACE_BUST_UNDERBUST_V0.md](CONTRACT_INTERFACE_BUST_UNDERBUST_V0.md) | - | L2 Contract |
| CHEST Contract (Legacy) | Deprecated | [CONTRACT_INTERFACE_CHEST_V0.md](CONTRACT_INTERFACE_CHEST_V0.md) | - | UNDERBUST/BUST로 전환 |
| CIRCUMFERENCE Contract | SoT | [CONTRACT_INTERFACE_CIRCUMFERENCE_V0.md](CONTRACT_INTERFACE_CIRCUMFERENCE_V0.md) | - | L2 Contract |
| HIP Contract | SoT | [CONTRACT_INTERFACE_HIP_V0.md.txt](CONTRACT_INTERFACE_HIP_V0.md.txt) | - | L2 Contract |
| THIGH Contract | SoT | [CONTRACT_INTERFACE_THIGH_V0.md.txt](CONTRACT_INTERFACE_THIGH_V0.md.txt) | - | L2 Contract |
| BUST/UNDERBUST Geometric | SoT | [GEOMETRIC_DESIGN_BUST_UNDERBUST_V0.md](GEOMETRIC_DESIGN_BUST_UNDERBUST_V0.md) | - | L3 Geometric |
| CHEST Geometric | SoT | [GEOMETRIC_DESIGN_CHEST_V0.md](GEOMETRIC_DESIGN_CHEST_V0.md) | - | L3 Geometric (legacy reference) |
| HIP Geometric | SoT | [GEOMETRIC_DESIGN_HIP_V0.md.txt](GEOMETRIC_DESIGN_HIP_V0.md.txt) | - | L3 Geometric |
| THIGH Geometric | SoT | [GEOMETRIC_DESIGN_THIGH_V0.md.txt](GEOMETRIC_DESIGN_THIGH_V0.md.txt) | - | L3 Geometric |
| BUST/UNDERBUST Validation | SoT | [VALIDATION_FRAME_BUST_UNDERBUST_V0.md](VALIDATION_FRAME_BUST_UNDERBUST_V0.md) | - | L4 Validation |
| CHEST Validation | SoT | [VALIDATION_FRAME_CHEST_V0.md](VALIDATION_FRAME_CHEST_V0.md) | - | L4 Validation (legacy reference) |
| CIRCUMFERENCE Validation | SoT | [VALIDATION_FRAME_CIRCUMFERENCE_V0.md](VALIDATION_FRAME_CIRCUMFERENCE_V0.md) | - | L4 Validation |
| HIP Validation | SoT | [VALIDATION_FRAME_HIP_V0.md](VALIDATION_FRAME_HIP_V0.md) | - | L4 Validation |
| THIGH Validation | SoT | [VALIDATION_FRAME_THIGH_V0.md](VALIDATION_FRAME_THIGH_V0.md) | - | L4 Validation |

---

## SizeKorea Evidence/Anchors

**Evidence 문서**: [docs/semantic/evidence/sizekorea_measurement_methods_v0.md](../../semantic/evidence/sizekorea_measurement_methods_v0.md)

모든 측정 정의는 SizeKorea Evidence 문서를 기준점(anchor)으로 참조합니다.

---

## Legacy (구 문서 목록)

| Legacy Doc | Superseded By | Reason | Notes |
|------------|---------------|--------|-------|
| [bust.md](bust.md) | [SEMANTIC_DEFINITION_BUST_VNEXT.md](SEMANTIC_DEFINITION_BUST_VNEXT.md) | pre-sizekorea definition; anchors updated | v1.0 → vNext |
| [hip.md](hip.md) | [SEMANTIC_DEFINITION_HIP_VNEXT.md.txt](SEMANTIC_DEFINITION_HIP_VNEXT.md.txt) | pre-sizekorea definition; anchors updated | v1.0 → vNext |
| [waist.md](waist.md) | [docs/semantic/measurement_semantics_v0.md](../../semantic/measurement_semantics_v0.md) | pre-sizekorea definition; anchors updated | v1.0 → v0 (통합) |
| [README.md](README.md) | [docs/semantic/measurement_semantics_v0.md](../../semantic/measurement_semantics_v0.md) | pre-sizekorea definition; anchors updated | Meta-Policy v1.3 → v0 (통합) |
| [FREEZE_DECLARATION.md](FREEZE_DECLARATION.md) | [docs/semantic/measurement_semantics_v0.md](../../semantic/measurement_semantics_v0.md) | pre-sizekorea definition; anchors updated | v1.0.0 → v0 (통합) |

**주의**: Legacy 문서는 참조용으로만 유지되며, SoT로 사용하지 않습니다.

---

## TODO (아직 재작성 안된 키 목록)

현재 `docs/semantic/measurement_semantics_v0.md`에 45개 표준 키가 정의되어 있으며, 개별 SEMANTIC_DEFINITION 문서는 다음 키들에 대해 아직 생성되지 않았습니다:

- WAIST (현재 measurement_semantics_v0.md에 통합 정의)
- 기타 45개 키 중 SEMANTIC_DEFINITION_* 문서가 없는 항목들

**참고**: 모든 키의 의미론은 `docs/semantic/measurement_semantics_v0.md`에서 확인 가능합니다.
