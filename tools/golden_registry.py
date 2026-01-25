#!/usr/bin/env python3
"""
Golden Registry Maintenance Tool

golden_registry.json을 자동으로 갱신합니다.
NPZ 파일의 족보를 추적하기 위한 facts-only 기록입니다.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))


def compute_file_hash(file_path: Path, max_size_mb: int = 50) -> Optional[str]:
    """Compute SHA256 hash of file if size <= max_size_mb."""
    if not file_path.exists():
        return None
    
    try:
        size_bytes = file_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb > max_size_mb:
            return None  # Skip large files
        
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def get_file_metadata(file_path: Path) -> Optional[Dict[str, Any]]:
    """Get file mtime and size."""
    if not file_path.exists():
        return None
    try:
        stat = file_path.stat()
        return {
            "mtime": stat.st_mtime,
            "size_bytes": stat.st_size
        }
    except Exception:
        return None


def extract_npz_metadata(npz_path: Path) -> Dict[str, Any]:
    """Extract metadata from NPZ file."""
    metadata = {
        "schema_version": None,
        "meta_unit": None
    }
    
    if not npz_path.exists():
        return metadata
    
    try:
        import numpy as np
        npz_data = np.load(npz_path, allow_pickle=True)
        
        if "schema_version" in npz_data:
            schema = npz_data["schema_version"]
            if isinstance(schema, (str, bytes)):
                metadata["schema_version"] = str(schema)
            elif hasattr(schema, 'item'):
                metadata["schema_version"] = str(schema.item())
        
        if "meta_unit" in npz_data:
            unit = npz_data["meta_unit"]
            if isinstance(unit, (str, bytes)):
                metadata["meta_unit"] = str(unit)
            elif hasattr(unit, 'item'):
                metadata["meta_unit"] = str(unit.item())
    except Exception:
        pass  # NPZ metadata extraction failed
    
    return metadata


def find_generator_script(npz_path: Path) -> tuple[Optional[str], Optional[str]]:
    """Find generator script and its commit hash."""
    # Common patterns
    patterns = [
        "create_real_data_golden.py",
        "create_s0_dataset.py",
        "export_golden_*.py"
    ]
    
    for pattern in patterns:
        for gen_file in project_root.rglob(pattern):
            if gen_file.exists():
                gen_rel = str(gen_file.relative_to(project_root))
                # Try to get commit
                try:
                    result = subprocess.run(
                        ["git", "log", "-n", "1", "--pretty=format:%H", "--", gen_rel],
                        capture_output=True,
                        text=True,
                        check=True,
                        cwd=str(project_root)
                    )
                    commit = result.stdout.strip() if result.stdout.strip() else None
                except Exception:
                    commit = None
                
                return gen_rel, commit
    
    return None, None


def load_golden_registry(registry_path: Path) -> Dict[str, Any]:
    """Load golden registry."""
    if not registry_path.exists():
        return {
            "schema_version": "golden_registry@1",
            "updated_at": datetime.now().isoformat(),
            "entries": []
        }
    
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
        
        # Ensure schema_version
        if "schema_version" not in registry:
            registry["schema_version"] = "golden_registry@1"
        
        # Ensure entries
        if "entries" not in registry:
            registry["entries"] = []
        
        return registry
    except Exception as e:
        print(f"Warning: Failed to load golden registry: {e}", file=sys.stderr)
        return {
            "schema_version": "golden_registry@1",
            "updated_at": datetime.now().isoformat(),
            "entries": []
        }


def upsert_golden_entry(
    registry_path: Path,
    npz_path: Path,
    source_path_abs: Optional[str] = None
) -> None:
    """Upsert golden registry entry for an NPZ file."""
    registry = load_golden_registry(registry_path)
    
    # Convert npz_path to relative if possible
    try:
        npz_rel = str(npz_path.relative_to(project_root))
    except ValueError:
        npz_rel = str(npz_path)
    
    npz_abs = str(npz_path.resolve())
    
    # Check if entry exists
    existing_idx = None
    for i, entry in enumerate(registry["entries"]):
        if entry.get("npz_path") == npz_rel or entry.get("npz_path_abs") == npz_abs:
            existing_idx = i
            break
    
    # Get file metadata
    file_meta = get_file_metadata(npz_path)
    if not file_meta:
        print(f"Warning: NPZ file not found: {npz_path}", file=sys.stderr)
        return
    
    # Extract NPZ metadata
    npz_metadata = extract_npz_metadata(npz_path)
    
    # Find generator script
    generator_script, generator_commit = find_generator_script(npz_path)
    
    # Compute hash (only for small files)
    npz_sha256 = compute_file_hash(npz_path, max_size_mb=50)
    
    # Create entry
    entry = {
        "npz_path": npz_rel,
        "npz_path_abs": npz_abs,
        "npz_sha256": npz_sha256,
        "npz_mtime": file_meta["mtime"],
        "npz_size_bytes": file_meta["size_bytes"],
        "schema_version": npz_metadata.get("schema_version"),
        "meta_unit": npz_metadata.get("meta_unit"),
        "source_path_abs": source_path_abs,
        "generator_script": generator_script,
        "generator_commit": generator_commit,
        "notes": ""
    }
    
    # Upsert
    if existing_idx is not None:
        registry["entries"][existing_idx] = entry
    else:
        registry["entries"].append(entry)
    
    # Update timestamp
    registry["updated_at"] = datetime.now().isoformat()
    
    # Atomic write
    temp_path = registry_path.with_suffix(".json.tmp")
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        # Ensure parent directory exists
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic rename
        shutil.move(str(temp_path), str(registry_path))
        
        print(f"Updated: {registry_path} ({len(registry['entries'])} entries)")
    except Exception as e:
        print(f"Error: Failed to write golden registry: {e}", file=sys.stderr)
        if temp_path.exists():
            temp_path.unlink()
        raise


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Update golden registry from NPZ file"
    )
    parser.add_argument(
        "--npz_path",
        type=str,
        required=True,
        help="Path to NPZ file"
    )
    parser.add_argument(
        "--source_path_abs",
        type=str,
        default=None,
        help="Source file absolute path (optional)"
    )
    parser.add_argument(
        "--registry_path",
        type=str,
        default="docs/verification/golden_registry.json",
        help="Golden registry path"
    )
    
    args = parser.parse_args()
    
    npz_path = (project_root / args.npz_path).resolve()
    registry_path = project_root / args.registry_path
    
    source_path_abs = None
    if args.source_path_abs:
        source_path_abs = str(Path(args.source_path_abs).resolve())
    
    upsert_golden_entry(
        registry_path=registry_path,
        npz_path=npz_path,
        source_path_abs=source_path_abs
    )


if __name__ == "__main__":
    main()
