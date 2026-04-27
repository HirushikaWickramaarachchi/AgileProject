from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db
from models.user import User
from models.club import Club
from models.event import Event
from models.membership import Membership

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

ADMIN_EMAIL = "admin@clubsync.edu"
ADMIN_PASSWORD = "admin123"


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
def index():
    return redirect(url_for("admin.login"))


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.members"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin.members"))

        flash("Invalid email or password.")

    return render_template("admin_login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.login"))


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    total_users = User.query.count()
    total_clubs = Club.query.count()
    total_events = Event.query.count()
    total_memberships = Membership.query.count()

    clubs_with_counts = (
        db.session.query(Club, db.func.count(Membership.id).label("member_count"))
        .outerjoin(Membership, Club.id == Membership.club_id)
        .group_by(Club.id)
        .order_by(db.desc("member_count"))
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_clubs=total_clubs,
        total_events=total_events,
        total_memberships=total_memberships,
        clubs_with_counts=clubs_with_counts,
    )


@admin_bp.route("/members")
@admin_required
def members():
    memberships = (
        db.session.query(Membership, User, Club)
        .join(User, Membership.user_id == User.id)
        .join(Club, Membership.club_id == Club.id)
        .order_by(User.name)
        .all()
    )
    total_users = User.query.count()
    return render_template("admin_members.html", memberships=memberships, total_users=total_users)


@admin_bp.route("/members/<int:membership_id>/remove", methods=["POST"])
@admin_required
def remove_member(membership_id):
    membership = Membership.query.get_or_404(membership_id)
    db.session.delete(membership)
    db.session.commit()
    flash("Member removed from club.", "success")
    return redirect(url_for("admin.members"))


@admin_bp.route("/events")
@admin_required
def events():
    return render_template("admin_events.html")
