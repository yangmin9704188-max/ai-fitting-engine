# validation: round29 S1 per-case skip reasons logging (SSoT)

## 목적

Round29를 통해 Round28에서 관측된 processed=0이고 artifacts/visual/SKIPPED.txt가 헤더 4줄만 있어서 케이스별 원인 추적이 불가능한 문제를 해결합니다.
케이스별 스킵 사유를 SSoT로 남기는 로깅을 추가합니다.
PASS/FAIL 판정 금지. 측정 알고리즘 정답 튜닝 금지. 대규모 리팩터링 금지.

## 변경 파일 목록

### 커밋 1: validation: add per-case skip reasons log for geo_v0_s1 facts runner (round29)
- `verification/runners/run_geo_v0_s1_facts.py`: 케이스별 스킵 사유 로깅 추가 (skip_reasons.jsonl)

### 커밋 2: docs(ops,reports): record round29 skip reasons logging
- `reports/validation/INDEX.md`: Round29 항목 추가
- `docs/ops/INDEX.md`: Round Registry에 Round29 추가

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round29_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## Round28 → Round29 개선

### Round28 관측
- processed=0
- artifacts/visual/SKIPPED.txt는 헤더 4줄만 존재
- 케이스별 원인 추적 불가능

### Round29 목표
- 케이스별 스킵 사유를 SSoT로 남기는 로깅 추가
- skip_reasons.jsonl 파일에 각 케이스의 스킵 사유 기록
- proxy 슬롯 5개는 반드시 attempted_load=True까지 진입하여 로드 시도
- artifacts/visual/SKIPPED.txt는 헤더만 유지, 케이스별 사유는 skip_reasons.jsonl에 기록 (overwrite 방지)

## 구현 선택 (facts-only)

### 1) Skip Reasons Logging
- **산출물**: `<RUN_DIR>/artifacts/skip_reasons.jsonl` (JSON Lines 형식)
- **각 레코드 필드**:
  - `case_id` (string): 케이스 ID
  - `has_mesh_path` (bool): mesh_path 존재 여부
  - `mesh_path` (string|null): mesh_path 값
  - `attempted_load` (bool): 로드 시도 여부
  - `stage` (string): 스킵 단계 (precheck|load_mesh|convert_units|measure|metadata)
  - `reason` (string): 스킵 사유 (short stable key)
  - `exception_1line` (string|null): 예외 메시지 (1-line)
- **효과**: processed=0이어도 "왜 0인지"를 케이스 단위로 사실로 남김

### 2) Proxy 슬롯 5개 로드 시도 보장
- **방식**: mesh_path가 있는 케이스(현재 5개)는 attempted_load=True까지 진입
- **실패 처리**: stage=load_mesh에서 exception_1line 기록
- **precheck 차단**: precheck에서 막힌다면 stage=precheck로 reason 기록
- **효과**: proxy 슬롯 5개에 대한 상세 로드 실패 원인 추적 가능

### 3) SKIPPED.txt 헤더만 유지
- **방식**: artifacts/visual/SKIPPED.txt는 visual best-effort 증빙 헤더로만 유지
- **케이스별 사유**: skip_reasons.jsonl에 기록하여 overwrite로 가려지지 않게 함
- **효과**: 헤더는 유지하되, 상세 사유는 별도 파일에 안전하게 기록

## 금지사항 준수 확인

- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 측정 알고리즘 변경 없음 (로깅만 추가)
- ✅ no PASS/FAIL 판정: facts-only 유지
- ✅ verification/runs/** 커밋 금지 준수
- ✅ semantic 재해석 금지: 단위 변환만 수행 (의미 매핑 금지)

## DoD 체크리스트

### Round29 실행 전 (현재 PR)
- [x] run_geo_v0_s1_facts.py에 케이스별 스킵 사유 로깅 추가
- [x] skip_reasons.jsonl 파일 생성 로직 추가
- [x] proxy 슬롯 5개는 attempted_load=True까지 진입하도록 보장
- [x] SKIPPED.txt는 헤더만 유지하도록 수정
- [x] reports/validation/INDEX.md 업데이트 (Round29 항목)
- [x] docs/ops/INDEX.md 업데이트 (Round Registry)
- [x] 커밋 및 푸시 완료

### Round29 실행 후 (후속 PR 예정)
- [ ] Round29 실행 (위 커맨드)
- [ ] 산출물 점검 (KPI.md, KPI_DIFF.md, lineage/manifest, PROMPT_SNAPSHOT.md, visual/SKIPPED.txt, artifacts/skip_reasons.jsonl)
- [ ] processed/skipped 수치 확인
- [ ] reports/validation/geo_v0_s1_facts_round29.md 생성
- [ ] 커밋: "validation: round29 geo v0 S1 facts + postprocess closure"

## DoD Self-check (facts-only)

**주의**: 아래는 "존재/경로/관측값"으로만 기입 (판정 금지).

### 1) skip_reasons.jsonl 생성 경로
- [ ] `verification/runs/facts/geo_v0_s1/round29_<timestamp>/artifacts/skip_reasons.jsonl` exists
  - 파일 크기: [실행 후 기록]
  - 라인 수: [실행 후 기록] (>=200 또는 최소 proxy 5개 포함)

### 2) Proxy 5개 레코드 샘플 5줄
```
[실행 후 skip_reasons.jsonl에서 proxy 5개 케이스 레코드 샘플 5줄 복사]
```

### 3) Skip Reasons 레코드 필드 확인
- [ ] 각 레코드에 다음 필드 존재:
  - case_id (string)
  - has_mesh_path (bool)
  - mesh_path (string|null)
  - attempted_load (bool)
  - stage (precheck|load_mesh|convert_units|measure|metadata)
  - reason (short stable key)
  - exception_1line (optional, 1-line)

### 4) Proxy 슬롯 5개 attempted_load 확인
- [ ] proxy 슬롯 5개 (311610164126, 20_F_1049, 121607160426, 21_F_4430, 511609194879)의 attempted_load가 모두 True
  - attempted_load=True 레코드 수: [실행 후 기록]

### 5) Round29 실행 결과 (facts-only)
- [ ] processed cases: [실행 후 기록]
- [ ] skipped cases: [실행 후 기록]
- [ ] processed > 0 여부: [실행 후 기록]

### 6) Postprocess 산출물 생성 확인
- [ ] `KPI.md` exists
- [ ] `KPI_DIFF.md` exists (상단 경고 라인 존재 여부: [실행 후 기록])
- [ ] `lineage/manifest` 또는 `LINEAGE.md` exists
- [ ] `PROMPT_SNAPSHOT.md` exists

### 7) SKIPPED.txt 헤더 확인
- [ ] `artifacts/visual/SKIPPED.txt` exists
- [ ] 헤더 4줄만 존재 (케이스별 상세 사유는 skip_reasons.jsonl에 기록)
  - 헤더 내용: [실행 후 기록]

## 스모크 테스트

### Skip Reasons 로깅 확인
```bash
# skip_reasons.jsonl 파일이 생성되는지 확인
ls -la verification/runs/facts/geo_v0_s1/round29_*/artifacts/skip_reasons.jsonl
# 예상: 파일 존재
```

### Proxy 슬롯 attempted_load 확인
```bash
# proxy 슬롯 5개의 attempted_load가 True인지 확인
py -c "import json; f = open('verification/runs/facts/geo_v0_s1/round29_*/artifacts/skip_reasons.jsonl'); lines = [json.loads(l) for l in f if l.strip()]; proxy_cases = ['311610164126', '20_F_1049', '121607160426', '21_F_4430', '511609194879']; proxy_records = [r for r in lines if r['case_id'] in proxy_cases]; print(f'Proxy records: {len(proxy_records)}'); print(f'All attempted_load=True: {all(r.get(\"attempted_load\") == True for r in proxy_records)}')"
# 예상: Proxy records: 5, All attempted_load=True: True
```

### 링크 유효성 확인
- [x] `reports/validation/INDEX.md`에서 Round29 링크 유효성 확인
- [x] `docs/ops/INDEX.md`에서 Round Registry 링크 유효성 확인

## 롤백

```bash
git revert HEAD~1 HEAD
```

또는 브랜치 삭제:
```bash
git branch -D validation/round29-s1-skip-reasons
git push origin --delete validation/round29-s1-skip-reasons
```
