"""Create one test sent_message so you can test tracking without sending email."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.user import _conn
from app.models.sent_message import SentMessage

c = _conn()
camp = c.execute("SELECT id FROM campaigns ORDER BY id DESC LIMIT 1").fetchone()
rec  = c.execute("SELECT id FROM recipients ORDER BY id DESC LIMIT 1").fetchone()
c.close()

if not camp or not rec:
    print("You need at least one campaign AND one recipient first.")
    print("Add a recipient and create a campaign in the dashboard, then re-run.")
    sys.exit(1)

msg = SentMessage.create(
    campaign_id=camp[0], recipient_id=rec[0], channel="email",
    subject="Test message",
    body="<p>Test. <a href='#'>link</a></p>",
)
print("Test message created. Open this URL in your browser:")
print(f"  http://172.20.10.8:5000/t/{msg.tracking_token}")
