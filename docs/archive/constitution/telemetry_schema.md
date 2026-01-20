Level: L1 (Contract)
Change Rule: ADR 권장

================

# Telemetry Schema

## 1. Purpose
Telemetry는 다음 목적을 가진다.
- 비용 정산
- 성능 분석
- 실패 탐지
- B2B SLA 대응

## 2. Mandatory Fields
InferenceRun 기준 필수 필드:
- snapshot_version
- semantic_version
- geometry_impl_version
- dataset_version
- latency_ms (total)
- gpu_ms
- cpu_ms
- egress_bytes
- transmission_mode
- uncertainty_score
- cost_model_version

## 3. Cost Strategy
- Telemetry는 **측정값**을 기록한다.
- 비용 추정치는 cost_model_version 기준으로 재계산 가능해야 한다.
- pure_inference_cost_usd는 옵션 필드로 허용한다.

## 4. Acceptance Queries (Litmus Test)

### 4.1 Snapshot Cost Report
- 평균 latency
- 평균 egress_bytes
- Gate fail rate
- Pure vs Fully-loaded 비용 추정

### 4.2 Quality Risk Report
- uncertainty_score 분포
- QUAL label 수집 현황

본 쿼리가 단순 조인으로 불가능할 경우,
스키마는 **부적합**으로 간주한다.

## 5. Sample Payload
실제 JSON 샘플은 `docs/ops/telemetry_sample.md`에 기록한다.