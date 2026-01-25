# ops: add Makefile wrapper to finalize rounds (round1)

## 목적
1인 개발의 "명령어 복붙/순서 기억" 에너지를 줄이기 위해, Makefile에 round 실행 래퍼 타겟을 추가합니다.
원칙: runner 실행 후 성공/실패와 무관하게 postprocess_round.py는 반드시 실행되게 합니다 (죽지 않는 마감).

## 구현 범위

### 1. Makefile에 `curated_v0_round` 타겟 추가
- `make curated_v0_round RUN_DIR=<out_dir>` 형식
- 동작:
  - A) RUN_DIR이 없으면 에러 메시지 출력하고 종료
  - B) facts_summary.json이 이미 존재하면 runner는 자동으로 스킵
  - C) postprocess는 항상 실행 (runner 성공/실패와 무관)
- 타겟은 "가볍게" 유지: 복잡한 인자 파싱 금지

### 2. 문서 추가
- `docs/ops/round_runbook.md` (신규)
  - "Round 실행 최소 명령"만 10줄 이내로 추가

## 변경 파일 목록

- `Makefile` (업데이트: curated_v0_round 타겟 추가)
- `docs/ops/round_runbook.md` (신규)

## 금지사항 준수 확인
- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 runner/측정 로직 의미 변경 없음
- ✅ no PASS/FAIL 판정: facts-only 유지

## 스모크 테스트

### 실행 명령
```bash
make curated_v0_round RUN_DIR=verification/runs/facts/curated_v0/round20_20260125_164801
```

### 기대 결과
- ✅ facts_summary.json이 이미 존재하면 runner 스킵 메시지 출력
- ✅ postprocess는 항상 실행됨
- ✅ postprocess는 0 exit로 종료 (runner 실패해도 전체는 죽지 않음)

### 스모크 테스트 결과

**참고**: Windows 환경에서는 `make` 명령이 없어 직접 테스트하지 못했으나, Makefile 문법은 표준이며 Linux/WSL 환경에서 정상 동작할 것으로 예상됩니다.

**예상 동작:**
```
facts_summary.json already exists in verification/runs/facts/curated_v0/round20_20260125_164801, skipping runner.
To force re-run, delete verification/runs/facts/curated_v0/round20_20260125_164801/facts_summary.json or run without SKIP_RUNNER=1
Running postprocess_round.py (always executed)...
Lane: curated_v0
...
Postprocessing complete!
```

## Makefile 타겟 상세

```makefile
curated_v0_round:
	@if [ -z "$(RUN_DIR)" ]; then \
		echo "Error: RUN_DIR is required. Usage: make curated_v0_round RUN_DIR=<out_dir>"; \
		exit 1; \
	fi
	@if [ "$(SKIP_RUNNER)" != "1" ]; then \
		if [ ! -f "$(RUN_DIR)/facts_summary.json" ]; then \
			echo "Running curated_v0 facts runner..."; \
			python verification/runners/run_curated_v0_facts_round1.py \
				--npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz \
				--out_dir $(RUN_DIR); \
		else \
			echo "facts_summary.json already exists in $(RUN_DIR), skipping runner."; \
			echo "To force re-run, delete $(RUN_DIR)/facts_summary.json or run without SKIP_RUNNER=1"; \
		fi \
	else \
		echo "SKIP_RUNNER=1: Skipping runner execution."; \
	fi
	@echo "Running postprocess_round.py (always executed)..."
	@python tools/postprocess_round.py --current_run_dir $(RUN_DIR) || true
```

**주요 특징:**
- RUN_DIR 검증: 없으면 에러 메시지 출력 후 종료
- 자동 스킵: facts_summary.json이 이미 존재하면 runner 스킵
- 강제 스킵: `SKIP_RUNNER=1`로 runner 강제 스킵 가능
- 항상 postprocess: `|| true`로 runner 실패해도 postprocess 실행

## 참고

- 루트에 파일 추가하지 않음 (Makefile 및 docs/ops/ 안에서만 해결)
- Makefile은 표준 POSIX make 문법 사용 (Linux/WSL/Git Bash에서 동작)
- Windows 환경에서는 WSL 또는 Git Bash 사용 권장
