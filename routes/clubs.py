from flask import Blueprint, render_template, session, redirect, url_for

clubs_bp = Blueprint("clubs", __name__)

@clubs_bp.route("/clubs")
def clubs():
    return render_template("club_list.html")


@clubs_bp.route("/events")
def events():
    return render_template("event.html")


@clubs_bp.route("/myclubs")
def myclubs():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("club_details.html")