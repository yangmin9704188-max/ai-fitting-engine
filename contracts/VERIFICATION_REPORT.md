# Port Checklist Verification Report

**Status**: VERIFICATION COMPLETE
**Date**: 2026-01-29
**Scope**: port_readiness_checklist_v0.md, port_event_note_template_v0.md vs interface_ledger_v0.md

---

## 1. Canon Coverage Map

### 1.1 interface_ledger_v0.md Canon Locks

| Canon | Ledger Section | port_readiness_checklist_v0.md | Status |
|-------|---------------|-------------------------------|--------|
| Path=C | §1 | §4.1 Row 1, §4.3 `path_base` | ✅ COVERED |
| Name=B | §2 | §4.1 Row 2, §6.3 `fitting_facts_summary.json` | ✅ COVERED |
| Version=C | §3 | §4.1 Row 3, §4.3 (6 keys listed) | ✅ COVERED |
| Round | §4 | §4.1 Row 6 | ✅ COVERED |
| NaN→null | §5 | §4.1 Row 4 | ✅ COVERED |
| Warnings | §6 | §4.1 Row 5 | ✅ COVERED |

**Port Checklist Canon Coverage: 6/6 (100%)**

### 1.2 port_event_note_template_v0.md Coverage

| Template Section | Canon Reference | Status |
|-----------------|-----------------|--------|
| Allowlist Files | §2 of checklist | ✅ ALIGNED |
| Release Snapshot | §3 of checklist | ✅ ALIGNED |
| Verification Checks | §4-6 of checklist | ✅ ALIGNED |

---

## 2. Mismatch List (Main Repo Files vs Ledger)

### 2.1 CRITICAL: Filename Mismatch

**Location**: `docs/contract/fitting_interface_v0.md`

| Line | Current Value | Canon Value (Ledger §2) |
|------|--------------|------------------------|
| 38 | `"facts_summary.json"` | `"fitting_facts_summary.json"` |
| 63 | `### facts_summary.json` | `### fitting_facts_summary.json` |
| 65 | `"facts_summary.v0"` | `"fitting_facts_summary.v0"` |

**Location**: `modules/fitting/specs/fitting_manifest.schema.json`

| Line | Current Value | Canon Value (Ledger §2) |
|------|--------------|------------------------|
| 139-141 | `"facts_summary": { "const": "facts_summary.json" }` | `"fitting_facts_summary": { "const": "fitting_facts_summary.json" }` |

### 2.2 CRITICAL: Missing 4 Version Keys

**Location**: `modules/fitting/specs/fitting_manifest.schema.json` → provenance object

Canon requires (Ledger §3):
```
[ ] snapshot_version
[ ] semantic_version
[ ] geometry_impl_version
[ ] dataset_version
```

Current schema only has: `schema_version`, `code_fingerprint`, `input_fingerprints`

### 2.3 CRITICAL: Missing Path Policy Fields

**Location**: `modules/fitting/specs/fitting_manifest.schema.json` → provenance object

Canon requires (Ledger §1):
```
[ ] path_base (enum: manifest_dir, run_dir)
[ ] manifest_path (string)
```

Current schema: NOT PRESENT

### 2.4 WARNING: Warnings Format Drift

**Location**: `docs/contract/fitting_interface_v0.md` lines 58, 78

| Current | Canon (Ledger §6) |
|---------|------------------|
| `dict[CODE] -> list[string]` | `{count, sample_messages, truncated}` |

**Note**: Ledger §6.3 allows simple format for internal use, but cross-module output requires canonical format.

---

## 3. Tooling Alignment

### 3.1 Tool Drift Observation

**Tool**: `tools/inspect_run.ps1` (fitting_lab)
**Issue**: References `facts_summary.json` but canonical output filename is `fitting_facts_summary.json`
**Status**: DOCUMENTED in port_readiness_checklist_v0.md §6.2 (관측 사항)
**Action**: 도구 업데이트 여부는 별도 판단 (per checklist)

### 3.2 Snapshot Tool

**Tool**: `tools/make_release_snapshot.ps1` (fitting_lab)
**Status**: Referenced in port_readiness_checklist_v0.md §3.3
**Alignment**: N/A (tool creates snapshot, doesn't parse artifact filenames)

---

## 4. Port Checklist Document Verdict

### 4.1 port_readiness_checklist_v0.md

| Criterion | Status |
|-----------|--------|
| Canon 6/6 covered | ✅ PASS |
| Allowlist correctly specified | ✅ PASS |
| Pre-port checks reference Ledger | ✅ PASS |
| Anti-footgun rules present | ✅ PASS |
| Tool drift documented | ✅ PASS |

**Verdict**: ✅ port_readiness_checklist_v0.md is CANON-COMPLIANT

### 4.2 port_event_note_template_v0.md

| Criterion | Status |
|-----------|--------|
| Allowlist matches checklist | ✅ PASS |
| Minimal template (no inference) | ✅ PASS |

**Verdict**: ✅ port_event_note_template_v0.md is CANON-COMPLIANT

---

## 5. Upstream Files Requiring Patch

Port documents are compliant. However, the **source files to be ported** have mismatches:

| File | Issue | Severity |
|------|-------|----------|
| `docs/contract/fitting_interface_v0.md` | Filename: facts_summary → fitting_facts_summary | CRITICAL |
| `docs/contract/fitting_interface_v0.md` | Warnings format: simple → canonical | WARNING |
| `modules/fitting/specs/fitting_manifest.schema.json` | Missing 4 version keys in provenance | CRITICAL |
| `modules/fitting/specs/fitting_manifest.schema.json` | Missing path_base, manifest_path | CRITICAL |
| `modules/fitting/specs/fitting_manifest.schema.json` | Filename: facts_summary → fitting_facts_summary | CRITICAL |

**Recommendation**: Patch upstream files BEFORE port execution, or port will carry mismatches.

---

## Summary

- **Port Checklist Documents**: ✅ COMPLIANT
- **Upstream Source Files**: ⚠️ REQUIRE PATCHES (see PATCH_BLOCKS.md)
- **Tool Drift**: DOCUMENTED (no immediate action required)

