.

🚀 AI Fitting Engine: Logic Core
본 레포지토리는 B2B 가상 피팅 서비스를 위한 설명 가능하고 재현 가능한 체형 생성 엔진의 로직 코어를 관리합니다.

📌 Single Source of Truth (SoT)
모든 전략적 결정과 철학은 아래 문서를 단일 진실원으로 삼습니다.

전략 및 철학: docs/MASTER_PLAN.md (또는 Notion Master Plan v1.1) 참조

실시간 상태: SYNC_HUB.md (현재 마일스톤 및 릴리즈 상태)

🏗️ 5-Layer R&D Pipeline
본 프로젝트는 레이어 간 의존성을 격리하기 위해 5계층 파이프라인을 준수합니다.

Semantic: docs/policies/measurements/ (의미 정의)

Contract: docs/policies/measurements/ (인터페이스 규격)

Geometric: core/measurements/ (구현 로직)

Validation: verification/reports/ (사실 기록)

Judgment: docs/judgments/ (해석 및 질문)

📂 Directory Structure (Map)
레포지토리의 주요 구조와 역할은 다음과 같습니다.

Core Logic
core/: 재사용 가능한 순수 로직 (측정 함수, 필터, 유틸리티)

pipelines/: 실험 및 실행 파이프라인

engine/: (Future) 제품 로직 통합 공간 (현재 점진적 이전 중)

Verification & Ops
verification/: 5-Layer 검증 러너 및 골든 데이터셋(NPZ)

tools/: 운영 자동화 (sync_state.py, db_upsert.py, render_ai_prompt.py)

db/: 공식 메타데이터 및 스키마 관리 (SQLite)

Data & Artifacts
data/: 처리된 데이터 및 데이터셋

models/: SMPL-X 모델 파라미터 및 관련 파일

artifacts/: 실험 실행 결과물 및 로그

🛠️ Quick Start & Commands
AI 에이전트와의 협업 및 시스템 운영을 위한 주요 명령어입니다.

Bash

# AI 협업용 프롬프트 생성
make ai-prompt

# 특정 측정 항목 v0 검증 실행
python verification/runners/verify_chest_v0.py

# 시스템 상태 업데이트 (SYNC HUB 동기화)
make sync ARGS="--set snapshot.status=candidate"
📏 Technical Standards
단위(Unit): 모든 내부 인터페이스 및 연산은 meters(m) 단위를 표준으로 합니다.

좌표계: SMPL-X 표준 좌표계를 준수합니다.

지적 정직성: 정의되지 않은 상황(Degenerate)에서는 억지로 값을 추정하지 않고 NaN을 반환합니다.