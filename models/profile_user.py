from models import db

<<<<<<< HEAD
=======

>>>>>>> 3870056749563c0ea895fc0f68e3fce2014d6dc7
class ProfileUser(db.Model):
    __tablename__ = "profile_users"

    id = db.Column(db.Integer, primary_key=True)
<<<<<<< HEAD
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    phone = db.Column(db.String(30))
    address = db.Column(db.String(255))
    gender = db.Column(db.String(30))
    bio = db.Column(db.Text)
    dob = db.Column(db.String(20))
    major = db.Column(db.String(100))
    avatar = db.Column(db.String(255))
=======
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    major = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    dob = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)

>>>>>>> 3870056749563c0ea895fc0f68e3fce2014d6dc7
