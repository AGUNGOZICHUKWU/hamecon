"""Report metrics: turns raw click/submit/training events into numbers."""

from app.models.user import _conn


def campaign_metrics():
    """One row per campaign with engagement counts and click rate."""
    c = _conn()
    camps = c.execute(
        "SELECT id, name, channel, scenario, difficulty, status FROM campaigns ORDER BY id DESC"
    ).fetchall()
    result = []
    for camp in camps:
        cid = camp["id"]
        sent = c.execute(
            "SELECT COUNT(*) FROM sent_messages WHERE campaign_id=?", (cid,)
        ).fetchone()[0]
        clicked = c.execute(
            """SELECT COUNT(DISTINCT ce.sent_message_id)
                 FROM click_events ce
                 JOIN sent_messages sm ON sm.id = ce.sent_message_id
                WHERE sm.campaign_id=?""", (cid,)
        ).fetchone()[0]
        submitted = c.execute(
            """SELECT COUNT(DISTINCT se.sent_message_id)
                 FROM submit_events se
                 JOIN sent_messages sm ON sm.id = se.sent_message_id
                WHERE sm.campaign_id=?""", (cid,)
        ).fetchone()[0]
        trained = c.execute(
            """SELECT COUNT(DISTINCT ts.sent_message_id)
                 FROM training_sessions ts
                 JOIN sent_messages sm ON sm.id = ts.sent_message_id
                WHERE sm.campaign_id=?""", (cid,)
        ).fetchone()[0]
        click_rate = round(100 * clicked / sent, 1) if sent else 0.0
        result.append({
            "name": camp["name"], "channel": camp["channel"],
            "scenario": camp["scenario"], "difficulty": camp["difficulty"],
            "status": camp["status"], "sent": sent, "clicked": clicked,
            "submitted": submitted, "trained": trained, "click_rate": click_rate,
        })
    c.close()
    return result


def recipient_metrics():
    """One row per recipient with a vulnerability score (click rate %)."""
    c = _conn()
    recs = c.execute(
        "SELECT id, full_name, email FROM recipients WHERE is_active=1 ORDER BY full_name"
    ).fetchall()
    result = []
    for r in recs:
        rid = r["id"]
        received = c.execute(
            "SELECT COUNT(*) FROM sent_messages WHERE recipient_id=?", (rid,)
        ).fetchone()[0]
        clicked = c.execute(
            """SELECT COUNT(DISTINCT ce.sent_message_id)
                 FROM click_events ce
                 JOIN sent_messages sm ON sm.id = ce.sent_message_id
                WHERE sm.recipient_id=?""", (rid,)
        ).fetchone()[0]
        score = round(100 * clicked / received, 1) if received else 0.0
        result.append({
            "name": r["full_name"], "email": r["email"],
            "received": received, "clicked": clicked, "vulnerability": score,
        })
    c.close()
    return result
