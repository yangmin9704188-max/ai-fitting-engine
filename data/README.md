# Data Guide (data/)

본 문서는 이 레포의 `data/` 디렉터리 구조, 데이터 출처, 정제 규칙, 단위/스키마 관례, 재생성 워크플로우를 정의한다. 목표는 “추론 없이” 데이터의 의미와 재현 가능성을 확보하는 것이다.

## 0) 공개/라이선스 상태
- 현재(현 시점) 원천 데이터 및 파생 데이터는 공개 가능.
- 단, 향후 PoC/B2B 계약 단계에서 비공개 전환 가능성이 있으므로, 파일/폴더 단위로 공개 정책을 재검토할 수 있다.

## 1) 단위(Unit) 정책
- Raw(`data/raw`)는 **원천 단위 보존**이 원칙이다. (SizeKorea 원천 단위: **mm**)
- Processed(`data/processed`)는 프로젝트 내에서 사용하기 위한 **정제/파생 데이터**이며, 단위 변환/컬럼 표준화가 적용된다.
- **모든 processed 데이터는 meters(m) 단위를 강제하며 0.001m(1mm) 해상도를 가진다.**
- Ingestion 단계에서 원천 단위(mm/cm/m)를 meters로 명시적 변환 및 양자화를 수행한다 (`data/ingestion.py::canonicalize_units_to_m`).
- 프로젝트의 “계약/측정 표준 단위”는 `docs/contract/UNIT_STANDARD.md`를 단일 진실원으로 삼는다.
  - 단위 정책이 확정/변경되면 processed는 재정제하여 일관성을 확보한다.

## 2) 디렉터리 레이아웃

### 2.1) `data/raw/` (원천 데이터, 수정 금지)
정제되지 않은 원천 데이터/다운로드 파일을 보관한다. 이 폴더에서는 전처리/정제를 수행하지 않는다.

#### 2.1.1) `data/raw/scans_3d/`
- SizeKorea에서 다운로드한 표준 남/녀 신체 3D 스캔 OBJ 일부
- 현재는 실험용으로 일부 연령대만 다운로드한 상태
- 예시:
  - `6차_20대_남성.obj`
  - `6차_20대_여성.obj`
  - `6차_30대_남성.obj`
  - `6차_40대_남성.obj`

#### 2.1.2) `data/raw/sizekorea_raw/`
- SizeKorea 보고서/원천 테이블(7th/8th) 보관
- 파일:
  - `2021년 8차 인체치수조사_최종보고서.pdf` (8차 최종보고서)
  - `7th_data.csv` / `7th_data.xlsx` (2015년 직접 측정 6,427건, 기본 단위 mm)
  - `8th_data_3d.csv` (2020~2024년 3D 스캔 기반 4,552건)
  - `8th_data_direct.csv` (2020~2024년 직접 측정 5,099건)
  - `8th_data.xlsx` (직접/3D 스캔 포함)

**Raw 규칙**
- 원천 파일은 “내용 수정 금지”.
- 정제/필터링/컬럼명 변경/단위 변환은 `data/processed`에서 수행한다.

---

### 2.2) `data/processed/` (정제/파생 데이터)
원천 데이터를 프로젝트에서 쓰기 좋은 형태로 정제한 결과물을 저장한다.

#### 2.2.1) `data/processed/SizeKorea_Final/`
7차+8차 데이터를 통합하고 이상치 제거 후, 분석/샘플링에 필요한 최소 필드만 남겨 저장한 정제 데이터.

**정제 요약(현 상태)**
- 대상: 7차 + 8차 데이터 통합
- 이상치 제거: **Z-Score ±3σ(outlier 제거)**
- 연령 범위: **20대~50대**
- 성별/연령 bin으로 분류하여 파일로 저장(남/녀 분리, 20/30/40/50대)

**컬럼(현 상태)**
- 신장, 몸무게, 가슴둘레, 허리둘레, 엉덩이둘레 중심
- 컬럼명 표준화:
  - `height`, `weight`, `chest_girth`, `Waist_Girth`, `Hip_Girth`
- 단위 변환:
  - 원천 **mm → (현 저장) cm**

**파일**
- `SizeKorea_20-29_Female.csv`
- `SizeKorea_20-29_Male.csv`
- `SizeKorea_30-39_Female.csv`
- `SizeKorea_30-39_Male.csv`
- `SizeKorea_40-49_Female.csv`
- `SizeKorea_40-49_Male.csv`
- `SizeKorea_50-59_Female.csv`
- `SizeKorea_50-59_Male.csv`

**Processed 규칙**
- 이 폴더의 산출물은 raw로부터 재생성 가능해야 한다(재현성).
- 단위/표준 키/컬럼 정책이 변경되면 processed는 재정제 및 갱신한다.

#### 2.2.2) `data/processed/step1_output/`
SMPL-X 기반 파이프라인의 초기 단계 산출물(초기 betas 및 메타데이터)을 보관한다.

- `init_betas_all.npy`
- `init_betas_female.npy`
- `init_betas_male.npy`
- `targets_metadata.csv`

##### `targets_metadata.csv` 컬럼(요약)
- Age:
  - `age`, `age_low`, `age_high`
- Anthropometrics:
  - `height_cm`, `weight_kg`, `chest_cm`, `waist_cm`, `hip_cm`
- Scaling:
  - `body_scale`, `raw_scale`, `scale_clipp`
- Derived:
  - `bmi`
- Betas:
  - `beta0_raw`, `beta0_clipped`

---

## 3) 재생성(정제/골든셋) 워크플로우 개요
- Raw(mm, 원천) → Processed(정제/표준화) → step1_output(모델 입력 파생) → Verification/Golden(회귀/사실 기록용)

재생성 트리거(요약)
- facts-only 러너 결과에서 `UNIT_FAIL`/`PERIMETER_LARGE` 재현, NaN 고율, 퇴화 경고 반복이 관측되면,
  구현 튜닝보다 “단위 표준화 + golden 재생성”이 우선이다.

---

## 4) Do-not-commit(운영 정책에 따라 선택)
현재는 공개 가능 상태이나, 향후 비공개 전환 시 다음을 우선 검토한다.
- 원천 대용량 파일(예: `data/raw/scans_3d/` 대량 OBJ)
- 고객 데이터/계약 데이터가 섞이기 시작하는 시점의 입력/로그/런 결과물

---

## 5) TODO (봉인 대상)
- UNDERBUST/BUST 이원화가 raw/processed에서 어떤 컬럼으로 반영되는지 명시
  - 현재 processed에는 `chest_girth`만 존재하므로, 이 필드가 레거시 CHEST 의미인지(underbust인지, bust인지, 혹은 혼합인지) 정의가 필요하다.
- Processed 단위(cm → m 또는 mm 유지) 최종 봉인 및 재정제 계획 수립
- “마스터 테이블 1개 + 파생 슬라이스(성별/연령 bin CSV)” 전략 채택 여부 결정
