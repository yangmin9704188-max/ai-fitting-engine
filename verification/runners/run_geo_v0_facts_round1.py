#!/usr/bin/env python3
"""
Geometric v0 Facts-Only Runner (Round 1)

Purpose: Collect measurement results + metadata from core_measurements_v0
and generate facts-only summary report.
"""

from __future__ import annotations

import os
import sys
import json
import argparse
import numpy as np
import csv
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import subprocess

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from core.measurements.core_measurements_v0 import (
    measure_circumference_v0_with_metadata,
    measure_width_depth_v0_with_metadata,
    measure_height_v0_with_metadata,
    measure_arm_length_v0_with_metadata,
    create_weight_metadata,
    MeasurementResult,
)

# This round's keys
CIRCUMFERENCE_KEYS = [
    "NECK_CIRC_M", "BUST_CIRC_M", "UNDERBUST_CIRC_M", 
    "WAIST_CIRC_M", "HIP_CIRC_M", "THIGH_CIRC_M", "MIN_CALF_CIRC_M"
]

WIDTH_DEPTH_KEYS = [
    "CHEST_WIDTH_M", "CHEST_DEPTH_M",
    "WAIST_WIDTH_M", "WAIST_DEPTH_M",
    "HIP_WIDTH_M", "HIP_DEPTH_M"
]

HEIGHT_KEYS = ["HEIGHT_M", "CROTCH_HEIGHT_M", "KNEE_HEIGHT_M"]

ALL_KEYS = CIRCUMFERENCE_KEYS + WIDTH_DEPTH_KEYS + HEIGHT_KEYS + ["ARM_LEN_M", "WEIGHT_KG"]


def get_git_sha() -> Optional[str]:
    """Get current git SHA if available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def load_npz_dataset(npz_path: str) -> tuple[List[np.ndarray], List[str]]:
    """Load NPZ dataset and return (verts_list, case_ids)."""
    data = np.load(npz_path, allow_pickle=True)
    
    if "verts" in data:
        verts_array = data["verts"]
        if verts_array.dtype == object:
            # Variable-length arrays
            verts_list = [verts_array[i] for i in range(len(verts_array))]
        else:
            # Fixed shape: (N, V, 3) -> list of (V, 3)
            if verts_array.ndim == 3:
                verts_list = [verts_array[i] for i in range(verts_array.shape[0])]
            else:
                verts_list = [verts_array]
        
        case_ids = data.get("case_id", [f"case_{i}" for i in range(len(verts_list))])
        if isinstance(case_ids, np.ndarray):
            case_ids = case_ids.tolist()
        
        return verts_list, case_ids
    else:
        raise ValueError(f"NPZ file missing 'verts' key. Found keys: {list(data.keys())}")


def measure_all_keys(verts: np.ndarray, case_id: str) -> Dict[str, MeasurementResult]:
    """Measure all keys for a single case."""
    results = {}
    
    # Circumference group
    for key in CIRCUMFERENCE_KEYS:
        try:
            result = measure_circumference_v0_with_metadata(verts, key)
            results[key] = result
        except Exception as e:
            # Record failure
            results[key] = MeasurementResult(
                standard_key=key,
                value_m=float('nan'),
                metadata={
                    "standard_key": key,
                    "value_m": float('nan'),
                    "unit": "m",
                    "precision": 0.001,
                    "warnings": [f"EXEC_FAIL: {str(e)}"],
                    "version": {"semantic_tag": "semantic-v0", "schema_version": "metadata-schema-v0"}
                }
            )
    
    # Width/Depth group
    for key in WIDTH_DEPTH_KEYS:
        try:
            result = measure_width_depth_v0_with_metadata(verts, key, proxy_used=False)
            results[key] = result
        except Exception as e:
            results[key] = MeasurementResult(
                standard_key=key,
                value_m=float('nan'),
                metadata={
                    "standard_key": key,
                    "value_m": float('nan'),
                    "unit": "m",
                    "precision": 0.001,
                    "warnings": [f"EXEC_FAIL: {str(e)}"],
                    "version": {"semantic_tag": "semantic-v0", "schema_version": "metadata-schema-v0"}
                }
            )
    
    # Height group
    for key in HEIGHT_KEYS:
        try:
            result = measure_height_v0_with_metadata(verts, key)
            results[key] = result
        except Exception as e:
            results[key] = MeasurementResult(
                standard_key=key,
                value_m=float('nan'),
                metadata={
                    "standard_key": key,
                    "value_m": float('nan'),
                    "unit": "m",
                    "precision": 0.001,
                    "warnings": [f"EXEC_FAIL: {str(e)}"],
                    "version": {"semantic_tag": "semantic-v0", "schema_version": "metadata-schema-v0"}
                }
            )
    
    # ARM_LEN_M (requires joints, simplified for now)
    try:
        result = measure_arm_length_v0_with_metadata(verts, joints_xyz=None, joint_ids=None)
        results["ARM_LEN_M"] = result
    except Exception as e:
        results["ARM_LEN_M"] = MeasurementResult(
            standard_key="ARM_LEN_M",
            value_m=float('nan'),
            metadata={
                "standard_key": "ARM_LEN_M",
                "value_m": float('nan'),
                "unit": "m",
                "precision": 0.001,
                "warnings": [f"EXEC_FAIL: {str(e)}"],
                "version": {"semantic_tag": "semantic-v0", "schema_version": "metadata-schema-v0"}
            }
        )
    
    # WEIGHT_KG (input-only, skip for now - would need input data)
    # results["WEIGHT_KG"] = create_weight_metadata(70.0)  # Placeholder
    
    return results


def aggregate_results(all_results: List[Dict[str, MeasurementResult]]) -> Dict[str, Any]:
    """Aggregate results across all cases."""
    summary = {}
    
    for key in ALL_KEYS:
        key_results = [r.get(key) for r in all_results if key in r]
        if not key_results:
            continue
        
        # Extract values
        values = []
        nan_count = 0
        warnings_all = []
        proxy_used_count = 0
        proxy_types = defaultdict(int)
        band_scan_used_count = 0
        band_scan_limits = []
        canonical_sides = defaultdict(int)
        pose_unknown_counts = defaultdict(int)
        pose_total_counts = defaultdict(int)
        
        # Debug aggregation variables
        cross_section_reasons = defaultdict(int)
        cross_section_candidates_counts = []
        body_axis_reasons = defaultdict(int)
        landmark_reasons = defaultdict(int)
        
        for result in key_results:
            if result is None:
                continue
            
            # Value
            value = result.value_m if result.value_m is not None else result.value_kg
            if value is not None and not np.isnan(value):
                values.append(float(value))
            else:
                nan_count += 1
            
            # Warnings
            meta = result.metadata
            warnings = meta.get("warnings", [])
            warnings_all.extend(warnings)
            
            # Proxy
            proxy = meta.get("proxy", {})
            if proxy.get("proxy_used", False):
                proxy_used_count += 1
                proxy_type = proxy.get("proxy_type")
                if proxy_type:
                    proxy_types[proxy_type] += 1
            
            # Band scan
            search = meta.get("search", {})
            if search.get("band_scan_used", False):
                band_scan_used_count += 1
                limit = search.get("band_scan_limit_mm")
                if limit is not None:
                    band_scan_limits.append(limit)
            
            # Canonical side
            method = meta.get("method", {})
            canonical_side = method.get("canonical_side")
            if canonical_side:
                canonical_sides[canonical_side] += 1
            
            # Pose unknown
            pose = meta.get("pose", {})
            for pose_key in ["breath_state", "arms_down", "strict_standing", "knee_flexion_forbidden"]:
                if pose_key in pose:
                    pose_total_counts[pose_key] += 1
                    if pose[pose_key] == "unknown":
                        pose_unknown_counts[pose_key] += 1
            
            # Debug info aggregation
            debug = meta.get("debug", {})
            if debug:
                # Cross-section debug
                cross_section = debug.get("cross_section", {})
                if cross_section:
                    reason = cross_section.get("reason_not_found")
                    if reason:
                        cross_section_reasons[reason] += 1
                    candidates_count = cross_section.get("candidates_count", 0)
                    cross_section_candidates_counts.append(candidates_count)
                
                # Body axis debug
                body_axis = debug.get("body_axis", {})
                if body_axis:
                    if not body_axis.get("valid", True):
                        reason = body_axis.get("reason_invalid", "unknown")
                        body_axis_reasons[reason] += 1
                
                # Landmark regions debug
                landmark_regions = debug.get("landmark_regions", {})
                if landmark_regions:
                    reason = landmark_regions.get("reason_not_found")
                    if reason:
                        landmark_reasons[reason] += 1
        
        # Compute statistics
        total_count = len(key_results)
        nan_rate = nan_count / total_count if total_count > 0 else 0.0
        
        value_stats = {}
        if values:
            value_stats = {
                "min": float(np.min(values)),
                "median": float(np.median(values)),
                "max": float(np.max(values)),
                "count": len(values)
            }
        
        # Warnings Top 5
        warning_counts = defaultdict(int)
        for w in warnings_all:
            # Extract warning type (before colon if exists)
            w_type = w.split(":")[0] if ":" in w else w
            warning_counts[w_type] += 1
        warnings_top5 = sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Debug aggregation
        debug_summary = {}
        if cross_section_reasons:
            debug_summary["cross_section_reasons"] = dict(cross_section_reasons)
        if cross_section_candidates_counts:
            debug_summary["cross_section_candidates_counts"] = {
                "min": int(np.min(cross_section_candidates_counts)),
                "median": float(np.median(cross_section_candidates_counts)),
                "max": int(np.max(cross_section_candidates_counts)),
                "zero_count": sum(1 for c in cross_section_candidates_counts if c == 0)
            }
        if body_axis_reasons:
            debug_summary["body_axis_reasons"] = dict(body_axis_reasons)
        if landmark_reasons:
            debug_summary["landmark_reasons"] = dict(landmark_reasons)
        
        summary[key] = {
            "total_count": total_count,
            "nan_count": nan_count,
            "nan_rate": nan_rate,
            "value_stats": value_stats,
            "warnings_top5": warnings_top5,
            "proxy_used_count": proxy_used_count,
            "proxy_types": dict(proxy_types),
            "band_scan_used_count": band_scan_used_count,
            "band_scan_limits": list(set(band_scan_limits)) if band_scan_limits else [],
            "canonical_sides": dict(canonical_sides),
            "pose_unknown_rates": {
                k: pose_unknown_counts[k] / pose_total_counts[k] 
                if pose_total_counts[k] > 0 else 0.0
                for k in pose_total_counts
            },
            "debug_summary": debug_summary if debug_summary else {}
        }
    
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Geometric v0 Facts-Only Runner (Round 1)"
    )
    parser.add_argument(
        "--npz",
        type=str,
        default="verification/datasets/golden/core_measurements_v0/s0_synthetic_cases.npz",
        help="Input NPZ dataset path"
    )
    parser.add_argument(
        "--n_samples",
        type=int,
        default=None,
        help="Number of samples to process (None = all)"
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default=None,
        help="Output directory (default: verification/runs/facts/geo_v0/round1_<timestamp>)"
    )
    args = parser.parse_args()
    
    # Load dataset
    print(f"Loading dataset: {args.npz}")
    verts_list, case_ids = load_npz_dataset(args.npz)
    print(f"  Loaded {len(verts_list)} cases")
    
    # Limit samples
    if args.n_samples is not None:
        if args.n_samples < len(verts_list):
            verts_list = verts_list[:args.n_samples]
            case_ids = case_ids[:args.n_samples]
            print(f"  Limited to {args.n_samples} samples")
        elif args.n_samples > len(verts_list):
            print(f"  Warning: n_samples ({args.n_samples}) > available cases ({len(verts_list)}), using all {len(verts_list)} cases")
    
    # Process all cases
    print("\nProcessing cases...")
    all_results = []
    for i, (verts, case_id) in enumerate(zip(verts_list, case_ids)):
        print(f"  [{i+1}/{len(verts_list)}] {case_id}")
        try:
            results = measure_all_keys(verts, case_id)
            all_results.append(results)
        except Exception as e:
            print(f"    ERROR: {e}")
            traceback.print_exc()
            # Continue with empty results
            all_results.append({})
    
    # Aggregate
    print("\nAggregating results...")
    summary = aggregate_results(all_results)
    
    # Get git SHA
    git_sha = get_git_sha()
    
    # Save raw results (JSON)
    if args.out_dir is None:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path(f"verification/runs/facts/geo_v0/round1_{timestamp}")
    else:
        out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Save summary JSON
    from datetime import datetime
    summary_json = {
        "git_sha": git_sha,
        "dataset_path": args.npz,
        "n_samples": len(verts_list),
        "case_ids": case_ids,
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    }
    
    summary_path = out_dir / "facts_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=2, ensure_ascii=False)
    print(f"\nSaved summary: {summary_path}")
    
    # Generate markdown report
    report_path = out_dir / "geo_v0_facts_round2.md"
    generate_report(summary_json, report_path)
    print(f"Saved report: {report_path}")
    
    # Also save to reports directory for PR
    reports_dir = Path("reports/validation")
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_final_path = reports_dir / "geo_v0_facts_round2.md"
    generate_report(summary_json, report_final_path)
    print(f"Saved report (for PR): {report_final_path}")


def generate_report(summary_json: Dict[str, Any], output_path: Path):
    """Generate markdown report from summary JSON."""
    git_sha = summary_json.get("git_sha", "unknown")
    dataset_path = summary_json.get("dataset_path", "unknown")
    n_samples = summary_json.get("n_samples", 0)
    summary = summary_json.get("summary", {})
    
    lines = []
    lines.append("# Geometric v0 Facts-Only Summary (Round 2 - Debug Instrumentation)")
    lines.append("")
    lines.append("## 1. 실행 조건")
    lines.append("")
    lines.append(f"- **샘플 수**: {n_samples}")
    lines.append(f"- **입력 데이터셋**: `{dataset_path}`")
    lines.append(f"- **Git SHA**: `{git_sha}`")
    lines.append(f"- **실행 일시**: {summary_json.get('timestamp', 'N/A')}")
    lines.append("")
    
    # Section 2: Key별 요약 테이블
    lines.append("## 2. Key별 요약")
    lines.append("")
    lines.append("| Key | Total | NaN | NaN Rate | Min | Median | Max |")
    lines.append("|-----|-------|-----|----------|-----|--------|-----|")
    
    for key in ALL_KEYS:
        if key not in summary:
            continue
        s = summary[key]
        value_stats = s.get("value_stats", {})
        if value_stats:
            lines.append(
                f"| {key} | {s['total_count']} | {s['nan_count']} | "
                f"{s['nan_rate']:.2%} | {value_stats.get('min', 'N/A'):.4f} | "
                f"{value_stats.get('median', 'N/A'):.4f} | {value_stats.get('max', 'N/A'):.4f} |"
            )
        else:
            lines.append(
                f"| {key} | {s['total_count']} | {s['nan_count']} | "
                f"{s['nan_rate']:.2%} | N/A | N/A | N/A |"
            )
    lines.append("")
    
    # Section 3: Warnings Top 리스트
    lines.append("## 3. Warnings Top 리스트")
    lines.append("")
    
    # Overall warnings
    all_warnings = defaultdict(int)
    for key, s in summary.items():
        for w_type, count in s.get("warnings_top5", []):
            all_warnings[w_type] += count
    
    lines.append("### 3.1 전체 Warnings Top 10")
    lines.append("")
    lines.append("| Warning Type | Count |")
    lines.append("|--------------|-------|")
    for w_type, count in sorted(all_warnings.items(), key=lambda x: x[1], reverse=True)[:10]:
        lines.append(f"| {w_type} | {count} |")
    lines.append("")
    
    # Key별 warnings
    lines.append("### 3.2 Key별 Warnings Top 5")
    lines.append("")
    for key in ALL_KEYS:
        if key not in summary:
            continue
        s = summary[key]
        warnings_top5 = s.get("warnings_top5", [])
        if warnings_top5:
            lines.append(f"**{key}**:")
            for w_type, count in warnings_top5:
                lines.append(f"- `{w_type}`: {count}")
            lines.append("")
    
    # Section 4: Proxy/Band Scan/Side 기록 통계
    lines.append("## 4. Proxy/Band Scan/Side 기록 통계")
    lines.append("")
    
    lines.append("### 4.1 Proxy 사용")
    lines.append("")
    lines.append("| Key | Proxy Used Count | Proxy Types |")
    lines.append("|-----|------------------|-------------|")
    for key in ALL_KEYS:
        if key not in summary:
            continue
        s = summary[key]
        proxy_types = s.get("proxy_types", {})
        proxy_types_str = ", ".join([f"{k}: {v}" for k, v in proxy_types.items()]) if proxy_types else "N/A"
        lines.append(f"| {key} | {s.get('proxy_used_count', 0)} | {proxy_types_str} |")
    lines.append("")
    
    lines.append("### 4.2 Band Scan 사용")
    lines.append("")
    lines.append("| Key | Band Scan Used Count | Band Scan Limits |")
    lines.append("|-----|----------------------|------------------|")
    for key in ALL_KEYS:
        if key not in summary:
            continue
        s = summary[key]
        limits = s.get("band_scan_limits", [])
        limits_str = ", ".join([str(l) for l in limits]) if limits else "N/A"
        lines.append(f"| {key} | {s.get('band_scan_used_count', 0)} | {limits_str} |")
    lines.append("")
    
    lines.append("### 4.3 Canonical Side 기록")
    lines.append("")
    lines.append("| Key | Canonical Sides |")
    lines.append("|-----|-----------------|")
    for key in ALL_KEYS:
        if key not in summary:
            continue
        s = summary[key]
        sides = s.get("canonical_sides", {})
        sides_str = ", ".join([f"{k}: {v}" for k, v in sides.items()]) if sides else "N/A"
        lines.append(f"| {key} | {sides_str} |")
    lines.append("")
    
    lines.append("### 4.4 Pose Unknown 비율")
    lines.append("")
    lines.append("| Key | Breath State Unknown | Arms Down Unknown | Strict Standing Unknown | Knee Flexion Unknown |")
    lines.append("|-----|----------------------|-------------------|------------------------|----------------------|")
    for key in ALL_KEYS:
        if key not in summary:
            continue
        s = summary[key]
        pose_unknown = s.get("pose_unknown_rates", {})
        lines.append(
            f"| {key} | "
            f"{pose_unknown.get('breath_state', 0.0):.2%} | "
            f"{pose_unknown.get('arms_down', 0.0):.2%} | "
            f"{pose_unknown.get('strict_standing', 0.0):.2%} | "
            f"{pose_unknown.get('knee_flexion_forbidden', 0.0):.2%} |"
        )
    lines.append("")
    
    # Section 4.5: Debug 정보 (실패 원인 분해)
    lines.append("### 4.5 Debug 정보 (실패 원인 분해)")
    lines.append("")
    
    # Cross-section reasons
    lines.append("#### 4.5.1 CROSS_SECTION_NOT_FOUND 원인 분포")
    lines.append("")
    lines.append("| Key | Reason | Count |")
    lines.append("|-----|--------|-------|")
    for key in ALL_KEYS:
        if key not in summary:
            continue
        s = summary[key]
        debug_summary = s.get("debug_summary", {})
        cross_section_reasons = debug_summary.get("cross_section_reasons", {})
        if cross_section_reasons:
            for reason, count in cross_section_reasons.items():
                lines.append(f"| {key} | {reason} | {count} |")
        else:
            # Check if CROSS_SECTION_NOT_FOUND warning exists
            warnings_top5 = s.get("warnings_top5", [])
            if any("CROSS_SECTION_NOT_FOUND" in w[0] for w in warnings_top5):
                lines.append(f"| {key} | (no debug info) | - |")
    lines.append("")
    
    # Cross-section candidates count
    lines.append("#### 4.5.2 Cross-section Candidates Count 통계")
    lines.append("")
    lines.append("| Key | Min | Median | Max | Zero Count |")
    lines.append("|-----|-----|--------|-----|-----------|")
    for key in ALL_KEYS:
        if key not in summary:
            continue
        s = summary[key]
        debug_summary = s.get("debug_summary", {})
        candidates_stats = debug_summary.get("cross_section_candidates_counts", {})
        if candidates_stats:
            lines.append(
                f"| {key} | {candidates_stats.get('min', 0)} | "
                f"{candidates_stats.get('median', 0.0):.1f} | "
                f"{candidates_stats.get('max', 0)} | "
                f"{candidates_stats.get('zero_count', 0)} |"
            )
    lines.append("")
    
    # Body axis reasons
    lines.append("#### 4.5.3 BODY_AXIS_TOO_SHORT 원인 분포")
    lines.append("")
    lines.append("| Key | Reason | Count |")
    lines.append("|-----|--------|-------|")
    for key in ALL_KEYS:
        if key not in summary:
            continue
        s = summary[key]
        debug_summary = s.get("debug_summary", {})
        body_axis_reasons = debug_summary.get("body_axis_reasons", {})
        if body_axis_reasons:
            for reason, count in body_axis_reasons.items():
                lines.append(f"| {key} | {reason} | {count} |")
    lines.append("")
    
    # Landmark regions reasons
    lines.append("#### 4.5.4 LANDMARK_REGIONS_NOT_FOUND 원인 분포")
    lines.append("")
    lines.append("| Key | Reason | Count |")
    lines.append("|-----|--------|-------|")
    for key in ALL_KEYS:
        if key not in summary:
            continue
        s = summary[key]
        debug_summary = s.get("debug_summary", {})
        landmark_reasons = debug_summary.get("landmark_reasons", {})
        if landmark_reasons:
            for reason, count in landmark_reasons.items():
                lines.append(f"| {key} | {reason} | {count} |")
    lines.append("")
    
    # Section 5: 이슈 분류
    lines.append("## 5. 이슈 분류")
    lines.append("")
    
    issues = {
        "GEO_BUG": [],
        "POSE/PROXY": [],
        "COVERAGE/UNKNOWN": []
    }
    
    for key in ALL_KEYS:
        if key not in summary:
            continue
        s = summary[key]
        
        # GEO_BUG: 물리적으로 말이 안 되는 범위
        value_stats = s.get("value_stats", {})
        if value_stats:
            min_val = value_stats.get("min", 0)
            max_val = value_stats.get("max", 0)
            # Check for unreasonable ranges
            if "CIRC" in key:
                if max_val > 3.0:  # > 3m circumference
                    issues["GEO_BUG"].append(f"{key}: max circumference {max_val:.4f}m > 3.0m")
                if min_val < 0.1:  # < 10cm circumference
                    issues["GEO_BUG"].append(f"{key}: min circumference {min_val:.4f}m < 0.1m")
            elif "HEIGHT" in key or key == "ARM_LEN_M":
                if max_val > 3.0:  # > 3m height/length
                    issues["GEO_BUG"].append(f"{key}: max {max_val:.4f}m > 3.0m")
                if min_val < 0.1:  # < 10cm
                    issues["GEO_BUG"].append(f"{key}: min {min_val:.4f}m < 0.1m")
            elif "WIDTH" in key or "DEPTH" in key:
                if max_val > 1.0:  # > 1m width/depth
                    issues["GEO_BUG"].append(f"{key}: max {max_val:.4f}m > 1.0m")
                if min_val < 0.05:  # < 5cm
                    issues["GEO_BUG"].append(f"{key}: min {min_val:.4f}m < 0.05m")
        
        # POSE/PROXY: proxy_used가 높음
        if s.get("proxy_used_count", 0) > s.get("total_count", 1) * 0.5:
            issues["POSE/PROXY"].append(f"{key}: proxy_used rate {s.get('proxy_used_count', 0)/s.get('total_count', 1):.2%}")
        
        # COVERAGE/UNKNOWN: 메타 unknown 과다
        pose_unknown = s.get("pose_unknown_rates", {})
        for pose_key, rate in pose_unknown.items():
            if rate > 0.5:  # > 50% unknown
                issues["COVERAGE/UNKNOWN"].append(f"{key}: {pose_key} unknown rate {rate:.2%}")
    
    for issue_type, issue_list in issues.items():
        if issue_list:
            lines.append(f"### {issue_type}")
            lines.append("")
            for issue in issue_list:
                lines.append(f"- {issue}")
            lines.append("")
        else:
            lines.append(f"### {issue_type}")
            lines.append("")
            lines.append("- (없음)")
            lines.append("")
    
    # Write report
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
