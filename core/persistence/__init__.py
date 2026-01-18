"""
Core Persistence Layer: Constitution v1 Compliant

헌법 준수 원칙:
- Snapshot First
- 단일 트랜잭션
- 버전 키 파생
- UUID는 DB에서 생성
"""

from core.persistence.inference_persister import (
    InferencePersister,
    ConstitutionViolationError
)

__all__ = [
    'InferencePersister',
    'ConstitutionViolationError'
]
