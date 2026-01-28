# Round 67 - geo_v0_s1 (Success-not-processed wiring)

- RUN_DIR: verification/runs/facts/geo_v0_s1/round67_20260128_171454

## Facts

### Coverage / Counts
- total_cases: 200
- processed_cases: 199
- skipped_cases: 0
- has_mesh_path_true: 200
- has_mesh_path_null: 0

### Observability
- success_logged_count: 200
- success_not_processed_count: 0
- exec_fail_count: 0
- processed_sink_count: 0

### Evidence artifacts
- artifacts/skip_reasons.jsonl: 199 records
- artifacts/exec_failures.jsonl: 0 records (exists)
- artifacts/processed_sink.jsonl: 0 records (exists)
- artifacts/success_not_processed.jsonl: 0 records (exists)
- artifacts/visual/verts_proxy.npz: created (200 cases)
- mm->m conversion warnings: 200 cases

## Anomalies (facts-only)
- Loop reported "Processed 200/200", but skip_reasons.jsonl contains 199 records; 1 case has no skip_reason record despite skipped=0 and exec_fail=0.
- WARN observed: has_mesh_path_true expected 5 vs actual 200 (stale expectation signal).

## Next action proposal (facts-only)
- Add observability to detect and list missing skip_reason records (record_expected_total, record_actual_total, record_missing_case_ids) in next round.
