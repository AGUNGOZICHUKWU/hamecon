"""Real auth: login, logout, audit logging."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User, _conn
from app.auth.forms import LoginForm

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


def _audit(user_id, action, details=None):
    """Write one row to audit_log. Never raises - auditing must not break auth."""
    try:
        c = _conn()
        c.execute(
            "INSERT INTO audit_log (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)",
            (user_id, action, details, request.remote_addr),
        )
        c.commit()
        c.close()
    except Exception:
        pass


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data.strip())
        if user and user.is_active and user.check_password(form.password.data):
            login_user(user)
            _audit(user.id, "login_success")
            flash(f"Welcome back, {user.username}.", "success")
            return redirect(url_for("admin.dashboard"))
        _audit(user.id if user else None, "login_failed", form.username.data.strip())
        flash("Invalid username or password.", "error")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    _audit(current_user.id, "logout")
    logout_user()
    flash("You have been signed out.", "success")
    return redirect(url_for("auth.login"))
