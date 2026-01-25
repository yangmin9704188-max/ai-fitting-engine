#!/usr/bin/env python3
"""
Facts Summary KPI Header Generator

입력: facts_summary.json 경로
출력: markdown string (KPI HEADER)을 stdout으로 출력

KPI 5개를 안정적으로 출력:
1. total_cases / valid_cases / expected_fail_cases (키가 없으면 N/A)
2. NaN rate Top5 keys (가능하면)
3. failure_reason Top5 (가능하면)
4. HEIGHT_M 분포 요약 p50/p95 (있으면)
5. BUST/WAIST/HIP p50 (있으면)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def safe_get(data: Dict[str, Any], *keys: str, default: Any = "N/A") -> Any:
    """Safely get nested keys, return default if any key is missing."""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        if key not in current:
            return default
        current = current[key]
    return current if current is not None else default


def get_nan_rates(summary_data: Dict[str, Any]) -> List[tuple[str, float]]:
    """Extract NaN rates from summary data. Returns list of (key, rate) tuples."""
    nan_rates = []
    
    # Try different possible structures
    summary = safe_get(summary_data, "summary", default={})
    if not summary or summary == "N/A":
        summary = safe_get(summary_data, "statistics", default={})
    
    if not isinstance(summary, dict):
        return []
    
    for key, stats in summary.items():
        if not isinstance(stats, dict):
            continue
        
        # Try different possible NaN rate keys
        nan_rate = None
        if "nan_rate_pct" in stats:
            nan_rate = float(stats["nan_rate_pct"])
        elif "nan_rate" in stats:
            nan_rate = float(stats["nan_rate"]) * 100.0
        elif "nan_rates" in stats:
            # Nested structure like {"nan_rates": {"underbust": {"rate": 0.1}}}
            nan_rates_dict = stats["nan_rates"]
            if isinstance(nan_rates_dict, dict):
                for sub_key, sub_stats in nan_rates_dict.items():
                    if isinstance(sub_stats, dict) and "rate" in sub_stats:
                        rate_val = float(sub_stats["rate"]) * 100.0
                        nan_rates.append((f"{key}.{sub_key}", rate_val))
            continue
        
        if nan_rate is not None:
            nan_rates.append((key, nan_rate))
    
    # Sort by rate descending
    nan_rates.sort(key=lambda x: x[1], reverse=True)
    return nan_rates[:5]


def get_failure_reasons(summary_data: Dict[str, Any]) -> List[tuple[str, int]]:
    """Extract top failure reasons. Returns list of (reason, count) tuples."""
    reasons = []
    
    summary = safe_get(summary_data, "summary", default={})
    if not summary or summary == "N/A":
        summary = safe_get(summary_data, "statistics", default={})
    
    if not isinstance(summary, dict):
        return []
    
    # Look for warnings_top5 or similar structures
    for key, stats in summary.items():
        if not isinstance(stats, dict):
            continue
        
        if "warnings_top5" in stats:
            warnings = stats["warnings_top5"]
            if isinstance(warnings, list):
                for w in warnings:
                    if isinstance(w, dict):
                        reason = w.get("reason", "unknown")
                        count = w.get("n", 0)
                        if count > 0:
                            reasons.append((f"{key}:{reason}", count))
    
    # Sort by count descending
    reasons.sort(key=lambda x: x[1], reverse=True)
    return reasons[:5]


def get_percentile(values: List[float], percentile: float) -> Optional[float]:
    """Calculate percentile from list of values."""
    if not values:
        return None
    sorted_vals = sorted(values)
    idx = int(len(sorted_vals) * percentile / 100.0)
    idx = min(idx, len(sorted_vals) - 1)
    return sorted_vals[idx]


def get_value_distribution(summary_data: Dict[str, Any], key: str) -> Dict[str, Optional[float]]:
    """Get p50/p95 for a specific key."""
    result = {"p50": None, "p95": None}
    
    summary = safe_get(summary_data, "summary", default={})
    if not summary or summary == "N/A":
        summary = safe_get(summary_data, "statistics", default={})
    
    if not isinstance(summary, dict):
        return result
    
    key_stats = summary.get(key, {})
    if not isinstance(key_stats, dict):
        return result
    
    # Try to get median (p50)
    if "median" in key_stats:
        result["p50"] = key_stats["median"]
    
    # For p95, we need to reconstruct from min/max or use max as approximation
    # In practice, we'll use max as p95 approximation if available
    if "max" in key_stats:
        result["p95"] = key_stats["max"]
    
    return result


def generate_kpi_header(summary_data: Dict[str, Any]) -> str:
    """Generate KPI header markdown."""
    lines = ["# Facts Summary KPI", ""]
    
    # 1. Total cases / valid cases / expected fail cases
    total_cases = safe_get(summary_data, "n_samples", default="N/A")
    valid_cases = safe_get(summary_data, "summary", "valid_cases", default="N/A")
    if valid_cases == "N/A":
        valid_cases = safe_get(summary_data, "statistics", "valid_cases", default="N/A")
    expected_fail_cases = safe_get(summary_data, "summary", "expected_fail_cases", default="N/A")
    if expected_fail_cases == "N/A":
        expected_fail_cases = safe_get(summary_data, "statistics", "expected_fail_cases", default="N/A")
    
    lines.append("## 1. Case Counts")
    lines.append(f"- **Total cases**: {total_cases}")
    lines.append(f"- **Valid cases**: {valid_cases}")
    lines.append(f"- **Expected fail cases**: {expected_fail_cases}")
    lines.append("")
    
    # 2. NaN rate Top5
    nan_rates = get_nan_rates(summary_data)
    lines.append("## 2. NaN Rate Top5")
    if nan_rates:
        for key, rate in nan_rates:
            lines.append(f"- **{key}**: {rate:.2f}%")
    else:
        lines.append("- N/A")
    lines.append("")
    
    # 3. Failure reason Top5
    failure_reasons = get_failure_reasons(summary_data)
    lines.append("## 3. Failure Reason Top5")
    if failure_reasons:
        for reason, count in failure_reasons:
            lines.append(f"- **{reason}**: {count}")
    else:
        lines.append("- N/A")
    lines.append("")
    
    # 4. HEIGHT_M distribution
    height_dist = get_value_distribution(summary_data, "HEIGHT_M")
    lines.append("## 4. HEIGHT_M Distribution")
    if height_dist["p50"] is not None:
        lines.append(f"- **p50**: {height_dist['p50']:.4f} m")
    else:
        lines.append("- **p50**: N/A")
    if height_dist["p95"] is not None:
        lines.append(f"- **p95**: {height_dist['p95']:.4f} m")
    else:
        lines.append("- **p95**: N/A")
    lines.append("")
    
    # 5. BUST/WAIST/HIP p50
    lines.append("## 5. BUST/WAIST/HIP p50")
    for key in ["BUST_CIRC_M", "WAIST_CIRC_M", "HIP_CIRC_M"]:
        dist = get_value_distribution(summary_data, key)
        if dist["p50"] is not None:
            lines.append(f"- **{key}**: {dist['p50']:.4f} m")
        else:
            lines.append(f"- **{key}**: N/A")
    lines.append("")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python summarize_facts_kpi.py <facts_summary.json>", file=sys.stderr)
        sys.exit(1)
    
    json_path = Path(sys.argv[1])
    if not json_path.exists():
        print(f"Error: File not found: {json_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            summary_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read file: {e}", file=sys.stderr)
        sys.exit(1)
    
    kpi_header = generate_kpi_header(summary_data)
    print(kpi_header)


if __name__ == "__main__":
    main()
