import os
import re
import glob
import numpy as np
import pandas as pd
from tqdm import tqdm
import torch
import smplx

# ---------------------------------------------------------
# ⚙️ 설정 (Configuration)
# ---------------------------------------------------------
# ✅ SMPL-X 모델 루트 폴더: "models" (그 아래에 smplx 폴더가 있어야 함)
# 예: C:\...\models\smplx\SMPLX_MALE.pkl
MODEL_FOLDER = r"C:\Users\caino\Desktop\ai model\models"

# ✅ 8개 CSV가 들어있는 폴더
CSV_DIR = r"C:\Users\caino\Desktop\ai model\SizeKorea_Final"

# ✅ 파일 패턴: 아래 8개 이름을 모두 포함해야 함
# SizeKorea_20-29_Female.csv ... SizeKorea_50-59_Male.csv
CSV_GLOB = os.path.join(CSV_DIR, "SizeKorea_*-*_*.csv")

# ✅ 출력 폴더
OUTPUT_FOLDER = r"C:\Users\caino\Desktop\ai model\step1_output"

# 컬럼 이름 (CSV 내부 컬럼명이 다르면 여기만 바꾸면 됨)
COL_MAP = {
    "gender": "Gender",        # 없어도 됨(파일명으로 보강)
    "age": "Age",              # 없어도 됨(파일명 age-range를 메타로 보관)
    "height": "Height",        # cm
    "weight": "Weight",        # kg
    "chest": "Chest_Girth",    # cm
    "waist": "Waist_Girth",    # cm
    "hip": "Hip_Girth"         # cm
}

# 하이퍼파라미터
NUM_BETAS = 20
BMI_REF = 22.0
BETA0_SCALE = 0.04
BETA0_CLIP = 0.5
SCALE_CLIP = (0.85, 1.15)

# 1차 물리 필터(노이즈 제거)
HEIGHT_RANGE = (130.0, 210.0)
WEIGHT_RANGE = (35.0, 180.0)
GIRTH_RANGE  = (50.0, 160.0)

# ---------------------------------------------------------
# 🔎 파일명 파서: SizeKorea_20-29_Male.csv → age_range, gender
# ---------------------------------------------------------
FILENAME_RE = re.compile(r"SizeKorea_(\d{2})-(\d{2})_(Male|Female)\.csv$", re.IGNORECASE)

def parse_filename_meta(path: str):
    base = os.path.basename(path)
    m = FILENAME_RE.match(base)
    if not m:
        return None, None, None
    a0 = int(m.group(1))
    a1 = int(m.group(2))
    g = m.group(3).lower()  # male/female
    return a0, a1, g

# ---------------------------------------------------------
# 📏 1. Robust Canonical Height
# ---------------------------------------------------------
def robust_height_cm(vertices, q_low=0.005, q_high=0.995):
    y = vertices[:, 1]
    y_low = torch.quantile(y, q_low)
    y_high = torch.quantile(y, q_high)
    return (y_high - y_low).item() * 100.0

def get_canonical_heights(model_root, num_betas=20):
    """
    model_root는 .../models (그 아래에 smplx 폴더 존재)
    .pkl 강제 로드: ext='pkl'
    """
    print("📏 Calculating Canonical Heights (Robust)...")
    device = torch.device("cpu")
    canonical_h = {}

    for gender in ["male", "female"]:
        model = smplx.create(
            model_root,
            model_type="smplx",
            gender=gender,
            use_pca=False,
            num_betas=num_betas,
            batch_size=1,
            ext="pkl",  # ✅ .pkl 강제
        ).to(device)
        model.eval()

        with torch.no_grad():
            betas = torch.zeros((1, num_betas), device=device)
            out = model(betas=betas)
            verts = out.vertices[0]
            h = robust_height_cm(verts)

        canonical_h[gender] = h
        print(f"   ✅ {gender.capitalize()}: {h:.2f} cm")

    # 안전 범위 체크
    for g, h in canonical_h.items():
        if not (120.0 <= h <= 220.0):
            raise RuntimeError(f"Canonical height out of range for {g}: {h:.2f} cm. Check model files.")

    return canonical_h

# ---------------------------------------------------------
# 🧬 2. Heuristic Init (BMI)
# ---------------------------------------------------------
def compute_bmi(height_cm, weight_kg):
    h_m = height_cm / 100.0
    if h_m <= 0:
        return np.nan
    return weight_kg / (h_m ** 2)

def get_init_betas(height_cm, weight_kg, num_betas=20):
    betas = np.zeros((num_betas,), dtype=np.float32)
    bmi = compute_bmi(height_cm, weight_kg)

    beta0_raw = np.nan
    beta0_clipped = np.nan

    if np.isfinite(bmi):
        beta0_raw = (bmi - BMI_REF) * BETA0_SCALE
        beta0_clipped = float(np.clip(beta0_raw, -BETA0_CLIP, BETA0_CLIP))
        betas[0] = beta0_clipped

    return betas, bmi, beta0_raw, beta0_clipped

# ---------------------------------------------------------
# 🛠️ 3. Row 처리
# ---------------------------------------------------------
def normalize_gender(value, fallback_gender=None):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return fallback_gender

    s = str(value).strip().lower()
    if s.startswith("m") or s in ["male", "man", "남", "남자"]:
        return "male"
    if s.startswith("f") or s in ["female", "woman", "여", "여자"]:
        return "female"
    return fallback_gender

def process_row(row, canonical_heights, source_file, age_low, age_high, file_gender):
    # 성별: CSV 우선, 없으면 파일명 기반
    gender = normalize_gender(row.get(COL_MAP["gender"], None), fallback_gender=file_gender)
    if gender not in ["male", "female"]:
        return None

    # 필수 숫자 파싱
    try:
        h = float(row[COL_MAP["height"]])
        w = float(row[COL_MAP["weight"]])
        c = float(row[COL_MAP["chest"]])
        waist = float(row[COL_MAP["waist"]])
        hip = float(row[COL_MAP["hip"]])
    except (KeyError, ValueError, TypeError):
        return None

    # 1차 물리 필터
    if not (HEIGHT_RANGE[0] <= h <= HEIGHT_RANGE[1]): return None
    if not (WEIGHT_RANGE[0] <= w <= WEIGHT_RANGE[1]): return None
    if not (GIRTH_RANGE[0]  <= c <= GIRTH_RANGE[1]):  return None
    if not (GIRTH_RANGE[0]  <= waist <= GIRTH_RANGE[1]): return None
    if not (GIRTH_RANGE[0]  <= hip <= GIRTH_RANGE[1]): return None

    # body_scale
    base_h = canonical_heights[gender]
    raw_scale = h / base_h
    final_scale = float(np.clip(raw_scale, SCALE_CLIP[0], SCALE_CLIP[1]))
    scale_clipped = not (SCALE_CLIP[0] <= raw_scale <= SCALE_CLIP[1])

    # init betas
    init_beta, bmi, beta0_raw, beta0_clipped = get_init_betas(h, w, NUM_BETAS)

    # Age(선택)
    age_val = None
    if COL_MAP["age"] in row.index:
        try:
            age_val = float(row[COL_MAP["age"]]) if pd.notna(row[COL_MAP["age"]]) else None
        except (ValueError, TypeError):
            age_val = None

    # 원본 추적용 id: 파일 + row index
    rid = f"{source_file}:{int(row.name)}"

    target = {
        "id": rid,
        "source_file": source_file,
        "gender": gender,

        "age": age_val,
        "age_low": age_low,
        "age_high": age_high,

        "height_cm": h,
        "weight_kg": w,
        "chest_cm": c,
        "waist_cm": waist,
        "hip_cm": hip,

        "body_scale": final_scale,
        "raw_scale": float(raw_scale),
        "scale_clipped": bool(scale_clipped),

        "bmi": float(bmi) if np.isfinite(bmi) else np.nan,
        "beta0_raw": float(beta0_raw) if np.isfinite(beta0_raw) else np.nan,
        "beta0_clipped": float(beta0_clipped) if np.isfinite(beta0_clipped) else np.nan,
    }

    return target, init_beta

# ---------------------------------------------------------
# 🚀 실행부
# ---------------------------------------------------------
def run_step1():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # 1) canonical heights
    canon_h = get_canonical_heights(MODEL_FOLDER, NUM_BETAS)

    # 2) CSV 목록 수집
    csv_paths = sorted(glob.glob(CSV_GLOB))
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files matched: {CSV_GLOB}")

    print("\n📂 CSV files to process:")
    for p in csv_paths:
        print("  -", os.path.basename(p))

    valid_targets = []
    valid_betas = []
    male_betas = []
    female_betas = []

    # 3) 파일별 처리
    for path in csv_paths:
        source_file = os.path.basename(path)
        age_low, age_high, file_gender = parse_filename_meta(path)

        if file_gender not in ["male", "female"]:
            print(f"\n⚠️ Filename pattern not matched: {source_file} (age/gender meta may be missing)")
        else:
            print(f"\n➡️ Processing: {source_file}  (age {age_low}-{age_high}, gender {file_gender})")

        df = pd.read_csv(path)

        for _, row in tqdm(df.iterrows(), total=len(df), desc=source_file):
            result = process_row(row, canon_h, source_file, age_low, age_high, file_gender)
            if result is None:
                continue
            target, beta = result
            valid_targets.append(target)
            valid_betas.append(beta)

            if target["gender"] == "male":
                male_betas.append(beta)
            else:
                female_betas.append(beta)

    # 4) 저장
    print("\n💾 Saving Artifacts...")

    df_targets = pd.DataFrame(valid_targets)
    df_targets.to_csv(os.path.join(OUTPUT_FOLDER, "targets_metadata.csv"), index=False)

    valid_betas_arr = np.stack(valid_betas, axis=0).astype(np.float32) if valid_betas else np.zeros((0, NUM_BETAS), dtype=np.float32)
    male_betas_arr  = np.stack(male_betas, axis=0).astype(np.float32)  if male_betas  else np.zeros((0, NUM_BETAS), dtype=np.float32)
    female_betas_arr= np.stack(female_betas, axis=0).astype(np.float32)if female_betas else np.zeros((0, NUM_BETAS), dtype=np.float32)

    np.save(os.path.join(OUTPUT_FOLDER, "init_betas_all.npy"), valid_betas_arr)
    np.save(os.path.join(OUTPUT_FOLDER, "init_betas_male.npy"), male_betas_arr)
    np.save(os.path.join(OUTPUT_FOLDER, "init_betas_female.npy"), female_betas_arr)

    print("-" * 60)
    print("🎉 Step 1 Complete!")
    print(f"   - Total Valid Rows: {len(valid_targets)}")
    print(f"   - Male Betas: {male_betas_arr.shape}, Female Betas: {female_betas_arr.shape}")
    print(f"   - Canonical Heights: {canon_h}")
    print(f"   - Output Folder: {OUTPUT_FOLDER}")
    print("👉 다음 Step 2는 targets_metadata.csv + init_betas_*.npy를 로드해서 시작하면 됩니다.")

if __name__ == "__main__":
    run_step1()
