---
run_id: "apose_normalization-2026-01-13-run-001"
policy_name: "A-Pose Normalization"
policy_version: "v1.1"
execution_date: "2026-01-13"
status: "completed"
artifacts_path: "runs/apose_normalization/2026-01-13_run_001"
---

# Run: A-Pose Normalization v1.1 — 2026-01-13_run_001

## 실행 목적
- Phase 2 Batch Fitting을 위한 초기 beta 파라미터 생성

## 입력 요약
- 입력 데이터:
  - 내부 SMPL-X 기반 데이터
- 처리 대상:
  - female beta initialization 전용

## 실행 결과 요약
- 생성된 산출물:
  - `init_betas_female.npy`
- 용도:
  - LBFGS 초기값으로 사용
  - Phase 2 – Batch Fitting 단계에서 활용

## 관련 코드
- `pipelines/step1_execute.py`
- 실행 스크립트:
  - `step1_data_prep.py`

## 비고
- 본 Run은 A-Pose Normalization v1.1을 전제로 수행됨
- 당시 실행 시점의 코드 상태는 정책 Freeze 기준과 동일한 커밋을 사용
- 상세한 개발 맥락은 2026-01-13 개발일지 참조
