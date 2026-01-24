# Geometric v0 Facts-Only Summary (Round 1)

## 1. 실행 조건

- **샘플 수**: (실행 후 업데이트 필요)
- **입력 데이터셋**: `verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz`
- **Git SHA**: (실행 후 업데이트 필요)
- **실행 일시**: (실행 후 업데이트 필요)

**참고**: 이 리포트는 템플릿입니다. 실제 리포트를 생성하려면 다음 명령을 실행하세요:

```bash
# 1. 데이터셋 생성
python verification/datasets/golden/core_measurements_v0/create_s0_dataset.py

# 2. Facts runner 실행
python verification/runners/run_geo_v0_facts_round1.py \
  --npz verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz \
  --n_samples 20 \
  --out_dir verification/runs/facts/geo_v0/round1_$(date +%Y%m%d_%H%M%S)
```

## 2. Key별 요약

| Key | Total | NaN | NaN Rate | Min | Median | Max |
|-----|-------|-----|----------|-----|--------|-----|
| (실행 후 업데이트 필요) |

## 3. Warnings Top 리스트

### 3.1 전체 Warnings Top 10

| Warning Type | Count |
|--------------|-------|
| (실행 후 업데이트 필요) |

### 3.2 Key별 Warnings Top 5

(실행 후 업데이트 필요)

## 4. Proxy/Band Scan/Side 기록 통계

### 4.1 Proxy 사용

| Key | Proxy Used Count | Proxy Types |
|-----|------------------|-------------|
| (실행 후 업데이트 필요) |

### 4.2 Band Scan 사용

| Key | Band Scan Used Count | Band Scan Limits |
|-----|----------------------|------------------|
| (실행 후 업데이트 필요) |

### 4.3 Canonical Side 기록

| Key | Canonical Sides |
|-----|-----------------|
| (실행 후 업데이트 필요) |

### 4.4 Pose Unknown 비율

| Key | Breath State Unknown | Arms Down Unknown | Strict Standing Unknown | Knee Flexion Unknown |
|-----|----------------------|-------------------|------------------------|----------------------|
| (실행 후 업데이트 필요) |

## 5. 이슈 분류

### GEO_BUG

- (실행 후 업데이트 필요)

### POSE/PROXY

- (실행 후 업데이트 필요)

### COVERAGE/UNKNOWN

- (실행 후 업데이트 필요)
