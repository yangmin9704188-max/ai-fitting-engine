# Bust/Underbust Real-Data Golden NPZ Generation

## Purpose

Generate Golden NPZ from real processed(m_standard) data for bust/underbust v0 facts-only validation.

## Prerequisites

1. **Processed(m_standard) data must exist:**
   - Path: `data/processed/m_standard/`
   - Format: CSV files with measurement columns in meters (m)
   - If not exists, first regenerate:
     ```bash
     python data/regenerate_processed_m_standard.py \
       --input_csv data/processed/SizeKorea_Final/SizeKorea_20-29_Female.csv \
       --source_unit cm \
       --columns height:Height chest_girth:Chest_Girth waist_girth:Waist_Girth hip_girth:Hip_Girth \
       --output_dir data/processed/m_standard
     ```

## Generation

```bash
python verification/datasets/golden/bust_underbust_v0/create_real_data_golden.py \
  --processed_csv data/processed/m_standard/SizeKorea_20-29_Female_m.csv \
  --output_npz verification/datasets/golden/bust_underbust_v0/golden_real_data_v0.npz \
  --source_unit cm \
  --n 200
```

**Output:**
- `verification/datasets/golden/bust_underbust_v0/golden_real_data_v0.npz`
- Contains: `verts` (N, V, 3), `case_id`, `meta_unit="m"`, `schema_version="bust_underbust_v0_real@1"`, `ingestion_provenance`

## Facts Runner Run B Execution

After generating the real-data golden NPZ, run facts-only analysis:

```bash
python verification/tools/run_bust_underbust_facts_v0.py \
  --input_npz verification/datasets/golden/bust_underbust_v0/golden_real_data_v0.npz \
  --n 200 \
  --out_dir verification/runs/facts/bust_underbust/REAL_$(date +%Y%m%d_%H%M)
```

**Output (not committed):**
- `verification/runs/facts/bust_underbust/REAL_YYYYMMDD_HHMM/facts_summary.json`
- `verification/runs/facts/bust_underbust/REAL_YYYYMMDD_HHMM/facts_per_sample.csv`

## NPZ Meta Validation

The facts runner automatically validates:
- `meta_unit` must be "m" (otherwise `UNIT_FAIL` warning recorded)
- `schema_version` presence (otherwise `GOLDEN_META_MISSING` warning recorded)
- Shape validation: `verts` must be (N, V, 3) for Golden datasets

## Notes

- Real-data golden NPZ uses placeholder verts generated from measurement data (not actual 3D meshes)
- In full implementation, this would load actual 3D mesh/verts from a mesh generation pipeline
- Schema mismatches are handled gracefully: warnings recorded, invalid cases skipped (no exceptions)
