# Constitution Change Summary (v0 → v1)

## 목적
본 문서는 기존 README 기반 헌법(v0)을 폐기하고,
Snapshot / Telemetry / Version-driven 거버넌스를 핵심으로 하는
신규 헌법(v1)을 채택한 배경과 구조적 변경점을 요약한다.

---

## 1. 헌법의 역할 재정의

### 기존(v0)
- README 중심의 서술형 문서
- R&D 설명과 운영 규칙이 혼재
- 버전 개념이 암묵적이며 재현성 보장 불명확

### 신규(v1)
- docs/constitution/ 이하 L0/L1 문서로 명확히 분리
- “설명”이 아니라 **통제 기준(Control Plane)** 역할
- 모든 실행, 데이터, 리포트는 Snapshot을 기준으로만 해석

---

## 2. 핵심 구조 변경 요약

### (A) Version First → Snapshot First
- 모든 산출물은 Snapshot ID를 최상위 키로 가짐
- Snapshot = Code + Weights + Schema + Env 의 불변 묶음
- 무버전 패치 금지 원칙 명문화

### (B) Layer 분리 방식 변경
- Semantic / Geometric 개념 분리는 유지
- 내부 구현은 Differentiable Geometry로 통합
- Jacobian 기반 **Top-K Sensitivity Analysis** 도입

### (C) Validation 철학 변경
- 전수 검증 폐기
- Telemetry 기반 샘플링 검증 채택
- GEO / PROC Gate 우선, QUAL Gate는 캘리브레이션 단계로 한정

---

## 3. 데이터 및 스키마 거버넌스

### 기존
- 로그 중심, 비용·품질 추적 불명확

### 신규
- 6 Core Entity 고정
- 모든 Row에 4종 버전 키 강제
- “쿼리 1~2개로 리포트 가능”을 설계 합격 기준으로 채택

---

## 4. 전달 및 비즈니스 구조 변경

- 결과 전달을 단일 방식이 아닌 Hybrid Delivery로 정의
  - Option A: Server Render (이미지)
  - Option B: Parameter Stream (β, θ, 치수)
- 기술 옵션이 아닌 가격 정책과 직접 연동

---

## 5. 상태 선언

- 기존 README 기반 헌법은 DEPRECATED 상태
- 본 문서 이후 작성되는 모든 문서는 Constitution v1을 따른다
- Constitution v1은 Tag 기반으로 봉인된다
