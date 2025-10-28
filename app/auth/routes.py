from __future__ import annotations

from typing import Optional

from flask import (
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from ..extensions import db, login_manager
from ..models import User
from ..services.email import send_email
from ..services.tokens import generate_token, validate_token
from . import auth_bp


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


@login_manager.unauthorized_handler
def unauthorized_handler():
    flash("Please sign in to continue.", "warning")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already signed in.", "info")
        return redirect(url_for("dashboard.user_home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters long.")
        if not email:
            errors.append("Email is required.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if User.query.filter((User.email == email) | (User.username == username)).first():
            errors.append("An account with that email or username already exists.")

        if errors:
            for error in errors:
                flash(error, "error")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            _send_verification_email(user)
            flash("Account created. Check your email to activate your account.", "success")
            return redirect(url_for("auth.verify_notice", email=email))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.user_home"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter(
            (User.email == identifier.lower()) | (User.username == identifier)
        ).first()

        if not user or not user.check_password(password):
            flash("Invalid credentials. Please try again.", "error")
            return render_template("auth/login.html")

        if not user.email_confirmed:
            flash("Your email is not verified yet. Please check your inbox.", "warning")
            return redirect(url_for("auth.verify_notice", email=user.email))

        if not user.is_active:
            flash("This account has been deactivated.", "error")
            return render_template("auth/login.html")

        login_user(user)
        flash("Welcome back!", "success")
        next_url = request.args.get("next")
        return redirect(next_url or url_for("dashboard.user_home"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/verify")
def verify_notice():
    email = request.args.get("email")
    return render_template("auth/verify_notice.html", email=email)


@auth_bp.route("/verify/<token>")
def verify_email(token: str):
    data = validate_token(token, "email-verify", max_age=86400)
    if not data:
        flash("Verification link is invalid or expired.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(email=data.get("email")).first()
    if not user:
        flash("Account not found.", "error")
        return redirect(url_for("auth.register"))

    if not user.email_confirmed:
        user.email_confirmed = True
        db.session.commit()

    flash("Your account has been activated. You can sign in now.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification():
    email = request.form.get("email", "").strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No account found with that email.", "error")
        return redirect(url_for("auth.verify_notice", email=email))

    if user.email_confirmed:
        flash("Your email is already verified.", "info")
        return redirect(url_for("auth.login"))

    _send_verification_email(user)
    flash("A new verification link has been sent.", "success")
    return redirect(url_for("auth.verify_notice", email=email))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("If an account exists, a reset email has been sent.", "info")
            return redirect(url_for("auth.forgot_password"))

        _send_password_reset_email(user)
        flash("A reset link has been sent. Check your inbox (and spam folder).", "success")
        return redirect(url_for("auth.forgot_password"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token: str):
    data = validate_token(token, "password-reset", max_age=3600)
    if not data:
        flash("Reset link is invalid or expired.", "error")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=data.get("email")).first()
    if not user:
        flash("Account not found.", "error")
        return redirect(url_for("auth.register"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
        else:
            user.set_password(password)
            db.session.commit()
            flash("Your password has been updated. Please sign in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        if request.form.get("action") == "update_locale":
            locale = request.form.get("locale", current_user.locale)
            if locale not in {"en", "ar"}:
                flash("Unsupported language selection.", "error")
            else:
                current_user.locale = locale
                db.session.commit()
                flash("Language preference updated.", "success")
        elif request.form.get("action") == "delete_account":
            password = request.form.get("password", "")
            if not current_user.check_password(password):
                flash("Password is incorrect. Account not deleted.", "error")
            else:
                user = current_user._get_current_object()
                logout_user()
                db.session.delete(user)
                db.session.commit()
                flash("Account deleted successfully.", "info")
                return redirect(url_for("auth.register"))

    return render_template("auth/profile.html")


@auth_bp.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not current_user.check_password(current_password):
        flash("Current password is incorrect.", "error")
    elif new_password != confirm_password:
        flash("New passwords do not match.", "error")
    elif len(new_password) < 8:
        flash("Password must be at least 8 characters long.", "error")
    else:
        current_user.set_password(new_password)
        db.session.commit()
        logout_user()
        flash("Password updated. Please sign in again.", "success")
        return redirect(url_for("auth.login"))

    return redirect(url_for("auth.profile"))


def _send_verification_email(user: User) -> None:
    token = generate_token({"email": user.email}, "email-verify")
    verification_link = url_for("auth.verify_email", token=token, _external=True)
    html_body = render_template(
        "emails/verify_email.html",
        username=user.username,
        verification_link=verification_link,
    )
    send_email("Confirm your account", [user.email], html_body)


def _send_password_reset_email(user: User) -> None:
    token = generate_token({"email": user.email}, "password-reset")
    reset_link = url_for("auth.reset_password", token=token, _external=True)
    html_body = render_template(
        "emails/reset_password.html",
        username=user.username,
        reset_link=reset_link,
    )
    send_email("Reset your password", [user.email], html_body)
