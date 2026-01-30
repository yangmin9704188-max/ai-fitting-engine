# Dashboard Contract v0 — Patch Blocks

각 패치는 최소 범위로 제한됨. 복사/붙여넣기 가능.

---

## Patch 1: PLAN_v0.yaml — Evidence 누락 5건 수정 (I-01)

**대상**: `docs/ops/dashboard/PLAN_v0.yaml`

### 1-a. B03 item 3 (line 100 부근)

**Before**:
```yaml
            - "Production 산출물에 geometry_manifest.json 포함"
```

**After**:
```yaml
            - "Production 산출물에 geometry_manifest.json 포함 (Evidence: verification/runs/**/geometry_manifest.json)"
```

### 1-b. F03 items (line 183-185 부근)

**Before**:
```yaml
          items:
            - "fitting production pipeline 구현"
            - "fitting_facts_summary.json 대량 생성 가능"
```

**After**:
```yaml
          items:
            - "fitting production pipeline 구현 (Evidence: TBD)"
            - "fitting_facts_summary.json 대량 생성 가능 (Evidence: TBD)"
```

### 1-c. F04 items (line 196-198 부근)

**Before**:
```yaml
          items:
            - "fitting facts validation 로직 구현"
            - "fitting KPI report 생성"
```

**After**:
```yaml
          items:
            - "fitting facts validation 로직 구현 (Evidence: TBD)"
            - "fitting KPI report 생성 (Evidence: TBD)"
```

---

## Patch 2: PLAN_v0.yaml — B02 레거시 경로 병기 (I-02)

**대상**: `docs/ops/dashboard/PLAN_v0.yaml`
**위치**: B02 dod items, item 2 (line 85 부근)

**Before**:
```yaml
            - "측정 로직 구현 (Evidence: core/measurements/*.py)"
```

**After**:
```yaml
            - "측정 로직 구현 (Evidence: core/measurements/*.py 또는 modules/body/measurements/*.py)"
```

---

## Patch 3: PLAN_v0.yaml — milestone 범위 주석 추가 (I-10)

**대상**: `docs/ops/dashboard/PLAN_v0.yaml`
**위치**: 헤더 주석 블록 끝 (line 8 뒤)

**추가**:
```yaml
# Rule: 이 파일의 모든 steps는 milestone 필드에 명시된 단일 milestone에 속한다.
# Rule: milestone 전환 시 새 PLAN 파일(PLAN_v1.yaml 등)을 생성한다.
```

---

## Patch 4: EXPORT_CONTRACT_v0.md — §1 시제 수정 (I-03)

**대상**: `docs/ops/dashboard/EXPORT_CONTRACT_v0.md`
**위치**: §1 Overview, line 11 부근

**Before**:
```markdown
Dashboard는 **렌더 결과물**이며, 사람이 직접 편집하지 않는다.
진행률 데이터는 각 Lab의 exports 디렉토리에서 수집하여 자동 집계한다.
```

**After**:
```markdown
Dashboard는 **렌더 결과물**이며, 사람이 직접 편집하지 않는다.
진행률 데이터는 각 Lab의 exports 디렉토리에서 수집하여 집계한다 (수집 방식: §5 Bootstrap vs Automated 참조).
```

---

## Patch 5: EXPORT_CONTRACT_v0.md — §2.2 렌더러 시제 수정 (D-2)

**대상**: `docs/ops/dashboard/EXPORT_CONTRACT_v0.md`
**위치**: §2.2 Optional, line 44 부근

**Before**:
```markdown
- 없어도 렌더러는 PROGRESS_LOG.jsonl만으로 동작해야 함
```

**After**:
```markdown
- 렌더러 구현 시, PROGRESS_LOG.jsonl만으로 동작 가능해야 함 (snapshot 부재 허용)
```

---

## Patch 6: EXPORT_CONTRACT_v0.md — §2.3 경로 관계 주석 (I-04)

**대상**: `docs/ops/dashboard/EXPORT_CONTRACT_v0.md`
**위치**: §2.3 Release Evidence, line 53 뒤

**추가** (기존 "경로 형식은..." 줄 바로 아래):
```markdown
- **참고**: port_readiness_checklist_v0.md §3.1의 `releases/` 경로는 lab 내부 기준. export 계약의 `exports/releases/`는 exports 표면 내부 경로이며, lab 내부 `releases/`와는 독립된 사본 위치.
```

---

## Patch 7: EXPORT_CONTRACT_v0.md — §3.2 제목 변경 (I-07)

**대상**: `docs/ops/dashboard/EXPORT_CONTRACT_v0.md`
**위치**: §3.2 제목 (line 74 부근)

**Before**:
```markdown
### 3.2 Validation Rules
```

**After**:
```markdown
### 3.2 Field Constraints
```

---

## Patch 8: LAB_SOURCES_v0.yaml — TBD 구분 + body 소스 (I-05, I-06)

**대상**: `docs/ops/dashboard/LAB_SOURCES_v0.yaml`
**위치**: sources 블록 전체 (line 11~18)

**Before**:
```yaml
sources:
  fitting_lab:
    progress_log_path: "TBD_ABSOLUTE_PATH/exports/progress/PROGRESS_LOG.jsonl"
    progress_snapshot_path: "TBD_ABSOLUTE_PATH/exports/progress/PROGRESS_SNAPSHOT.json"  # optional

  garment_lab:
    progress_log_path: "TBD_ABSOLUTE_PATH/exports/progress/PROGRESS_LOG.jsonl"
    progress_snapshot_path: "TBD_ABSOLUTE_PATH/exports/progress/PROGRESS_SNAPSHOT.json"  # optional
```

**After**:
```yaml
sources:
  # body 모듈은 중앙 Hub(ai_model) 내부에서 직접 관리.
  # body 이벤트는 hub 로컬 PROGRESS_LOG.jsonl에 기록한다.
  hub:
    progress_log_path: "TBD_HUB_PATH/exports/progress/PROGRESS_LOG.jsonl"
    progress_snapshot_path: "TBD_HUB_PATH/exports/progress/PROGRESS_SNAPSHOT.json"  # optional
    modules: ["body"]

  fitting_lab:
    progress_log_path: "TBD_FITTING_LAB_PATH/exports/progress/PROGRESS_LOG.jsonl"
    progress_snapshot_path: "TBD_FITTING_LAB_PATH/exports/progress/PROGRESS_SNAPSHOT.json"  # optional
    modules: ["fitting"]

  garment_lab:
    progress_log_path: "TBD_GARMENT_LAB_PATH/exports/progress/PROGRESS_LOG.jsonl"
    progress_snapshot_path: "TBD_GARMENT_LAB_PATH/exports/progress/PROGRESS_SNAPSHOT.json"  # optional
    modules: ["garment"]
```

---

## Patch 9: PROJECT_DASHBOARD.md — placeholder 및 칼럼명 (I-08, I-09)

**대상**: `docs/ops/PROJECT_DASHBOARD.md`

### 9-a. Phase×Module 매트릭스 (line 28-33)

**Before**:
```markdown
| Phase | Body | Fitting | Garment |
|-------|------|---------|---------|
| **P01** Contract & Data | B01: _/_ | F01: _/_ | G01: _/_ |
| **P02** Geometry & Measurement | B02: _/_ , B03: _/_ | F02: _/_ | G02: _/_ |
| **P03** Validation & Confidence | B04: _/_ , B05: _/_ | F03: _/_ , F04: _/_ | — |
| **P04** Application | B06: _/_ | — | — |
```

**After**:
```markdown
| Phase | Body | Fitting | Garment |
|-------|------|---------|---------|
| **P01** Contract & Data | B01: —/3 | F01: —/3 | G01: —/2 |
| **P02** Geometry & Measurement | B02: —/3 , B03: —/3 | F02: —/2 | G02: —/2 |
| **P03** Validation & Confidence | B04: —/3 , B05: —/2 | F03: —/2 , F04: —/2 | — |
| **P04** Application | B06: —/2 | — | — |
```

### 9-b. Unlock Status 칼럼명 (line 75)

**Before**:
```markdown
| Step | Depends On | Dependencies Met? |
```

**After**:
```markdown
| Step | Depends On | Unlock Status |
```

### 9-c. Unlock Status 렌더 힌트 (line 90)

**Before**:
```markdown
> `(auto)` = renderer fills YES/NO based on dependency step completion (done == total)
```

**After**:
```markdown
> `(auto)` = renderer fills UNLOCKED/BLOCKED based on dependency step completion (done == total)
```

### 9-d. Data Sources 테이블에 hub 추가 (I-05 관련, line 16-22)

**Before**:
```markdown
| Source | Path | Status |
|--------|------|--------|
| Plan (SSoT) | `docs/ops/dashboard/PLAN_v0.yaml` | (auto) |
| Lab Sources | `docs/ops/dashboard/LAB_SOURCES_v0.yaml` | (auto) |
| Export Contract | `docs/ops/dashboard/EXPORT_CONTRACT_v0.md` | (auto) |
| fitting_lab log | (from LAB_SOURCES_v0.yaml) | (auto) |
| garment_lab log | (from LAB_SOURCES_v0.yaml) | (auto) |
```

**After**:
```markdown
| Source | Path | Status |
|--------|------|--------|
| Plan (SSoT) | `docs/ops/dashboard/PLAN_v0.yaml` | (auto) |
| Lab Sources | `docs/ops/dashboard/LAB_SOURCES_v0.yaml` | (auto) |
| Export Contract | `docs/ops/dashboard/EXPORT_CONTRACT_v0.md` | (auto) |
| hub (body) log | (from LAB_SOURCES_v0.yaml) | (auto) |
| fitting_lab log | (from LAB_SOURCES_v0.yaml) | (auto) |
| garment_lab log | (from LAB_SOURCES_v0.yaml) | (auto) |
```
