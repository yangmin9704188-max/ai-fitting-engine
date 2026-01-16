import torch
import smplx
import os
import numpy as np
from core.pose_policy import PoseNormalizer

# =========================
# Config
# =========================
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
MODEL_FOLDER = './models'
OUTPUT_DIR = './pose_debug'
os.makedirs(OUTPUT_DIR, exist_ok=True)

SYMMETRY_THRESH = 0.02  # ✅ 정책 회귀 임계값(낮을수록 대칭)
SAVE_OBJ = True         # 필요 없으면 False로 꺼도 됨

print(f"⚙️ 검증 디바이스: {DEVICE}")

def save_obj(vertices, faces, filename):
    with open(filename, 'w') as f:
        f.write(f"# Debug Pose: {os.path.basename(filename)}\n")

        if torch.is_tensor(vertices):
            v = vertices.detach().cpu().numpy()
        else:
            v = vertices

        # [B,N,3] -> [N,3] if B=1
        if v.ndim == 3 and v.shape[0] == 1:
            v = v.squeeze(0)

        v = v.astype(np.float32)

        for p in v:
            f.write(f"v {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}\n")

        if torch.is_tensor(faces):
            faces_np = faces.detach().cpu().numpy()
        else:
            faces_np = faces

        for face in faces_np:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

    print(f"   💾 저장: {filename}")

def symmetry_score_from_vertices(vertices_tensor):
    """
    좌/우 팔 대칭 점수(낮을수록 좋음)
    - 팔 영역을 |x| 상위 8%로 근사
    - 좌/우 각각 y 최대값 차이 절댓값
    """
    v = vertices_tensor.detach()
    if v.ndim == 3:
        v = v[0]  # (N,3)
    x = v[:, 0]
    y = v[:, 1]

    absx = torch.abs(x)
    thr = torch.quantile(absx, 0.92)
    mask_arms = absx >= thr

    mask_left = mask_arms & (x < 0)
    mask_right = mask_arms & (x > 0)

    if mask_left.sum() < 50 or mask_right.sum() < 50:
        return float('inf')

    maxY_left = y[mask_left].max().item()
    maxY_right = y[mask_right].max().item()
    return abs(maxY_left - maxY_right)

def fail(msg):
    print(f"❌ FAIL: {msg}")
    raise SystemExit(1)

def verify_pose_policy():
    print("🧪 [Pose Policy Verification] (FROZEN A-Pose)")

    # 1) 모델 로드
    try:
        model = smplx.create(
            MODEL_FOLDER,
            model_type='smplx',
            gender='male',
            use_pca=False,
            num_betas=10,
            ext='pkl'
        ).to(DEVICE)
        model.eval()
    except Exception as e:
        fail(f"Model load failed: {e}")

    normalizer = PoseNormalizer(device=DEVICE)

    with torch.no_grad():
        # [A] Baseline (optional)
        betas1 = torch.zeros((1, 10), dtype=torch.float32, device=DEVICE)
        out_t = normalizer.run_forward(model, betas1, {}, enforce_policy_apose=False)
        if SAVE_OBJ:
            save_obj(out_t.vertices, model.faces, os.path.join(OUTPUT_DIR, '00_Baseline_TPose.obj'))

        # [B] Policy A-Pose (batch=1)
        out_ap1 = normalizer.run_forward(model, betas1, {}, enforce_policy_apose=True)
        score1 = symmetry_score_from_vertices(out_ap1.vertices)
        print(f"   - Policy A-Pose (B=1) symmetry_score = {score1:.6f}")

        if score1 > SYMMETRY_THRESH:
            fail(f"Symmetry score too high for B=1: {score1:.6f} > {SYMMETRY_THRESH}")

        if SAVE_OBJ:
            save_obj(out_ap1.vertices, model.faces, os.path.join(OUTPUT_DIR, '02_Policy_APose_B1.obj'))

        # [C] Policy A-Pose (batch=2)
        betas2 = torch.zeros((2, 10), dtype=torch.float32, device=DEVICE)
        out_ap2 = normalizer.run_forward(model, betas2, {}, enforce_policy_apose=True)

        # batch 첫 샘플 기준으로 점수 체크(정책 동일성 확인 목적)
        score2 = symmetry_score_from_vertices(out_ap2.vertices[0:1])
        print(f"   - Policy A-Pose (B=2, sample0) symmetry_score = {score2:.6f}")

        if score2 > SYMMETRY_THRESH:
            fail(f"Symmetry score too high for B=2: {score2:.6f} > {SYMMETRY_THRESH}")

        if SAVE_OBJ:
            save_obj(out_ap2.vertices[0:1], model.faces, os.path.join(OUTPUT_DIR, '03_Policy_APose_B2_sample0.obj'))

    print("✅ PASS: Pose policy is stable and within threshold.")
    print(f"👉 Outputs in: {OUTPUT_DIR}")

if __name__ == "__main__":
    verify_pose_policy()
