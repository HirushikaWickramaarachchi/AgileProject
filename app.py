from flask import Flask
from datetime import timedelta
from sqlalchemy import inspect, text
from models import db
from seeds import seed_demo_data

from routes.auth import auth
from routes.dashboard import dashboard_bp
from routes.clubs import clubs_bp
from routes.admin import admin_bp

from routes.profile import profile_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = "change_this_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clubsync.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=7)

db.init_app(app)


def ensure_club_schema_columns():
    inspector = inspect(db.engine)

    if "clubs" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("clubs")}
    statements = []

    if "category" not in existing_columns:
        statements.append("ALTER TABLE clubs ADD COLUMN category VARCHAR(50)")

    if "image_path" not in existing_columns:
        statements.append("ALTER TABLE clubs ADD COLUMN image_path VARCHAR(255)")

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
    ensure_club_schema_columns()
    ensure_profile_schema_columns()
    seed_demo_data()

app.register_blueprint(auth)
app.register_blueprint(dashboard_bp)
app.register_blueprint(clubs_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(profile_bp)

if __name__ == "__main__":
    app.run(debug=True)
