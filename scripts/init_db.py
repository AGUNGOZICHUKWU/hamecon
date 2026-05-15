#!/usr/bin/env python3
"""
init_db.py - Create the Hamecon SQLite database from data/schema.sql

Usage:
    python scripts/init_db.py

Safety: refuses to run if the database already exists, so it can never
silently destroy data. Delete data/hamecon.db by hand for a fresh start.
"""

import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = PROJECT_ROOT / "data" / "schema.sql"
DB_PATH = PROJECT_ROOT / "data" / "hamecon.db"


def main():
    if not SCHEMA_PATH.exists():
        print(f"ERROR: schema file not found at {SCHEMA_PATH}")
        sys.exit(1)

    if DB_PATH.exists():
        print(f"ERROR: database already exists at {DB_PATH}")
        print("For a fresh database, delete it first with:")
        print(f"    rm {DB_PATH}")
        sys.exit(1)

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    print(f"Creating database at {DB_PATH} ...")
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()

    print("Database created successfully.")
    print(f"  Location: {DB_PATH}")
    print("Now run: python scripts/verify_db.py")


if __name__ == "__main__":
    main()
