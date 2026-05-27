"""Read-only audit log viewer."""

from flask import render_template
from flask_login import login_required
from app.admin.routes import admin_bp
from app.models.user import _conn


@admin_bp.route("/audit")
@login_required
def audit_log_view():
    c = _conn()
    total = c.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
    rows = c.execute(
        """SELECT al.id, al.created_at, al.action, al.target,
                  al.details, al.ip_address, u.username
             FROM audit_log al
             LEFT JOIN users u ON u.id = al.user_id
            ORDER BY al.id DESC
            LIMIT 100"""
    ).fetchall()
    c.close()
    return render_template("admin/audit.html",
                           entries=[dict(r) for r in rows], total=total)
