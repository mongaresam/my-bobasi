"""
Bobasi NG-CDF Bursary Borrowing System
Bobasi Constituency, Kisii County, Kenya
Run locally: python app.py
"""

import os
from flask import Flask, render_template
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
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "production")

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config["default"]))

    # Create folders only when running locally
    if not os.environ.get("RENDER"):
        os.makedirs(app.config.get("UPLOAD_FOLDER", "static/uploads"), exist_ok=True)
        os.makedirs("database", exist_ok=True)

    # Initialize extensions
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
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
            "User": User,
        }

    return app


# ===========================================================
# Flask application for Gunicorn / Render
# ===========================================================

env = os.environ.get("FLASK_ENV", "production")
app = create_app(env)


# ===========================================================
# Local Development
# ===========================================================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

        from models.models import seed_defaults

        seed_defaults()

        print("✅ Database initialized")

    print("=" * 60)
    print("Bobasi NG-CDF Bursary Borrowing System")
    print("Bobasi Constituency, Kisii County")
    print("=" * 60)
    print("Running on http://127.0.0.1:5000")
    print("Admin: admin@bobasi.go.ke")
    print("Password: Admin@1234")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=(env == "development"),
    )
