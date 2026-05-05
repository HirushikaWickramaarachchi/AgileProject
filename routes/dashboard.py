from flask import Blueprint, render_template, session, redirect, url_for
from models.user import User

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def index():
    return render_template("home.html")


@dashboard_bp.route("/home")
def home():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("home.html")


@dashboard_bp.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("home.html")


@dashboard_bp.route("/profile")
def profile():

    user_id = session["user_id"]

    user = User.query.get(user_id)

    return render_template("profile.html", user=user)

@dashboard_bp.route("/edit_profile")
def edit_profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("profile_edit.html")