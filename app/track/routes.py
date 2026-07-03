"""Public tracking routes. NOT behind login."""

from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.models.sent_message import SentMessage, record_click, record_submit
from app.models.user import _conn

track_bp = Blueprint("track", __name__, template_folder="../templates/track")

@track_bp.route("/t/PREVIEW")
def preview():
    """Placeholder landing shown when an operator clicks a preview tracking link.

    This route exists so previewing a campaign draft does not return a 404.
    No click event is recorded, no consent is checked, and no real recipient
    data is touched. It is a visual aid for the operator during review.
    """
    return (
        "<html><body style='font-family:sans-serif;padding:2em;"
        "background:#fdf7e3;color:#333;'>"
        "<h2 style='color:#b8860b;'>Preview Link</h2>"
        "<p>This is what a real recipient would land on when they click "
        "the tracking link in a dispatched message.</p>"
        "<p><strong>No click event is recorded in preview mode.</strong></p>"
        "</body></html>",
        200,
    )

@track_bp.route("/t/<token>")
def click(token):
    msg = SentMessage.get_by_token(token)
    if not msg:
        abort(404)
    record_click(msg.id, request.remote_addr,
                 request.headers.get("User-Agent", ""))
    # Pick branded template by campaign scenario
    from app.models.campaign import Campaign
    camp = Campaign.get(msg.campaign_id)
    scenario = camp.scenario if camp else "mobile_money"
    template_map = {
        "mobile_money": "track/landing_momo.html",
        "banking":      "track/landing_bank.html",

    }
    # Special: if from_name mentions Orange, use Orange template
    if camp and camp.from_name and "orange" in camp.from_name.lower():
        return render_template("track/landing_orange.html", token=token)
    return render_template(template_map.get(scenario, "track/landing.html"), token=token)


@track_bp.route("/s/<token>", methods=["POST"])
def submit(token):
    msg = SentMessage.get_by_token(token)
    if not msg:
        abort(404)
    total_len = sum(len(v) for v in request.form.values())
    record_submit(msg.id, total_len, request.remote_addr,
                  request.headers.get("User-Agent", ""))
    return redirect(url_for("track.learn", token=token))


def _get_or_create_lesson(msg):
    """Return the cached lesson if one exists; otherwise generate via Claude and cache it."""
    c = _conn()
    row = c.execute(
        "SELECT lesson_text FROM training_sessions WHERE sent_message_id=?",
        (msg.id,),
    ).fetchone()
    if row:
        c.close()
        return row["lesson_text"]
    # Fetch the campaign for its language.
    camp = c.execute("SELECT language FROM campaigns WHERE id=?",
                     (msg.campaign_id,)).fetchone()
    language = camp["language"] if camp else "fr"
    c.close()

    from app.ai.generator import generate_lesson
    lesson = generate_lesson(
        msg.subject or "(SMS message)", msg.body,
        channel=msg.channel, language=language,
    )
    c = _conn()
    c.execute(
        "INSERT INTO training_sessions (sent_message_id, lesson_text) VALUES (?,?)",
        (msg.id, lesson),
    )
    c.commit(); c.close()
    return lesson


@track_bp.route("/learn/<token>")
def learn(token):
    import json as _json
    msg = SentMessage.get_by_token(token)
    if not msg:
        abort(404)
    lesson_raw = _get_or_create_lesson(msg)

    lesson_data = None
    try:
        lesson_data = _json.loads(lesson_raw)
        # Validate expected shape
        if not isinstance(lesson_data.get("red_flags"), list):
            lesson_data = None
    except Exception:
        pass

    from app.models.campaign import Campaign
    camp = Campaign.get(msg.campaign_id)
    scenario = camp.scenario if camp else "banking"
    from_name = (camp.from_name or "") if camp else ""

    return render_template(
        "track/learn.html",
        lesson=lesson_raw,
        lesson_data=lesson_data,
        scenario=scenario,
        from_name=from_name,
    )
