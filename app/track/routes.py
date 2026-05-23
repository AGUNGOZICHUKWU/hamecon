"""Public tracking routes. NOT behind login - recipients are not logged-in users."""

from flask import Blueprint, render_template, request, redirect, url_for, abort
from app.models.sent_message import SentMessage, record_click, record_submit

track_bp = Blueprint("track", __name__, template_folder="../templates/track")


@track_bp.route("/t/<token>")
def click(token):
    """The recipient clicked the link in their simulated phishing message."""
    msg = SentMessage.get_by_token(token)
    if not msg:
        abort(404)
    record_click(msg.id, request.remote_addr,
                 request.headers.get("User-Agent", ""))
    return render_template("track/landing.html", token=token)


@track_bp.route("/s/<token>", methods=["POST"])
def submit(token):
    """
    The recipient submitted the fake form.
    We measure the total input length, then discard the values.
    The actual typed text is NEVER stored or logged.
    """
    msg = SentMessage.get_by_token(token)
    if not msg:
        abort(404)
    total_len = sum(len(v) for v in request.form.values())
    record_submit(msg.id, total_len, request.remote_addr,
                  request.headers.get("User-Agent", ""))
    return redirect(url_for("track.learn", token=token))


@track_bp.route("/learn/<token>")
def learn(token):
    """Teachable moment - the real AI version is built in Day 11."""
    msg = SentMessage.get_by_token(token)
    if not msg:
        abort(404)
    return render_template("track/learn_placeholder.html")
