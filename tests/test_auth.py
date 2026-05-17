"""Tests for auth routes: register, login, logout, forgot_password."""
from werkzeug.security import generate_password_hash
from models import db as _db
from models.user import User


class TestRegister:
    def test_register_page_loads(self, client):
        res = client.get("/register")
        assert res.status_code == 200

    def test_register_success(self, client, app):
        res = client.post("/register", data={
            "name": "New User",
            "email": "new@example.com",
            "password": "Password@123",
            "confirmPassword": "Password@123",
        }, follow_redirects=True)
        assert res.status_code == 200
        with app.app_context():
            user = User.query.filter_by(email="new@example.com").first()
            assert user is not None
            assert user.name == "New User"

    def test_register_sets_session(self, client):
        client.post("/register", data={
            "name": "New User",
            "email": "new@example.com",
            "password": "Password@123",
            "confirmPassword": "Password@123",
        })
        with client.session_transaction() as sess:
            assert "user_id" in sess

    def test_register_duplicate_email(self, client, sample_user):
        res = client.post("/register", data={
            "name": "Another",
            "email": "test@example.com",
            "password": "Password@123",
            "confirmPassword": "Password@123",
        }, follow_redirects=True)
        assert b"Email already exists" in res.data

    def test_register_password_mismatch(self, client):
        res = client.post("/register", data={
            "name": "User",
            "email": "mismatch@example.com",
            "password": "Password@123",
            "confirmPassword": "Different@456",
        }, follow_redirects=True)
        assert b"Passwords do not match" in res.data


class TestLogin:
    def test_login_page_loads(self, client):
        res = client.get("/login")
        assert res.status_code == 200

    def test_login_success(self, client, app):
        with app.app_context():
            user = User(
                name="Login User",
                email="login@example.com",
                password_hash=generate_password_hash("correctpass"),
            )
            _db.session.add(user)
            _db.session.commit()

        res = client.post("/login", data={
            "email": "login@example.com",
            "password": "correctpass",
        }, follow_redirects=True)
        assert res.status_code == 200

    def test_login_sets_session(self, client, app):
        with app.app_context():
            user = User(
                name="Login User",
                email="login2@example.com",
                password_hash=generate_password_hash("correctpass"),
            )
            _db.session.add(user)
            _db.session.commit()

        client.post("/login", data={
            "email": "login2@example.com",
            "password": "correctpass",
        })
        with client.session_transaction() as sess:
            assert "user_id" in sess

    def test_login_wrong_password(self, client, app):
        with app.app_context():
            user = User(
                name="Login User",
                email="login3@example.com",
                password_hash=generate_password_hash("correctpass"),
            )
            _db.session.add(user)
            _db.session.commit()

        res = client.post("/login", data={
            "email": "login3@example.com",
            "password": "wrongpass",
        }, follow_redirects=True)
        assert b"Invalid email or password" in res.data

    def test_login_unknown_email(self, client):
        res = client.post("/login", data={
            "email": "nobody@example.com",
            "password": "anything",
        }, follow_redirects=True)
        assert b"Invalid email or password" in res.data


class TestLogout:
    def test_logout_clears_session(self, client, app):
        with app.app_context():
            user = User(
                name="Logout User",
                email="logout@example.com",
                password_hash=generate_password_hash("pass"),
            )
            _db.session.add(user)
            _db.session.commit()

        client.post("/login", data={"email": "logout@example.com", "password": "pass"})
        client.get("/logout")
        with client.session_transaction() as sess:
            assert "user_id" not in sess

    def test_logout_redirects(self, client):
        res = client.get("/logout")
        assert res.status_code == 302


class TestForgotPassword:
    def test_forgot_password_page_loads(self, client):
        res = client.get("/forgot-password")
        assert res.status_code == 200

    def test_reset_password_success(self, client, app):
        with app.app_context():
            user = User(
                name="Reset User",
                email="reset@example.com",
                password_hash=generate_password_hash("oldpass"),
            )
            _db.session.add(user)
            _db.session.commit()

        res = client.post("/forgot-password", data={
            "email": "reset@example.com",
            "password": "NewPass@123",
            "confirmPassword": "NewPass@123",
        }, follow_redirects=True)
        assert b"Password reset successful" in res.data

    def test_reset_unknown_email(self, client):
        res = client.post("/forgot-password", data={
            "email": "ghost@example.com",
            "password": "NewPass@123",
            "confirmPassword": "NewPass@123",
        }, follow_redirects=True)
        assert b"Email not found" in res.data

    def test_reset_password_mismatch(self, client, app):
        with app.app_context():
            user = User(
                name="Reset User2",
                email="reset2@example.com",
                password_hash=generate_password_hash("oldpass"),
            )
            _db.session.add(user)
            _db.session.commit()

        res = client.post("/forgot-password", data={
            "email": "reset2@example.com",
            "password": "NewPass@123",
            "confirmPassword": "Different@456",
        }, follow_redirects=True)
        assert b"Passwords do not match" in res.data
