# validation: round30 S1 load_failed diagnostics (resolved path/exception)

## 목적

Round30을 통해 Round29에서 관측된 proxy 5개가 stage=load_mesh, reason=load_failed로 전부 실패한 문제를 진단하기 위해 구체적인 예외/경로 resolve 정보를 facts로 남기고, processed>=1을 복구합니다.
PASS/FAIL 판정 금지. 측정 알고리즘 정답 튜닝 금지. 대규모 리팩터링 금지.

## 변경 파일 목록

### 커밋 1: validation: record resolved mesh path and load exception for S1 runner (round30)
- `verification/runners/run_geo_v0_s1_facts.py`: skip_reasons.jsonl 레코드에 진단 필드 추가

### 커밋 2: docs(ops,reports): record round30 load_failed diagnostics
- `reports/validation/INDEX.md`: Round30 항목 추가
- `docs/ops/INDEX.md`: Round Registry에 Round30 추가

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round30_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## Round29 → Round30 개선

### Round29 관측
- 200 중 195는 manifest_path_is_null (정상)
- proxy 5개는 stage=load_mesh, reason=load_failed로 전부 실패
- processed=0

### Round30 목표
- load_failed의 "구체 예외/경로 resolve"를 facts로 남김
- skip_reasons.jsonl 레코드에 추가 필드:
  - mesh_path_resolved (string): resolve된 경로
  - mesh_exists (bool): 파일 존재 여부
  - exception_type (optional): 예외 타입
  - exception_1line (optional): 예외 메시지 1줄 (load_failed에 반드시 채워질 것)
- 상대경로 mesh_path는 Path.cwd() 기준으로 resolve
- 목표: processed>=1 복구

## 구현 선택 (facts-only)

### 1) Skip Reasons 레코드 진단 필드 추가
- **추가 필드**:
  - `mesh_path_resolved` (string): resolve된 경로
  - `mesh_exists` (bool): 파일 존재 여부
  - `exception_type` (optional): 예외 타입 (예: FileNotFoundError, ValueError)
  - `exception_1line` (optional): 예외 메시지 1줄 (load_failed에 반드시 채워질 것)
- **효과**: load_failed 원인을 구체적으로 추적 가능

### 2) 상대경로 mesh_path resolve
- **방식**: 
  - if absolute: resolve() 그대로
  - else: (Path.cwd() / mesh_path).resolve()
- **효과**: 상대경로가 올바르게 resolve되어 파일 존재 여부 확인 가능

### 3) 로더 예외 상세 기록
- **방식**: 로더에서 예외 발생 시
  - stage="load_mesh", reason="load_failed"
  - exception_1line에는 str(e) 1줄로 기록
  - mesh_path_resolved/mesh_exists도 함께 기록
- **효과**: 예외 원인을 구체적으로 파악 가능

### 4) Proxy 슬롯 5개 attempted_load 보장
- **방식**: proxy 5개 케이스(has_mesh_path=True 5개)는 반드시 attempted_load=True로 들어가게 유지
- **효과**: proxy 슬롯에 대한 상세 로드 실패 원인 추적 가능

## 금지사항 준수 확인

- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 측정 알고리즘 변경 없음 (로깅/진단만 추가)
- ✅ no PASS/FAIL 판정: facts-only 유지
- ✅ verification/runs/** 커밋 금지 준수
- ✅ semantic 재해석 금지: 단위 변환만 수행 (의미 매핑 금지)

## DoD 체크리스트

### Round30 실행 전 (현재 PR)
- [x] skip_reasons.jsonl 레코드에 진단 필드 추가 (mesh_path_resolved, mesh_exists, exception_type, exception_1line)
- [x] 상대경로 mesh_path는 Path.cwd() 기준으로 resolve
- [x] 로더에서 예외 발생 시 상세 정보 기록
- [x] proxy 5개 케이스는 attempted_load=True 유지
- [x] reports/validation/INDEX.md 업데이트 (Round30 항목)
- [x] docs/ops/INDEX.md 업데이트 (Round Registry)
- [x] 커밋 및 푸시 완료

### Round30 실행 후 (후속 PR 예정)
- [ ] Round30 실행 (위 커맨드)
- [ ] 산출물 점검 (KPI.md, KPI_DIFF.md, lineage/manifest, PROMPT_SNAPSHOT.md, artifacts/skip_reasons.jsonl)
- [ ] processed/skipped 수치 확인
- [ ] reports/validation/geo_v0_s1_facts_round30.md 생성
- [ ] 커밋: "validation: round30 geo v0 S1 facts + postprocess closure"

## DoD Self-check (facts-only)

**주의**: 아래는 "존재/경로/관측값"으로만 기입 (판정 금지).

### 1) Proxy 5개 레코드 진단 정보 (5줄)
```
[실행 후 skip_reasons.jsonl에서 proxy 5개 케이스 레코드의 mesh_path_resolved / mesh_exists / exception_1line 출력 5줄 복사]
```

### 2) Skip Reasons 레코드 진단 필드 확인
- [ ] 각 레코드에 다음 필드 존재 (load_failed인 경우):
  - mesh_path_resolved (string): resolve된 경로
  - mesh_exists (bool): 파일 존재 여부
  - exception_type (optional): 예외 타입
  - exception_1line (optional): 예외 메시지 1줄

### 3) 상대경로 resolve 확인
- [ ] 상대경로 mesh_path가 Path.cwd() 기준으로 올바르게 resolve됨
  - mesh_path_resolved 경로: [실행 후 기록]
  - mesh_exists: [실행 후 기록]

### 4) Round30 실행 결과 (facts-only)
- [ ] processed cases: [실행 후 기록]
- [ ] skipped cases: [실행 후 기록]
- [ ] processed >= 1 여부: [실행 후 기록] (목표: processed>=1 복구)

### 5) Postprocess 산출물 생성 확인
- [ ] `KPI.md` exists
- [ ] `KPI_DIFF.md` exists (상단 경고 라인 존재 여부: [실행 후 기록])
- [ ] `lineage/manifest` 또는 `LINEAGE.md` exists
- [ ] `PROMPT_SNAPSHOT.md` exists

### 6) Proxy 슬롯 5개 attempted_load 확인
- [ ] proxy 슬롯 5개 (311610164126, 20_F_1049, 121607160426, 21_F_4430, 511609194879)의 attempted_load가 모두 True
  - attempted_load=True 레코드 수: [실행 후 기록]

## 스모크 테스트

### Skip Reasons 진단 필드 확인
```bash
# skip_reasons.jsonl에서 proxy 5개 레코드의 진단 필드 확인
py -c "import json; f = open('verification/runs/facts/geo_v0_s1/round30_*/artifacts/skip_reasons.jsonl'); lines = [json.loads(l) for l in f if l.strip()]; proxy_cases = ['311610164126', '20_F_1049', '121607160426', '21_F_4430', '511609194879']; proxy_records = [r for r in lines if r['case_id'] in proxy_cases]; print(f'Proxy records: {len(proxy_records)}'); print(f'All have mesh_path_resolved: {all(\"mesh_path_resolved\" in r for r in proxy_records)}'); print(f'All have mesh_exists: {all(\"mesh_exists\" in r for r in proxy_records)}'); print(f'All have exception_1line: {all(\"exception_1line\" in r for r in proxy_records if r.get(\"reason\") == \"load_failed\")}')"
# 예상: Proxy records: 5, All have mesh_path_resolved: True, All have mesh_exists: True, All have exception_1line: True
```

### 링크 유효성 확인
- [x] `reports/validation/INDEX.md`에서 Round30 링크 유효성 확인
- [x] `docs/ops/INDEX.md`에서 Round Registry 링크 유효성 확인

## 롤백

```bash
git revert HEAD~1 HEAD
```

또는 브랜치 삭제:
```bash
git branch -D validation/round30-s1-load-failed-diagnostics
git push origin --delete validation/round30-s1-load-failed-diagnostics
```
