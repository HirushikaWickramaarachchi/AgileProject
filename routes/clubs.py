from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import Attendance, Club, Event, Membership, User, db

clubs_bp = Blueprint("clubs", __name__)
CLUB_CATEGORIES = ["All", "Tech", "Arts", "Culture", "Academic", "Leadership"]
SEARCH_MIN_CHARS = 2


def _get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    current_user = db.session.get(User, user_id)

    if not current_user:
        session.pop("user_id", None)
        session.pop("user_name", None)
        return None

    return current_user


def _member_club_ids_for_user(user_id):
    if not user_id:
        return set()

    memberships = Membership.query.filter_by(user_id=user_id).all()
    return {membership.club_id for membership in memberships}


def _attended_events_by_club_for_user(user_id, club_ids):
    if not user_id or not club_ids:
        return {}

    attended_events = (
        Event.query.join(Attendance, Attendance.event_id == Event.id)
        .filter(Attendance.user_id == user_id, Event.club_id.in_(club_ids))
        .order_by(Event.id.asc())
        .all()
    )
    attended_events_by_club = {club_id: [] for club_id in club_ids}

    for event in attended_events:
        attended_events_by_club[event.club_id].append(event)

    return attended_events_by_club


def _redirect_to_safe_next_or(default_endpoint, **default_values):
    next_path = request.form.get("next", "").strip()

    if next_path and next_path.startswith("/") and not next_path.startswith("//"):
        return redirect(next_path)

    return redirect(url_for(default_endpoint, **default_values))


def _search_snippet(text, max_length=140):
    if not text:
        return ""
    compact_text = " ".join(text.split())
    if len(compact_text) <= max_length:
        return compact_text
    return compact_text[: max_length - 1].rstrip() + "…"


@clubs_bp.route("/search")
def search():
    raw_query = request.args.get("q", "", type=str)
    query = " ".join(raw_query.strip().split())

    validation_error = None
    results = []

    if query and len(query) < SEARCH_MIN_CHARS:
        validation_error = f"Please enter at least {SEARCH_MIN_CHARS} characters to search."
    elif query:
        like_query = f"%{query}%"

        matched_clubs = (
            Club.query.filter(
                db.or_(
                    Club.name.ilike(like_query),
                    Club.description.ilike(like_query),
                )
            )
            .order_by(Club.name.asc())
            .all()
        )

        matched_events = (
            Event.query.join(Club, Event.club_id == Club.id)
            .filter(
                db.or_(
                    Event.title.ilike(like_query),
                    Event.description.ilike(like_query),
                    Club.name.ilike(like_query),
                )
            )
            .order_by(Event.id.asc())
            .all()
        )

        for club in matched_clubs:
            results.append(
                {
                    "type": "Club",
                    "title": club.name,
                    "description": _search_snippet(club.description),
                    "url": url_for("clubs.club_details", club_id=club.id),
                    "meta": club.category if club.category else "Student Club",
                }
            )

        for event in matched_events:
            host_club = event.club.name if event.club else "Club Event"
            results.append(
                {
                    "type": "Event",
                    "title": event.title,
                    "description": _search_snippet(
                        event.description if event.description else "No event description available."
                    ),
                    "url": url_for("clubs.event_details", event_id=event.id),
                    "meta": f"{host_club} | {event.date}",
                }
            )

    return render_template(
        "search_results.html",
        query=query,
        search_min_chars=SEARCH_MIN_CHARS,
        validation_error=validation_error,
        results=results,
        total_results=len(results),
    )


@clubs_bp.route("/clubs")
def clubs():
    requested_category = request.args.get("category", "All", type=str).strip()
    selected_category = (
        requested_category if requested_category in CLUB_CATEGORIES else "All"
    )

    clubs_query = Club.query
    if selected_category != "All":
        clubs_query = clubs_query.filter(Club.category == selected_category)

    clubs_list = clubs_query.order_by(Club.name.asc()).all()
    current_user = _get_current_user()
    member_club_ids = _member_club_ids_for_user(current_user.id if current_user else None)
    attended_events_by_club = _attended_events_by_club_for_user(
        current_user.id if current_user else None,
        [club.id for club in clubs_list],
    )
    club_summaries = []

    for club in clubs_list:
        events = sorted(club.events, key=lambda club_event: club_event.id)
        club_summaries.append(
            {
                "club": club,
                "member_count": len(club.memberships),
                "event_count": len(events),
                "is_member": club.id in member_club_ids,
                "attended_events": attended_events_by_club.get(club.id, []),
            }
        )

    return render_template(
        "club_list.html",
        club_summaries=club_summaries,
        categories=CLUB_CATEGORIES,
        selected_category=selected_category,
    )


@clubs_bp.route("/clubs/<int:club_id>")
def club_details(club_id):
    club = Club.query.get_or_404(club_id)
    events = Event.query.filter_by(club_id=club.id).order_by(Event.id.asc()).all()
    current_user = _get_current_user()
    member_club_ids = _member_club_ids_for_user(current_user.id if current_user else None)
    attended_events_by_club = _attended_events_by_club_for_user(
        current_user.id if current_user else None,
        [club.id],
    )
    members = sorted(
        (membership.user for membership in club.memberships if membership.user is not None),
        key=lambda user: user.name.lower(),
    )

    return render_template(
        "club_details.html",
        club=club,
        events=events,
        members=members,
        member_count=len(club.memberships),
        is_member=club.id in member_club_ids,
        attended_events=attended_events_by_club.get(club.id, []),
    )


@clubs_bp.route("/clubs/<int:club_id>/join", methods=["POST"])
def join_club(club_id):
    current_user = _get_current_user()

    if not current_user:
        flash("Please log in to join a club.", "warning")
        return redirect(url_for("auth.login"))

    club = Club.query.get_or_404(club_id)
    existing_membership = Membership.query.filter_by(
        user_id=current_user.id,
        club_id=club.id,
    ).first()

    if existing_membership:
        flash(f"You are already a member of {club.name}.", "info")
        return _redirect_to_safe_next_or("clubs.club_details", club_id=club.id)

    db_membership = Membership(user_id=current_user.id, club_id=club.id)
    db.session.add(db_membership)
    db.session.commit()

    flash(f"You joined {club.name}.", "success")
    return _redirect_to_safe_next_or("clubs.club_details", club_id=club.id)


@clubs_bp.route("/clubs/<int:club_id>/leave", methods=["POST"])
def leave_club(club_id):
    current_user = _get_current_user()

    if not current_user:
        flash("Please log in to leave a club.", "warning")
        return redirect(url_for("auth.login"))

    club = Club.query.get_or_404(club_id)
    membership = Membership.query.filter_by(
        user_id=current_user.id,
        club_id=club.id,
    ).first()

    if not membership:
        flash(f"You are not currently a member of {club.name}.", "info")
        return _redirect_to_safe_next_or("clubs.club_details", club_id=club.id)

    related_attendances = (
        Attendance.query.join(Event, Attendance.event_id == Event.id)
        .filter(
            Attendance.user_id == current_user.id,
            Event.club_id == club.id,
        )
        .all()
    )
    cancelled_attendance_count = len(related_attendances)

    for attendance in related_attendances:
        db.session.delete(attendance)

    db.session.delete(membership)
    db.session.commit()

    if cancelled_attendance_count:
        event_label = "event" if cancelled_attendance_count == 1 else "events"
        flash(
            f"You left {club.name} and your attendance for "
            f"{cancelled_attendance_count} related {event_label} was cancelled.",
            "success",
        )
    else:
        flash(f"You left {club.name}.", "success")

    return _redirect_to_safe_next_or("clubs.club_details", club_id=club.id)


@clubs_bp.route("/events")
def events():
    featured_event = Event.query.order_by(Event.id.asc()).first()

    if featured_event:
        return redirect(url_for("clubs.event_details", event_id=featured_event.id))

    return render_template(
        "event.html",
        event=None,
        club=None,
        attendee_count=0,
        attendees=[],
        related_events=[],
        is_attending=False,
        is_club_member=False,
    )


@clubs_bp.route("/events/<int:event_id>")
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    attendees = sorted(
        (
            attendance.user
            for attendance in event.attendances
            if attendance.user is not None
        ),
        key=lambda user: user.name.lower(),
    )
    related_events = (
        Event.query.filter(Event.club_id == event.club_id, Event.id != event.id)
        .order_by(Event.id.asc())
        .limit(3)
        .all()
    )
    is_attending = False
    is_club_member = False
    current_user = _get_current_user()

    if current_user:
        membership = Membership.query.filter_by(
            user_id=current_user.id,
            club_id=event.club_id,
        ).first()
        is_club_member = membership is not None

        attendance = Attendance.query.filter_by(
            user_id=current_user.id,
            event_id=event.id,
        ).first()
        is_attending = attendance is not None

    return render_template(
        "event.html",
        event=event,
        club=event.club,
        attendee_count=len(event.attendances),
        attendees=attendees,
        related_events=related_events,
        is_attending=is_attending,
        is_club_member=is_club_member,
    )


@clubs_bp.route("/events/<int:event_id>/attend", methods=["POST"])
def attend_event(event_id):
    current_user = _get_current_user()

    if not current_user:
        flash("Please log in to mark attendance.", "warning")
        return redirect(url_for("auth.login"))

    event = Event.query.get_or_404(event_id)
    existing_attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        event_id=event.id,
    ).first()

    if existing_attendance:
        flash(f"You are already marked as attending {event.title}.", "info")
        return _redirect_to_safe_next_or("clubs.event_details", event_id=event.id)

    membership = Membership.query.filter_by(
        user_id=current_user.id,
        club_id=event.club_id,
    ).first()
    if not membership:
        club_name = event.club.name if event.club else "this club"
        flash(
            f"You need to join {club_name} before attending its events.",
            "warning",
        )
        return _redirect_to_safe_next_or("clubs.event_details", event_id=event.id)

    attendance = Attendance(user_id=current_user.id, event_id=event.id)
    db.session.add(attendance)
    db.session.commit()

    flash(f"Attendance marked for {event.title}.", "success")
    return _redirect_to_safe_next_or("clubs.event_details", event_id=event.id)


@clubs_bp.route("/events/<int:event_id>/unattend", methods=["POST"])
def unattend_event(event_id):
    current_user = _get_current_user()

    if not current_user:
        flash("Please log in to update attendance.", "warning")
        return redirect(url_for("auth.login"))

    event = Event.query.get_or_404(event_id)
    attendance = Attendance.query.filter_by(
        user_id=current_user.id,
        event_id=event.id,
    ).first()

    if not attendance:
        flash(f"You are not currently marked as attending {event.title}.", "info")
        return _redirect_to_safe_next_or("clubs.event_details", event_id=event.id)

    db.session.delete(attendance)
    db.session.commit()

    flash(f"Attendance removed for {event.title}.", "success")
    return _redirect_to_safe_next_or("clubs.event_details", event_id=event.id)


@clubs_bp.route("/myclubs")
def myclubs():
    current_user = _get_current_user()

    if not current_user:
        return redirect(url_for("auth.login"))

    joined_clubs = (
        Club.query.join(Membership, Membership.club_id == Club.id)
        .filter(Membership.user_id == current_user.id)
        .order_by(Club.name.asc())
        .all()
    )
    club_ids = [club.id for club in joined_clubs]
    attended_events_by_club = _attended_events_by_club_for_user(current_user.id, club_ids)
    my_club_summaries = []

    for club in joined_clubs:
        my_club_summaries.append(
            {
                "club": club,
                "member_count": len(club.memberships),
                "event_count": len(club.events),
                "attended_events": attended_events_by_club.get(club.id, []),
            }
        )

    return render_template(
        "my_clubs.html",
        current_user=current_user,
        my_club_summaries=my_club_summaries,
    )
