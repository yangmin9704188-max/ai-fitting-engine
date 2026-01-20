AI Virtual Fitting Engine
Internal Project Constitution & Operating Manual

Scope
This document is an internal-only operating constitution.
It is optimized for LLM comprehension, reproducibility, and governance —
not for marketing or external communication.

1. Project Vision & Hard KPIs

본 프로젝트의 모든 기술적·정책적 판단은 아래 KPI 달성 여부를 최우선 기준으로 한다.

Hard KPIs

Cost: 추론 건당 10원 미만
(클라우드/GPU/렌더링 비용 포함)

Latency: 입력 → 최종 결과까지 10–30초 이내

Quality:

B2B 커머스 수준의 고퀄리티 이미지

설명 가능한(Explainable) 신체 치수 산출

KPI를 충족하지 못하는 기술적 선택은
정확성·완성도와 무관하게 채택 대상이 아니다.

2. LLM-Orchestrated Governance (Single-Owner Model)

본 프로젝트는 1인 개발 환경이므로,
역할 분리를 통해 시스템적 안정성을 확보한다.

Role	Agent	Responsibility	Authority
Owner	Human (민영)	최종 의사결정, 문서 확정, Git Commit & Tag 실행	최종 승인
Planner	GPT	정책(Policy) 설계, 보고서/명세서 작성, 커밋·태그 요청	설계 주도
Advisor	Gemini	2차 검토, 논리적 반례 제시, 비구속적 피드백	조언
Executor	Cursor	코드 작성, 실험 수행, 아티팩트 생성	구현/실행
중요한 원칙

LLM은 결정하지 않는다

Human은 추론하지 않는다

Git은 **사실의 기준(Source of Truth)**이다

3. Core Design Philosophy
Geometry-First

치수 측정에 블랙박스 AI를 사용하지 않는다

모든 measurement는 기하학적으로 설명 가능해야 한다

Deterministic & Explainable

같은 입력 → 같은 결과

모든 수치에는 Policy Report라는 근거 문서가 존재해야 한다

Failure is a Feature

FAIL은 오류가 아니다

Semantic Gate에서 실패하는 것이 시스템의 정상 동작

4. Policy Lifecycle (Strict State Machine)
정책 상태 정의

Draft: 설계/가설 단계

Candidate: 구현 완료, 검증 대기

Frozen: 모든 게이트 통과 + Git Tag 존재

Archived: 실패 또는 더 이상 사용하지 않음

Deprecated: Frozen이지만 대체 정책 존재

절대 규칙

No Tag, No Frozen
Git Tag가 없는 정책은 어떤 경우에도 Frozen이 아니다.

5. Verification Gates (모두 필수)

Semantic Validity

측정값이 실제 의류 제작/피팅 의미와 일치하는가

Wiring Proof

정책 cfg ↔ 런타임 cfg 일치(hash)

Golden Set Regression

대표 데이터셋에서 성능 퇴행 없음

Stability (보조 지표)

std / CV (단, 의미 게이트보다 우선하지 않음)

6. Single Policy Report Rule (Solo Development)

본 프로젝트에서는 정책당 Policy Report 1개만 사용한다.

작성/확정 규칙

실행 전:

Report는 초안(Draft) 상태

Git SHA / Tag를 값으로 기입하지 않는다

실행 후:

결과(PASS / FAIL) 확정

이 시점에만 Git 필드를 채운다

이후 값은 절대 변경되지 않는다

초안에 적힌 Git 값은 “확정값”이 아니라
비권위적 메모로 간주한다.

7. Notion ↔ Git Data Contract (Canonical)
Policies DB (요약)

Identity: Name, Version, Measurement, Owner, Created Date

Status: Draft / Candidate / Frozen / Archived / Deprecated

Git Binding:

Frozen Git Tag

Frozen Commit SHA

Base Commit

Lineage:

Supersedes / Superseded By

Reporting:

Latest Report

Policy Reports DB (요약)

Identity: Report ID, Related Policy, Report Type

Result:

PASS / FAIL / PARTIAL

Gate Failed

Git Context:

Evaluated Policy Commit

Verification Tool Commit

Execution:

Artifacts Path

Dataset / Input

8. Git Evidence Protocol (Mandatory)
핵심 원칙

문서에 Git 값을 서술로 적지 않는다

항상 명령어 블록으로만 제공

사람은 출력값을 복사해서 필드에 입력한다

표준 명령어 템플릿
정책 구현 기준 커밋(Base / Evaluated)
git log -n 1 --format="%H" -- <POLICY_IMPL_FILE_PATH>

검증 도구 커밋
git log -n 1 --format="%H" -- <VERIFICATION_TOOL_FILE_PATH>

Frozen Tag 기준 커밋
git show -s --format="%H" <freeze_tag_name>

금지 표현

“확인 후 기입”

“이전 커밋 사용”

“HEAD 기준”

9. Commit / Tag Request Protocol (LLM Rule)

GPT는 다음과 같이 행동해야 한다.

커밋이 필요한 시점:

명확하게 요청

포함할 경로 명시

태그가 필요한 시점:

모든 게이트 통과 확인 후

태그명까지 제안

Human은:

명령어 실행 결과만 신뢰

추정·기억 기반 SHA 사용 금지

10. Failure as a First-Class Outcome

FAIL 정책은 다음과 같이 처리된다.

Archived 상태로 보존

Policy Report에 실패 원인 명시

후속 정책(vNext)의 설계 근거로 사용

실패한 정책은 삭제되지 않는다
실패는 설계 자산이다.

11. Worked Example (Reference)

Shoulder Width v1.1.3

Result: FAIL

원인: Semantic mismatch

조치: v1.2로 계승

이 사례는 본 프로젝트의 정상적인 작동 예시이다.

Final Note

이 문서는

코드보다 우선한다

실험보다 우선한다

편의보다 우선한다

이 문서와 충돌하는 구현은 잘못된 구현이다.

### Result Semantics: PASS / PARTIAL / FAIL

Policy Report results are interpreted as follows:

- PASS:
  - All mandatory gates pass.
  - Policy is eligible for Frozen status.

- PARTIAL:
  - Semantic Validity MUST be PASS.
  - Wiring Proof MUST be PASS.
  - Stability or auxiliary metrics (e.g. CV, std) may be below target.
  - PARTIAL results MAY be Frozen only if explicitly approved by the Owner
    and documented in the Policy Report.

- FAIL:
  - Any failure in Semantic Validity or Wiring Proof.
  - Policy MUST NOT be Frozen and is Archived.

### Artifact Directory Naming Convention

All verification artifacts MUST be stored under a deterministic path.

Format:
artifacts/<measurement>/<policy_name>/<version>/<YYYYMMDD>_<result>/

Example:
artifacts/shoulder_width/shoulder_width_v1.1.3/20260117_FAIL/

Rules:
- Date is the execution date.
- Result is one of PASS / PARTIAL / FAIL.
- Artifacts from different runs MUST NOT be merged.
- Policy Reports MUST reference this exact path.

