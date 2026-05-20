"""User model: bcrypt passwords + Flask-Login integration."""

import sqlite3
import bcrypt
from pathlib import Path
from flask_login import UserMixin

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "hamecon.db"


def _conn():
    """Open a SQLite connection: foreign keys on, rows accessible by column name."""
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON;")
    return c


class User(UserMixin):
    def __init__(self, row):
        self.id            = row["id"]
        self.username      = row["username"]
        self.email         = row["email"]
        self.password_hash = row["password_hash"]
        self.role_id       = row["role_id"]
        self.role_name     = row["role_name"]
        self.is_active_db  = bool(row["is_active"])

    @property
    def is_active(self):
        return self.is_active_db

    @staticmethod
    def _row_to_user(row):
        return User(row) if row else None

    @classmethod
    def get(cls, user_id: int):
        c = _conn()
        row = c.execute(
            """SELECT u.*, r.name AS role_name
                 FROM users u JOIN roles r ON r.id = u.role_id
                WHERE u.id = ?""",
            (user_id,),
        ).fetchone()
        c.close()
        return cls._row_to_user(row)

    @classmethod
    def get_by_username(cls, username: str):
        c = _conn()
        row = c.execute(
            """SELECT u.*, r.name AS role_name
                 FROM users u JOIN roles r ON r.id = u.role_id
                WHERE u.username = ?""",
            (username,),
        ).fetchone()
        c.close()
        return cls._row_to_user(row)

    def check_password(self, plain: str) -> bool:
        return bcrypt.checkpw(plain.encode("utf-8"), self.password_hash.encode("utf-8"))

    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

    def has_role(self, role_name: str) -> bool:
        return self.role_name == role_name
