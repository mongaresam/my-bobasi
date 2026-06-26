"""
Bobasi NG-CDF Bursary Borrowing System
Bobasi Constituency, Kisii County, Kenya
Run: python app.py
"""

import os
from flask import Flask, render_template, jsonify
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
from models.models import db, User

login_manager = LoginManager()
migrate = Migrate()


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None


def create_app(config_name=None):
    if not config_name:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config["default"]))

    os.makedirs(app.config.get("UPLOAD_FOLDER", "static/uploads"), exist_ok=True)
    os.makedirs("database", exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    login_manager.login_message = "Please log in to access this page."

    # Register blueprints
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.admin import admin_bp
    from routes.finance import finance_bp
    from routes.application import application_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(finance_bp, url_prefix="/finance")
    app.register_blueprint(application_bp, url_prefix="/application")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.shell_context_processor
    def make_shell_context():
        return {"db": db, "User": User}

    return app


if __name__ == "__main__":
    env = os.environ.get("FLASK_ENV", "development")
    app = create_app(env)

    with app.app_context():
        db.create_all()
        # Seed default admin users
        from models.models import seed_defaults
        seed_defaults()
        print("✅ Database initialized")

    print("=" * 55)
    print("  BOBASI NG-CDF BURSARY BORROWING SYSTEM")
    print("  Bobasi Constituency, Kisii County, Kenya")
    print("=" * 55)
    print("  URL:   http://127.0.0.1:5000")
    print("  Admin: admin@bobasi.go.ke / Admin@1234")
    print("=" * 55)

    app.run(host="0.0.0.0", port=5000, debug=(env == "development"))
