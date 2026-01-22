---
Canonical: SYNC_HUB.md
Key dictionary: docs/contract/standard_keys.md
related_measurement_key ENUM: UNDERBUST|BUST|WAIST|HIP|THIGH|CIRCUMFERENCE|CHEST_LEGACY
Guard ref: .github/workflows/guard-sync-state.yml
Rule: This header block is canonical and must not be modified without explicit architect approval.
---

1. Project Overview \& Identity

Project: AI Fitting Engine

Mission: 사진 없이 신체 치수만으로 설명 가능하고 재현 가능한 3D 체형($\\beta$) 생성 엔진 구축

Core Principle: 5-Layer R\&D 파이프라인(Semantic–Contract–Geometric–Validation–Judgment)의 엄격한 분리 및 지적 정직성(GIGO) 유지

2. Milestone Achievements (누적 성과)

Current Milestone: MVP-1 Measurement Frame Stabilization v0

Accomplishments:

5-Layer R\&D 프레임워크 정립 및 운영 정합성 체계 구축

4개 Measurement(Circumference, CHEST(legacy), HIP, THIGH) v0 완주 및 봉인(프레임 관점)

가슴 계열 치수 이원화 정책 확정:

UNDERBUST = 구조(흉곽)

BUST = 볼륨(젖가슴 최대)

브라 사이즈 입력 매핑 정책 확정:

입력 "75A" → UNDERBUST(band) + Δ(cup)로 BUST 산출

Cup Delta Table(MVP): cup당 +2.5cm 증가 대표값 테이블 채택

3. Terminology \& Standard Keys (Single Source of Truth)
   3.1 Standard Keys (Internal)

UNDERBUST\_CIRC\_M : 밑가슴/흉곽 둘레(구조 Anchor), meters

BUST\_CIRC\_M : 젖가슴 최대 둘레(볼륨), meters

**Standard Keys Dictionary**: See [docs/contract/standard_keys.md](docs/contract/standard_keys.md) for the complete authoritative list.

3.1.1 related_measurement_key ENUM Rule

See header block for ENUM definition. **Rule**: related_measurement_key must use domain tokens (UNDERBUST, BUST, etc.), not full standard keys (UNDERBUST_CIRC_M) or arbitrary strings.

3.2 Legacy Handling

기존 단일 정의였던 CHEST는 표준 키에서 제외(Deprecated) 한다.

과거 CHEST v0 산출물은 legacy reference로만 유지하며, 앞으로 가슴 계열은 UNDERBUST/BUST로만 표준화한다.
(즉, “CHEST = 표준 가슴”이라는 표현은 금지)

4. Current Status \& Active Strategy

Current Track: Track A: Body Engine (Measurement Logic Core)

Strategic Direction:

기존 단일 CHEST 정의를 폐기하고, 브라 사이즈 입력과 직접 연동되는 UNDERBUST 및 BUST 체계로 전환

모든 측정 결과는 자동 보정 없이 신호(Warning 포함) 기반의 사실 기록 위주로 관리

5. Bra Input Spec (MVP, Normative)
   5.1 Input Format

브라 사이즈 입력 표준: 문자열 "75A" 형식 (한국 사용자 친화)

5.2 Parsing Rule

"75A" →

band\_cm = 75

cup = 'A'

5.3 Allowed Range (MVP)

band\_cm: 65–90 (초기 운영 범위; 확장 가능)

cup: A–F (초기 운영 범위; 확장 가능)

5.4 Cup Delta Table (대표값, cm)

A: 10.0

B: 12.5

C: 15.0

D: 17.5

E: 20.0

F: 22.5

5.5 Computation (Unit-Consistent, meters)

UNDERBUST\_CIRC\_M = band\_cm / 100.0

BUST\_CIRC\_M = UNDERBUST\_CIRC\_M + (DELTA\_CM\[cup] / 100.0)

6. Male Rule (Normative)

Male은 별도 키를 추가하지 않고 동일 키(UNDERBUST\_CIRC\_M, BUST\_CIRC\_M)를 사용한다.

다만 남성의 경우 Δ = (BUST - UNDERBUST)는 0에 가깝게 수축(≈0) 되도록 모델링/제약한다.
(큰 Δ가 관측되면 자동 보정하지 않고 Warning 신호로 기록)

7. Today’s Objective (Current Focus)

Objective: Bust/Underbust 이원화 체계의 Semantic \& Contract 논리 완결성 확보 + 키 맵핑 최신화

Key Tasks:

UNDERBUST\_CIRC\_M, BUST\_CIRC\_M에 대한 Semantic → Contract 문서 작성/정리

프로젝트 전체 Standard Key Mapping 업데이트(가슴 계열 우선)

legacy CHEST 관련 문서에서 Deprecated 처리 및 참조 관계 명시

Ops Hygiene (Backlog):

레포지토리 내 불필요한 레거시 README 및 중복 파일 정리 (핵심 작업 완료 후)

8. Operational Guardrails (AI Notes)

Do NOT: Validation 레이어에 판정 임계값(PASS/FAIL)을 넣지 말 것 (오직 사실 기록)

Do NOT: 시스템 재설계 제안 금지
Do NOT: tools/, db/, pipelines/, tests/, .github/workflows/ 및 측정 러너/검증 경로 변경 PR은 docs/sync/CURRENT\_STATE.md에 (a) changed\_paths, (b) 2~4줄 변경 요약을 반영하기 전에는 머지하지 말 것.
Focus on: 가슴 계열 이원화 정의의 논리적 완결성(Semantic \& Contract) + 키 표준화

Focus on: L4 Validation 산출물 경로는 verification/reports/<measurement\_key>\_v0/로 고정한다(예: validation\_summary.json은 warnings 기반 사실 기록 요약).

**Guard ref**: See header block for official definition location.

9. Provenance

Snapshot Tag: snapshot-20260122-bust-underbust-mvp1

Commit (main HEAD): 9b7ef4a9539e051d43b8e95ed8e1bd6d35845fa0

