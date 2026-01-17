# Evidence Packer CLI

## Overview

`tools/pack_evidence.py`는 로컬 실험 결과를 Evidence Package schema v1.0에 맞춰 자동으로 패키징하는 CLI 도구입니다.

## When to Use

로컬 GPU(예: RTX 4070 Super)에서 실험을 실행한 후, 측정된 수치 값만 입력하면 표준 Evidence Package를 생성합니다. 생성된 패키지를 PR로 올리면 GitHub Actions의 `evidence-check` 워크플로우가 자동으로 스키마 검증을 수행합니다.

## Basic Usage Examples

### Example 1: Basic Package

```bash
python tools/pack_evidence.py \
  --task shoulder_width \
  --policy_version v1.2 \
  --run_id 20260118_120000 \
  --primary_value 5.8 \
  --baseline_ref tags/shoulder_width_v1.1 \
  --baseline_primary_value 5.7
```

### Example 2: With Secondary Metrics

```bash
python tools/pack_evidence.py \
  --task shoulder_width \
  --policy_version v1.2 \
  --run_id 20260118_120000 \
  --primary_value 5.8 \
  --baseline_ref tags/shoulder_width_v1.1 \
  --baseline_primary_value 5.7 \
  --secondary fail_rate=0.02:ratio \
  --secondary p95_abs_err_mm=14.2:mm
```

## Generated Files and Folder Structure

실행 시 다음 폴더와 파일이 생성됩니다:

```
artifacts/<task>/<policy_version>/runs/<run_id>/
  manifest.json
  metrics.json
  summary.md
```

**예시:**
```
artifacts/shoulder_width/v1.2/runs/20260118_120000/
  manifest.json    # 메타데이터, git 정보, baseline 참조
  metrics.json     # 측정 결과, 회귀 분석 (delta, delta_pct)
  summary.md       # 인간 판독용 요약 (30줄 이내)
```

## CI Validation (evidence-check)

PR에 Evidence Package가 포함되면 GitHub Actions의 `evidence-check` 워크플로우가 자동으로:

1. **스키마 검증**: manifest.json/metrics.json의 schema_version 및 필수 키 확인
2. **회귀 검증**: primary metric의 delta/delta_pct가 허용 범위 내인지 확인 (abs(delta) <= 0.3, abs(delta_pct) <= 5)
3. **fail_rate 검증**: secondary metric 중 fail_rate가 0.05 이하인지 확인

검증 실패 시 PR이 블록되며, 성공 시 PASS 상태로 표시됩니다.

## Command Line Arguments

### Required

- `--task`: Task 이름 (예: `shoulder_width`)
- `--policy_version`: Policy 버전 (예: `v1.2`)
- `--run_id`: Run ID (예: `20260118_120000`)
- `--primary_value`: Primary metric 값 (float)
- `--baseline_ref`: Baseline 참조 (예: `tags/v1.1`)
- `--baseline_primary_value`: Baseline primary metric 값 (float)

### Optional

- `--primary_name`: Primary metric 이름 (default: `mae`)
- `--primary_unit`: Primary metric 단위 (default: `cm`)
- `--secondary`: Secondary metric (형식: `KEY=VALUE:UNIT`, 반복 가능)
- `--dataset_id`, `--dataset_version`, `--split`: 데이터셋 정보
- `--experiment_name`, `--description`, `--seed`: 실험 설정
- `--host`, `--gpu`: 실행 환경 정보 (default: auto-detect)

자세한 옵션은 `python tools/pack_evidence.py --help`로 확인하세요.
