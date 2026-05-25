"""Adaptive difficulty engine.

Rules-based and fully explainable. Given a recipient's history, it
recommends the difficulty of their NEXT phishing test:
  - No history          -> easy   (start gently)
  - Clicked last test   -> same   (needs more practice at this level)
  - Spotted last test   -> harder (ready for more challenge)
"""

from app.models.user import _conn

_ORDER = ["easy", "medium", "hard"]


def _harder(difficulty: str) -> str:
    """Return the next level up, capped at 'hard'."""
    i = _ORDER.index(difficulty) if difficulty in _ORDER else 0
    return _ORDER[min(i + 1, len(_ORDER) - 1)]


def recommend_difficulty(recipient_id: int) -> dict:
    """Return {'difficulty': str, 'reason': str} for this recipient's next test."""
    c = _conn()
    row = c.execute(
        """SELECT cmp.difficulty AS difficulty,
                  (SELECT COUNT(*) FROM click_events ce
                    WHERE ce.sent_message_id = sm.id) AS clicks
             FROM sent_messages sm
             JOIN campaigns cmp ON cmp.id = sm.campaign_id
            WHERE sm.recipient_id = ?
            ORDER BY sm.id DESC
            LIMIT 1""",
        (recipient_id,),
    ).fetchone()
    c.close()

    if not row:
        return {"difficulty": "easy",
                "reason": "No history yet — start with an easy scenario."}

    last = row["difficulty"]
    if row["clicks"] > 0:
        return {"difficulty": last,
                "reason": f"Clicked the last {last} test — repeat this level to reinforce."}
    return {"difficulty": _harder(last),
            "reason": f"Spotted the last {last} test — ready for more challenge."}
