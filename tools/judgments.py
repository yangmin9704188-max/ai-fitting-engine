#!/usr/bin/env python3
"""
Judgment Scaffolding Tool

라운드 실행 결과에서 judgment 문서를 생성하는 스캐폴딩 도구입니다.
facts-only 기록을 위한 보관/기록용 문서를 생성합니다.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# Add project root to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))


def extract_lane_round_from_prompt_snapshot(prompt_snapshot_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """Extract lane and round from PROMPT_SNAPSHOT.md if available."""
    if not prompt_snapshot_path.exists():
        return None, None
    
    try:
        content = prompt_snapshot_path.read_text(encoding='utf-8')
        lane = None
        round_id = None
        
        # Extract lane
        lane_match = re.search(r'lane:\s*`([^`]+)`', content)
        if lane_match:
            lane = lane_match.group(1)
        
        # Extract current_run_dir and parse round from it
        run_dir_match = re.search(r'current_run_dir:\s*`([^`]+)`', content)
        if run_dir_match:
            run_dir_str = run_dir_match.group(1)
            # Extract round pattern like round20_20260125_164801
            round_match = re.search(r'round(\d+)_\d{8}_\d{6}', run_dir_str)
            if round_match:
                round_id = f"round{round_match.group(1)}"
        
        return lane, round_id
    except Exception:
        return None, None


def extract_lane_round_from_path(run_dir: Path) -> Tuple[Optional[str], Optional[str]]:
    """Extract lane and round from run_dir path string."""
    run_dir_str = str(run_dir)
    
    # Extract lane (e.g., curated_v0)
    lane_match = re.search(r'/([^/]+)/round\d+', run_dir_str)
    if not lane_match:
        lane_match = re.search(r'\\([^\\]+)\\round\d+', run_dir_str)
    
    lane = lane_match.group(1) if lane_match else None
    
    # Extract round (e.g., round20)
    round_match = re.search(r'round(\d+)', run_dir_str)
    round_id = f"round{round_match.group(1)}" if round_match else None
    
    return lane, round_id


def scan_evidence_files(run_dir: Path, repo_root: Path) -> dict:
    """Scan for evidence files and return links/missing status."""
    evidence_files = {
        'ROUND_CHARTER.md': 'ROUND_CHARTER',
        'PROMPT_SNAPSHOT.md': 'PROMPT_SNAPSHOT',
        'KPI_DIFF.md': 'KPI_DIFF',
        'LINEAGE.md': 'LINEAGE',
        'KPI.md': 'KPI',
        'CANDIDATES/GOLDEN_CANDIDATE.md': 'GOLDEN_CANDIDATE',
        'CANDIDATES/BASELINE_CANDIDATE.md': 'BASELINE_CANDIDATE',
        'CANDIDATES/GOLDEN_REGISTRY_PATCH.json': 'GOLDEN_REGISTRY_PATCH',
        'CANDIDATES/BASELINE_UPDATE_PROPOSAL.md': 'BASELINE_UPDATE_PROPOSAL',
    }
    
    results = {}
    for file_path, key in evidence_files.items():
        full_path = run_dir / file_path
        if full_path.exists():
            # Calculate relative path from repo_root
            try:
                rel_path = full_path.relative_to(repo_root)
                results[key] = str(rel_path).replace('\\', '/')
            except ValueError:
                results[key] = f"missing: {file_path}"
        else:
            results[key] = f"missing: {file_path}"
    
    return results


def extract_baseline_info(prompt_snapshot_path: Path, repo_root: Path) -> Tuple[Optional[str], Optional[str]]:
    """Extract baseline alias and run_dir from PROMPT_SNAPSHOT.md if available."""
    if not prompt_snapshot_path.exists():
        return None, None
    
    try:
        content = prompt_snapshot_path.read_text(encoding='utf-8')
        baseline_alias = None
        baseline_run_dir = None
        
        # Extract baseline_tag(alias)
        alias_match = re.search(r'baseline_tag\(alias\):\s*`([^`]+)`', content)
        if alias_match:
            baseline_alias = alias_match.group(1)
        
        # Extract baseline_run_dir
        baseline_dir_match = re.search(r'baseline_run_dir:\s*`([^`]+)`', content)
        if baseline_dir_match:
            baseline_run_dir_str = baseline_dir_match.group(1)
            # Convert to relative path if possible
            baseline_path = Path(baseline_run_dir_str)
            if baseline_path.is_absolute():
                try:
                    baseline_run_dir = str(baseline_path.relative_to(repo_root)).replace('\\', '/')
                except ValueError:
                    baseline_run_dir = baseline_run_dir_str
            else:
                baseline_run_dir = baseline_run_dir_str.replace('\\', '/')
        
        return baseline_alias, baseline_run_dir
    except Exception:
        return None, None


def generate_judgment_document(
    template_path: Path,
    run_dir: Path,
    repo_root: Path,
    lane: Optional[str],
    round_id: Optional[str],
    date_str: str,
    slug: str,
    evidence_results: dict,
    baseline_alias: Optional[str],
    baseline_run_dir: Optional[str],
    dry_run: bool = False
) -> str:
    """Generate judgment document content from template."""
    if not template_path.exists():
        print(f"Error: Template file not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    
    template_content = template_path.read_text(encoding='utf-8')
    
    # Calculate relative path for run_dir
    try:
        run_dir_rel = str(run_dir.relative_to(repo_root)).replace('\\', '/')
    except ValueError:
        run_dir_rel = str(run_dir)
    
    # Replace metadata placeholders
    template_content = template_content.replace('[lane]', lane or 'unknown')
    template_content = template_content.replace('[round_id]', round_id or 'unknown')
    template_content = template_content.replace('[run_dir]', run_dir_rel)
    template_content = template_content.replace('[baseline_alias or null]', baseline_alias or 'null')
    template_content = template_content.replace('[baseline_run_dir or null]', baseline_run_dir or 'null')
    template_content = template_content.replace('[YYYY-MM-DD]', date_str)
    template_content = template_content.replace('[Human name or identifier]', 'auto-generated')
    
    # Replace evidence links
    evidence_replacements = {
        'ROUND_CHARTER': evidence_results.get('ROUND_CHARTER', 'missing: ROUND_CHARTER.md'),
        'PROMPT_SNAPSHOT': evidence_results.get('PROMPT_SNAPSHOT', 'missing: PROMPT_SNAPSHOT.md'),
        'KPI_DIFF': evidence_results.get('KPI_DIFF', 'missing: KPI_DIFF.md'),
        'LINEAGE': evidence_results.get('LINEAGE', 'missing: LINEAGE.md'),
        'KPI': evidence_results.get('KPI', 'missing: KPI.md'),
        'GOLDEN_CANDIDATE': evidence_results.get('GOLDEN_CANDIDATE', 'missing: CANDIDATES/GOLDEN_CANDIDATE.md'),
        'BASELINE_CANDIDATE': evidence_results.get('BASELINE_CANDIDATE', 'missing: CANDIDATES/BASELINE_CANDIDATE.md'),
        'GOLDEN_REGISTRY_PATCH': evidence_results.get('GOLDEN_REGISTRY_PATCH', 'missing: CANDIDATES/GOLDEN_REGISTRY_PATCH.json'),
        'BASELINE_UPDATE_PROPOSAL': evidence_results.get('BASELINE_UPDATE_PROPOSAL', 'missing: CANDIDATES/BASELINE_UPDATE_PROPOSAL.md'),
    }
    
    for key, value in evidence_replacements.items():
        template_content = template_content.replace(f'[link to {key}]', value)
        # Handle conditional "(있으면)" cases
        if key == 'KPI':
            if value.startswith('missing:'):
                template_content = re.sub(r'- \*\*KPI\*\*: \[link to KPI\.md\] \(있으면\)', '', template_content)
            else:
                template_content = template_content.replace('[link to KPI.md] (있으면)', value)
        else:
            if value.startswith('missing:'):
                template_content = template_content.replace(f'[link to CANDIDATES/{key}.md] (있으면)', '')
                template_content = template_content.replace(f'[link to CANDIDATES/{key}.json] (있으면)', '')
    
    # Add disclaimer if not present
    if '이 문서는 보관/기록용이며 자동 판정이 아니다' not in template_content:
        # Add after Status line if exists
        if '**Status**:' in template_content:
            status_line_idx = template_content.find('**Status**:')
            next_newline = template_content.find('\n', status_line_idx)
            if next_newline != -1:
                template_content = (
                    template_content[:next_newline+1] +
                    '\n**Note**: 이 문서는 보관/기록용이며 자동 판정이 아닙니다.\n' +
                    template_content[next_newline+1:]
                )
    
    return template_content


def main():
    parser = argparse.ArgumentParser(
        description='Generate judgment scaffolding document from run directory'
    )
    parser.add_argument(
        '--from-run',
        type=str,
        required=True,
        help='Run directory path (required)'
    )
    parser.add_argument(
        '--out-dir',
        type=str,
        default='docs/judgments',
        help='Output directory (default: docs/judgments)'
    )
    parser.add_argument(
        '--template',
        type=str,
        default='docs/judgments/templates/JUDGMENT_ENTRY_TEMPLATE.md',
        help='Template file path (default: docs/judgments/templates/JUDGMENT_ENTRY_TEMPLATE.md)'
    )
    parser.add_argument(
        '--slug',
        type=str,
        default='judgment',
        help='Slug for filename (default: judgment)'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Date in YYYYMMDD format (default: today)'
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run: output facts-only info without creating file'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    run_dir = Path(args.from_run).resolve()
    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}", file=sys.stderr)
        sys.exit(1)
    
    template_path = (repo_root / args.template).resolve()
    if not template_path.exists():
        print(f"Error: Template file not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    
    out_dir = (repo_root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine date
    if args.date:
        try:
            date_obj = datetime.strptime(args.date, '%Y%m%d')
            date_str = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format. Expected YYYYMMDD, got: {args.date}", file=sys.stderr)
            sys.exit(1)
    else:
        date_obj = datetime.now()
        date_str = date_obj.strftime('%Y-%m-%d')
        args.date = date_obj.strftime('%Y%m%d')
    
    # Extract lane and round
    prompt_snapshot_path = run_dir / 'PROMPT_SNAPSHOT.md'
    lane, round_id = extract_lane_round_from_prompt_snapshot(prompt_snapshot_path)
    
    if lane is None or round_id is None:
        lane, round_id = extract_lane_round_from_path(run_dir)
    
    if lane is None:
        lane = 'unknown'
    if round_id is None:
        round_id = 'unknown'
    
    # Scan evidence files
    evidence_results = scan_evidence_files(run_dir, repo_root)
    
    # Extract baseline info
    baseline_alias, baseline_run_dir = extract_baseline_info(prompt_snapshot_path, repo_root)
    
    # Generate output filename
    output_filename = f"{args.date}_{lane}_{round_id}_{args.slug}.md"
    output_path = out_dir / output_filename
    
    # Generate document content
    document_content = generate_judgment_document(
        template_path=template_path,
        run_dir=run_dir,
        repo_root=repo_root,
        lane=lane,
        round_id=round_id,
        date_str=date_str,
        slug=args.slug,
        evidence_results=evidence_results,
        baseline_alias=baseline_alias,
        baseline_run_dir=baseline_run_dir,
        dry_run=args.dry_run
    )
    
    # Dry run: output facts-only info
    if args.dry_run:
        print(f"Dry run: Would create file: {output_path.relative_to(repo_root)}")
        print(f"\nEvidence files:")
        for key, value in evidence_results.items():
            if value.startswith('missing:'):
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {value}")
        print(f"\nMetadata:")
        print(f"  lane: {lane}")
        print(f"  round: {round_id}")
        print(f"  run_dir: {run_dir.relative_to(repo_root) if run_dir.is_relative_to(repo_root) else run_dir}")
        if baseline_alias:
            print(f"  baseline_alias: {baseline_alias}")
        if baseline_run_dir:
            print(f"  baseline_run_dir: {baseline_run_dir}")
        return
    
    # Check if file exists
    if output_path.exists() and not args.overwrite:
        print(f"Error: File already exists: {output_path.relative_to(repo_root)}", file=sys.stderr)
        print(f"Use --overwrite to overwrite.", file=sys.stderr)
        sys.exit(1)
    
    # Write file
    output_path.write_text(document_content, encoding='utf-8')
    print(f"Created judgment document: {output_path.relative_to(repo_root)}")


if __name__ == '__main__':
    main()
