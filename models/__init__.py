from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.club import Club
from models.event import Event
from models.membership import Membership
from models.attendance import Attendance
from models.profile_user import ProfileUser
