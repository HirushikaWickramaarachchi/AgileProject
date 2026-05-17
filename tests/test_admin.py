"""
Tests for admin routes: login, dashboard, events, members.
"""


class TestAdminAuth:
    def test_login_page_loads(self, client):
        res = client.get("/admin/login")
        assert res.status_code == 200

    def test_login_success(self, client, admin_user):
        res = client.post("/admin/login", data={
            "email": "admin@clubsync.edu",
            "password": "admin123"
        }, follow_redirects=True)
        assert res.status_code == 200

    def test_login_wrong_password(self, client, admin_user):
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

    def test_non_admin_user_cannot_login(self, client, sample_user):
        res = client.post("/admin/login", data={
            "email": "test@example.com",
            "password": "hashed"
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
        assert b"Registered Users" in res.data
        assert b"Total Events" in res.data
        assert b"Club Memberships" in res.data


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


class TestAdminClubs:
    def test_clubs_page_loads(self, admin_client):
        res = admin_client.get("/admin/clubs")
        assert res.status_code == 200

    def test_create_club(self, admin_client, app):
        from models.club import Club
        res = admin_client.post("/admin/clubs", data={
            "name": "New Club",
            "description": "A brand new club",
        }, follow_redirects=True)
        assert res.status_code == 200
        assert b"Club created successfully" in res.data
        with app.app_context():
            assert Club.query.filter_by(name="New Club").first() is not None

    def test_create_club_missing_fields(self, admin_client):
        res = admin_client.post("/admin/clubs", data={
            "name": "",
            "description": "",
        }, follow_redirects=True)
        assert b"required" in res.data

    def test_create_club_duplicate_name(self, admin_client, sample_club, app):
        with app.app_context():
            from models.club import Club
            name = Club.query.get(sample_club).name
        res = admin_client.post("/admin/clubs", data={
            "name": name,
            "description": "Duplicate",
        }, follow_redirects=True)
        assert b"already exists" in res.data

    def test_delete_club(self, admin_client, sample_club, app):
        from models.club import Club
        res = admin_client.post(f"/admin/clubs/{sample_club}/delete", follow_redirects=True)
        assert res.status_code == 200
        with app.app_context():
            assert Club.query.get(sample_club) is None

    def test_delete_nonexistent_club(self, admin_client):
        res = admin_client.post("/admin/clubs/9999/delete")
        assert res.status_code == 404


class TestAdminUsers:
    def test_users_page_loads(self, admin_client):
        res = admin_client.get("/admin/users")
        assert res.status_code == 200

    def test_users_page_lists_non_admin_users(self, admin_client, sample_user, app):
        from models.user import User
        with app.app_context():
            user = User.query.get(sample_user)
            name = user.name
        res = admin_client.get("/admin/users")
        assert name.encode() in res.data

    def test_delete_user(self, admin_client, sample_user):
        res = admin_client.post(f"/admin/users/{sample_user}/delete", follow_redirects=True)
        assert res.status_code == 200
        assert b"has been deleted" in res.data

    def test_cannot_delete_admin_user(self, admin_client, admin_user):
        res = admin_client.post(f"/admin/users/{admin_user}/delete", follow_redirects=True)
        assert b"Cannot delete admin accounts" in res.data

    def test_delete_nonexistent_user(self, admin_client):
        res = admin_client.post("/admin/users/9999/delete")
        assert res.status_code == 404
