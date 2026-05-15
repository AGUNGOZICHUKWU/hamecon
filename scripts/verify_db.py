#!/usr/bin/env python3
"""
verify_db.py - Check that the Hamecon database has all expected tables.

Usage:
    python scripts/verify_db.py
"""

import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "hamecon.db"

EXPECTED_TABLES = [
    "roles", "users", "recipients", "consent_records", "campaigns",
    "sent_emails", "click_events", "submit_events", "training_sessions",
    "audit_log",
]


def main():
    if not DB_PATH.exists():
        print(f"ERROR: database not found at {DB_PATH}")
        print("Run 'python scripts/init_db.py' first.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        ).fetchall()
        found = [r[0] for r in rows]

        print("Tables found in the database:")
        for t in found:
            print(f"  - {t}")

        missing = [t for t in EXPECTED_TABLES if t not in found]
        extra = [t for t in found if t not in EXPECTED_TABLES]

        print()
        if missing:
            print(f"MISSING tables: {missing}")
        if extra:
            print(f"UNEXPECTED tables: {extra}")
        if not missing and not extra:
            print("All 10 expected tables are present. Schema looks correct.")

        roles = conn.execute("SELECT id, name FROM roles ORDER BY id;").fetchall()
        print()
        print("Seeded roles:")
        for r in roles:
            print(f"  {r[0]}: {r[1]}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
