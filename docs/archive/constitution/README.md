---
Level: L0 (Constitution)
Change Rule: ADR 필수 + Tag 필수
Scope: Project-wide
---

# L0 헌법

==================

# Constitution: AI Virtual Fitting Engine (B2B)

## 1. Purpose
본 문서는 AI 기반 B2B 가상 피팅 엔진의 **불변 원칙(Constitution)**을 정의한다.  
이 문서에 명시된 원칙은 구현, 실험, 운영 효율보다 **우선**한다.

## 2. Core Principles

### 2.1 Immutable Snapshot
- 동일한 `snapshot_version`은 동일한 입력에 대해 동일한 결과를 산출해야 한다(허용 오차 내).
- 무버전 패치(Hotfix without version increment)는 금지한다.
- 코드, 가중치, 설정, 데이터 버전 중 하나라도 변경되면 **새 snapshot**을 발행한다.

### 2.2 Mandatory Version Keys
모든 데이터 레코드는 다음 4개 버전 키를 **반드시 포함**해야 한다.
- `snapshot_version`
- `semantic_version`
- `geometry_impl_version`
- `dataset_version`

### 2.3 Minimal Core Schema
시스템은 **6개 Core Entity**로 시작하며, 확장은 명시적 필요가 있을 때만 허용한다.
과도한 초기 스키마 확장은 금지한다.

### 2.4 Telemetry-Driven Design
설계의 합격 조건은 다음과 같다.
- 비용, 성능, 실패율 리포트가 **1~2개의 쿼리**로 산출 가능해야 한다.
- Telemetry는 디버깅 도구가 아니라 **정산·품질·운영의 근간**이다.

### 2.5 Gate Priority Order
Gate의 우선순위는 다음과 같다.
1. PROC (운영 안정성)
2. GEO (기하학적 유효성)
3. QUAL (심미성 – 데이터 수집 단계)

QUAL Gate는 초기에는 차단 장치가 아니라 **자동화를 위한 레이블 수집 단계**로 정의한다.

### 2.6 Hybrid Delivery
결과 전달 방식은 단일 방식으로 고정하지 않는다.
- Server Render (Image)
- Parameter Stream (β, θ, measurements)

고객사 인프라와 가격 정책에 따라 선택 가능해야 한다.

## 3. Document Governance
- 본 문서는 L0 문서이다.
- 변경 시 ADR 기록 및 Git Tag 발행이 필수이다.

## 4. Navigation
- Versioning 상세: `governance_policy.md`
- 스키마 계약: `schema_contract.md`
- Telemetry 규격: `telemetry_schema.md`