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
    return render_template("admin/dashboard.html")
