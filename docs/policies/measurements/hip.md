title: "Hip Circumference"

version: "v1.0"

status: "legacy"

created\_date: "2026-01-16"

frozen\_commit\_sha: "9731aa4"

author: "Yang"

---

> **⚠️ LEGACY DOCUMENT**  
> **status**: legacy  
> **superseded_by**: [docs/policies/measurements/INDEX.md](INDEX.md)  
> **reason**: pre-sizekorea definition; anchors updated  
> **note**: do not treat as SoT

---

\# Hip Circumference v1.0



> Doc Type: Contract  

> Layer: Semantic



---



\## 1. Summary



본 계약은 HIP(엉덩이둘레) 측정의 의미를 고정한다.  

이 계약이 깨질 경우 엉덩이둘레 측정의 일관성이 보장되지 않으며, 의류 제작 및 피팅에 혼란이 발생한다.



---



\## 2. Scope



\### In Scope



\- HIP 측정의 의미 정의

\- 선택 규칙 (Selection Rule)

\- 모호성 처리 규칙



\### Out of Scope



\- 구현 세부 (Plane 방정식, 정점 루프, 특정 축 좌표값)

\- 정확도 비교

\- Gate, PASS/FAIL 판단

\- Geometric Layer 구현



---



\## 3. Invariants (Normative)



\### 3.1 MUST (필수)



\- \*\*Key\*\*: HIP

\- \*\*Definition\*\*: 둔부 및 골반 최대 돌출 지점을 지나는 단면의 둘레

\- \*\*Selection Rule\*\*: 해당 영역 내 둘레값의 최대값(Max) 채택



\### 3.2 MUST NOT (금지)



\- Plane 방정식 기재 금지

\- 정점 루프 기재 금지

\- 특정 축(Axis) 좌표값 기재 금지

\- (이러한 내용은 Geometric Layer에서 다룸)



\### 3.3 SHOULD (권장)



\- \*\*Ambiguity Handling\*\*: 만약 최대 돌출 지점이 모호하거나 다수가 존재할 경우, 해부학적 기준에 따라 일관되게 식별 가능한 단면 하나를 선택한다.



---



\## 4. Interface / Schema (If Applicable)



N/A (Semantic-only 계약)



---



\## 5. Prohibitions (Explicit)



\- Gate 정의

\- Acceptance / PASS / FAIL

\- 품질 평가

\- 모델 학습, 회귀, Re-PCA 등



---



\## 6. Change Notes



v1.0:

\- HIP 측정 의미 정의 초기화



---



\## 7. Freeze Notes



\*\*Frozen Artifacts:\*\*

\- 본 문서 (Hip Circumference v1.0)



\*\*Change Control:\*\*

\- 변경은 새 버전 + 새 Freeze + 새 Tag로만 가능

