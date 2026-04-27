"""
Tests for admin routes: login, dashboard, events, members.
"""


class TestAdminAuth:
    def test_login_page_loads(self, client):
        res = client.get("/admin/login")
        assert res.status_code == 200

    def test_login_success(self, client):
        res = client.post("/admin/login", data={
            "email": "admin@clubsync.edu",
            "password": "admin123"
        }, follow_redirects=True)
        assert res.status_code == 200

    def test_login_wrong_password(self, client):
        res = client.post("/admin/login", data={
            "email": "admin@clubsync.edu",
            "password": "wrongpassword"
        }, follow_redirects=True)
        assert b"Invalid email or password" in res.data

    def test_login_wrong_email(self, client):
        res = client.post("/admin/login", data={
            "email": "wrong@email.com",
            "password": "admin123"
        }, follow_redirects=True)
        assert b"Invalid email or password" in res.data

    def test_logout_redirects_to_login(self, admin_client):
        res = admin_client.get("/admin/logout", follow_redirects=True)
        assert res.status_code == 200

    def test_protected_route_redirects_when_not_logged_in(self, client):
        res = client.get("/admin/members")
        assert res.status_code == 302
        assert "/admin/login" in res.headers["Location"]


class TestAdminDashboard:
    def test_dashboard_loads(self, admin_client):
        res = admin_client.get("/admin/dashboard")
        assert res.status_code == 200

    def test_dashboard_shows_counts(self, admin_client):
        res = admin_client.get("/admin/dashboard")
        assert b"Total Members" in res.data
        assert b"Total Events" in res.data
        assert b"Total Clubs" in res.data


class TestAdminEvents:
    def test_events_page_loads(self, admin_client):
        res = admin_client.get("/admin/events")
        assert res.status_code == 200

    def test_create_event(self, admin_client, sample_club):
        res = admin_client.post("/admin/events", data={
            "title": "New Event",
            "club_id": sample_club,
            "date": "2026-07-01",
            "description": "Test description"
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b"Event created successfully" in res.data

    def test_create_event_missing_title(self, admin_client, sample_club):
        res = admin_client.post("/admin/events", data={
            "title": "",
            "club_id": sample_club,
            "date": "2026-07-01",
        }, follow_redirects=True)
        assert b"required" in res.data

    def test_delete_event(self, admin_client, sample_event):
        res = admin_client.post(f"/admin/events/{sample_event}/delete", follow_redirects=True)
        assert res.status_code == 200
        assert b"Event deleted" in res.data

    def test_edit_event(self, admin_client, sample_event, sample_club):
        res = admin_client.post(f"/admin/events/{sample_event}/edit", data={
            "title": "Updated Event",
            "club_id": sample_club,
            "date": "2026-08-01",
            "description": "Updated description"
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b"Event updated successfully" in res.data

    def test_delete_nonexistent_event(self, admin_client):
        res = admin_client.post("/admin/events/9999/delete")
        assert res.status_code == 404


class TestAdminMembers:
    def test_members_page_loads(self, admin_client):
        res = admin_client.get("/admin/members")
        assert res.status_code == 200

    def test_remove_member(self, admin_client, app, sample_club, sample_user):
        from models import db
        from models.membership import Membership
        with app.app_context():
            m = Membership(user_id=sample_user, club_id=sample_club)
            db.session.add(m)
            db.session.commit()
            membership_id = m.id

        res = admin_client.post(f"/admin/members/{membership_id}/remove", follow_redirects=True)
        assert res.status_code == 200
        assert b"removed from club" in res.data

    def test_remove_nonexistent_member(self, admin_client):
        res = admin_client.post("/admin/members/9999/remove")
        assert res.status_code == 404
