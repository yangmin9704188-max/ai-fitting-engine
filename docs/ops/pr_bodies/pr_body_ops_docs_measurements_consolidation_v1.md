# PR Body: ops(docs): consolidate measurements policies (SoT index + legacy banners)

## 무엇을 만들었는지

- **INDEX.md 신규 생성**: `docs/policies/measurements/INDEX.md`
  - SizeKorea 정의/기준점/측정방법이 유입된 상태에서 measurements 정책 문서의 단일 진입점(SoT) 제공
  - Current SoT 섹션: 현재 유효한 문서 링크 모음 (표 형태)
  - SizeKorea Evidence/Anchors 섹션: evidence 문서 링크 모음
  - Legacy 섹션: 구 문서 목록 + superseded 표기
  - TODO 섹션: 아직 재작성 안된 키 목록

- **Legacy 배너 추가**: 5개 문서에 legacy 배너 추가
  - `bust.md`: status "frozen" → "legacy", 상단 배너 추가
  - `hip.md`: status "frozen" → "legacy", 상단 배너 추가
  - `waist.md`: status "frozen" → "legacy", 상단 배너 추가
  - `README.md`: status "frozen" → "legacy", 상단 배너 추가
  - `FREEZE_DECLARATION.md`: status "frozen" → "legacy", 상단 배너 추가

## 변경 범위

**폴더**: `docs/policies/measurements/`

**변경 파일**:
1. `docs/policies/measurements/INDEX.md` (신규)
2. `docs/policies/measurements/bust.md` (legacy 배너 추가)
3. `docs/policies/measurements/hip.md` (legacy 배너 추가)
4. `docs/policies/measurements/waist.md` (legacy 배너 추가)
5. `docs/policies/measurements/README.md` (legacy 배너 추가)
6. `docs/policies/measurements/FREEZE_DECLARATION.md` (legacy 배너 추가)
7. `docs/ops/pr_bodies/pr_body_ops_docs_measurements_consolidation_v1.md` (신규, 이 파일)

## 스모크

### 변경 파일이 Allowed scope 밖이 없는지 확인
```
✅ 모든 변경 파일이 docs/policies/measurements/** 또는 docs/ops/pr_bodies/** 범위 내
```

### legacy 배너가 실제로 삽입됐는지 샘플 확인

**bust.md (샘플 1)**:
```markdown
---
title: "Bust Circumference"
version: "v1.0"
status: "legacy"
...

> **⚠️ LEGACY DOCUMENT**  
> **status**: legacy  
> **superseded_by**: [docs/policies/measurements/INDEX.md](INDEX.md)  
> **reason**: pre-sizekorea definition; anchors updated  
> **note**: do not treat as SoT
```

**README.md (샘플 2)**:
```markdown
---
title: "Body Measurement Meta-Policy"
version: "v1.3"
status: "legacy"
...

> **⚠️ LEGACY DOCUMENT**  
> **status**: legacy  
> **superseded_by**: [docs/policies/measurements/INDEX.md](INDEX.md)  
> **reason**: pre-sizekorea definition; anchors updated  
> **note**: do not treat as SoT
```

**FREEZE_DECLARATION.md (샘플 3)**:
```markdown
---
title: "Measurement Semantic + Interface Freeze"
version: "v1.0.0"
status: "legacy"
...

> **⚠️ LEGACY DOCUMENT**  
> **status**: legacy  
> **superseded_by**: [docs/policies/measurements/INDEX.md](INDEX.md)  
> **reason**: pre-sizekorea definition; anchors updated  
> **note**: do not treat as SoT
```

### INDEX에서 링크가 깨지지 않는지 확인
```
✅ 상대경로 사용 확인:
- [docs/semantic/measurement_semantics_v0.md](../../semantic/measurement_semantics_v0.md)
- [docs/semantic/evidence/sizekorea_measurement_methods_v0.md](../../semantic/evidence/sizekorea_measurement_methods_v0.md)
- [SEMANTIC_DEFINITION_BUST_VNEXT.md](SEMANTIC_DEFINITION_BUST_VNEXT.md)
- [INDEX.md](INDEX.md)
```

## DoD 체크리스트

- [x] INDEX.md 신규 생성 (목적/원칙, Current SoT, SizeKorea Evidence, Legacy, TODO 섹션)
- [x] Legacy 문서 5개 식별 (bust.md, hip.md, waist.md, README.md, FREEZE_DECLARATION.md)
- [x] Legacy 문서 상단에 배너 추가 (status 변경 + 배너 삽입)
- [x] PR 바디 작성 완료
- [x] 스모크 실행 (변경 범위 확인, 배너 샘플 확인, 링크 확인)
- [x] git diff로 allowed scope 밖 파일 변경 없음 확인
- [ ] CI green 확인 후 머지 (CI red면 머지 금지)

## 롤백 포인트

**커밋 해시**: (커밋 후 업데이트)

**롤백 방법**:
```bash
git revert <commit_hash>
```

또는

```bash
git checkout main
git branch -D ops/docs-measurements-consolidation-v1
```
