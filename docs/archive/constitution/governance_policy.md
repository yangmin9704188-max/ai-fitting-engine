# 스냅샷/버저닝 정책

Level: L0
Change Rule: ADR 필수 + Tag 필수

==================

# Governance Policy: Snapshot & Versioning

## 1. Snapshot Definition
Snapshot은 다음 요소의 조합으로 정의된다.
- Code revision (git SHA)
- Model weights
- Runtime / config
- Dataset versions

Snapshot ID 형식:
snapshot@X.Y.Z+build.<gitsha>

## 2. Snapshot Invariants
- Snapshot은 불변(Immutable)이다.
- 동일 snapshot_version은 항상 재현 가능해야 한다.
- 운영 편의를 이유로 한 무버전 수정은 금지한다.

## 3. Hash Strategy
- 초기 단계에서는 Quick Hash를 허용한다.
  - (file size, modified time, partial content hash)
- 목적은 보안이 아닌 **재현성 추적**이다.

## 4. Snapshot Release Rules
- Snapshot 발행 시:
  - `releases.md` 자동 갱신
  - snapshot_version 명시
- 이전 snapshot은 삭제하지 않는다.

## 5. Enforcement
- Snapshot 발행 없는 배포는 허용되지 않는다.