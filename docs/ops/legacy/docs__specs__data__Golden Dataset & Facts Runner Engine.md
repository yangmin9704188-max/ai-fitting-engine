1. 목적과 범위
1.1 목적

Geometric/Validation 레이어에서 “조용한 오답(스케일 붕괴, 축 혼동, 단면 공백 등)”을 **실험 런너(Facts Runner)**로 조기에 표면화하고, 이를 재현 가능한 **Golden Dataset(NPZ)**로 고정하여 회귀 검증 기반의 개발 루프를 안정화한다.

Golden S0 (Synthetic): 엔진 자체의 기하학 로직을 자극하는 “퇴화/잡음/스케일 오류 의심” 케이스를 포함해, 측정 실패/경고 패턴을 정형화한다.

Golden Real-data (curated_v0 기반): 실측 분포 기반의 “현장형 Facts”를 확보하여, Synthetic에서만 맞는 엔진이 되지 않도록 한다.

1.2 범위(포함)

Golden NPZ 생성(합성/실데이터 기반) 및 메타데이터/Provenance 기록

invariant check(물리 범위, 스케일 정합) 및 실패 시 디버그 JSON 트레이스 저장

Facts Runner로 NaN rate / warning 빈도 / 실패 reason 분포 등 facts-only 리포트 생성

“빠른 루프(FAST MODE)”로 단일 케이스(normal_1 등)만 생성/검증하여 디버깅 시간 단축

산출물 경로/커밋 정책 정합(SYNC_HUB 기반) 준수

1.3 범위(비포함)

측정 정의의 의미론(Semantic) 확정 및 인체공학적 해석

Facts에 대한 PASS/FAIL 판단(임계값 박기)

curated_v0 데이터 정제/계약 변경(이번 라운드 목표는 Validation 관측 기반)

운영 원칙 상, facts-only 관측/기록을 우선하며 “판단”은 별도 레이어로 분리한다는 프로젝트 원칙을 따른다.

MasterPlan

SYNC_HUB

2. 시스템 구성 요소
2.1 실행 엔트리포인트
(A) Synthetic Golden S0 생성기

스크립트: verification/datasets/golden/core_measurements_v0/create_s0_dataset.py

특징:

ONLY_CASE 환경변수로 단일 케이스 생성(FAST MODE)

invariant fail 시 debug JSON 저장 및 “요약 출력” 제공

NPZ 저장 후 RE-OPEN PROOF(재로딩 후 스케일 지속성 검증)

(B) Real-data Golden 생성기 (curated_v0 → NPZ)

스크립트: verification/datasets/golden/core_measurements_v0/create_real_data_golden.py

입력:

data/processed/curated_v0/curated_v0.parquet (사용자 실행 로그 기준)

출력:

verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz

meta_unit / schema_version / created_at / source_path_abs 등 메타 포함(사용자 실행 로그 기준)

(C) Facts Runner

Synthetic(geo_v0):

verification/runners/run_geo_v0_facts_round1.py

Real-data(curated_v0):

verification/runners/run_curated_v0_facts_round1.py

공통 출력:

facts_summary.json

*_facts_*.md (리포트)

산출물 커밋 정책:

verification/runs/**는 커밋 금지, 경로/명령만 기록한다.

SYNC_HUB

2.2 산출물/커밋 정책(운영)

verification/runs/**: 산출물 디렉토리 → 커밋 금지

verification/datasets/**.npz: 재현 목적 Golden에 한해 allowlist로 커밋 허용(정책 준수 필요)

SYNC_HUB

3. 입력 데이터 및 전제
3.1 Golden S0 (Synthetic)

케이스 타입:

정상 케이스(normal_1 등)

퇴화/극소/노이즈/스케일 오류 의심 케이스(예: degenerate_y_range, minimal_vertices, random_noise_seed123 등)

스케일 전제:

Height 축(Up axis) 기준 bounding box span이 “사람 범위” 내로 들어오도록 정규화

키 정규화 이후 **둘레 계열(XZ)**도 인체 스케일에 맞게 동반 정규화(오늘 디버깅 핵심)

3.2 Golden Real-data (curated_v0)

소스:

curated_v0.parquet에서 N개 샘플을 추출하여 NPZ로 변환(오늘 Round20에서 200 케이스 사용)

단위 전제:

curated_v0는 meters 단위를 기본으로 하며, NPZ에 meta_unit을 기록해 runner에서 검증 가능하도록 한다(운영 철학/SoT 규칙과 정합).

MasterPlan

4. 처리 파이프라인(단계별)
Stage 0 — FAST MODE(단일 케이스 생성)로 디버깅 루프 단축

목표: invariant fail을 유발하는 케이스(예: normal_1)만 빠르게 생성/검증하여 원인 추적 시간을 줄인다.

입력:

ONLY_CASE=normal_1

동작:

지정 케이스만 생성

invariant check 수행

실패 시 debug JSON(최근 fail) 파싱/요약 출력

성공 시 NPZ 저장 + re-open proof

Stage 1 — 스케일 정규화(Height + XZ 동반 정합)

목표: “키는 정상인데 둘레가 비정상” 같은 축/스케일 불일치를 제거한다.

Height 축 span을 target height로 맞추는 스케일 팩터를 적용

둘레(가슴/허리/힙) 추정/생성 시,

“이론상(after_scale_theoretical)”과

“verts 기반 추정(from_verts_after)”
가 일치하도록 XZ 스케일을 정합시키는 것이 핵심(오늘 로그에서 bust_radius/둘레가 before/after로 비교되는 형태로 진전)

Stage 2 — Invariant Check + Debug Trace

목표: 실패는 예외로 죽지 않고 “진단 가능한 데이터”로 남긴다.

invariant fail 시:

debug JSON 저장

key 후보/추정치/스케일 팩터/클램프 적용 여부 등 기록

성공 시:

“이전 실패 레코드가 stale임”을 명시(현재 run과 구분)

Stage 3 — NPZ Save + Re-open Proof

목표: “생성기는 성공했는데 runner가 파일을 못 찾는다/스케일이 저장되지 않는다” 류의 운영 실패를 차단한다.

NPZ 저장 직후:

File exists / size / mtime 출력

Re-open proof:

np.load로 재로딩

bbox span이 target과 일치하는지 재검증

Stage 4 — Facts Runner 실행 및 리포트 생성

목표: “고쳤다”가 아니라 “관측 결과가 무엇인지”를 기록한다.

JSON:

facts_summary.json (집계/분포/실패 reason)

Markdown:

*_facts_*.md (사람이 읽을 수 있는 보고서)

커밋 정책:

산출물은 verification/runs/**에 두되 커밋 금지(경로/명령/대표 리포트만 validation 폴더로 고정하는 방식 채택)

SYNC_HUB

5. 품질 센서(Validation 관측 신호)
5.1 핵심 관측 지표

케이스 수(Loaded, Valid, Expected fail)

NaN rate(측정키별)

failure reason 분포(mesh_empty_at_height, empty_slice, no_vertices_in_region 등)

스케일/축 의심 신호(10배/100배 패턴 등)

5.2 오늘의 핵심 리스크와 처리 방향

(해결됨/진행) S0 스케일 불일치: Height 정규화 + XZ 동반 정합으로 “키는 사람인데 둘레는 괴물” 상태를 제거하는 방향으로 진전

(진행) stale debug JSON 혼입: “현재 run 성공/이전 fail record”를 명확히 구분 출력하도록 개선(오늘 출력에 반영)

6. Runbook (bash)
6.1 Synthetic S0: FAST MODE(normal_1) 생성/검증
rm -f verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz

ONLY_CASE=normal_1 py verification/datasets/golden/core_measurements_v0/create_s0_dataset.py

6.2 Synthetic S0: Facts Runner 실행
py verification/runners/run_geo_v0_facts_round1.py \
  --npz verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz \
  --n_samples 20 \
  --out_dir verification/runs/facts/geo_v0/roundXX_fastmode_normal1

6.3 Real-data Golden(curated_v0): NPZ 생성 + Facts Runner 실행 (Round20)
py verification/datasets/golden/core_measurements_v0/create_real_data_golden.py \
  --n_cases 200 \
  --out_npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz

py verification/runners/run_curated_v0_facts_round1.py \
  --npz verification/datasets/golden/core_measurements_v0/golden_real_data_v0.npz \
  --out_dir verification/runs/facts/curated_v0/round20_$(date +%Y%m%d_%H%M%S)

7. Freeze(봉인) 규칙 및 운영 메모
7.1 Golden S0 Freeze

Round17까지 “Valid ≥ 10, expected_fail 5, no clamp” 조건을 만족시키고,

이후 이슈는 generator 수정 없이 metadata/provenance/validation 관측으로 처리한다는 Freeze 원칙을 선언(사용자 정리 기준).

7.2 산출물 커밋 규칙

verification/runs/**는 커밋 금지, 대신 재현 가능한 명령과 핵심 보고서 경로만 문서에 고정한다.

SYNC_HUB

8. 테스트 전략(결정성/회귀)

FAST MODE로 “단일 케이스” 생성/검증 루프를 회귀 테스트 수준으로 유지

NPZ Re-open proof로 “저장/경로/지속성” 운영 실패를 회귀 봉인

Real-data Golden을 통해 “Synthetic만 맞는 엔진”을 조기 차단

