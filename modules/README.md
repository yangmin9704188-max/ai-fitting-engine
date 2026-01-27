# Modules

modules는 코드/스펙/아티팩트의 물리적 경계를 정의합니다.

## 모듈 구조

- **body**: 신체 측정 로직 및 바디 모델 데이터
- **garment**: 의상 자산/규격 관리
- **fitting**: Body×Garment 결합 결과 (충돌/드레이프/착장 산출)

## Cross-Module 규칙 요약

- **body ↔ garment 상호 import 금지**: `modules/body/**`는 `modules/garment/**`를 import 금지, 그 반대도 금지
- **fitting만 스키마 참조 허용**: `modules/fitting/**`만 `modules/body/**`, `modules/garment/**`의 "스키마(specs/schema)" 참조를 허용

자세한 규칙은 [`docs/architecture/LAYERS_v1.md`](../docs/architecture/LAYERS_v1.md) 및 [`docs/ops/GUARDRAILS.md`](../docs/ops/GUARDRAILS.md)를 참조하세요.

## 전환 전략

**점진 도입**: 아직 레거시 코드가 `core/`, `pipelines/` 등에 존재하므로, modules는 점진적으로 도입됩니다.

- 기존 코드는 이동하지 않음 (대이동 금지)
- 새 코드만 modules 구조를 따름
- Import 경계 검사: `tools/ops/check_import_boundaries.py`로 검증

## 참고 문서

- [Architecture v1](../docs/architecture/LAYERS_v1.md)
- [Legacy Map](../docs/LEGACY_MAP.md)
- [Guardrails](../docs/ops/GUARDRAILS.md)
