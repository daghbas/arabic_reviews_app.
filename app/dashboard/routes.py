from __future__ import annotations

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import User
from . import dashboard_bp


def _admin_required():
    if not current_user.is_admin:
        flash("Administrator access is required to view that page.", "error")
        return False
    return True


@dashboard_bp.route("/home")
@login_required
def user_home():
    if current_user.is_admin:
        return redirect(url_for("dashboard.admin_panel"))
    return render_template("dashboard/user_home.html")


@dashboard_bp.route("/admin", methods=["GET", "POST"])
@login_required
def admin_panel():
    if not _admin_required():
        return redirect(url_for("dashboard.user_home"))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            role = request.form.get("role", "user")

            errors = []
            if not username or not email or not password:
                errors.append("All fields are required for new users.")
            if len(password) < 8:
                errors.append("Password must be at least 8 characters long.")
            if User.query.filter((User.email == email) | (User.username == username)).first():
                errors.append("A user with that email or username already exists.")

            if errors:
                for error in errors:
                    flash(error, "error")
            else:
                new_user = User(username=username, email=email, role=role, email_confirmed=True)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash("User created successfully.", "success")

        elif action == "delete":
            user_id = request.form.get("user_id")
            user = db.session.get(User, int(user_id)) if user_id and user_id.isdigit() else None
            if user and user.id != current_user.id:
                db.session.delete(user)
                db.session.commit()
                flash("User deleted.", "info")
            else:
                flash("Cannot delete that user.", "error")

    query = User.query.order_by(User.created_at.desc())
    search = request.args.get("q", "").strip()
    role_filter = request.args.get("role", "")

    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%"))
            | (User.email.ilike(f"%{search}%"))
        )
    if role_filter:
        query = query.filter_by(role=role_filter)

    users = query.all()
    roles = sorted({row[0] for row in User.query.with_entities(User.role).distinct()})

    return render_template(
        "dashboard/admin_panel.html",
        users=users,
        search=search,
        role_filter=role_filter,
        roles=roles,
    )
