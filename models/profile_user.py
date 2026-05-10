from models import db

class ProfileUser(db.Model):
    __tablename__ = "profile_users"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    phone = db.Column(db.String(30))
    address = db.Column(db.String(255))
    gender = db.Column(db.String(30))
    bio = db.Column(db.Text)
    dob = db.Column(db.String(20))
    major = db.Column(db.String(100))
    avatar = db.Column(db.String(255))