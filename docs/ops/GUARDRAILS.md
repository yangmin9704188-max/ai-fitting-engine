# Guardrails

## Blocker (머지 차단)

### 구조 오염
- **Import 경계 검사 실패 시 Blocker 발동(merge 차단)**
- Cross-Module 참조 위반 시 merge 차단
- Cross-Layer contamination 금지 (레이어 간 코드 호출/직접 import 금지)

## Warning (경고)

- 환경차로 흔들릴 수 있는 자동 문서 생성/포맷팅류는 Warning으로 처리
- Warning은 merge를 차단하지 않음

## Cross-Layer Contamination 금지

레이어 간 코드 호출/직접 import는 금지됩니다. 레이어 간 통신은 artifact-only 원칙을 따르며, '링크/참조'로만 이루어집니다.

## Cross-Module 참조 허용범위

### 금지 규칙
- `modules/body/**`는 `modules/garment/**`를 import 금지
- `modules/garment/**`는 `modules/body/**` import 금지

### 허용 규칙
- `modules/fitting/**`만 `modules/body/**`, `modules/garment/**`의 "스키마(specs/schema)" 참조를 허용
- 허용 범위는 문자열 패턴으로 좁게 제한:
  - `modules/body/specs`
  - `modules/garment/specs`
  - `specs/body_schema.json` 등

## 전환기 처리 원칙

아직 `modules/`가 없거나 일부만 도입된 상황에서:
- 대상 폴더가 없으면 검사 스킵(PASS)하되, 경고 1줄만 출력 가능
- `modules/` 디렉토리가 존재하지 않으면 검사 스킵 후 exit 0

## Import 경계 검사

Import 경계 검사는 `tools/ops/check_import_boundaries.py` 스크립트로 수행됩니다.

### 검사 대상
- `modules/body/**`가 `modules/garment/**`를 참조하면 FAIL
- `modules/garment/**`가 `modules/body/**`를 참조하면 FAIL
- `modules/fitting/**`만 body/garment의 스키마 경로(specs/schema) 참조 허용

### 출력
- 위반 건수 0이면 exit 0
- 위반 있으면 위반 목록 출력 후 exit 1
- `modules/`가 없으면 "SKIP: modules/ not found" 한 줄 출력 후 exit 0

## 참고

- 레이어 오염(geometry가 validation을 import 등)은 이 PR에서 강제 검사까지는 하지 않고, Guardrails 문서에 정책만 먼저 고정 (추후 확장 여지)
