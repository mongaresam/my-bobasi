"""
Bobasi BBS - Admin Routes
"""
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models.models import db, User, Student, Application, Review, Disbursement, Loan, Notification

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ("admin", "review_committee"):
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def super_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Super admin access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    stats = {
        "total_students": Student.query.count(),
        "total_apps": Application.query.count(),
        "pending": Application.query.filter_by(status="pending").count(),
        "under_review": Application.query.filter_by(status="under_review").count(),
        "approved": Application.query.filter_by(status="approved").count(),
        "rejected": Application.query.filter_by(status="rejected").count(),
        "disbursed": Application.query.filter_by(status="disbursed").count(),
        "total_disbursed": db.session.query(db.func.sum(Disbursement.amount)).scalar() or 0,
        "total_loans": Loan.query.count(),
        "active_loans": Loan.query.filter_by(status="active").count(),
        "total_disbursed_count": Disbursement.query.count(),
    }
    recent_apps = Application.query.order_by(Application.submitted_at.desc()).limit(8).all()
    notifications = current_user.notifications.filter_by(is_read=False).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent_apps=recent_apps, notifications=notifications)


@admin_bp.route("/applications")
@login_required
@admin_required
def applications():
    status = request.args.get("status", "")
    search = request.args.get("search", "").lower()
    query = Application.query
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.join(Student).filter(
            db.or_(
                Application.application_number.ilike(f"%{search}%"),
                Student.full_name.ilike(f"%{search}%"),
                Student.institution.ilike(f"%{search}%"),
            )
        )
    apps = query.order_by(Application.submitted_at.desc()).all()
    return render_template("admin/applications.html", applications=apps, status=status, search=search)


@admin_bp.route("/application/<int:app_id>")
@login_required
@admin_required
def view_application(app_id):
    app_obj = Application.query.get_or_404(app_id)
    reviews = app_obj.reviews.all()
    return render_template("admin/view_application.html", application=app_obj, reviews=reviews)


@admin_bp.route("/application/<int:app_id>/update-status", methods=["POST"])
@login_required
@admin_required
def update_status(app_id):
    app_obj = Application.query.get_or_404(app_id)
    new_status = request.form.get("status")
    amount = request.form.get("approved_amount", "")
    reason = request.form.get("rejection_reason", "")
    comments = request.form.get("committee_comments", "")

    if new_status not in ("pending", "under_review", "approved", "rejected", "disbursed", "completed"):
        flash("Invalid status.", "danger")
        return redirect(url_for("admin.view_application", app_id=app_id))

    app_obj.status = new_status
    app_obj.committee_comments = comments
    app_obj.reviewed_by = current_user.name
    app_obj.reviewed_at = datetime.utcnow()

    if new_status == "approved":
        try:
            app_obj.approved_amount = float(amount)
        except (ValueError, TypeError):
            app_obj.approved_amount = app_obj.requested_amount
        app_obj.approved_at = datetime.utcnow()
    elif new_status == "rejected":
        app_obj.rejection_reason = reason

    db.session.commit()

    # Notify student
    student_user = app_obj.student.user
    msg_map = {
        "approved": f"Congratulations! Your application {app_obj.application_number} has been APPROVED for KShs. {app_obj.approved_amount:,.0f}.",
        "rejected": f"Your application {app_obj.application_number} was not approved. Reason: {reason}",
        "under_review": f"Your application {app_obj.application_number} is now under review by the committee.",
        "disbursed": f"Funds for application {app_obj.application_number} have been disbursed. Check your account.",
    }
    if new_status in msg_map:
        notif = Notification(
            user_id=student_user.id,
            title=f"Application {new_status.replace('_', ' ').title()}",
            message=msg_map[new_status],
            type="application",
        )
        db.session.add(notif)
        db.session.commit()

    flash(f"Application status updated to '{new_status}'.", "success")
    return redirect(url_for("admin.view_application", app_id=app_id))


@admin_bp.route("/application/<int:app_id>/review", methods=["POST"])
@login_required
@admin_required
def add_review(app_id):
    app_obj = Application.query.get_or_404(app_id)
    decision = request.form.get("decision")
    rec_amount = request.form.get("recommended_amount", "")
    comments = request.form.get("comments", "")

    if decision not in ("recommend_approval", "recommend_rejection", "need_more_info"):
        flash("Invalid decision.", "danger")
        return redirect(url_for("admin.view_application", app_id=app_id))

    review = Review(
        application_id=app_id,
        reviewer_id=current_user.id,
        decision=decision,
        recommended_amount=float(rec_amount) if rec_amount else None,
        comments=comments,
    )
    db.session.add(review)
    if app_obj.status == "pending":
        app_obj.status = "under_review"
    db.session.commit()
    flash("Review submitted.", "success")
    return redirect(url_for("admin.view_application", app_id=app_id))


@admin_bp.route("/students")
@login_required
@admin_required
def students():
    search = request.args.get("search", "").lower()
    query = Student.query
    if search:
        query = query.filter(
            db.or_(
                Student.full_name.ilike(f"%{search}%"),
                Student.admission_number.ilike(f"%{search}%"),
                Student.institution.ilike(f"%{search}%"),
            )
        )
    students_list = query.order_by(Student.created_at.desc()).all()
    return render_template("admin/students.html", students=students_list, search=search)


@admin_bp.route("/students/<int:student_id>")
@login_required
@admin_required
def view_student(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template("admin/view_student.html", student=student)


@admin_bp.route("/users")
@login_required
@super_admin_required
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users_list)


@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@login_required
@super_admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Cannot change your own status.", "warning")
        return redirect(url_for("admin.users"))
    user.status = "suspended" if user.status == "active" else "active"
    db.session.commit()
    flash(f"User {user.name} is now {user.status}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/add", methods=["POST"])
@login_required
@super_admin_required
def add_user():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "review_committee")

    if User.query.filter_by(email=email).first():
        flash("Email already exists.", "danger")
        return redirect(url_for("admin.users"))

    from models.models import User
    user = User(name=name, email=email, role=role, status="active", email_verified=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash(f"User {name} created.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/reports")
@login_required
@admin_required
def reports():
    # By sub-county
    sc_data = db.session.query(
        Student.sub_county,
        db.func.count(Application.id),
        db.func.sum(Application.approved_amount)
    ).join(Application, Application.student_id == Student.id, isouter=True
    ).group_by(Student.sub_county).all()

    # By status
    status_data = db.session.query(
        Application.status,
        db.func.count(Application.id)
    ).group_by(Application.status).all()

    # By institution
    inst_data = db.session.query(
        Application.institution,
        db.func.count(Application.id),
        db.func.sum(Application.approved_amount)
    ).group_by(Application.institution).order_by(db.func.count(Application.id).desc()).limit(10).all()

    total_disbursed = db.session.query(db.func.sum(Disbursement.amount)).scalar() or 0

    return render_template("admin/reports.html",
        sc_data=sc_data,
        status_data=status_data,
        inst_data=inst_data,
        total_disbursed=total_disbursed,
    )


@admin_bp.route("/notifications/mark-read", methods=["POST"])
@login_required
def mark_notifications_read():
    for n in current_user.notifications.filter_by(is_read=False).all():
        n.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for("admin.dashboard"))
