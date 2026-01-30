# Final Port Checklist (Human-Executable)

**Status**: READY FOR USE
**Date**: 2026-01-29
**Purpose**: 10-15 item checklist for fitting_lab → main port execution

---

## Pre-Port Phase (8 items)

### Canon Alignment
- [ ] **1. Verify interface_ledger_v0.md exists** in `contracts/`
- [ ] **2. Confirm 6 canon locks documented**: Path=C, Name=B, Version=C, Round, NaN→null, Warnings

### Source File Patches (apply BEFORE port)
- [ ] **3. fitting_interface_v0.md filename patched**: `facts_summary` → `fitting_facts_summary` (4 locations)
- [ ] **4. fitting_interface_v0.md policy sections added**: Version Policy (C), Path Policy (C)
- [ ] **5. fitting_manifest.schema.json filename patched**: expected_files key updated
- [ ] **6. fitting_manifest.schema.json version keys added**: snapshot_version, semantic_version, geometry_impl_version, dataset_version
- [ ] **7. fitting_manifest.schema.json path fields added**: path_base, manifest_path

### Evidence
- [ ] **8. Release snapshot created** (fitting_lab side): `releases/fitting_v0_YYYYMMDD_HHMMSS/`

---

## Port Execution Phase (4 items)

### File Copy (allowlist only)
- [ ] **9. Copy 3 files** (copy-only, NOT git mv):
  - `labs/runners/run_fitting_v0_facts.py` → `modules/fitting/runners/`
  - `labs/specs/fitting_manifest.schema.json` → `modules/fitting/specs/`
  - `contracts/fitting_interface_v0.md` → `docs/contract/`

### Git Operations
- [ ] **10. Create branch**: `port/fitting-v0-<milestone>`
- [ ] **11. Stage ONLY allowlist files** (no `git add -A`)
- [ ] **12. Commit with message**: `port: fitting v0 files from fitting_lab (<milestone>)`

---

## Post-Port Phase (3 items)

### Verification
- [ ] **13. Files exist in main repo**:
  ```
  ls modules/fitting/runners/run_fitting_v0_facts.py
  ls modules/fitting/specs/fitting_manifest.schema.json
  ls docs/contract/fitting_interface_v0.md
  ```

- [ ] **14. Smoke run executed** (if applicable per fitting_interface_v0.md)

- [ ] **15. Port Event recorded**: Use `contracts/port_event_note_template_v0.md` or PR description

---

## Anti-Footgun Reminders

| ❌ DO NOT | ✅ DO |
|-----------|------|
| Add files beyond allowlist | Copy exactly 3 files |
| Use `git mv` | Use `cp` (copy) |
| Modify interface_ledger_v0.md | Reference it as SSoT |
| Port without snapshot | Create snapshot first |
| Auto-extend allowlist | Request explicit approval |

---

## Quick Reference

**Allowlist files (exactly 3)**:
1. `run_fitting_v0_facts.py`
2. `fitting_manifest.schema.json`
3. `fitting_interface_v0.md`

**Canonical output filename**: `fitting_facts_summary.json` (NOT `facts_summary.json`)

**4 Version keys** (always present, `"UNSPECIFIED"` if unknown):
- `snapshot_version`
- `semantic_version`
- `geometry_impl_version`
- `dataset_version`

**SSoT**: `contracts/interface_ledger_v0.md`

---

**Total items**: 15 (Pre-Port: 8, Execution: 4, Post-Port: 3)

