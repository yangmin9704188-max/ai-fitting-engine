## Summary

Round14 마무리: stale invariant-fail 로깅 정리 + verts 기반 bust 정합 보정.

## Changes

### A) 로깅 정리
- **이전**: "Last invariant fail analysis"가 과거 fail JSON을 읽어 성공 run과 혼선.
- **이후**: 성공 run에서만 해당 블록 출력. 출력 시 "STALE / Previous invariant fail record" 명시, timestamp + "This is previous fail record; current run passed" 문구.
- FAST MODE에서 요약은 run **종료 후** (성공 시)에만 출력.

### B) verts 기반 bust 정합 보정
- **이전**: `bust_circ_theoretical ≈ 1.27m`, `bust_circ_from_verts ≈ 1.91m` 불일치.
- **이후**: normal_1(fastmode)에서 xz_scale_factor로 x,z만 중심 기준 스케일. `bust_circ_from_verts_after`가 theoretical에 정합.
- `desired_radius = bust_circ_est / (2*pi)`, `xz_factor = desired_radius / actual_radius_from_verts`. y 미변경으로 HEIGHT(y-span) proof 유지.

### C) 로그 증명
- `bust_circ_after_scale_theoretical`, `bust_circ_from_verts_before` / `bust_circ_from_verts_after`, `xz_scale_factor` 로그 및 trace JSON 저장.

## Test Results

```
[SYNTH CIRC DEBUG] case=normal_1
  bust_circ_after_scale_theoretical=1.2701m
  bust_circ_from_verts_before=1.9084m
  xz_scale_factor=0.6655
  bust_circ_from_verts_after=1.2701m
  clamp_applied=False
[OK] normal_1 (valid): passed
```

- `bust_circ_from_verts_after` ~1.27m (theoretical 대비 허용 오차 내)
- `clamp_applied=False`, HEIGHT proof 유지
- NPZ save / reopen proof 유지

## Related
- Trace: `verification/datasets/runs/debug/s0_circ_synth_trace_normal_1.json`
- Runner: `verification/runs/facts/geo_v0/round15_bust_verts_aligned_normal1/`
