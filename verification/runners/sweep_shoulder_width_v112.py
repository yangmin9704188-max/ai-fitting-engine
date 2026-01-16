# sweep_shoulder_width_v112.py
# Parameter sweep for Shoulder Width v1.1.2 to evaluate numeric stability
# before policy freeze.

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from itertools import product
import numpy as np

# Add core/measurements to path
current_dir = os.path.dirname(os.path.abspath(__file__))
target_dir = os.path.join(current_dir, "../core/measurements")
sys.path.insert(0, target_dir)

from shoulder_width_v112 import (
    measure_shoulder_width_v112,
    ShoulderWidthV112Config,
)

# ---------------------------------------------------------
# Joint ID Mapping for SMPL-X (Standard)
# ---------------------------------------------------------
SMPLX_JOINT_IDS = {
    "L_shoulder": 16,
    "R_shoulder": 17,
    "L_elbow": 18,
    "R_elbow": 19,
    "L_wrist": 20,
    "R_wrist": 21,
}

# ---------------------------------------------------------
# Parameter sweep ranges
# ---------------------------------------------------------
R0_RATIOS = [0.26, 0.30, 0.33, 0.36]
R1_RATIOS = [0.18, 0.22, 0.26]
CAP_QUANTILES = [0.88, 0.90, 0.92, 0.94]


def _load_npz(path: str):
    """Load NPZ file and extract required arrays."""
    data = np.load(path, allow_pickle=False)
    keys = set(data.files)
    for k in ("verts", "lbs_weights", "joints_xyz"):
        if k not in keys:
            raise KeyError(f"NPZ missing required key: {k}. Found keys: {sorted(keys)}")
    return data["verts"], data["lbs_weights"], data["joints_xyz"]


def _ensure_batched(verts, w, j):
    """Ensure all arrays are batched (T, ...) format."""
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


def _compute_stats(widths: np.ndarray, fallback_flags: np.ndarray):
    """Compute statistics for a configuration."""
    valid = np.isfinite(widths)
    widths_valid = widths[valid]
    fallback_valid = fallback_flags[valid]

    n = int(widths_valid.size)
    if n == 0:
        return {
            "mean_width": float("nan"),
            "std_width": float("nan"),
            "cv_pct": float("nan"),
            "fallback_rate_pct": float("nan"),
            "n_valid": 0,
            "n_total": int(widths.size),
        }

    widths64 = widths_valid.astype(np.float64)
    mean = float(widths64.mean())
    std = float(widths64.std(ddof=1)) if n >= 2 else 0.0
    cv_pct = (std / mean) * 100.0 if mean > 1e-12 else 0.0

    fb_count = int(fallback_valid.sum())
    fb_rate = (fb_count / n) * 100.0 if n > 0 else 0.0

    return {
        "mean_width": mean,
        "std_width": std,
        "cv_pct": cv_pct,
        "fallback_rate_pct": fb_rate,
        "n_valid": n,
        "n_total": int(widths.size),
    }


def _run_config(verts, w, j, r0_ratio, r1_ratio, cap_quantile):
    """Run measurement for one configuration across all frames."""
    cfg = ShoulderWidthV112Config(
        r0_ratio=r0_ratio,
        r1_ratio=r1_ratio,
        cap_quantile=cap_quantile,
    )

    widths = []
    fallback_flags = []
    err_count = 0

    for t in range(verts.shape[0]):
        try:
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
        except Exception:
            err_count += 1
            widths.append(np.nan)
            fallback_flags.append(0)

    widths = np.array(widths, dtype=np.float64)
    fallback_flags = np.array(fallback_flags, dtype=np.int32)

    stats = _compute_stats(widths, fallback_flags)
    stats["error_count"] = err_count

    return stats


def _write_csv(csv_path: str, rows: list[dict]):
    """Write results to CSV file."""
    out = Path(csv_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "r0_ratio",
        "r1_ratio",
        "cap_quantile",
        "mean_width",
        "std_width",
        "cv_pct",
        "fallback_rate_pct",
        "n_valid",
        "n_total",
        "error_count",
    ]

    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _print_top5(rows: list[dict]):
    """Print top 5 most stable configurations."""
    # Filter valid configs (finite CV, low fallback preferred)
    valid = [
        r
        for r in rows
        if np.isfinite(r["cv_pct"]) and r["n_valid"] > 0
    ]

    if not valid:
        print("\n⚠️  No valid configurations found.")
        return

    # Sort by CV (ascending), then by fallback rate (ascending)
    sorted_configs = sorted(
        valid,
        key=lambda x: (x["cv_pct"], x["fallback_rate_pct"]),
    )

    top5 = sorted_configs[:5]

    print("\n" + "=" * 80)
    print(" [ Top 5 Most Stable Configurations ]")
    print("=" * 80)
    print(
        f"{'r0_ratio':>8s} {'r1_ratio':>8s} {'cap_quantile':>12s} "
        f"{'CV %':>8s} {'Fallback %':>12s} {'Mean Width':>12s} {'Std':>10s}"
    )
    print("-" * 80)

    for cfg in top5:
        print(
            f"{cfg['r0_ratio']:8.2f} {cfg['r1_ratio']:8.2f} {cfg['cap_quantile']:12.2f} "
            f"{cfg['cv_pct']:8.4f} {cfg['fallback_rate_pct']:12.4f} "
            f"{cfg['mean_width']:12.6f} {cfg['std_width']:10.6f}"
        )

    print("=" * 80 + "\n")


def main():
    ap = argparse.ArgumentParser(
        description="Parameter sweep for Shoulder Width v1.1.2"
    )
    ap.add_argument(
        "--npz",
        type=str,
        required=True,
        help="Path to NPZ containing verts/lbs_weights/joints_xyz",
    )
    ap.add_argument(
        "--out_csv",
        type=str,
        default="verification/reports/sweep_shoulder_v112.csv",
        help="Output CSV path",
    )
    args = ap.parse_args()

    # Load data
    print(f"Loading NPZ: {args.npz}")
    verts, w, j = _load_npz(args.npz)
    verts, w, j = _ensure_batched(verts, w, j)
    n_frames = verts.shape[0]
    print(f"Loaded {n_frames} frames")

    # Generate all parameter combinations
    param_combos = list(product(R0_RATIOS, R1_RATIOS, CAP_QUANTILES))
    n_configs = len(param_combos)
    print(f"\nSweeping {n_configs} configurations...")
    print(f"  r0_ratio: {R0_RATIOS}")
    print(f"  r1_ratio: {R1_RATIOS}")
    print(f"  cap_quantile: {CAP_QUANTILES}")

    # Run sweep
    results = []
    for idx, (r0, r1, cap_q) in enumerate(param_combos, 1):
        print(f"\n[{idx}/{n_configs}] r0={r0:.2f}, r1={r1:.2f}, cap_quantile={cap_q:.2f}")

        stats = _run_config(verts, w, j, r0, r1, cap_q)

        row = {
            "r0_ratio": r0,
            "r1_ratio": r1,
            "cap_quantile": cap_q,
            "mean_width": stats["mean_width"],
            "std_width": stats["std_width"],
            "cv_pct": stats["cv_pct"],
            "fallback_rate_pct": stats["fallback_rate_pct"],
            "n_valid": stats["n_valid"],
            "n_total": stats["n_total"],
            "error_count": stats["error_count"],
        }
        results.append(row)

        print(
            f"  → CV: {stats['cv_pct']:.4f}%, "
            f"Fallback: {stats['fallback_rate_pct']:.4f}%, "
            f"Valid: {stats['n_valid']}/{stats['n_total']}"
        )

    # Write CSV
    _write_csv(args.out_csv, results)
    print(f"\n✅ CSV saved: {args.out_csv}")

    # Print top 5
    _print_top5(results)


if __name__ == "__main__":
    main()
