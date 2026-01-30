# CONSISTENCY_CHECK.md (Facts-Only)

**생성일**: 2026-01-29
**작업자**: Contract/Interface Editor
**상태**: 적용 완료

---

## 검증 항목 체크리스트

### 1. Path Base 정의 (REL 기준 manifest_dir)

| 검증 항목 | 대상 파일 | 상태 | 비고 |
|----------|----------|------|------|
| `manifest_dir`가 canonical REL base로 명시됨 | `contracts/interface_ledger_v0.md` Section 1.2 | ✅ 적용됨 | "Canonical REL Base: manifest_dir" |
| `path_base` enum 정의 (manifest_dir, run_dir) | `fitting_manifest.schema.json` provenance | ✅ 적용됨 | enum: ["manifest_dir", "run_dir"] 추가 |
| Path policy 섹션 존재 | `fitting_interface_v0.md` | ✅ 적용됨 | "## Path Policy (C)" 섹션 추가 |
| Legacy run_dir 허용 조건 명시 | `interface_ledger_v0.md` Section 1.2 | ✅ 적용됨 | "provenance에 path_base 명시 시 허용" |

---

### 2. Fitting 출력 파일명 충돌 제거

| 검증 항목 | 대상 파일 | 상태 | 비고 |
|----------|----------|------|------|
| fitting 출력 파일명 = `fitting_facts_summary.json` | `interface_ledger_v0.md` Section 2.1 | ✅ 적용됨 | 테이블에 명시 |
| expected_files 수정 | `fitting_interface_v0.md` | ✅ 적용됨 | `facts_summary` → `fitting_facts_summary` |
| Output Files 섹션 제목 수정 | `fitting_interface_v0.md` | ✅ 적용됨 | `### facts_summary.json` → `### fitting_facts_summary.json` |
| Smoke test 기대 파일명 수정 | `fitting_interface_v0.md` | ✅ 적용됨 | 2곳 모두 수정 |
| body 입력 `facts_summary.json` 언급 유지 | `fitting_interface_v0.md` | ✅ 유지됨 | 변경 없음 (혼동 방지) |

---

### 3. 4 Version Keys 존재 (UNSPECIFIED + VERSION_KEY_UNSPECIFIED)

| 검증 항목 | 대상 파일 | 상태 | 비고 |
|----------|----------|------|------|
| 4키 목록 정의 | `interface_ledger_v0.md` Section 3.1 | ✅ 적용됨 | snapshot_version, semantic_version, geometry_impl_version, dataset_version |
| Unknown 시 `"UNSPECIFIED"` 명시 | `interface_ledger_v0.md` Section 3.2 | ✅ 적용됨 | "Unknown 처리 규칙" |
| `VERSION_KEY_UNSPECIFIED` warning 코드 명시 | `interface_ledger_v0.md` Section 3.2 | ✅ 적용됨 | "warning 코드 VERSION_KEY_UNSPECIFIED 기록 필수" |
| schema에 4키 추가 | `fitting_manifest.schema.json` provenance | ✅ 적용됨 | 4개 키 + manifest_path 추가 |
| Version Policy 섹션 존재 | `fitting_interface_v0.md` | ✅ 적용됨 | "## Version Policy (C)" 섹션 추가 |

---

### 4. Warnings 포맷: Canonical {count, sample_messages, truncated}

| 검증 항목 | 대상 파일 | 상태 | 비고 |
|----------|----------|------|------|
| Canonical format 정의 | `interface_ledger_v0.md` Section 6.1 | ✅ 적용됨 | {count, sample_messages, truncated} 구조 |
| sample_messages 최대 5개 규칙 | `interface_ledger_v0.md` Section 6.2 | ✅ 적용됨 | "sample_messages: 최대 5개" |
| truncated 플래그 규칙 | `interface_ledger_v0.md` Section 6.2 | ✅ 적용됨 | "truncated: 5개 초과 시 true" |
| Cross-module 출력 canonical 필수 | `interface_ledger_v0.md` Section 6.2 | ✅ 적용됨 | "Cross-module artifact는 canonical format 사용 필수" |
| Simple format은 내부용만 | `interface_ledger_v0.md` Section 6.3 | ✅ 적용됨 | "내부 사용 시에만 허용" |

---

### 5. NaN/Inf → null 직렬화 (Schema-문서 일치)

| 검증 항목 | 대상 파일 | 상태 | 비고 |
|----------|----------|------|------|
| NaN → null 규칙 명시 | `interface_ledger_v0.md` Section 5.1 | ✅ 적용됨 | 테이블에 명시 |
| Inf → null + warning 코드 | `interface_ledger_v0.md` Section 5.1 | ✅ 적용됨 | `INF_SERIALIZED_AS_NULL` |
| Schema에 null 허용 | `geometry_manifest.schema.json` measurements_summary | ✅ 적용됨 | `["number", "null"]` |
| Schema 호환성 규칙 | `interface_ledger_v0.md` Section 5.2 | ✅ 적용됨 | "측정값 필드에 null 허용 필수" |

---

### 6. Round 신규 규칙 vs 기존 round40~71 LEGACY 스탬프

| 검증 항목 | 대상 파일 | 상태 | 비고 |
|----------|----------|------|------|
| 신규 round 경로 형식 정의 | `interface_ledger_v0.md` Section 4.4 | ✅ 적용됨 | `docs/ops/rounds/<lane>/<milestone>/round_<NN>.md` |
| Milestone 형식 정의 | `interface_ledger_v0.md` Section 4.2 | ✅ 적용됨 | `M<NN>_<short_tag>` |
| Legacy round 처리 규칙 | `interface_ledger_v0.md` Section 4.5 | ✅ 적용됨 | "LEGACY NAMING... 히스토리 보존" |
| round40.md LEGACY 스탬프 | `docs/ops/rounds/round40.md` | ✅ 적용됨 | 4줄 스탬프 prepend |
| round71.md LEGACY 스탬프 | `docs/ops/rounds/round71.md` | ✅ 적용됨 | 4줄 스탬프 prepend |
| 총 30개 파일 스탬프 | `docs/ops/rounds/round*.md` | ✅ 적용됨 | 동일 스탬프 적용 |

---

### 7. MasterPlan.txt LEGACY 스탬프

| 검증 항목 | 대상 파일 | 상태 | 비고 |
|----------|----------|------|------|
| LEGACY 스탬프 추가 | `docs/MasterPlan.txt` line 1 | ✅ 적용됨 | 4줄 스탬프 prepend |
| Canonical source 링크 | 스탬프 내용 | ✅ 적용됨 | `SYNC_HUB.md`, `docs/architecture/LAYERS_v1.md` |
| 내용 재작성 없음 | `docs/MasterPlan.txt` | ✅ 유지됨 | 스탬프만 추가 |

---

## 일관성 검증 요약

| Canon | 정의 문서 | 적용 문서 | 적용 Schema | 상태 |
|-------|----------|----------|-------------|------|
| Path=C | interface_ledger_v0.md §1 | fitting_interface_v0.md | fitting_manifest.schema.json | ✅ |
| Name=B | interface_ledger_v0.md §2 | fitting_interface_v0.md | — | ✅ |
| Version=C | interface_ledger_v0.md §3 | fitting_interface_v0.md | fitting_manifest.schema.json | ✅ |
| Round policy | interface_ledger_v0.md §4 | round40~71 스탬프 | — | ✅ |
| NaN→null | interface_ledger_v0.md §5 | — | geometry_manifest.schema.json | ✅ |
| Warnings canonical | interface_ledger_v0.md §6 | fitting_interface_v0.md (기존) | — | ✅ |

---

## 적용된 파일 목록

### 신규 생성 (1개)
- `contracts/interface_ledger_v0.md`

### LEGACY 스탬프 추가 (31개)
- `docs/MasterPlan.txt`
- `docs/ops/rounds/round40.md` ~ `round71.md` (30개)

### 내용 수정 (3개)
- `fitting_lab/contracts/fitting_interface_v0.md`
- `fitting_lab/labs/specs/fitting_manifest.schema.json`
- `fitting_lab/contracts/geometry_manifest.schema.json`

---

## 미해결 항목 (범위 외)

| 항목 | 사유 | 후속 조치 |
|------|------|----------|
| `specs/common/geometry_manifest.schema.json` null 허용 | fitting_lab 외부 파일 | 별도 PR 필요 |
| `docs/ops/rounds/README.md` 신규 규칙 안내 | 대규모 편집 금지 | 필요 시 1~3줄 추가 (별도 PR) |
| Sample output 파일 업데이트 | 코드/산출물 변경 금지 | 다음 run 시 자동 반영 |

---

## 최종 판정

**모든 합의된 Canon이 문서/스키마에 반영됨**: ✅ 완료

- Path policy C: ✅ 정의됨, 적용됨
- Naming policy B: ✅ 정의됨, 적용됨
- Version policy C: ✅ 정의됨, 적용됨
- Round policy: ✅ 정의됨, LEGACY 스탬프 적용됨
- NaN→null: ✅ 정의됨, schema 수정됨
- Warnings canonical: ✅ 정의됨 (기존 fitting_interface_v0.md 유지)
