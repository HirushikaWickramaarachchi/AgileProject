import csv
import io
import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app, Response
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from models import db
from models.user import User
from models.club import Club
from models.event import Event
from models.membership import Membership
from models.attendance import Attendance
from models.profile_user import ProfileUser


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
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email, is_admin=True).first()
        if user and check_password_hash(user.password_hash, password):
            session.permanent = bool(request.form.get("remember"))
            session["admin_logged_in"] = True
            session["admin_user_id"] = user.id
            session["admin_name"] = user.name
            return redirect(url_for("admin.dashboard"))

        flash("Invalid email or password.", "danger")

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

    upcoming_events = sorted(
        db.session.query(Event, Club).join(Club, Event.club_id == Club.id).all(),
        key=lambda row: _parse_event_date(row[0].date)
    )[:4]

    recent_memberships = (
        db.session.query(Membership, User, Club)
        .join(User, Membership.user_id == User.id)
        .join(Club, Membership.club_id == Club.id)
        .order_by(Membership.id.desc())
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
        upcoming_events=upcoming_events,
        recent_memberships=recent_memberships,
    )


ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def _save_club_image(file):
    if not file or file.filename == "":
        return None, None
    ext = os.path.splitext(secure_filename(file.filename))[1].lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        return None, f"Invalid image format '{ext}'. Allowed: PNG, JPG, GIF, WEBP."
    filename = f"clubs/{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(current_app.root_path, "static", "images", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file.save(save_path)
    return f"images/{filename}", None


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
            image_path, img_err = _save_club_image(request.files.get("image"))
            if img_err:
                flash(img_err, "danger")
            else:
                db.session.add(Club(name=name, description=description, image_path=image_path))
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


@admin_bp.route("/clubs/<int:club_id>/edit", methods=["POST"])
@admin_required
def edit_club(club_id):
    club = Club.query.get_or_404(club_id)
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if not name or not description:
        flash("Name and description are required.", "danger")
    elif Club.query.filter(Club.name == name, Club.id != club_id).first():
        flash("A club with that name already exists.", "danger")
    else:
        new_image, img_err = _save_club_image(request.files.get("image"))
        if img_err:
            flash(img_err, "danger")
        else:
            club.name = name
            club.description = description
            if new_image:
                club.image_path = new_image
            db.session.commit()
            flash(f'"{club.name}" updated successfully.', "success")
    return redirect(url_for("admin.clubs"))


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
    all_users = User.query.filter_by(is_admin=False).order_by(User.name).all()
    all_clubs = Club.query.order_by(Club.name).all()
    return render_template(
        "admin_members.html",
        memberships=memberships,
        total_users=total_users,
        all_users=all_users,
        all_clubs=all_clubs,
    )


@admin_bp.route("/members/add", methods=["POST"])
@admin_required
def add_member():
    user_id = request.form.get("user_id", "").strip()
    club_id = request.form.get("club_id", "").strip()
    if not user_id or not club_id:
        flash("User and club are required.", "danger")
        return redirect(url_for("admin.members"))
    existing = Membership.query.filter_by(user_id=int(user_id), club_id=int(club_id)).first()
    if existing:
        flash("That user is already a member of that club.", "warning")
        return redirect(url_for("admin.members"))
    db.session.add(Membership(user_id=int(user_id), club_id=int(club_id)))
    db.session.commit()
    flash("Member added successfully.", "success")
    return redirect(url_for("admin.members"))


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


@admin_bp.route("/events/<int:event_id>/attendees")
@admin_required
def event_attendees(event_id):
    event = Event.query.get_or_404(event_id)
    attendance_records = (
        db.session.query(Attendance, User)
        .join(User, Attendance.user_id == User.id)
        .filter(Attendance.event_id == event_id)
        .order_by(User.name)
        .all()
    )
    attended_user_ids = {a.user_id for a, _ in attendance_records}
    all_users = User.query.filter_by(is_admin=False).order_by(User.name).all()
    non_attendees = [u for u in all_users if u.id not in attended_user_ids]
    return jsonify({
        "event": event.title,
        "attendees": [
            {"attendance_id": a.id, "name": u.name, "email": u.email}
            for a, u in attendance_records
        ],
        "non_attendees": [{"id": u.id, "name": u.name} for u in non_attendees],
    })


@admin_bp.route("/events/<int:event_id>/attendance/add", methods=["POST"])
@admin_required
def add_attendance(event_id):
    Event.query.get_or_404(event_id)
    user_id = request.form.get("user_id", "").strip()
    if not user_id:
        return jsonify({"error": "user_id required"}), 400
    existing = Attendance.query.filter_by(user_id=int(user_id), event_id=event_id).first()
    if existing:
        return jsonify({"error": "Already marked as attended"}), 409
    record = Attendance(user_id=int(user_id), event_id=event_id)
    db.session.add(record)
    db.session.commit()
    user = User.query.get(int(user_id))
    return jsonify({"attendance_id": record.id, "name": user.name, "email": user.email})


@admin_bp.route("/events/attendance/<int:attendance_id>/remove", methods=["POST"])
@admin_required
def remove_attendance(attendance_id):
    record = Attendance.query.get_or_404(attendance_id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({"ok": True})


@admin_bp.route("/events/<int:event_id>/attendees/export")
@admin_required
def export_attendees(event_id):
    event = Event.query.get_or_404(event_id)
    attendees = (
        db.session.query(User)
        .join(Attendance, Attendance.user_id == User.id)
        .filter(Attendance.event_id == event_id)
        .order_by(User.name)
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Email"])
    for u in attendees:
        writer.writerow([u.name, u.email])
    filename = f"{event.title.replace(' ', '_')}_attendees.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


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
    all_users = User.query.order_by(User.name).all()
    return render_template("admin_users.html", all_users=all_users)


@admin_bp.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session.get("admin_user_id"):
        flash("You cannot change your own admin status.", "danger")
        return redirect(url_for("admin.users"))
    user.is_admin = not user.is_admin
    db.session.commit()
    status = "promoted to admin" if user.is_admin else "demoted to regular user"
    flash(f'"{user.name}" has been {status}.', "success")
    return redirect(url_for("admin.users"))


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


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@admin_required
def reset_user_password(user_id):
    from werkzeug.security import generate_password_hash
    user = User.query.get_or_404(user_id)
    new_password = request.form.get("new_password", "").strip()
    if len(new_password) < 6:
        flash("Password must be at least 6 characters.", "danger")
        return redirect(url_for("admin.users"))
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    flash(f'Password for "{user.name}" has been reset.', "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/profile")
@admin_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    profile = ProfileUser.query.filter_by(user_id=user_id).first()
    club_count = Membership.query.filter_by(user_id=user_id).count()
    event_count = Attendance.query.filter_by(user_id=user_id).count()
    return jsonify({
        "name": user.name,
        "email": user.email,
        "is_admin": user.is_admin,
        "clubs_joined": club_count,
        "events_attended": event_count,
        "major": profile.major if profile else None,
        "phone": profile.phone if profile else None,
        "address": profile.address if profile else None,
        "gender": profile.gender if profile else None,
        "bio": profile.bio if profile else None,
        "dob": profile.dob if profile else None,
    })
