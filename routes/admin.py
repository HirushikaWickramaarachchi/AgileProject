from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from models import db
from models.user import User
from models.club import Club
from models.event import Event
from models.membership import Membership


def _parse_event_date(date_str):
    for fmt in ("%A, %B %d, %Y", "%A, %B %d, %Y | %I:%M %p"):
        try:
            part = date_str.split(" | ")[0].strip()
            return datetime.strptime(part, "%A, %B %d, %Y")
        except ValueError:
            pass
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except ValueError:
        return datetime.min

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


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

        user = User.query.filter_by(email=email, is_admin=True).first()
        if user and check_password_hash(user.password_hash, password):
            session.permanent = bool(request.form.get("remember"))
            session["admin_logged_in"] = True
            session["admin_user_id"] = user.id
            session["admin_name"] = user.name
            return redirect(url_for("admin.members"))

        flash("Invalid email or password.")

    return render_template("admin_login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_user_id", None)
    session.pop("admin_name", None)
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


@admin_bp.route("/clubs", methods=["GET", "POST"])
@admin_required
def clubs():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if not name or not description:
            flash("Name and description are required.", "danger")
        elif Club.query.filter_by(name=name).first():
            flash("A club with that name already exists.", "danger")
        else:
            db.session.add(Club(name=name, description=description))
            db.session.commit()
            flash("Club created successfully.", "success")
        return redirect(url_for("admin.clubs"))

    all_clubs = (
        db.session.query(Club, db.func.count(Membership.id).label("member_count"))
        .outerjoin(Membership, Club.id == Membership.club_id)
        .group_by(Club.id)
        .order_by(Club.name)
        .all()
    )
    return render_template("admin_clubs.html", all_clubs=all_clubs)


@admin_bp.route("/clubs/<int:club_id>/delete", methods=["POST"])
@admin_required
def delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    db.session.delete(club)
    db.session.commit()
    flash(f'"{club.name}" and all its events and memberships have been deleted.', "success")
    return redirect(url_for("admin.clubs"))


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


@admin_bp.route("/events", methods=["GET", "POST"])
@admin_required
def events():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        club_id = request.form.get("club_id", "").strip()
        date = request.form.get("date", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not club_id or not date:
            flash("Title, club, and date are required.", "danger")
        else:
            event = Event(title=title, club_id=int(club_id), date=date, description=description)
            db.session.add(event)
            db.session.commit()
            flash("Event created successfully.", "success")
        return redirect(url_for("admin.events"))

    all_events = sorted(
        db.session.query(Event, Club)
        .join(Club, Event.club_id == Club.id)
        .all(),
        key=lambda row: _parse_event_date(row[0].date)
    )
    clubs = Club.query.order_by(Club.name).all()
    total_events = Event.query.count()
    return render_template("admin_events.html", all_events=all_events, clubs=clubs, total_events=total_events)


@admin_bp.route("/events/<int:event_id>/edit", methods=["POST"])
@admin_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    title = request.form.get("title", "").strip()
    club_id = request.form.get("club_id", "").strip()
    date = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()

    if not title or not club_id or not date:
        flash("Title, club, and date are required.", "danger")
    else:
        event.title = title
        event.club_id = int(club_id)
        event.date = date
        event.description = description
        db.session.commit()
        flash("Event updated successfully.", "success")
    return redirect(url_for("admin.events"))


@admin_bp.route("/events/<int:event_id>/delete", methods=["POST"])
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted.", "success")
    return redirect(url_for("admin.events"))


@admin_bp.route("/users")
@admin_required
def users():
    all_users = User.query.filter_by(is_admin=False).order_by(User.name).all()
    return render_template("admin_users.html", all_users=all_users)


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash("Cannot delete admin accounts.", "danger")
        return redirect(url_for("admin.users"))
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{user.name}" has been deleted.', "success")
    return redirect(url_for("admin.users"))
