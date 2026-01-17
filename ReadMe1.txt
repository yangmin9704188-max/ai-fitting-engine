ai_models/
│
├── core/                      # 🔒 제품 핵심 (봉인 영역)
│   ├── pose_policy.py         # (기존 step2_utils.py)
│   └── __init__.py
│
├── pipelines/                 # 🔁 실행 파이프라인
│   ├── step1_execute.py
│   └── __init__.py
│
├── verification/              # 🧪 검증/회귀 테스트
│   ├── verify_pose_policy.py  # (기존 step2_verify_pose.py)
│   └── README.md
│
├── data/
│   ├── raw/                   # 🔵 원본 데이터 (읽기 전용)
│   │   ├── sizekorea_original/
│   │   │   └── 7th_8th_excel/
│   │   └── scans_3d/
│   │       └── male_female_20s_50s_obj/
│   │
│   ├── processed/             # 🟢 전처리된 데이터
│   │   ├── sizekorea_final/
│   │   └── step1_outputs/
│   │
│   └── models/                # 🧠 외부 모델 파일
│       └── smplx/
│           └── *.pkl
│
├── artifacts/                 # ⚫ 실행 결과/디버그 산출물
│   ├── pose_debug/
│   │   ├── baseline/
│   │   ├── policy_apose/
│   │   └── candidates/
│   └── logs/
│
├── experiments/               # 🧪 실험/임시 코드 (자유 구역)
│   └── scratch_*.py
│
└── README.md

core/ – Product Core (Do Not Touch Lightly)

프로덕션에서 항상 호출되는 핵심 정책 코드가 위치합니다.

pose_policy.py

모든 측정 전 A-Pose 강제 정책을 정의

정책 값(axis, angle, joint pair 등)은 상수로 봉인(FROZEN)

run_forward() 시 body_pose가 없으면 자동으로 정책 A-Pose 적용

⚠️ 이 디렉토리의 코드는
변경 시 반드시 verification/의 회귀 테스트를 통과해야 합니다.

🔁 pipelines/ – Execution Pipelines

실제 데이터 처리 단계별 실행 스크립트입니다.

step1_execute.py

SizeKorea 기반 데이터 → SMPL-X 파라미터 변환

이후 Step2(Smart Mapper)의 입력으로 사용될 중간 산출물 생성

파이프라인 스크립트는 재실행 가능해야 하며,
산출물은 data/processed/에 저장됩니다.

🧪 verification/ – Policy & Regression Verification

정책이 깨지지 않았는지 확인하는 전용 코드입니다.

verify_pose_policy.py

봉인된 A-Pose 정책이 여전히:

좌우 대칭을 유지하는지

batch 환경에서도 동일하게 동작하는지

symmetry score 기준으로 PASS / FAIL 판단

모델 버전 변경, 파라미터 수정, 환경 변경 시
반드시 실행해야 하는 검증 스크립트입니다.

🗂 data/ – Data Assets
data/raw/

원본 데이터 (절대 수정 금지)

SizeKorea 7·8차 엑셀 데이터

고해상도 3D 인체 스캔(obj)

data/processed/

전처리 및 중간 결과물

SizeKorea 정제 CSV

Step1 실행 결과(npy, csv)

data/models/

외부 모델 파일

SMPL-X .pkl 파일 등

기준 원칙:

raw → 재생성 불가

processed → 재생성 가능

⚫ artifacts/ – Runtime Outputs & Debug

실행 결과 및 디버그 산출물 저장 공간입니다.

pose_debug/

T-Pose / Policy A-Pose OBJ 파일

A-Pose 후보 탐색 결과(candidates)

검증용 시각화 결과

언제든 삭제 가능하며,
Git 관리 대상이 아닙니다.

🧪 experiments/ – Experiments / Scratch

실험용 코드

임시 테스트

구조가 확정되지 않은 아이디어

자유롭게 사용하되,
여기 있는 코드는 제품 로직이 아닙니다.

🧭 Development Principles

Policy First

A-Pose, dtype, device 등 핵심 규칙은 정책으로 고정

Reproducibility

동일 입력 → 동일 출력

Separation of Concerns

Core / Pipeline / Verification / Data 분리

Regression Safety

변경은 허용하되, 깨지면 즉시 탐지

🚀 Typical Workflow

Raw data 준비 (data/raw/)

Step1 실행 → 중간 산출물 생성 (pipelines/)

Core 정책 적용 (core/pose_policy.py)

정책 검증 (verification/verify_pose_policy.py)

결과 확인 (artifacts/)

📝 Notes

본 저장소는 엔진화/패키징을 염두에 두고 설계됨

B2B PoC, 내부 API, 추후 서비스 연동을 고려한 구조

정책 변경 시 반드시 문서 및 검증 스크립트 동반 업데이트