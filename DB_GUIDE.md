# Database Guide

## 공식 데이터베이스

**공식 DB 경로:** `db/metadata.db` (SQLite)

이 프로젝트는 단일 공식 데이터베이스만 사용합니다. 모든 DB 쓰기 작업은 `tools/db_upsert.py`를 통해 이 파일에 기록됩니다.

## 목적

데이터베이스는 **artifact 인덱스(검색/집계/상태)** 역할을 합니다.

**중요 원칙:**
- 문서 전문은 Git에 저장
- 메타데이터만 DB에 저장
- DB는 검색/집계를 위한 인덱스 역할
- 5-Layer는 논리 흐름/분류 축이며, policy/spec/run/report는 artifact 타입 (교차 분류)

## 5-Layer 체제

본 프로젝트는 **5-Layer R&D 파이프라인**을 따릅니다:

### L1 Semantic (정의)
- "무엇을 재는가?"에 대한 의미론적 정의
- 불변/금지 사항 명시
- 예: CHEST는 가슴 볼륨이 아닌 흉곽 기반 측정

### L2 Contract (계약)
- "어떤 규격으로 소통하는가?"에 대한 약속
- 키/단위/입출력 계약
- 예: 모든 입력은 미터(m) 단위, 결과는 NaN 허용

### L3 Geometric (구현)
- "어떻게 계산하는가?"에 대한 최소 구현
- 알고리즘 절차 (판정 없음)
- 예: 중앙값 기반의 단면 슬라이싱

### L4 Validation (검증)
- "기록된 사실은 무엇인가?"에 대한 리스크 센싱
- 사실 기록 중심 (Warning/NaN/degenerate)
- **PASS/FAIL 판정 금지**

### L5 Judgment (판단)
- "이 결과의 의미는 무엇인가?"에 대한 서술적 해석
- Open Questions 도출
- **액션 지시 금지**

## 스키마

SQLite 기반 6개 테이블:

### 1. policies
정책 메타데이터

- `id`: 정책 ID (PK)
- `name`: 정책 이름
- `version`: 정책 버전
- `status`: 상태 (draft | candidate | frozen | archived | deprecated)
- `created_at`: 생성 시간
- `frozen_at`: Frozen 시점 (NULL 가능)
- `frozen_git_tag`: Frozen Git Tag (NULL 가능)
- `frozen_commit_sha`: Frozen Commit SHA (NULL 가능)
- `base_commit`: Base Commit SHA

### 2. experiments
실험 메타데이터

- `id`: 실험 ID (PK)
- `experiment_id`: 실험 식별자 (고유)
- `policy_id`: 정책 ID (FK)
- `run_id`: 실행 ID
- `status`: 상태
- `created_at`: 생성 시간
- `extra_json`: 추가 메타데이터 (JSON)

**원칙:**
- 정책 버전과 실험 ID는 분리
- `extra_json`은 유연한 메타데이터 확장용

### 3. reports
보고서 메타데이터

- `id`: 보고서 ID (PK)
- `report_id`: 보고서 식별자 (고유)
- `policy_name`: 정책 이름
- `policy_version`: 정책 버전
- `result`: 결과 (pass | fail | hold) - **판정 필드로 사용 금지**
- `created_at`: 생성 시간
- `artifacts_path`: 아티팩트 경로
- `inputs`: 입력 정보

**중요:**
- `result` 필드는 레거시 호환성을 위해 유지되지만, **5-Layer 체제에서는 판정 필드로 사용하지 않습니다**
- Validation Layer (L4)는 PASS/FAIL 판정을 하지 않으며, 사실 기록만 수행합니다
- Judgment Layer (L5)는 서술적 해석만 제공하며, 액션 지시를 하지 않습니다
- `report_type`과 `extra_json`을 통해 "validation_frame" 또는 "judgment_memo" 등 기록 성격으로 해석합니다

### 4. policy_changes
정책 변경 이력

- `id`: 변경 ID (PK)
- `policy_id`: 정책 ID (FK)
- `change_type`: 변경 타입
- `from_version`: 이전 버전
- `to_version`: 새 버전
- `commit_sha`: 변경 커밋 SHA
- `created_at`: 생성 시간

### 5. specs
명세서 메타데이터

- `id`: 명세서 ID (PK)
- `spec_type`: 명세서 타입
- `related_policy_id`: 관련 정책 ID (FK, NULL 가능)
- `git_commit`: Git 커밋 SHA
- `file_path`: 파일 경로
- `created_at`: 생성 시간

### 6. artifacts (신규)
Artifact 인덱스 (5-Layer 분류)

- `id`: Artifact ID (PK)
- `artifact_type`: Artifact 타입 (policy | spec | run | report | dataset | judgment_memo 등)
- `layer`: 레이어 (L1 | L2 | L3 | L4 | L5) - **필수**
- `policy_id`: 정책 ID (FK, NULL 가능)
- `experiment_id`: 실험 ID (FK, NULL 가능)
- `related_measurement_key`: 관련 측정 키 (TEXT, NULL 가능)
  - **반드시 UNDERBUST/BUST 구분 기록**
  - 표준 키: "UNDERBUST" 또는 "BUST"
  - 레거시 CHEST는 "CHEST_LEGACY"로만 기록 (선택)
- `git_commit`: Git 커밋 SHA (NULL 가능)
- `file_path`: 파일 경로 (NULL 가능)
- `artifacts_path`: 아티팩트 경로 (NULL 가능)
- `status`: 상태 (NULL 가능)
- `created_at`: 생성 시간
- `extra_json`: 추가 메타데이터 (JSON)
  - `section_id`: 단면 식별자 (문자열, 선택)
  - `method_tag`: 방법 태그 (문자열, 선택)

**원칙:**
- `layer`는 필수 필드이며, artifact가 어느 레이어에 속하는지 명확히 인덱싱합니다
- `artifact_type`과 `layer`는 교차 분류됩니다 (예: report는 L4 또는 L5일 수 있음)
- `related_measurement_key`는 가슴 계열 측정의 경우 반드시 UNDERBUST/BUST를 구분합니다
- `extra_json`에 `section_id`와 `method_tag`를 저장합니다 (컬럼 추가 금지)

## 가슴 계열 측정 인덱싱 규칙

### 표준 키
- **UNDERBUST**: 가슴 아래 둘레 (표준)
- **BUST**: 가슴 둘레 (표준)

### 레거시 처리
- **CHEST**: Deprecated (표준 키에서 제외)
  - 기존 데이터가 있다면 `related_measurement_key`에 "CHEST_LEGACY"로만 기록 (선택)

### DB 인덱싱
- `artifacts.related_measurement_key`에는 반드시 "UNDERBUST" 또는 "BUST"로 구분 기록
- 내부 표준 키: `UNDERBUST_CIRC_M` / `BUST_CIRC_M`
- DB에는 "UNDERBUST" 또는 "BUST"로만 기록

## section_id / method_tag 저장 규칙

### 저장 위치
- `artifacts.extra_json`에 JSON 객체로 저장:
  ```json
  {
    "section_id": "<string>",
    "method_tag": "<string>"
  }
  ```

### 규칙
- `section_id`와 `method_tag`가 존재하는 artifact만 `extra_json`에 저장
- 존재하지 않으면 생략 가능 (NULL 또는 빈 JSON 허용)
- 향후 집계용이지만, 이번 작업은 "저장 경로를 정해두는 것"만 수행

## 사용 도구

- `tools/db_upsert.py`: DB 쓰기 단일 진입점
  - artifacts run 폴더 또는 리포트 md 입력 받아 upsert
  - Antigravity가 매 실험 종료 후 실행
  - `artifacts` 테이블에도 자동 upsert (레이어 인덱싱 포함)

## 정책 버전과 실험 ID 분리

- **정책 버전**: 정책의 버전 관리 (policies 테이블)
- **실험 ID**: 개별 실험 실행 식별자 (experiments 테이블)
- 하나의 정책 버전에 여러 실험이 연결될 수 있음

## JSON 필드 사용 이유

- `experiments.extra_json`: 실험별 유연한 메타데이터 확장
- `reports.metrics_json`: 구조화된 메트릭 데이터 저장 (레거시)
- `artifacts.extra_json`: 레이어별 추가 메타데이터 (section_id, method_tag 등)
- 스키마 변경 없이 메타데이터 확장 가능

## 레이어 인덱싱 예시

### Policy 문서 (L1 Semantic)
- `artifact_type`: "policy"
- `layer`: "L1"
- `file_path`: "docs/policies/measurements/SEMANTIC_DEFINITION_CHEST_VNEXT.md"

### Contract 문서 (L2 Contract)
- `artifact_type`: "spec"
- `layer`: "L2"
- `file_path`: "docs/policies/measurements/CONTRACT_INTERFACE_CHEST_V0.md"

### Geometric 구현 (L3 Geometric)
- `artifact_type`: "spec"
- `layer`: "L3"
- `file_path`: "docs/policies/measurements/GEOMETRIC_DESIGN_CHEST_V0.md"

### Validation 결과 (L4 Validation)
- `artifact_type`: "report"
- `layer`: "L4"
- `artifacts_path`: "verification/reports/chest_v0/validation_results.csv"
- `extra_json`: `{"section_id": "plane_y_0.85", "method_tag": "median_slice"}`

### Judgment 문서 (L5 Judgment)
- `artifact_type`: "judgment_memo"
- `layer`: "L5"
- `file_path`: "docs/judgments/measurements/CHEST_V0_JUDGMENT_20260121_R1.md"
