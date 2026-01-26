# curated_v0 Real-data Gate v0 (Facts-only Sensors)

**목적**: PASS/FAIL이 아니라 "facts 신호 → 다음 행동" 맵핑을 정의합니다.

**주의**: 이 문서는 판정(PASS/FAIL)을 포함하지 않습니다. 오직 경고 신호와 권장 행동만을 매핑합니다.

---

## Baseline Reference

- **Baseline Round**: Round 20
- **Baseline Report**: [reports/validation/curated_v0_facts_round1.md](../../reports/validation/curated_v0_facts_round1.md)
- **Baseline Run Dir**: `verification/runs/facts/curated_v0/round20_20260125_164801`
- **Baseline Tag (alias)**: `curated-v0-realdata-v0.1`

---

## NaN Rate 경고 트리거 (판정 아님)

Round20/21 facts_summary 분포를 기반으로 한 경고 트리거 구간:

| NaN Rate 구간 | 경고 트리거 | 권장 행동 |
|--------------|------------|----------|
| 0% | 정상 범위 | Ignore (documented) |
| 0% < NaN ≤ 30% | 부분 결측 | Manual Investigation (원인 파악) |
| 30% < NaN ≤ 70% | 높은 결측률 | Manual Investigation (데이터 소스 확인) |
| 70% < NaN < 100% | 매우 높은 결측률 | Manual Investigation (매핑/추출 로직 점검) |
| 100% | All-null | Backlog Register (coverage_backlog.md에 기록) |

**근거 (Round20 facts)**:
- CHEST_CIRC_M_REF: NaN 71.0% (142/200) → Manual Investigation
- UNDERBUST_CIRC_M: NaN 45.0% (90/200) → Manual Investigation
- BELOW_KNEE_CIRC_M, MID_THIGH_CIRC_M, NAVEL_WAIST_DEPTH_M, NAVEL_WAIST_WIDTH_M: NaN 30.5% (61/200) → Manual Investigation
- NECK_DEPTH_M, NECK_WIDTH_M, TOP_HIP_CIRC_M, UNDERBUST_DEPTH_M, UNDERBUST_WIDTH_M, UPPER_HIP_CIRC_M: NaN 100% → Backlog Register

---

## 핵심 키 범위 경고 트리거 (판정 아님)

Round20 분포를 기반으로 한 합리적 범위 경고:

| Key | Round20 Median | 경고 트리거 범위 | 권장 행동 |
|-----|---------------|----------------|----------|
| HEIGHT_M | 1.6555 m | < 1.20 m 또는 > 2.20 m | Manual Investigation |
| BUST_CIRC_M | 0.9050 m | < 0.40 m 또는 > 1.80 m | Manual Investigation |
| WAIST_CIRC_M | 0.7935 m | < 0.40 m 또는 > 1.80 m | Manual Investigation |
| HIP_CIRC_M | 0.9535 m | < 0.40 m 또는 > 1.80 m | Manual Investigation |
| NECK_CIRC_M | 0.3430 m | < 0.08 m 또는 > 1.60 m | Manual Investigation |

**주의**: 이 범위는 "의심 신호"만 제공하며, 자동 FAIL 판정에는 사용하지 않습니다.

---

## Facts 신호 → 다음 행동 매핑

| 신호 패턴 | 경고 트리거 | 다음 행동 |
|---------|-----------|----------|
| NaN = 100% (all-null) | All-null 키 감지 | Backlog Register (coverage_backlog.md에 기록) |
| NaN > 70% & reason=VALUE_MISSING | 높은 결측률 + 값 누락 | Manual Investigation (데이터 소스/매핑 확인) |
| NaN 30-70% & reason=VALUE_MISSING | 중간 결측률 | Manual Investigation (원인 파악) |
| NaN < 30% & reason=VALUE_MISSING | 낮은 결측률 | Ignore (documented) |
| Suspicious scale (10x/100x 패턴) | 단위 오류 의심 | Manual Investigation (단위 메타데이터 검증) |
| 범위 이탈 (경고 트리거 범위 밖) | 합리적 범위 밖 값 | Manual Investigation (스케일/단위 확인) |
| 정상 범위 (NaN 0%, 범위 내) | 정상 관측 | Ignore (documented) |

---

## Action 정의

### 1) Manual Investigation
- 데이터 소스 확인 (curated_v0 파이프라인 입력/출력)
- 매핑/추출 로직 점검 (sizekorea_v2.json, build_curated_v0.py)
- 단위 메타데이터 검증 (unit canonicalization 로직)
- 원인 파악 후 문서화 (사실 기록만, 판정 금지)

### 2) Ignore (documented)
- 정상 범위 내 관측치
- 문서에 "정상 범위"로 기록
- 추가 조치 불필요

### 3) Backlog Register
- NaN 100% 키를 `reports/validation/coverage_backlog.md`에 기록
- 판정/추측 없이 누적만 수행
- 측정 로직 수정 대상으로 분류하지 않음

---

## Round21 실행 정보

**재현 커맨드**:
```bash
RUN_DIR="verification/runs/facts/curated_v0/round21_$(date +%Y%m%d_%H%M%S)" \
make curated_v0_round \
RUN_DIR="$RUN_DIR"
```

**입력 NPZ**: `verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz` (Round20과 동일)

**prev_run_dir 선택 기준**:
- 같은 lane(curated_v0)에서 시간상 가장 최근 run_dir
- 경로가 `verification/runs/facts/curated_v0/round*_YYYYMMDD_HHMMSS` 형태
- postprocess 산출물(KPI.md 또는 lineage/manifest 등) 존재로 run_dir임이 확인됨
- prev가 없으면 baseline_run_dir로 fallback (경고만)
- **prev==baseline이면 KPI_DIFF가 0으로 수렴하는 것은 정상임** (비교 오염 방지)

---

## Visual Proxy 정책

- **best-effort**: 실패 시 warning 기록하되 DoD/완료를 차단하지 않음
- **measurement-only NPZ (verts 없음)**: 
  - `artifacts/visual/` 생성
  - `SKIPPED.txt` 또는 `README.md`에 사유 명시:
    ```
    Reason: measurement-only NPZ (No verts available)
    ```

---

## Coverage Backlog 추적

- **경로 고정**: `reports/validation/coverage_backlog.md`
- **NaN 100% 키만 누적** (slim rule)
- **신규 항목 누적 시 행 끝에 추적 태그**: `[Round21]` 또는 `run_dir=...` 또는 `ts=...`

---

## 참고

- **Gate Draft**: [docs/verification/curated_v0_gate_draft_v0.md](../../verification/curated_v0_gate_draft_v0.md)
- **Baseline Report**: [reports/validation/curated_v0_facts_round1.md](../../reports/validation/curated_v0_facts_round1.md)
- **Coverage Backlog**: [reports/validation/coverage_backlog.md](../../reports/validation/coverage_backlog.md)
