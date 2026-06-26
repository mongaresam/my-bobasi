"""
Bobasi BBS - Student Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models.models import db, Student, Application, Loan, Notification

student_bp = Blueprint("student", __name__)


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "student":
            flash("Student access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@student_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    student = current_user.student_profile
    if not student:
        flash("Profile not found.", "danger")
        return redirect(url_for("auth.logout"))

    apps = student.applications.order_by(Application.submitted_at.desc()).limit(5).all()
    disbursements_list = student.loans.all()  # loan records = grant records
    total_received = sum(l.principal_amount for l in disbursements_list)
    notifications = current_user.notifications.filter_by(is_read=False).limit(5).all()

    # Application status counts
    status_counts = {
        "pending": student.applications.filter_by(status="pending").count(),
        "under_review": student.applications.filter_by(status="under_review").count(),
        "approved": student.applications.filter_by(status="approved").count(),
        "disbursed": student.applications.filter_by(status="disbursed").count(),
        "rejected": student.applications.filter_by(status="rejected").count(),
    }

    return render_template("student/dashboard.html",
        student=student,
        apps=apps,
        disbursements=disbursements_list,
        total_received=total_received,
        notifications=notifications,
        status_counts=status_counts,
    )


@student_bp.route("/profile", methods=["GET", "POST"])
@login_required
@student_required
def profile():
    student = current_user.student_profile
    if not student:
        flash("Profile error.", "danger")
        return redirect(url_for("auth.logout"))

    if request.method == "POST":
        f = request.form
        student.full_name = f.get("full_name", student.full_name)
        student.admission_number = f.get("admission_number", "")
        student.institution = f.get("institution", "")
        student.campus = f.get("campus", "")
        student.course = f.get("course", "")
        student.year_of_study = int(f.get("year_of_study") or 1)
        student.level_of_study = f.get("level_of_study", "")
        student.date_of_birth = f.get("date_of_birth", "")
        student.id_number = f.get("id_number", "")
        student.phone = f.get("phone", "")
        student.parent_phone = f.get("parent_phone", "")
        student.gender = f.get("gender", "")

        # Location
        student.sub_county = f.get("sub_county", "")
        student.division = f.get("division", "")
        student.location = f.get("location", "")
        student.sub_location = f.get("sub_location", "")
        student.ward = f.get("ward", "")
        student.polling_station = f.get("polling_station", "")
        student.registered_voter = f.get("registered_voter", "")
        student.postal_address = f.get("postal_address", "")

        # Family
        student.family_status = f.get("family_status", "")
        student.father_name = f.get("father_name", "")
        student.mother_name = f.get("mother_name", "")
        student.siblings_count = int(f.get("siblings_count") or 0)
        student.siblings_working = int(f.get("siblings_working") or 0)
        student.siblings_secondary = int(f.get("siblings_secondary") or 0)
        student.siblings_post_secondary = int(f.get("siblings_post_secondary") or 0)
        student.orphan_sponsor = f.get("orphan_sponsor", "")
        student.another_sponsor = f.get("another_sponsor", "")
        student.prev_bursary = f.get("prev_bursary", "")
        student.prev_bursary_years = f.get("prev_bursary_years", "")
        student.prev_bursary_amount = f.get("prev_bursary_amount", "")

        # Financial
        student.father_income = float(f.get("father_income") or 0)
        student.mother_income = float(f.get("mother_income") or 0)
        student.self_income = float(f.get("self_income") or 0)
        student.father_occupation = f.get("father_occupation", "")
        student.mother_occupation = f.get("mother_occupation", "")
        student.household_income = student.total_family_income

        # Bank & verification
        student.bank_ac_no = f.get("bank_ac_no", "")
        student.account_name = f.get("account_name", "")
        student.bank_branch = f.get("bank_branch", "")
        student.school_email = f.get("school_email", "")
        student.finance_person = f.get("finance_person", "")
        student.finance_contact = f.get("finance_contact", "")
        student.principal_name = f.get("principal_name", "")
        student.principal_contact = f.get("principal_contact", "")
        student.religious_leader = f.get("religious_leader", "")
        student.chief_name = f.get("chief_name", "")
        student.profile_complete = True
        current_user.name = student.full_name

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("student.dashboard"))

    return render_template("student/profile.html", student=student)


@student_bp.route("/notifications")
@login_required
@student_required
def notifications():
    notifs = current_user.notifications.order_by(Notification.created_at.desc()).all()
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template("student/notifications.html", notifications=notifs)


@student_bp.route("/disbursements")
@login_required
@student_required
def my_disbursements():
    student = current_user.student_profile
    grants = student.loans.order_by(Loan.created_at.desc()).all()
    return render_template("student/my_disbursements.html", grants=grants, student=student)


@student_bp.route("/applications")
@login_required
@student_required
def my_applications():
    student = current_user.student_profile
    apps = student.applications.order_by(Application.submitted_at.desc()).all()
    return render_template("student/my_applications.html", applications=apps, student=student)
