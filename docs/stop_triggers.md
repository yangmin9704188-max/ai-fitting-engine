# Stop Triggers Specification

## Scope

이 문서는 Autonomous R&D Factory의 중단 트리거(Stop Triggers) 정의입니다.
트리거가 true가 되면 자동 실행을 중단하고 Human의 개입을 요청합니다.

## Trigger Definitions

### FREEZE_REQUIRED

**When true:**
- Frozen 상태의 정책을 수정하려는 시도
- Frozen policy의 semantic definition 변경 요청
- Frozen policy의 cfg_hash를 변경하려는 시도
- "No Tag, No Frozen" 원칙 위반

**Human request:**
```
[STOP TRIGGER: FREEZE_REQUIRED]

Frozen 상태의 정책을 수정하려는 시도가 감지되었습니다.
Frozen 정책은 변경할 수 없습니다.

옵션:
1. 새 버전으로 분기 (policy_name_v1.3 등)
2. 요청을 철회
3. Policy Lifecycle 재검토 필요

어떻게 진행할까요?
```

### AUDIT_FAILED

**When true:**
- v1 audit 결과 NON-COMPLIANT
- v2 audit 결과 NON-COMPLIANT (최대 2회 시도 후)
- audit checklist의 ERROR 레벨 이슈가 해결되지 않음

**Human request:**
```
[STOP TRIGGER: AUDIT_FAILED]

Gemini audit에서 NON-COMPLIANT 판정을 받았습니다.
최대 재시도 횟수에 도달했습니다.

문제 요약:
[Gemini feedback 요약]

다음 중 선택해주세요:
1. 수동으로 Execution Pack 수정
2. Evidence Pack 재검토 (실험 재실행)
3. Audit 기준 재검토
```

### SPEC_CHANGE

**When true:**
- Evidence Pack과 기존 Policy Lifecycle/규격의 불일치
- 새로운 정책 상태(state)가 정의됨
- Verification Gate 정의 변경
- Frozen 원칙 위반

**Human request:**
```
[STOP TRIGGER: SPEC_CHANGE]

운영 규격(헌법) 변경이 감지되었습니다.
Spec change는 Human 승인이 필요합니다.

변경 내용:
[구체적인 변경 사항]

승인하시겠습니까? (Y/N)
승인 시 docs/ 디렉토리 관련 문서 업데이트 필요.
```

### UNEXPECTED_ERROR

**When true:**
- Evidence Pack 파싱 실패
- 필수 파일 누락 (pending_review.json, observation.md, manifest.json)
- run_id 불일치
- JSON/YAML 형식 오류

**Human request:**
```
[STOP TRIGGER: UNEXPECTED_ERROR]

예상치 못한 오류가 발생했습니다.

오류 내용:
[구체적인 오류 메시지]

조치:
1. Evidence Pack 무결성 확인
2. 파일 경로 확인
3. 재실행 또는 수동 수정
```

### INSUFFICIENT_EVIDENCE

**When true:**
- Evidence Pack의 필수 필드 누락
- gates 정보 불완전
- manifest.json의 artifacts 목록 불완전
- 실행 검증을 위한 정보 부족

**Human request:**
```
[STOP TRIGGER: INSUFFICIENT_EVIDENCE]

Evidence Pack에 필수 정보가 부족합니다.

누락된 정보:
[구체적인 누락 항목]

필요 조치:
- verification runner 재실행
- observation.md 수동 보완
- manifest.json 검증
```

### RISK_HIGH

**When true:**
- Frozen 정책에 영향을 주는 변경
- Core measurement 로직 변경
- Verification Gate 기준 변경
- Policy Lifecycle 상태 전이 (Candidate → Frozen 등)

**Human request:**
```
[STOP TRIGGER: RISK_HIGH]

높은 위험도 변경이 감지되었습니다.
Human 승인이 필요합니다.

변경 영향 범위:
[영향받는 정책/모듈 목록]

위험 요소:
[구체적인 위험 사항]

승인하시겠습니까? (Y/N)
```

## Trigger JSON Format

v3 Execution Pack의 Stop Triggers는 다음 형식입니다:

```json
{
  "TRIGGER_ID": {
    "condition": "구체적인 true 조건 설명",
    "human_message": "Human에게 표시할 메시지",
    "severity": "ERROR" | "WARNING",
    "requires_approval": true | false
  }
}
```

## Trigger Priority

여러 트리거가 동시에 true인 경우:
1. ERROR > WARNING
2. FREEZE_REQUIRED > SPEC_CHANGE > RISK_HIGH > 기타

## Enforcement

- 트리거가 true가 되면 즉시 실행을 중단합니다.
- Human의 명시적 승인 없이는 진행하지 않습니다.
- 트리거 해결 후 재시작은 새로운 Evidence Pack 기반으로 진행됩니다.
