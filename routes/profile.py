from flask import Blueprint, render_template, session, redirect, url_for, request
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os

from models import db
from models.user import User
from models.club import Club
from models.membership import Membership
from models.profile_user import ProfileUser


profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/my-profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    user = User.query.get(user_id)

    joined_clubs = (
        Club.query
        .join(Membership, Membership.club_id == Club.id)
        .filter(Membership.user_id == user_id)
        .order_by(Club.name.asc())
        .all()
    )

    profile_data = ProfileUser.query.filter_by(user_id=user.id).first()

    return render_template(
        "profile.html",
        user=user,
        profile=profile_data,
        club_history=joined_clubs
    )


@profile_bp.route("/profile-edit", methods=["GET", "POST"])
def profile_edit():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    profile_data = ProfileUser.query.filter_by(user_id=user.id).first()

    if not profile_data:
        profile_data = ProfileUser(user_id=user.id)
        db.session.add(profile_data)

    if request.method == "POST":

        avatar = request.files.get("avatar")

        if avatar and avatar.filename:

            filename = secure_filename(avatar.filename)

            upload_folder = os.path.join(
                "static",
                "uploads"
            )

            os.makedirs(upload_folder, exist_ok=True)

            avatar_path = os.path.join(
                upload_folder,
                filename
            )

            avatar.save(avatar_path)

            profile_data.avatar = filename



        # Account Management: change password
        if request.form.get("current_password"):
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            if not current_password and not new_password and not confirm_password:
                return redirect(url_for("profile.profile_edit", error="no_change"))

            if not check_password_hash(user.password_hash, current_password):
                return redirect(url_for("profile.profile_edit", error="wrong_password"))

            if new_password != confirm_password:
                return redirect(url_for("profile.profile_edit", error="password_mismatch"))

            if not new_password:
                return "New password cannot be empty"

            user.password_hash = generate_password_hash(new_password)
            db.session.commit()

            return redirect(url_for("profile.profile_edit", updated=1))

        # User table fields
        if "name" in request.form:
            name = request.form.get("name")
            if name:
                user.name = name

        if "email" in request.form:
            email = request.form.get("email")
            if email:
                user.email = email

        # ProfileUser table fields
        if "major" in request.form:
            profile_data.major = request.form.get("major")

        if "phone" in request.form:
            profile_data.phone = request.form.get("phone")

        if "address" in request.form:
            profile_data.address = request.form.get("address")

        if "gender" in request.form:
            profile_data.gender = request.form.get("gender")

        if "bio" in request.form:
            profile_data.bio = request.form.get("bio")

        if "dob" in request.form:
            profile_data.dob = request.form.get("dob")

        db.session.commit()

        section = request.args.get("section", "edit-profile")
        return redirect(url_for("profile.profile_edit", updated=1, section=section))

    return render_template(
        "profile_edit.html",
        user=user,
        profile=profile_data
    )