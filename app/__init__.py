from __future__ import annotations

import os

from flask import Flask

from .auth import auth_bp
from .config import Config
from .dashboard import dashboard_bp
from .extensions import db, login_manager, mail
from .models import User
from .views import main_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    with app.app_context():
        _prepare_database()
        app.register_blueprint(auth_bp, url_prefix="/auth")
        app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
        app.register_blueprint(main_bp)

    return app


def _prepare_database() -> None:
    db.create_all()

    if not User.query.filter_by(role="admin").first():
        admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
        admin_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "ChangeMe123!")

        admin = User(
            username=admin_username,
            email=admin_email.lower(),
            role="admin",
            email_confirmed=True,
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
