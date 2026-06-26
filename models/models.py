"""
Bobasi NG-CDF Bursary System - Database Models
"""

from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ─────────────────────────────────────────────
# USER MODEL
# ─────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum("student", "admin", "finance_officer", "review_committee"),
        default="student", nullable=False
    )
    status = db.Column(
        db.Enum("active", "inactive", "suspended"),
        default="active", nullable=False
    )
    email_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student_profile = db.relationship("Student", backref="user", uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship("Notification", backref="user", lazy="dynamic", cascade="all, delete-orphan")
    reviews_given = db.relationship("Review", backref="reviewer", foreign_keys="Review.reviewer_id")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "admin"

    def is_finance(self):
        return self.role == "finance_officer"

    def is_committee(self):
        return self.role == "review_committee"

    def is_student(self):
        return self.role == "student"

    @property
    def unread_notifications(self):
        return self.notifications.filter_by(is_read=False).count()

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"


# ─────────────────────────────────────────────
# STUDENT MODEL
# ─────────────────────────────────────────────
class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    admission_number = db.Column(db.String(50), unique=True)
    institution = db.Column(db.String(200))
    campus = db.Column(db.String(200))
    course = db.Column(db.String(200))
    year_of_study = db.Column(db.Integer)
    level_of_study = db.Column(db.String(50))  # Certificate, Diploma, Degree, Masters, PhD
    date_of_birth = db.Column(db.String(20))
    id_number = db.Column(db.String(20), unique=True)
    phone = db.Column(db.String(20))
    parent_phone = db.Column(db.String(20))
    gender = db.Column(db.Enum("male", "female", "other"))

    # Location
    sub_county = db.Column(db.String(100))
    division = db.Column(db.String(100))
    location = db.Column(db.String(100))
    sub_location = db.Column(db.String(100))
    ward = db.Column(db.String(100))
    polling_station = db.Column(db.String(100))
    registered_voter = db.Column(db.String(5))
    postal_address = db.Column(db.String(200))

    # Family
    family_status = db.Column(
        db.Enum("total_orphan", "partial_orphan", "both_parents_alive"),
        default="both_parents_alive"
    )
    father_name = db.Column(db.String(150))
    mother_name = db.Column(db.String(150))
    guardian_name = db.Column(db.String(150))
    guardian_phone = db.Column(db.String(20))
    siblings_count = db.Column(db.Integer, default=0)
    siblings_working = db.Column(db.Integer, default=0)
    siblings_secondary = db.Column(db.Integer, default=0)
    siblings_post_secondary = db.Column(db.Integer, default=0)
    orphan_sponsor = db.Column(db.String(200))
    another_sponsor = db.Column(db.String(5))
    sponsor_details = db.Column(db.String(200))

    # Financial
    father_income = db.Column(db.Float, default=0)
    mother_income = db.Column(db.Float, default=0)
    self_income = db.Column(db.Float, default=0)
    father_occupation = db.Column(db.String(150))
    mother_occupation = db.Column(db.String(150))
    household_income = db.Column(db.Float, default=0)

    # Previous bursary
    prev_bursary = db.Column(db.String(5))
    prev_bursary_years = db.Column(db.String(100))
    prev_bursary_amount = db.Column(db.String(50))

    # Bank details
    bank_ac_no = db.Column(db.String(50))
    account_name = db.Column(db.String(150))
    bank_branch = db.Column(db.String(100))
    school_email = db.Column(db.String(150))

    # Verifiers
    finance_person = db.Column(db.String(150))
    finance_contact = db.Column(db.String(20))
    principal_name = db.Column(db.String(150))
    principal_contact = db.Column(db.String(20))
    religious_leader = db.Column(db.String(150))
    chief_name = db.Column(db.String(150))

    profile_complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = db.relationship("Application", backref="student", lazy="dynamic", cascade="all, delete-orphan")
    documents = db.relationship("Document", backref="student", lazy="dynamic", cascade="all, delete-orphan")
    loans = db.relationship("Loan", backref="student", lazy="dynamic")
    disbursements = db.relationship("Disbursement", backref="student", lazy="dynamic")

    @property
    def total_family_income(self):
        return (self.father_income or 0) + (self.mother_income or 0) + (self.self_income or 0)

    def __repr__(self):
        return f"<Student {self.full_name}>"


# ─────────────────────────────────────────────
# APPLICATION MODEL
# ─────────────────────────────────────────────
class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    application_number = db.Column(db.String(30), unique=True, nullable=False)
    academic_year = db.Column(db.String(10), nullable=False, default="2025/2026")
    semester = db.Column(db.Enum("1", "2", "3"), default="1")
    institution = db.Column(db.String(200))
    course = db.Column(db.String(200))
    level_of_study = db.Column(db.String(100))
    requested_amount = db.Column(db.Float, nullable=False)
    approved_amount = db.Column(db.Float, nullable=True)
    purpose = db.Column(db.Text)

    # Siblings in school (JSON)
    siblings_json = db.Column(db.Text)

    status = db.Column(
        db.Enum("pending", "under_review", "approved", "rejected", "disbursed", "completed"),
        default="pending", nullable=False
    )
    rejection_reason = db.Column(db.Text, nullable=True)
    committee_comments = db.Column(db.Text, nullable=True)

    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    disbursed_at = db.Column(db.DateTime, nullable=True)

    reviewed_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = db.relationship("Document", backref="application", lazy="dynamic", cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="application", lazy="dynamic", cascade="all, delete-orphan")
    disbursements = db.relationship("Disbursement", backref="application", lazy="dynamic")
    loan = db.relationship("Loan", backref="application", uselist=False)

    def get_siblings(self):
        import json
        if self.siblings_json:
            try:
                return json.loads(self.siblings_json)
            except Exception:
                return []
        return []

    def __repr__(self):
        return f"<Application {self.application_number} [{self.status}]>"


# ─────────────────────────────────────────────
# DOCUMENT MODEL
# ─────────────────────────────────────────────
class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    document_name = db.Column(db.String(255))
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    status = db.Column(db.Enum("pending", "verified", "rejected"), default="pending")
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Document {self.document_name}>"


# ─────────────────────────────────────────────
# REVIEW MODEL
# ─────────────────────────────────────────────
class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    decision = db.Column(
        db.Enum("recommend_approval", "recommend_rejection", "need_more_info"),
        nullable=False
    )
    recommended_amount = db.Column(db.Float, nullable=True)
    comments = db.Column(db.Text)
    review_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Review {self.decision} on App#{self.application_id}>"


# ─────────────────────────────────────────────
# DISBURSEMENT MODEL
# ─────────────────────────────────────────────
class Disbursement(db.Model):
    __tablename__ = "disbursements"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    finance_officer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    disbursement_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(
        db.Enum("bank_transfer", "mpesa", "cheque", "cash"),
        nullable=False
    )
    bank_name = db.Column(db.String(100))
    account_number = db.Column(db.String(50))
    reference_number = db.Column(db.String(100), unique=True)
    status = db.Column(db.Enum("pending", "processed", "failed"), default="processed")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    finance_officer = db.relationship("User", foreign_keys=[finance_officer_id])

    def __repr__(self):
        return f"<Disbursement KShs.{self.amount} → App#{self.application_id}>"


# ─────────────────────────────────────────────
# LOAN MODEL
# ─────────────────────────────────────────────
class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    principal_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, default=0.0)
    repayment_period_months = db.Column(db.Integer, default=24)
    monthly_installment = db.Column(db.Float)
    total_payable = db.Column(db.Float)
    balance_remaining = db.Column(db.Float)
    start_date = db.Column(db.String(20))
    due_date = db.Column(db.String(20))
    status = db.Column(db.Enum("active", "completed", "defaulted", "waived"), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    repayments = db.relationship("Repayment", backref="loan", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def total_paid(self):
        return sum(r.amount for r in self.repayments)

    def __repr__(self):
        return f"<Loan {self.id} KShs.{self.principal_amount}>"


# ─────────────────────────────────────────────
# REPAYMENT MODEL
# ─────────────────────────────────────────────
class Repayment(db.Model):
    __tablename__ = "repayments"

    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey("loans.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.Enum("bank_transfer", "mpesa", "cheque", "cash"), nullable=False)
    reference_number = db.Column(db.String(100))
    balance_remaining = db.Column(db.Float)
    recorded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    recorder = db.relationship("User", foreign_keys=[recorded_by])
    student = db.relationship("Student", foreign_keys=[student_id])

    def __repr__(self):
        return f"<Repayment KShs.{self.amount} on Loan#{self.loan_id}>"


# ─────────────────────────────────────────────
# NOTIFICATION MODEL
# ─────────────────────────────────────────────
class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(
        db.Enum("application", "disbursement", "repayment", "review", "system"),
        default="system"
    )
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notification '{self.title}' → User#{self.user_id}>"


# ─────────────────────────────────────────────
# SEED FUNCTION
# ─────────────────────────────────────────────
def seed_defaults():
    """Create default system users if they don't exist."""
    defaults = [
        {"name": "System Administrator", "email": "admin@bobasi.go.ke",
         "password": "Admin@1234", "role": "admin"},
        {"name": "Finance Officer", "email": "finance@bobasi.go.ke",
         "password": "Admin@1234", "role": "finance_officer"},
        {"name": "Review Committee", "email": "review@bobasi.go.ke",
         "password": "Admin@1234", "role": "review_committee"},
    ]
    for d in defaults:
        if not User.query.filter_by(email=d["email"]).first():
            u = User(name=d["name"], email=d["email"], role=d["role"],
                     status="active", email_verified=True)
            u.set_password(d["password"])
            db.session.add(u)
    db.session.commit()
