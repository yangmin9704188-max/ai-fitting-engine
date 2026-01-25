# Commit Policy

**Purpose**: Define "what to commit" based on signals (no judgment, no thresholds).

## Non-Negotiables

### PASS/FAIL 금지
- 모든 커밋 결정은 facts-only 신호 기반
- 자동 PASS/FAIL 판정 로직 금지
- 임계 수치 선언 금지

### Semantic 재논의 금지
- 측정 단위/의미론 재해석 금지
- 기존 contract/schema 의미 변경 금지
- 커밋 결정 시 semantic 변경 포함 금지

### 로컬 산출물 커밋 금지
- `verification/runs/` 하위 산출물 커밋 금지
- `verification/tmp/` 하위 파일 커밋 금지
- `verification/local_artifacts/` 하위 파일 커밋 금지 (README.md 제외)
- 런타임 생성 파일 커밋 금지

## Commit Targets / Non-Targets

### Commit Targets (Allow)
- `docs/ops/**`: 운영 문서/템플릿/인덱스
- `docs/verification/**`: 검증 정책/계약/레지스트리
- `tools/postprocess_round.py`: 라운드 후처리 도구
- `tools/round_registry.py`: 레지스트리 유지 도구
- `tools/kpi_diff.py`: KPI diff 생성 도구
- `tools/coverage_backlog.py`: Coverage backlog 유지 도구
- `tools/lineage.py`: Lineage manifest 생성 도구
- `tools/golden_registry.py`: Golden registry 유지 도구
- `tools/visual_provenance.py`: Visual provenance 생성 도구
- `reports/validation/lanes/**`: 표준화된 리포트 (lanes 아래)
- `reports/validation/INDEX.md`: 리포트 인덱스
- `.cursorrules`: 프로젝트 규칙
- `.gitignore`: Git ignore 규칙
- `Makefile`: 빌드/실행 래퍼

### Non-Targets (Deny)
- `verification/runs/**`: 로컬 실행 산출물
- `verification/tmp/**`: 임시 파일
- `verification/local_artifacts/**`: 로컬 전용 산출물 (README.md 제외)
- `core/**`: 코어 로직 (ops PR에서 변경 금지)
- `pipelines/**`: 파이프라인 로직 (ops PR에서 변경 금지)
- `tests/**`: 테스트 코드 (ops PR에서 변경 금지)
- `*.xls`, `*.xlsx`: 임시 엑셀 파일
- 깨진 파일명 파일 (인코딩 오류)

## Golden Candidate Signals

**주의**: 아래 신호는 "판정"이 아니라 "관찰 가능한 사실"입니다. 임계 수치는 선언하지 않습니다.

### Coverage 신호
- **All-null 키 감소**: 이전 round 대비 100% NaN 키 개수 감소
- **All-null 키 신규 등장**: 이전 round에 없던 100% NaN 키 등장
- **Coverage backlog 상태**: `docs/verification/coverage_backlog.md`의 ACTIVE 키 개수

### Distribution 신호
- **HEIGHT_M 분포 안정성**: p50/p95 값의 변화량 (절대값, 단위: m)
- **BUST/WAIST/HIP p50 변화**: 이전 round 대비 변화량 (절대값, 단위: m)
- **분포 형태 변화**: 히스토그램/분위수 패턴 변화 (정성적 관찰)

### Failure Reason 신호
- **Top5 reason 변화**: 이전 round 대비 failure reason Top5 교집합/차집합
- **신규 reason 등장**: 이전에 없던 failure reason이 Top5에 진입
- **Reason 해소**: 이전 Top5 reason이 현재 Top5에서 사라짐

### Registry 신호
- **Round 연속성**: `round_registry.json`에서 round_num 연속성
- **Artifact 완성도**: KPI.md, KPI_DIFF.md, LINEAGE.md 존재 여부
- **Baseline 일관성**: baseline.run_dir이 변경되지 않음

### Lineage 신호
- **Code fingerprint 안정성**: `LINEAGE.md`의 code_fingerprints (git commit) 변화
- **NPZ 메타데이터 일관성**: schema_version, meta_unit 일관성
- **Source 추적성**: source_path_abs, source_npz 경로 유효성

## Action Mapping

**중요**: 아래는 "자동 수행"이 아니라 "권고/후속 작업"입니다.

### Golden Tag 후보 신호
다음 신호가 충족되면 golden tag 후보로 고려:
- Coverage 신호: All-null 키 감소 + 신규 등장 없음
- Distribution 신호: HEIGHT_M p50/p95 안정성 + BUST/WAIST/HIP p50 안정성
- Failure Reason 신호: Top5 reason 안정성 (교집합 높음)
- Registry 신호: Round 연속성 + Artifact 완성도
- Lineage 신호: Code fingerprint 안정성 + NPZ 메타데이터 일관성

**후속 작업**: `docs/verification/golden_s0_freeze_v0.md` 참조하여 freeze 선언 고려

### Baseline 후보 신호
다음 신호가 충족되면 baseline 후보로 고려:
- Registry 신호: Round 연속성 + Artifact 완성도
- Coverage 신호: All-null 키 감소 또는 안정성
- Distribution 신호: HEIGHT_M/BUST/WAIST/HIP 분포 안정성
- Lineage 신호: Source 추적성 + Code fingerprint 안정성

**후속 작업**: `docs/ops/baselines.json` 업데이트 고려, `docs/verification/round_registry.json` baseline 설정 고려

### Registry 업데이트 권고
다음 신호가 충족되면 registry 업데이트 권고:
- Artifact 완성도: KPI.md, KPI_DIFF.md, LINEAGE.md 모두 존재
- Round 연속성: round_num이 이전 round와 연속
- Coverage backlog 갱신: coverage_backlog.md가 갱신됨

**후속 작업**: `postprocess_round.py` 실행으로 registry 자동 업데이트

## Evidence Checklist

커밋 전 다음 산출물 존재 여부를 확인합니다:

### Round Artifacts
- [ ] `KPI.md`: `<run_dir>/KPI.md` 존재
- [ ] `KPI_DIFF.md`: `<run_dir>/KPI_DIFF.md` 존재 (prev/baseline 비교)
- [ ] `LINEAGE.md`: `<run_dir>/LINEAGE.md` 존재
- [ ] `ROUND_CHARTER.md`: `<run_dir>/ROUND_CHARTER.md` 존재 (또는 스텁)
- [ ] `PROMPT_SNAPSHOT.md`: `<run_dir>/PROMPT_SNAPSHOT.md` 존재

### Registries
- [ ] `docs/verification/round_registry.json`: 현재 round 엔트리 존재
- [ ] `docs/verification/golden_registry.json`: NPZ 엔트리 존재 (해당하는 경우)
- [ ] `docs/verification/coverage_backlog.md`: 갱신 여부 확인

### Visual Provenance
- [ ] `artifacts/visual/` 폴더 존재
- [ ] Visual 가능: `front_xy.png`, `side_zy.png` 존재
- [ ] Visual 불가: `SKIPPED.txt` 존재 (고정 문구 + reason line 포함)

### Report
- [ ] `reports/validation/lanes/<lane>/<round_id>_facts.md` 존재 (새 round)
- [ ] 또는 기존 report 경로 유지 (기존 round)

## Reference Links

- [`docs/verification/curated_v0_gate_draft_v0.md`](../verification/curated_v0_gate_draft_v0.md): Facts 신호 → 행동 매핑
- [`docs/verification/kpi_diff_contract_v0.md`](../verification/kpi_diff_contract_v0.md): KPI_DIFF 구조
- [`docs/verification/round_registry_contract_v0.md`](../verification/round_registry_contract_v0.md): Round registry 스키마
- [`docs/verification/lineage_manifest_contract_v0.md`](../verification/lineage_manifest_contract_v0.md): LINEAGE 구조
- [`docs/verification/golden_s0_freeze_v0.md`](../verification/golden_s0_freeze_v0.md): Golden freeze 예시
