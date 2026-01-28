# Module: body

Body module produces upstream body artifacts (e.g., `facts_summary.json`) for other modules.

## Canonical Reference

Cross-module interfaces are canonical in `contracts/interface_ledger_v0.md`. Do not duplicate rules here.

## Core Policies

- Facts-only (no PASS/FAIL). Units: meters (m). NaN/Inf serialize as null.
- All cross-module artifacts MUST carry 4 version keys: `snapshot_version`, `semantic_version`, `geometry_impl_version`, `dataset_version` (unknown=`"UNSPECIFIED"` + warning `VERSION_KEY_UNSPECIFIED`).
- New rounds: `docs/ops/rounds/<lane_slug>/<milestone_id>/round_<NN>.md` (per-lane, per-milestone reset).

## Links

- [Interface Ledger v0](../../contracts/interface_ledger_v0.md) — cross-module SSoT
- [geo_v0_s1 Contract](../../docs/policies/measurements/geo_v0_s1_contract_v0.md) — body/geo_v0_s1 lane contract
