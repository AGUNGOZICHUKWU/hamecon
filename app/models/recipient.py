"""Recipient and ConsentRecord models. Consent is enforced via a method."""

from app.models.user import _conn


class Recipient:
    def __init__(self, row):
        self.id           = row["id"]
        self.full_name    = row["full_name"]
        self.email        = row["email"]
        self.language     = row["language"]
        self.organisation = row["organisation"]
        self.notes        = row["notes"]
        self.is_active    = bool(row["is_active"])

    @classmethod
    def all(cls):
        c = _conn()
        rows = c.execute(
            "SELECT * FROM recipients WHERE is_active=1 ORDER BY full_name"
        ).fetchall()
        c.close()
        return [cls(r) for r in rows]

    @classmethod
    def get(cls, recipient_id: int):
        c = _conn()
        r = c.execute("SELECT * FROM recipients WHERE id=?", (recipient_id,)).fetchone()
        c.close()
        return cls(r) if r else None

    @classmethod
    def create(cls, full_name, email, language, organisation, notes):
        c = _conn()
        cur = c.execute(
            """INSERT INTO recipients (full_name, email, language, organisation, notes)
               VALUES (?, ?, ?, ?, ?)""",
            (full_name, email, language, organisation, notes),
        )
        rid = cur.lastrowid
        c.commit(); c.close()
        return cls.get(rid)

    def has_active_consent(self) -> bool:
        """The legal gate. No message may be sent unless this returns True."""
        c = _conn()
        row = c.execute(
            """SELECT id FROM consent_records
               WHERE recipient_id = ?
                 AND revoked_at IS NULL
                 AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)""",
            (self.id,),
        ).fetchone()
        c.close()
        return row is not None


class ConsentRecord:
    @staticmethod
    def grant(recipient_id, granted_by_user, scope, evidence_note, expires_at=None):
        c = _conn()
        c.execute(
            """INSERT INTO consent_records
               (recipient_id, granted_by_user, scope, evidence_note, expires_at)
               VALUES (?, ?, ?, ?, ?)""",
            (recipient_id, granted_by_user, scope, evidence_note, expires_at),
        )
        c.commit(); c.close()
    
    @staticmethod
    def revoke(recipient_id):
        """Mark the active consent record as revoked."""
        c = _conn()
        c.execute(
            """UPDATE consent_records
               SET revoked_at = CURRENT_TIMESTAMP
               WHERE recipient_id = ?
                 AND revoked_at IS NULL""",
            (recipient_id,),
        )
        c.commit(); c.close()