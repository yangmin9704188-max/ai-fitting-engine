import torch
import smplx

MODEL_FOLDER = "../models"  # 기존에 쓰던 경로
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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

print("\n[1] Direct attribute check")
candidates = [
    "lbs_weights",
    "weights",
    "vert_weights",
    "vertex_weights",
    "skinning_weights",
]
for name in candidates:
    print(f"{name:20s} ->", hasattr(model, name))

print("\n[2] Buffer names containing 'weight'")
buf_names = [n for n, _ in model.named_buffers()]
for n in buf_names:
    if "weight" in n.lower():
        print(" -", n)

print("\n[3] Parameter names containing 'weight'")
param_names = [n for n, _ in model.named_parameters()]
for n in param_names:
    if "weight" in n.lower():
        print(" -", n)
