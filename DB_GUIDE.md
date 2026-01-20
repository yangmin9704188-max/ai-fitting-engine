# Database Guide

## 목적

데이터베이스는 상태/검색/집계용 메타데이터 저장소입니다.

**중요 원칙:**
- 문서 전문은 Git에 저장
- 메타데이터만 DB에 저장
- DB는 검색/집계를 위한 인덱스 역할

## 스키마

SQLite 기반 5개 테이블:

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
- `experiment_id`: 실험 ID (FK)
- `report_type`: 보고서 타입
- `result`: 결과 (PASS | FAIL | PARTIAL)
- `gate_failed`: 실패한 게이트
- `evaluated_policy_commit`: 평가된 정책 커밋
- `verification_tool_commit`: 검증 도구 커밋
- `artifacts_path`: 아티팩트 경로
- `dataset`: 데이터셋 정보
- `metrics_json`: 메트릭 데이터 (JSON)
- `created_at`: 생성 시간

**원칙:**
- `metrics_json`은 구조화된 메트릭 데이터 저장용
- 문서 전문은 Git에 저장, 메타데이터만 DB

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

## 사용 도구

- `tools/db_upsert.py`: DB 쓰기 단일 진입점
  - artifacts run 폴더 또는 리포트 md 입력 받아 upsert
  - Antigravity가 매 실험 종료 후 실행

## 정책 버전과 실험 ID 분리

- **정책 버전**: 정책의 버전 관리 (policies 테이블)
- **실험 ID**: 개별 실험 실행 식별자 (experiments 테이블)
- 하나의 정책 버전에 여러 실험이 연결될 수 있음

## JSON 필드 사용 이유

- `experiments.extra_json`: 실험별 유연한 메타데이터 확장
- `reports.metrics_json`: 구조화된 메트릭 데이터 저장
- 스키마 변경 없이 메타데이터 확장 가능
