from flask import Blueprint, render_template
from models.club import Club
from models.event import Event
from models.user import User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/about")
def about():

    total_clubs = Club.query.count()
    total_events = Event.query.count()
    total_students = User.query.count()

    return render_template(
        "about.html",
        total_clubs=total_clubs,
        total_events=total_events,
        total_students=total_students
    )


@main_bp.route("/clubs")
def clubs():
    return render_template("club_list.html")
