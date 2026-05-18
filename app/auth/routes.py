
from flask import Blueprint, render_template, request, redirect, url_for, flash

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        flash("Real authentication arrives in Day 6.", "info")
        return redirect(url_for("admin.dashboard"))
    return render_template("auth/login.html")
