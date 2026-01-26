# Obsidian Home

**Start Here**: 이 파일이 프로젝트 탐색의 단일 진입점입니다.

---

## 5-Layer Navigation

### L1 Semantic (정의)
- **SoT**: [docs/semantic/measurement_semantics_v0.md](../semantic/measurement_semantics_v0.md) - 45개 표준 키 의미론 봉인
- **Measurements Index**: [docs/policies/measurements/INDEX.md](measurements/INDEX.md) - 측정 정책 SoT 인덱스
- **SizeKorea Evidence**: [docs/semantic/evidence/sizekorea_measurement_methods_v0.md](../semantic/evidence/sizekorea_measurement_methods_v0.md) - 측정 방법 기준점

### L2 Contract (계약)
- **Interface Contracts**: [docs/policies/measurements/CONTRACT_INTERFACE_*.md](measurements/) - 측정 인터페이스 계약
- **Unit Standard**: [docs/contract/UNIT_STANDARD.md](../contract/UNIT_STANDARD.md) - 단위 표준

### L3 Geometric (구현)
- **Core Measurements**: [core/measurements/](../../core/measurements/) - 측정 함수 구현
- **Geometric Designs**: [docs/policies/measurements/GEOMETRIC_DESIGN_*.md](measurements/) - 기하학 설계 문서

### L4 Validation (검증)
- **Validation Frames**: [docs/policies/measurements/VALIDATION_FRAME_*.md](measurements/) - 검증 프레임
- **Validation Reports**: [reports/validation/](../../reports/validation/) - 검증 리포트

### L5 Judgment (판단)
- **Judgments Index**: [docs/judgments/INDEX.md](../judgments/INDEX.md) - 판단 문서 인덱스
- **Judgments**: [docs/judgments/measurements/](../judgments/measurements/) - 측정 판단 문서

---

## Current Baseline (facts-only)

- **baseline_tag (alias)**: `curated-v0-realdata-v0.1`
- **baseline_run_dir**: `verification/runs/facts/curated_v0/round20_20260125_164801`
- **baseline_report**: [reports/validation/curated_v0_facts_round1.md](../../reports/validation/curated_v0_facts_round1.md)
- **lane**: `curated_v0`

---

## Key Registries

- **Round Registry**: [docs/verification/round_registry.json](../verification/round_registry.json) - 검증 라운드 추적
- **Golden Registry**: [docs/verification/golden_registry.json](../verification/golden_registry.json) - NPZ 파일 전역 레지스트리
- **Coverage Backlog**: [docs/verification/coverage_backlog.md](../verification/coverage_backlog.md) - all-null 키 추적

---

## SizeKorea Integration

- **Integration Checklist**: [docs/ops/sizekorea_integration_checklist.md](sizekorea_integration_checklist.md) - SizeKorea 통합 상태 체크리스트
- **Raw Data**: `data/raw/sizekorea_raw/` - SizeKorea 원천 데이터
- **Curated Dataset**: `data/processed/curated_v0/curated_v0.parquet` - 통합 정제 데이터셋
- **Mapping Contract**: `data/column_map/sizekorea_v2.json` - 컬럼 매핑 계약

---

## Ops Cross-cutting

- **SYNC_HUB**: [SYNC_HUB.md](../../SYNC_HUB.md) - 전략적 결정 및 현재 마일스톤
- **CURRENT_STATE**: [docs/sync/CURRENT_STATE.md](../sync/CURRENT_STATE.md) - 실시간 파이프라인 상태
- **Cursor Rules**: [.cursorrules](../../.cursorrules) - AI 협업 규칙
- **Cursor Prompt Header**: [docs/ops/cursor_prompt_header.md](cursor_prompt_header.md) - 표준 프롬프트 헤더

---

## How to Use (30 sec)

**옵시디언에서 클릭 3개로 탐색하는 루틴:**

1. **Home 열기**: 파일 탐색기에서 `docs/ops/OBSIDIAN_HOME.md` 클릭
2. **Canvas 열기**: `docs/ops/canvas/PROJECT_MAP.canvas` 더블클릭 (Canvas 뷰)
3. **링크 따라가기**: Home 또는 Canvas에서 원하는 문서 링크 클릭

**추가 팁:**
- Graph view로 문서 간 연결 관계 시각화
- 파일 검색(Ctrl+O)으로 빠른 문서 찾기
- Home을 스타(즐겨찾기)로 고정하여 빠른 접근
