# Dashboard Contract v0 — Verification Report

**생성일**: 2026-01-29
**대상 파일**: PLAN_v0.yaml, EXPORT_CONTRACT_v0.md, LAB_SOURCES_v0.yaml, PROJECT_DASHBOARD.md
**Canon 참조**: interface_ledger_v0.md (제공됨), port_readiness_checklist_v0.md (제공됨)

---

## A. Cross-file Consistency Checks

### A-1. PLAN_v0.yaml 내부 정합성

#### Step ID 고유성

| Module | Step IDs | 중복 |
|--------|----------|------|
| body | B01, B02, B03, B04, B05, B06 | 없음 |
| fitting | F01, F02, F03, F04 | 없음 |
| garment | G01, G02 | 없음 |

모듈 간 교차 중복도 없음 (B/F/G prefix로 구분됨).

#### depends_on 참조 정합성

| Step | depends_on | 참조 대상 존재 |
|------|------------|--------------|
| B01 | [] | (해당 없음) |
| B02 | body:B01 | 존재 |
| B03 | body:B02 | 존재 |
| B04 | body:B03 | 존재 |
| B05 | body:B04 | 존재 |
| B06 | body:B05 | 존재 |
| F01 | body:B01 | 존재 |
| F02 | fitting:F01, body:B03 | 모두 존재 |
| F03 | fitting:F02, body:B04 | 모두 존재 |
| F04 | fitting:F03 | 존재 |
| G01 | [] | (해당 없음) |
| G02 | garment:G01 | 존재 |

모든 depends_on 참조가 유효한 step ID를 가리킴.

#### unlocks ↔ depends_on 대칭성

모든 unlock 관계가 대상 step의 depends_on에 역방향으로 존재함. 불일치 없음.

#### dod.total vs len(dod.items)

| Step | dod.total | len(items) | 일치 |
|------|-----------|------------|------|
| B01 | 3 | 3 | O |
| B02 | 3 | 3 | O |
| B03 | 3 | 3 | O |
| B04 | 3 | 3 | O |
| B05 | 2 | 2 | O |
| B06 | 2 | 2 | O |
| F01 | 3 | 3 | O |
| F02 | 2 | 2 | O |
| F03 | 2 | 2 | O |
| F04 | 2 | 2 | O |
| G01 | 2 | 2 | O |
| G02 | 2 | 2 | O |

모든 step에서 total과 items 개수 일치.

#### Phase ↔ Step 참조

| Phase | 참조 steps | 존재 여부 |
|-------|-----------|----------|
| P01 | B01, F01, G01 | 모두 존재 |
| P02 | B02, B03, F02, G02 | 모두 존재 |
| P03 | B04, B05, F03, F04 | 모두 존재 |
| P04 | B06 | 존재 |

---

### A-2. Evidence-first 원칙 위반 (PLAN_v0.yaml)

**I-01**: 5개 DoD item에 `(Evidence: <path>)` 패턴이 누락됨.

| Step | Item 내용 | 관측 | 기대 |
|------|----------|------|------|
| B03 | "Production 산출물에 geometry_manifest.json 포함" | Evidence 경로 없음 | `(Evidence: <예시 경로>)` 포함 필요 |
| F03 | "fitting production pipeline 구현" | Evidence 경로 없음 | `(Evidence: <예시 경로>)` 포함 필요 |
| F03 | "fitting_facts_summary.json 대량 생성 가능" | Evidence 경로 없음 | `(Evidence: <예시 경로>)` 포함 필요 |
| F04 | "fitting facts validation 로직 구현" | Evidence 경로 없음 | `(Evidence: <예시 경로>)` 포함 필요 |
| F04 | "fitting KPI report 생성" | Evidence 경로 없음 | `(Evidence: <예시 경로>)` 포함 필요 |

- **Canon**: DoD_CHECKLISTS_v1.md — 모든 항목에 `(Evidence: <path>)` 패턴 사용
- **Risk**: 렌더러/에이전트가 완료 여부를 파일 존재로 판단할 수 없음
- **Minimal Fix**: 각 item에 `(Evidence: TBD)` 추가 (경로 미정이면 TBD 표기)

---

### A-3. Evidence 경로 레거시 표기 (PLAN_v0.yaml)

**I-02**: B02 DoD item의 Evidence 경로가 레거시 구조 사용.

| Step | Item | 관측 경로 | Canon/현행 대안 |
|------|------|---------|----------------|
| B02 | "측정 로직 구현" | `core/measurements/*.py` | `modules/body/measurements/*.py` 또는 `core/measurements/*.py` |

- **Canon**: DoD_CHECKLISTS_v1.md는 `modules/body/measurements/*.py 또는 core/measurements/*.py`로 병기
- **Risk**: 모듈 전환 후 경로가 맞지 않을 수 있음
- **Minimal Fix**: `(Evidence: core/measurements/*.py 또는 modules/body/measurements/*.py)` 병기

---

### A-4. EXPORT_CONTRACT_v0.md 내부 정합성

#### 고정 경로 명시

- `<lab_root>/exports/progress/PROGRESS_LOG.jsonl` — 명시됨, 명확
- `<lab_root>/exports/progress/PROGRESS_SNAPSHOT.json` — 명시됨, optional 표기됨
- `<lab_root>/exports/releases/<lane>_<YYYYMMDD>_<HHMMSS>/` — 명시됨, optional 표기됨

#### PROGRESS_LOG 필드 정의

9개 필드(ts, lab, module, step_id, dod_done_delta, dod_total, evidence_paths, rid, note) 모두 타입/필수 여부/설명이 명시됨.

#### Bootstrap vs Required DoD

Mode 1 (Bootstrap)과 Mode 2 (Automated) 분리 명시됨. 단, 아래 I-03 참조.

---

### A-5. 시제 불일치 (EXPORT_CONTRACT_v0.md)

**I-03**: §1 Overview의 시제가 Mode 2(자동)가 이미 활성인 것처럼 읽힘.

| 위치 | 관측 | 기대 | Risk |
|------|------|------|------|
| §1 "진행률 데이터는 각 Lab의 exports 디렉토리에서 수집하여 자동 집계한다." | 현재 시제 단정 | §5에 따르면 현재는 Mode 1 (수동) | 자동화가 이미 구현된 것으로 오독 가능 |

- **Minimal Fix**: "자동 집계한다" → "수집하여 집계한다 (수집 방식은 §5 Bootstrap/Automated 참조)"

---

### A-6. Release 경로 prefix 불일치

**I-04**: EXPORT_CONTRACT §2.3과 port_readiness_checklist §3.1의 release 경로 prefix가 다름.

| 문서 | 경로 형식 |
|------|---------|
| EXPORT_CONTRACT §2.3 | `<lab_root>/exports/releases/<lane>_<YYYYMMDD>_<HHMMSS>/` |
| port_readiness_checklist §3.1 | `releases/<lane>_<YYYYMMDD>_<HHMMSS>/` |

- **Canon**: port_readiness_checklist_v0.md는 `releases/` 기준 (lab_root 상대)
- **Risk**: Export contract가 `exports/` 하위에 releases를 두면 port_readiness의 경로와 불일치
- **Minimal Fix**: EXPORT_CONTRACT §2.3에 "port_readiness_checklist_v0.md §3.1의 `releases/` 경로와의 관계: export 계약에서는 `exports/releases/`를 사용하며, 이는 lab의 exports 표면 내부 경로임. lab 내부의 `releases/` 경로와는 별개." 주석 추가

---

### A-7. body 모듈 이벤트 소스 미정의

**I-05**: LAB_SOURCES_v0.yaml과 EXPORT_CONTRACT_v0.md 모두 fitting_lab, garment_lab만 정의. body 모듈 진행률의 이벤트 소스(ai_model hub 자체?)가 명시되지 않음.

| 관측 | 기대 | Risk |
|------|------|------|
| sources에 fitting_lab, garment_lab만 존재 | body 모듈의 이벤트 소스 명시 필요 | 렌더러가 body 모듈 진행률을 수집할 수 없음 |

- **Minimal Fix**: LAB_SOURCES_v0.yaml에 `hub` (또는 `ai_model`) 소스 항목 추가, 또는 body 모듈은 hub 내부에서 직접 관리됨을 주석으로 명시

---

### A-8. LAB_SOURCES_v0.yaml TBD placeholder 구분 불가

**I-06**: fitting_lab과 garment_lab 모두 동일한 `TBD_ABSOLUTE_PATH` 문자열 사용.

| 관측 | 기대 | Risk |
|------|------|------|
| 두 lab 모두 `TBD_ABSOLUTE_PATH` | `TBD_FITTING_LAB_PATH`, `TBD_GARMENT_LAB_PATH` 등 구분 | 일괄 치환(find-replace) 시 두 lab에 동일 경로가 설정될 위험 |

- **Minimal Fix**: 각 lab별 고유 placeholder 사용

---

### A-9. EXPORT_CONTRACT_v0.md §3.2 제목 용어 충돌

**I-07**: "Validation Rules" 제목이 프로젝트의 L4 Validation 레이어와 용어 충돌.

| 관측 | 기대 | Risk |
|------|------|------|
| §3.2 제목: "Validation Rules" | "Field Constraints" 또는 "Schema Rules" | L4 Validation과 혼동 가능 |

- **Minimal Fix**: 제목을 "3.2 Field Constraints" 또는 "3.2 Schema Rules"로 변경

---

### A-10. PROJECT_DASHBOARD.md 정합성

- GENERATED 헤더: HTML 주석으로 5줄 존재 — 명확
- Data Sources 테이블의 경로: PLAN_v0.yaml, LAB_SOURCES_v0.yaml, EXPORT_CONTRACT_v0.md — 모두 실제 파일 경로와 일치
- Phase×Module 매트릭스: P01~P04 × body/fitting/garment — PLAN_v0.yaml의 phases와 일치
- Module Progress 표: Total 합계 — body=16, fitting=9, garment=4 (총 29) — PLAN_v0.yaml과 일치
- Unlock Status 표: 12 steps의 depends_on — PLAN_v0.yaml과 일치
- Recent Events 표: 구조 존재, placeholder 상태

---

### A-11. Dashboard placeholder 렌더링 위험

**I-08**: Phase×Module 매트릭스에서 `_/_` placeholder 사용.

| 관측 | 기대 | Risk |
|------|------|------|
| `B01: _/_` | `B01: —/3` 또는 `` B01: `—/3` `` | `_/_`가 일부 Markdown 렌더러에서 이탤릭으로 해석될 가능성 |

- **Minimal Fix**: `_/_` → `—/—` 또는 숫자 placeholder(`0/3`) 사용

---

### A-12. "Dependencies Met?" 표현

**I-09**: Unlock Status 테이블 칼럼명 "Dependencies Met?"와 렌더 힌트 "YES/NO".

| 관측 | 기대 | Risk |
|------|------|------|
| 칼럼명: "Dependencies Met?", 값: "YES/NO" | "Unlock Status" 칼럼, 값: "UNLOCKED/BLOCKED" | "Met" + "YES/NO"가 판정(judgment) 언어로 오독 가능 |

- **Risk 수준**: 낮음 (산술 비교 `done == total`이므로 facts-based). 그러나 프로젝트의 facts-only 원칙에 더 부합하는 용어 사용 권장.
- **Minimal Fix**: 칼럼명 → "Unlock Status", 값 → "UNLOCKED / BLOCKED"

---

## B. Canon Compliance Checks

### B-1. Facts-only 원칙

| 문서 | 관측 |
|------|------|
| PLAN_v0.yaml | DoD items는 사실 기록 (evidence path 기반). 판정 언어 없음. |
| EXPORT_CONTRACT_v0.md | §6에 "PASS/FAIL 판정을 넣지 않는다" 명시. 필드에 판정 값 없음. |
| LAB_SOURCES_v0.yaml | 경로 매핑만 포함. 판정 요소 없음. |
| PROJECT_DASHBOARD.md | I-09 외에는 판정 언어 없음. |

Facts-only 원칙 준수. I-09는 경미한 용어 조정 권장.

### B-2. Evidence-first 원칙

| 문서 | 관측 |
|------|------|
| PLAN_v0.yaml | 12 steps 중 7 steps의 모든 items에 Evidence 패턴 있음. 5개 items 누락 (I-01). |
| EXPORT_CONTRACT_v0.md | evidence_paths 필드 필수, 빈 배열 금지 — 원칙 준수. |

I-01 패치 적용 시 완전 준수.

### B-3. Append-only 원칙

| 문서 | 관측 |
|------|------|
| EXPORT_CONTRACT_v0.md §2.1 | "한 번 기록된 줄은 수정/삭제 금지" 명시 |
| EXPORT_CONTRACT_v0.md §3.2 | "시간순 append만 허용 (과거 시점 삽입 금지)" 명시 |

Append-only 원칙 준수.

### B-4. Naming 제약 (interface_ledger_v0.md §2)

| 확인 항목 | 관측 |
|----------|------|
| Dashboard 문서가 fitting 출력을 `fitting_facts_summary.json`으로 참조하는가? | PLAN_v0.yaml F02 DoD item에 "fitting_facts_summary.json 스키마 준수" 기재 — 일치 |
| body 출력을 `facts_summary.json`으로 참조하는가? | PLAN_v0.yaml B04 DoD item에 "facts_summary.json 생성" 기재 — 일치 |

Naming Policy 준수.

### B-5. Milestone 형식 (interface_ledger_v0.md §4.2)

| 확인 항목 | 관측 |
|----------|------|
| PLAN_v0.yaml milestone 값 | `M01_baseline` — `M<NN>_<tag>` 형식 준수 |
| EXPORT_CONTRACT Example 1 rid | `fitting_v0_facts__M01_baseline__r01` — `<lane_slug>__<milestone_id>__r<NN>` 형식 준수 |

Round/Milestone 형식 준수.

### B-6. Version Policy (interface_ledger_v0.md §3)

Dashboard 문서는 cross-module artifact를 생성하지 않으므로 4 version keys 요구 대상 아님. PROGRESS_LOG.jsonl은 progress artifact이며 cross-module artifact가 아님. 충돌 없음.

---

## C. Mermaid Checks

### C-1. 위치 및 라벨

- PROJECT_DASHBOARD.md 하단에 "## Dependency Graph (Mermaid, optional)" 전용 섹션 존재 — 적합
- 섹션 제목에 "optional" 명시 — 적합
- 하단에 "Text tables above are the primary view. Mermaid is supplementary only." 명시 — 적합

### C-2. 코드 펜스 및 구문

- ` ```mermaid ` / ` ``` ` 펜스 정상
- `graph LR` 키워드 유효
- 노드 정의: `B01[B01 Contract]` 등 — 대괄호 라벨 구문 유효
- 화살표: `-->` 사용 — 유효

### C-3. 엣지 정합성 (Mermaid ↔ PLAN_v0.yaml)

| Mermaid 엣지 | PLAN depends_on | 일치 |
|-------------|----------------|------|
| B01 --> B02 | B02 depends body:B01 | O |
| B02 --> B03 | B03 depends body:B02 | O |
| B03 --> B04 | B04 depends body:B03 | O |
| B04 --> B05 | B05 depends body:B04 | O |
| B05 --> B06 | B06 depends body:B05 | O |
| B01 --> F01 | F01 depends body:B01 | O |
| F01 --> F02 | F02 depends fitting:F01 | O |
| B03 --> F02 | F02 depends body:B03 | O |
| F02 --> F03 | F03 depends fitting:F02 | O |
| B04 --> F03 | F03 depends body:B04 | O |
| F03 --> F04 | F04 depends fitting:F03 | O |
| G01 --> G02 | G02 depends garment:G01 | O |

12개 엣지 모두 PLAN_v0.yaml depends_on과 일치. 누락/추가 엣지 없음.

### C-4. 텍스트 표 대체 여부

Mermaid가 텍스트 표를 대체하지 않음 (별도 섹션, 보조 역할 명시). 적합.

---

## D. Ambiguity & Inference Traps

### D-1. 자동화 존재 단정 (EXPORT_CONTRACT §1)

> "진행률 데이터는 각 Lab의 exports 디렉토리에서 수집하여 **자동** 집계한다."

- **위험**: 자동 수집 스크립트가 이미 존재하는 것처럼 읽힘. §5에서 현재는 Mode 1(수동)이라 명시하지만, §1만 읽으면 오독 가능.
- **Minimal Rewrite**: "진행률 데이터는 각 Lab의 exports 디렉토리에서 수집하여 집계한다 (수집 방식: §5 참조)."

### D-2. 렌더러 요구사항 단정 (EXPORT_CONTRACT §2.2)

> "없어도 렌더러는 PROGRESS_LOG.jsonl만으로 **동작해야 함**"

- **위험**: 렌더러가 아직 존재하지 않음. "해야 함"은 미래 구현에 대한 요구사항이지만, 현재 존재하는 것처럼 읽힘.
- **Minimal Rewrite**: "렌더러 구현 시 PROGRESS_LOG.jsonl만으로 동작 가능해야 함 (snapshot 없이도 집계 가능)"

### D-3. PLAN_v0.yaml milestone 범위 미명시

> `milestone: M01_baseline` (top-level)

- **위험**: 모든 steps가 M01_baseline에 속하는지, 아니면 일부 steps가 다른 milestone에 속할 수 있는지 명시되지 않음.
- **Minimal Rewrite**: 헤더 주석에 `# Rule: 이 PLAN의 모든 steps는 milestone 필드에 명시된 단일 milestone에 속한다.` 추가

### D-4. 파일 존재 단정 없음 확인

PLAN_v0.yaml의 Evidence 경로들은 모두 DoD 완료 조건으로만 사용되며, "이 파일이 존재한다"는 단정이 아님. 적합.
단, B02 item의 `core/measurements/*.py`는 레거시 경로일 수 있으므로 I-02 참조.

### D-5. 출처 없는 명령어/도구 언급

Dashboard 4개 파일에서 출처 없는 명령어나 도구 언급 없음. EXPORT_CONTRACT §2.3에서 port_readiness_checklist_v0.md §3.1을 정확히 참조. 적합.

---

## 요약: 식별된 이슈 목록

| ID | 분류 | 파일 | 요약 |
|----|------|------|------|
| I-01 | Evidence-first 위반 | PLAN_v0.yaml | 5개 DoD item에 Evidence 경로 누락 |
| I-02 | 레거시 경로 | PLAN_v0.yaml | B02 evidence에 `core/` 경로 단독 사용 |
| I-03 | 시제 불일치 | EXPORT_CONTRACT_v0.md | §1 "자동 집계한다" vs §5 Mode 1 수동 현재 |
| I-04 | 경로 prefix 불일치 | EXPORT_CONTRACT_v0.md | §2.3 `exports/releases/` vs port_readiness `releases/` |
| I-05 | 이벤트 소스 누락 | LAB_SOURCES_v0.yaml | body 모듈 이벤트 소스 미정의 |
| I-06 | TBD 구분 불가 | LAB_SOURCES_v0.yaml | 두 lab 동일 TBD placeholder |
| I-07 | 용어 충돌 | EXPORT_CONTRACT_v0.md | §3.2 "Validation Rules" vs L4 Validation |
| I-08 | 렌더링 위험 | PROJECT_DASHBOARD.md | `_/_` placeholder |
| I-09 | 판정 언어 | PROJECT_DASHBOARD.md | "Dependencies Met?" + "YES/NO" |
| I-10 | 범위 미명시 | PLAN_v0.yaml | milestone 범위가 전체 steps 포함인지 명시 없음 |
