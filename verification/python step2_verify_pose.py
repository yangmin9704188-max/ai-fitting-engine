# step2_verify_pose.py
# Numeric stability verification for Shoulder Width v1.1.2
# Adds:
# - fallback rate report
# - per-frame width logging to CSV

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(current_dir, "../core/measurements")
sys.path.append(target_dir)

from shoulder_width_v112 import (
    measure_shoulder_width_v112,
    ShoulderWidthV112Config,
)

# ---------------------------------------------------------
# [IMPORTANT] Joint ID Mapping for SMPL-X (Standard)
# If you use a custom rig, UPDATE these indices!
# ---------------------------------------------------------
SMPLX_JOINT_IDS = {
    "L_shoulder": 16,  # L_Shoulder
    "R_shoulder": 17,  # R_Shoulder
    "L_elbow": 18,     # L_Elbow
    "R_elbow": 19,     # R_Elbow
    "L_wrist": 20,     # L_Wrist
    "R_wrist": 21,     # R_Wrist
}


def _load_npz(path: str):
    data = np.load(path, allow_pickle=False)
    keys = set(data.files)
    for k in ("verts", "lbs_weights", "joints_xyz"):
        if k not in keys:
            raise KeyError(f"NPZ missing required key: {k}. Found keys: {sorted(keys)}")
    return data["verts"], data["lbs_weights"], data["joints_xyz"]


def _ensure_batched(verts, w, j):
    # verts: (T,N,3) or (N,3)
    if verts.ndim == 2:
        verts = verts[None, ...]
    if verts.ndim != 3 or verts.shape[-1] != 3:
        raise ValueError(f"verts must be (T,N,3) or (N,3), got {verts.shape}")
    T = verts.shape[0]

    # lbs_weights: (T,N,J) or (N,J)
    if w.ndim == 2:
        w = np.broadcast_to(w[None, ...], (T,) + w.shape)
    elif w.ndim == 3:
        if w.shape[0] != T:
            raise ValueError("lbs_weights T must match verts T.")
    else:
        raise ValueError(f"lbs_weights must be (N,J) or (T,N,J), got {w.shape}")

    # joints_xyz: (T,J,3) or (J,3)
    if j.ndim == 2:
        j = np.broadcast_to(j[None, ...], (T,) + j.shape)
    elif j.ndim == 3:
        if j.shape[0] != T:
            raise ValueError("joints_xyz T must match verts T.")
    else:
        raise ValueError(f"joints_xyz must be (J,3) or (T,J,3), got {j.shape}")

    return verts, w, j


def _stats(widths: np.ndarray):
    widths64 = widths.astype(np.float64)
    mean = float(widths64.mean()) if widths64.size else float("nan")
    std = float(widths64.std(ddof=1)) if widths64.size >= 2 else 0.0
    cv_pct = (std / mean) * 100.0 if mean > 1e-12 else 0.0
    w_min = float(widths64.min()) if widths64.size else float("nan")
    w_max = float(widths64.max()) if widths64.size else float("nan")
    max_dev = max(abs(w_min - mean), abs(w_max - mean)) if widths64.size else float("nan")
    return mean, std, cv_pct, w_min, w_max, max_dev


def _print_report(widths: np.ndarray, fallback_flags: np.ndarray, err_count: int):
    mean, std, cv_pct, w_min, w_max, max_dev = _stats(widths)

    n = int(widths.size)
    fb = int(fallback_flags.sum())
    fb_rate = (fb / n) * 100.0 if n > 0 else 0.0

    print("\n" + "=" * 62)
    print(" [ Shoulder Width v1.1.2 Stability Report ]")
    print("=" * 62)
    print(f"Frames processed           : {n}")
    print(f"Errors (exceptions)        : {err_count}")
    print(f"Fallback frames            : {fb} ({fb_rate:.4f} %)")
    print("-" * 62)
    print(f"Mean width                 : {mean:.6f} m")
    print(f"Std dev (ddof=1)           : {std:.6f} m")
    print(f"CV (std/mean)              : {cv_pct:.4f} %  <-- lower is better")
    print(f"Min / Max                  : {w_min:.6f} / {w_max:.6f} m")
    print(f"Max deviation from mean    : {max_dev:.6f} m")
    print("=" * 62 + "\n")


def _write_csv(csv_path: str, rows: list[dict]):
    out = Path(csv_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "frame_idx",
        "width_m",
        "fallback",
        "error",
        "note",
    ]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--npz", type=str, required=True, help="Path to NPZ containing verts/lbs_weights/joints_xyz")
    ap.add_argument("--csv_out", type=str, default="widths_v112.csv", help="Output CSV path")
    ap.add_argument("--dump_debug_first", action="store_true", help="Save debug info for first successful frame")
    args = ap.parse_args()

    verts, w, j = _load_npz(args.npz)
    verts, w, j = _ensure_batched(verts, w, j)

    cfg = ShoulderWidthV112Config()

    print(f"Running v1.1.2 on {verts.shape[0]} frames")
    print(f"Config: distal_w={cfg.distal_w_threshold}, "
          f"s=[{cfg.s_min_ratio},{cfg.s_max_ratio}], "
          f"r0={cfg.r0_ratio}, r1={cfg.r1_ratio}, "
          f"q={cfg.cap_quantile}, min_pts={cfg.min_cap_points}")

    widths = []
    fallback_flags = []
    rows = []

    err_count = 0
    dumped_first = False

    for t in range(verts.shape[0]):
        try:
            # We use return_debug=True for each frame to reliably capture fallback flag.
            # This is intended for verification, not for production.
            width, debug = measure_shoulder_width_v112(
                verts=verts[t],
                lbs_weights=w[t],
                joints_xyz=j[t],
                joint_ids=SMPLX_JOINT_IDS,
                cfg=cfg,
                return_debug=True,
            )
            fb = int(np.array(debug.get("fallback", [0])).reshape(-1)[0])
            widths.append(width)
            fallback_flags.append(fb)

            rows.append({
                "frame_idx": t,
                "width_m": f"{float(width):.9f}",
                "fallback": fb,
                "error": 0,
                "note": "",
            })

            if args.dump_debug_first and (not dumped_first):
                # Save a single debug dump for inspection
                out_path = "debug_v112_firstframe.npz"
                np.savez(out_path, **debug)
                print(f"Saved first debug: {out_path}")
                dumped_first = True

        except Exception as e:
            err_count += 1
            # For CSV alignment, log NaN width with error flag
            widths.append(np.nan)
            fallback_flags.append(0)
            rows.append({
                "frame_idx": t,
                "width_m": "nan",
                "fallback": 0,
                "error": 1,
                "note": str(e).replace("\n", " "),
            })

    widths = np.array(widths, dtype=np.float64)
    fallback_flags = np.array(fallback_flags, dtype=np.int32)

    # Exclude NaNs from numeric stats
    valid = np.isfinite(widths)
    widths_valid = widths[valid]
    fallback_valid = fallback_flags[valid]

    _print_report(widths_valid.astype(np.float32), fallback_valid, err_count)
    _write_csv(args.csv_out, rows)

    print(f"CSV saved: {args.csv_out}")
    print("CSV columns: frame_idx, width_m, fallback, error, note")


if __name__ == "__main__":
    main()
