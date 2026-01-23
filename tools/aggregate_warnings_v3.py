#!/usr/bin/env python3
"""
Aggregate warnings from curated_v0 v3 run for facts-only summary.

Reads warnings JSONL and curated dataset to generate facts-only statistics.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any


def load_warnings(warnings_path: Path) -> List[Dict[str, Any]]:
    """Load warnings from JSONL file."""
    warnings = []
    with open(warnings_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                warnings.append(json.loads(line))
    return warnings


def aggregate_warnings(warnings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate warnings by reason, source, etc."""
    stats = {
        "total": len(warnings),
        "by_reason": Counter(),
        "by_source": defaultdict(lambda: Counter()),
        "sentinel_missing": {
            "total": 0,
            "by_value": Counter(),
            "sentinel_count_sum": 0
        }
    }
    
    for w in warnings:
        reason = w.get('reason', 'unknown')
        source = w.get('source', 'unknown')
        
        stats["by_reason"][reason] += 1
        stats["by_source"][source][reason] += 1
        
        # SENTINEL_MISSING aggregation
        if reason == 'SENTINEL_MISSING':
            stats["sentinel_missing"]["total"] += 1
            sentinel_value = w.get('sentinel_value', 'unknown')
            stats["sentinel_missing"]["by_value"][sentinel_value] += 1
            sentinel_count = w.get('sentinel_count', 0)
            if isinstance(sentinel_count, (int, float)):
                stats["sentinel_missing"]["sentinel_count_sum"] += int(sentinel_count)
    
    return stats


def analyze_null_persistence(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze null persistence by standard_key."""
    # Exclude meta columns
    meta_cols = ['SEX', 'AGE', 'HUMAN_ID', '_source']
    standard_keys = [col for col in df.columns if col not in meta_cols]
    
    null_stats = []
    total_rows = len(df)
    
    for key in standard_keys:
        null_count = df[key].isna().sum()
        null_rate = null_count / total_rows if total_rows > 0 else 0.0
        
        # Get sources that have this key
        sources = df[df[key].notna()]['_source'].unique().tolist() if '_source' in df.columns else []
        
        null_stats.append({
            "standard_key": key,
            "null_count": int(null_count),
            "null_rate": null_rate,
            "sources": sources
        })
    
    # Sort by null_count descending
    null_stats.sort(key=lambda x: x["null_count"], reverse=True)
    
    return {
        "total_rows": total_rows,
        "keys_with_nulls": null_stats
    }


def analyze_source_missing_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze missing patterns by source × key."""
    if '_source' not in df.columns:
        return {}
    
    meta_cols = ['SEX', 'AGE', 'HUMAN_ID', '_source']
    standard_keys = [col for col in df.columns if col not in meta_cols]
    
    source_patterns = defaultdict(lambda: [])
    
    for source in df['_source'].unique():
        source_df = df[df['_source'] == source]
        total_rows = len(source_df)
        
        for key in standard_keys:
            null_count = source_df[key].isna().sum()
            null_rate = null_count / total_rows if total_rows > 0 else 0.0
            
            if null_count > 0:
                source_patterns[source].append({
                    "key": key,
                    "null_count": int(null_count),
                    "null_rate": null_rate
                })
        
        # Sort by null_count descending
        source_patterns[source].sort(key=lambda x: x["null_count"], reverse=True)
    
    return dict(source_patterns)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Aggregate warnings from curated_v0 v3 run"
    )
    parser.add_argument(
        '--warnings',
        type=str,
        default='verification/runs/curated_v0/warnings_v3.jsonl',
        help='Path to warnings JSONL file'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        default='data/processed/curated_v0/curated_v0.csv',
        help='Path to curated dataset (CSV or parquet)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='verification/runs/curated_v0/aggregation_v3.json',
        help='Path to save aggregation results (JSON)'
    )
    
    args = parser.parse_args()
    
    warnings_path = Path(args.warnings)
    dataset_path = Path(args.dataset)
    output_path = Path(args.output)
    
    # Load warnings
    print(f"Loading warnings from: {warnings_path}")
    warnings = load_warnings(warnings_path)
    print(f"Loaded {len(warnings)} warnings")
    
    # Aggregate warnings
    print("Aggregating warnings...")
    warning_stats = aggregate_warnings(warnings)
    
    # Load dataset (try CSV first, then parquet)
    print(f"Loading dataset from: {dataset_path}")
    df = None
    try:
        if dataset_path.suffix == '.csv' or not dataset_path.exists():
            # Try CSV first
            csv_path = dataset_path.with_suffix('.csv')
            if csv_path.exists():
                df = pd.read_csv(csv_path, encoding='utf-8-sig')
            elif dataset_path.suffix == '.parquet' and dataset_path.exists():
                # Try parquet
                try:
                    df = pd.read_parquet(dataset_path)
                except ImportError:
                    print("Warning: Cannot read parquet (pyarrow/fastparquet not available). Skipping dataset analysis.")
                    df = None
        else:
            try:
                df = pd.read_parquet(dataset_path)
            except ImportError:
                print("Warning: Cannot read parquet (pyarrow/fastparquet not available). Skipping dataset analysis.")
                df = None
    except Exception as e:
        print(f"Warning: Could not load dataset: {e}. Skipping dataset analysis.")
        df = None
    
    null_stats = None
    source_patterns = None
    
    if df is not None:
        print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        
        # Analyze null persistence
        print("Analyzing null persistence...")
        null_stats = analyze_null_persistence(df)
        
        # Analyze source missing patterns
        print("Analyzing source missing patterns...")
        source_patterns = analyze_source_missing_patterns(df)
    else:
        print("Skipping dataset analysis (dataset not available)")
    
    # Combine results
    results = {
        "warnings": {
            "total": warning_stats["total"],
            "by_reason": dict(warning_stats["by_reason"]),
            "by_source": {
                source: dict(reasons) 
                for source, reasons in warning_stats["by_source"].items()
            },
            "sentinel_missing": warning_stats["sentinel_missing"]
        }
    }
    
    if null_stats is not None:
        results["null_persistence"] = null_stats
    if source_patterns is not None:
        results["source_missing_patterns"] = source_patterns
    
    # Save results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved aggregation results to: {output_path}")
    
    # Print summary
    print("\n=== Summary ===")
    print(f"Total warnings: {warning_stats['total']}")
    print(f"\nTop reasons:")
    for reason, count in warning_stats['by_reason'].most_common(10):
        print(f"  {reason}: {count}")
    
    print(f"\nSentinel missing:")
    print(f"  Total: {warning_stats['sentinel_missing']['total']}")
    print(f"  Sentinel count sum: {warning_stats['sentinel_missing']['sentinel_count_sum']}")
    for value, count in warning_stats['sentinel_missing']['by_value'].most_common():
        print(f"    {value}: {count}")
    
    if null_stats is not None:
        print(f"\nTop null persistence keys:")
        for key_info in null_stats['keys_with_nulls'][:10]:
            print(f"  {key_info['standard_key']}: {key_info['null_count']} ({key_info['null_rate']:.2%})")


if __name__ == '__main__':
    main()
