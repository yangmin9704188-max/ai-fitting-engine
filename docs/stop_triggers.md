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

## Slack Notification

Stop Trigger가 true일 때만 Slack 알림이 전송됩니다.
정상(PASS) 상황에서는 절대 알림하지 않습니다.

**알림 조건:**
- 하나 이상의 Stop Trigger가 true인 경우에만 Slack 알림
- 모든 트리거가 false면 알림 없음 (정상 동작)

**알림 내용:**
- 활성화된 트리거 목록 (comma-separated)
- PR 번호, 브랜치, 실행자(actor) 정보
- PR URL 링크
- 트리거별 권장 조치사항 (Suggested Action)

**워크플로우:**
- PR 이벤트 (opened, synchronize, reopened) 및 workflow_dispatch에서 실행
- test/** 브랜치 push 이벤트에서도 실행 (테스트용)
- `tools/extract_stop_triggers.py`로 트리거 추출
- GitHub Actions에서 Slack webhook으로 POST

**안전장치:**
- SLACK_WEBHOOK_URL secret이 비어있으면 경고만 출력하고 종료 (실패하지 않음)
- 증거 부족(파일 미존재 등) 시 INSUFFICIENT_EVIDENCE=true로 설정하여 알림
- push 트리거는 test/** 브랜치에만 한정하여 노이즈 방지

## How to Test Slack Notifications

**방법 1: workflow_dispatch with force_trigger (권장)**

1. GitHub Actions 탭에서 "stop-trigger-slack" 워크플로우 선택
2. "Run workflow" 클릭
3. "force_trigger" 드롭다운에서 테스트할 트리거 선택 (예: AUDIT_FAILED)
4. "Run workflow" 클릭
5. 워크플로우 로그에서 다음 확인:
   - "Force trigger mode: AUDIT_FAILED" 메시지
   - "Active triggers: AUDIT_FAILED" 출력
   - "Send Slack notification" step 실행 여부
6. Slack 채널에서 `[STOP]` 메시지 수신 확인

**방법 2: test/** 브랜치 push (테스트 주입)**

1. test/** 브랜치에서 `triggers.json` 생성:
   ```json
   {"FREEZE_REQUIRED": false, "AUDIT_FAILED": true, "SPEC_CHANGE": false, "UNEXPECTED_ERROR": false, "INSUFFICIENT_EVIDENCE": false, "RISK_HIGH": false}
   ```
2. 커밋 및 푸시 (test/** 브랜치)
3. 워크플로우가 자동 실행됨
4. Slack 알림 확인

**예상 로그 증거:**
```
Force trigger mode: AUDIT_FAILED
Active triggers: AUDIT_FAILED
HAS_TRIGGERS=true
SUGGESTION=Architect intervention required
Slack notification sent successfully: 200
```

**주의:**
- force_trigger는 테스트 목적으로만 사용
- 운영 환경에서는 실제 evidence 파일에서 트리거를 추출
- test/** 브랜치 외의 push 이벤트는 워크플로우를 트리거하지 않음

## Enforcement

- 트리거가 true가 되면 즉시 실행을 중단합니다.
- Human의 명시적 승인 없이는 진행하지 않습니다.
- 트리거 해결 후 재시작은 새로운 Evidence Pack 기반으로 진행됩니다.
