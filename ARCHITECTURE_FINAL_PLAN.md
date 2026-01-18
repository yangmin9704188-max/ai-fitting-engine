ARCHITECTURE_FINAL_PLAN.md

AI 기반 가상 피팅 엔진 (B2B Core Architecture Specification)

0\. 문서 목적 및 적용 범위

본 문서는 AI 가상 피팅 엔진(B2B)의 아키텍처, 거버넌스, 검증, 배포, 비용
관리에 대한 최종 합의안을 기술 명세 형태로 정의한다.

이 문서는 다음의 \*\*최상위 기준 문서(Constitution)\*\*로 작동한다.

데이터베이스 스키마 설계

R&D 및 MVP 파이프라인

품질 검증 및 실패 분류

버전 관리 및 배포 정책

B2B 계약 시 기술 부속 문서(Technical Appendix)

이후 생성되는 모든 코드, 정책, 문서는 본 문서와의 정합성을 필수 조건으로
한다.

1\. 시스템 목표 및 비목표 1.1 목표

사진 입력 없이 (성별 / 나이 / 키 / 체중 + 선택적 간접 치수) 기반

SMPL-X 파라메트릭 인체 모델을 사용하여

설명 가능하고 재현 가능한 신체 치수를 산출하고

B2B 환경에서 예측 가능한 품질과 비용 구조로 제공한다.

1.2 비목표 (초기 단계 명시적 제외)

범용 고정밀 의류 물리 시뮬레이션(PBD)

전면적 Diffusion 기반 VTON 이미지 생성

고객 수동 피드백에 의존하는 품질 환류

2\. 전체 아키텍처 개요 2.1 트랙 분리 구조

본 시스템은 기능 목적에 따라 두 개의 MVP 트랙으로 분리된다.

구분 MVP-1: Logic Core MVP-2: Visual Trigger 목적 계약·신뢰·설명가능성
시장 설득·시각적 검증 핵심 산출물 치수 벡터, Fit Risk, Uncertainty 렌더
이미지 또는 인터랙티브 뷰 품질 기준 재현성, 수치 안정성 시각적 일관성,
QUAL Gate 초기 우선순위 High Medium (최소 단위)

모든 트랙은 공통 거버넌스 및 품질 게이트를 반드시 통과해야 한다.

3\. R&D Core Layer Specification Layer 1. Semantic Policy Layer 목적

신체 치수의 의미, 단위, 해부학적 불변성을 명시적으로 정의하고 봉인한다.

주요 산출물

치수 정의(랜드마크, 측정 경로)

단위 및 스케일 계약

금지 조건 및 가정

허용 변형(invariance) 규칙

실패 코드

SEM_FAIL: 정의 모호성, 단위 불일치, 불변성 위반

스키마 핵심 필드 (요약)

measurement_id

semantic_version

unit

anatomical_reference

forbidden_conditions\[\]

Layer 2. Differentiable Geometry Layer 목적

Semantic 정의를 SMPL-X 상에서 수치적으로 안정적이고 미분 가능하게
구현한다.

핵심 원칙

개념 레이어는 분리하되

내부 최적화 경로는 Gradient Disconnect가 발생하지 않도록 설계한다.

주요 구성

SMPL-X 기반 치수 계산 경로

수치 최적화(L-BFGS 등)

안정성 가드(dtype/device/범위 제한)

3.2.1 Top-K 신체 치수 민감도 분석 (Sensitivity Summary)

Full Jacobian 계산은 수행하지 않는다.

정의

Shape Parameter 𝛽 β 변화가

주요 신체 치수 𝑘 k개에 미치는 국소 민감도만 산출한다.

목적

디버깅 비용 절감

설명 가능성 확보

B2B 리포트용 수치 근거 제공

산출물

Top-K Sensitivity Mapping

예: "β₃가 +1σ 변화할 경우 Shoulder Width는 +0.28cm 변화"

활용 구분

내부 R&D: 수치 안정성/설계 검증

B2B 리포트: 요약 통계만 노출

실패 코드

GEO_FAIL: 수치 발산, 메시 왜곡, 최적화 실패

Layer 3. Validation Layer 목적

모델의 재현성 및 위험 영역을 사전에 식별한다.

검증 데이터 구성 (3축)

Golden Set

대표 분포

회귀 테스트 기준

Stress / OOD Set

극단 체형, 경계 포즈

실패 표면 탐색

Synthetic GT (Goal-driven Calibration)

MD 기반 합성 데이터

목적: Upper Bound 확인 및 Metric 캘리브레이션

범위 제한:

상의 1종

표준 포즈

제한된 β 샘플링

실패 코드

VAL_FAIL: 재현성 붕괴, 회귀 실패, 분포 드리프트

4\. Quality Gate System Gate 1. GEO Gate (Zero Tolerance)

관통, 자기교차

비매니폴드

스케일 오류

→ 즉시 실패 처리

Gate 2. QUAL Gate (단계적 진화) Phase 0: 초기 캘리브레이션

제한된 인적 검수(샘플링)

Inter-Observer Reliability 측정

Phase 1: Rule-based Stress Test

해부학적 한계 포즈

극단 β 조합

관절 경계 왜곡 테스트

Phase 2 (추후)

데이터 축적 후

경량 생성 모델(VAE 등) 기반 adversarial 고려

실패 코드

QUAL_FAIL: 시각적 일관성 붕괴

Gate 3. PROC Gate (운영 안정성)

API 스키마 계약

응답 시간 SLO

오류 처리 규약

실패 코드

PROC_FAIL

5\. Hybrid Transmission & Delivery Strategy 목적

Egress 비용과 품질 일관성 간의 트레이드오프를 고객 환경에 맞게 선택
가능하도록 한다.

Option A. Server Render

2D 이미지 전송

보안 및 결과 일관성 우선

Option B. Parameter Stream

𝛽 , 𝜃 β,θ + 치수 벡터 전송

클라이언트(Three.js 등) 복원

Egress 최소화

Viewer SDK

Option B 선택 시

표준 렌더 파이프라인 강제

6\. Cost & KPI Management 6.1 KPI 분해 원칙 구분 정의 Pure Inference
Cost GPU/CPU 연산 Fully-loaded Cost Cold Start, Egress, Logging,
Validation 포함 6.2 Local Validation Lane

로컬 4070 Super 활용

오프라인 회귀 테스트

Snapshot 빌드 전용

클라우드 비용 절감 목적

7\. Versioning & Governance 7.1 Immutable Snapshot 원칙

동일 Snapshot = 동일 결과

무버전 패치 금지

변경 시 반드시 신규 버전 발행

7.2 Snapshot 구성 요소

Code hash

Model weights

Config

Runtime container

Dataset versions

7.3 Automation First

Snapshot 발행 자동화

수동 개입 최소화

거버넌스 붕괴 방지

8\. Telemetry & Uncertainty Schema 필수 필드

snapshot_version

semantic_version

geometry_impl_version

uncertainty_score

uncertainty_method (e.g. MC Dropout, Ensemble)

9\. 문서 고정 선언

본 문서는 ARCHITECTURE_FINAL_PLAN.md로 봉인되며, 이후 모든 변경은 버전
증가 및 변경 이력 기록을 통해서만 허용된다.
