#!/usr/bin/env python3
"""
Minimal runtime verification for round md path + ingest integration.
This is a scratch/test script, not a production tool.

Facts-only. Does NOT modify contracts/dashboard docs.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def main() -> None:
    print("=" * 60)
    print("Round MD Path + Ingest Verification (facts-only)")
    print("=" * 60)

    # Create temporary run_dir structure
    # Pattern: verification/runs/facts/<lane>/round<NN>_<timestamp>
    temp_base = Path(tempfile.mkdtemp(prefix="verify_round_md_"))
    print(f"\n[1] Temp base: {temp_base}")

    lane = "geo_v0_s1"
    round_num = 99
    run_dir_name = f"round{round_num}_20260130_120000"
    fake_run_dir = temp_base / "verification" / "runs" / "facts" / lane / run_dir_name
    fake_run_dir.mkdir(parents=True, exist_ok=True)

    # Create minimal facts_summary.json
    facts_summary_path = fake_run_dir / "facts_summary.json"
    facts_summary_path.write_text('{"schema_version": "test"}', encoding="utf-8")
    print(f"[2] Created fake run_dir: {fake_run_dir}")
    print(f"    facts_summary.json: {facts_summary_path.exists()}")

    # Import update_new_round_registry
    try:
        from tools.postprocess_round import update_new_round_registry, project_root as pp_root
    except ImportError as e:
        print(f"[ERROR] Failed to import update_new_round_registry: {e}")
        shutil.rmtree(temp_base, ignore_errors=True)
        sys.exit(1)

    # We need to temporarily set project_root for the function
    # But since it uses a global, we'll call with paths relative to our temp

    # Actually, we need to call the function with proper paths
    # The function uses project_root global, so we need to patch it or work around

    # Workaround: We'll test the path computation logic directly
    print("\n[3] Testing path computation logic...")

    milestone_id = "M01_baseline"
    lane_slug = lane.replace("/", "_")
    round_md_dir = project_root / "docs" / "ops" / "rounds" / lane_slug / milestone_id
    round_md_filename = f"round_{round_num:02d}.md"
    round_md_path = round_md_dir / round_md_filename
    round_md_relpath = f"docs/ops/rounds/{lane_slug}/{milestone_id}/{round_md_filename}"

    print(f"    lane: {lane}")
    print(f"    lane_slug: {lane_slug}")
    print(f"    round_num: {round_num}")
    print(f"    milestone_id: {milestone_id}")
    print(f"    round_md_relpath: {round_md_relpath}")
    print(f"    round_md_path: {round_md_path}")

    # Check if directory can be created
    print("\n[4] Creating round md directory (idempotent)...")
    try:
        round_md_dir.mkdir(parents=True, exist_ok=True)
        print(f"    Directory exists: {round_md_dir.exists()}")
    except Exception as e:
        print(f"    [ERROR] Failed to create directory: {e}")

    # Check if stub needs to be created
    stub_created = False
    if not round_md_path.exists():
        print("\n[5] Creating stub (file does not exist)...")
        
        # Try template first
        template_candidates = [
            project_root / "docs" / "ops" / "rounds" / "ROUND_TEMPLATE.md",
            project_root / "docs" / "ops" / "rounds" / "ROUND_TEMPLATE_v1.md",
        ]
        stub_content = None
        template_used = None
        for tpl_path in template_candidates:
            if tpl_path.exists():
                try:
                    stub_content = tpl_path.read_text(encoding="utf-8")
                    template_used = tpl_path.name
                    break
                except Exception:
                    continue

        if stub_content:
            print(f"    Using template: {template_used}")
        else:
            print("    No template found, using fallback stub")
            stub_content = f"""# Round {round_num}

## Goal
[라운드 목표를 간단히 기술]

## Changes
[주요 변경사항을 나열]

## Artifacts
- **run_dir**: `verification/runs/facts/{lane}/{run_dir_name}`

## Progress Events (dashboard)

```jsonl
# (optional) one event per line
```

## Notes
[추가 메모]
"""

        round_md_path.write_text(stub_content, encoding="utf-8")
        stub_created = True
        print(f"    Stub written: {round_md_path.exists()}")
    else:
        print("\n[5] Stub already exists (not overwriting)")
        stub_content = round_md_path.read_text(encoding="utf-8")

    # Verify stub contains required sections
    print("\n[6] Verifying stub content...")
    has_progress_section = "## Progress Events (dashboard)" in stub_content
    has_jsonl_fence = "```jsonl" in stub_content
    has_fence_close = stub_content.count("```") >= 2  # At least open and close

    print(f"    Contains '## Progress Events (dashboard)': {has_progress_section}")
    print(f"    Contains '```jsonl': {has_jsonl_fence}")
    print(f"    Has fence close (```): {has_fence_close}")

    # Test ingest call
    print("\n[7] Testing ingest subprocess call...")
    ingest_script = project_root / "tools" / "ingest_round_progress_events_v0.py"
    if not ingest_script.exists():
        print(f"    [ERROR] Ingest script not found: {ingest_script}")
    else:
        cmd = [
            sys.executable,
            str(ingest_script),
            "--round-path", str(round_md_path),
            "--hub-root", str(project_root),
            "--dry-run"  # Don't actually append to log
        ]
        print(f"    Command: {' '.join(cmd[:3])} ...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"    Exit code: {result.returncode}")
        print(f"    Stdout: {result.stdout.strip()[:200] if result.stdout else '(empty)'}")
        if result.stderr:
            print(f"    Stderr: {result.stderr.strip()[:200]}")

    # Cleanup
    print("\n[8] Cleanup...")
    shutil.rmtree(temp_base, ignore_errors=True)
    print(f"    Temp dir removed: {not temp_base.exists()}")

    # Optionally clean up created stub if we made it
    if stub_created:
        print(f"    Note: Stub was created at {round_md_path}")
        print(f"    This is a REAL file in the repo. Consider removing if unneeded.")

    print("\n" + "=" * 60)
    print("Verification complete (facts-only)")
    print("=" * 60)


if __name__ == "__main__":
    main()
