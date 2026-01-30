# CONSISTENCY_REPORT.md — Consistency & Ambiguity Report (Facts-Only)

**Generated**: 2026-01-29
**Auditor**: Contract/Interface Auditor

---

## 1. Path Base Ambiguity

### Issue 1.1: Relative Path Base Undefined in Fitting
| File | Field/Section | Observation |
|------|---------------|-------------|
| `fitting_interface_v0.md` | `inputs.body_source.*_path` | Paths specified as "string, minLength:1" with no base definition |
| `fitting_manifest.schema.json` | `body_source.geometry_manifest_path` | "Path to geometry manifest" — no base specified |
| `geometry_manifest.schema.json` (fitting_lab) | description | States "경로는 상대경로 또는 절대경로를 사용할 수 있습니다" but no canonical REL base |

**Inference Risk**: Cursor cannot determine if relative paths resolve from manifest_dir, run_dir, or cwd.

### Issue 1.2: Sample Uses Absolute Path
| File | Field | Observed Value |
|------|-------|----------------|
| `fitting_lab/runs/smoke_real_body_ref/facts_summary.json` | `provenance.manifest_path` | `C:\\Users\\caino\\Desktop\\fitting_lab\\labs\\samples\\manifest_real_body_ref.json` |

**Inference Risk**: No evidence of relative path resolution tested.

### Issue 1.3: Body Module Path Policy Missing
| File | Section | Observation |
|------|---------|-------------|
| `geo_v0_s1_contract_v0.md` | Section 3 (Input Manifest) | mesh_path defined as "string or null" — no base specified |
| `LINEAGE.md` | `npz_path`, `facts_summary.json` | Uses Windows backslash paths, unclear if relative to run_dir |

---

## 2. Filename Collision: facts_summary.json

### Issue 2.1: Body vs Fitting Output Collision
| Module | Output File | Documented Location |
|--------|-------------|---------------------|
| body (geo_v0_s1) | `facts_summary.json` | `verification/runs/facts/geo_v0_s1/<round>/facts_summary.json` |
| fitting | `facts_summary.json` | `fitting_interface_v0.md` Section "Output Files" |

**Policy Given**: Fitting output MUST be `fitting_facts_summary.json` to avoid collision.

### Issue 2.2: fitting_interface_v0.md Contradicts Policy
| File | Section | Field | Value |
|------|---------|-------|-------|
| `fitting_interface_v0.md` | "Optional Fields → outputs" | `expected_files.facts_summary` | `"facts_summary.json"` (const) |

**Contradiction**: Document says `"facts_summary.json"` but policy says `"fitting_facts_summary.json"`.

### Issue 2.3: fitting_manifest.schema.json Silent on Output Filename
| File | Section | Observation |
|------|---------|-------------|
| `fitting_manifest.schema.json` | `outputs.expected_files` | Array of strings, no constraints on filenames |

---

## 3. Version Keys Inconsistency

### Issue 3.1: Version Key Names Differ Across Schemas
| Schema | Version Keys Present |
|--------|---------------------|
| `fitting_manifest.schema.json` | `schema_version`, `provenance.schema_version`, `provenance.code_fingerprint` |
| `geometry_manifest.schema.json` | `schema_version`, `contract_version`, `geometry_impl_version`, `dataset_version` |
| `geo_v0_s1_contract_v0.md` | References `s1_mesh_v0@1` for manifest schema |

**Policy Given**: Align version keys: `snapshot_version`, `semantic_version`, `geometry_impl_version`, `dataset_version`.

### Issue 3.2: Missing Keys Per Policy
| Schema | `snapshot_version` | `semantic_version` | `geometry_impl_version` | `dataset_version` |
|--------|--------------------|--------------------|-------------------------|-------------------|
| `fitting_manifest.schema.json` | MISSING | MISSING | MISSING | MISSING |
| `geometry_manifest.schema.json` | MISSING | MISSING | PRESENT | PRESENT (nullable) |

### Issue 3.3: UNSPECIFIED Policy Not Implemented
| File | Observation |
|------|-------------|
| All schemas | No "UNSPECIFIED" default value defined |
| All schemas | No `VERSION_KEY_UNSPECIFIED` warning schema |

---

## 4. Round Numbering Scheme Conflict

### Issue 4.1: Global vs Folder-Split Naming
| Policy Source | Format |
|---------------|--------|
| **Given Policy** | `docs/ops/rounds/<lane_slug>/<milestone_id>/round_<NN>.md` |
| **Observed (round71.md)** | `docs/ops/rounds/round71.md` |

### Issue 4.2: Legacy Round Format
| File | Path | Lane | Observation |
|------|------|------|-------------|
| `round71.md` | `docs/ops/rounds/round71.md` | geo_v0_s1 | Global naming, not folder-split |

**SYNC_HUB.md Section 10**: "Round notes are added only via `docs/ops/rounds/roundXX.md` (append-only)."
**INDEX.md**: States rounds should be `roundXX.md` files.

**Conflict**: Existing policy says `roundXX.md` (global), new policy says folder-split.

---

## 5. Warning Structure Inconsistency

### Issue 5.1: Three Different Warning Formats
| Source | Format |
|--------|--------|
| `fitting_interface_v0.md` | `dict[CODE] -> {count: int, sample_messages: [<=5], truncated: bool}` |
| `fitting_lab/.../facts_summary.json` (sample) | `dict[CODE] -> [array of strings]` |
| `geometry_manifest.schema.json` | `array of strings` |

### Issue 5.2: Sample Output Doesn't Match Contract
| File | Section | Contract Format | Actual Format |
|------|---------|-----------------|---------------|
| `fitting_lab/runs/smoke_real_body_ref/facts_summary.json` | `warnings` | `{count, sample_messages, truncated}` | `{"MISSING_INPUT": ["..."], "MISSING_KEY": [...]}` |

**Observation**: Sample output uses simpler array-of-strings format, not explosion-prevention format.

---

## 6. NaN/Inf Serialization Ambiguity

### Issue 6.1: Explicit Policy vs Schema Silence
| File | Statement |
|------|-----------|
| `fitting_interface_v0.md` | "NaN allowed internally, serialized as null in JSON" |
| `geometry_manifest.schema.json` | `measurements_summary` additionalProperties: `{"type": "number"}` — no null allowed |

### Issue 6.2: NaN Policy Missing in Geometry Schema
| File | Field | Type Constraint | Allows null? |
|------|-------|-----------------|--------------|
| `geometry_manifest.schema.json` | `measurements_summary.*` | `number` | NO |
| `fitting_interface_v0.md` | metrics fields | "float or null" | YES |

**Inference Risk**: Geometry manifest cannot represent NaN measurements per its own schema.

---

## 7. Always-Emit Rules Gap

### Issue 7.1: Body Has Explicit Rules, Fitting Does Not
| File | Observability Fields | Always-Emit Requirement |
|------|---------------------|------------------------|
| `geo_v0_s1_contract_v0.md` Section 4.3 | 20+ fields listed | "MUST be present even when counts are zero" |
| `fitting_interface_v0.md` | `nan_count`, `reasons`, `warnings` | No explicit always-emit clause |

### Issue 7.2: Missing Zero-Count Guarantee for Fitting
| File | Field | Issue |
|------|-------|-------|
| `fitting_interface_v0.md` | `reasons.missing_input` | Not stated if MUST appear when count=0 |

---

## 8. Lane/Module Naming Gaps

### Issue 8.1: Fitting Lane Undefined
| File | Observation |
|------|-------------|
| `fitting_interface_v0.md` | No lane name defined (e.g., `fitting_v0_facts`) |
| `fitting_manifest.schema.json` | No lane field |

### Issue 8.2: Policy vs Practice
| Policy Given | Example |
|--------------|---------|
| Lane format | `body/geo_v0_s1`, `fitting/fitting_v0_facts` |
| Observed (body) | `geo_v0_s1` (without `body/` prefix) |

---

## 9. Governance Document Conflicts

### Issue 9.1: 5-Layer vs 6-Layer
| File | States |
|------|--------|
| `MasterPlan.txt` | "5-Layer R&D 파이프라인" in header table |
| `MasterPlan.txt` | Line 3: "최종 구조는 6 Layers + 3 Modules로 정의되었습니다" |
| `SYNC_HUB.md` | "6-Layer R&D 파이프라인" |
| `INDEX.md` | Section "5-Layer Organization Principle" labeled "LEGACY NOTE" |

**Observation**: MasterPlan.txt contains both 5-Layer table and 6-Layer reference.

### Issue 9.2: Layer Numbering in MasterPlan.txt
| MasterPlan.txt Layer | Name | LAYERS_v1.md Layer | Name |
|---------------------|------|-------------------|------|
| L1 | Geometry | L1 | Contract |
| L2 | Production | L2 | Geometry |
| L3 | Validation | L3 | Production |
| L4 | Intelligence | L4 | Validation |
| L5 | Application | L5 | Confidence |
| — | — | L6 | Application |

**Conflict**: MasterPlan.txt uses different layer mapping than LAYERS_v1.md.

---

## 10. Schema Location Inconsistency

### Issue 10.1: geometry_manifest.schema.json Locations
| Location | $id Field |
|----------|-----------|
| `fitting_lab/contracts/geometry_manifest.schema.json` | `specs/common/geometry_manifest.schema.json` |
| `specs/common/geometry_manifest.schema.json` (expected) | Not provided for comparison |

**Risk**: fitting_lab copy may drift from canonical `specs/common/` version.

---

## 11. Summary: Cursor Inference Points

| # | Issue | Inference Required | Priority |
|---|-------|-------------------|----------|
| 1 | Path base (REL vs ABS) | Cursor must guess manifest_dir vs run_dir | HIGH |
| 2 | facts_summary filename collision | Cursor must guess fitting output name | HIGH |
| 3 | Version keys alignment | Cursor must decide which keys to emit | MEDIUM |
| 4 | Round naming (global vs folder-split) | Cursor must decide format | MEDIUM |
| 5 | Warning structure format | Cursor must guess explosion-prevention vs simple | HIGH |
| 6 | NaN serialization in geometry | Cursor must decide null vs number | MEDIUM |
| 7 | Always-emit rules for fitting | Cursor must guess which fields required at zero | MEDIUM |
| 8 | Lane naming for fitting | Cursor must invent lane name | LOW |
| 9 | 5-Layer vs 6-Layer in MasterPlan | Cursor may use wrong layer model | HIGH |

---

## 12. Evidence Citations (Exact References)

| Issue | File | Line/Field | Exact Text (≤25 words) |
|-------|------|------------|------------------------|
| 2.2 | fitting_interface_v0.md | Section "Optional Fields" | `expected_files.facts_summary` (string, const): `"facts_summary.json"` |
| 5.1 | fitting_interface_v0.md | Section "Facts-Only Policy" | `dict[CODE] -> {count: int, sample_messages: [<=5], truncated: bool}` |
| 5.2 | facts_summary.json (sample) | `warnings` | `{"MISSING_INPUT": ["PATH/TO/REAL/body_measurements.json"], ...}` |
| 6.1 | fitting_interface_v0.md | Section "Facts-Only Policy" | "NaN allowed internally, serialized as null in JSON output" |
| 6.2 | geometry_manifest.schema.json | `measurements_summary` | `"additionalProperties": {"type": "number"}` |
| 9.1 | MasterPlan.txt | Line 1 table header | "5-Layer R&D 파이프라인" |
| 9.1 | MasterPlan.txt | Line 3 | "최종 구조는 6 Layers + 3 Modules로 정의되었습니다" |
