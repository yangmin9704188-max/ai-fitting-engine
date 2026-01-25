# ops: add round postprocessing tool (v0.2)

## 목적
팀 시스템 최소 자동화 레이어(v0.2) 구현: 라운드 후처리를 단일 명령으로 자동화하여 운영 일관성 확보

## 자동화된 기능

### 1. 라운드 후처리 단일 명령 도구
- `tools/postprocess_round.py`: 라운드 실행 후 필수 후처리 도구
  - KPI 생성: `KPI.md`, `kpi.json`
  - Prev/Baseline diff: `KPI_DIFF.md` (두 섹션 모두 포함)
  - ROUND_CHARTER.md 자동 생성 (템플릿 기반)
  - Coverage backlog 자동 업데이트

### 2. Baseline 관리
- `tools/set_baseline_run.py`: Baseline run 설정 도구
- `verification/runs/facts/_baseline.json`: Baseline 포인터 파일

### 3. KPI Summarizer 개선
- `tools/summarize_facts_kpi.py`: `--out_json` 옵션 추가

### 4. 프로젝트 헌법 업데이트
- `.cursorrules`: 라운드 후처리 필수 규칙 추가 (Section 9)

### 5. 문서
- `docs/verification/round_ops_v0.md`: Runbook (표준 실행 커맨드 템플릿)
- `docs/verification/coverage_backlog.md`: Facts-only coverage tracking

## 변경 파일 목록

- `tools/postprocess_round.py` (신규)
- `tools/set_baseline_run.py` (신규)
- `tools/summarize_facts_kpi.py` (개선: --out_json 옵션)
- `.cursorrules` (업데이트: Section 9 추가)
- `docs/verification/round_ops_v0.md` (신규)
- `docs/verification/coverage_backlog.md` (신규)

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
- `verification/runs/facts/curated_v0/round20_20260125_164801/KPI.md`
- `verification/runs/facts/curated_v0/round20_20260125_164801/kpi.json`
- `verification/runs/facts/curated_v0/round20_20260125_164801/KPI_DIFF.md`
- `verification/runs/facts/curated_v0/round20_20260125_164801/ROUND_CHARTER.md`
- `docs/verification/coverage_backlog.md` (업데이트됨)

### 2. Baseline 설정
```bash
py tools/set_baseline_run.py \
  --run_dir verification/runs/facts/curated_v0/round20_20260125_164801
```

**기대 산출물:**
- `verification/runs/facts/_baseline.json` 생성

### 3. Baseline diff 확인
```bash
py tools/postprocess_round.py \
  --run_dir verification/runs/facts/curated_v0/round20_20260125_164503
```

**기대 결과:**
- `KPI_DIFF.md`에 "Diff vs Baseline" 섹션 포함 확인

## 스모크 테스트 결과

✅ Postprocess 실행 성공: 모든 산출물 생성 확인
✅ Baseline 설정 성공: _baseline.json 생성 확인
✅ Baseline diff 생성 확인: KPI_DIFF.md에 두 섹션 모두 포함
