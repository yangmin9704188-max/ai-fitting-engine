# Ops Index

**Purpose**: Central index for operational automation, documentation, and registry systems.

## Baseline Configuration

### curated_v0 Lane (Fixed)
- **baseline_tag (alias)**: `curated-v0-realdata-v0.1`
- **baseline_run_dir**: `verification/runs/facts/curated_v0/round20_20260125_164801`
- **baseline_report**: `reports/validation/curated_v0_facts_round1.md`
- **lane**: `curated_v0` (fixed)

## Core Registries

### Round Registry
- **Path**: [`docs/verification/round_registry.json`](../verification/round_registry.json)
- **Purpose**: Tracks all verification rounds, baseline configuration, and round history per lane
- **Schema**: `round_registry@1`

### Golden Registry
- **Path**: [`docs/verification/golden_registry.json`](../verification/golden_registry.json)
- **Purpose**: Global registry for NPZ files (golden datasets), tracks provenance, schema, and metadata
- **Schema**: `golden_registry@1`

### Coverage Backlog
- **Path**: [`docs/verification/coverage_backlog.md`](../verification/coverage_backlog.md)
- **Purpose**: Facts-only tracking of all-null keys (NaN 100%) across rounds
- **Policy**: No judgment, no auto-fix, accumulation only

## Golden S0 Freeze

**Tag**: `golden-s0-v0.1`  
**Commit**: `cc15544bc26b244d28463568d1d32660679979d3`  
**Date**: 2026-01-25

### Freeze Rule
**이후 발생하는 모든 Geometric/Validation 이슈는 S0 generator를 수정하는 것이 아니라 metadata/provenance/validation으로 해결한다.**

### Reproduce Commands
```bash
rm -f verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz
py verification/datasets/golden/core_measurements_v0/create_s0_dataset.py
py verification/runners/run_geo_v0_facts_round1.py \
  --npz verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz \
  --n_samples 20 \
  --out_dir verification/runs/facts/geo_v0/round17_valid10_expanded
```

### Reference
- **Documentation**: [`docs/verification/golden_s0_freeze_v0.md`](../verification/golden_s0_freeze_v0.md)
- **Baseline Report**: `reports/validation/geo_v0_facts_round17_valid10_expanded.md`

## Database

- **Guide**: [`DB_GUIDE.md`](../../DB_GUIDE.md)
- **Schema**: `db/schema.sql`
- **Purpose**: Artifact index (search/aggregation/status), not document storage

## 5-Layer Organization Principle

**5-Layer는 "폴더 분리"가 아니라 "인덱스/레지스트리로 묶기" 원칙을 따릅니다.**

- Policy/Spec/Run/Report는 artifact 타입 (교차 분류)
- 5-Layer는 논리 흐름/분류 축
- 레지스트리와 인덱스로 연결 관계를 관리
- 폴더 구조는 물리적 저장소일 뿐, 논리적 분류는 레지스트리로 표현

## Templates

- [`templates/report_facts_stub.md`](templates/report_facts_stub.md): Facts-only report template
- [`templates/adr_stub.md`](templates/adr_stub.md): Architecture Decision Record template
- [`templates/spec_stub.md`](templates/spec_stub.md): Specification template

## Operational Tools

- `baselines.json`: Lane baseline configuration
- `cursor_prompt_header.md`: Standardized prompt header for Cursor AI
- `round_runbook.md`: Round execution runbook

## Commit Policy

- **Policy**: [`COMMIT_POLICY.md`](COMMIT_POLICY.md)
- **Purpose**: Define "what to commit" based on signals (no judgment, no thresholds)
- **Key Sections**:
  - Non-negotiables (PASS/FAIL 금지, semantic 재논의 금지, 로컬 산출물 커밋 금지)
  - Commit targets / Non-targets
  - Golden candidate signals
  - Action mapping (권고/후속 작업)
  - Evidence checklist

## Judgments

- **Index**: [`../judgments/INDEX.md`](../judgments/INDEX.md)
- **Policy**: [`JUDGMENTS_POLICY.md`](JUDGMENTS_POLICY.md)
- **Runbook**: [`JUDGMENTS_RUNBOOK.md`](JUDGMENTS_RUNBOOK.md)
- **Template**: [`../judgments/templates/JUDGMENT_ENTRY_TEMPLATE.md`](../judgments/templates/JUDGMENT_ENTRY_TEMPLATE.md)
- **Purpose**: Archive lifecycle for confirmed judgment/decision documents (CANDIDATES → Judgments)
