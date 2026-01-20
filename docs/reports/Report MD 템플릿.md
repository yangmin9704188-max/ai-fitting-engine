---
report_id: "apose_normalization-v11-R1"   # 전역 유니크 ID
result: "pass"                            # pass | fail | hold
policy_name: "A-Pose Normalization"
policy_version: "v1.1"
created_date: "2026-01-16"
artifacts_path: "verification/reports/apose_v11"
inputs: "synthetic pose set"
---

# Report: <Policy Name> <Policy Version> — <report_id>

## 1. Purpose
> 이 리포트가 **무엇을 검증하기 위한 리포트인지** 1~2줄로 명확히 기술

- 대상 정책: **A-Pose Normalization v1.1**
- 목적: Freeze 승인 기준 충족 여부 검증

---

## 2. Evaluation Scope
- Evaluation type:
  - Offline / Synthetic / Real data (택1 또는 서술)
- Input description:
  - synthetic pose set
- Artifacts location:
  - `verification/reports/apose_v11`

---

## 3. Gate Results
> ⚠️ Gate 이름과 의미는 **Policy의 Gate Definitions**를 그대로 따른다.  
> ⚠️ 여기에는 **결과와 관찰 사실만** 기록한다.

### Gate G1: <Gate Name>
- **Result**: PASS | FAIL | HOLD
- **Observation**
  - (측정 요약, 로그 요약, 정량/정성 근거)

### Gate G2: <Gate Name>
- **Result**: PASS | FAIL | HOLD
- **Observation**
  - (근거 요약)

*(Policy에 정의된 Gate 수만큼 반복)*

---

## 4. Issues & Deviations (선택)
> FAIL/HOLD 또는 경계 케이스가 있을 때만 작성

- Issue:
- Impact:
- Mitigation / Follow-up:

---

## 5. Conclusion
> 이 리포트의 **최종 판단 요약**

- Overall Result: **PASS**
- Decision:
  - A-Pose Normalization v1.1은
    모든 정의된 Gate를 만족하여 Frozen 승인 기준을 충족함.

---

## 6. Notes (선택)
- 특이사항
- 재실험 필요 여부
- 다음 Action 제안
