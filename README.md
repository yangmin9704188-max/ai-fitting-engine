\### 🚀 AI Fitting Engine: Logic Core (v1.2)

본 레포지토리는 한국인 표준 체형 데이터(SizeKorea)를 기반으로 한 설명 가능하고 재현 가능한 가상 피팅 엔진의 로직 코어를 관리합니다.



\### 📌 Single Source of Truth (SoT)#

모든 전략적 결정과 엔진 아키텍처는 아래 문서를 단일 진실원으로 삼습니다.



전략 및 마스터 플랜: docs/ops/MASTER\_PLAN.md (v1.2 Refined)



현재 프로젝트 상태: SYNC\_HUB.md



로컬 파일 인덱스: SYNC\_HUB\_FILE\_INDEX.md



\### 🏗️ 5-Layer R\&D Pipeline (Architecture v1.2)#

본 프로젝트는 데이터 흐름과 로직을 5개의 계층으로 격리하여 운영합니다.



L1: Geometry: SizeKorea 표준 기반 측정 로직 (core/measurements/)



L2: Production: 1.2만 명 대량 데이터 생성 및 경량화 (verification/runners/)



L3: Validation: 이상치 탐지 및 사실 기반 KPI 기록 (verification/runs/)



L4: Intelligence: 데이터 간 상관관계 및 체형 가중치 분석



L5: Application: 튜닝된 SMPL-X 기반 최종 바디 모델 서비스화



\### 📂 Directory Structure (Map)

전체 구조는 docs/ops/PROJECT\_STRUCTURE.md를 참조하세요.



core/: 핵심 기하학 연산 로직 (Convex Hull 기반 둘레 측정 등)



data/: SizeKorea 원천 데이터 및 전처리된 데이터셋



verification/: 골든 데이터셋(NPZ) 및 라운드별 실행 엔진



docs/ops/: 프로젝트 운영 가이드, INDEX, PR 기록물



artifacts/: 각 실행 라운드에서 생성된 시각화 지표 및 로그



\### 📏 Technical Standards

표준 단위: 모든 내부 인터페이스는 Meters(m) 단위를 사용합니다.



좌표계: SMPL-X 표준 좌표계를 준수합니다.



지적 정직성: 정의되지 않은 상황(Degenerate)에서는 억지로 값을 추정하지 않고 NaN을 반환하며, 사유를 기록합니다.



측정 원칙: 수치 보정을 위한 상수 클램프(Clamp) 사용을 절대 금지하며, 기하학적 해결책(Convex Hull 등)만을 사용합니다.

