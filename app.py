from flask import Flask
from datetime import timedelta
from models import db

from routes.auth import auth
from routes.dashboard import dashboard_bp
from routes.clubs import clubs_bp
from routes.admin import admin_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = "change_this_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clubsync.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(days=7)

db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(auth)
app.register_blueprint(dashboard_bp)
app.register_blueprint(clubs_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)