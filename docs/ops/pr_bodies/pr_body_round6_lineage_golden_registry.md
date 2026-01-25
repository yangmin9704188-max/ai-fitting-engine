# ops: add lineage manifest and golden registry on postprocess (round6)

## 목적
postprocess_round.py 마감 단계에서 lineage manifest와 golden_registry.json을 자동 생성/갱신합니다.
이는 "재현성/추적성"을 위한 facts-only 기록입니다 (판정 금지).

## 구현 범위

### 1. tools/lineage.py (신규)
- LINEAGE.md 렌더링
- 기능:
  - Basic Info: current_run_dir, lane, round_id, round_num
  - Inputs: npz_path, source_path_abs, facts_summary.json
  - Code Fingerprints: git commit hashes (postprocess_round.py, summarize_facts_kpi.py, generator_script)
  - Timestamps: created_at, npz_mtime, facts_summary_mtime
  - Outputs: KPI.md, KPI_DIFF.md, report, registry paths (존재 여부 포함)
  - NPZ Metadata: schema_version, meta_unit (NPZ 메타에서 추출)

### 2. tools/golden_registry.py (신규)
- golden_registry.json upsert
- 기능:
  - npz_path 기준 upsert (있으면 갱신, 없으면 append)
  - NPZ 메타데이터 추출 (schema_version, meta_unit)
  - generator_script 및 commit hash 수집
  - SHA256 계산 (작은 파일만, <= 50MB)
  - Atomic write (임시파일 -> rename)

### 3. tools/postprocess_round.py 업데이트
- LINEAGE.md 생성 로직 추가
- golden_registry.json upsert 로직 추가
- round_num, round_id 추출 및 전달

### 4. 문서
- `docs/verification/lineage_manifest_contract_v0.md` (신규)
- `docs/verification/golden_registry_contract_v0.md` (신규)

## 변경 파일 목록

- `tools/lineage.py` (신규)
- `tools/golden_registry.py` (신규)
- `tools/postprocess_round.py` (업데이트: lineage/golden_registry 갱신 추가)
- `docs/verification/lineage_manifest_contract_v0.md` (신규)
- `docs/verification/golden_registry_contract_v0.md` (신규)
- `docs/verification/golden_registry.json` (신규)

## LINEAGE.md 샘플 (일부)

```markdown
# Lineage Manifest

**schema_version**: lineage@1

## Basic Info
- current_run_dir, lane, round_id, round_num

## Inputs
- npz_path, npz_path_abs, source_path_abs
- facts_summary.json

## Code Fingerprints
- tools/postprocess_round.py: <commit_hash>
- tools/summarize_facts_kpi.py: <commit_hash>
- generator_script: <path>
  - commit: <commit_hash>

## Timestamps
- created_at, npz_mtime, facts_summary_mtime

## Outputs
- KPI.md, KPI_DIFF.md, report, registry paths

## NPZ Metadata
- schema_version, meta_unit
```

## Golden Registry 스키마 요약

```json
{
  "schema_version": "golden_registry@1",
  "updated_at": "ISO timestamp",
  "entries": [
    {
      "npz_path": "relative path",
      "npz_path_abs": "absolute path",
      "npz_sha256": "hash (optional, <= 50MB)",
      "npz_mtime": "timestamp",
      "npz_size_bytes": "size",
      "schema_version": "from NPZ meta",
      "meta_unit": "from NPZ meta",
      "source_path_abs": "source file path",
      "generator_script": "script path",
      "generator_commit": "git commit hash",
      "notes": ""
    }
  ]
}
```

## Upsert 규칙

- **중복 방지 키**: `npz_path` 또는 `npz_path_abs`
- 같은 `npz_path`가 있으면 갱신(upsert), 없으면 append
- Atomic write (임시파일 -> rename)

## 금지사항 준수 확인
- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 runner/측정 로직 의미 변경 없음
- ✅ no PASS/FAIL 판정: facts-only 유지

## 스모크 테스트

### 실행 명령
```bash
py tools/postprocess_round.py \
  --current_run_dir verification/runs/facts/curated_v0/round20_20260125_164801
```

### 기대 결과
- ✅ LINEAGE.md 생성
- ✅ docs/verification/golden_registry.json 생성/갱신
- ✅ 해당 run이 사용한 npz가 기록됨
- ✅ postprocess는 0 exit로 종료

### 스모크 테스트 결과

```
Lane: curated_v0
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Prev: verification\runs\facts\curated_v0\round20_20260125_164801
Baseline: verification\runs\facts\curated_v0\round20_20260125_164801
Facts summary: verification\runs\facts\curated_v0\round20_20260125_164801\facts_summary.json
Generated: KPI.md
Generated: KPI_DIFF.md
Updated: reports/validation/round_registry.json (6 entries)
Updated: docs/verification/coverage_backlog.md (6 entries)
Updated: docs/verification/round_registry.json
Generated: LINEAGE.md
Updated: docs/verification/golden_registry.json (1 entries)

Postprocessing complete!
```

✅ 모든 기대 결과 확인:
- LINEAGE.md 생성 확인:
  - Basic Info, Inputs, Code Fingerprints, Timestamps, Outputs, NPZ Metadata 모두 포함
  - git commit hashes 수집 확인
  - generator_script 경로 및 commit 확인
- golden_registry.json 생성 확인:
  - 1개 entry 추가 확인
  - npz_path, npz_path_abs, npz_sha256, npz_mtime, npz_size_bytes 포함
  - schema_version, meta_unit, source_path_abs 포함
  - generator_script 포함
- postprocess 정상 종료 (exit code 0)

## 성능/안전

- SHA256은 작은 파일만 계산 (<= 50MB, 기본 OFF)
- 모든 파일 write는 atomic하게 구현 (임시파일 -> rename)
- 실패 시 예외로 죽지 말고 warnings 출력 후 계속:
  - git이 없는 환경: commit hash를 null로 처리
  - NPZ 파일이 없으면: golden_registry 업데이트 스킵
  - 파일 읽기 실패: 해당 필드만 N/A로 처리

## 참고

- 루트에 파일 추가하지 않음 (tools/ 및 docs/verification/ 안에서만 해결)
- LINEAGE.md는 각 run_dir에 생성 (라운드별 산출물)
- golden_registry.json은 전역 레지스트리 (모든 NPZ 파일 추적)
