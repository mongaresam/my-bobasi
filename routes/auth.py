"""
Bobasi BBS - Authentication Routes
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from models.models import db, User, Student

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
@auth_bp.route("/home")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return render_template("auth/home.html")


def dashboard_redirect():
    pass


@auth_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin():
        return redirect(url_for("admin.dashboard"))
    elif current_user.is_finance():
        return redirect(url_for("finance.dashboard"))
    elif current_user.is_committee():
        return redirect(url_for("admin.applications"))
    else:
        return redirect(url_for("student.dashboard"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not all([name, email, password, confirm]):
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("auth/register.html")
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("auth/register.html")

        user = User(name=name, email=email, role="student", status="active", email_verified=True)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        student = Student(user_id=user.id, full_name=name)
        db.session.add(student)
        db.session.commit()

        login_user(user)
        flash(f"Welcome, {name}! Please complete your profile.", "success")
        return redirect(url_for("student.profile"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")
        if user.status == "suspended":
            flash("Your account has been suspended. Contact the administrator.", "danger")
            return render_template("auth/login.html")
        if user.status == "inactive":
            flash("Your account is inactive. Contact the administrator.", "warning")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()

        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)
        return redirect(url_for("auth.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_pw = request.form.get("current_password", "")
        new_pw = request.form.get("new_password", "")
        confirm_pw = request.form.get("confirm_password", "")

        if not current_user.check_password(current_pw):
            flash("Current password is incorrect.", "danger")
            return render_template("auth/change_password.html")
        if new_pw != confirm_pw:
            flash("New passwords do not match.", "danger")
            return render_template("auth/change_password.html")
        if len(new_pw) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("auth/change_password.html")

        current_user.set_password(new_pw)
        db.session.commit()
        flash("Password changed successfully.", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("auth/change_password.html")
