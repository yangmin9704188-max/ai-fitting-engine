# validate-evidence 조사 결과

## 1. GitHub Workflow 확인

### 워크플로우 파일
- **경로**: `.github/workflows/evidence.yml`
- **워크플로우 이름**: `evidence-check`
- **Job 이름**: `validate-evidence`

### 실행 트리거
- `pull_request`: main 브랜치 대상
- `push`: main 브랜치 대상
- `workflow_dispatch`: 수동 실행

### 실제 실행 커맨드
```bash
python tools/validate_evidence.py --base "$BASE_SHA" --head "$HEAD_SHA"
```

### 실행 조건
- `IS_INFRA_ONLY != 'true'` (infra-only PR은 스킵)
- `HAS_EVIDENCE_RUNS == 'true'` (artifacts/**/runs/** 변경 감지 시)
- 변경 파일 패턴: `artifacts/[^/]+/[^/]+/runs/([^/]+)/manifest.json`

---

## 2. manifest.json 검사 스크립트

### 파일 경로
- `tools/validate_evidence.py`

### 핵심 검사 조건

#### manifest.json 필수 키 (9개)
- `schema_version` (값: "evidence.manifest.v1")
- `task`
- `policy_version`
- `run_id`
- `created_at_utc`
- `runner`
- `code`
- `data`
- `experiment`
- `baseline` (baseline.ref 필수, 비어있으면 안됨)

#### metrics.json 필수 키 (6개)
- `schema_version` (값: "evidence.metrics.v1")
- `task`
- `policy_version`
- `run_id`
- `metrics` (metrics.primary 필수)
- `regression` (regression.baseline_ref 필수, manifest의 baseline.ref와 일치해야 함)

#### 필수 파일
- `manifest.json`
- `metrics.json`
- `summary.md`

#### PASS/FAIL 규칙 (품질 게이트)
- Primary metric regression: `abs(delta) <= 0.3`, `abs(delta_pct) <= 5`
- Secondary metric fail_rate: `fail_rate <= 0.05`

---

## 3. Git 히스토리

### 최초 도입 커밋
- **커밋**: `b6d9bcdec1f0a84294431a28f095122caa4b7ab5`
- **날짜**: 2026-01-18
- **작성자**: Minyoung Yang <yangmin9704188@gmail.com>
- **메시지**: "evidence: add schema v1 docs and validation runner"
- **내용**:
  - `docs/evidence_schema_v1.md` 추가 (스키마 v1.0 명세)
  - `tools/validate_evidence.py` 추가 (스키마 검증)
  - `.github/workflows/evidence.yml` 업데이트
  - 샘플 run 추가: `artifacts/sample_task/v0/runs/sample_run_001/`
  - 검증 규칙: 누락 파일, 스키마 버전, baseline.ref, 회귀 임계값

### 최근 변경 커밋 (상위 5개)

1. **63eadb2** (2026-01-20)
   - "ops: stabilize evidence pipeline infra-only detection"
   - infra-only 감지 안정화

2. **9a89398** (2026-01-19)
   - "ci: include Makefile in infra-only allowlist"
   - Makefile을 infra-only 허용 목록에 추가

3. **b6d9bcd** (2026-01-18)
   - "evidence: add schema v1 docs and validation runner"
   - 최초 도입

4. **b1dc81d** (2026-01-17)
   - "ci(evidence): skip validation for infra-only PRs (path-based guard)"
   - infra-only PR 스킵 로직 추가

5. **aa63e6a** (2026-01-17)
   - "fix: compute PR changed files using merge-base triple-dot for infra-only detection"
   - infra-only 감지 개선

### 패턴 분석
- **도입 시기**: 2026-01-18 (약 4일 전)
- **주요 변경 내용**: 대부분 infra-only 감지 관련 수정 (완화 시도)
- **작성자**: 모두 동일 (Minyoung Yang)

---

## 4. 결론: 3단 분류

### 분류: **B - 유용하지만 필수는 아님 (완화/required 해제 후보)**

#### 근거

**B 분류 근거:**
1. **최근 도입** (2026-01-18)
   - 프로젝트 핵심 운영 장치라기보다는 최근 추가된 검증 도구
   - Git 히스토리상 약 4일 전 도입

2. **완화 시도 흔적**
   - 최근 커밋 대부분이 infra-only 감지 완화 관련
   - "skip validation for infra-only PRs" 등 완화 로직 추가
   - infra-only 허용 목록 확장 (Makefile 추가 등)

3. **품질 게이트 포함**
   - PASS/FAIL 규칙 포함 (delta, delta_pct, fail_rate 임계값)
   - 이는 "과도한 거버넌스"의 징후일 수 있음
   - 스키마 검증은 유용하지만, 품질 임계값은 완화 가능

4. **조건부 실행**
   - infra-only PR은 이미 스킵됨
   - artifacts/**/runs/** 변경 시에만 실행
   - 필수 검사라기보다는 선택적 검증

5. **스키마 검증은 유용**
   - manifest.json, metrics.json 구조 검증은 추적성에 도움
   - 하지만 필수 파일 검사는 완화 가능 (summary.md 등)

**A (현재 운영 필수)가 아닌 이유:**
- 최근 도입으로 핵심 운영 장치라 보기 어려움
- infra-only 스킵 로직이 이미 있어 필수성 낮음
- 품질 게이트가 포함되어 있어 과도한 거버넌스 가능성

**C (레거시/과도한 거버넌스)가 아닌 이유:**
- 스키마 검증 자체는 유용함 (추적성)
- 최근 도입으로 레거시는 아님
- 완화 시도가 있어 완전히 제거할 필요는 없음

#### 권장 조치
- **required 해제**: CI에서 required 체크 해제 고려
- **품질 게이트 완화**: PASS/FAIL 규칙을 warning으로 변경 또는 제거
- **선택적 검증**: 스키마 검증만 유지, 품질 임계값은 제거
- **문서화**: 검증 목적과 범위를 명확히 문서화

---

## 참고 파일

- `.github/workflows/evidence.yml` (197줄)
- `tools/validate_evidence.py` (273줄)
- `docs/evidence_schema_v1.md` (스키마 명세)

---

*조사 일시: 2026-01-22*
*조사 범위: 레포 파일 및 Git 히스토리만 (추측 없음)*
