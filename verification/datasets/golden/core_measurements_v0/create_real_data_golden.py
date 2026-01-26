#!/usr/bin/env python3
"""
Create core_measurements_v0 Golden NPZ from curated_v0 real data (processed/m_standard).

Purpose: Round20 – real-data golden NPZ for validation. No generator changes (S0 frozen).
Input: curated_v0 parquet or m_standard CSV. Auto-discover with priority.
Output: golden_real_data_v0.npz with measurements, case_id, case_metadata, meta_unit="m".
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Repo root
_REPO_ROOT = Path(__file__).resolve().parents[4]

# Standard measurement keys (m/kg). Meta HUMAN_ID/SEX/AGE excluded from measurements dict.
_CORE_KEYS = [
    "HEIGHT_M", "WEIGHT_KG", "HEAD_CIRC_M", "NECK_CIRC_M", "NECK_WIDTH_M", "NECK_DEPTH_M",
    "SHOULDER_WIDTH_M", "CHEST_CIRC_M_REF", "BUST_CIRC_M", "UNDERBUST_CIRC_M",
    "UNDERBUST_WIDTH_M", "UNDERBUST_DEPTH_M", "CHEST_WIDTH_M", "CHEST_DEPTH_M",
    "WAIST_CIRC_M", "NAVEL_WAIST_CIRC_M", "ABDOMEN_CIRC_M",
    "WAIST_WIDTH_M", "WAIST_DEPTH_M", "NAVEL_WAIST_WIDTH_M", "NAVEL_WAIST_DEPTH_M",
    "HIP_CIRC_M", "HIP_WIDTH_M", "HIP_DEPTH_M", "UPPER_HIP_CIRC_M", "TOP_HIP_CIRC_M",
    "UPPER_ARM_CIRC_M", "ELBOW_CIRC_M", "WRIST_CIRC_M", "ARM_LEN_M",
    "CROTCH_HEIGHT_M", "KNEE_HEIGHT_M", "CROTCH_FB_LEN_M", "BACK_LEN_M", "FRONT_CENTER_LEN_M",
    "THIGH_CIRC_M", "MID_THIGH_CIRC_M", "KNEE_CIRC_M", "BELOW_KNEE_CIRC_M",
    "CALF_CIRC_M", "MIN_CALF_CIRC_M", "ANKLE_MAX_CIRC_M",
]
# Parquet may have extras (e.g. BICEPS_CIRC_M, FOREARM_CIRC_M); we include any *_M / WEIGHT_KG.
_SCHEMA_VERSION = "core_measurements_v0_real@1"


def _abs(p: Path) -> Path:
    return p.resolve()


def _discover_source(repo_root: Path) -> Tuple[Optional[Path], str, List[Path]]:
    """
    Discover curated_v0 m_standard source. Priority:
    1. data/processed/curated_v0/curated_v0.parquet
    2. data/processed/m_standard/*_m.csv (first found)

    Returns:
        (resolved_path, "parquet"|"csv", list of all paths checked)
    """
    checked: List[Path] = []
    # 1. Parquet
    p1 = _abs(repo_root / "data" / "processed" / "curated_v0" / "curated_v0.parquet")
    checked.append(p1)
    if p1.exists():
        return p1, "parquet", checked
    # 2. m_standard CSVs
    m_dir = _abs(repo_root / "data" / "processed" / "m_standard")
    checked.append(m_dir)
    if m_dir.exists():
        for f in sorted(m_dir.glob("*_m.csv")):
            checked.append(_abs(f))
            return _abs(f), "csv", checked
    return None, "", checked


def _load_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def _load_m_standard_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Map common m_standard column names -> standard keys if present
    renames = {
        "height": "HEIGHT_M",
        "chest_girth": "BUST_CIRC_M",
        "waist_girth": "WAIST_CIRC_M",
        "hip_girth": "HIP_CIRC_M",
    }
    rename = {k: v for k, v in renames.items() if k in df.columns}
    if rename:
        df = df.rename(columns=rename)
    return df


def _is_measurement_key(c: str) -> bool:
    return c in _CORE_KEYS or (c.endswith("_M") or c == "WEIGHT_KG") and c not in ("HUMAN_ID", "SEX", "AGE", "_source")


def _stable_hash(row: pd.Series, index: int) -> str:
    raw = str(index) + "|" + "|".join(f"{k}={v}" for k, v in sorted(row.dropna().items()) if isinstance(v, (int, float, str)))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _row_to_measurements_and_meta(
    row: pd.Series,
    index: int,
    human_id_col: Optional[str],
    source_label: str,
    keys: List[str],
) -> Tuple[Dict[str, Any], str, Dict[str, Any]]:
    measurements: Dict[str, Any] = {}
    warnings: List[str] = []

    for k in keys:
        if k not in row.index:
            continue
        v = row[k]
        if pd.isna(v) or (isinstance(v, float) and not np.isfinite(v)):
            measurements[k] = None
            warnings.append(f"VALUE_MISSING:{k}")
        else:
            try:
                measurements[k] = float(v)
            except (TypeError, ValueError):
                measurements[k] = None
                warnings.append(f"VALUE_MISSING:{k}")

    if human_id_col and human_id_col in row.index and pd.notna(row[human_id_col]):
        case_id = str(row[human_id_col]).strip()
    else:
        case_id = f"real_{_stable_hash(row, index)}"

    meta: Dict[str, Any] = {
        "source": source_label,
        "warnings": warnings,
        "provenance": {"source_path": source_label},
    }
    if "_source" in row.index and pd.notna(row["_source"]):
        meta["_source"] = str(row["_source"])

    return measurements, case_id, meta


def run(
    repo_root: Path,
    n_cases: int,
    out_npz: Path,
    case_ids_json: Optional[Path] = None,
) -> Tuple[int, Path, List[str]]:
    """
    Discover source, load, sample, build NPZ. Returns (n_cases, source_path_abs, warnings).
    
    Args:
        repo_root: Repository root path
        n_cases: Number of cases (ignored if case_ids_json is provided)
        out_npz: Output NPZ path
        case_ids_json: Optional path to case_ids manifest JSON (SSoT mode - bypasses sampling)
    """
    all_warnings: List[str] = []
    found, kind, checked = _discover_source(repo_root)

    if found is None:
        lines = [
            "ERROR: No curated_v0 / m_standard source found.",
            "Paths checked (absolute):",
        ] + [f"  - {_abs(p)}" for p in checked]
        msg = "\n".join(lines)
        print(msg)
        raise SystemExit(1)

    print(f"[SOURCE] Resolved: {_abs(found)}")
    print(f"[SOURCE] Kind: {kind}")
    for p in checked:
        print(f"[SOURCE] Checked: {_abs(p)}")

    if kind == "parquet":
        df = _load_parquet(found)
    else:
        df = _load_m_standard_csv(found)

    keys = [c for c in df.columns if _is_measurement_key(c)]
    human_id_col = "HUMAN_ID" if "HUMAN_ID" in df.columns else None

    # SSoT mode: --case_ids_json takes priority over n_cases/sampling
    if case_ids_json is not None:
        case_ids_json = _abs(case_ids_json) if not case_ids_json.is_absolute() else case_ids_json
        if not case_ids_json.exists():
            print(f"ERROR: case_ids manifest not found: {case_ids_json}")
            raise SystemExit(1)
        
        with open(case_ids_json, 'r', encoding='utf-8') as f:
            manifest_case_ids = json.load(f)
        
        if not isinstance(manifest_case_ids, list):
            print(f"ERROR: case_ids manifest must be a JSON array (list), got: {type(manifest_case_ids)}")
            raise SystemExit(1)
        
        print(f"[SSoT] Loading {len(manifest_case_ids)} case_ids from manifest: {case_ids_json}")
        
        # Filter df to only manifest case_ids (preserve order)
        if human_id_col and human_id_col in df.columns:
            # Use HUMAN_ID column for matching
            df_filtered = df[df[human_id_col].isin(manifest_case_ids)].copy()
            # Reorder to match manifest order
            case_id_to_index = {cid: idx for idx, cid in enumerate(manifest_case_ids)}
            df_filtered['_manifest_order'] = df_filtered[human_id_col].map(case_id_to_index)
            df_filtered = df_filtered.sort_values('_manifest_order').drop(columns=['_manifest_order'])
        else:
            # Fallback: use stable hash to match case_ids
            # This is less reliable but works if HUMAN_ID is not available
            df_filtered_list = []
            for manifest_cid in manifest_case_ids:
                # Try to find row that would generate this case_id
                # This is approximate - ideally HUMAN_ID should be used
                matching_rows = df[df.apply(
                    lambda row: f"real_{_stable_hash(row, row.name)}" == manifest_cid,
                    axis=1
                )]
                if len(matching_rows) > 0:
                    df_filtered_list.append(matching_rows.iloc[0])
            
            if len(df_filtered_list) < len(manifest_case_ids):
                missing = set(manifest_case_ids) - {f"real_{_stable_hash(row, row.name)}" for row in df_filtered_list}
                print(f"ERROR: {len(missing)} case_ids from manifest not found in source:")
                for cid in list(missing)[:10]:  # Show first 10
                    print(f"  - {cid}")
                if len(missing) > 10:
                    print(f"  ... and {len(missing) - 10} more")
                raise SystemExit(1)
            
            df_filtered = pd.DataFrame(df_filtered_list).reset_index(drop=True)
        
        # Verify all manifest case_ids are present (reproducibility enforcement)
        if human_id_col and human_id_col in df_filtered.columns:
            found_case_ids = set(df_filtered[human_id_col].astype(str))
            manifest_case_ids_set = set(str(cid) for cid in manifest_case_ids)
            missing = manifest_case_ids_set - found_case_ids
            if missing:
                print(f"ERROR: {len(missing)} case_ids from manifest not found in source (reproducibility violation):")
                for cid in list(missing)[:10]:  # Show first 10
                    print(f"  - {cid}")
                if len(missing) > 10:
                    print(f"  ... and {len(missing) - 10} more")
                raise SystemExit(1)
        
        df = df_filtered.reset_index(drop=True)
        print(f"[SSoT] Filtered to {len(df)} cases (manifest order preserved)")
    else:
        # Normal sampling mode (original behavior)
        if n_cases < len(df):
            df = df.sample(n=n_cases, random_state=42).reset_index(drop=True)
        else:
            df = df.reset_index(drop=True)

    n = len(df)
    measurements_list: List[Dict[str, Any]] = []
    case_ids: List[str] = []
    case_metas: List[Dict[str, Any]] = []

    for i in range(n):
        row = df.iloc[i]
        meas, cid, meta = _row_to_measurements_and_meta(
            row, i, human_id_col, source_label=str(_abs(found)), keys=keys
        )
        measurements_list.append(meas)
        case_ids.append(cid)
        case_metas.append(meta)

    out_npz = _abs(Path(out_npz))
    out_npz.parent.mkdir(parents=True, exist_ok=True)

    meas_arr = np.empty(n, dtype=object)
    meas_arr[:] = measurements_list
    case_id_arr = np.array(case_ids, dtype=object)
    case_class_arr = np.array(["curated_real"] * n, dtype=object)
    meta_arr = np.empty(n, dtype=object)
    meta_arr[:] = case_metas

    created_at = datetime.now(timezone.utc).isoformat()

    np.savez(
        str(out_npz),
        measurements=meas_arr,
        case_id=case_id_arr,
        case_class=case_class_arr,
        case_metadata=meta_arr,
        meta_unit=np.array("m", dtype=object),
        schema_version=np.array(_SCHEMA_VERSION, dtype=object),
        created_at=np.array(created_at, dtype=object),
        source_path_abs=np.array(str(_abs(found)), dtype=object),
    )

    print(f"[NPZ] Written: {out_npz}")
    print(f"[NPZ] Cases: {n}, meta_unit: m, schema_version: {_SCHEMA_VERSION}")
    return n, _abs(found), all_warnings


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Create core_measurements_v0 Golden NPZ from curated_v0 real data (Round20/22)."
    )
    ap.add_argument(
        "--n_cases",
        type=int,
        default=200,
        help="Number of cases to include (default: 200). Ignored if --case_ids_json is provided.",
    )
    ap.add_argument(
        "--out_npz",
        type=str,
        default=str(Path(__file__).parent / "golden_real_data_v0.npz"),
        help="Output NPZ path (default: .../core_measurements_v0/golden_real_data_v0.npz)",
    )
    ap.add_argument(
        "--case_ids_json",
        type=str,
        default=None,
        help="Path to case_ids manifest JSON (SSoT mode - bypasses sampling, preserves order). Takes priority over --n_cases.",
    )
    args = ap.parse_args()

    out = Path(args.out_npz)
    if not out.is_absolute():
        out = _REPO_ROOT / out

    case_ids_json_path = None
    if args.case_ids_json:
        case_ids_json_path = Path(args.case_ids_json)
        if not case_ids_json_path.is_absolute():
            case_ids_json_path = _REPO_ROOT / case_ids_json_path

    n, src, _ = run(_REPO_ROOT, args.n_cases, out, case_ids_json=case_ids_json_path)
    print(f"[DONE] {n} cases -> {out.resolve()}")
    print(f"[DONE] Source: {src}")


if __name__ == "__main__":
    main()
