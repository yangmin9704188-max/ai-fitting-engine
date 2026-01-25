# 공식 단축 명령 목록

이 문서는 AI Fitting Engine 프로젝트에서 사용 가능한 공식 단축 명령들을 정리합니다.
이 문서는 `make commands-update` 명령으로 자동 생성됩니다.

## Overview

Makefile을 통해 제공되는 단축 명령들입니다. 각 명령의 목적, 사용법, 예시를 확인할 수 있습니다.

## Quick Recipes

자주 사용하는 조합 명령들입니다.

## 기본 변수

다음 변수들은 Makefile에서 기본값으로 설정되어 있으며, 필요시 오버라이드할 수 있습니다:

- `BASELINE_RUN_DIR`: 기본값 `verification/runs/facts/curated_v0/round20_20260125_164801`
- `GOLDEN_REGISTRY`: 기본값 `docs/verification/golden_registry.json`

**예시**:
```bash
make postprocess-baseline BASELINE_RUN_DIR=verification/runs/facts/curated_v0/round21_20260126_120000
```
