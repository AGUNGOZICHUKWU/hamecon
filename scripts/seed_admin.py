"""Seed an admin user. Run once."""

import sys
import getpass
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.user import User, _conn


def main():
    username = input("Admin username: ").strip()
    email    = input("Admin email: ").strip()
    pw       = getpass.getpass("Admin password (8+ chars): ")
    if len(pw) < 8:
        print("Password too short."); sys.exit(1)

    c = _conn()
    if c.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone():
        print("That username already exists."); sys.exit(1)

    admin_role = c.execute("SELECT id FROM roles WHERE name = 'admin'").fetchone()
    if not admin_role:
        print("admin role missing - re-run init_db.py."); sys.exit(1)

    c.execute(
        "INSERT INTO users (username, email, password_hash, role_id) VALUES (?, ?, ?, ?)",
        (username, email, User.hash_password(pw), admin_role[0]),
    )
    c.commit()
    print(f"Created admin user '{username}'.")
    c.close()


if __name__ == "__main__":
    main()
