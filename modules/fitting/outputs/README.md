# Fitting Outputs

This directory contains experimental outputs from fitting module work.

## Structure

Each run should create a subdirectory named with a unique run ID:

```
outputs/
├── <run_id_1>/
│   ├── manifest.json       # Run metadata
│   ├── results/            # Raw fitting results
│   └── reports/            # Analysis reports
└── <run_id_2>/
    └── ...
```

## Naming Convention

Use descriptive run IDs with timestamps or semantic names:
- `fitting_experiment_20260128_001`
- `collision_test_v1`
- `drape_sim_round64`

## Artifacts Policy

- Large binary files (mesh outputs, NPZ files) should NOT be committed to git
- Use `.gitignore` patterns to exclude large artifacts
- Small metadata files (JSON, summary CSVs) may be committed if useful for review

## Review Process

1. Anti-gravity generates outputs here
2. Cursor or Claude Code reviews outputs
3. If approved, results are promoted to appropriate locations (e.g., `verification/runs/`, `artifacts/`)
