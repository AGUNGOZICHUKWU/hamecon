"""Admin reports route."""

from flask import render_template
from flask_login import login_required
from app.admin.routes import admin_bp
from app.services.reports import campaign_metrics, recipient_metrics


@admin_bp.route("/reports")
@login_required
def reports():
    return render_template(
        "admin/reports.html",
        campaigns=campaign_metrics(),
        recipients=recipient_metrics(),
    )
