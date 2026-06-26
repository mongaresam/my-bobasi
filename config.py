"""
Bobasi NG-CDF Bursary System - Configuration
"""
import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "bobasi-ngcdf-bursary-secret-2025-kisii")
    DEBUG = False
    TESTING = False

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'database', 'bobasi_bursary.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # File uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx"}

    # Email
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "noreply@bobasi.go.ke")

    # Bursary settings
    BURSARY_NAME = "Bobasi NG-CDF Bursary Fund"
    CONSTITUENCY = "Bobasi Constituency"
    COUNTY = "Kisii County"
    BURSARY_MAX_AMOUNT = 50000
    APPLICATION_PREFIX = "BOB"
    FINANCIAL_YEAR = "2025/2026"
    OFFICES = ["Nyamache", "Itumbe", "Nyacheki"]
    POSTAL_ADDRESS = "P.O BOX 98-40203, Nyamache"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # Use MySQL in production:
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:pass@host/bursary_db"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
