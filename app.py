from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

from models import db, User

app = Flask(__name__)

# CONFIGURATION
app.config["SECRET_KEY"] = "change_this_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clubsync.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Keep sessions for 7 days
app.permanent_session_lifetime = timedelta(days=7)

db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# HOME PAGE
@app.route("/")
def index():
    return render_template("home.html")

# REGISTER PAGE
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name").strip()
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")

        if not name or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already exists.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id
        session["user_name"] = new_user.name

        return redirect(url_for("home"))

    return render_template("signup.html")


# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):

            session.permanent = True
            session["user_id"] = user.id
            session["user_name"] = user.name

            flash("Login successful.", "success")
            return redirect(url_for("home"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")

# HOME PAGE
@app.route("/home")
def home():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("home.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    return f"Welcome {session['user_name']} to ClubSync Dashboard"

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return render_template("home.html")

@app.route("/clubs")
def clubs():
    return render_template("club_list.html")


@app.route("/events")
def events():
    return render_template("event.html")


@app.route("/myclubs")
def myclubs():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("club_details.html")


@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("profile.html")

# RUN APP
if __name__ == "__main__":
    app.run(debug=True)