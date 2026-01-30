**Status**: CANONICAL (SSoT)
**Edits**: Allowed only via version bump (v0 → v1) and explicit review.
“Canonical 문서(contracts/)는 자동 수정 금지. 에이전트는 후보(row)만 artifacts/에 출력한다.”

“레거시 문서는 스탬프 외 수정 금지. 규칙 변경은 새 버전(contract-lock-v1)에서만.”

# Interface Ledger v0 (Cross-Module Canon)

**Status**: CANONICAL
**Created**: 2026-01-29
**Purpose**: body/garment/fitting 모듈 간 artifact interface 단일 정본

---

## 1. Path Policy (C)

### 1.1 허용 경로 형식
- **ABS 경로**: 허용
- **REL 경로**: 허용

### 1.2 Canonical REL Base
- **정본 기준**: `manifest_dir` (manifest 파일이 위치한 디렉토리)
- **Legacy 허용**: `run_dir` 기준 REL 해석은 provenance에 `path_base` 명시 시 허용

### 1.3 Provenance 기록 규칙
REL 경로 사용 시 provenance에 반드시 포함:
```json
{
  "path_base": "manifest_dir",
  "manifest_path": "/absolute/path/to/manifest.json"
}
```

---

## 2. Naming Policy (B)

### 2.1 파일명 규칙

| Module | 입력 파일명 | 출력 파일명 |
|--------|------------|------------|
| body | N/A (manifest, mesh 소비) | `facts_summary.json` |
| fitting | body의 `facts_summary.json` (경로로 참조) | `fitting_facts_summary.json` |
| garment | (TBD) | (TBD) |

### 2.2 충돌 방지 규칙
- fitting 모듈 출력 파일명은 반드시 `fitting_facts_summary.json`
- body 모듈 출력 `facts_summary.json`과 동일 이름 사용 금지

---

## 3. Version Policy (C) — 4 Keys Always

### 3.1 필수 Version Keys
모든 cross-module artifact의 provenance에 항상 4개 키 존재:

| Key | 설명 | Unknown 시 값 |
|-----|------|---------------|
| `snapshot_version` | 시점 스냅샷 식별자 | `"UNSPECIFIED"` |
| `semantic_version` | 시맨틱 버전 문자열 | `"UNSPECIFIED"` |
| `geometry_impl_version` | geometry 구현 버전 | `"UNSPECIFIED"` |
| `dataset_version` | 데이터셋 버전 | `"UNSPECIFIED"` |

### 3.2 Unknown 처리 규칙
- 값이 unknown일 경우: `"UNSPECIFIED"` 문자열로 설정
- warning 코드 `VERSION_KEY_UNSPECIFIED` 기록 필수

### 3.3 예시
```json
{
  "provenance": {
    "schema_version": "fitting_manifest.v0",
    "snapshot_version": "UNSPECIFIED",
    "semantic_version": "UNSPECIFIED",
    "geometry_impl_version": "geo_v0_s1",
    "dataset_version": "round71",
    "code_fingerprint": "abc123"
  }
}
```

---

## 4. Round Policy (모듈별 + Milestone별 리셋)

### 4.1 Lane 형식
- `<module>/<lane_id>` (예: `body/geo_v0_s1`, `fitting/fitting_v0_facts`)

### 4.2 Milestone 형식
- `M<NN>_<short_tag>` (예: `M01_baseline`, `M02_torso_recovery`)
- tag는 자유, 형식(`M<NN>_`)은 고정

### 4.3 Round ID 형식
- `<lane_slug>__<milestone_id>__r<NN>`
- 예: `geo_v0_s1__M01_baseline__r01`

### 4.4 Round 문서 경로 (신규)
```
docs/ops/rounds/<lane_slug>/<milestone_id>/round_<NN>.md
```
예: `docs/ops/rounds/geo_v0_s1/M01_baseline/round_01.md`

### 4.5 Legacy Round 처리
- 기존 `docs/ops/rounds/round40.md` ~ `round71.md`는 LEGACY NAMING
- 내용 재작성 없이 헤더 최상단 LEGACY 스탬프만 추가
- 히스토리 보존 목적

---

## 5. NaN/Inf Serialization Policy

### 5.1 JSON 직렬화 규칙

| 내부 값 | JSON 출력 | Warning 코드 |
|--------|----------|-------------|
| NaN | `null` | (없음, 정상) |
| Inf | `null` | `INF_SERIALIZED_AS_NULL` |
| -Inf | `null` | `NEG_INF_SERIALIZED_AS_NULL` |

### 5.2 Schema 호환성
- `"type": "number"` 필드는 `["number", "null"]`로 확장
- 측정값 필드에 null 허용 필수

---

## 6. Warnings Format Policy

### 6.1 Canonical Format (cross-module 출력용)
```json
{
  "warnings": {
    "<CODE>": {
      "count": 5,
      "sample_messages": ["msg1", "msg2", "msg3", "msg4", "msg5"],
      "truncated": true
    }
  }
}
```

### 6.2 규칙
- `sample_messages`: 최대 5개
- `truncated`: 5개 초과 시 `true`
- Cross-module artifact는 canonical format 사용 필수

### 6.3 Simple Format (내부/run artifact용)
```json
{
  "warnings": {
    "<CODE>": ["msg1", "msg2", ...]
  }
}
```
- 내부 사용 시에만 허용

---

## 7. Module × Artifact Summary

| Module | Input Artifact | Output Artifact | Output Schema |
|--------|----------------|-----------------|---------------|
| body | s1_manifest.json, *.obj | facts_summary.json | facts_summary.v0 |
| fitting | fitting_manifest.json, facts_summary.json | fitting_facts_summary.json | fitting_facts_summary.v0 |
| garment | (TBD) | (TBD) | (TBD) |

---

## Appendix: Legacy Stamp Format

문서 최상단 line 1에 사용:> ⚠️ STATUS: LEGACY NAMING
> New rounds use folder-split format: docs/ops/rounds/<lane_slug>/<milestone_id>/round_<NN>.md
> This file preserved for history.
---


