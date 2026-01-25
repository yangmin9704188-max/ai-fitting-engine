# Lineage Manifest Contract v0

## Purpose

Lineage Manifest는 재현성/추적성을 위한 facts-only 기록입니다.
판정하지 않고 사실만 기록합니다.

## File Location

- `<current_run_dir>/LINEAGE.md`

## Schema

```markdown
# Lineage Manifest

**schema_version**: lineage@1

## Basic Info
- current_run_dir, lane, round_id, round_num

## Inputs
- npz_path, npz_path_abs, source_path_abs
- facts_summary.json 경로

## Code Fingerprints
- tools/postprocess_round.py git commit hash
- tools/summarize_facts_kpi.py git commit hash
- generator_script 경로 + commit hash (가능하면)

## Timestamps
- created_at (now)
- npz_mtime (있으면)
- facts_summary_mtime (있으면)

## Outputs
- KPI.md, KPI_DIFF.md, report, registry paths (존재 여부 포함)

## NPZ Metadata (있으면)
- schema_version, meta_unit
```

## 최소 필드 정의

### 필수 필드
- schema_version: "lineage@1"
- current_run_dir, lane, round_id, round_num
- facts_summary.json 경로

### 선택 필드
- npz_path, npz_path_abs (NPZ가 facts_summary에 기록되어 있으면)
- source_path_abs (NPZ 메타에 있으면)
- code_fingerprints (git이 있으면)
- timestamps (파일이 존재하면)
- outputs (파일이 존재하면)

## Notes

- 모든 경로는 가능하면 상대 경로로 저장
- git commit hash는 git이 없는 환경에서는 N/A로 처리 (크래시 금지)
- 파일이 없으면 "not found" 또는 "N/A"로 표기
