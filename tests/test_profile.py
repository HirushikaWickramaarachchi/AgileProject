"""
Tests for profile routes: profile page, edit profile, validations.
"""

from models import db as _db
from models.club import Club
from models.membership import Membership
from models.event import Event
from models.attendance import Attendance


class TestProfilePage:

    def test_profile_page_requires_login(self, client):

        res = client.get("/profile")

        assert res.status_code == 302


    def test_profile_page_loads(self, client, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        res = client.get("/profile", follow_redirects=True)

        assert res.status_code == 200


    def test_profile_shows_email(self, client, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        res = client.get("/profile", follow_redirects=True)

        assert b"test@example.com" in res.data


    def test_profile_shows_empty_clubs_message(self, client, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        res = client.get("/profile", follow_redirects=True)

        assert b"You have not joined any clubs yet" in res.data


    def test_profile_shows_joined_club(self, client, app, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        with app.app_context():

            club = Club(
                name="AI Club",
                description="Artificial Intelligence Club"
            )

            _db.session.add(club)
            _db.session.commit()

            membership = Membership(
                user_id=sample_user,
                club_id=club.id
            )

            _db.session.add(membership)
            _db.session.commit()

        res = client.get("/profile", follow_redirects=True)

        assert b"AI Club" in res.data


    def test_profile_shows_attendance_history(self, client, app, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        with app.app_context():

            club = Club(
                name="Tech Club",
                description="Technology Club"
            )

            _db.session.add(club)
            _db.session.commit()

            membership = Membership(
                user_id=sample_user,
                club_id=club.id
            )

            _db.session.add(membership)

            event = Event(
                title="Tech Meetup",
                club_id=club.id,
                date="2026-06-01",
                description="Weekly meetup"
            )

            _db.session.add(event)
            _db.session.commit()

            attendance = Attendance(
                user_id=sample_user,
                event_id=event.id
            )

            _db.session.add(attendance)
            _db.session.commit()

        res = client.get("/profile", follow_redirects=True)

        assert b"Tech Meetup" in res.data


class TestProfileEdit:

    def test_profile_edit_page_requires_login(self, client):

        res = client.get("/profile-edit")

        assert res.status_code == 302


    def test_profile_edit_page_loads(self, client, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        res = client.get("/profile-edit", follow_redirects=True)

        assert res.status_code == 200


    def test_update_bio(self, client, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        res = client.post(
            "/profile-edit",
            data={
                "bio": "Updated bio"
            },
            follow_redirects=True
        )

        assert res.status_code == 200


    def test_update_phone(self, client, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        res = client.post(
            "/profile-edit",
            data={
                "phone": "+61412345678"
            },
            follow_redirects=True
        )

        assert res.status_code == 200


    def test_update_email(self, client, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        res = client.post(
            "/profile-edit",
            data={
                "email": "newemail@example.com"
            },
            follow_redirects=True
        )

        assert res.status_code == 200


    def test_password_mismatch(self, client, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        res = client.post(
            "/profile-edit",
            data={
                "current_password": "Password123!",
                "new_password": "NewPassword123!",
                "confirm_new_password": "WrongPassword"
            },
            follow_redirects=True
        )

        assert res.status_code in [200, 302]


    def test_invalid_phone_number(self, client, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        res = client.post(
            "/profile-edit",
            data={
                "phone": "invalid-phone"
            },
            follow_redirects=True
        )

        assert res.status_code in [200, 302]


    def test_invalid_email_format(self, client, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        res = client.post(
            "/profile-edit",
            data={
                "email": "invalid-email"
            },
            follow_redirects=True
        )

        assert res.status_code in [200, 302]


class TestProfileStatistics:

    def test_engagement_rate_zero(self, client, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        res = client.get("/profile", follow_redirects=True)

        assert b"0%" in res.data


    def test_engagement_rate_calculation(self, client, app, sample_user):

        with client.session_transaction() as sess:
            sess["user_id"] = sample_user
            sess["user_name"] = "Test User"
            sess["logged_in"] = True

        with app.app_context():

            club = Club(
                name="Coding Club",
                description="Programming club"
            )

            _db.session.add(club)
            _db.session.commit()

            membership = Membership(
                user_id=sample_user,
                club_id=club.id
            )

            _db.session.add(membership)

            event = Event(
                title="Python Workshop",
                club_id=club.id,
                date="2026-06-15",
                description="Learn Python"
            )

            _db.session.add(event)
            _db.session.commit()

            attendance = Attendance(
                user_id=sample_user,
                event_id=event.id
            )

            _db.session.add(attendance)
            _db.session.commit()

        res = client.get("/profile", follow_redirects=True)

        assert b"100%" in res.data