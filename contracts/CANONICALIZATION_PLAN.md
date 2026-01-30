# CANONICALIZATION_PLAN.md — Minimal Canonicalization Plan (Doc-Only)

**Generated**: 2026-01-29
**Auditor**: Contract/Interface Auditor

---

## Scope

- Doc-only patches (no code changes)
- No folder moves, no deletions
- COPY-based approach with legacy stamps where needed
- Minimal surface area

---

## 1. Create Cross-Module Interface Ledger

**Target**: `contracts/interface_ledger_v0.md` (NEW)
**Insertion**: New file

```markdown
# Interface Ledger v0 (Cross-Module)

**Status**: CANONICAL
**Purpose**: Single source of truth for artifact interfaces across body/garment/fitting modules.

---

## 1. Path Resolution Policy

### Canonical Policy (C)
- **ABS paths**: Allowed
- **REL paths**: Allowed
- **Canonical REL base**: `manifest_dir` (directory containing the manifest file)
- **Legacy REL base**: `run_dir` may be allowed only if explicitly signaled in provenance

### Provenance Recording
When using relative paths, provenance MUST include:
- `path_base`: `"manifest_dir"` or `"run_dir"`
- `manifest_path`: Absolute path to manifest file (for REL resolution)

---

## 2. Naming Policy

### Body Module
- Input: N/A (consumes manifests/meshes)
- Output: `facts_summary.json`

### Fitting Module
- Input: Body's `facts_summary.json` (referenced by path)
- Output: `fitting_facts_summary.json` (NOT `facts_summary.json`)

### Collision Prevention Rule
- Fitting module output filename MUST differ from body module output filename
- `fitting_facts_summary.json` is the canonical fitting output name

---

## 3. Version Keys Policy (C)

### Required Version Keys (all modules)
| Key | Description | If Unknown |
|-----|-------------|------------|
| `schema_version` | Schema identifier (e.g., `fitting_manifest.v0`) | REQUIRED |
| `geometry_impl_version` | Geometry implementation version | `"UNSPECIFIED"` + `VERSION_KEY_UNSPECIFIED` warning |
| `dataset_version` | Dataset version | `"UNSPECIFIED"` + `VERSION_KEY_UNSPECIFIED` warning |

### Optional Version Keys
| Key | Description |
|-----|-------------|
| `snapshot_version` | Point-in-time snapshot identifier |
| `semantic_version` | Semantic versioning string |

### UNSPECIFIED Handling
- If a version key is unknown at runtime, it MUST exist with value `"UNSPECIFIED"`
- A warning with code `VERSION_KEY_UNSPECIFIED` MUST be recorded

---

## 4. Round Policy

### Lane Format
- `<module>/<lane_id>` (e.g., `body/geo_v0_s1`, `fitting/fitting_v0_facts`)

### Milestone Format
- `M<NN>_<short_tag>` (e.g., `M01_baseline`, `M02_torso_recovery`)

### Round ID Format
- `<lane_slug>__<milestone_id>__r<NN>` (e.g., `geo_v0_s1__M01_baseline__r01`)

### Round Docs Path (NEW rounds)
- `docs/ops/rounds/<lane_slug>/<milestone_id>/round_<NN>.md`
- Example: `docs/ops/rounds/geo_v0_s1/M01_baseline/round_01.md`

### Legacy Rounds
- Existing `docs/ops/rounds/roundXX.md` files are LEGACY naming
- Do NOT edit; add LEGACY stamp at header

---

## 5. NaN/Inf Serialization Policy

### JSON Serialization
- NaN → `null`
- Inf → `null` (with warning `INF_SERIALIZED_AS_NULL`)
- -Inf → `null` (with warning `NEG_INF_SERIALIZED_AS_NULL`)

### Schema Compliance
- Schemas using `"type": "number"` for measurements MUST be updated to `"type": ["number", "null"]`

---

## 6. Warning Structure Policy

### Canonical Format (explosion prevention)
```json
{
  "warnings": {
    "<CODE>": {
      "count": <int>,
      "sample_messages": ["msg1", "msg2", ...],  // max 5
      "truncated": <bool>
    }
  }
}
```

### Simple Format (legacy, allowed for internal)
```json
{
  "warnings": {
    "<CODE>": ["msg1", "msg2", ...]
  }
}
```

### Policy
- External/cross-module artifacts SHOULD use canonical format
- Internal/run artifacts MAY use simple format

---

## 7. Always-Emit Fields (Fitting Module)

These fields MUST be present in `fitting_facts_summary.json` even when counts are zero:

- `nan_count.total` (int)
- `nan_count.nan` (int)
- `nan_rate` (float)
- `reasons.missing_input` (int)
- `reasons.parse_fail` (int)
- `reasons.zero_division` (int)
- `reasons.missing_key` (int)

---

## Appendix: Module × Artifact Summary

| Module | Input Artifact | Output Artifact | Schema |
|--------|----------------|-----------------|--------|
| body | s1_manifest.json, *.obj | facts_summary.json | facts_summary.v0 |
| fitting | fitting_manifest.json, facts_summary.json | fitting_facts_summary.json | fitting_facts_summary.v0 |
| garment | (TBD) | (TBD) | (TBD) |
```

---

## 2. Add LEGACY Stamp to MasterPlan.txt

**Target**: `docs/MasterPlan.txt`
**Insertion**: Top of file (line 1)

```markdown
> ⚠️ STATUS: LEGACY (SUPERSEDED)
> DO NOT EDIT. Canonical source: SYNC_HUB.md, docs/architecture/LAYERS_v1.md
> Last valid as-of: 2026-01-27 • Reason: Layer model updated to 6-Layer + 3-Module in Architecture v1
---

```

---

## 3. Update fitting_interface_v0.md: Output Filename

**Target**: `fitting_lab/contracts/fitting_interface_v0.md`
**Section**: "Optional Fields → outputs"
**Change**: Replace `facts_summary.json` with `fitting_facts_summary.json`

### Patch Block (replace section)

**Find** (approximately lines 39-43):
```markdown
#### `outputs` (continued)
- **`expected_files`** (object, optional):
  - `fitting_summary` (string, const): `"fitting_summary.json"`
  - `facts_summary` (string, const): `"facts_summary.json"`
```

**Replace with**:
```markdown
#### `outputs` (continued)
- **`expected_files`** (object, optional):
  - `fitting_summary` (string, const): `"fitting_summary.json"`
  - `fitting_facts_summary` (string, const): `"fitting_facts_summary.json"`
```

---

## 4. Update fitting_interface_v0.md: Add Path Base Policy

**Target**: `fitting_lab/contracts/fitting_interface_v0.md`
**Insertion**: After "## Integration Rules" section (bottom of file)

### Patch Block (append)

```markdown

---

## Path Resolution Policy

### Relative Path Base
- All relative paths in `fitting_manifest.json` resolve from **manifest_dir** (the directory containing the manifest file)
- Absolute paths are allowed and used as-is

### Provenance Recording
When paths are relative, `provenance` SHOULD include:
```json
{
  "provenance": {
    "path_base": "manifest_dir",
    "manifest_path": "/absolute/path/to/manifest.json"
  }
}
```
```

---

## 5. Update fitting_manifest.schema.json: Add Version Keys

**Target**: `fitting_lab/labs/specs/fitting_manifest.schema.json`
**Section**: `properties.provenance.properties`
**Change**: Add `geometry_impl_version` and `dataset_version`

### Patch Block (extend provenance properties)

**Find** (approximately lines 188-209):
```json
        "provenance": {
            "type": "object",
            "required": [
                "schema_version",
                "code_fingerprint"
            ],
            "additionalProperties": false,
            "properties": {
                "schema_version": {
                    "type": "string",
                    "const": "fitting_manifest.v0",
                    "description": "Schema version for provenance tracking"
                },
                "code_fingerprint": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Fingerprint of the code that generated this manifest"
                },
                "input_fingerprints": {
                    "type": "object",
                    "description": "Fingerprints of input files",
                    "additionalProperties": {
                        "type": "string"
                    }
                }
            }
        }
```

**Replace with**:
```json
        "provenance": {
            "type": "object",
            "required": [
                "schema_version",
                "code_fingerprint"
            ],
            "additionalProperties": false,
            "properties": {
                "schema_version": {
                    "type": "string",
                    "const": "fitting_manifest.v0",
                    "description": "Schema version for provenance tracking"
                },
                "code_fingerprint": {
                    "type": "string",
                    "minLength": 1,
                    "description": "Fingerprint of the code that generated this manifest"
                },
                "geometry_impl_version": {
                    "type": "string",
                    "description": "Geometry implementation version. Use 'UNSPECIFIED' if unknown."
                },
                "dataset_version": {
                    "type": ["string", "null"],
                    "description": "Dataset version. Use 'UNSPECIFIED' if unknown."
                },
                "path_base": {
                    "type": "string",
                    "enum": ["manifest_dir", "run_dir"],
                    "description": "Base directory for relative path resolution"
                },
                "input_fingerprints": {
                    "type": "object",
                    "description": "Fingerprints of input files",
                    "additionalProperties": {
                        "type": "string"
                    }
                }
            }
        }
```

---

## 6. Add LEGACY Stamp to Existing Round Files

**Target**: `docs/ops/rounds/round71.md` (and all existing roundXX.md files)
**Insertion**: Top of file (line 1)

### Patch Block (prepend)

```markdown
> ⚠️ STATUS: LEGACY NAMING
> New rounds use folder-split format: docs/ops/rounds/<lane>/<milestone>/round_<NN>.md
> This file preserved for history. Last updated: 2026-01-28
---

```

---

## 7. Update geometry_manifest.schema.json: Allow Null in Measurements

**Target**: `fitting_lab/contracts/geometry_manifest.schema.json` (and `specs/common/geometry_manifest.schema.json`)
**Section**: `properties.measurements_summary`
**Change**: Allow null for NaN serialization

### Patch Block

**Find** (approximately lines 69-74):
```json
    "measurements_summary": {
      "type": "object",
      "description": "측정 결과 요약 (키-값 쌍, 단위는 meters)",
      "additionalProperties": {
        "type": "number"
      }
    },
```

**Replace with**:
```json
    "measurements_summary": {
      "type": "object",
      "description": "측정 결과 요약 (키-값 쌍, 단위는 meters). NaN은 null로 직렬화.",
      "additionalProperties": {
        "type": ["number", "null"]
      }
    },
```

---

## 8. Create Provenance Pointer for geometry_manifest.schema.json Copy

**Target**: `fitting_lab/contracts/geometry_manifest.schema.json`
**Insertion**: Top of file (after opening brace)

### Patch Block (add after line 1)

**Find**:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
```

**Replace with**:
```json
{
  "$comment": "COPY of specs/common/geometry_manifest.schema.json. Canonical source: AI_model/specs/common/geometry_manifest.schema.json. Sync date: 2026-01-29.",
  "$schema": "http://json-schema.org/draft-07/schema#",
```

---

## 9. Summary: Files to Modify

| # | File | Action | Lines Affected |
|---|------|--------|----------------|
| 1 | `contracts/interface_ledger_v0.md` | CREATE | ~120 lines (new) |
| 2 | `docs/MasterPlan.txt` | PREPEND | 4 lines (legacy stamp) |
| 3 | `fitting_lab/contracts/fitting_interface_v0.md` | EDIT | ~10 lines (filename + path policy) |
| 4 | `fitting_lab/labs/specs/fitting_manifest.schema.json` | EDIT | ~15 lines (version keys) |
| 5 | `docs/ops/rounds/round71.md` | PREPEND | 4 lines (legacy stamp) |
| 6 | `fitting_lab/contracts/geometry_manifest.schema.json` | EDIT | ~3 lines (null type + comment) |
| 7 | `specs/common/geometry_manifest.schema.json` | EDIT | ~3 lines (null type) |

---

## 10. Optional: Machine-Readable Ledger Row Export Spec

**Target**: `contracts/interface_ledger_rows.schema.json` (NEW, optional)

### Spec

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Interface Ledger Row",
  "description": "Machine-readable ledger row for cross-module artifact tracking",
  "type": "object",
  "required": ["producer", "consumer", "kind", "canonical_path", "required", "format"],
  "properties": {
    "producer": {"type": "string", "description": "Module that produces the artifact (body/fitting/garment)"},
    "consumer": {"type": "string", "description": "Module that consumes the artifact"},
    "kind": {"type": "string", "enum": ["manifest", "facts", "schema", "mesh"]},
    "canonical_path": {"type": "string", "description": "Canonical file path pattern"},
    "required": {"type": "boolean"},
    "format": {"type": "string", "enum": ["json", "jsonl", "obj", "npz", "md"]},
    "version_keys_present": {"type": "array", "items": {"type": "string"}},
    "units": {"type": "string", "enum": ["m", "mm", "cm", "none"]},
    "nan_serialization": {"type": "string", "enum": ["null", "NaN_string", "omit"]},
    "path_base_used": {"type": "string", "enum": ["manifest_dir", "run_dir", "absolute"]}
  }
}
```

### Sample Row (JSONL)

```jsonl
{"producer":"body","consumer":"fitting","kind":"facts","canonical_path":"verification/runs/facts/geo_v0_s1/<round>/facts_summary.json","required":true,"format":"json","version_keys_present":["schema_version"],"units":"m","nan_serialization":"null","path_base_used":"run_dir"}
{"producer":"fitting","consumer":"external","kind":"facts","canonical_path":"runs/<run>/fitting_facts_summary.json","required":true,"format":"json","version_keys_present":["schema_version","geometry_impl_version"],"units":"m","nan_serialization":"null","path_base_used":"manifest_dir"}
```

---

## 11. Non-Actions (Explicitly Out of Scope)

| Item | Reason |
|------|--------|
| Move `docs/ops/rounds/roundXX.md` files | No folder moves policy |
| Delete MasterPlan.txt | No deletions policy |
| Rewrite legacy sections in INDEX.md | No SSoT edits during parallel work |
| Modify code files | Doc-only plan |
| Create `modules/` directories | No folder creation unless explicitly required |

---

## 12. Application Order

1. Create `contracts/interface_ledger_v0.md` (defines all policies)
2. Add LEGACY stamp to `docs/MasterPlan.txt`
3. Update `fitting_lab/contracts/fitting_interface_v0.md` (filename + path policy)
4. Update `fitting_lab/labs/specs/fitting_manifest.schema.json` (version keys)
5. Update geometry_manifest.schema.json files (null type)
6. Add LEGACY stamp to existing round files
7. (Optional) Create ledger row schema
