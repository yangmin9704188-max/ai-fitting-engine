#!/usr/bin/env python3
"""Summarize sanity check results from verification."""

import pandas as pd
import numpy as np

df = pd.read_csv('verification/reports/smart_mapper_v001/verification_results.csv')

print('\n' + '=' * 100)
print('Case-by-Case Sanity Check Summary')
print('=' * 100)
print(f"{'Case':<6} | {'Height':<8} | {'Height Pred':<13} | {'Height Err':<12} | {'Joint SW':<10} | {'Measured SW':<13} | {'Target SW':<11} | {'SW Ratio':<9}")
print('-' * 100)

for _, row in df.iterrows():
    h_err = abs(row['height_pred_m'] - row['height_m']) if pd.notna(row['height_pred_m']) else None
    sw_ratio = row['measured_sw_m'] / row['joint_sw_m'] if pd.notna(row['measured_sw_m']) and pd.notna(row['joint_sw_m']) else None
    
    case_id = int(row['case_id'])
    height_m = row['height_m']
    height_pred = row['height_pred_m'] if pd.notna(row['height_pred_m']) else None
    height_err = h_err if h_err is not None else None
    joint_sw = row['joint_sw_m'] if pd.notna(row['joint_sw_m']) else None
    measured_sw = row['measured_sw_m'] if pd.notna(row['measured_sw_m']) else None
    target_sw = row['target_shoulder_width_m'] if pd.notna(row['target_shoulder_width_m']) else None
    
    if sw_ratio is not None:
        print(f"{case_id:<6} | {height_m:8.2f} | {height_pred:13.4f} | {height_err:12.4f} | {joint_sw:10.4f} | {measured_sw:13.4f} | {target_sw:11.4f} | {sw_ratio:9.2f}x")
    else:
        print(f"{case_id:<6} | {height_m:8.2f} | {height_pred:13.4f} | {height_err:12.4f} | {joint_sw:10.4f} | {'N/A':<13} | {target_sw if target_sw is not None else 'N/A':<11} | {'N/A':<9}")

print('\n' + '=' * 100)
print('Summary Statistics')
print('=' * 100)

# Height accuracy
height_errors = (df['height_pred_m'] - df['height_m']).abs()
print(f'\nHeight Prediction Accuracy:')
print(f'  Mean error: {height_errors.mean():.4f}m')
print(f'  Max error: {height_errors.max():.4f}m')
print(f'  All errors < 0.02m: {(height_errors < 0.02).all()}')

# Joint-based shoulder width
print(f'\nJoint-based Shoulder Width:')
print(f'  Mean: {df["joint_sw_m"].mean():.4f}m')
print(f'  Min: {df["joint_sw_m"].min():.4f}m')
print(f'  Max: {df["joint_sw_m"].max():.4f}m')
print(f'  Range: {df["joint_sw_m"].max() - df["joint_sw_m"].min():.4f}m')

# Measured shoulder width
sw_cases = df[df['measured_sw_m'].notna()]
if len(sw_cases) > 0:
    print(f'\nMeasured Shoulder Width (n={len(sw_cases)}):')
    print(f'  Mean: {sw_cases["measured_sw_m"].mean():.4f}m')
    print(f'  Min: {sw_cases["measured_sw_m"].min():.4f}m')
    print(f'  Max: {sw_cases["measured_sw_m"].max():.4f}m')
    print(f'  Range: {sw_cases["measured_sw_m"].max() - sw_cases["measured_sw_m"].min():.4f}m')
    
    # Ratio
    ratios = sw_cases['measured_sw_m'] / sw_cases['joint_sw_m']
    print(f'\nMeasured/Joint Ratio:')
    print(f'  Mean: {ratios.mean():.2f}x')
    print(f'  Min: {ratios.min():.2f}x')
    print(f'  Max: {ratios.max():.2f}x')
    
    # vs Target
    print(f'\nMeasured vs Target:')
    print(f'  Mean error: {sw_cases["shoulder_width_error_m"].mean():.4f}m')
    print(f'  Mean error %: {sw_cases["shoulder_width_error_pct"].mean():.1f}%')
    print(f'  Max error: {sw_cases["shoulder_width_error_m"].max():.4f}m')
    print(f'  Max error %: {sw_cases["shoulder_width_error_pct"].max():.1f}%')

print('\n' + '=' * 100)
