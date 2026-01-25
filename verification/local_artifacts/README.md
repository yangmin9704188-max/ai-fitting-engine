# Local Artifacts

이 폴더는 로컬에서 생성된 실험/테스트 산출물을 임시 보관합니다.

## 원칙

- **baseline/공식 리포트**는 `reports/validation/`의 고정 파일명으로만 커밋합니다.
- 이 폴더는 gitignored이며, PR에 포함되지 않습니다.
- 테스트/실험 산출물은 이 폴더로 이동하여 로컬에서만 관리합니다.

## 공식 리포트 (커밋 대상)

공식 리포트는 다음 문서에 명시된 고정 파일명만 커밋합니다:
- `reports/validation/INDEX.md`
- `docs/verification/golden_s0_freeze_v0.md`
- `docs/verification/round_registry.json`

예:
- `reports/validation/geo_v0_facts_round17_valid10_expanded.md` (기준선)
- `reports/validation/curated_v0_facts_round1.md` (round20 기준선)

## 로컬 테스트 산출물

테스트로 생성된 리포트는 이 폴더로 이동하여 로컬에서만 관리합니다.
예: `geo_v0_facts_round2.md` ~ `round10.md` (공식 리포트가 아닌 테스트 산출물)
