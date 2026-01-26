# validation: round31 S1 loader fallback and exceptions (processed>=5 목표)

## 목적

Round31을 통해 Round30에서 관측된 proxy 5개가 mesh_exists=true인데 load_mesh에서 전부 load_failed인 문제를 해결하기 위해 로더를 이중화하고, 예외 1줄을 facts로 남기면서도 processed=5까지 바로 찍을 수 있도록 합니다.
PASS/FAIL 판정 금지. 측정 알고리즘 정답 튜닝 금지. 대규모 리팩터링 금지.

## 변경 파일 목록

### 커밋 1: validation: add trimesh-optional loader with pure OBJ fallback + exception capture (round31)
- `verification/runners/run_geo_v0_s1_facts.py`: 2단 OBJ 로더 추가 (trimesh 옵션 + pure Python parser 필수)

### 커밋 2: docs(ops,reports): record round31 loader fallback
- `reports/validation/INDEX.md`: Round31 항목 추가
- `docs/ops/INDEX.md`: Round Registry에 Round31 추가

## 재현 커맨드

```bash
RUN_DIR="verification/runs/facts/geo_v0_s1/round31_$(date +%Y%m%d_%H%M%S)" && \
py verification/runners/run_geo_v0_s1_facts.py --out_dir "$RUN_DIR" && \
py tools/postprocess_round.py --current_run_dir "$RUN_DIR"
```

## Round30 → Round31 개선

### Round30 관측
- proxy 5개는 mesh_exists=true인데 load_mesh에서 전부 load_failed
- processed=0

### Round31 목표
- 예외 1줄을 facts로 남기면서도 processed=5까지 바로 찍을 수 있도록 로더를 이중화
- Loader A: trimesh (옵션, MTL/재질 의존 최소화)
- Loader B: pure Python OBJ parser (필수, 'v '와 'f ' 라인만 파싱)
- 목표: processed>=5 복구

## 구현 선택 (facts-only)

### 1) 2단 OBJ 로더 구성
- **Loader A: trimesh (옵션)**
  - try: import trimesh
  - load 시 MTL/재질은 목적이 아니므로 가능한 한 geometry만 로드 (재질/텍스처 의존 최소화)
  - 실패하면 예외를 기록하고 loader B로 fallback
- **Loader B: pure Python OBJ parser (필수)**
  - 파일을 open(..., encoding='utf-8', errors='ignore')로 읽고
  - 'v ' 라인과 'f ' 라인만 파싱하여 vertices/faces 배열을 만듦
  - 'mtllib', 'usemtl', 'vt', 'vn' 등은 무시 (재질/텍스처 목적 아님)
  - face는 "f a/b/c ..." 형태에서 정점 인덱스만 추출 (슬래시 앞 숫자)하고 1-indexed->0-indexed 변환
  - 최소한 vertices만 확보되면 이후 파이프라인이 진행 가능하도록 함
- **효과**: trimesh가 실패해도 pure Python parser로 fallback하여 processed>=5 달성

### 2) 로드 실패 시 skip_reasons.jsonl 기록
- **필수 필드**:
  - exception_type = type(e).__name__
  - exception_1line = str(e).splitlines()[0] (빈 문자열이면 repr(e))
  - loader_name = "trimesh" 또는 "fallback_obj_parser"
  - mesh_path_resolved, mesh_exists는 유지
- **성공 시 (권장)**:
  - loaded_verts, loaded_faces
- **효과**: load_failed 원인을 구체적으로 추적 가능

### 3) Proxy 슬롯 5개 attempted_load 보장
- **방식**: proxy 5개 케이스(has_mesh_path=True 5개)는 반드시 attempted_load=True로 들어가게 유지
- **DoD**: proxy 5개 레코드에는 loader_name과 (성공 시 loaded_*, 실패 시 exception_*)가 반드시 들어가야 함
- **효과**: proxy 슬롯에 대한 상세 로드 성공/실패 원인 추적 가능

## 금지사항 준수 확인

- ✅ no deletions: git rm 없음
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음
- ✅ no code logic changes: 기존 측정 알고리즘 변경 없음 (로더만 추가)
- ✅ no PASS/FAIL 판정: facts-only 유지
- ✅ verification/runs/** 커밋 금지 준수
- ✅ semantic 재해석 금지: 단위 변환만 수행 (의미 매핑 금지)

## DoD 체크리스트

### Round31 실행 전 (현재 PR)
- [x] 2단 OBJ 로더 추가 (trimesh 옵션 + pure Python parser 필수)
- [x] skip_reasons.jsonl 레코드에 loader_name, loaded_verts, loaded_faces 필드 추가
- [x] 로드 실패 시 exception_type, exception_1line 기록
- [x] proxy 5개 케이스는 attempted_load=True 유지
- [x] reports/validation/INDEX.md 업데이트 (Round31 항목)
- [x] docs/ops/INDEX.md 업데이트 (Round Registry)
- [x] 커밋 및 푸시 완료

### Round31 실행 후 (후속 PR 예정)
- [ ] Round31 실행 (위 커맨드)
- [ ] 산출물 점검 (KPI.md, KPI_DIFF.md, lineage/manifest, PROMPT_SNAPSHOT.md, artifacts/skip_reasons.jsonl)
- [ ] processed/skipped 수치 확인 (목표: processed>=5)
- [ ] reports/validation/geo_v0_s1_facts_round31.md 생성
- [ ] 커밋: "validation: round31 geo v0 S1 facts + postprocess closure"

## DoD Self-check (facts-only)

**주의**: 아래는 "존재/경로/관측값"으로만 기입 (판정 금지).

### 1) Proxy 5개 레코드 진단 정보 (5줄)
```
[실행 후 skip_reasons.jsonl에서 proxy 5개 케이스 레코드의 loader_name, mesh_exists, loaded_verts/loaded_faces 또는 exception_1line 출력 5줄 복사]
```

### 2) Skip Reasons 레코드 로더 필드 확인
- [ ] 각 레코드에 다음 필드 존재 (load_failed인 경우):
  - loader_name: "trimesh" 또는 "fallback_obj_parser"
  - exception_type: 예외 타입 (예: FileNotFoundError, ValueError)
  - exception_1line: 예외 메시지 1줄 (빈 문자열이면 repr(e))
- [ ] 성공 케이스 (있는 경우):
  - loaded_verts: 로드된 정점 수
  - loaded_faces: 로드된 면 수 (optional)

### 3) Round31 실행 결과 (facts-only)
- [ ] processed cases: [실행 후 기록] (목표: >=5)
- [ ] skipped cases: [실행 후 기록]
- [ ] processed >= 5 여부: [실행 후 기록] (목표: processed>=5 복구)

### 4) Postprocess 산출물 생성 확인
- [ ] `KPI.md` exists
- [ ] `KPI_DIFF.md` exists (상단 경고 라인 존재 여부: [실행 후 기록])
- [ ] `lineage/manifest` 또는 `LINEAGE.md` exists
- [ ] `PROMPT_SNAPSHOT.md` exists

### 5) Proxy 슬롯 5개 attempted_load 확인
- [ ] proxy 슬롯 5개 (311610164126, 20_F_1049, 121607160426, 21_F_4430, 511609194879)의 attempted_load가 모두 True
  - attempted_load=True 레코드 수: [실행 후 기록]

### 6) Loader 사용 확인
- [ ] proxy 5개 레코드에서 loader_name이 "trimesh" 또는 "fallback_obj_parser"로 기록됨
  - trimesh 사용: [실행 후 기록]
  - fallback_obj_parser 사용: [실행 후 기록]

## 스모크 테스트

### Skip Reasons 로더 필드 확인
```bash
# skip_reasons.jsonl에서 proxy 5개 레코드의 로더 필드 확인
py -c "import json; f = open('verification/runs/facts/geo_v0_s1/round31_*/artifacts/skip_reasons.jsonl'); lines = [json.loads(l) for l in f if l.strip()]; proxy_cases = ['311610164126', '20_F_1049', '121607160426', '21_F_4430', '511609194879']; proxy_records = [r for r in lines if r['case_id'] in proxy_cases]; print(f'Proxy records: {len(proxy_records)}'); print(f'All have loader_name: {all(\"loader_name\" in r for r in proxy_records)}'); print(f'Loader names: {[r.get(\"loader_name\") for r in proxy_records]}')"
# 예상: Proxy records: 5, All have loader_name: True, Loader names: ['trimesh' or 'fallback_obj_parser']
```

### 링크 유효성 확인
- [x] `reports/validation/INDEX.md`에서 Round31 링크 유효성 확인
- [x] `docs/ops/INDEX.md`에서 Round Registry 링크 유효성 확인

## 롤백

```bash
git revert HEAD~1 HEAD
```

또는 브랜치 삭제:
```bash
git branch -D validation/round31-s1-loader-fallback-and-exceptions
git push origin --delete validation/round31-s1-loader-fallback-and-exceptions
```
