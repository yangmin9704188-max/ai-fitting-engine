# DoD Checklists v1 (Evidence-first)

모든 항목은 체크박스 + 끝에 `(Evidence: <path>)`가 붙어 파일 존재로 완료 판단이 가능합니다.

## L1 Contract DoD

- [ ] Standard Keys 정의 문서 존재 (Evidence: `docs/contract/standard_keys.md`)
- [ ] Contract JSON 파일 존재 (Evidence: TBD — will be created in module adoption PR)
- [ ] 단위/스케일 계약 문서화 (Evidence: `docs/contract/measurement_coverage_v0.csv`)

## L2 Geometry DoD

- [ ] geometry_manifest.json 스키마 정의 (Evidence: `specs/common/geometry_manifest.schema.json`)
- [ ] 모든 모듈의 L2 산출물에 geometry_manifest.json 포함 (Evidence: `modules/*/outputs/*/geometry_manifest.json`)
- [ ] 측정 로직 구현 (Evidence: `modules/body/measurements/*.py` 또는 `core/measurements/*.py`)

## L3 Production DoD

- [ ] 대량 데이터 생성 파이프라인 구현 (Evidence: `verification/runners/*.py` 또는 `modules/*/production/*.py`)
- [ ] 경량화 로직 구현 (Evidence: NPZ 파일 또는 경량화 스크립트)
- [ ] Production 산출물에 geometry_manifest.json 포함 (Evidence: `verification/runs/**/geometry_manifest.json`)

## L4 Validation DoD

- [ ] 이상치 탐지 로직 구현 (Evidence: `verification/tools/*.py` 또는 `modules/*/validation/*.py`)
- [ ] facts_summary.json 생성 (Evidence: `verification/runs/**/facts_summary.json`)
- [ ] KPI Report 생성 (Evidence: `reports/validation/*.md`)
- [ ] Coverage backlog 관리 (Evidence: `reports/validation/coverage_backlog.md`)

## L5 Confidence DoD

- [ ] 상관관계 분석 로직 구현 (Evidence: `modules/*/confidence/*.py` 또는 분석 스크립트)
- [ ] Feature Weights 산출 (Evidence: `artifacts/confidence/feature_weights.json`)
- [ ] Correlation Matrix 산출 (Evidence: `artifacts/confidence/correlation_matrix.json`)

## L6 Application DoD

- [ ] SMPL-X 튜닝 파이프라인 구현 (Evidence: `modules/application/*.py` 또는 튜닝 스크립트)
- [ ] 최종 모델 산출물 생성 (Evidence: `models/k_smplx/*.pkl` 또는 모델 파일)
- [ ] 서비스 적용 산출물 생성 (Evidence: `artifacts/application/*`)

## Ops Plane DoD

- [ ] Import 경계 검사 실패 시 Blocker 발동(merge 차단) (Evidence: `docs/ops/GUARDRAILS.md`)
- [ ] Import 경계 검사 스크립트 존재 (Evidence: `tools/ops/check_import_boundaries.py`)
- [ ] Tier2 backfill 기록 의무(폐기된 골든셋 명시) (Evidence: `docs/ops/BACKFILL_LOG.md`)
- [ ] Ops Plane Charter 문서 존재 (Evidence: `docs/ops/OPS_PLANE.md`)
- [ ] Backfill Policy 문서 존재 (Evidence: `docs/ops/BACKFILL_POLICY.md`)

## Cross-Layer Contamination 검사 DoD

- [ ] 레이어 간 코드 import 금지 정책 문서화 (Evidence: `docs/architecture/LAYERS_v1.md`)
- [ ] Artifact Interface 표준 정의 (Evidence: `specs/common/geometry_manifest.schema.json`)

## Cross-Module 참조 검사 DoD

- [ ] body ↔ garment 상호 import 금지 정책 문서화 (Evidence: `docs/architecture/LAYERS_v1.md`)
- [ ] fitting만 스키마 참조 허용 정책 문서화 (Evidence: `docs/architecture/LAYERS_v1.md`)
- [ ] Import 경계 검사 스크립트 실행 통과 (Evidence: `tools/ops/check_import_boundaries.py` 실행 결과)
