#!/usr/bin/env python3
"""
Check DB Status - Verify if SQLite database is empty shell

Purpose: Check if a SQLite database has tables but no data rows.
"""

import sqlite3
import sys
from pathlib import Path


def check_db_status(db_path: str) -> dict:
    """Check database status: tables and row counts."""
    if not Path(db_path).exists():
        return {
            "exists": False,
            "error": f"Database file not found: {db_path}"
        }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # Count rows in each table
        table_counts = {}
        total_rows = 0
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_counts[table] = count
            total_rows += count
        
        conn.close()
        
        return {
            "exists": True,
            "tables": tables,
            "table_counts": table_counts,
            "total_rows": total_rows,
            "is_empty_shell": len(tables) > 0 and total_rows == 0,
            "has_data": total_rows > 0
        }
    except Exception as e:
        return {
            "exists": True,
            "error": str(e)
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/check_db_status.py <db_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    result = check_db_status(db_path)
    
    if not result.get("exists"):
        print(f"Error: {result.get('error')}")
        sys.exit(1)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    print(f"Database: {db_path}")
    print(f"Tables: {len(result['tables'])}")
    print(f"Total rows: {result['total_rows']}")
    print(f"Status: {'Empty shell' if result['is_empty_shell'] else 'Has data' if result['has_data'] else 'No tables'}")
    
    if result['table_counts']:
        print("\nTable row counts:")
        for table, count in result['table_counts'].items():
            print(f"  {table}: {count}")


if __name__ == "__main__":
    main()
