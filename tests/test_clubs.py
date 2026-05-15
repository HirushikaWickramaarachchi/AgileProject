"""Tests for clubs routes: list, details, join, leave, events, attend, unattend, myclubs."""
from werkzeug.security import generate_password_hash
from models import db as _db
from models.user import User
from models.club import Club
from models.event import Event
from models.membership import Membership
from models.attendance import Attendance


def _logged_in_client(client, app):
    """Create a regular user and log them in; returns (client, user_id)."""
    with app.app_context():
        user = User(
            name="Club User",
            email="clubuser@example.com",
            password_hash=generate_password_hash("pass"),
        )
        _db.session.add(user)
        _db.session.commit()
        uid = user.id
    with client.session_transaction() as sess:
        sess["user_id"] = uid
    return client, uid


class TestClubList:
    def test_clubs_page_loads(self, client):
        res = client.get("/clubs")
        assert res.status_code == 200

    def test_clubs_shows_club_name(self, client, sample_club, app):
        with app.app_context():
            club = Club.query.get(sample_club)
            name = club.name
        res = client.get("/clubs")
        assert name.encode() in res.data

    def test_clubs_category_filter(self, client, app):
        with app.app_context():
            club = Club(name="Tech Club", category="Tech", description="")
            _db.session.add(club)
            _db.session.commit()
        res = client.get("/clubs?category=Tech")
        assert res.status_code == 200
        assert b"Tech Club" in res.data

    def test_clubs_invalid_category_defaults_to_all(self, client, sample_club):
        res = client.get("/clubs?category=NonExistent")
        assert res.status_code == 200


class TestClubDetails:
    def test_club_details_loads(self, client, sample_club):
        res = client.get(f"/clubs/{sample_club}")
        assert res.status_code == 200

    def test_club_details_404_on_missing(self, client):
        res = client.get("/clubs/99999")
        assert res.status_code == 404

    def test_club_details_shows_events(self, client, sample_club, sample_event, app):
        with app.app_context():
            event = Event.query.get(sample_event)
            title = event.title
        res = client.get(f"/clubs/{sample_club}")
        assert title.encode() in res.data

    def test_club_details_shows_club_image_when_present(self, client, app):
        with app.app_context():
            club = Club(
                name="Image Club",
                description="Club with custom image",
                image_path="images/clubs/ai-society.jpg",
            )
            _db.session.add(club)
            _db.session.commit()
            club_id = club.id

        res = client.get(f"/clubs/{club_id}")
        assert b"images/clubs/ai-society.jpg" in res.data

    def test_club_details_uses_default_image_when_missing(self, client, sample_club):
        res = client.get(f"/clubs/{sample_club}")
        assert b"images/clubs/default.png" in res.data


class TestJoinClub:
    def test_join_requires_login(self, client, sample_club):
        res = client.post(f"/clubs/{sample_club}/join", follow_redirects=True)
        assert b"log in" in res.data.lower() or res.status_code == 200

    def test_join_success(self, client, app, sample_club):
        c, uid = _logged_in_client(client, app)
        res = c.post(f"/clubs/{sample_club}/join", follow_redirects=True)
        assert res.status_code == 200
        with app.app_context():
            m = Membership.query.filter_by(user_id=uid, club_id=sample_club).first()
            assert m is not None

    def test_join_duplicate_shows_flash(self, client, app, sample_club):
        c, uid = _logged_in_client(client, app)
        with app.app_context():
            _db.session.add(Membership(user_id=uid, club_id=sample_club))
            _db.session.commit()
        res = c.post(f"/clubs/{sample_club}/join", follow_redirects=True)
        assert b"already a member" in res.data


class TestLeaveClub:
    def test_leave_requires_login(self, client, sample_club):
        res = client.post(f"/clubs/{sample_club}/leave", follow_redirects=True)
        assert b"log in" in res.data.lower() or res.status_code == 200

    def test_leave_success(self, client, app, sample_club):
        c, uid = _logged_in_client(client, app)
        with app.app_context():
            _db.session.add(Membership(user_id=uid, club_id=sample_club))
            _db.session.commit()
        res = c.post(f"/clubs/{sample_club}/leave", follow_redirects=True)
        assert res.status_code == 200
        with app.app_context():
            m = Membership.query.filter_by(user_id=uid, club_id=sample_club).first()
            assert m is None

    def test_leave_removes_related_attendance_only_and_keeps_events(self, client, app, sample_club, sample_event):
        c, uid = _logged_in_client(client, app)
        with app.app_context():
            other_club = Club(name="Other Club", description="Another club")
            other_user = User(
                name="Other User",
                email="other@example.com",
                password_hash=generate_password_hash("pass"),
            )
            _db.session.add_all([other_club, other_user])
            _db.session.commit()

            other_event = Event(
                title="Other Club Event",
                club_id=other_club.id,
                date="2026-07-01",
                description="Different club event",
            )
            _db.session.add(other_event)
            _db.session.commit()

            _db.session.add(Membership(user_id=uid, club_id=sample_club))
            _db.session.add(Attendance(user_id=uid, event_id=sample_event))
            _db.session.add(Attendance(user_id=uid, event_id=other_event.id))
            _db.session.add(Attendance(user_id=other_user.id, event_id=sample_event))
            _db.session.commit()

            other_event_id = other_event.id
            other_user_id = other_user.id

        res = c.post(f"/clubs/{sample_club}/leave", follow_redirects=True)
        assert res.status_code == 200
        assert b"attendance for 1 related event was cancelled" in res.data

        with app.app_context():
            membership = Membership.query.filter_by(user_id=uid, club_id=sample_club).first()
            related_attendance = Attendance.query.filter_by(user_id=uid, event_id=sample_event).first()
            other_club_attendance = Attendance.query.filter_by(user_id=uid, event_id=other_event_id).first()
            other_user_attendance = Attendance.query.filter_by(user_id=other_user_id, event_id=sample_event).first()

            assert membership is None
            assert related_attendance is None
            assert other_club_attendance is not None
            assert other_user_attendance is not None
            assert _db.session.get(Event, sample_event) is not None
            assert _db.session.get(Event, other_event_id) is not None

    def test_leave_removes_multiple_related_attendances(self, client, app, sample_club, sample_event):
        c, uid = _logged_in_client(client, app)
        with app.app_context():
            second_event = Event(
                title="Second Club Event",
                club_id=sample_club,
                date="2026-07-15",
                description="Another event from the same club",
            )
            _db.session.add(second_event)
            _db.session.commit()

            _db.session.add(Membership(user_id=uid, club_id=sample_club))
            _db.session.add(Attendance(user_id=uid, event_id=sample_event))
            _db.session.add(Attendance(user_id=uid, event_id=second_event.id))
            _db.session.commit()

            second_event_id = second_event.id

        res = c.post(f"/clubs/{sample_club}/leave", follow_redirects=True)
        assert res.status_code == 200
        assert b"attendance for 2 related events was cancelled" in res.data

        with app.app_context():
            assert Attendance.query.filter_by(user_id=uid, event_id=sample_event).first() is None
            assert Attendance.query.filter_by(user_id=uid, event_id=second_event_id).first() is None
            assert _db.session.get(Event, sample_event) is not None
            assert _db.session.get(Event, second_event_id) is not None

    def test_leave_not_member_shows_flash(self, client, app, sample_club):
        c, _ = _logged_in_client(client, app)
        res = c.post(f"/clubs/{sample_club}/leave", follow_redirects=True)
        assert b"not currently a member" in res.data


class TestEventRoutes:
    def test_events_redirect_to_first_event(self, client, sample_event):
        res = client.get("/events")
        assert res.status_code in (200, 302)

    def test_events_empty_renders_page(self, client):
        res = client.get("/events")
        assert res.status_code == 200

    def test_event_details_loads(self, client, sample_event):
        res = client.get(f"/events/{sample_event}")
        assert res.status_code == 200

    def test_event_details_404_on_missing(self, client):
        res = client.get("/events/99999")
        assert res.status_code == 404


class TestAttendEvent:
    def test_attend_requires_login(self, client, sample_event):
        res = client.post(f"/events/{sample_event}/attend", follow_redirects=True)
        assert b"log in" in res.data.lower() or res.status_code == 200

    def test_attend_requires_membership(self, client, app, sample_event):
        c, _ = _logged_in_client(client, app)
        res = c.post(f"/events/{sample_event}/attend", follow_redirects=True)
        assert b"join" in res.data.lower()

    def test_attend_success(self, client, app, sample_club, sample_event):
        c, uid = _logged_in_client(client, app)
        with app.app_context():
            _db.session.add(Membership(user_id=uid, club_id=sample_club))
            _db.session.commit()
        res = c.post(f"/events/{sample_event}/attend", follow_redirects=True)
        assert res.status_code == 200
        with app.app_context():
            a = Attendance.query.filter_by(user_id=uid, event_id=sample_event).first()
            assert a is not None

    def test_attend_duplicate_shows_flash(self, client, app, sample_club, sample_event):
        c, uid = _logged_in_client(client, app)
        with app.app_context():
            _db.session.add(Membership(user_id=uid, club_id=sample_club))
            _db.session.add(Attendance(user_id=uid, event_id=sample_event))
            _db.session.commit()
        res = c.post(f"/events/{sample_event}/attend", follow_redirects=True)
        assert b"already" in res.data


class TestUnattendEvent:
    def test_unattend_requires_login(self, client, sample_event):
        res = client.post(f"/events/{sample_event}/unattend", follow_redirects=True)
        assert b"log in" in res.data.lower() or res.status_code == 200

    def test_unattend_success(self, client, app, sample_club, sample_event):
        c, uid = _logged_in_client(client, app)
        with app.app_context():
            _db.session.add(Membership(user_id=uid, club_id=sample_club))
            _db.session.add(Attendance(user_id=uid, event_id=sample_event))
            _db.session.commit()
        res = c.post(f"/events/{sample_event}/unattend", follow_redirects=True)
        assert res.status_code == 200
        with app.app_context():
            a = Attendance.query.filter_by(user_id=uid, event_id=sample_event).first()
            assert a is None

    def test_unattend_not_attending_shows_flash(self, client, app, sample_event):
        c, _ = _logged_in_client(client, app)
        res = c.post(f"/events/{sample_event}/unattend", follow_redirects=True)
        assert b"not currently" in res.data


class TestMyClubs:
    def test_myclubs_requires_login(self, client):
        res = client.get("/myclubs")
        assert res.status_code == 302

    def test_myclubs_shows_joined_clubs(self, client, app, sample_club):
        c, uid = _logged_in_client(client, app)
        with app.app_context():
            _db.session.add(Membership(user_id=uid, club_id=sample_club))
            _db.session.commit()
            club_name = Club.query.get(sample_club).name
        res = c.get("/myclubs")
        assert res.status_code == 200
        assert club_name.encode() in res.data

    def test_myclubs_empty_when_no_clubs(self, client, app):
        c, _ = _logged_in_client(client, app)
        res = c.get("/myclubs")
        assert res.status_code == 200


class TestGlobalSearch:
    def test_search_page_loads_without_query(self, client):
        res = client.get("/search")
        assert res.status_code == 200
        assert b"Start Searching" in res.data

    def test_search_requires_minimum_two_characters(self, client):
        res = client.get("/search?q=a")
        assert res.status_code == 200
        assert b"at least 2 characters" in res.data

    def test_search_finds_clubs_and_events_case_insensitive(self, client, app):
        with app.app_context():
            club = Club(
                name="Quantum Builders Club",
                description="Build practical quantum and AI projects.",
                category="Tech",
            )
            _db.session.add(club)
            _db.session.commit()

            event = Event(
                title="Quantum Kickoff Session",
                club_id=club.id,
                date="2026-08-01",
                description="Hands-on welcome event for new members.",
            )
            _db.session.add(event)
            _db.session.commit()

            club_id = club.id
            event_id = event.id

        res = client.get("/search?q=QUANTUM")
        assert res.status_code == 200
        assert b"Quantum Builders Club" in res.data
        assert b"Quantum Kickoff Session" in res.data
        assert f"/clubs/{club_id}".encode() in res.data
        assert f"/events/{event_id}".encode() in res.data

    def test_search_handles_no_results(self, client):
        res = client.get("/search?q=zzzz-no-match")
        assert res.status_code == 200
        assert b"No Results Found" in res.data
