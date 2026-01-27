# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Fitting Engine - a virtual fitting engine built on Korean standard body data (SizeKorea) that generates explainable, reproducible 3D body shapes from body measurements (no photos required).

## Architecture: 6 Layers + 3 Modules

**6 Layers** (data flows top-to-bottom, inter-layer code imports forbidden):
1. **Contract (L1)**: Standard key definitions, unit/scale contracts
2. **Geometry (L2)**: SizeKorea-based measurement logic (Convex Hull, circumference calculations)
3. **Production (L3)**: Large-scale data generation, NPZ compression
4. **Validation (L4)**: Anomaly detection, facts-based KPI recording (no PASS/FAIL thresholds)
5. **Confidence (L5)**: Correlation analysis, body-type weights
6. **Application (L6)**: Final SMPL-X engine tuning, custom body model generation

**3 Modules** (cross-module imports forbidden except fitting→schemas):
- `body`: Body measurement logic and body model data
- `garment`: Garment asset/specification management
- `fitting`: Body×Garment combination results (collision/drape/fitting)

**Critical Rules**:
- Layer communication via artifacts only (no code imports between layers)
- `modules/body/**` and `modules/garment/**` cannot import each other
- Only `modules/fitting/**` may reference body/garment schemas
- Canonical unit: **meters (m)**, precision: 0.001m (1mm)
- SMPL-X standard coordinate system

## Common Commands

```bash
# Run verification round (curated_v0)
make curated_v0_round RUN_DIR=verification/runs/facts/curated_v0/<round_dir>

# Run geo v0 S1 round
make geo_v0_s1_round RUN_DIR=verification/runs/facts/geo_v0_s1/<round_dir>

# Postprocess round (required after every round execution)
make postprocess RUN_DIR=<round_dir>
python tools/postprocess_round.py --current_run_dir <round_dir>

# Check ops lock (run before PR to verify no forbidden changes)
make ops_guard
python tools/ops/check_ops_lock.py --base main

# Golden registry patch
make golden-apply PATCH=<patch.json>

# Run tests
pytest tests/
pytest tests/test_<name>.py  # single test file
```

## Key Documents (Single Source of Truth)

- **Master Plan**: `docs/ops/MASTER_PLAN.md`
- **Current State**: `SYNC_HUB.md`
- **Architecture**: `docs/architecture/LAYERS_v1.md`
- **Standard Keys**: `docs/contract/standard_keys.md`
- **Guardrails**: `docs/ops/GUARDRAILS.md`

## Strict Safety Rules (Always Apply)

1. **NO DELETIONS**: `git rm` forbidden without explicit user approval
2. **NO LARGE-SCALE FILE MOVES**: Do not move `core/`, `pipelines/`, `verification/`, `tests/`
3. **NO UNREQUESTED REFACTORING**: Do not clean up unrequested functions/files
4. **NO SEMANTIC POLICY DRIFT**: Do not modify standard key definitions or policy documents without approval
5. **NO SMART GUESSING**: No automatic similar-matching, auto-substitution, or guess-based modifications
6. **NO HARDCODED KEY CHECKS**: Never use `if key == '...'` pattern to hide problems

## Prohibited Modifications (Without Explicit Instruction)

- `data/`, `models/`, `artifacts/`, `experiments/` (source data/outputs)
- `verification/runs/` (execution outputs - never commit)
- Legacy documentation rewrites

## Validation Layer Policy

- Validation layer records **facts only** (no PASS/FAIL judgments)
- Output path: `verification/reports/<measurement_key>_v0/`
- Facts output: `verification/runs/facts/...` (do not commit)

## Round Execution Protocol

After any round execution, **always** run postprocessing:
```bash
python tools/postprocess_round.py --current_run_dir <out_dir>
```

When `facts_summary.json` exists, include KPI Header in reports using:
```bash
python tools/summarize_facts_kpi.py <facts_summary.json>
```

## PR Requirements

- Include: changed file list, reproduction commands, scope compliance summary
- Changes to `core/`, `tests/`, `verification/`, `tools/`, `db/`, `pipelines/`, `.github/workflows/` require `docs/sync/CURRENT_STATE.md` update
- New round records: add via `docs/ops/rounds/roundXX.md` only (append-only)
