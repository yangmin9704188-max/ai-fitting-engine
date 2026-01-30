<!-- GENERATED — DO NOT EDIT MANUALLY -->
<!-- This file is rendered by tools/render_dashboard_v0.py -->
<!-- Manual edits will be overwritten on next render cycle. -->
<!-- To change plan/structure: edit docs/ops/dashboard/PLAN_v0.yaml -->
<!-- To change data sources: edit docs/ops/dashboard/LAB_SOURCES_v0.yaml -->

# Project Dashboard

**Milestone**: M01_baseline
**Rendered**: 2026-01-29T09:46:57Z

---

## Data Sources

| Source | Path | Status |
|--------|------|--------|
| Plan (SSoT) | `docs/ops/dashboard/PLAN_v0.yaml` | loaded |
| Lab Sources | `docs/ops/dashboard/LAB_SOURCES_v0.yaml` | loaded |
| Export Contract | `docs/ops/dashboard/EXPORT_CONTRACT_v0.md` | reference |
| hub (body) log | `C:/Users/caino/Desktop/AI_model/exports/progress/PROGRESS_LOG.jsonl` | loaded |
| fitting_lab (fitting) log | `TBD_FITTING_LAB_PATH/exports/progress/PROGRESS_LOG.jsonl` | TBD |
| garment_lab (garment) log | `TBD_GARMENT_LAB_PATH/exports/progress/PROGRESS_LOG.jsonl` | TBD |

---

## Phase x Module Matrix

| Phase | Body | Fitting | Garment |
|-------|------|---------|---------|
| **P01** Contract & Data Foundation | B01: 3/3 | F01: 0/3 | G01: 0/2 |
| **P02** Geometry & Measurement | B02: 1/3 , B03: 0/3 | F02: 0/2 | G02: 0/2 |
| **P03** Validation & Confidence | B04: 0/3 , B05: 0/2 | F03: 0/2 , F04: 0/2 | — |
| **P04** Application | B06: 0/2 | — | — |

> Cell format: `<step_id>: <done>/<total>`

---

## Module Progress

### Body

| Step | Name | Layer | Done | Total | Progress | Unlocks |
|------|------|-------|------|-------|----------|---------|
| B01 | Standard Keys Contract | L1 | 3 | 3 | 100% | body:B02, fitting:F01 |
| B02 | Geometry Implementation | L2 | 1 | 3 | 33% | body:B03 |
| B03 | Production Pipeline | L3 | 0 | 3 | 0% | body:B04, fitting:F02 |
| B04 | Validation Facts | L4 | 0 | 3 | 0% | body:B05, fitting:F03 |
| B05 | Confidence Analysis | L5 | 0 | 2 | 0% | body:B06 |
| B06 | Application Model | L6 | 0 | 2 | 0% | — |
| **Total** | | | **4** | **16** | **25%** | |

### Fitting

| Step | Name | Layer | Done | Total | Progress | Unlocks |
|------|------|-------|------|-------|----------|---------|
| F01 | Fitting Interface Contract | L1 | 0 | 3 | 0% | fitting:F02 |
| F02 | Fitting Geometry & Runner | L2 | 0 | 2 | 0% | fitting:F03 |
| F03 | Fitting Production | L3 | 0 | 2 | 0% | fitting:F04 |
| F04 | Fitting Validation | L4 | 0 | 2 | 0% | — |
| **Total** | | | **0** | **9** | **0%** | |

### Garment

| Step | Name | Layer | Done | Total | Progress | Unlocks |
|------|------|-------|------|-------|----------|---------|
| G01 | Garment Contract | L1 | 0 | 2 | 0% | garment:G02 |
| G02 | Garment Geometry | L2 | 0 | 2 | 0% | — |
| **Total** | | | **0** | **4** | **0%** | |

---

## Unlock Status

| Step | Depends On | Unlock Status |
|------|------------|---------------|
| B01 | (none) | UNLOCKED |
| B02 | body:B01 | UNLOCKED |
| B03 | body:B02 | BLOCKED |
| B04 | body:B03 | BLOCKED |
| B05 | body:B04 | BLOCKED |
| B06 | body:B05 | BLOCKED |
| F01 | body:B01 | UNLOCKED |
| F02 | fitting:F01, body:B03 | BLOCKED |
| F03 | fitting:F02, body:B04 | BLOCKED |
| F04 | fitting:F03 | BLOCKED |
| G01 | (none) | UNLOCKED |
| G02 | garment:G01 | BLOCKED |

> UNLOCKED = all dependencies have done == total. BLOCKED = at least one dependency incomplete.

---

## Warnings (facts-only)

- source 'fitting_lab': path is TBD (TBD_FITTING_LAB_PATH/exports/progress/PROGRESS_LOG.jsonl)
- source 'garment_lab': path is TBD (TBD_GARMENT_LAB_PATH/exports/progress/PROGRESS_LOG.jsonl)

---

## Recent Events

| # | Timestamp | Lab | Module | Step | Delta | Evidence Count | Note |
|---|-----------|-----|--------|------|-------|----------------|------|
| 1 | 2026-01-29T18:46:20.111017+09:00 | hub | body | B02 | 1 | 1 | geometry schema defined |
| 2 | 2026-01-29T18:46:11.140769+09:00 | hub | body | B01 | 1 | 1 | contract JSON |
| 3 | 2026-01-29T18:45:57.808415+09:00 | hub | body | B01 | 2 | 2 | standard keys + unit standard documented |

> Maximum 20 most recent events displayed. Full history in each lab's PROGRESS_LOG.jsonl.

---

## Dependency Graph (Mermaid, optional viewer support)

```mermaid
graph LR
    B01[B01 Standard Keys Contract] --> B02[B02 Geometry Implementation]
    B02[B02 Geometry Implementation] --> B03[B03 Production Pipeline]
    B03[B03 Production Pipeline] --> B04[B04 Validation Facts]
    B04[B04 Validation Facts] --> B05[B05 Confidence Analysis]
    B05[B05 Confidence Analysis] --> B06[B06 Application Model]
    B01[B01 Standard Keys Contract] --> F01[F01 Fitting Interface Contract]
    F01[F01 Fitting Interface Contract] --> F02[F02 Fitting Geometry & Runner]
    B03[B03 Production Pipeline] --> F02[F02 Fitting Geometry & Runner]
    F02[F02 Fitting Geometry & Runner] --> F03[F03 Fitting Production]
    B04[B04 Validation Facts] --> F03[F03 Fitting Production]
    F03[F03 Fitting Production] --> F04[F04 Fitting Validation]
    G01[G01 Garment Contract] --> G02[G02 Garment Geometry]
```

> Text tables above are the primary view. Mermaid is supplementary only.
