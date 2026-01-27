# Legacy Map

## 목적

레거시를 건드리지 않고 새 표준(v1)으로 이동하는 가이드입니다.

## 원칙

- **레거시는 삭제/이동하지 않는다**: 안전/충돌 방지를 위해 기존 문서/폴더는 그대로 유지합니다.
- **새 작업은 v1 경로로만 추가한다**: 앞으로 생성되는 모든 문서/코드는 v1 표준 경로를 따릅니다.
- **레거시 수정이 필요하면 '최소 링크'만 추가한다**: 레거시 문서를 수정해야 할 경우, 본문 대량 수정 없이 v1 문서 링크만 추가합니다.

## SSoT Links (v1 표준)

새 작업은 다음 문서를 단일 진실원(SSoT)으로 참조합니다:

- **Architecture**: [`docs/architecture/LAYERS_v1.md`](architecture/LAYERS_v1.md) - 6 Layers, 3 Modules 정의
- **DoD Checklists**: [`docs/architecture/DoD_CHECKLISTS_v1.md`](architecture/DoD_CHECKLISTS_v1.md) - Evidence-first DoD 체크리스트
- **Ops Plane**: [`docs/ops/OPS_PLANE.md`](ops/OPS_PLANE.md) - Ops Plane Charter
- **Guardrails**: [`docs/ops/GUARDRAILS.md`](ops/GUARDRAILS.md) - Import 경계 검사 및 구조 오염 방지 규칙
- **Backfill Policy**: [`docs/ops/BACKFILL_POLICY.md`](ops/BACKFILL_POLICY.md) - Tier 0/1/2 백필 정책
- **Backfill Log**: [`docs/ops/BACKFILL_LOG.md`](ops/BACKFILL_LOG.md) - Tier2 백필 실행 기록

## Legacy → Recommended v1 Mapping

### 측정/기하 관련 문서

| Legacy 위치 | Recommended v1 경로 | 비고 |
|------------|---------------------|------|
| `core/measurements/` | `modules/body/measurements/` (점진 도입) | 기존 코드는 이동하지 않음, 새 코드만 modules로 |
| `docs/policies/measurements/` | `docs/architecture/` 또는 `modules/body/specs/` | 레거시는 유지, 새 문서는 v1 경로로 |
| `docs/architecture_final_plan.md` | `docs/architecture/LAYERS_v1.md` 참조 | 레거시 문서는 유지, v1 링크만 추가 |

### Ops 관련 문서

| Legacy 위치 | Recommended v1 경로 | 비고 |
|------------|---------------------|------|
| 기존 ops 문서 | `docs/ops/` (현존 경로 유지) | 이미 v1 표준 경로에 있음 |
| 라운드 기록 | `docs/ops/rounds/roundXX.md` | 새 라운드 기록은 이 경로로만 추가 |

### Validation Report

| Legacy 위치 | Recommended v1 경로 | 비고 |
|------------|---------------------|------|
| `reports/validation/` | `reports/validation/` (현존 경로 유지) | 기존 경로 유지 |

### Geometry 산출물 인터페이스

| Legacy 위치 | Recommended v1 경로 | 비고 |
|------------|---------------------|------|
| 기존 산출물 | `specs/common/geometry_manifest.schema.json` | 모든 L2 산출물은 이 스키마를 따라야 함 |

**중요**: 위 매핑은 "이동하지 말고 링크만 추가"를 의미합니다. 레거시 파일을 삭제하거나 이동하지 않습니다.

## 새 파일을 어디에 만들 것인가

### 라운드 기록
- **경로**: `docs/ops/rounds/roundXX.md`
- **템플릿**: [`docs/ops/rounds/ROUND_TEMPLATE.md`](ops/rounds/ROUND_TEMPLATE.md) 참조

### 새 레이어/모듈 문서
- **기준**: [`docs/architecture/LAYERS_v1.md`](architecture/LAYERS_v1.md)의 레이어/모듈 정의를 따름
- **경로 예시**:
  - L2 Geometry 문서: `docs/architecture/` 또는 `modules/<module>/geometry/`
  - 모듈 스펙: `modules/<module>/specs/`

### Geometry 산출물 인터페이스
- **스키마 경로**: `specs/common/geometry_manifest.schema.json` (고정)
- **모든 L2 산출물**: `geometry_manifest.json` 포함 의무

## 전환 전략

1. **점진 도입**: 기존 코드/문서는 그대로 유지하고, 새 작업만 v1 경로로 추가
2. **링크 우선**: 레거시 문서 수정이 필요하면 본문 대량 수정 없이 v1 문서 링크만 추가
3. **안전 우선**: 레거시 삭제/이동은 하지 않음 (충돌 방지)
