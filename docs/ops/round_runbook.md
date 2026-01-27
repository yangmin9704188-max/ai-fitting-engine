# Round Runbook

> **라운드 기록 규칙**: 라운드 기록은 `docs/ops/rounds/roundXX.md`로만 추가합니다.

## Round 실행 최소 명령

### curated_v0 facts round 실행

```bash
# 1. Runner 실행 + Postprocess (자동)
make curated_v0_round RUN_DIR=verification/runs/facts/curated_v0/round20_$(date +%Y%m%d_%H%M%S)

# 2. Postprocess만 실행 (runner 스킵)
make curated_v0_round RUN_DIR=verification/runs/facts/curated_v0/round20_20260125_164801 SKIP_RUNNER=1
```

**참고:**
- `RUN_DIR`이 없으면 에러 메시지 출력 후 종료
- `facts_summary.json`이 이미 존재하면 runner는 자동으로 스킵됨
- Postprocess는 항상 실행됨 (runner 성공/실패와 무관)
