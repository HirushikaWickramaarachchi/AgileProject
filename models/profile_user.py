from models import db

class ProfileUser(db.Model):
    __tablename__ = "profile_users"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    major = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    dob = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)