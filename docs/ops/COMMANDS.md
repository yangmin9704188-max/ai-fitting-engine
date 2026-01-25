# 공식 단축 명령 목록

이 문서는 AI Fitting Engine 프로젝트에서 사용 가능한 공식 단축 명령들을 정리합니다.

## 기본 명령

### sync-dry
**목적**: Sync state를 dry-run 모드로 실행하여 변경 사항을 미리 확인

**기본 사용법**:
```bash
make sync-dry ARGS="--set snapshot.status=candidate"
```

**예시**:
```bash
make sync-dry ARGS="--set snapshot.status=candidate"
```

### sync
**목적**: Sync state를 실행하여 상태를 업데이트

**기본 사용법**:
```bash
make sync ARGS="--set last_update.trigger=manual_test"
```

**예시**:
```bash
make sync ARGS="--set snapshot.status=hold --set last_update.trigger=test"
```

### ai-prompt
**목적**: AI 프롬프트를 렌더링하여 출력

**기본 사용법**:
```bash
make ai-prompt
```

**예시**:
```bash
make ai-prompt
```

### ai-prompt-json
**목적**: AI 프롬프트를 JSON 형식으로 렌더링하여 출력

**기본 사용법**:
```bash
make ai-prompt-json
```

**예시**:
```bash
make ai-prompt-json
```

### curated_v0_round
**목적**: Curated v0 라운드를 실행 (runner + postprocess)

**기본 사용법**:
```bash
make curated_v0_round RUN_DIR=<out_dir> [SKIP_RUNNER=1]
```

**예시**:
```bash
make curated_v0_round RUN_DIR=verification/runs/facts/curated_v0/round20_20260125_164801
make curated_v0_round RUN_DIR=verification/runs/facts/curated_v0/round20_20260125_164801 SKIP_RUNNER=1
```

### ops_guard
**목적**: Ops lock 경고 센서 실행

**기본 사용법**:
```bash
make ops_guard [BASE=main]
```

**예시**:
```bash
make ops_guard
```

## Round Ops Shortcuts

### postprocess
**목적**: 라운드 실행 결과에 대한 후처리 실행 (KPI/DIFF/CHARTER 생성)

**기본 사용법**:
```bash
make postprocess RUN_DIR=<dir>
```

**예시**:
```bash
make postprocess RUN_DIR=verification/runs/facts/curated_v0/round20_20260125_164801
```

### postprocess-baseline
**목적**: Baseline run directory에 대한 후처리 실행 (BASELINE_RUN_DIR 사용)

**기본 사용법**:
```bash
make postprocess-baseline
```

**예시**:
```bash
make postprocess-baseline
```

### curated_v0_baseline
**목적**: Baseline에 대한 curated_v0 라운드 실행 (runner 스킵, postprocess만)

**기본 사용법**:
```bash
make curated_v0_baseline
```

**예시**:
```bash
make curated_v0_baseline
```

### golden-apply
**목적**: Golden registry에 패치 적용

**기본 사용법**:
```bash
make golden-apply PATCH=<patch.json> [FORCE=1]
```

**예시**:
```bash
make golden-apply PATCH=verification/runs/facts/curated_v0/round20_20260125_164801/CANDIDATES/GOLDEN_REGISTRY_PATCH.json
make golden-apply PATCH=<path> FORCE=1
```

### judgment
**목적**: 라운드 실행 결과에서 judgment 문서 생성 (스캐폴딩)

**기본 사용법**:
```bash
make judgment FROM_RUN=<run_dir> [OUT_DIR=docs/judgments] [SLUG=...] [DRY_RUN=1]
```

**예시**:
```bash
make judgment FROM_RUN=verification/runs/facts/curated_v0/round20_20260125_164801
make judgment FROM_RUN=<run_dir> DRY_RUN=1 SLUG=smoke
```

## 기본 변수

다음 변수들은 Makefile에서 기본값으로 설정되어 있으며, 필요시 오버라이드할 수 있습니다:

- `BASELINE_RUN_DIR`: 기본값 `verification/runs/facts/curated_v0/round20_20260125_164801`
- `GOLDEN_REGISTRY`: 기본값 `docs/verification/golden_registry.json`

**예시**:
```bash
make postprocess-baseline BASELINE_RUN_DIR=verification/runs/facts/curated_v0/round21_20260126_120000
```
