import os
from flask import Flask, session
from datetime import timedelta
from sqlalchemy import inspect, text
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from models import db, User
from seeds import seed_demo_data

load_dotenv()

from routes.auth import auth
from routes.dashboard import dashboard_bp
from routes.clubs import clubs_bp
from routes.admin import admin_bp
from routes.profile import profile_bp
from routes.main import main_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-fallback-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clubsync.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=7)

csrf = CSRFProtect(app)
db.init_app(app)


@app.context_processor
def inject_navbar_access():
    user_id = session.get("user_id")
    user_is_admin = False

    if user_id:
        user = db.session.get(User, user_id)
        user_is_admin = bool(user and user.is_admin)

    return {
        "navbar_can_access_admin": bool(
            session.get("admin_logged_in") or user_is_admin
        )
    }


def ensure_schema_columns():
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()

    statements = []

    if "clubs" in table_names:
        existing = {col["name"] for col in inspector.get_columns("clubs")}
        if "category" not in existing:
            statements.append("ALTER TABLE clubs ADD COLUMN category VARCHAR(50)")
        if "image_path" not in existing:
            statements.append("ALTER TABLE clubs ADD COLUMN image_path VARCHAR(255)")

    if "users" in table_names:
        existing = {col["name"] for col in inspector.get_columns("users")}
        if "is_admin" not in existing:
            statements.append("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0")

    if not statements:
        return

    with db.engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))

def ensure_profile_schema_columns():

    inspector = inspect(db.engine)

    if "profile_users" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("profile_users")
    }

    statements = []

    if "avatar" not in existing_columns:
        statements.append(
            "ALTER TABLE profile_users ADD COLUMN avatar VARCHAR(255)"
        )

    if not statements:
        return

    with db.engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


with app.app_context():
    db.create_all()

    ensure_profile_schema_columns()
    ensure_schema_columns()

    seed_demo_data()

app.register_blueprint(auth)
app.register_blueprint(dashboard_bp)
app.register_blueprint(clubs_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
