"""
Bobasi BBS - Finance Routes (Disbursements only — no repayments)
"""
import uuid
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.models import db, Application, Disbursement, Loan, Notification, Student

finance_bp = Blueprint("finance", __name__)


def finance_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ("admin", "finance_officer"):
            flash("Finance officer access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@finance_bp.route("/dashboard")
@login_required
@finance_required
def dashboard():
    stats = {
        "approved_pending_disburse": Application.query.filter_by(status="approved").count(),
        "total_disbursed": db.session.query(db.func.sum(Disbursement.amount)).scalar() or 0,
        "total_beneficiaries": db.session.query(Disbursement.student_id).distinct().count(),
        "disbursed_apps": Application.query.filter_by(status="disbursed").count(),
        "total_applied": db.session.query(db.func.sum(Application.requested_amount)).filter(
            Application.status.in_(["approved", "disbursed"])
        ).scalar() or 0,
    }
    recent_disb = Disbursement.query.order_by(Disbursement.created_at.desc()).limit(10).all()
    # Monthly disbursement data for chart
    monthly = []
    for month in range(1, 13):
        total = db.session.query(db.func.sum(Disbursement.amount)).filter(
            db.func.strftime('%m', Disbursement.disbursement_date) == f"{month:02d}"
        ).scalar() or 0
        monthly.append(round(total))

    return render_template("finance/dashboard.html",
        stats=stats,
        recent_disb=recent_disb,
        monthly=monthly,
    )


@finance_bp.route("/disburse", methods=["GET", "POST"])
@login_required
@finance_required
def disburse():
    if request.method == "POST":
        app_id = request.form.get("application_id")
        amount = request.form.get("amount")
        method = request.form.get("payment_method")
        bank_name = request.form.get("bank_name", "")
        account_number = request.form.get("account_number", "")
        notes = request.form.get("notes", "")

        app_obj = Application.query.get(app_id)
        if not app_obj:
            flash("Application not found.", "danger")
            return redirect(request.url)
        if app_obj.status != "approved":
            flash("Application must be in 'Approved' status before disbursement.", "warning")
            return redirect(request.url)

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            flash("Please enter a valid amount greater than zero.", "danger")
            return redirect(request.url)

        ref = f"BOB-DISB-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        disb = Disbursement(
            application_id=app_obj.id,
            student_id=app_obj.student_id,
            finance_officer_id=current_user.id,
            amount=amount,
            payment_method=method,
            bank_name=bank_name,
            account_number=account_number,
            reference_number=ref,
            notes=notes,
            status="processed",
        )
        db.session.add(disb)

        # Grant record (no repayment required)
        loan = Loan(
            application_id=app_obj.id,
            student_id=app_obj.student_id,
            principal_amount=amount,
            interest_rate=0.0,
            repayment_period_months=0,
            monthly_installment=0,
            total_payable=amount,
            balance_remaining=0,
            start_date=datetime.now().strftime("%Y-%m-%d"),
            due_date=datetime.now().strftime("%Y-%m-%d"),
            status="active",
        )
        db.session.add(loan)

        app_obj.status = "disbursed"
        app_obj.disbursed_at = datetime.utcnow()

        notif = Notification(
            user_id=app_obj.student.user_id,
            title="🎉 Bursary Funds Disbursed",
            message=f"Congratulations! KShs {amount:,.0f} has been disbursed for your bursary application {app_obj.application_number}. Reference: {ref}. Method: {method.replace('_', ' ').title()}.",
            type="disbursement",
        )
        db.session.add(notif)
        db.session.commit()

        flash(f"✅ Disbursement of KShs {amount:,.0f} processed successfully. Reference: {ref}", "success")
        return redirect(url_for("finance.disbursements"))

    approved_apps = Application.query.filter_by(status="approved").order_by(Application.submitted_at.desc()).all()
    return render_template("finance/disburse.html", approved_apps=approved_apps)


@finance_bp.route("/disbursements")
@login_required
@finance_required
def disbursements():
    method_filter = request.args.get("method", "")
    search = request.args.get("search", "").strip()
    query = Disbursement.query
    if method_filter:
        query = query.filter_by(payment_method=method_filter)
    if search:
        query = query.join(Student).filter(
            db.or_(
                Student.full_name.ilike(f"%{search}%"),
                Disbursement.reference_number.ilike(f"%{search}%"),
            )
        )
    disbs = query.order_by(Disbursement.created_at.desc()).all()
    total = sum(d.amount for d in disbs)
    return render_template("finance/disbursements.html",
        disbursements=disbs,
        total=total,
        method_filter=method_filter,
        search=search,
    )


@finance_bp.route("/grants")
@login_required
@finance_required
def grants():
    """View all disbursed grants (loan records = bursary grant records)"""
    status_filter = request.args.get("status", "")
    query = Loan.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    grants_list = query.order_by(Loan.created_at.desc()).all()
    return render_template("finance/grants.html", grants=grants_list, status_filter=status_filter)
