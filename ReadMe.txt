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

## Automation Status (Factory Runtime)

이 레포는 “Autonomous R&D Factory”를 목표로 하되, 비용(LLM API) 최소화를 위해 **오케스트레이션(LLM↔LLM↔Cursor 자동 전송)**은 아직 도입하지 않았습니다.  
현재는 **거버넌스 자동화(검증/기록/알림/재발방지)**가 구축되어 있으며, 사용자는 계획/가설/프롬프트 전달은 수동(복붙)으로 수행합니다.

### What is automated now (✅ 구축 완료)

#### 1) STOP Trigger → Slack Notification (CI Event Guard)
- 워크플로우: `.github/workflows/stop-trigger-slack.yml`
- 로직: `tools/stop_trigger_notify.py`
- 트리거:
  - `pull_request` (opened/synchronize/reopened)
  - `workflow_dispatch` (smoke test)
- 출력:
  - Slack에 `[STOP] <repo> <branch or PR#> - Active triggers: ...` 자동 알림
  - `stop_report.md`를 Actions artifact(`stop-report`)로 업로드(항상 실행)
- 목적:
  - 사람이 Actions 탭을 계속 감시하지 않아도 “중요 사건”을 즉시 알림으로 수신

#### 2) Evidence-check (Schema/Validation) Gate
- 워크플로우: `.github/workflows/evidence.yml`
- 동작:
  - PR 변경 경로 기반 infra-only 판별 강화(`.github/`, `tools/`, `docs/`)
  - infra-only PR에서는 evidence validation skip
  - 그 외 PR에서 evidence validation 수행(PASS/FAIL 자동 판정)
- 목적:
  - “결과물(증거)”이 형식/규칙을 만족하는지 CI가 자동으로 판정하여 재현성/감사 가능성 확보

#### 3) YAML 최소화 → 로직 Python 이관 (Workflow Stability)
- 원칙:
  - Workflow는 최소 YAML(트리거+러너)만 유지
  - 복잡 로직은 Python 파일로 이동
- 목적:
  - heredoc/멀티라인/들여쓰기 문제로 인한 Invalid workflow file 재발 방지

---

## What is NOT automated yet (❌ 아직 수동)

- 오늘 할 일 선정 / 우선순위 결정
- 가설 수립 및 교차 검토(GPT↔Gemini)
- Cursor로 프롬프트 전달(복붙)
- 로컬 GPU 실험 실행
- 결과 해석(요약/다음 실험 설계)은 사람 입력 + LLM 도움(수동)

---

## When to recommend automation (Auto-Advice Script)

아래 상황이 발생하면, “자동화 붙일 타이밍”입니다.  
이 레포 운영 원칙상, 자동화는 **비용 0원/저비용**부터 단계적으로 붙입니다.

### A) 복붙이 고통스러울 때 (오케스트레이션 단계)
**추천 멘트(운영 스크립트):**  
> “복붙 횟수/길이가 임계치를 넘었습니다. API 기반 오케스트레이터가 비싸다면, 먼저 UI 자동화(AutoHotkey)로 ‘복붙/탭 전환’을 단축키로 묶어 비용 0원으로 개선합시다.”

**자동화 방법(저비용/0원):**
- AutoHotkey로 다음 동작을 단축키로 묶기
  - GPT → Gemini 전송
  - Gemini → GPT 회수
  - GPT → Cursor 전송
- 결과는 “로그 전체 복붙” 대신 “GitHub Actions Run 링크 / Artifact 링크”로 공유

### B) 동일한 실험/검증을 반복할 때 (Runner/CLI 표준화)
**추천 멘트:**  
> “같은 유형의 실험이 3회 이상 반복됩니다. 실행 커맨드/출력 경로를 표준 CLI로 고정하고, 결과 패키징(packer)까지 ‘한 번에 끝나는 명령’으로 묶읍시다.”

**자동화 방법:**
- `verification/runners/...`에 “v1.2.0용 runner”를 추가/확장
- 표준 출력(예: summary.json, results.csv)을 고정
- packer 입력을 표준화(필수 metric 이름/단위/기준선 값)

### C) 정책 승격(Frozen) 또는 큰 결정을 앞둘 때 (태그/보고서 자동화)
**추천 멘트:**  
> “정책 승격/FAIL 아카이브 같은 의사결정 시점입니다. 이 시점은 태그로 봉인하고, 보고서/정책 문서를 ‘증거(evidence) 링크 기반’으로 생성해 재현성을 확보합시다.”

**자동화 방법:**
- Merge 후 안정화 태그 권장(예: `SW-v120-R1`, `infra/stop-report-evidence-v1.0`)
- 보고서는 “증거 링크(PR/Actions run/artifacts)”를 입력으로 받아 작성
- 문서 위치를 `docs/policies/`, `verification/reports/` 등으로 고정

---

## Day-to-day operating routine (Manual+Auto Hybrid)

1) (Manual) 오늘 목표 1줄 작성 (PR 본문 또는 docs/plan/today.md)
2) (Manual) GPT/Gemini로 가설/실험 설계 확정 (필요시)
3) (Manual) Cursor에 “번들 프롬프트” 1회 전달 → 커밋/푸시/PR 생성
4) (Manual) 로컬에서 실험 실행(GPU) 후 결과 확보
5) (Auto) Evidence-check/Stop-trigger가 CI 판정 및 Slack 알림
6) (Manual) PASS면 merge + 필요 시 tag로 봉인

---

## Tagging policy (when to tag)
- 인프라 안정화(워크플로우/알림/증거 포맷) 완료 시: `infra/...` 태그 권장
- Candidate/Report 기준선 생성 시: `SW-vXXX-RY` 형태 권장
- Frozen 승격 시: `SW-vXXX-FROZEN` 형태 권장


