# Round21 실행 가이드

## Round21 실행 명령

아래 명령을 실행하세요 (줄바꿈은 \ 컨벤션):

```bash
RUN_DIR="verification/runs/facts/curated_v0/round21_$(date +%Y%m%d_%H%M%S)" \
make curated_v0_round \
RUN_DIR="$RUN_DIR"
```

## 실행 후 확인 사항

### 1. 산출물 점검 (라운드 완료 조건)

RUN_DIR에 다음 파일들이 존재해야 합니다:

- [ ] `KPI.md` - KPI 요약
- [ ] `KPI_DIFF.md` - KPI 차이 (prev/baseline 비교)
- [ ] `lineage/manifest` 또는 `LINEAGE.md` - Lineage 정보
- [ ] `PROMPT_SNAPSHOT.md` - 프롬프트 스냅샷
- [ ] `artifacts/visual/` 또는 `SKIPPED.txt` - Visual proxy 또는 SKIPPED 기록

### 2. prev/baseline 자동추론 확인

- [ ] prev_run_dir 자동 추론이 정상 동작했는지 확인 (경고만 표면화, 빌드 깨지지 않게)
- [ ] prev==baseline인 경우 KPI_DIFF가 0으로 수렴하는 것이 정상임을 확인

### 3. coverage_backlog 확인

- [ ] `reports/validation/coverage_backlog.md`가 업데이트되었는지 확인
- [ ] 신규 항목에 추적 태그(`[Round21]` 또는 `run_dir=...` 또는 `ts=...`)가 추가되었는지 확인

### 4. Visual Proxy 확인

- [ ] measurement-only NPZ인 경우 `SKIPPED.txt` 또는 `README.md`에 다음 사유가 명시되었는지 확인:
  ```
  Reason: measurement-only NPZ (No verts available)
  ```

## 실행 후 다음 단계

1. Gate 문서 업데이트 (Round21 facts_summary 기반으로 수치 보완)
2. reports/validation/curated_v0_facts_round21.md 생성 (Round21 facts_summary 기반)
3. 커밋 및 PR 생성
