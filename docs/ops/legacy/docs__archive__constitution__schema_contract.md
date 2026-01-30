Level: L1 (Contract)
Change Rule: ADR 권장 + Migration Note 필수

===========================

# Schema Contract

## 1. Core Entities (Fixed = 6)

1. SnapshotRelease
2. PolicySemantic
3. GeometryImplementation
4. DatasetVersion
5. InferenceRun
6. GateResult

## 2. Mandatory Version Keys
모든 엔터티는 아래 키를 반드시 포함해야 한다.
- snapshot_version
- semantic_version
- geometry_impl_version
- dataset_version

## 3. InferenceRun
- 단일 추론 실행의 **원본 기록**
- 불변 데이터
- 포함 필드 예:
  - input_summary
  - gpu_ms / cpu_ms
  - egress_bytes
  - transmission_mode
  - uncertainty_score
  - cost_model_version
  - snapshot_version (FK)

## 4. GateResult
- InferenceRun에 대한 해석 결과
- Gate 로직 변경 시 재생성 가능
- Gate 종류:
  - PROC
  - GEO
  - QUAL

## 5. QUAL Data Collection
QUAL Gate는 다음 필드를 포함할 수 있다.
- qual_label
- qual_labeler
- qual_label_confidence
- qual_proxy_scores (optional)

## 6. Extension Policy
- Core Entity 추가는 L1 변경으로 간주한다.
- 반드시 ADR로 근거를 남긴다.