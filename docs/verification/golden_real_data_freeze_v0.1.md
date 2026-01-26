# Golden Real Data Freeze v0.1

**Purpose**: Real-data golden NPZ reproducibility freeze via case-id manifest (SSoT).

**Freeze Commit**: `[COMMIT_HASH]` (will be updated after commit)  
**Date**: 2026-01-26

**주의**: Git tag는 생성하지 않습니다. 이 Freeze는 Commit Hash로만 보증됩니다.

---

## Manifest (SSoT)

**경로**: `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.case_ids.json`

이 manifest는 "집합 + 순서"가 곧 SSoT입니다. 명단 외 케이스는 데이터가 아닙니다.

---

## How to reproduce

### 재생성 커맨드 (--case_ids_json 모드)

```bash
py verification/datasets/golden/core_measurements_v0/create_real_data_golden.py \
  --case_ids_json verification/datasets/golden/core_measurements_v0/golden_real_data_v0.case_ids.json \
  --out_npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz
```

**중요**: `--case_ids_json` 모드는 샘플링을 완전히 우회(Bypass)합니다.
- `--n_cases`, `--seed` 등 샘플링 관련 옵션은 무시됩니다.
- manifest에 있는 case_id가 소스에서 누락되면 명시적 오류로 종료됩니다 (재현성 강제).
- 출력 케이스 순서는 manifest 순서를 그대로 유지합니다.

---

## Freeze rule

**이후 발생하는 모든 Real-data Golden 관련 이슈는 리샘플링/분포개선 목적 샘플링으로 해결하지 않습니다.**

- manifest에 명시된 case_ids만 사용합니다.
- manifest 순서를 변경하지 않습니다.
- manifest에 없는 case_id를 추가하지 않습니다.

---

## 금지사항

- ❌ 리샘플링/분포개선 목적 샘플링 금지
- ❌ manifest 순서 변경 금지
- ❌ manifest에 없는 case_id 추가 금지
- ❌ Git tag 생성 금지 (Commit Hash만 사용)

---

## Outputs

- `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz`
- `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.case_ids.json` (manifest)

---

## Related Rounds

| Round | Purpose | Report |
|-------|---------|--------|
| 20 | Initial real-data golden creation | `reports/validation/curated_v0_facts_round1.md` |
| 21 | Gate v0 (facts-only sensors) | `reports/validation/curated_v0_facts_round21.md` |
| **22** | **Freeze via manifest (SSoT)** | `reports/validation/curated_v0_facts_round22.md` |

---

## Manifest extraction

현재 NPZ에서 manifest를 추출하려면:

```bash
py verification/datasets/golden/core_measurements_v0/extract_case_ids_manifest.py \
  --npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz \
  --out_json verification/datasets/golden/core_measurements_v0/golden_real_data_v0.case_ids.json
```
