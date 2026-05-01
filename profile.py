from flask import Blueprint, render_template, session, redirect, url_for
from models.user import User
from models.club import Club
from models.membership import Membership

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
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

    return render_template(
        "profile.html",
        user=user,
        club_history=joined_clubs
    )
