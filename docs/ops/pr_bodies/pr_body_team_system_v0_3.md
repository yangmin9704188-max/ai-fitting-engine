# ops: enhance round postprocessing tool (v0.3)

## 목적
팀 시스템 경량 확장(v0.3): Prompt Context Logger, Regression Fact-Check, Data Lineage Manifest, Visual Provenance 추가

## 자동화된 기능

### 1. Prompt Context Logger
- `ROUND_CHARTER.md`에 Prompt Snapshot 섹션 자동 추가
- `PROMPT_SNAPSHOT_TEXT` env var 또는 `PROMPT_SNAPSHOT_PATH` 파일에서 읽기
- 없으면 안내 문구만 남기고 에러 없이 진행

### 2. Regression Fact-Check
- `KPI_DIFF.md`에 Degradation Warning 섹션 추가
- Baseline 대비 주요 지표 악화 시 `⚠️ DEGRADATION` 토큰 출력
- 임계값:
  - NaN rate top5 합이 baseline 대비 +3%p 이상 악화
  - HEIGHT p50이 baseline 대비 ±2% 이상 이동
  - failure_reason top1 count가 baseline 대비 +3% 이상 증가
- Facts-only 경고 (PASS/FAIL 판정 금지)

### 3. Data Lineage Manifest
- `lineage.json` 자동 생성
- 기록 항목:
  - generator_script_path 및 script_sha256
  - source_path_abs의 mtime/size
  - git_commit, created_at

### 4. Visual Provenance (경량 대체안)
- `run_dir/visual/`에 PNG 생성:
  - `normal_1_xy.png`: vertices x-y scatter
  - `normal_1_zy.png`: vertices z-y scatter
- bbox/aspect ratio를 이미지 내 텍스트로 표기
- 리포트 하단에 상대경로 링크 자동 삽입

## 변경 파일 목록

- `tools/postprocess_round.py` (v0.2 → v0.3)

## 금지사항 준수 확인
- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 runner/측정 로직 의미 변경 없음 (추가 도구만)

## 스모크 테스트

### 1. Postprocess 실행
```bash
py tools/postprocess_round.py \
  --run_dir verification/runs/facts/curated_v0/round20_20260125_164801
```

**기대 산출물:**
- `ROUND_CHARTER.md`에 Prompt Snapshot 섹션 존재
- `KPI_DIFF.md`에 Degradation Warning 섹션 (baseline 설정 시)
- `lineage.json` 생성
- `visual/normal_1_xy.png`, `visual/normal_1_zy.png` 생성 (matplotlib 사용 가능 시)
- 리포트 파일에 visual 링크 추가

## 스모크 테스트 결과

✅ Postprocess 실행 성공: 모든 산출물 생성 확인
✅ Prompt Snapshot 섹션 추가 확인
✅ Lineage.json 생성 확인
⚠️ Visual PNG 생성: matplotlib 의존성 (선택적)
