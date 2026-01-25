# ops(devex): auto-generate COMMANDS.md and enforce via CI

## 목적
COMMANDS.md 자동 생성 도구 및 CI 검사 추가. Makefile 변경 시 COMMANDS.md 갱신 누락을 방지.

## 변경 사항

### 1. tools/ops/generate_commands_md.py 신설
- **목적**: `make help` 실행 결과를 파싱하여 COMMANDS.md 자동 생성
- **입력**: `make help` 실행 결과 (Source of truth = Makefile help output)
- **출력**: docs/ops/COMMANDS.md (overwrite)
- **내용 정책**:
  - `make help` 출력에 나열된 targets/예시를 우선 반영
  - 섹션 구성: Overview, 기본 명령, Round Ops Shortcuts, Quick Recipes, 기본 변수
  - facts-only, 판정 문구 금지
  - 절대경로 금지, OS 종속 로직 금지

### 2. Makefile commands-update 타겟 추가
- **사용**: `make commands-update`
- **동작**: `python tools/ops/generate_commands_md.py`
- **help에 1줄 추가**: `make commands-update`

### 3. GitHub Actions 워크플로우 추가
- **파일**: `.github/workflows/commands-docs-check.yml`
- **트리거**: pull_request (Makefile, tools/ops/generate_commands_md.py, docs/ops/COMMANDS.md 변경 시)
- **job 동작**:
  - checkout
  - python tools/ops/generate_commands_md.py 실행
  - git diff --exit-code docs/ops/COMMANDS.md
  - diff가 있으면 CI 실패 (= COMMANDS.md 갱신 누락을 잡아냄)
- **CI가 커밋/푸시/PR 수정 절대 하지 않음** (검사만)

## Scope
- ✅ tools/ops/generate_commands_md.py 신규 생성
- ✅ Makefile commands-update 타겟 추가
- ✅ docs/ops/COMMANDS.md (generator로 생성)
- ✅ .github/workflows/commands-docs-check.yml 신규 생성
- ✅ 그 외 모든 경로 변경/추가 0

## DevEx 체크리스트

### Generator 구현
- ✅ commands generator가 `make help` 실행 결과 기반으로 동작
- ✅ Source of truth = Makefile help output 명시
- ✅ 절대경로 금지, OS 종속 로직 금지

### 명령 실행
- ✅ `make commands-update` 동작 확인
- ✅ `python tools/ops/generate_commands_md.py` 직접 실행 가능

### CI 검사
- ✅ commands-docs-check workflow가 COMMANDS.md freshness를 검사
- ✅ CI는 검사만 수행, 자동 커밋/푸시 없음

## Smoke 검증

### 1. make help
```
Available targets:
  make sync-dry ARGS="--set snapshot.status=candidate"
  make sync ARGS="--set last_update.trigger=manual_test"
  ...
```

### 2. python tools/ops/generate_commands_md.py
```
Generated: docs/ops/COMMANDS.md
```

### 3. make commands-update
```
Generated: docs/ops/COMMANDS.md
```

### 4. git diff로 COMMANDS.md 생성/갱신 확인
- COMMANDS.md가 generator로 생성/갱신됨

## 품질 검증

### Generator 스크립트
- ✅ `make help` 실행 결과 파싱 로직 구현
- ✅ Makefile 변수 기본값 추출
- ✅ 섹션별 명령 정리 (Available targets, Round Ops Shortcuts, Examples)

### CI 워크플로우
- ✅ PR 트리거 설정
- ✅ 경로 필터 설정 (Makefile, generator, COMMANDS.md)
- ✅ 검사만 수행, 자동 커밋/푸시 없음

## Rollback
- `tools/ops/generate_commands_md.py` 삭제 가능
- `Makefile` commands-update 타겟 제거 가능
- `.github/workflows/commands-docs-check.yml` 삭제 가능

## 변경 파일 목록

**신규 파일 (2개):**
- `tools/ops/generate_commands_md.py`
- `.github/workflows/commands-docs-check.yml`

**수정 파일 (2개):**
- `Makefile` (commands-update 타겟 추가)
- `docs/ops/COMMANDS.md` (generator로 생성)

## 원칙 준수
- ✅ PASS/FAIL 판정 금지: facts-only 문서, 판정 문구 없음
- ✅ Semantic 재논의 금지: 기존 로직 의미 변경 없음
- ✅ 대규모 리팩터링 금지: generator + CI 추가만
- ✅ CI가 레포에 자동 커밋/자동 수정하지 않음: 검사만 수행
- ✅ 허용 범위 준수: tools/ops/generate_commands_md.py + Makefile + docs/ops/COMMANDS.md + .github/workflows/commands-docs-check.yml 외 변경 0
