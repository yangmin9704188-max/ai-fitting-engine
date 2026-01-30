# Port Event Note Template v0

**Purpose**: fitting_lab → main 포트 이벤트 기록용 템플릿

---

## Port Event Record

**Date**: YYYY-MM-DD
**Milestone**: M<NN>_<tag> (예: M01_alpha)
**Round ID**: <lane>__<milestone>__r<NN> (해당 시)

### Allowlist Files Copied

| # | Source (fitting_lab) | Destination (main) | Status |
|---|---------------------|-------------------|--------|
| 1 | labs/runners/run_fitting_v0_facts.py | modules/fitting/runners/run_fitting_v0_facts.py | OK/SKIP |
| 2 | labs/specs/fitting_manifest.schema.json | modules/fitting/specs/fitting_manifest.schema.json | OK/SKIP |
| 3 | contracts/fitting_interface_v0.md | docs/contract/fitting_interface_v0.md | OK/SKIP |

### Release Snapshot

**Location**: `releases/fitting_v0_YYYYMMDD_HHMMSS/`
**Created by**: (담당자/에이전트)

### Verification

- [ ] Pre-port checks passed (ledger compliance)
- [ ] Files copied successfully
- [ ] Post-port smoke run executed (해당 시)
- [ ] Always-emit files exist

### Notes

(추가 사항 기록)

---

**Recorded by**: (담당자)
**PR Link**: (해당 시)
