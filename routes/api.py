"""
Bobasi BBS - API Routes (JSON)
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.models import db, Application, Student, Disbursement, Loan, Repayment, Notification
from datetime import datetime

api_bp = Blueprint("api", __name__)


@api_bp.route("/stats")
@login_required
def stats():
    if current_user.role not in ("admin", "finance_officer", "review_committee"):
        return jsonify({"error": "Unauthorized"}), 403

    monthly = [0] * 12
    for app in Application.query.all():
        try:
            dt = datetime.fromisoformat(str(app.submitted_at))
            if dt.year == datetime.now().year:
                monthly[dt.month - 1] += 1
        except Exception:
            pass

    return jsonify({
        "total_apps": Application.query.count(),
        "pending": Application.query.filter_by(status="pending").count(),
        "approved": Application.query.filter_by(status="approved").count(),
        "rejected": Application.query.filter_by(status="rejected").count(),
        "disbursed": Application.query.filter_by(status="disbursed").count(),
        "total_disbursed": db.session.query(db.func.sum(Disbursement.amount)).scalar() or 0,
        "monthly_applications": monthly,
    })


@api_bp.route("/notifications/mark-read", methods=["POST"])
@login_required
def mark_notifications():
    for n in current_user.notifications.filter_by(is_read=False).all():
        n.is_read = True
    db.session.commit()
    return jsonify({"status": "ok"})


@api_bp.route("/application/<int:app_id>/status")
def app_status(app_id):
    app = Application.query.get_or_404(app_id)
    return jsonify({
        "id": app.id,
        "application_number": app.application_number,
        "status": app.status,
        "submitted_at": str(app.submitted_at),
        "approved_amount": app.approved_amount,
    })


@api_bp.route("/me")
@login_required
def me():
    return jsonify({
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "status": current_user.status,
    })
