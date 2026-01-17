import torch
import smplx
import numpy as np # numpy는 자주 쓰이니 위에서 import

# verification 폴더에서 실행하므로 상위 models
MODEL_FOLDER = "../models"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# SMPL 계열에서 "기본 바디 관절 22개" 순서
SMPL_BODY_22 = {
    0: "pelvis", 1: "left_hip", 2: "right_hip", 3: "spine1",
    4: "left_knee", 5: "right_knee", 6: "spine2", 7: "left_ankle",
    8: "right_ankle", 9: "spine3", 10: "left_foot", 11: "right_foot",
    12: "neck", 13: "left_collar", 14: "right_collar", 15: "head",
    16: "left_shoulder", 17: "right_shoulder", 18: "left_elbow", 19: "right_elbow",
    20: "left_wrist", 21: "right_wrist",
}

def main():
    print("DEVICE:", DEVICE)

    model = smplx.create(
        MODEL_FOLDER,
        model_type="smplx",
        gender="male",
        use_pca=False,
        num_betas=10,
        ext="pkl",
    ).to(DEVICE)
    model.eval()

    # 1) lbs_weights shape 확인
    w = model.lbs_weights
    print("\n[lbs_weights]")
    print(" - dtype:", w.dtype)
    print(" - device:", w.device)
    print(" - shape:", tuple(w.shape), "  (expected: (V, J))")

    V = w.shape[0]
    J = w.shape[1]
    print(f" - V (num vertices) = {V}")
    print(f" - J (num joints for weights) = {J}")

    # 2) SMPL-X forward 한번 해서 joints 출력 shape 확인
    betas = torch.zeros((1, 10), dtype=torch.float32, device=DEVICE)
    with torch.no_grad():
        out = model(betas=betas)
    
    print("\n[forward output]")
    print(" - vertices:", tuple(out.vertices.shape))
    if hasattr(out, "joints") and out.joints is not None:
        print(" - joints:", tuple(out.joints.shape))
    else:
        print(" - joints: (not provided by this model output)")

    # 3) 우리가 쓸 “팔 체인 joint index”가 weights 범위 내인지 확인
    left_arm = [16, 18, 20]
    right_arm = [17, 19, 21]
    print("\n[arm joint indices sanity]")
    print(" - left_arm:", left_arm, "=> names:", [SMPL_BODY_22[i] for i in left_arm])
    print(" - right_arm:", right_arm, "=> names:", [SMPL_BODY_22[i] for i in right_arm])

    assert max(left_arm + right_arm) < J, (
        f"lbs_weights joint dim J={J} is too small for expected indices. "
    )
    print(" ✅ arm indices are within lbs_weights joint dimension.")

    # 4) “팔 영향이 큰 vertex”가 실제로 존재하는지 간단 체크
    armL = w[:, left_arm].sum(dim=1)
    armR = w[:, right_arm].sum(dim=1)
    print("\n[arm influence quick stats]")
    for name, t in [("armL", armL), ("armR", armR)]:
        print(
            f" - {name}: min={t.min().item():.6f}, "
            f"p50={t.median().item():.6f}, max={t.max().item():.6f}"
        )

    # ---------------------------------------------------------
    # 5) [Visual Debug] lbs_weights 연속 시각화 3종 저장 (Phase 2)
    # 목적:
    # - 삼각근(어깨 캡) vs 팔(상완/전완)이 weights 기준으로 어떻게 분류되는지 확인
    # ---------------------------------------------------------
    print("\n[Visual Debug] Saving continuous arm-weight meshes...")

    try:
        import trimesh
        import numpy as np

        def to_red_colormap(w_np: np.ndarray) -> np.ndarray:
            """
            w_np: (V,) float
            연속값을 0~1로 정규화해서 '빨강 강도'로 표시한다.
            threshold(mask)를 쓰지 않아 얼룩 현상을 방지한다.
            """
            wv = w_np.astype(np.float64)
            wv = (wv - wv.min()) / (wv.max() - wv.min() + 1e-8)

            colors = np.ones((wv.shape[0], 4), dtype=np.uint8)
            colors[:] = np.array([200, 200, 200, 255], dtype=np.uint8)

            colors[:, 0] = 255
            colors[:, 1] = (255 * (1.0 - wv)).astype(np.uint8)
            colors[:, 2] = (255 * (1.0 - wv)).astype(np.uint8)
            return colors

        # lbs_weights → numpy
        w_np = model.lbs_weights.detach().cpu().numpy()  # (V, J)

        # 포즈 영향 제거용 template
        v_template = model.v_template.detach().cpu().numpy()
        faces = model.faces

        # 3종 weight 분해
        w16 = w_np[:, 16]                     # left_shoulder root
        w1820 = w_np[:, 18] + w_np[:, 20]     # distal arm (elbow + wrist)
        wsum = w_np[:, 16] + w1820            # combined

        items = [
            ("debug_w16_shoulder.obj", w16),
            ("debug_w1820_distal_arm.obj", w1820),
            ("debug_w16_18_20_sum.obj", wsum),
        ]

        for fname, vec in items:
            colors = to_red_colormap(vec)
            mesh = trimesh.Trimesh(
                vertices=v_template,
                faces=faces,
                vertex_colors=colors,
                process=False
            )
            mesh.export(fname)
            print(f" 🎨 saved: {fname}")

        print(" ✅ Open the OBJ files and compare:")
        print("   - debug_w16_shoulder.obj")
        print("   - debug_w1820_distal_arm.obj")
        print("   - debug_w16_18_20_sum.obj")

    except ImportError:
        print(" ⚠️ trimesh not installed. Skipping visualization.")
    except Exception as e:
        print(f" ⚠️ Error during visualization: {e}")


if __name__ == "__main__":
    main()