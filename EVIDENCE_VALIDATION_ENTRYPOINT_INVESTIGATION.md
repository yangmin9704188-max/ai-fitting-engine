# Evidence Validation Entrypoint 조사 결과

## 1. 특정 문자열 검색 결과

### 문자열 1: "Guard: Skip if infra-only (double-check using env var)"

**검색 결과:** 없음 (정확한 문자열 매칭 실패)

**유사 문자열:**
- `.github/workflows/evidence.yml` 라인 171:
  ```yaml
  # Guard: Skip if infra-only (double-check using env var)
  echo "validate env IS_INFRA_ONLY=${IS_INFRA_ONLY}"
  ```

### 문자열 2: "validate env IS_INFRA_ONLY=false"

**검색 결과:**
- `.github/workflows/evidence.yml` 라인 172:
  ```yaml
  echo "validate env IS_INFRA_ONLY=${IS_INFRA_ONLY}"
  ```
- 동일 파일 라인 141 (다른 스텝):
  ```yaml
  echo "validate env IS_INFRA_ONLY=${IS_INFRA_ONLY}"
  ```

### 문자열 3: "[FAIL] manifest.json 파일이 없습니다: artifacts/shoulder_width/v1.2/regression/20260117_153136_PASS/manifest.json"

**검색 결과:**
- `tools/validate_observation.py` 라인 40:
  ```python
  print(f"[FAIL] manifest.json 파일이 없습니다: {manifest_path}")
  ```

**주변 코드 (라인 30-41):**
```python
# manifest.json 체크 (--require-manifest 옵션)
if require_manifest:
    artifacts = data.get("artifacts", {})
    run_dir = artifacts.get("run_dir", "")
    if not run_dir:
        print("[FAIL] artifacts.run_dir이 비어있습니다.")
        sys.exit(1)
    
    manifest_path = Path(run_dir) / "manifest.json"
    if not manifest_path.exists():
        print(f"[FAIL] manifest.json 파일이 없습니다: {manifest_path}")
        sys.exit(1)
```

---

## 2. .github/workflows 전체 스캔 결과

### validate_evidence.py를 호출하는 워크플로우

| 워크플로우 파일 | Job 이름 | Step 이름 | 실행 조건 | 커맨드 |
|----------------|----------|-----------|-----------|--------|
| `.github/workflows/evidence.yml` | `validate-evidence` | `Validate evidence runs (schema v1.0)` | `IS_INFRA_ONLY != 'true' && HAS_EVIDENCE_RUNS == 'true'` | `python tools/validate_evidence.py --base "$BASE_SHA" --head "$HEAD_SHA"` |

### validate_observation.py를 호출하는 워크플로우

| 워크플로우 파일 | Job 이름 | Step 이름 | 실행 조건 | 커맨드 |
|----------------|----------|-----------|-----------|--------|
| `.github/workflows/evidence.yml` | `validate-evidence` | `Validate observation & manifest (if present)` | `IS_INFRA_ONLY != 'true' && HAS_EVIDENCE_RUNS != 'true'` | `python tools/validate_observation.py --require-manifest` |

**중요:** 두 스텝은 상호 배타적 조건:
- `HAS_EVIDENCE_RUNS == 'true'` → `validate_evidence.py` 실행
- `HAS_EVIDENCE_RUNS != 'true'` → `validate_observation.py` 실행

---

## 3. 다른 validate/evidence 관련 스크립트 조사

### tools/validate_observation.py

**기능:**
- `logs/observation.md` 파일에서 YAML 블록 파싱
- `artifacts.run_dir` 필드에서 경로 추출
- 해당 경로의 `manifest.json` 존재 여부 검증

**regression 경로 처리:**
- **직접 enumerate하지 않음**
- `logs/observation.md`에 하드코딩된 경로를 그대로 사용
- 현재 `logs/observation.md` 내용:
  ```yaml
  artifacts:
    run_dir: artifacts/shoulder_width/v1.2/regression/20260117_153136_PASS
  ```

**문제점:**
- `observation.md`에 레거시 경로(`regression/`)가 하드코딩되어 있음
- `validate_observation.py`는 이 경로를 검증 대상으로 사용
- 경로가 변경되지 않았는지 확인하지 않음 (git diff 사용 안 함)

### tools/pack_evidence.py

**기능:**
- Evidence Package 생성 (manifest.json, metrics.json 등)
- regression 계산 포함
- **regression 폴더를 직접 스캔하지 않음**

### tools/validate_evidence.py

**기능:**
- base/head diff로 변경된 artifacts만 검증
- `runs` 디렉토리만 대상 (regression/ 제외)
- **regression 경로를 스캔하지 않음**

---

## 4. 최종 결론

### **B) 다른 workflow/스크립트가 실행되고 있다**

**근거:**

1. **실제 실행되는 스크립트:**
   - `tools/validate_observation.py` (우리가 수정하지 않은 파일)
   - `logs/observation.md`에 하드코딩된 경로 사용

2. **워크플로우 실행 조건:**
   - `HAS_EVIDENCE_RUNS != 'true'`일 때 `validate_observation.py` 실행
   - `HAS_EVIDENCE_RUNS == 'true'`일 때 `validate_evidence.py` 실행
   - 현재 PR은 `HAS_EVIDENCE_RUNS != 'true'`이므로 `validate_observation.py`가 실행됨

3. **문제의 원인:**
   - `logs/observation.md`에 레거시 경로가 하드코딩:
     ```yaml
     run_dir: artifacts/shoulder_width/v1.2/regression/20260117_153136_PASS
     ```
   - `validate_observation.py`는 이 경로의 `manifest.json` 존재 여부만 체크
   - 경로가 변경되었는지 확인하지 않음 (git diff 사용 안 함)
   - 레거시 경로에 manifest.json이 없으면 FAIL

4. **우리가 수정한 파일:**
   - `tools/validate_evidence.py` - 이 파일은 실행되지 않음 (조건 불만족)
   - `validate_observation.py`는 수정하지 않았음

---

## 요약

**실제 엔트리포인트:**
- `.github/workflows/evidence.yml` → `Validate observation & manifest (if present)` 스텝
- `tools/validate_observation.py --require-manifest`
- `logs/observation.md`에서 `artifacts.run_dir` 경로 읽기
- 해당 경로의 `manifest.json` 존재 여부 검증

**문제:**
- `logs/observation.md`에 레거시 경로(`artifacts/shoulder_width/v1.2/regression/20260117_153136_PASS`)가 하드코딩
- `validate_observation.py`는 이 경로를 변경 여부와 관계없이 검증
- 레거시 경로에 manifest.json이 없으면 FAIL

**해결 방향:**
- `validate_observation.py`를 수정하여:
  1. `run_dir` 경로가 이번 PR에서 변경되었는지 확인
  2. 변경되지 않은 레거시 경로는 검증 대상에서 제외
  3. 또는 `observation.md`의 `run_dir`를 업데이트하여 유효한 경로로 변경

---

*조사 일시: 2026-01-22*
*조사 범위: 레포 파일 및 워크플로우만 (추측 없음)*
