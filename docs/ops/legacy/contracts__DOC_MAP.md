# DOC_MAP.md — Document/Schema/Artifact Inventory Map

**Generated**: 2026-01-29
**Auditor**: Contract/Interface Auditor

---

## 1. Provided Files Inventory

| # | Path | Type | Module | Status | References |
|---|------|------|--------|--------|------------|
| 1 | `docs/MasterPlan.txt` | SSoT | common | LEGACY-CANDIDATE | Mentions 5-Layer (outdated); SYNC_HUB.md supersedes |
| 2 | `docs/ops/GUARDRAILS.md` | ops | common | CANONICAL-CANDIDATE | Referenced by OPS_PLANE.md, LAYERS_v1.md |
| 3 | `docs/ops/INDEX.md` | ops | common | CANONICAL-CANDIDATE | Central ops index; self-declares round registry frozen |
| 4 | `docs/ops/OPS_PLANE.md` | ops | common | CANONICAL-CANDIDATE | References GUARDRAILS.md, sealed at `opsplane-v1` |
| 5 | `docs/sync/CURRENT_STATE.md` | SSoT | common | CANONICAL-CANDIDATE | Operational change log |
| 6 | `docs/architecture/LAYERS_v1.md` | SSoT | common | CANONICAL-CANDIDATE | Sealed at `arch-v1`; supersedes 5-Layer |
| 7 | `docs/architecture/DoD_CHECKLISTS_v1.md` | ops | common | CANONICAL-CANDIDATE | Evidence-first checklists |
| 8 | `fitting_lab/labs/specs/fitting_manifest.schema.json` | schema | fitting | CANONICAL-CANDIDATE | Defines fitting_manifest.v0 |
| 9 | `fitting_lab/contracts/fitting_interface_v0.md` | contract | fitting | CANONICAL-CANDIDATE | Facts-only policy, artifact interface |
| 10 | `fitting_lab/contracts/geometry_manifest.schema.json` | schema | common | DUPLICATE | Copy of `specs/common/geometry_manifest.schema.json`? |
| 11 | `fitting_lab/runs/smoke_real_body_ref/facts_summary.json` | sample | fitting | evidence | Sample output, filename collides with body module |
| 12 | `docs/ops/rounds/round71.md` | round | body | LEGACY-CANDIDATE | Global round naming (not folder-split) |
| 13 | `verification/runs/facts/geo_v0_s1/round71_.../KPI.md` | report | body | evidence | Round71 KPI output |
| 14 | `verification/runs/facts/geo_v0_s1/round71_.../KPI_DIFF.md` | report | body | evidence | Round71 KPI diff output |
| 15 | `verification/runs/facts/geo_v0_s1/round71_.../LINEAGE.md` | report | body | evidence | Round71 lineage manifest |
| 16 | `SYNC_HUB.md` | SSoT | common | CANONICAL-CANDIDATE | Project-wide canonical header |
| 17 | `docs/policies/measurements/geo_v0_s1_contract_v0.md` | contract | body | CANONICAL-CANDIDATE | Interface lock for geo_v0_s1 lane |

---

## 2. Cross-Module Schema Locations

### 2.1 Body Module (geo_v0_s1)
| Artifact | Expected Path | Status |
|----------|---------------|--------|
| geometry_manifest.schema.json | `specs/common/geometry_manifest.schema.json` | Referenced in LAYERS_v1.md |
| facts_summary.json | `verification/runs/facts/geo_v0_s1/<round>/facts_summary.json` | Exists in samples |
| input manifest schema | `s1_mesh_v0@1` | Documented in geo_v0_s1_contract_v0.md |

### 2.2 Fitting Module (fitting_v0)
| Artifact | Expected Path | Status |
|----------|---------------|--------|
| fitting_manifest.schema.json | `fitting_lab/labs/specs/fitting_manifest.schema.json` | Exists |
| fitting_interface_v0.md | `fitting_lab/contracts/fitting_interface_v0.md` | Exists |
| geometry_manifest.schema.json (copy) | `fitting_lab/contracts/geometry_manifest.schema.json` | Exists (potential duplicate) |

### 2.3 Garment Module
| Artifact | Expected Path | Status |
|----------|---------------|--------|
| garment_manifest.schema.json | `modules/garment/specs/` or `specs/garment/` | MISSING (planned) |

---

## 3. Missing But Expected Documents

| Path | Type | Reason Expected |
|------|------|-----------------|
| `contracts/interface_ledger_v0.md` | contract | Cross-module ledger (not yet created) |
| `modules/fitting/README.md` | SSoT | Module-level short SSoT |
| `modules/body/README.md` | SSoT | Module-level short SSoT |
| `modules/garment/README.md` | SSoT | Module-level short SSoT |
| `docs/ops/rounds/body/geo_v0_s1/M01_xxx/round_71.md` | round | Per new round policy (folder-split) |
| `contracts/path_resolution_policy.md` | contract | ABS vs REL path base rules |
| `contracts/version_keys_policy.md` | contract | Unified version key alignment |
| `contracts/nan_serialization_policy.md` | contract | Unified NaN/Inf handling |
| `fitting_lab/contracts/fitting_facts_summary.schema.json` | schema | Separate schema for fitting output |

---

## 4. Duplicate/Collision Candidates

| Item | Location A | Location B | Issue |
|------|------------|------------|-------|
| geometry_manifest.schema.json | `specs/common/geometry_manifest.schema.json` | `fitting_lab/contracts/geometry_manifest.schema.json` | Potential version drift |
| facts_summary.json (filename) | Body output | Fitting output | Collision risk in same run_dir |
| round naming | `docs/ops/rounds/round71.md` | Policy says folder-split | Legacy vs new policy |

---

## 5. Document Status Summary

| Status | Count | Action |
|--------|-------|--------|
| CANONICAL-CANDIDATE | 12 | Confirm as canonical, add to ledger |
| LEGACY-CANDIDATE | 2 | Add LEGACY stamp at header |
| DUPLICATE | 1 | Verify sync, add provenance pointer |
| evidence | 4 | Sample/run outputs, no action |
| UNKNOWN | 0 | — |
| MISSING | 9+ | Per Section 3 |

---

## 6. Module × Document Type Matrix

| Module | SSoT | contract | schema | ops | round | report | sample |
|--------|------|----------|--------|-----|-------|--------|--------|
| common | SYNC_HUB.md, LAYERS_v1.md, CURRENT_STATE.md | — | geometry_manifest.schema.json | GUARDRAILS.md, INDEX.md, OPS_PLANE.md, DoD_CHECKLISTS_v1.md | — | — | — |
| body | — | geo_v0_s1_contract_v0.md | s1_mesh_v0@1 (inline) | — | round71.md | KPI.md, KPI_DIFF.md, LINEAGE.md | facts_summary.json |
| fitting | — | fitting_interface_v0.md | fitting_manifest.schema.json | — | — | — | facts_summary.json (collision) |
| garment | — | — | — | — | — | — | — |

---

## 7. Canonical Path Recommendations

| Document Category | Recommended Canonical Path |
|-------------------|----------------------------|
| Cross-module ledger | `contracts/interface_ledger_v0.md` |
| Module contracts | `contracts/<module>/<contract_name>.md` |
| Module schemas | `specs/<module>/<schema_name>.schema.json` |
| Common schemas | `specs/common/<schema_name>.schema.json` |
| Module README | `modules/<module>/README.md` |
| Round notes (new) | `docs/ops/rounds/<lane_slug>/<milestone_id>/round_<NN>.md` |
| Round notes (legacy) | `docs/ops/rounds/roundXX.md` (frozen, add LEGACY stamp) |
