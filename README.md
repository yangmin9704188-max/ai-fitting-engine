# AI Fitting Engine

1인 개발 환경의 AI 기반 가상 피팅 엔진 프로젝트입니다.

## 프로젝트 개요

이 프로젝트는 AI 에이전트 분업 구조를 통해 1인 개발 환경에서도 체계적인 R&D와 운영을 가능하게 합니다.

## 폴더 구조

### 제품 로직
- **`engine/`**: 미래 제품 로직의 중심 (점진적 이전 예정)
  - 현재는 비어있으며, 향후 `core/`, `pipelines/` 로직이 점진적으로 이동될 예정
  - 이번 PR에서는 이동하지 않음

### 현재 실행 로직
- **`core/`**: 재사용 가능한 순수 로직 (측정 함수, 필터, 유틸리티)
- **`pipelines/`**: 실행 파이프라인
- **`verification/`**: 검증 러너 및 도구
- **`tests/`**: 테스트 스위트

### 운영 자동화
- **`tools/`**: 운영 자동화 스크립트
  - `sync_state.py`: CURRENT_STATE.md 패치 도구
  - `render_ai_prompt.py`: AI 협업 프롬프트 생성
  - `db_upsert.py`: DB 쓰기 단일 진입점

### 데이터베이스
- **`db/metadata.db`**: 공식 메타데이터 데이터베이스 (SQLite)
  - 모든 DB 쓰기 작업은 `tools/db_upsert.py`를 통해 이 파일에 기록됩니다
  - 스키마는 `db/schema.sql`에 정의되어 있습니다

### 실험 산출물
- **`artifacts/`**: 실험 실행 결과물
- **`experiments/`**: 실험 관련 파일
- **`logs/`**: 실행 로그

### 문서
- **`docs/`**: 프로젝트 문서
  - `archive/`: 레거시 문서 (강제 규칙 아님, 참고용)
  - `sync/`: Sync Hub 관련 문서

### 데이터 및 모델
- **`data/`**: 처리된 데이터
- **`models/`**: SMPL-X 모델 파일

## AI 분업 구조

프로젝트는 다음 역할로 분업됩니다:

- **Human**: 최종 의사결정, 문서 확정, Git Commit & Tag 실행
- **GPT**: 정책(Policy) 설계, 보고서/명세서 작성
- **Gemini**: 2차 검토, 논리적 반례 제시
- **Cursor**: 코드 작성, 실험 수행, 아티팩트 생성
- **Antigravity**: 실험 종료 후 DB 업데이트 자동화

## 하루 작업 루틴

### 작업 시작
1. `make ai-prompt` 또는 `make ai-prompt-json`으로 현재 상태 프롬프트 확인
2. `docs/templates/CURSOR_TASK_TEMPLATE.md` 템플릿 사용하여 작업 지시

### 작업 종료
1. 실험 결과 확인
2. `tools/db_upsert.py` 실행 (Antigravity가 자동 실행)
3. 필요 시 `tools/sync_state.py`로 CURRENT_STATE.md 업데이트

## 레거시 문서

`docs/archive/` 폴더에는 과거 문서들이 보관되어 있습니다.
이 문서들은 강제 규칙이 아니며, 참고용으로만 사용됩니다.

## Makefile 명령어

```bash
# AI 프롬프트 생성
make ai-prompt
make ai-prompt-json

# CURRENT_STATE.md 패치
make sync-dry ARGS="--set snapshot.status=candidate"
make sync ARGS="--set last_update.trigger=manual_test"
```

## 참고 문서

- `SYNC_HUB.md`: Sync Hub 구조 및 사용법
- `DB_GUIDE.md`: 데이터베이스 사용 가이드
- `engine/README.md`: Engine 폴더 설명
