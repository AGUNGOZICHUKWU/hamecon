"""Campaign routes: list, create (AI), review, approve, send, view messages."""

import os
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.admin.routes import admin_bp, role_required
from app.models.campaign import Campaign
from app.models.user import _conn
from app.auth.routes import _audit
from app.ai.generator import generate_phish_email, generate_phish_sms


_DEFAULT_FROM_NAMES = {
    "mobile_money": "MTN Mobile Money",
    "banking":      "Afriland First Bank",
    "university":   "Service Scolarité",
}


@admin_bp.route("/campaigns")
@login_required
def campaigns_list():
    return render_template("admin/campaigns/list.html", items=Campaign.all())


@admin_bp.route("/campaigns/new", methods=["GET", "POST"])
@role_required("admin")
def campaigns_new():
    if request.method == "POST":
        f = request.form
        channel, language, difficulty = f["channel"], f["language"], f["difficulty"]
        brief = f["brief"].strip()
        try:
            if channel == "sms":
                body, subject = generate_phish_sms(brief, language, difficulty), None
            else:
                result = generate_phish_email(brief, language, difficulty)
                subject, body = result["subject"], result["body_html"]
        except Exception as e:
            flash(f"AI generation failed: {e}", "error")
            return render_template("admin/campaigns/new.html", data=f)

        from_name = f.get("from_name", "").strip()
        if not from_name:
            from_name = _DEFAULT_FROM_NAMES.get(f["scenario"], "Hamecon Training")

        camp = Campaign.create(
            name=f["name"].strip(), brief=brief, channel=channel,
            language=language, difficulty=difficulty, scenario=f["scenario"],
            draft_subject=subject, draft_body=body, created_by=current_user.id,
            from_name=from_name,
        )
        _audit(current_user.id, "campaign_created", f"campaign_id={camp.id}")
        flash("Campaign drafted. Review the AI content below.", "success")
        return redirect(url_for("admin.campaigns_detail", campaign_id=camp.id))

    return render_template("admin/campaigns/new.html", data={})


@admin_bp.route("/campaigns/<int:campaign_id>")
@login_required
def campaigns_detail(campaign_id):
    camp = Campaign.get(campaign_id)
    if not camp:
        flash("Campaign not found.", "error")
        return redirect(url_for("admin.campaigns_list"))
    return render_template("admin/campaigns/detail.html", camp=camp)


@admin_bp.route("/campaigns/<int:campaign_id>/approve", methods=["POST"])
@role_required("admin")
def campaigns_approve(campaign_id):
    Campaign.approve(campaign_id, current_user.id)
    _audit(current_user.id, "campaign_approved", f"campaign_id={campaign_id}")
    flash("Campaign approved. You can now send it.", "success")
    return redirect(url_for("admin.campaigns_detail", campaign_id=campaign_id))


@admin_bp.route("/campaigns/<int:campaign_id>/send", methods=["POST"])
@role_required("admin")
def campaigns_send(campaign_id):
    from app.services.campaign_sender import send_campaign
    result = send_campaign(campaign_id)
    if "error" in result:
        flash(result["error"], "error")
        return redirect(url_for("admin.campaigns_detail", campaign_id=campaign_id))
    _audit(current_user.id, "campaign_sent",
           f"campaign_id={campaign_id} sent={result['sent']} "
           f"skipped_no_consent={result['skipped_no_consent']} failed={result['failed']}")
    flash(f"Campaign sent. Delivered: {result['sent']}. "
          f"Skipped (no consent): {result['skipped_no_consent']}. "
          f"Failed: {result['failed']}.", "success")
    return redirect(url_for("admin.campaigns_messages", campaign_id=campaign_id))


@admin_bp.route("/campaigns/<int:campaign_id>/messages")
@login_required
def campaigns_messages(campaign_id):
    base = os.environ.get("TRACKING_BASE_URL", "http://172.20.10.8:5000")
    c = _conn()
    rows = c.execute(
        """SELECT sm.tracking_token, sm.subject, sm.body, r.full_name, r.email
             FROM sent_messages sm
             JOIN recipients r ON r.id = sm.recipient_id
            WHERE sm.campaign_id = ?
            ORDER BY sm.id""",
        (campaign_id,),
    ).fetchall()
    c.close()
    messages = []
    for row in rows:
        url = f"{base}/t/{row['tracking_token']}"
        body = (row["body"] or "").replace("{{TRACKING_LINK}}", url)
        messages.append({
            "recipient": row["full_name"], "email": row["email"],
            "subject": row["subject"], "body": body, "tracking_url": url,
        })
    return render_template("admin/campaigns/messages.html",
                           camp=Campaign.get(campaign_id), messages=messages)
