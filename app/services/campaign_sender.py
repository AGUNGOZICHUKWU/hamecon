"""Campaign send engine: consent gate + Gmail SMTP delivery."""

import os
from app.models.user import _conn
from app.models.recipient import Recipient
from app.models.campaign import Campaign
from app.models.sent_message import SentMessage
from app.email.sender import send_email

_SENDER_NAMES = {
    "mobile_money": "MTN Mobile Money",
    "banking":      "Afriland First Bank",
    "university":   "Service Scolarité",
}

_TRACKING_BASE = os.environ.get("TRACKING_BASE_URL", "http://172.20.10.8:5000")


def send_campaign(campaign_id: int) -> dict:
    camp = Campaign.get(campaign_id)
    if not camp:
        return {"error": "Campaign not found."}
    if camp.status != "approved":
        return {"error": f"Campaign status is '{camp.status}', not 'approved'."}
    if camp.channel != "email":
        return {"error": "SMS dispatch is a later step. This campaign is SMS."}

    c = _conn()
    c.execute("UPDATE campaigns SET status='sending', started_at=CURRENT_TIMESTAMP WHERE id=?",
              (campaign_id,))
    c.commit(); c.close()

    sent = 0
    skipped_no_consent = 0
    failed = 0

    for recipient in Recipient.all():
        # ===== THE CONSENT GATE =====
        if not recipient.has_active_consent():
            skipped_no_consent += 1
            continue
        # ============================

        msg = SentMessage.create(
            campaign_id=camp.id, recipient_id=recipient.id,
            channel="email", subject=camp.draft_subject, body=camp.draft_body,
        )
        tracking_url = f"{_TRACKING_BASE}/t/{msg.tracking_token}"
        body = camp.draft_body or ""
        if "{{TRACKING_LINK}}" in body:
            body = body.replace("{{TRACKING_LINK}}", tracking_url)
        else:
            body += f'<p><a href="{tracking_url}">{tracking_url}</a></p>'

        try:
            send_email(recipient.email, camp.draft_subject, body,
                       from_name=camp.from_name or _SENDER_NAMES.get(camp.scenario, "Hamecon Training"))
        except Exception:
            failed += 1

    c = _conn()
    c.execute("UPDATE campaigns SET status='completed', completed_at=CURRENT_TIMESTAMP WHERE id=?",
              (campaign_id,))
    c.commit(); c.close()

    return {"sent": sent, "skipped_no_consent": skipped_no_consent, "failed": failed}
