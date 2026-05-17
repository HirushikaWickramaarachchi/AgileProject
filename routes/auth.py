from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import re
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name").strip()
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        confirm = request.form.get("confirmPassword")

        # EMAIL VALIDATION
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(email_pattern, email):
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for("auth.register"))

        # STRONG PASSWORD VALIDATION
        password_pattern = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,}$"
        )

        if not re.match(password_pattern, password):
            flash(
                "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character.",
                "danger",
            )
            return redirect(url_for("auth.register"))

        # PASSWORD MATCH CHECK
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        # CHECK EXISTING EMAIL
        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.register"))

        # CREATE USER
        new_user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id
        session["user_name"] = new_user.name

        flash("Account created successfully.", "success")

        return redirect(url_for("dashboard.home"))

    return render_template("signup.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):

            session.permanent = True
            session["user_id"] = user.id
            session["user_name"] = user.name

            if user.is_admin:
                session["admin_logged_in"] = True
                session["admin_user_id"] = user.id
                session["admin_name"] = user.name
                flash("Login successful.", "success")
                return redirect(url_for("admin.dashboard"))

            flash("Login successful.", "success")
            return redirect(url_for("dashboard.home"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@auth.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("dashboard.index"))


@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        confirm = request.form.get("confirmPassword")

        # STRONG PASSWORD VALIDATION
        password_pattern = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,}$"
        )

        if not re.match(password_pattern, password):
            flash(
                "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number and one special character.",
                "danger",
            )
            return redirect(url_for("auth.forgot_password"))

        # CHECK PASSWORD MATCH
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.forgot_password"))

        # CHECK USER EXISTS
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email not found.", "danger")
            return redirect(url_for("auth.forgot_password"))

        # UPDATE PASSWORD
        user.password_hash = generate_password_hash(password)

        db.session.commit()

        flash("Password reset successful.", "success")

        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")