# Engine

This folder will contain core product logic.

## Migration Plan

Logic from `core/` and `pipelines/` will be incrementally migrated to `engine/` over time.

**Important:** This PR does not perform any migration. The current structure is preserved:
- `core/`: Reusable pure logic (measurements, filters, utilities) - DO NOT MOVE YET
- `pipelines/`: Execution pipelines - DO NOT MOVE YET
- `verification/`: Verification runners and tools - DO NOT MOVE YET
- `tests/`: Test suites - DO NOT MOVE YET

Migration will happen incrementally in future PRs, not in this structure declaration PR.
