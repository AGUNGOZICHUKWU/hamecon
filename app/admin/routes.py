"""Admin routes. All require login; some require the admin role."""

from functools import wraps
from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")


def role_required(role_name):
    """Decorator: reject with 403 if the logged-in user lacks the role."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not current_user.has_role(role_name):
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    from app.services.reports import campaign_metrics, recipient_metrics
    camps = campaign_metrics()
    recs = recipient_metrics()
    total_sent = sum(c["sent"] for c in camps)
    total_clicked = sum(c["clicked"] for c in camps)
    stats = {
        "campaigns": len(camps),
        "recipients": len(recs),
        "sent": total_sent,
        "clicked": total_clicked,
        "trained": sum(c["trained"] for c in camps),
        "click_rate": round(100 * total_clicked / total_sent, 1) if total_sent else 0.0,
        "high_risk": sum(1 for r in recs if r["vulnerability"] >= 50),
        "active": sum(1 for c in camps if c["status"] in ("approved", "sent")),
    }
    top = sorted(camps, key=lambda c: c["click_rate"], reverse=True)[:5]
    return render_template("admin/dashboard.html", stats=stats, top_campaigns=top)
