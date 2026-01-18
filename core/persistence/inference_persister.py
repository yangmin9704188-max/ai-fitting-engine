"""
Inference Persister: Constitution v1 Compliant

헌법 준수 원칙:
1. Snapshot First: snapshot_id로 조회, 없으면 즉시 예외
2. 단일 트랜잭션: InferenceRun → GateResult → Telemetry → DeliveryArtifact
3. 버전 키 파생: Snapshot에서 code_git_sha, schema_version, model_version 파생
4. UUID는 DB에서 생성 (pgcrypto.gen_random_uuid())
5. Telemetry 필수 필드 검증
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from psycopg2 import sql


class ConstitutionViolationError(Exception):
    """헌법 위반 예외: 복구 불가능한 오류"""
    pass


class InferencePersister:
    """
    Inference 결과를 PostgreSQL에 헌법 준수 방식으로 적재.
    
    트랜잭션 순서:
    1. Snapshot 조회 (없으면 ConstitutionViolationError)
    2. InferenceRun INSERT (UUID는 DB 생성)
    3. GateResult INSERT (각 Gate마다 1 row)
    4. Telemetry INSERT (최소 1 row)
    5. DeliveryArtifact INSERT (0~N rows)
    """
    
    def __init__(self, db_connection_string: str):
        """
        Args:
            db_connection_string: PostgreSQL connection string
                예: "postgresql://user:pass@host:5432/dbname"
        """
        self.conn_string = db_connection_string
        self._conn = None
    
    def _get_connection(self):
        """트랜잭션용 연결 반환"""
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self.conn_string)
        return self._conn
    
    def _fetch_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """
        🔒 Snapshot First: snapshot_id로 조회하여 버전 키 파생
        
        Args:
            snapshot_id: Snapshot ID (UUID 문자열)
        
        Returns:
            Snapshot row dict with version keys:
            - snapshot_id
            - code_git_sha
            - schema_version
            - model_version
            - dataset_version (optional, from Snapshot or default)
        
        Raises:
            ConstitutionViolationError: Snapshot이 존재하지 않을 때
        """
        conn = self._get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT 
                    snapshot_id,
                    code_git_sha,
                    schema_version,
                    model_version,
                    weights_hash,
                    weights_quick_hash,
                    runtime_env
                FROM snapshot
                WHERE snapshot_id = %s
                """,
                (snapshot_id,)
            )
            row = cur.fetchone()
            
            if row is None:
                raise ConstitutionViolationError(
                    f"Snapshot not found: {snapshot_id}. "
                    "Constitution violation: Snapshot must exist before inference run."
                )
            
            # Dict로 변환
            snapshot = dict(row)
            
            # 필수 버전 키 검증
            required_keys = ['code_git_sha', 'schema_version', 'model_version']
            missing = [k for k in required_keys if snapshot.get(k) is None]
            if missing:
                raise ConstitutionViolationError(
                    f"Snapshot {snapshot_id} missing required version keys: {missing}"
                )
            
            return snapshot
    
    def _validate_telemetry_fields(self, telemetry_data: Dict[str, Any]):
        """
        🔒 Telemetry 필수 필드 검증
        
        필수 필드:
        - egress_bytes
        - pure_inference_cost_usd
        - latency_ms
        - uncertainty_score
        - delivery_mode (IMAGE 또는 PARAMETER)
        """
        required = [
            'egress_bytes',
            'pure_inference_cost_usd',
            'latency_ms',
            'uncertainty_score',
            'delivery_mode'
        ]
        missing = [k for k in required if k not in telemetry_data]
        if missing:
            raise ConstitutionViolationError(
                f"Telemetry missing required fields: {missing}"
            )
        
        if telemetry_data['delivery_mode'] not in ['IMAGE', 'PARAMETER']:
            raise ConstitutionViolationError(
                f"Invalid delivery_mode: {telemetry_data['delivery_mode']}. "
                "Must be IMAGE or PARAMETER."
            )
    
    def persist_inference(
        self,
        snapshot_id: str,
        inference_input: Dict[str, Any],
        inference_result: Dict[str, Any],
        gate_result: Dict[str, Any],  # GateResult (1:1 관계, 단일 dict)
        telemetry_data: Dict[str, Any],
        delivery_artifacts: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        단일 추론 실행을 헌법 준수 방식으로 DB에 적재.
        
        Args:
            snapshot_id: Snapshot ID (UUID 문자열)
            inference_input: 추론 입력 파라미터 (JSON 직렬화 가능)
            inference_result: 추론 결과 (JSON 직렬화 가능)
            gate_result: GateResult (1:1 관계, 단일 dict):
                - gate_type: 'PROC' | 'GEO' | 'QUAL'
                - passed: bool
                - failure_code: Optional[str] (예: 'GEO_FAIL', 'PROC_FAIL')
                - details: Optional[Dict] (추가 메타데이터)
            telemetry_data: Telemetry 데이터 (필수 필드 포함)
            delivery_artifacts: DeliveryArtifact 리스트 (Optional, 0~N)
                각 dict는:
                - artifact_type: str
                - storage_path: str
                - size_bytes: int
        
        Returns:
            run_id: 생성된 InferenceRun의 UUID (문자열, PK 컬럼명: run_id)
        
        Raises:
            ConstitutionViolationError: 헌법 위반 시
            psycopg2.Error: DB 오류 시
        """
        
        # 1. Snapshot 조회 (버전 키 파생)
        snapshot = self._fetch_snapshot(snapshot_id)
        
        # 2. Telemetry 필수 필드 검증
        self._validate_telemetry_fields(telemetry_data)
        
        # 3. GateResult 검증 (필수)
        if not gate_result:
            raise ConstitutionViolationError(
                "GateResult is mandatory (1:1 relationship with InferenceRun)."
            )
        
        # 4. 단일 트랜잭션으로 INSERT
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # 트랜잭션 시작 (psycopg2는 autocommit=False가 기본)
                
                # 4.1. InferenceRun INSERT (UUID는 DB에서 생성)
                cur.execute(
                    """
                    INSERT INTO inference_run (
                        snapshot_id,
                        code_git_sha,
                        schema_version,
                        model_version,
                        dataset_version,
                        input_summary,
                        result_summary,
                        created_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING run_id
                    """,
                    (
                        snapshot_id,
                        snapshot['code_git_sha'],
                        snapshot['schema_version'],
                        snapshot['model_version'],
                        snapshot.get('dataset_version'),
                        json.dumps(inference_input),
                        json.dumps(inference_result),
                        datetime.utcnow()
                    )
                )
                inference_run_row = cur.fetchone()
                run_id = str(inference_run_row['run_id'])
                
                # 4.2. GateResult INSERT (1:1 관계, 단일 row)
                # 🔒 모든 Row에 4종 버전 키 필수 포함
                cur.execute(
                    """
                    INSERT INTO gate_result (
                        run_id,
                        snapshot_id,
                        code_git_sha,
                        schema_version,
                        model_version,
                        gate_type,
                        passed,
                        failure_code,
                        details
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    """,
                    (
                        run_id,
                        snapshot_id,
                        snapshot['code_git_sha'],
                        snapshot['schema_version'],
                        snapshot['model_version'],
                        gate_result['gate_type'],
                        gate_result['passed'],
                        gate_result.get('failure_code'),
                        json.dumps(gate_result.get('details')) if gate_result.get('details') else None
                    )
                )
                
                # 4.3. Telemetry INSERT (최소 1 row, Gate FAIL이어도 반드시 저장)
                # 🔒 정산/운영 관점에서 실패도 비용 집계에 포함
                cur.execute(
                    """
                    INSERT INTO telemetry (
                        run_id,
                        snapshot_id,
                        code_git_sha,
                        schema_version,
                        model_version,
                        dataset_version,
                        latency_ms,
                        gpu_ms,
                        cpu_ms,
                        egress_bytes,
                        transmission_mode,
                        uncertainty_score,
                        pure_inference_cost_usd,
                        delivery_mode,
                        cost_model_version,
                        created_at
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING telemetry_id
                    """,
                    (
                        run_id,
                        snapshot_id,
                        snapshot['code_git_sha'],
                        snapshot['schema_version'],
                        snapshot['model_version'],
                        snapshot.get('dataset_version'),
                        telemetry_data['latency_ms'],
                        telemetry_data.get('gpu_ms'),
                        telemetry_data.get('cpu_ms'),
                        telemetry_data['egress_bytes'],
                        telemetry_data.get('transmission_mode'),
                        telemetry_data['uncertainty_score'],
                        telemetry_data['pure_inference_cost_usd'],
                        telemetry_data['delivery_mode'],
                        telemetry_data.get('cost_model_version'),
                        datetime.utcnow()
                    )
                )
                telemetry_id = cur.fetchone()['telemetry_id']
                
                # 4.4. DeliveryArtifact INSERT (0~N rows)
                # 🔒 모든 Row에 4종 버전 키 필수 포함
                if delivery_artifacts:
                    for artifact in delivery_artifacts:
                        cur.execute(
                            """
                            INSERT INTO delivery_artifact (
                                run_id,
                                snapshot_id,
                                code_git_sha,
                                schema_version,
                                model_version,
                                artifact_type,
                                storage_path,
                                size_bytes
                            )
                            VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s
                            )
                            """,
                            (
                                run_id,
                                snapshot_id,
                                snapshot['code_git_sha'],
                                snapshot['schema_version'],
                                snapshot['model_version'],
                                artifact['artifact_type'],
                                artifact['storage_path'],
                                artifact['size_bytes']
                            )
                        )
                
                # 커밋 (성공 시)
                conn.commit()
                
                return run_id
                
        except ConstitutionViolationError:
            # 헌법 위반은 재시도 불가 → 즉시 롤백
            conn.rollback()
            raise
        except psycopg2.Error as e:
            # DB 오류 → 롤백
            conn.rollback()
            raise
        except Exception as e:
            # 기타 예외 → 롤백
            conn.rollback()
            raise RuntimeError(f"Unexpected error during inference persistence: {e}") from e
    
    def close(self):
        """연결 종료"""
        if self._conn and not self._conn.closed:
            self._conn.close()
            self._conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============================================================
# 사용 예시 (독스트링)
# ============================================================

"""
사용 예시:

from core.persistence.inference_persister import InferencePersister, ConstitutionViolationError

persister = InferencePersister("postgresql://user:pass@localhost/dbname")

try:
    inference_run_id = persister.persist_inference(
        snapshot_id="550e8400-e29b-41d4-a716-446655440000",
        inference_input={
            "gender": "male",
            "age": 30,
            "height_m": 1.75,
            "weight_kg": 70.0
        },
        inference_result={
            "shoulder_width_m": 0.42,
            "betas": [0.1, 0.2, ...],
            "status": "SUCCESS"
        },
        gate_results=[
            {
                "gate_type": "PROC",
                "passed": True,
                "failure_code": None,
                "details": None
            },
            {
                "gate_type": "GEO",
                "passed": True,
                "failure_code": None,
                "details": None
            },
            {
                "gate_type": "QUAL",
                "passed": False,
                "failure_code": "QUAL_FAIL",
                "details": {"reason": "visual_inconsistency"}
            }
        ],
        telemetry_data={
            "latency_ms": 1520,
            "gpu_ms": 1200,
            "cpu_ms": 320,
            "egress_bytes": 245760,
            "transmission_mode": "REST_API",
            "uncertainty_score": 0.05,
            "pure_inference_cost_usd": 0.0012,
            "delivery_mode": "IMAGE",
            "cost_model_version": "v1.0"
        },
        delivery_artifacts=[
            {
                "artifact_type": "RENDERED_IMAGE",
                "storage_path": "s3://bucket/artifacts/img_123.png",
                "size_bytes": 245760
            }
        ]
    )
    print(f"Persisted run_id: {run_id}")
    
except ConstitutionViolationError as e:
    print(f"헌법 위반: {e}")
except Exception as e:
    print(f"오류: {e}")
finally:
    persister.close()
"""
