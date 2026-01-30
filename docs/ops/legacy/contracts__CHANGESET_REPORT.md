# CHANGESET_REPORT.md

**생성일**: 2026-01-29
**작업자**: Contract/Interface Editor

---

## 1. 변경 파일 목록

| # | 파일 경로 | 작업 유형 | 변경 목적 |
|---|----------|----------|----------|
| 1 | `contracts/interface_ledger_v0.md` | CREATE | 모든 Canon(Path=C, Name=B, Version=C, Round, NaN, warnings)을 단일 문서로 잠금 |
| 2 | `docs/MasterPlan.txt` | PREPEND | 5-Layer/6-Layer 혼재 → LEGACY 스탬프 추가, canonical 문서 링크 |
| 3 | `docs/ops/rounds/round40.md` ~ `round71.md` (30개) | PREPEND | LEGACY NAMING 스탬프 추가 (내용 재작성 없음) |
| 4 | `fitting_lab/contracts/fitting_interface_v0.md` | EDIT | fitting 출력 파일명 통일 + Version=C + Path=C 정책 추가 |
| 5 | `fitting_lab/labs/specs/fitting_manifest.schema.json` | EDIT | provenance에 4 version keys + path_base 추가 |
| 6 | `fitting_lab/contracts/geometry_manifest.schema.json` | EDIT | measurements_summary에 null 허용 (NaN→null 정책) |

---

## 2. 이슈-Canon 매핑 테이블

| Issue # | 이슈 설명 | 해결 Canon | 적용 파일 |
|---------|----------|-----------|----------|
| 1 | Path base 미정의 (manifest_dir vs run_dir) | Path policy: C | interface_ledger_v0.md, fitting_interface_v0.md, fitting_manifest.schema.json |
| 2 | facts_summary.json 파일명 충돌 (body vs fitting) | Naming policy: B | interface_ledger_v0.md, fitting_interface_v0.md |
| 3 | Version keys 불일치 (4키 누락) | Version policy: C | interface_ledger_v0.md, fitting_interface_v0.md, fitting_manifest.schema.json |
| 4 | Round 명명 규칙 충돌 (global vs folder-split) | Round policy | interface_ledger_v0.md, round40~71 LEGACY 스탬프 |
| 5 | warnings 포맷 불일치 (array vs {count,sample_messages}) | Canonical warnings format | interface_ledger_v0.md, fitting_interface_v0.md |
| 6 | NaN/Inf → null 직렬화 vs schema 불일치 | NaN→null policy | interface_ledger_v0.md, geometry_manifest.schema.json |
| 7 | MasterPlan.txt 5-Layer/6-Layer 혼재 | LEGACY stamp | MasterPlan.txt |

---

## 3. 파일별 상세 변경 내역

### 3.1 contracts/interface_ledger_v0.md (NEW)
- Canon 전체를 한 곳에 잠금
- Path=C, Name=B, Version=C, Round policy, NaN→null, warnings canonical 포맷
- Module × Artifact 매핑 테이블 포함

### 3.2 docs/MasterPlan.txt
- 헤더 최상단 4줄 LEGACY 스탬프 추가
- canonical 경로: `SYNC_HUB.md`, `docs/architecture/LAYERS_v1.md`
- 내용 재작성 없음

### 3.3 docs/ops/rounds/round40.md ~ round71.md (30개)
- 각 파일 헤더 최상단 4줄 LEGACY NAMING 스탬프 추가
- 내용 재작성 없음
- 새 round 파일 경로 안내: `docs/ops/rounds/<lane_slug>/<milestone_id>/round_<NN>.md`

### 3.4 fitting_lab/contracts/fitting_interface_v0.md
- `facts_summary.json` → `fitting_facts_summary.json` (fitting 출력 전용)
- body 입력 `facts_summary.json` 언급은 유지
- Version policy C 섹션 추가 (4키 always + UNSPECIFIED)
- Path policy C 섹션 추가 (manifest_dir 기준)
- smoke test/expected_files/예시 JSON 모두 통일

### 3.5 fitting_lab/labs/specs/fitting_manifest.schema.json
- `provenance.properties`에 추가:
  - `snapshot_version`, `semantic_version`, `geometry_impl_version`, `dataset_version`
  - `path_base` (enum: manifest_dir, run_dir)
  - `manifest_path` (ABS 경로 기록용)
- required 강제 안 함 (운영 리스크 방지), 문서에서 MUST로 잠금

### 3.6 fitting_lab/contracts/geometry_manifest.schema.json
- `measurements_summary.additionalProperties`: `"number"` → `["number", "null"]`
- NaN→null 직렬화 정책 반영

---

## 4. 변경하지 않은 항목 (명시적 제외)

| 항목 | 제외 사유 |
|------|----------|
| `specs/common/geometry_manifest.schema.json` | fitting_lab 외부, 이 PR 범위 밖 |
| `docs/ops/rounds/README.md` | 기존 유지, 필요 시 별도 PR |
| 코드 파일 전체 | 코드 변경 금지 정책 |
| 폴더 구조 변경 | 폴더 이동/삭제 금지 정책 |
