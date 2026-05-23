"""SentMessage model + click/submit event recording."""

import secrets
from app.models.user import _conn


class SentMessage:
    def __init__(self, row):
        self.id             = row["id"]
        self.campaign_id    = row["campaign_id"]
        self.recipient_id   = row["recipient_id"]
        self.channel        = row["channel"]
        self.subject        = row["subject"]
        self.body           = row["body"]
        self.tracking_token = row["tracking_token"]
        self.sent_at        = row["sent_at"]

    @staticmethod
    def new_token() -> str:
        """An unguessable, URL-safe random token. secrets is cryptographically strong."""
        return secrets.token_urlsafe(16)

    @classmethod
    def get_by_token(cls, token):
        c = _conn()
        r = c.execute("SELECT * FROM sent_messages WHERE tracking_token=?",
                      (token,)).fetchone()
        c.close()
        return cls(r) if r else None

    @classmethod
    def create(cls, campaign_id, recipient_id, channel, subject, body):
        token = cls.new_token()
        c = _conn()
        c.execute(
            """INSERT INTO sent_messages
               (campaign_id, recipient_id, channel, subject, body, tracking_token)
               VALUES (?,?,?,?,?,?)""",
            (campaign_id, recipient_id, channel, subject, body, token),
        )
        c.commit(); c.close()
        return cls.get_by_token(token)


def record_click(sent_message_id, ip, user_agent):
    """Record that a tracking link was clicked."""
    c = _conn()
    c.execute(
        "INSERT INTO click_events (sent_message_id, ip_address, user_agent) VALUES (?,?,?)",
        (sent_message_id, ip, user_agent),
    )
    c.commit(); c.close()


def record_submit(sent_message_id, input_length, ip, user_agent):
    """
    Record THAT a fake form was submitted.
    SECURITY RULE: we store only the input LENGTH, never the content.
    The submitted text is never read into a variable that is saved or logged.
    """
    c = _conn()
    c.execute(
        """INSERT INTO submit_events
           (sent_message_id, input_length, ip_address, user_agent)
           VALUES (?,?,?,?)""",
        (sent_message_id, input_length, ip, user_agent),
    )
    c.commit(); c.close()
