# Patch Blocks for Canon Alignment (Port Verification)

**Status**: READY TO APPLY
**Date**: 2026-01-29
**Target**: Main repo upstream files (pre-port alignment)

---

## Executive Summary

Port checklist documents (port_readiness_checklist_v0.md, port_event_note_template_v0.md) are **CANON-COMPLIANT**.

However, the actual source files in main repo have mismatches that must be patched BEFORE porting carries these inconsistencies forward.

---

## Patch A: fitting_interface_v0.md — Filename Update

**File**: `docs/contract/fitting_interface_v0.md`
**Canon**: interface_ledger_v0.md §2 (Name=B)

### A.1 Line 38: expected_files facts_summary

```diff
-  - `facts_summary` (string, const): `"facts_summary.json"`
+  - `fitting_facts_summary` (string, const): `"fitting_facts_summary.json"`
```

### A.2 Line 63: Section Header

```diff
-### `facts_summary.json`
+### `fitting_facts_summary.json`
```

### A.3 Line 65: Schema Version

```diff
-**Schema Version**: `facts_summary.v0`
+**Schema Version**: `fitting_facts_summary.v0`
```

### A.4 Line 68: schema_version value

```diff
-- `schema_version` (string): `"facts_summary.v0"`
+- `schema_version` (string): `"fitting_facts_summary.v0"`
```

---

## Patch B: fitting_interface_v0.md — Add Policy Sections

**File**: `docs/contract/fitting_interface_v0.md`
**Canon**: interface_ledger_v0.md §1 (Path=C), §3 (Version=C)
**Insert After**: Line 128 (end of file, after Integration Rules)

```markdown

---

## Version Policy (C) — 4 Keys Always

All cross-module fitting artifacts MUST include 4 version keys in provenance:

| Key | Description | Unknown Value |
|-----|-------------|---------------|
| `snapshot_version` | Point-in-time snapshot identifier | `"UNSPECIFIED"` |
| `semantic_version` | Semantic version string | `"UNSPECIFIED"` |
| `geometry_impl_version` | Geometry implementation version | `"UNSPECIFIED"` |
| `dataset_version` | Dataset version | `"UNSPECIFIED"` |

When any key is unknown, set value to `"UNSPECIFIED"` and emit warning `VERSION_KEY_UNSPECIFIED`.

---

## Path Policy (C)

- REL paths are relative to `manifest_dir` (directory containing manifest file)
- Provenance MUST include `path_base` and `manifest_path` when using REL paths:

```json
{
  "provenance": {
    "path_base": "manifest_dir",
    "manifest_path": "/absolute/path/to/manifest.json"
  }
}
```

Legacy `run_dir` base allowed only if `"path_base": "run_dir"` explicitly set in provenance.
```

---

## Patch C: fitting_manifest.schema.json — Filename Update

**File**: `modules/fitting/specs/fitting_manifest.schema.json`
**Canon**: interface_ledger_v0.md §2 (Name=B)

### C.1 Lines 139-141: expected_files.facts_summary → fitting_facts_summary

```diff
-                        "facts_summary": {
-                            "type": "string",
-                            "const": "facts_summary.json"
-                        }
+                        "fitting_facts_summary": {
+                            "type": "string",
+                            "const": "fitting_facts_summary.json"
+                        }
```

---

## Patch D: fitting_manifest.schema.json — Add Version Keys

**File**: `modules/fitting/specs/fitting_manifest.schema.json`
**Canon**: interface_ledger_v0.md §3 (Version=C)
**Insert Into**: `properties.provenance.properties` object (after line 178, before closing brace)

```json
                "snapshot_version": {
                    "type": "string",
                    "description": "Point-in-time snapshot identifier. Use UNSPECIFIED if unknown."
                },
                "semantic_version": {
                    "type": "string",
                    "description": "Semantic version string. Use UNSPECIFIED if unknown."
                },
                "geometry_impl_version": {
                    "type": "string",
                    "description": "Geometry implementation version. Use UNSPECIFIED if unknown."
                },
                "dataset_version": {
                    "type": "string",
                    "description": "Dataset version. Use UNSPECIFIED if unknown."
                },
```

---

## Patch E: fitting_manifest.schema.json — Add Path Policy Fields

**File**: `modules/fitting/specs/fitting_manifest.schema.json`
**Canon**: interface_ledger_v0.md §1 (Path=C)
**Insert Into**: `properties.provenance.properties` object

```json
                "path_base": {
                    "type": "string",
                    "enum": ["manifest_dir", "run_dir"],
                    "description": "Base directory for relative path resolution. Default: manifest_dir"
                },
                "manifest_path": {
                    "type": "string",
                    "description": "Absolute path to the manifest file for REL path resolution"
                },
```

---

## Patch Summary Table

| Patch | File | Change | Canon Reference |
|-------|------|--------|-----------------|
| A | docs/contract/fitting_interface_v0.md | facts_summary → fitting_facts_summary (4 locations) | §2 Name=B |
| B | docs/contract/fitting_interface_v0.md | Add Version Policy (C) and Path Policy (C) sections | §1, §3 |
| C | modules/fitting/specs/fitting_manifest.schema.json | facts_summary → fitting_facts_summary in expected_files | §2 Name=B |
| D | modules/fitting/specs/fitting_manifest.schema.json | Add 4 version keys to provenance | §3 Version=C |
| E | modules/fitting/specs/fitting_manifest.schema.json | Add path_base, manifest_path to provenance | §1 Path=C |

---

## Application Order

1. Apply Patch A (fitting_interface_v0.md filename changes)
2. Apply Patch B (fitting_interface_v0.md policy sections)
3. Apply Patches C, D, E (fitting_manifest.schema.json — can combine in single edit)

---

## Post-Patch Verification

After applying patches, verify:

```powershell
# Check filename in interface doc
Select-String -Path "docs/contract/fitting_interface_v0.md" -Pattern "fitting_facts_summary"
# Expected: 4+ matches

# Check schema has version keys
Select-String -Path "modules/fitting/specs/fitting_manifest.schema.json" -Pattern "snapshot_version|semantic_version|geometry_impl_version|dataset_version"
# Expected: 4 matches

# Check schema has path fields
Select-String -Path "modules/fitting/specs/fitting_manifest.schema.json" -Pattern "path_base|manifest_path"
# Expected: 2 matches
```

---

## Note on Port Checklist Documents

**port_readiness_checklist_v0.md** and **port_event_note_template_v0.md** are already CANON-COMPLIANT and require NO patches.

These patches are for the upstream source files to ensure ported content is consistent with canon.

