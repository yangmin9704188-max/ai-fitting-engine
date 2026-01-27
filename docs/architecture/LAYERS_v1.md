# Architecture v1: Layers & Modules

## 목적

"제품형 AI + 리스크 관리"를 증명하는 구조입니다. 레이어 간 격리와 모듈 간 명확한 경계를 통해 재현 가능성과 유지보수성을 보장합니다.

## 6 Layers 정의

### L1 Contract (A, G)
- **핵심 역할**: 표준 키 정의, 단위/스케일 계약, 입력 정규화 전제
- **산출물**: `contract/*.json`, `docs/contract/standard_keys.md`
- **금지사항**: 구현 로직 포함 금지, Contract는 "무엇을 기대하는가"만 정의

### L2 Geometry (D)
- **핵심 역할**: SizeKorea 표준 기반 측정 로직 구현 (Convex Hull, 둘레 계산 등)
- **산출물**: `geometry_manifest.json`, mesh, measurements, NPZ
- **금지사항**: Validation/Confidence 레이어 로직 import 금지

### L3 Production (D, G)
- **핵심 역할**: 1.2만 명 대량 데이터 생성 및 경량화 (Sampling, NPZ 압축)
- **산출물**: 대량 NPZ 파일, 경량화된 mesh 데이터셋
- **금지사항**: Geometry 레이어 코드 직접 호출 금지, Artifact Interface로만 통신

### L4 Validation (C)
- **핵심 역할**: 이상치 탐지, 사실 기반 KPI 기록, 정합성 검토
- **산출물**: `facts_summary.json`, KPI Report, coverage backlog
- **금지사항**: Geometry/Production 레이어 코드 import 금지, Artifact만 읽기

### L5 Confidence (B)
- **핵심 역할**: 데이터 간 상관관계 분석, 체형별 가중치 추출, 통계적 근거 산출
- **산출물**: Feature Weights, Correlation Matrix, 분석 리포트
- **금지사항**: 하위 레이어 코드 import 금지, Artifact Interface로만 데이터 접근

### L6 Application (G)
- **핵심 역할**: 최종 SMPL-X 엔진 튜닝, 맞춤형 바디 모델 생성
- **산출물**: K-SMPL-X Model, 서비스 적용 산출물
- **금지사항**: 하위 레이어 코드 직접 호출 금지, Artifact Interface로만 통신

## 3 Modules 정의

### body
- **역할**: 신체 측정 로직 및 바디 모델 데이터
- **산출물**: body 측정 결과, body 스키마

### garment
- **역할**: 의상 자산/규격 관리
- **산출물**: garment 스펙, 규격 데이터

### fitting
- **역할**: Body×Garment 결합 결과 (충돌/드레이프/착장 산출)
- **산출물**: fitting 결과, 충돌 분석, 드레이프 시뮬레이션

## Cross-Layer Contamination 금지

- **레이어 간 코드 호출/직접 import 금지**: 레이어 간 통신은 "Artifact Interface(파일/스키마)"로만 이루어집니다.
- **Artifact-only 통신**: 각 레이어는 하위 레이어의 코드를 import하지 않고, 산출물(artifact)만 읽습니다.
- **geometry_manifest.json이 L2→L3 기본 인터페이스**: L2 Geometry 레이어에서 L3 Production 레이어로의 통신은 `geometry_manifest.json`(스키마: [geometry_manifest.schema.json](../../specs/common/geometry_manifest.schema.json))을 통해서만 이루어집니다.
- **레이어 간 직접 호출 금지**: 레이어 간 코드 호출이나 직접 import는 구조 오염으로 간주되며 merge가 차단됩니다.

## Cross-Module 참조 규칙

- **body ↔ garment 상호 import 금지**: `modules/body/**`는 `modules/garment/**`를 import 금지, 그 반대도 금지
- **fitting만 스키마 참조 허용**: `modules/fitting/**`만 `modules/body/**`, `modules/garment/**`의 "스키마(specs/schema)" 참조를 허용
- **허용 범위**: `modules/body/specs`, `modules/garment/specs`, `specs/body_schema.json` 등 스키마 경로만

## Artifact Interface (geometry_manifest.json)

모든 모듈의 L2 산출물은 `geometry_manifest.json`을 포함해야 합니다.

### 최소 스키마
- 스키마 경로: `specs/common/geometry_manifest.schema.json` (고정)
- 자세한 스키마 정의는 [geometry_manifest.schema.json](../../specs/common/geometry_manifest.schema.json) 참조

### 원칙
- 모든 L2 산출물은 `geometry_manifest.json` 포함 의무
- 스키마는 `specs/common/`으로 고정하여 일관성 유지

## Ops Plane 문서와의 연결

- [Ops Plane Charter](../ops/OPS_PLANE.md): 운영 체계 및 SoT 정의
- [Guardrails](../ops/GUARDRAILS.md): Import 경계 검사 및 구조 오염 방지 규칙
- [Backfill Policy](../ops/BACKFILL_POLICY.md): Tier 0/1/2 백필 정책
- [Backfill Log](../ops/BACKFILL_LOG.md): Tier2 백필 실행 기록
