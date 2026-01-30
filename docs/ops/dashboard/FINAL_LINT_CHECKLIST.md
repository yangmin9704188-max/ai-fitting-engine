# Dashboard Contract v0 — Final Lint Checklist

사람이 빠르게 확인할 수 있는 최종 점검 목록.
패치 적용 후 아래 항목을 순서대로 확인한다.

---

- [ ] **1. Step ID 고유성**: PLAN_v0.yaml에서 B01~B06, F01~F04, G01~G02가 각각 고유하며 모듈 간 중복 없음
- [ ] **2. depends_on 참조 유효성**: 모든 depends_on 값(`body:B01` 등)이 실제 존재하는 step ID를 가리킴
- [ ] **3. unlocks 대칭성**: 모든 unlocks 항목이 대상 step의 depends_on에 역방향으로 존재
- [ ] **4. dod.total == len(dod.items)**: 12개 step 모두에서 total 숫자와 items 배열 개수가 일치
- [ ] **5. Evidence 패턴 완전성**: 모든 DoD item에 `(Evidence: <경로>)` 또는 `(Evidence: TBD)` 패턴이 존재 (I-01 패치 후)
- [ ] **6. TBD placeholder 구분**: LAB_SOURCES_v0.yaml에서 각 소스별 고유 TBD 문자열 사용 (`TBD_HUB_PATH`, `TBD_FITTING_LAB_PATH`, `TBD_GARMENT_LAB_PATH`)
- [ ] **7. body 이벤트 소스 명시**: LAB_SOURCES_v0.yaml에 hub 소스 항목이 존재하고, body 모듈 이벤트 경로가 정의됨
- [ ] **8. 판정 언어 부재**: 4개 파일 전체에 PASS, FAIL, threshold, clamp 단어가 없음 (검색으로 확인)
- [ ] **9. Bootstrap 모드 명시**: EXPORT_CONTRACT_v0.md §5에서 Mode 1(수동)이 현재이고 Mode 2(자동)가 운영 DoD임이 명확히 구분됨
- [ ] **10. §1 시제 수정**: EXPORT_CONTRACT_v0.md §1 Overview에서 "자동 집계한다"가 "집계한다 (§5 참조)"로 수정됨
- [ ] **11. §3.2 제목 수정**: EXPORT_CONTRACT_v0.md의 "Validation Rules" 제목이 "Field Constraints"로 변경됨 (L4 용어 충돌 해소)
- [ ] **12. Dashboard GENERATED 헤더**: PROJECT_DASHBOARD.md 상단에 DO NOT EDIT 주석이 존재
- [ ] **13. Mermaid 펜스 정상**: PROJECT_DASHBOARD.md의 Mermaid 블록이 ` ```mermaid ` / ` ``` `로 올바르게 감싸져 있고, "optional" 라벨 및 보조 역할 명시 존재
- [ ] **14. Placeholder 렌더링 안전**: Phase×Module 매트릭스에서 `_/_` 대신 `—/N` 형식 사용 (Markdown 이탤릭 오해석 방지)
- [ ] **15. 경로 정합성**: Data Sources 테이블의 3개 경로(`docs/ops/dashboard/PLAN_v0.yaml`, `docs/ops/dashboard/LAB_SOURCES_v0.yaml`, `docs/ops/dashboard/EXPORT_CONTRACT_v0.md`)가 실제 파일 위치와 일치
