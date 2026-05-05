import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from werkzeug.security import generate_password_hash
from app import app as flask_app
from models import db as _db
from models.user import User
from models.club import Club
from models.event import Event
from models.membership import Membership


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    flask_app.config["WTF_CSRF_ENABLED"] = False
    flask_app.config["SECRET_KEY"] = "test-secret"

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User(
            name="Admin",
            email="admin@clubsync.edu",
            password_hash=generate_password_hash("admin123"),
            is_admin=True,
        )
        _db.session.add(user)
        _db.session.commit()
        return user.id


@pytest.fixture
def admin_client(client, admin_user):
    with client.session_transaction() as sess:
        sess["admin_logged_in"] = True
        sess["admin_user_id"] = admin_user
        sess["admin_name"] = "Admin"
    return client


@pytest.fixture
def sample_club(app):
    with app.app_context():
        club = Club(name="Test Club", description="A test club")
        _db.session.add(club)
        _db.session.commit()
        return club.id


@pytest.fixture
def sample_event(app, sample_club):
    with app.app_context():
        event = Event(title="Test Event", club_id=sample_club, date="2026-06-01", description="A test event")
        _db.session.add(event)
        _db.session.commit()
        return event.id


@pytest.fixture
def sample_user(app):
    with app.app_context():
        user = User(name="Test User", email="test@example.com", password_hash="hashed")
        _db.session.add(user)
        _db.session.commit()
        return user.id
