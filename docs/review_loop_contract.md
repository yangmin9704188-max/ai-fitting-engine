# GPT ↔ Gemini Review Loop Contract

## Scope

이 문서는 Autonomous R&D Factory의 GPT ↔ Gemini 리뷰 루프 운영 규격(헌법)입니다.
코드가 아닌 운영 계약/명세서로서, 모든 LLM 에이전트는 이 규격을 준수해야 합니다.

## Input Requirements

### Evidence Pack (필수 입력)

리뷰 루프는 오직 다음 Evidence Pack만을 입력으로 사용합니다:

1. **pending_review.json**
   - 경로: 프로젝트 루트의 `pending_review.json`
   - 내용: observation 데이터와 artifacts 경로 정보

2. **logs/observation.md**
   - 경로: `logs/observation.md`
   - YAML frontmatter 블록 포함
   - policy_name, version, measurement, run_id, state_intent, gates 정보 포함

3. **manifest.json**
   - 경로: `artifacts/{category}/{version}/{run_id}_{status}/manifest.json`
   - run_id, timestamp, artifacts 목록 포함

### 입력 검증

- Evidence Pack의 세 파일은 모두 존재해야 합니다.
- run_id는 세 파일에서 일치해야 합니다.
- 파일 경로는 프로젝트 루트 기준 상대 경로입니다.

## Review Loop States

### v1: Initial Draft

**생성 주체**: GPT

**입력**: Evidence Pack

**출력**: v3 Execution Pack 구조를 따르는 초안

**품질 기준**:
- 모든 필수 필드 포함
- 기본적인 실행 지시사항 포함
- 구체성 수준: 중간 (v3보다 덜 구체적)

### v2: Revised Draft (optional)

**생성 주체**: GPT

**입력**: Evidence Pack + Gemini audit feedback

**출력**: Gemini 피드백을 반영한 개선된 초안

**품질 기준**:
- v1의 NON-COMPLIANT 항목이 모두 해결됨
- v3에 가까운 수준의 구체성

### v3: Final Execution Pack

**생성 주체**: GPT (Gemini audit 후)

**입력**: Evidence Pack + Gemini audit feedback (v1 또는 v2 기반)

**출력**: Cursor 실행 가능한 최종 Execution Pack

**필수 구성 요소**:

1. **Human Summary** (5~10줄)
   - 변경사항의 본질적 의미
   - 왜 이 변경이 필요한지
   - 실행 후 기대되는 결과
   - Human이 즉시 이해할 수 있는 수준

2. **Cursor Execution Prompt**
   - 파일/라인 명시 (절대 경로 또는 프로젝트 루트 기준 상대 경로)
   - 실행할 명령어 (복사-붙여넣기 가능한 형태)
   - 기대 산출물 명시 (파일 경로, 디렉토리 구조, JSON 필드명 등)
   - 실행 순서 (순차적 단계)
   - 실행 전/후 검증 방법

3. **Stop Triggers** (JSON)
   - 문서 `docs/stop_triggers.md`에 정의된 트리거 ID 목록
   - 각 트리거가 true가 되는 조건 명시
   - true일 때 Human에게 전달할 메시지

## Audit Process

### Auditor: Gemini

**역할**: v1 또는 v2를 검토하여 COMPLIANT / NON-COMPLIANT 판단

**출력 형식**:
```json
{
  "verdict": "COMPLIANT" | "NON-COMPLIANT",
  "feedback": [
    {
      "field": "field_name",
      "severity": "ERROR" | "WARNING",
      "issue": "구체적인 문제 설명",
      "suggestion": "개선 방안"
    }
  ],
  "stop_triggers": ["TRIGGER_ID1", "TRIGGER_ID2"]
}
```

### Audit Checklist

1. **Evidence 존재/경로 실존**
   - pending_review.json 존재 여부
   - logs/observation.md 존재 여부
   - manifest.json 경로가 실제로 존재하는지
   - 세 파일의 run_id 일치 여부

2. **status/state 일관성**
   - observation.md의 gates.status와 manifest.json의 status 일치
   - state_intent가 Policy Lifecycle에 부합하는지
   - gates 값들이 논리적으로 일관되는지

3. **Frozen 원칙 위반 여부**
   - Frozen 상태의 정책을 수정하려는 시도인지
   - No Tag, No Frozen 원칙 준수 여부
   - 변경이 frozen policy의 semantic definition을 변경하는지

4. **재현성/추적성**
   - 모든 경로가 추적 가능한지
   - 실행 명령어가 재현 가능한지
   - 기대 산출물이 검증 가능한지

5. **Cursor Execution Prompt 품질**
   - 파일/라인/명령어가 구체적으로 명시되었는지
   - 기대 산출물이 명확한지
   - 실행 전/후 검증 방법이 있는지

## Loop Flow

```
Evidence Pack
    ↓
GPT generates v1
    ↓
Gemini audits v1
    ↓
[COMPLIANT?]
    ├─ YES → v1 becomes v3 (skip v2)
    └─ NO → GPT generates v2
                ↓
            Gemini audits v2
                ↓
            [COMPLIANT?]
                ├─ YES → v2 becomes v3
                └─ NO → Stop Trigger activated → Human intervention
```

## Output Delivery

v3 Execution Pack은 다음 형식으로 Human에게 전달됩니다:

```markdown
# Human Summary
[5-10줄 요약]

# Cursor Execution Prompt
[구체적인 실행 지시사항]

# Stop Triggers
```json
{
  "FREEZE_REQUIRED": {
    "condition": "...",
    "human_message": "..."
  }
}
```
```

## Enforcement

- 이 규격은 절대적입니다. 예외는 없습니다.
- Evidence Pack 외의 입력을 사용하는 경우 즉시 거부됩니다.
- v3에 Human Summary, Cursor Execution Prompt, Stop Triggers가 모두 포함되지 않으면 NON-COMPLIANT입니다.
