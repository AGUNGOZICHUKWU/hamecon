"""Admin routes for managing recipients and capturing consent."""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.admin.routes import admin_bp, role_required
from app.models.recipient import Recipient, ConsentRecord
from app.auth.routes import _audit


@admin_bp.route("/recipients")
@login_required
def recipients_list():
    items = Recipient.all()
    return render_template("admin/recipients/list.html", items=items)


@admin_bp.route("/recipients/new", methods=["GET", "POST"])
@role_required("admin")
def recipients_new():
    if request.method == "POST":
        f = request.form
        if not f.get("consent_given"):
            flash("Consent checkbox is mandatory.", "error")
            return render_template("admin/recipients/new.html", data=f)

        r = Recipient.create(
            full_name=f["full_name"].strip(),
            email=f["email"].strip().lower(),
            language=f["language"],
            organisation=f.get("organisation", "").strip(),
            notes=f.get("notes", "").strip(),
        )
        ConsentRecord.grant(
            recipient_id=r.id,
            granted_by_user=current_user.id,
            scope=f.get("scope", "general_phishing_training"),
            evidence_note=f.get("evidence_note", "consent confirmed on signup"),
        )
        _audit(current_user.id, "recipient_created",
               f"recipient_id={r.id} email={r.email}")
        flash(f"Recipient {r.full_name} added with active consent.", "success")
        return redirect(url_for("admin.recipients_list"))

    return render_template("admin/recipients/new.html", data={})
