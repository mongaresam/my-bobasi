"""
Bobasi BBS - Application Routes
"""
import os, json, uuid
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models.models import db, Student, Application, Document, Notification, User

application_bp = Blueprint("application", __name__)


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "student":
            flash("Student access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def _gen_app_number(student_id):
    from config import config
    import os
    cfg = config.get(os.environ.get("FLASK_ENV", "development"), config["default"])
    year = datetime.now().year
    count = Application.query.count() + 1
    return f"BOB{year}{count:05d}"


def _allowed_file(filename):
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"pdf", "png", "jpg", "jpeg"})
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


@application_bp.route("/apply", methods=["GET", "POST"])
@login_required
@student_required
def apply():
    student = current_user.student_profile
    if not student:
        flash("Student profile not found.", "danger")
        return redirect(url_for("auth.logout"))

    if request.method == "POST":
        f = request.form
        siblings_list = []
        i = 0
        while f"sibling_name_{i}" in f:
            if f.get(f"sibling_name_{i}"):
                siblings_list.append({
                    "name": f.get(f"sibling_name_{i}", ""),
                    "institution": f.get(f"sibling_institution_{i}", ""),
                    "year": f.get(f"sibling_year_{i}", ""),
                    "total_fee": f.get(f"sibling_total_fee_{i}", ""),
                    "fees_paid": f.get(f"sibling_fees_paid_{i}", ""),
                    "outstanding": f.get(f"sibling_outstanding_{i}", ""),
                })
            i += 1

        try:
            amount = float(f.get("requested_amount") or 0)
            if amount <= 0:
                flash("Please enter a valid amount.", "danger")
                return render_template("application/apply.html", student=student)
        except ValueError:
            flash("Invalid amount.", "danger")
            return render_template("application/apply.html", student=student)

        # Update student profile fields from form
        student.institution = f.get("institution", student.institution or "")
        student.course = f.get("course", student.course or "")
        student.level_of_study = f.get("level_of_study", student.level_of_study or "")

        app_obj = Application(
            student_id=student.id,
            application_number=_gen_app_number(student.id),
            academic_year=f.get("academic_year", "2025/2026"),
            semester=f.get("semester", "1"),
            institution=f.get("institution", ""),
            course=f.get("course", ""),
            level_of_study=f.get("level_of_study", ""),
            requested_amount=amount,
            purpose=f.get("purpose", ""),
            siblings_json=json.dumps(siblings_list),
            status="pending",
        )
        db.session.add(app_obj)
        db.session.commit()

        # Notify admins
        admins = User.query.filter(User.role.in_(["admin", "review_committee"])).all()
        for admin in admins:
            notif = Notification(
                user_id=admin.id,
                title="New Bursary Application",
                message=f"New application {app_obj.application_number} from {student.full_name} — KShs. {amount:,.0f}",
                type="application",
            )
            db.session.add(notif)
        db.session.commit()

        flash(f"Application submitted! Reference: {app_obj.application_number}", "success")
        return redirect(url_for("application.view", app_id=app_obj.id))

    return render_template("application/apply.html", student=student)


@application_bp.route("/<int:app_id>")
@login_required
def view(app_id):
    app_obj = Application.query.get_or_404(app_id)
    # Only student owner or admin/committee/finance can view
    if current_user.role == "student":
        student = current_user.student_profile
        if not student or app_obj.student_id != student.id:
            flash("Access denied.", "danger")
            return redirect(url_for("student.dashboard"))
    return render_template("application/view.html", application=app_obj)


@application_bp.route("/track", methods=["GET"])
def track():
    ref = request.args.get("ref", "").strip().upper()
    application = None
    if ref:
        application = Application.query.filter_by(application_number=ref).first()
    return render_template("application/track.html", application=application, ref=ref)


@application_bp.route("/<int:app_id>/upload-documents", methods=["GET", "POST"])
@login_required
@student_required
def upload_documents(app_id):
    app_obj = Application.query.get_or_404(app_id)
    student = current_user.student_profile
    if not student or app_obj.student_id != student.id:
        flash("Access denied.", "danger")
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        doc_type = request.form.get("document_type", "other")
        file = request.files.get("document")
        if not file or file.filename == "":
            flash("No file selected.", "danger")
            return redirect(request.url)
        if not _allowed_file(file.filename):
            flash("File type not allowed. Upload PDF, PNG, JPG, DOC.", "danger")
            return redirect(request.url)

        filename = secure_filename(f"{student.id}_{app_id}_{uuid.uuid4().hex[:8]}_{file.filename}")
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)
        save_path = os.path.join(upload_dir, filename)
        file.save(save_path)

        doc = Document(
            student_id=student.id,
            application_id=app_id,
            document_type=doc_type,
            document_name=file.filename,
            file_path=f"uploads/{filename}",
            file_size=os.path.getsize(save_path),
            mime_type=file.content_type,
        )
        db.session.add(doc)
        db.session.commit()
        flash("Document uploaded successfully.", "success")
        return redirect(url_for("application.view", app_id=app_id))

    existing_docs = app_obj.documents.all()
    return render_template("application/upload_docs.html", application=app_obj, documents=existing_docs)
