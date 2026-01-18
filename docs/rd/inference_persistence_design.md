---
Level: L2
Change Rule: Free
Scope: R&D
---

# Inference Persistence Design

## 설계 요약

`core/persistence/inference_persister.py`는 Constitution v1 헌법을 코드로 강제하는 자동 적재 루틴입니다.

### 핵심 원칙 (헌법 준수)

1. **Snapshot First**: snapshot_id로 조회 → 없으면 즉시 예외 (무버전 패치 방지)
2. **단일 트랜잭션**: InferenceRun → GateResult → Telemetry → DeliveryArtifact 순서 고정
3. **버전 키 파생**: Snapshot 조회 결과에서 code_git_sha, schema_version, model_version 자동 파생
4. **UUID DB 생성**: pgcrypto.gen_random_uuid() 사용 (Python UUID 생성 금지)
5. **Telemetry 필수 필드**: egress_bytes, pure_inference_cost_usd, latency_ms, uncertainty_score, delivery_mode 검증

---

## 트랜잭션 순서 및 근거

### 순서: InferenceRun → GateResult → Telemetry → DeliveryArtifact

**왜 이 순서인가?**

1. **InferenceRun (최상위)**: 
   - 모든 결과의 루트 엔터티
   - inference_run_id는 이후 모든 INSERT의 FK
   - DB에서 UUID 자동 생성 (RETURNING 절 사용)

2. **GateResult (1:1):**
   - InferenceRun에 대한 해석 결과
   - Gate 로직 변경 시 재생성 가능하므로 InferenceRun 바로 다음에 위치
   - 헌법상 "GateResult 없는 InferenceRun" 금지 → 즉시 INSERT

3. **Telemetry (1:1):**
   - InferenceRun의 측정 데이터
   - 버전 키는 Snapshot에서 파생 (코드에서 직접 받지 않음)
   - 필수 필드 누락 시 예외 (헌법 위반)

4. **DeliveryArtifact (1:N):**
   - 실제 전달된 산출물 (이미지, 파라미터 등)
   - 0개일 수 있으므로 마지막에 위치
   - 실패 시에도 앞선 3개는 롤백되지 않도록 순서 고정

---

## 헌법 강제 메커니즘

### 1. Snapshot First (코드 강제)

```python
def _fetch_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
    # Snapshot 조회
    row = cur.fetchone()
    if row is None:
        raise ConstitutionViolationError(
            "Snapshot must exist before inference run."
        )
    return snapshot
```

**강제 효과:**
- Python 코드에서 Snapshot 생성 불가 (DB 조회만 가능)
- snapshot_id 없이 run 생성 불가
- 없으면 즉시 예외 → 무버전 패치 방지

### 2. 버전 키 파생 규칙 (코드 강제)

```python
# ❌ 금지: 함수 인자로 직접 받기
# def persist_inference(..., code_git_sha, schema_version, model_version)

# ✅ 허용: Snapshot에서 파생
snapshot = self._fetch_snapshot(snapshot_id)
code_git_sha = snapshot['code_git_sha']  # Snapshot에서 추출
```

**강제 효과:**
- 버전 키 불일치 불가능 (Snapshot 단일 소스)
- "나중에 업데이트" 패턴 불가 (무버전 패치 위반)

### 3. 단일 트랜잭션 (코드 강제)

```python
try:
    # InferenceRun INSERT
    # GateResult INSERT
    # Telemetry INSERT
    # DeliveryArtifact INSERT
    conn.commit()  # 모두 성공 시에만 커밋
except:
    conn.rollback()  # 중간 실패 시 전체 롤백
    raise
```

**강제 효과:**
- 부분 저장 불가능
- InferenceRun만 저장되고 GateResult 없는 상태 불가
- 일관성 보장

### 4. Telemetry 필수 필드 검증 (코드 강제)

```python
def _validate_telemetry_fields(self, telemetry_data: Dict[str, Any]):
    required = ['egress_bytes', 'pure_inference_cost_usd', ...]
    missing = [k for k in required if k not in telemetry_data]
    if missing:
        raise ConstitutionViolationError(...)
```

**강제 효과:**
- 필수 필드 누락 시 즉시 실패
- "나중에 채우기" 불가

### 5. UUID DB 생성 (SQL 강제)

```sql
-- InferenceRun INSERT 시 UUID 자동 생성
INSERT INTO inference_run (...) 
VALUES (...)
RETURNING inference_run_id  -- DB에서 생성된 UUID 반환
```

**강제 효과:**
- Python에서 UUID 생성 불가
- pgcrypto.gen_random_uuid() 사용 강제 (DB 레벨)

---

## 실패 시나리오 처리

### 1. Snapshot 없음

```python
snapshot = self._fetch_snapshot(snapshot_id)  # → ConstitutionViolationError
```

**동작:**
- 즉시 예외 발생
- 트랜잭션 시작 전 실패 → 롤백 불필요

### 2. Gate FAIL

```python
gate_results = [
    {"gate_type": "GEO", "passed": False, "failure_code": "GEO_FAIL"}
]
```

**동작:**
- GateResult는 INSERT됨 (실패도 기록)
- InferenceRun은 정상 저장 (실패는 GateResult에 기록)
- Telemetry, DeliveryArtifact도 정상 저장

### 3. Telemetry 필수 필드 누락

```python
telemetry_data = {"latency_ms": 100}  # egress_bytes 누락
self._validate_telemetry_fields(telemetry_data)  # → ConstitutionViolationError
```

**동작:**
- 검증 단계에서 즉시 예외 발생
- 트랜잭션 시작 전 실패 → 롤백 불필요

### 4. DB 오류 (중간 단계)

```python
# InferenceRun INSERT 성공
# GateResult INSERT 실패 (예: FK 제약 위반)
```

**동작:**
- psycopg2.Error 발생
- conn.rollback() → 전체 롤백
- InferenceRun도 롤백 (부분 저장 방지)

---

## 헌법 준수 검증 질문

### ✅ "이 실행은 어느 스냅샷의 결과인가?"

**답:** `inference_run.snapshot_id` FK로 명확히 연결

```sql
SELECT inference_run_id, snapshot_id FROM inference_run WHERE ...
```

### ✅ "이 비용은 어떤 코드/모델/스키마에서 발생했는가?"

**답:** Telemetry 테이블에 버전 키 저장 (Snapshot에서 파생)

```sql
SELECT 
    telemetry.inference_run_id,
    telemetry.code_git_sha,
    telemetry.schema_version,
    telemetry.model_version
FROM telemetry
WHERE inference_run_id = ...
```

### ✅ "나중에 이 결과를 재현할 수 있는가?"

**답:** Snapshot 조회 → 버전 키 추출 → 동일 코드/모델/스키마로 재실행 가능

```sql
SELECT * FROM snapshot WHERE snapshot_id = (
    SELECT snapshot_id FROM inference_run WHERE inference_run_id = ...
)
```

### ✅ "JOIN 1~2번으로 정산 리포트가 나오는가?"

**답:** Snapshot → InferenceRun → Telemetry JOIN 1~2번으로 가능

```sql
-- Snapshot별 평균 비용
SELECT 
    s.snapshot_id,
    AVG(t.pure_inference_cost_usd) as avg_cost,
    AVG(t.latency_ms) as avg_latency,
    AVG(t.egress_bytes) as avg_egress
FROM snapshot s
JOIN inference_run ir ON ir.snapshot_id = s.snapshot_id
JOIN telemetry t ON t.inference_run_id = ir.inference_run_id
GROUP BY s.snapshot_id
```

---

## 구현 세부사항

### PostgreSQL 연결

- `psycopg2` 사용 (SQL 직접 제어)
- `RealDictCursor` 사용 (컬럼명으로 접근)
- `execute_values` 사용 (배치 INSERT, GateResult/DeliveryArtifact)

### 트랜잭션 경계

- `autocommit=False` (기본값)
- `conn.commit()` 명시적 호출
- 예외 시 `conn.rollback()` 호출

### 예외 계층

1. `ConstitutionViolationError`: 헌법 위반 (복구 불가)
2. `psycopg2.Error`: DB 오류 (롤백 필요)
3. `RuntimeError`: 기타 예외 (롤백 필요)

---

## 사용법

```python
from core.persistence import InferencePersister, ConstitutionViolationError

persister = InferencePersister("postgresql://user:pass@localhost/dbname")

try:
    inference_run_id = persister.persist_inference(
        snapshot_id="550e8400-e29b-41d4-a716-446655440000",
        inference_input={"gender": "male", ...},
        inference_result={"shoulder_width_m": 0.42, ...},
        gate_results=[
            {"gate_type": "GEO", "passed": True, ...},
            {"gate_type": "PROC", "passed": True, ...}
        ],
        telemetry_data={
            "latency_ms": 1520,
            "egress_bytes": 245760,
            "pure_inference_cost_usd": 0.0012,
            "uncertainty_score": 0.05,
            "delivery_mode": "IMAGE"
        },
        delivery_artifacts=[
            {"artifact_type": "RENDERED_IMAGE", "storage_path": "...", "size_bytes": 245760}
        ]
    )
    print(f"Persisted: {inference_run_id}")
    
except ConstitutionViolationError as e:
    print(f"헌법 위반: {e}")
finally:
    persister.close()
```
