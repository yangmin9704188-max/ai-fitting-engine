#!/usr/bin/env python3
"""
Import 경계 검사 스크립트 (경찰관)

modules/ 디렉토리의 Cross-Module 참조 위반을 검사합니다.
- modules/body/** 가 modules/garment/** 를 참조하면 FAIL
- modules/garment/** 가 modules/body/** 를 참조하면 FAIL
- modules/fitting/** 만 body/garment의 스키마 경로(specs/schema) 참조 허용

전환기 처리: modules/가 없으면 SKIP하고 exit 0
"""

import os
import re
import sys
from pathlib import Path


def find_python_files(root_dir: Path) -> list[Path]:
    """Python 파일 목록을 재귀적으로 찾습니다."""
    python_files = []
    for file_path in root_dir.rglob("*.py"):
        python_files.append(file_path)
    return python_files


def check_imports_in_file(file_path: Path, violations: list[str]) -> None:
    """파일 내 import 문을 검사합니다."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
        return

    file_str = str(file_path)
    
    # modules/body/** 파일인 경우
    if "modules/body/" in file_str and "modules/body/specs" not in file_str:
        # modules/garment/** import 금지
        if re.search(r'from\s+modules\.garment|import\s+modules\.garment|from\s+["\']modules/garment', content):
            violations.append(f"{file_path}: modules/body/** cannot import modules/garment/**")
        # 상대경로 import도 체크
        if re.search(r'from\s+\.\.garment|from\s+\.\.\.garment', content):
            violations.append(f"{file_path}: modules/body/** cannot import modules/garment/** (relative import)")
    
    # modules/garment/** 파일인 경우
    if "modules/garment/" in file_str and "modules/garment/specs" not in file_str:
        # modules/body/** import 금지
        if re.search(r'from\s+modules\.body|import\s+modules\.body|from\s+["\']modules/body', content):
            violations.append(f"{file_path}: modules/garment/** cannot import modules/body/**")
        # 상대경로 import도 체크
        if re.search(r'from\s+\.\.body|from\s+\.\.\.body', content):
            violations.append(f"{file_path}: modules/garment/** cannot import modules/body/** (relative import)")
    
    # modules/fitting/** 파일인 경우 - 스키마 참조만 허용
    if "modules/fitting/" in file_str:
        # 허용되지 않는 직접 import 체크 (스키마 경로가 아닌 경우)
        body_imports = re.findall(r'from\s+modules\.body[^"\']*|import\s+modules\.body[^"\']*|from\s+["\']modules/body[^"\']*', content)
        for imp in body_imports:
            # specs/schema 경로는 허용
            if "specs" not in imp and "schema" not in imp:
                violations.append(f"{file_path}: modules/fitting/** can only import modules/body/** specs/schema, not: {imp.strip()}")
        
        garment_imports = re.findall(r'from\s+modules\.garment[^"\']*|import\s+modules\.garment[^"\']*|from\s+["\']modules/garment[^"\']*', content)
        for imp in garment_imports:
            # specs/schema 경로는 허용
            if "specs" not in imp and "schema" not in imp:
                violations.append(f"{file_path}: modules/fitting/** can only import modules/garment/** specs/schema, not: {imp.strip()}")


def main():
    """메인 함수"""
    repo_root = Path(__file__).parent.parent.parent
    modules_dir = repo_root / "modules"
    
    # 전환기 처리: modules/가 없으면 SKIP
    if not modules_dir.exists():
        print("SKIP: modules/ not found")
        sys.exit(0)
    
    violations = []
    python_files = find_python_files(modules_dir)
    
    for py_file in python_files:
        check_imports_in_file(py_file, violations)
    
    if violations:
        print("Import boundary violations found:")
        for violation in violations:
            print(f"  - {violation}")
        sys.exit(1)
    else:
        print("OK: No import boundary violations")
        sys.exit(0)


if __name__ == "__main__":
    main()
