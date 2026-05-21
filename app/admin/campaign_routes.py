"""Campaign routes: list, create (calls the AI), review, approve."""

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.admin.routes import admin_bp, role_required
from app.models.campaign import Campaign
from app.auth.routes import _audit
from app.ai.generator import generate_phish_email, generate_phish_sms


@admin_bp.route("/campaigns")
@login_required
def campaigns_list():
    return render_template("admin/campaigns/list.html", items=Campaign.all())


@admin_bp.route("/campaigns/new", methods=["GET", "POST"])
@role_required("admin")
def campaigns_new():
    if request.method == "POST":
        f = request.form
        channel    = f["channel"]
        language   = f["language"]
        difficulty = f["difficulty"]
        brief      = f["brief"].strip()

        # Call the AI generator. This is the moment Claude writes the phish.
        try:
            if channel == "sms":
                body = generate_phish_sms(brief, language, difficulty)
                subject = None
            else:
                result = generate_phish_email(brief, language, difficulty)
                subject = result["subject"]
                body = result["body_html"]
        except Exception as e:
            flash(f"AI generation failed: {e}", "error")
            return render_template("admin/campaigns/new.html", data=f)

        camp = Campaign.create(
            name=f["name"].strip(),
            brief=brief,
            channel=channel,
            language=language,
            difficulty=difficulty,
            scenario=f["scenario"],
            draft_subject=subject,
            draft_body=body,
            created_by=current_user.id,
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
    flash("Campaign approved. Sending will be enabled in Day 9.", "success")
    return redirect(url_for("admin.campaigns_detail", campaign_id=campaign_id))
