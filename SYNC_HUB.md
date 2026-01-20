# Sync Hub

Sync Hub는 프로젝트의 현재 상태를 추적하고 AI 협업을 위한 컨텍스트를 제공합니다.

## 파일 위치

- `docs/sync/CURRENT_STATE.md`: 현재 상태 정의 파일

## 구조

### Snapshot
- `id`: 스냅샷 식별자
- `status`: candidate | hold | released
- `last_change`: code | weight | config | dataset
- `version_keys`: 버전 키 플래그들

### Pipeline
- `position`: rd | local_validation | promotion | release_hold | production
- `active_runbook`: 활성 런북

### Signals
- `validation`: 검증 상태 및 불확실성 트렌드
- `cost`: 비용 신호 (pure, egress, cost_model_version)
- `latency`: 지연 시간 신호

### Decision
- `promotion`: 승격 상태
- `release`: 릴리스 상태
- `authority`: 권한
- `artifacts`: 아티팩트 참조

### Constraints
- `technical`: 기술적 제약
- `operational`: 운영적 제약

### Actions
- `allowed_actions`: 허용된 액션 목록
- `forbidden_actions`: 금지된 액션 목록

### Last Update
- `date`: 마지막 업데이트 날짜
- `trigger`: 업데이트 트리거

## Scope Lock

Sync Hub는 다음 범위로 제한됩니다:

- **허용**: 값 업데이트 (의미 해석 없이)
- **금지**: 구조 변경, 의미 해석/요약/설명 추가, 판단/이유 로직 추가

## 사용 도구

- `tools/sync_state.py`: CURRENT_STATE.md 패치 도구
- `tools/render_ai_prompt.py`: AI 협업 프롬프트 생성

## 업데이트 규칙

1. 코드/파이프라인 경로 변경 시 CURRENT_STATE.md 업데이트 필요 (CI Guard 강제)
2. 값만 변경 (설명 추가 금지)
3. 화이트리스트 기반 path만 수정 가능
