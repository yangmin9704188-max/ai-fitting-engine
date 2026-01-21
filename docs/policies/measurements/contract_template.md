---
title: "..."            # DB: policies.name
version: "vX.Y"         # DB: policies.version
status: "draft|candidate|frozen|archived|deprecated"
created_date: "YYYY-MM-DD"
frozen_commit_sha: "abcdef0"   # status=frozen일 때 필수, 그 외 생략 가능

author: "Yang"
latest_report: "..."            # (옵션) Contract 문서에서는 보통 비워둔다
---

# <Contract Title> <version>

> Doc Type: Contract  
> Layer: Semantic | Data | Interface (중 하나만 선택)

---

## 1. Summary
- 이 문서가 **무엇을 고정(Freeze)하는 계약인지**를 1~3줄로 명시한다.
- 이 계약이 깨질 경우 발생하는 혼란의 종류를 간단히 적는다.

---

## 2. Scope
### In Scope
- 본 계약이 책임지는 레이어와 대상
  - 예: 측정 의미(Semantic), 단위 규약(Data), 인터페이스 형태(Interface)

### Out of Scope
- 명시적으로 다루지 않는 것
  - 구현 세부, 정확도 비교, 성능, Gate, PASS/FAIL 판단, 서비스 레이어 등

---

## 3. Invariants (Normative)
> 이 섹션만이 **강제 규칙**이다.  
> MUST / MUST NOT / SHOULD 를 명확히 구분한다.

### 3.1 MUST (필수)
- 반드시 지켜야 하는 불변 조건을 나열한다.

### 3.2 MUST NOT (금지)
- 이 계약 하에서 절대 발생해서는 안 되는 행위를 나열한다.

### 3.3 SHOULD (권장)
- 강제는 아니지만, 일관성과 추적성을 위해 권장되는 규칙을 나열한다.

---

## 4. Interface / Schema (If Applicable)
> Data / Interface 계약일 때만 사용한다.  
> Semantic-only 계약이면 `N/A`로 둔다.

### Inputs
- 입력 형태, 필수 메타데이터, 단위 요구사항 등

### Outputs
- 출력 값의 의미, 단위, 필수 필드

### Schema (Optional)
```json
{
  "example_field": "type"
}

5. Prohibitions (Explicit)

이 계약 문서에서 의도적으로 다루지 않는 것을 다시 한 번 명시한다.

Gate 정의

Acceptance / PASS / FAIL

품질 평가

모델 학습, 회귀, Re-PCA 등

6. Change Notes

vX.Y:

왜 이 버전이 생겼는지

무엇이 바뀌었는지

의미(Semantic)가 바뀌었는지 여부를 명확히 적는다.

7. Freeze Notes (When status = candidate | frozen)

Draft 단계에서는 생략 가능

Frozen Artifacts:

이 계약과 함께 봉인되는 파일 목록

Change Control:

변경은 새 버전 + 새 Freeze + 새 Tag로만 가능함을 명시
