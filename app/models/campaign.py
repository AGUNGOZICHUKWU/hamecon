"""Campaign model: holds the brief, the AI draft, and the lifecycle status."""

from app.models.user import _conn


class Campaign:
    def __init__(self, row):
        self.id            = row["id"]
        self.name          = row["name"]
        self.brief         = row["brief"]
        self.channel       = row["channel"]
        self.language      = row["language"]
        self.difficulty    = row["difficulty"]
        self.scenario      = row["scenario"]
        self.status        = row["status"]
        self.draft_subject = row["draft_subject"]
        self.draft_body    = row["draft_body"]
        self.created_by    = row["created_by"]
        self.created_at    = row["created_at"]
        self.from_name     = row["from_name"] if "from_name" in row.keys() else None

    @classmethod
    def all(cls):
        c = _conn()
        rows = c.execute("SELECT * FROM campaigns ORDER BY created_at DESC").fetchall()
        c.close()
        return [cls(r) for r in rows]

    @classmethod
    def get(cls, campaign_id):
        c = _conn()
        r = c.execute("SELECT * FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
        c.close()
        return cls(r) if r else None

    @classmethod
    def create(cls, name, brief, channel, language, difficulty, scenario,
               draft_subject, draft_body, created_by, from_name=None):
        c = _conn()
        cur = c.execute(
            """INSERT INTO campaigns
               (name, brief, channel, language, difficulty, scenario,
                draft_subject, draft_body, created_by, from_name)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (name, brief, channel, language, difficulty, scenario,
             draft_subject, draft_body, created_by, from_name),
        )
        cid = cur.lastrowid
        c.commit(); c.close()
        return cls.get(cid)

    @staticmethod
    def approve(campaign_id, approved_by):
        """Move a campaign from 'draft' to 'approved'. Only drafts can be approved."""
        c = _conn()
        c.execute(
            """UPDATE campaigns
               SET status='approved', approved_by=?, approved_at=CURRENT_TIMESTAMP
               WHERE id=? AND status='draft'""",
            (approved_by, campaign_id),
        )
        c.commit(); c.close()
