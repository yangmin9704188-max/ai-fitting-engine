# Legacy Handling (Semantic v0)

## 1. Principles
- Legacy 의미를 “살리기 위해” 표준키를 자동 대체하지 않는다.
- Deprecated는 Reference-only로 유지하며, 신규 구현/보고/판정의 canonical로 쓰지 않는다. 

## 2. CHEST Legacy
- CHEST_CIRC_M_REF는 **legacy CHEST 계열의 참조용(REF)**이다.
- Canonical chest/bust 체계는 UNDERBUST_CIRC_M + BUST_CIRC_M이다.
- 금지: “CHEST = 표준 가슴둘레”라는 서술.
- 금지: CHEST_CIRC_M_REF가 결측이면 BUST/UNDERBUST로 자동 대체. (반대도 금지) :contentReference[oaicite:61]{index=61}

## 3. Multi-definition Families
- WAIST vs NAVEL_WAIST: 자동 대체 금지
- HIP vs UPPER_HIP vs TOP_HIP: 자동 대체 금지
- THIGH vs MID_THIGH: 자동 대체 금지
- CALF vs MIN_CALF: 자동 대체 금지
- ANKLE_MAX는 단독(파생 개념은 v0 범위 밖) :contentReference[oaicite:62]{index=62}
