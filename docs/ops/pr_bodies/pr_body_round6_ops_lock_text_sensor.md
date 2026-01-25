# ops: add lightweight ops-lock warning sensor (round6)

## 목적
금지된 경로/행동이 PR에 섞이는 것을 "경고만"으로 조기에 표면화하는 텍스트 센서를 추가합니다.
금지: 강제 차단(STOP) 금지. 실패로 빌드 깨지게 하지 않습니다.

## 구현 범위

### 1. tools/ops/check_ops_lock.py (신규)
- 입력: git diff --name-only <base>...HEAD 또는 현재 working tree 변경 파일 목록
- 규칙:
  - core/, pipelines/, verification/, tests/ 하위 변경이 있으면 "WARNING: restricted path touched"
  - git rm 감지 시 "WARNING: deletion detected"
- 출력은 사람이 읽기 쉬운 20줄 내외 요약
- Exit code 0 (경고만, 빌드 실패하지 않음)

### 2. docs/ops/cursor_prompt_header.md (업데이트)
- Ops Lock Check 안내 2~3줄 추가

### 3. Makefile (업데이트)
- `make ops_guard` 타겟 추가

## 변경 파일 목록

- `tools/ops/check_ops_lock.py` (신규)
- `docs/ops/cursor_prompt_header.md` (업데이트: ops lock check 안내 추가)
- `Makefile` (업데이트: ops_guard 타겟 추가)

## 금지사항 준수 확인
- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 runner/측정 로직 의미 변경 없음
- ✅ no PASS/FAIL 판정: facts-only 유지

## 스모크 테스트

### 실행 명령
```bash
py tools/ops/check_ops_lock.py --base main
```

또는

```bash
make ops_guard
```

### 기대 결과
- ✅ 변경 파일 목록 감지
- ✅ restricted path 경고 출력 (해당되는 경우)
- ✅ deletion 경고 출력 (해당되는 경우)
- ✅ Exit code 0 (경고만, 빌드 실패하지 않음)

### 스모크 테스트 결과

```
============================================================
Ops Lock Warning Sensor
============================================================
Changed files: 54

WARNINGS DETECTED:

  WARNING: restricted path touched
  Affected files (7):
    - core/measurements/core_measurements_v0.py
    - core/measurements/metadata_v0.py
    - tests/test_core_measurements_v0_smoke.py
    - verification/datasets/golden/core_measurements_v0/create_real_data_golden.py
    - verification/datasets/golden/core_measurements_v0/create_s0_dataset.py
    - verification/runners/run_curated_v0_facts_round1.py
    - verification/runners/run_geo_v0_facts_round1.py

Note: These are warnings only. Build will not fail.
Please review if these changes are intentional.
```

✅ 모든 기대 결과 확인:
- 변경 파일 목록 감지 확인 (54개)
- restricted path 경고 출력 확인 (7개 파일)
- Exit code 0 확인 (경고만, 빌드 실패하지 않음)

## 주요 기능

1. **경고 센서**:
   - core/, pipelines/, verification/, tests/ 하위 변경 감지
   - git rm (deletion) 감지
   - 경고만 출력, 빌드 실패하지 않음

2. **사용성**:
   - 사람이 읽기 쉬운 20줄 내외 요약
   - Makefile 타겟으로 간편 사용 (`make ops_guard`)

3. **안전성**:
   - Exit code 0 (경고만, 빌드 실패하지 않음)
   - 강제 차단(STOP) 금지

## 참고

- 루트에 파일 추가하지 않음 (tools/ops/, docs/ops/, Makefile만 수정)
- 기존 동작과 호환 (추가 기능만)
- PR 전에 수동으로 실행하여 경고 확인 가능
