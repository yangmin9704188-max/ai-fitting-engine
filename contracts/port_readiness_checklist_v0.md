# Port Readiness Checklist v0

**Status**: CANONICAL
**Created**: 2026-01-29
**Purpose**: fitting_lab → main 포트 안전성 및 저추론(low-inference) 보장을 위한 체크리스트

---

## 1. 범위 및 비목표 (Scope & Non-goals)

### 1.1 범위
- fitting_lab에서 main 레포로 **allowlist 파일만** copy-only 포트
- release snapshot 생성 (evidence 보존)
- 문서 기반 검증 (facts-only)

### 1.2 비목표 (금지 사항)
- 코드 리팩토링
- 폴더 이동 (`git mv` 금지)
- 파일 삭제 (`git rm` 금지)
- allowlist 외 파일 포트
- Canon 규칙 재정의 (interface_ledger_v0.md가 SSoT)

---

## 2. Port Allowlist (허용 파일 목록)

**정확히 3개 파일만 포트 허용:**

| # | fitting_lab 소스 경로 | main 목적지 경로 |
|---|----------------------|------------------|
| 1 | `labs/runners/run_fitting_v0_facts.py` | `modules/fitting/runners/run_fitting_v0_facts.py` |
| 2 | `labs/specs/fitting_manifest.schema.json` | `modules/fitting/specs/fitting_manifest.schema.json` |
| 3 | `contracts/fitting_interface_v0.md` | `docs/contract/fitting_interface_v0.md` |

### 2.1 Allowlist 확장 금지
- 위 3개 파일 외 추가 포트 시 별도 승인 필요
- 에이전트는 allowlist 임의 확장 금지

---

## 3. Release Snapshot Evidence 절차

### 3.1 Snapshot 경로 형식
```
releases/<lane>_<YYYYMMDD>_<HHMMSS>/
```
예시: `releases/fitting_v0_20260129_143000/`

### 3.2 Snapshot 내용물 (copy-only)
- `run_fitting_v0_facts.py`
- `fitting_manifest.schema.json`
- `fitting_interface_v0.md`

### 3.3 생성 도구 (fitting_lab 측)
```powershell
# fitting_lab 디렉토리에서 실행
powershell -ExecutionPolicy Bypass -File tools/make_release_snapshot.ps1
```

### 3.4 Snapshot 정책
- 포트 전 반드시 snapshot 생성
- snapshot은 수정 금지 (immutable evidence)
- main 레포에 commit 금지 (fitting_lab 로컬 보관)

---

## 4. Pre-Port Checks (포트 전 검증)

### 4.1 Ledger Compliance Check

| Canon | 검증 항목 | 참조 문서 |
|-------|----------|----------|
| Path=C | REL 경로 base가 `manifest_dir` 기준인지 확인 | interface_ledger_v0.md §1 |
| Name=B | fitting 출력 파일명이 `fitting_facts_summary.json`인지 확인 | interface_ledger_v0.md §2 |
| Version=C | provenance에 4 version keys 존재 확인 | interface_ledger_v0.md §3 |
| NaN→null | NaN/Inf가 null로 직렬화되는지 확인 | interface_ledger_v0.md §5 |
| Warnings | canonical format `{count, sample_messages, truncated}` 사용 확인 | interface_ledger_v0.md §6 |
| Round | 신규 round는 folder-split 형식 사용 | interface_ledger_v0.md §4 |

### 4.2 File Existence Checks (fitting_lab 측)

포트 전 다음 파일이 fitting_lab에 존재해야 함:

```
[ ] labs/runners/run_fitting_v0_facts.py
[ ] labs/specs/fitting_manifest.schema.json
[ ] contracts/fitting_interface_v0.md
```

### 4.3 Schema Validation Checks

`fitting_manifest.schema.json`의 provenance에 다음 키가 정의되어 있는지 확인:

```
[ ] schema_version
[ ] code_fingerprint
[ ] snapshot_version (또는 description에 UNSPECIFIED 언급)
[ ] semantic_version (또는 description에 UNSPECIFIED 언급)
[ ] geometry_impl_version (또는 description에 UNSPECIFIED 언급)
[ ] dataset_version (또는 description에 UNSPECIFIED 언급)
[ ] path_base (enum: manifest_dir, run_dir)
```

**참고**: 런타임 강제는 불필요. 스키마에 정의 존재만 확인.

---

## 5. Port Execution Checklist (포트 실행)

### 5.1 단계별 실행

```
[ ] Step 1: fitting_lab에서 release snapshot 생성
    → tools/make_release_snapshot.ps1 실행

[ ] Step 2: main 레포로 파일 복사 (copy, not move)
    → labs/runners/run_fitting_v0_facts.py
      → modules/fitting/runners/run_fitting_v0_facts.py
    → labs/specs/fitting_manifest.schema.json
      → modules/fitting/specs/fitting_manifest.schema.json
    → contracts/fitting_interface_v0.md
      → docs/contract/fitting_interface_v0.md

[ ] Step 3: main 레포에서 경로 존재 확인
    ls modules/fitting/runners/run_fitting_v0_facts.py
    ls modules/fitting/specs/fitting_manifest.schema.json
    ls docs/contract/fitting_interface_v0.md

[ ] Step 4: Port Event 기록
    → contracts/port_event_note_template_v0.md 템플릿 사용
    → 또는 PR description에 기록
```

### 5.2 Git 작업

```bash
# main 레포에서
git checkout -b port/fitting-v0-<milestone>
git add modules/fitting/runners/run_fitting_v0_facts.py
git add modules/fitting/specs/fitting_manifest.schema.json
git add docs/contract/fitting_interface_v0.md
git commit -m "port: fitting v0 files from fitting_lab (<milestone>)"
git push -u origin port/fitting-v0-<milestone>
# PR 생성 후 CI green 확인 → merge
```

---

## 6. Post-Port Verification (포트 후 검증)

### 6.1 Smoke Run (해당 시)

fitting_interface_v0.md에 문서화된 smoke test 명령어 참조:

```powershell
# main 레포 또는 fitting_lab에서 실행 (경로 조정 필요)
py modules/fitting/runners/run_fitting_v0_facts.py \
  --manifest <manifest_path> \
  --out_dir <output_dir>
```

**참고**: 실제 명령어는 fitting_interface_v0.md "Smoke Test" 섹션 참조.

### 6.2 Inspect Script (해당 시)

fitting_lab에 inspect 도구가 있는 경우:

```powershell
# fitting_lab 디렉토리에서
powershell -ExecutionPolicy Bypass -File tools/inspect_run.ps1 -RunDir <output_dir>
```

**관측 사항**: inspect_run.ps1은 `facts_summary.json`을 참조하나, canonical 출력 파일명은 `fitting_facts_summary.json`임. 도구 업데이트 여부는 별도 판단.

### 6.3 Always-Emit Files 확인

포트된 runner 실행 후 다음 파일이 생성되어야 함 (값이 null이어도 파일 존재 필수):

```
[ ] <out_dir>/fitting_summary.json
[ ] <out_dir>/fitting_facts_summary.json
```

---

## 7. Anti-Footgun Rules (추론/드리프트 방지)

### 7.1 Canonical Ledger 자동 수정 금지

```
❌ 에이전트가 contracts/interface_ledger_v0.md 직접 수정
✅ 에이전트는 artifacts/interface_ledger_rows.jsonl에 후보 row만 출력 (optional)
```

### 7.2 Legacy 문서 처리

- Legacy 문서는 **stamp-only** 편집만 허용
- 내용 재작성 금지

### 7.3 Stamp 금지 대상 (Denylist)

다음 경로에는 LEGACY 스탬프를 붙이지 않음:

```
contracts/**
modules/**
specs/**
```

이 경로들은 활성 코드/스키마이므로 legacy 처리 대상이 아님.

### 7.4 Allowlist 외 파일 포트 금지

- Section 2의 3개 파일 외 포트 시도 시 명시적 승인 필요
- 에이전트는 임의로 allowlist 확장 금지

---

## 8. Port Budget (포트 횟수 제한)

### 8.1 정책

**정책: 확인 필요 (to be confirmed)**

프로젝트에서 명시적으로 "최대 N회 포트" 정책이 문서화된 경우 여기에 기록.

예시 (확정 시):
```
- Alpha port: 1회
- Beta port: 1회
- Final port: 1회
- 총 최대 3회
```

### 8.2 포트 이력

| # | 날짜 | Milestone | 파일 | 비고 |
|---|------|-----------|------|------|
| 1 | (기록) | (기록) | (기록) | (기록) |

---

## Appendix A: Canon 참조 요약

| Canon | 정의 | SSoT |
|-------|------|------|
| Path=C | REL base = manifest_dir | interface_ledger_v0.md §1 |
| Name=B | fitting output = fitting_facts_summary.json | interface_ledger_v0.md §2 |
| Version=C | 4 keys always; unknown=UNSPECIFIED | interface_ledger_v0.md §3 |
| Round | folder-split per lane/milestone | interface_ledger_v0.md §4 |
| NaN→null | NaN/Inf serialize as null | interface_ledger_v0.md §5 |
| Warnings | canonical format {count, sample_messages, truncated} | interface_ledger_v0.md §6 |

---

## Appendix B: 관련 문서 링크

- [Interface Ledger v0](./interface_ledger_v0.md) — cross-module SSoT
- [Fitting Interface v0](../docs/contract/fitting_interface_v0.md) — fitting contract
- [GUARDRAILS](../docs/ops/GUARDRAILS.md) — import boundary rules
- [Port Event Note Template](./port_event_note_template_v0.md) — port 기록 템플릿
