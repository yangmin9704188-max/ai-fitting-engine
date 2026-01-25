# ops: ignore local-only geo_v0 test reports and add local artifacts folder

## 목적
기준선/공식 리포트는 유지하고, 테스트로 생성된 untracked 리포트는 로컬 전용으로 격리하여, 이후 루트/리포트 폴더가 더럽혀지지 않게 만듭니다.

## 구현 범위

### 1. 공식 리포트 기준 확인
다음 문서에서 공식 리포트 기준을 확인했습니다:
- `reports/validation/INDEX.md`: 공식 리포트 파일명 명시
- `docs/verification/golden_s0_freeze_v0.md`: 기준선 리포트 명시
- `docs/verification/round_registry.json`: 등록된 공식 리포트

**공식 리포트 (커밋 대상, 유지):**
- `reports/validation/geo_v0_facts_round13_fastmode_normal1_runner.md`
- `reports/validation/geo_v0_facts_round15_bust_verts_aligned_normal1.md`
- `reports/validation/geo_v0_facts_round16_waist_hip_verts_aligned_normal1.md`
- `reports/validation/geo_v0_facts_round17_valid10_expanded.md` (기준선)
- `reports/validation/curated_v0_facts_round1.md` (round20 기준선)

### 2. 로컬 전용 격리 폴더 생성
- `verification/local_artifacts/` 폴더 생성
- `verification/local_artifacts/README.md` 추가 (로컬 산출물 보관 규칙 문서화)

### 3. .gitignore 업데이트
- `verification/local_artifacts/` 추가 (README.md는 예외)
- 로컬 테스트 리포트 구체 파일명 추가 (9개):
  - `reports/validation/geo_v0_facts_round2.md`
  - `reports/validation/geo_v0_facts_round3_waist_hip_fix.md`
  - `reports/validation/geo_v0_facts_round4_waist_hip_fix.md`
  - `reports/validation/geo_v0_facts_round5_waist_hip_fallback_working.md`
  - `reports/validation/geo_v0_facts_round6_s0_humanlike.md`
  - `reports/validation/geo_v0_facts_round7_slice_shared.md`
  - `reports/validation/geo_v0_facts_round8_height_debug.md`
  - `reports/validation/geo_v0_facts_round9_s0_scale_fix.md`
  - `reports/validation/geo_v0_facts_round10_s0_scale_proof.md`
- 임시 파일 패턴 추가: `*.xls`, `*.xlsx`

### 4. 테스트 리포트 이동
- untracked 테스트 리포트를 `verification/local_artifacts/reports_validation_geo_v0/`로 이동
- (커밋에는 포함되지 않음, 로컬 전용)

## 변경 파일 목록

**신규 파일 (1개):**
- `verification/local_artifacts/README.md`

**수정 파일 (1개):**
- `.gitignore`

## 왜 와일드카드가 아니라 파일명 단위 ignore인가?

와일드카드(`geo_v0_facts_round*.md`)를 사용하면 향후 "공식 고정 파일명"까지 ignore될 수 있습니다.
예를 들어, 향후 `geo_v0_facts_round21_baseline.md` 같은 공식 리포트가 생길 수 있는데, 와일드카드를 사용하면 이것까지 ignore되어 버립니다.

따라서 현재 untracked로 확인된 테스트 리포트만 구체 파일명으로 ignore 처리했습니다.

## 금지사항 준수 확인
- ✅ no deletions: git rm 없음 (tracked 파일 삭제 없음)
- ✅ no moves: core/, pipelines/, verification/, tests/ 이동 없음 (untracked 파일만 이동)
- ✅ no code logic changes: 기존 runner/측정 로직 의미 변경 없음
- ✅ no PASS/FAIL 판정: facts-only 유지

## 정리 결과

### git status 확인
```
Changes to be committed:
  modified:   .gitignore
  new file:   verification/local_artifacts/README.md
```

### git diff --stat 확인
```
 .gitignore | 16 ++++++++++++++++
 1 file changed, 16 insertions(+)
```

✅ 테스트 리포트 untracked가 사라지고, 변경사항이 .gitignore + README 중심임을 확인

## 참고

- 루트에 파일 추가하지 않음 (verification/local_artifacts/ 안에서만 해결)
- 공식 리포트는 유지 (레지스트리/INDEX 기준)
- 로컬 테스트 산출물은 gitignored로 격리
