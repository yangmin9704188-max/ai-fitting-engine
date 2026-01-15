import torch
import smplx
from step2_utils import PoseNormalizer
from bench_utils import BenchTimer, print_bench

# ===== 설정 =====
MODEL_FOLDER = "./models"  # 당신 경로에 맞게 조정
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def dummy_shoulder_width(vertices):
    """
    아직 어깨 측정 함수가 없으니, '측정이란 이런 호출이다'를 보여주는 더미 함수.
    실제로는 나중에 shoulder_width(vertices, model)로 교체하면 됨.
    """
    v = vertices
    if v.ndim == 3:
        v = v[0]
    # 간단 계산(헛값이어도 됨): x 범위 길이
    return (v[:, 0].max() - v[:, 0].min()).item()

def main():
    print(f"DEVICE = {DEVICE}")

    # 1) 모델 로드
    model = smplx.create(
        MODEL_FOLDER,
        model_type="smplx",
        gender="male",
        use_pca=False,
        num_betas=10,
        ext="pkl"
    ).to(DEVICE)
    model.eval()

    # 2) normalizer + 입력
    normalizer = PoseNormalizer(device=DEVICE)
    betas = torch.zeros((1, 10), dtype=torch.float32, device=DEVICE)

    timer = BenchTimer(device=DEVICE)

    # --- 벤치 1: forward만 ---
    def bench_forward():
        out = normalizer.run_forward(model, betas, {}, enforce_policy_apose=True)
        _ = out.vertices.shape  # 최적화 방지용 접근

    # --- 벤치 2: forward + 측정 ---
    def bench_forward_plus_measure():
        out = normalizer.run_forward(model, betas, {}, enforce_policy_apose=True)
        w = dummy_shoulder_width(out.vertices)
        _ = float(w)

    r1 = timer.run("smplx_forward(B=1)", bench_forward, warmup=10, repeat=50)
    r2 = timer.run("forward+measure(B=1)", bench_forward_plus_measure, warmup=10, repeat=50)

    print_bench([r1, r2])

    # 측정만의 순수 비용도 보고 싶으면:
    # (forward+measure) - (forward) 정도로 대략 추정 가능

if __name__ == "__main__":
    main()
