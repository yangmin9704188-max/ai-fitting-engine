# Round 45

## Goal
Make torso-only channel produce at least one numeric value even when failure_reason is SINGLE_COMPONENT_ONLY, and add torso debug summary stats (area/perimeter/circularity proxy) to facts_summary.

## Changes
- **Single Component Fallback**:
  - core_measurements_v0: If `failure_reason == SINGLE_COMPONENT_ONLY` and perimeter is still None after Round44 hull fallback, compute `torso_perimeter` from single component using ordering → unordered → convex hull fallback chain. Record `TORSO_SINGLE_COMPONENT_FALLBACK_USED` flag when used.
  - runner: Aggregate `TORSO_SINGLE_COMPONENT_FALLBACK_USED` counts (per case/key) and add to `facts_summary` if > 0.
- **Torso Debug Summary Stats**:
  - runner: Collect per-key `area`, `perimeter`, and `circularity_proxy` (perimeter^2/area) from `torso_info["torso_stats"]` for processed cases.
  - runner: Compute summary statistics (min/max/median/p50/p95) for each metric per key and add to `facts_summary["torso_debug_stats_summary"]`.
- **Full Keys Unchanged**: Existing full keys (`*_CIRC_M`) logic remains unchanged.

## Artifacts
- **run_dir**: `verification/runs/facts/geo_v0_s1/round45_20260127_191401`
- **facts_summary**: `verification/runs/facts/geo_v0_s1/round45_20260127_191401/facts_summary.json`
- **KPI**: `verification/runs/facts/geo_v0_s1/round45_20260127_191401/KPI.md`
- **KPI_DIFF**: `verification/runs/facts/geo_v0_s1/round45_20260127_191401/KPI_DIFF.md`

## PR Link
[PR #214](https://github.com/yangmin9704188-max/ai-fitting-engine/pull/214)

## Notes
- **Run Statistics**: total_cases=200, processed=5, skipped=195, has_mesh_path_true=5, has_mesh_path_null=195
- **Torso Keys NaN Rate**: 0.0 for NECK_CIRC_TORSO_M, BUST_CIRC_TORSO_M, UNDERBUST_CIRC_TORSO_M (all 5 cases have numeric values)
- **Failure Reasons TopK**: `SINGLE_COMPONENT_ONLY=5` (all 5 processed cases)
- **Torso Diagnostics Summary**: Present with `n_intersection_points_summary`, `n_segments_summary`, `n_components_summary` for NECK_CIRC_M, BUST_CIRC_M, UNDERBUST_CIRC_M
- **Torso Debug Stats Summary**: Present with `area`, `perimeter`, `circularity_proxy` statistics (min/max/median/p50/p95) for NECK_CIRC_M, BUST_CIRC_M, UNDERBUST_CIRC_M
- **TORSO_SINGLE_COMPONENT_FALLBACK_USED**: 0 in this run (single component fallback not used; values computed via normal ordering/perimeter path)
- **Full Keys**: No changes to `*_CIRC_M` logic; all values computed successfully (nan_rate=0.0 for all keys)
