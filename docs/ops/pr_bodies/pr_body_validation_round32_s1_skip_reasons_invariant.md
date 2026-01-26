# PR: Round32 - S1 Skip Reasons Invariant

## 목적

Round31에서 `skip_reasons.jsonl`에 `records=195`, `has_mesh_path_true=0`이 관측되었습니다. 이는 proxy 5개 케이스가 로깅 루프에서 누락되었음을 의미합니다.

이번 라운드는 **"케이스당 1레코드 로깅 불변식"**을 복구하여 `records=200`, `has_mesh_path_true=5`를 보장합니다.

## 변경 사항

### 1. `verification/runners/run_geo_v0_s1_facts.py`

#### 케이스당 1레코드 로깅 보장
- `process_case` 함수를 `try/finally`로 감싸서 모든 케이스에 대해 로깅 보장
- 성공 케이스도 로깅 추가 (stage="measure", reason="success")
- 예상치 못한 예외 발생 시에도 로깅 보장

#### has_mesh_path 판정 단일화
- 기존: `has_mesh_path = mesh_path is not None`
- 변경: `has_mesh_path = (mesh_path is not None) and (str(mesh_path).strip() != "")`
- 빈 문자열도 `False`로 처리

#### 불변식 체크 및 자동 채우기
- `main` 함수에 불변식 체크 추가:
  - `manifest_cases == 200`
  - `jsonl_records == 200`
  - `has_mesh_path_true == 5` (proxy 기준)
- 누락된 케이스 자동 채우기:
  - `stage="invariant_fill"`
  - `reason="missing_log_record"`

### 2. `docs/ops/INDEX.md`
- Round32 엔트리 추가

### 3. `reports/validation/INDEX.md`
- Round32 섹션 추가

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round32_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## DoD Self-check (facts-only)

### 1. Records=200 확인
```bash
wc -l verification/runs/facts/geo_v0_s1/round32_*/artifacts/skip_reasons.jsonl
# 또는
cat verification/runs/facts/geo_v0_s1/round32_*/artifacts/skip_reasons.jsonl | wc -l
```

**예상 결과**: `200`

### 2. has_mesh_path_true=5 확인
```bash
grep -c '"has_mesh_path":true' verification/runs/facts/geo_v0_s1/round32_*/artifacts/skip_reasons.jsonl
```

**예상 결과**: `5`

### 3. Proxy 5개 레코드 샘플
```bash
grep '"has_mesh_path":true' verification/runs/facts/geo_v0_s1/round32_*/artifacts/skip_reasons.jsonl | head -5
```

**예상 필드**:
- `case_id`
- `has_mesh_path: true`
- `mesh_path` (non-null)
- `attempted_load` (true/false)
- `stage` (precheck/load_mesh/measure/invariant_fill)
- `reason` (success/load_failed/missing_log_record 등)
- `exception_1line` (실패 시) 또는 `loaded_verts`/`loaded_faces` (성공 시)

### 4. KPI/KPI_DIFF/LINEAGE 생성 확인
```bash
ls -la verification/runs/facts/geo_v0_s1/round32_*/KPI.md
ls -la verification/runs/facts/geo_v0_s1/round32_*/KPI_DIFF.md
ls -la verification/runs/facts/geo_v0_s1/round32_*/lineage/manifest.json
```

**예상 결과**: 모든 파일 존재

## 준수 사항

- ✅ PASS/FAIL 판정 금지 (facts-only)
- ✅ 측정 알고리즘 정답 튜닝 금지
- ✅ 대규모 리팩터링/폴더 이동/삭제(git rm) 금지
- ✅ verification/runs/** 커밋 금지
- ✅ 라운드 완료는 postprocess 마감까지
