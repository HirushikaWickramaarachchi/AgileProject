from flask import Blueprint, render_template, request, redirect, url_for, flash, session
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

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.register"))

        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already exists.", "danger")
            return redirect(url_for("auth.register"))

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

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email not found.", "danger")
            return redirect(url_for("auth.forgot_password"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("auth.forgot_password"))

        user.password_hash = generate_password_hash(password)
        db.session.commit()

        flash("Password reset successful.", "success")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")