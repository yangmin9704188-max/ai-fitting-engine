"""
Test: InferencePersister 헌법 준수 검증

3가지 케이스 검증:
1. 성공 케이스: 4개 테이블에 데이터가 정확히 생기는지 확인
2. Telemetry 필수 필드 누락: 전체 롤백 확인
3. Snapshot 미존재: 트랜잭션 시작 전 예외 확인
"""

import unittest
from typing import Dict, Any
import uuid
import json
import psycopg2
from psycopg2.extras import RealDictCursor, Json

from core.persistence import InferencePersister, ConstitutionViolationError


class TestInferencePersister(unittest.TestCase):
    """InferencePersister 헌법 준수 검증 테스트"""
    
    # DB 접속 정보 (고정값)
    db_conn_string = "postgresql://postgres:yang0702@localhost:5432/postgres"
    
    @classmethod
    def setUpClass(cls):
        """테스트 클래스 초기화: DB 연결 확인 및 테스트용 Snapshot 생성"""
        cls.persister = InferencePersister(cls.db_conn_string)
        
        # DB 연결 테스트
        try:
            conn = psycopg2.connect(cls.db_conn_string)
            conn.close()
        except psycopg2.Error as e:
            raise unittest.SkipTest(f"DB 연결 실패: {e}. PostgreSQL이 실행 중인지 확인하세요.")
        
        # 테스트용 Snapshot 생성
        cls.test_snapshot_id = str(uuid.uuid4())
        cls._create_test_snapshot(cls.test_snapshot_id)
    
    @classmethod
    def tearDownClass(cls):
        """테스트 클래스 정리: 테스트용 Snapshot 삭제"""
        if hasattr(cls, 'persister'):
            cls.persister.close()
        
        # 테스트용 Snapshot 삭제
        try:
            conn = psycopg2.connect(cls.db_conn_string)
            with conn.cursor() as cur:
                cur.execute("DELETE FROM snapshot WHERE snapshot_id = %s", (cls.test_snapshot_id,))
                conn.commit()
            conn.close()
        except Exception:
            pass  # 이미 삭제되었거나 테이블이 없을 수 있음
    
    @classmethod
    def _create_test_snapshot(cls, snapshot_id: str):
        """테스트용 Snapshot 생성"""
        conn = psycopg2.connect(cls.db_conn_string)
        try:
            with conn.cursor() as cur:
                # 테이블이 없으면 생성 (간단한 CREATE IF NOT EXISTS 시뮬레이션)
                # 실제로는 마이그레이션으로 관리되어야 하지만, 테스트 편의를 위해
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS snapshot (
                        snapshot_id UUID PRIMARY KEY,
                        code_git_sha VARCHAR(255) NOT NULL,
                        schema_version VARCHAR(255) NOT NULL,
                        model_version VARCHAR(255) NOT NULL,
                        weights_hash VARCHAR(255),
                        weights_quick_hash VARCHAR(255),
                        runtime_env JSONB
                    )
                """)
                
                # Snapshot INSERT (runtime_env는 JSONB)
                runtime_env_dict = {
                    'python_version': '3.10',
                    'os': 'linux',
                    'cuda_version': '11.8'
                }
                cur.execute("""
                    INSERT INTO snapshot (
                        snapshot_id, code_git_sha, schema_version, model_version, 
                        weights_hash, weights_quick_hash, runtime_env
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (snapshot_id) DO UPDATE SET
                        code_git_sha = EXCLUDED.code_git_sha,
                        schema_version = EXCLUDED.schema_version,
                        model_version = EXCLUDED.model_version,
                        weights_hash = EXCLUDED.weights_hash,
                        weights_quick_hash = EXCLUDED.weights_quick_hash,
                        runtime_env = EXCLUDED.runtime_env
                """, (
                    snapshot_id,
                    'abc123def456',
                    'schema_v1.0',
                    'model_v1.2',
                    'hash123',
                    'quick_hash456',
                    json.dumps(runtime_env_dict)  # JSON 문자열로 변환
                ))
                
                conn.commit()
        finally:
            conn.close()
    
    def setUp(self):
        """각 테스트 전 실행: 트랜잭션 롤백 준비"""
        # 각 테스트는 독립적이어야 하므로, 이전 테스트 데이터 정리
        self._cleanup_test_data()
    
    def tearDown(self):
        """각 테스트 후 실행: 테스트 데이터 정리"""
        self._cleanup_test_data()
    
    def _cleanup_test_data(self):
        """테스트 데이터 정리 (역순으로 삭제: FK 의존성 고려)"""
        conn = psycopg2.connect(self.db_conn_string)
        try:
            with conn.cursor() as cur:
                # 테스트용 run_id로 삭제 (실제 테이블이 존재한다고 가정)
                # 테이블이 없으면 무시
                try:
                    cur.execute("DELETE FROM delivery_artifact WHERE run_id IN (SELECT run_id FROM inference_run WHERE snapshot_id = %s)", (self.test_snapshot_id,))
                    cur.execute("DELETE FROM telemetry WHERE run_id IN (SELECT run_id FROM inference_run WHERE snapshot_id = %s)", (self.test_snapshot_id,))
                    cur.execute("DELETE FROM gate_result WHERE run_id IN (SELECT run_id FROM inference_run WHERE snapshot_id = %s)", (self.test_snapshot_id,))
                    cur.execute("DELETE FROM inference_run WHERE snapshot_id = %s", (self.test_snapshot_id,))
                    conn.commit()
                except psycopg2.errors.UndefinedTable:
                    # 테이블이 없으면 스킵 (첫 실행 시)
                    conn.rollback()
        finally:
            conn.close()
    
    def _get_row_counts(self, snapshot_id: str) -> Dict[str, int]:
        """4개 테이블의 row 개수 반환"""
        conn = psycopg2.connect(self.db_conn_string)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                counts = {}
                
                # InferenceRun
                try:
                    cur.execute("SELECT COUNT(*) as cnt FROM inference_run WHERE snapshot_id = %s", (snapshot_id,))
                    counts['inference_run'] = cur.fetchone()['cnt']
                except psycopg2.errors.UndefinedTable:
                    counts['inference_run'] = 0
                
                # GateResult
                try:
                    cur.execute("""
                        SELECT COUNT(*) as cnt FROM gate_result 
                        WHERE run_id IN (SELECT run_id FROM inference_run WHERE snapshot_id = %s)
                    """, (snapshot_id,))
                    counts['gate_result'] = cur.fetchone()['cnt']
                except psycopg2.errors.UndefinedTable:
                    counts['gate_result'] = 0
                
                # Telemetry
                try:
                    cur.execute("""
                        SELECT COUNT(*) as cnt FROM telemetry 
                        WHERE run_id IN (SELECT run_id FROM inference_run WHERE snapshot_id = %s)
                    """, (snapshot_id,))
                    counts['telemetry'] = cur.fetchone()['cnt']
                except psycopg2.errors.UndefinedTable:
                    counts['telemetry'] = 0
                
                # DeliveryArtifact
                try:
                    cur.execute("""
                        SELECT COUNT(*) as cnt FROM delivery_artifact 
                        WHERE run_id IN (SELECT run_id FROM inference_run WHERE snapshot_id = %s)
                    """, (snapshot_id,))
                    counts['delivery_artifact'] = cur.fetchone()['cnt']
                except psycopg2.errors.UndefinedTable:
                    counts['delivery_artifact'] = 0
                
                return counts
        finally:
            conn.close()
    
    def _create_success_test_data(self) -> Dict[str, Any]:
        """성공 케이스용 테스트 데이터 생성"""
        return {
            'snapshot_id': self.test_snapshot_id,
            'inference_input': {
                'gender': 'male',
                'age': 30,
                'height_m': 1.75,
                'weight_kg': 70.0
            },
            'inference_result': {
                'shoulder_width_m': 0.42,
                'betas': [0.1, 0.2, 0.3],
                'status': 'SUCCESS'
            },
            'gate_result': {
                'gate_type': 'PROC',
                'passed': True,
                'failure_code': None,
                'details': None
            },
            'telemetry_data': {
                'latency_ms': 1520,
                'gpu_ms': 1200,
                'cpu_ms': 320,
                'egress_bytes': 245760,
                'transmission_mode': 'REST_API',
                'uncertainty_score': 0.05,
                'pure_inference_cost_usd': 0.0012,
                'delivery_mode': 'IMAGE',
                'cost_model_version': 'v1.0'
            },
            'delivery_artifacts': [
                {
                    'artifact_type': 'RENDERED_IMAGE',
                    'storage_path': 's3://bucket/artifacts/img_123.png',
                    'size_bytes': 245760
                },
                {
                    'artifact_type': 'METADATA',
                    'storage_path': 's3://bucket/artifacts/meta_123.json',
                    'size_bytes': 1024
                }
            ]
        }
    
    def test_success_case_all_tables_populated(self):
        """
        케이스 1: 성공 케이스
        - 4개 테이블에 데이터가 정확히 1개씩(Artifact는 N개) 생기는지 확인
        - InferenceRun: 1 row
        - GateResult: 1 row (1:1 관계)
        - Telemetry: 1 row
        - DeliveryArtifact: 2 rows
        """
        # 실행 전 row 개수 확인
        counts_before = self._get_row_counts(self.test_snapshot_id)
        
        # 테스트 데이터 준비
        test_data = self._create_success_test_data()
        
        # 실행
        run_id = self.persister.persist_inference(
            snapshot_id=test_data['snapshot_id'],
            inference_input=test_data['inference_input'],
            inference_result=test_data['inference_result'],
            gate_result=test_data['gate_result'],
            telemetry_data=test_data['telemetry_data'],
            delivery_artifacts=test_data['delivery_artifacts']
        )
        
        # run_id가 반환되었는지 확인
        self.assertIsNotNone(run_id)
        self.assertIsInstance(run_id, str)
        
        # 실행 후 row 개수 확인
        counts_after = self._get_row_counts(self.test_snapshot_id)
        
        # 검증: 각 테이블에 예상된 개수의 row가 추가되었는지
        self.assertEqual(
            counts_after['inference_run'] - counts_before['inference_run'],
            1,
            "InferenceRun에 정확히 1개의 row가 생성되어야 함"
        )
        
        self.assertEqual(
            counts_after['gate_result'] - counts_before['gate_result'],
            1,  # 1:1 관계
            "GateResult에 정확히 1개의 row가 생성되어야 함 (1:1 관계)"
        )
        
        self.assertEqual(
            counts_after['telemetry'] - counts_before['telemetry'],
            1,
            "Telemetry에 정확히 1개의 row가 생성되어야 함"
        )
        
        self.assertEqual(
            counts_after['delivery_artifact'] - counts_before['delivery_artifact'],
            2,  # RENDERED_IMAGE, METADATA 각 1개
            "DeliveryArtifact에 정확히 2개의 row가 생성되어야 함"
        )
    
    def test_telemetry_missing_fields_rollback(self):
        """
        케이스 2: Telemetry 필수 필드 누락
        - latency_ms 등의 필수 필드를 제거하고 실행
        - DB에 아무 데이터도 남지 않고 전체 롤백되는지 확인
        """
        # 실행 전 row 개수 확인
        counts_before = self._get_row_counts(self.test_snapshot_id)
        
        # 테스트 데이터 준비 (Telemetry 필수 필드 누락)
        test_data = self._create_success_test_data()
        # latency_ms 제거
        test_data['telemetry_data'].pop('latency_ms', None)
        
        # 실행 시 예외 발생 확인
        with self.assertRaises(ConstitutionViolationError) as context:
            self.persister.persist_inference(
                snapshot_id=test_data['snapshot_id'],
                inference_input=test_data['inference_input'],
                inference_result=test_data['inference_result'],
                gate_result=test_data['gate_result'],
                telemetry_data=test_data['telemetry_data'],
                delivery_artifacts=test_data['delivery_artifacts']
            )
        
        # 예외 메시지에 "missing required fields" 포함 확인
        self.assertIn('missing required fields', str(context.exception).lower())
        
        # 실행 후 row 개수 확인 (변화가 없어야 함 = 전체 롤백)
        counts_after = self._get_row_counts(self.test_snapshot_id)
        
        self.assertEqual(
            counts_after['inference_run'],
            counts_before['inference_run'],
            "InferenceRun에 row가 생성되면 안 됨 (롤백 확인)"
        )
        
        self.assertEqual(
            counts_after['gate_result'],
            counts_before['gate_result'],
            "GateResult에 row가 생성되면 안 됨 (롤백 확인)"
        )
        
        self.assertEqual(
            counts_after['telemetry'],
            counts_before['telemetry'],
            "Telemetry에 row가 생성되면 안 됨 (롤백 확인)"
        )
        
        self.assertEqual(
            counts_after['delivery_artifact'],
            counts_before['delivery_artifact'],
            "DeliveryArtifact에 row가 생성되면 안 됨 (롤백 확인)"
        )
    
    def test_snapshot_not_found_exception_before_transaction(self):
        """
        케이스 3: Snapshot 미존재
        - DB에 없는 snapshot_id를 사용
        - 트랜잭션 시작 전에 예외가 발생하는지 확인
        - DB에 어떤 row도 남지 않아야 함
        """
        # 실행 전 row 개수 확인
        non_existent_snapshot_id = str(uuid.uuid4())
        counts_before = self._get_row_counts(non_existent_snapshot_id)
        
        # 테스트 데이터 준비
        test_data = self._create_success_test_data()
        test_data['snapshot_id'] = non_existent_snapshot_id  # 존재하지 않는 snapshot_id
        
        # 실행 시 예외 발생 확인
        with self.assertRaises(ConstitutionViolationError) as context:
            self.persister.persist_inference(
                snapshot_id=test_data['snapshot_id'],
                inference_input=test_data['inference_input'],
                inference_result=test_data['inference_result'],
                gate_result=test_data['gate_result'],
                telemetry_data=test_data['telemetry_data'],
                delivery_artifacts=test_data['delivery_artifacts']
            )
        
        # 예외 메시지에 "snapshot not found" 포함 확인
        self.assertIn('snapshot not found', str(context.exception).lower())
        
        # 실행 후 row 개수 확인 (변화가 없어야 함 = 트랜잭션 시작 전 실패)
        counts_after = self._get_row_counts(non_existent_snapshot_id)
        
        self.assertEqual(
            counts_after['inference_run'],
            counts_before['inference_run'],
            "InferenceRun에 row가 생성되면 안 됨 (트랜잭션 시작 전 예외)"
        )
        
        self.assertEqual(
            counts_after['gate_result'],
            counts_before['gate_result'],
            "GateResult에 row가 생성되면 안 됨 (트랜잭션 시작 전 예외)"
        )
        
        self.assertEqual(
            counts_after['telemetry'],
            counts_before['telemetry'],
            "Telemetry에 row가 생성되면 안 됨 (트랜잭션 시작 전 예외)"
        )
        
        self.assertEqual(
            counts_after['delivery_artifact'],
            counts_before['delivery_artifact'],
            "DeliveryArtifact에 row가 생성되면 안 됨 (트랜잭션 시작 전 예외)"
        )


if __name__ == '__main__':
    # 테스트 실행
    # Windows Git Bash에서 실행:
    # PYTHONPATH=. py -m unittest tests.test_db_persistence
    unittest.main()
